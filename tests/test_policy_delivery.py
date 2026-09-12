import asyncio
import importlib
import io
import json
from pathlib import Path
import pytest

from safetask.core import db
from safetask.core import regulation_pack as packs
from rag.retriever import RetrievalUnavailable, IndexRequired
from test_provenance import register
from test_retrieval_boundary import rig


@pytest.fixture
def pack_env(tmp_path):
    root = tmp_path / "domains"
    path = root / "test-domain/regulations.json"
    path.parent.mkdir(parents=True)
    entry = dict(citation="TEST-001", title="Neutral test source", topic_tags=["test"],
                 source_language="en", source_url="https://example.org/source", source_text="Neutral text",
                 literal_translation={"en": "Neutral translation"},
                 operational_interpretation={"en": "Neutral interpretation"}, authority_lanes=[],
                 confidence=packs.APPROVED_CONFIDENCE, translation_reviewed_by="Test reviewer",
                 interpretation_reviewed_by="Test reviewer")
    payload = dict(id="test", domain="test-domain", jurisdiction="Test scope", issuing_authority="Test issuer",
                   source_policy=packs.OFFICIAL_SOURCE_POLICY, source_review_model=packs.OPERATIONAL_REVIEW_MODEL,
                   official_source_domains=["example.org"], default_language="en", supported_languages=["en"],
                   source_url="https://example.org/source", review_status="approved", entries=[entry])
    path.write_text(json.dumps(payload))
    catalog = tmp_path / "catalog.json"
    catalog.write_text('{"schema_version":1,"sources":[]}')
    return path, catalog, payload, dict(domain_root=root, catalog_path=catalog, repository_root=tmp_path)


@pytest.mark.parametrize("condition", ["unregistered", "approved", "modified", "revoked", "synthetic", "invalid", "own_domains", "legacy", "malformed"])
def test_pack_contract_and_trusted_review_are_both_required(pack_env, condition, no_network):
    path, catalog, payload, kwargs = pack_env
    if condition == "synthetic":
        payload["source_kind"] = "synthetic"
    if condition == "invalid":
        payload["entries"][0].pop("interpretation_reviewed_by")
    if condition == "own_domains":
        payload["official_source_domains"] = ["attacker.example"]
        payload["source_url"] = payload["entries"][0]["source_url"] = "https://attacker.example/source"
    if condition == "legacy":
        payload = [dict(code="TEST", title="Neutral", summary="Neutral", keywords=[])]
    path.write_text(json.dumps(payload))
    if condition != "unregistered":
        register(path, catalog, path.parents[2])
    if condition == "modified":
        path.write_text(path.read_text() + " ")
    if condition == "revoked":
        catalog.write_text('{"schema_version":1,"sources":[]}')
    if condition == "malformed":
        path.write_text("{")
    status, body = packs.policy_response("test-domain", **kwargs)
    if condition == "approved":
        assert status == 200
        assert body["entries"][0]["provenance"] == body["provenance"]
        assert body["provenance"]["review_status"] == "reviewed"
    else:
        assert status == 409
        assert body["entries"] == []


@pytest.fixture
def flask_module(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(db, "DB_FILE", tmp_path / "unused.db")
    return importlib.import_module("safetask.apps.legacy_scc.app")


@pytest.mark.parametrize("server", ["flask", "legacy_scc", "surveillance_command_center"])
@pytest.mark.parametrize("reviewed", [False, True])
def test_all_three_serving_boundaries(pack_env, flask_module, monkeypatch, server, reviewed, no_network):
    path, catalog, payload, kwargs = pack_env
    if reviewed:
        register(path, catalog, path.parents[2])
    real = packs.policy_response
    invoke = lambda domain, **unused: real(domain, **kwargs)
    if server == "flask":
        monkeypatch.setattr(flask_module, "policy_response", invoke)
        def request(domain):
            response = flask_module.app.test_client().get(f"/policy-packs/{domain}/regulations.json")
            return response.status_code, response.headers, response.json
    else:
        module = importlib.import_module("safetask.apps." + server + ".server")
        monkeypatch.setattr(module, "policy_response", invoke)
        def request(domain):
            handler = object.__new__(module.ProxyHTTPRequestHandler)
            handler.wfile = io.BytesIO()
            headers, statuses = {}, []
            handler.send_response = statuses.append
            handler.send_header = lambda key, value: headers.update({key: value})
            handler.end_headers = lambda: None
            handler.path = f"/policy-packs/{domain}/regulations.json"
            handler.do_GET()
            return statuses[0], headers, json.loads(handler.wfile.getvalue())
    status, headers, body = request("gaming")
    assert (status, body["status"], body["entries"]) == (410, "retired", [])
    assert headers["Cache-Control"] == "no-store"
    status, headers, body = request("test-domain")
    assert status == (200 if reviewed else 409)
    assert headers["Cache-Control"] == "no-store"
    assert bool(body["entries"]) == reviewed


def test_upload_is_disabled_before_read_or_write(flask_module, monkeypatch, no_network):
    from safetask.core import doc_processor
    monkeypatch.setattr(doc_processor, "extract_text_from_pdf", lambda *a: pytest.fail("file read"))
    response = flask_module.app.test_client().post("/api/policies/upload")
    assert response.status_code == 410
    assert response.headers["Cache-Control"] == "no-store"
    with pytest.raises(ValueError, match="disabled"):
        doc_processor.process_upload("does-not-exist.pdf", "TEST", "Test")
    with pytest.raises(ValueError, match="disabled"):
        doc_processor.append_to_database("TEST", "Test", "Test", [])


@pytest.mark.parametrize("change", ["revoked", "modified"])
def test_pack_review_changed_during_read_fails_closed(pack_env, monkeypatch, change, no_network):
    path, catalog, payload, kwargs = pack_env
    register(path, catalog, path.parents[2])
    real = packs.resolve_provenance
    calls = []
    def change_after_first_check(*args, **options):
        result = real(*args, **options)
        if not calls:
            calls.append(True)
            if change == "revoked":
                catalog.write_text('{"schema_version":1,"sources":[]}')
            else:
                path.write_text(path.read_text() + " ")
        return result
    monkeypatch.setattr(packs, "resolve_provenance", change_after_first_check)
    status, body = packs.policy_response("test-domain", **kwargs)
    assert status == 409
    assert body["entries"] == []


@pytest.fixture
def incident_module(monkeypatch, rig, tmp_path):
    from rag import retriever as module
    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(module, "DocumentRetriever", lambda: rig[3])
    router = importlib.import_module("safetask.api.router")
    monkeypatch.setattr(router, "retriever", rig[3])
    monkeypatch.chdir(tmp_path)
    return router


@pytest.mark.parametrize("condition", ["reviewed", "unreviewed", "missing_index", "type_error", "partial", "failure", "revoked"])
def test_incident_adaptation_atomic_and_no_fabricated_fallback(incident_module, rig, condition, monkeypatch, no_network):
    source, catalog, indexer, retriever = rig
    register(source, catalog, source.parent.parent)
    if condition != "missing_index":
        indexer.index_directory()
    if condition == "unreviewed":
        catalog.write_text('{"schema_version":1,"sources":[]}')
        indexer.index_directory()
    if condition == "revoked":
        catalog.write_text('{"schema_version":1,"sources":[]}')
    if condition in {"type_error", "partial"}:
        card = retriever.search("neutral")[0]
        monkeypatch.setattr(retriever, "search", lambda *a, **k: [card, {"title": "fake"}] if condition == "partial" else [{}])
    if condition == "failure":
        def fail(*args, **kwargs):
            raise RetrievalUnavailable("test failure")
        monkeypatch.setattr(retriever, "search", fail)
    report = incident_module.IncidentReport(title="Test", description="Neutral incident", reporter="Test", location="Test")
    packet = no_network.run_until_complete(incident_module.report_incident(report))["packet"]
    text = json.dumps(packet)
    assert "OSHA" not in text and "8 hours" not in text and "24 hours" not in text
    if condition == "reviewed":
        assert packet["policy_sources_status"] == "reviewed_sources"
        assert packet["recommended_review"][0]["provenance"]["content_sha256"] == json.loads(catalog.read_text())["sources"][0]["content_sha256"]
        assert packet["recommended_review"][0]["page"] is None
    else:
        assert packet["recommended_review"] == []
        expected = "index_required" if condition == "missing_index" else (
            "no_reviewed_sources" if condition in {"unreviewed", "revoked"} else "retrieval_unavailable")
        assert packet["policy_sources_status"] == expected
    saved, = list(Path("data/safetask_incidents").glob("*.json"))
    assert json.loads(saved.read_text()) == packet
