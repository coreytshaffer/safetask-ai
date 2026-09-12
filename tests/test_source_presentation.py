"""Exercise actual route/CLI bodies without unrelated model/download startup."""
import argparse
import ast
import json
from pathlib import Path
import sys
import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rag.retriever import RetrievalUnavailable
from test_retrieval_boundary import rig
from test_provenance import register

ROOT = Path(__file__).resolve().parents[1]


def actual_function(path, name, namespace):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), namespace)
    return namespace[name]


@pytest.mark.parametrize("condition", ["reviewed", "unreviewed", "empty", "index_required", "failure"])
def test_search_api_serializes_provenance_and_explicit_status(rig, condition, monkeypatch, no_network):
    source, catalog, indexer, retriever = rig
    class SearchRequest(BaseModel):
        query: str
    if condition == "reviewed":
        register(source, catalog, source.parent.parent)
    if condition == "empty":
        source.unlink()
    if condition != "index_required":
        indexer.index_directory()
    if condition == "failure":
        monkeypatch.setattr(retriever, "search", lambda *a, **k: (_ for _ in ()).throw(TypeError("test error")))
    handler = actual_function("src/web/app.py", "search_docs", dict(
        app=FastAPI(), SearchRequest=SearchRequest, retriever=retriever,
        RetrievalUnavailable=RetrievalUnavailable, JSONResponse=JSONResponse))
    response = no_network.run_until_complete(handler(SearchRequest(query="neutral")))
    if condition in {"failure", "index_required"}:
        assert response.status_code == 503
        assert json.loads(response.body) == {"results": [], "retrieval_status": (
            "index_required" if condition == "index_required" else "retrieval_unavailable")}
    else:
        assert response["retrieval_status"] == "ready"
        if condition == "empty":
            assert response["results"] == []
        else:
            meta = response["results"][0]["metadata"]
            assert meta["provenance"]["review_status"] == condition
            assert meta["provenance_label"]


@pytest.mark.parametrize("missing", [False, True])
def test_cli_search_label_and_missing_index(rig, monkeypatch, capsys, missing):
    source, catalog, indexer, retriever = rig
    if not missing:
        indexer.index_directory()
    run = actual_function("src/cli.py", "main", dict(argparse=argparse,
        DocumentRetriever=lambda **kwargs: retriever, RetrievalUnavailable=RetrievalUnavailable))
    monkeypatch.setattr(sys, "argv", ["cli.py", "search", "neutral"])
    run()
    output = capsys.readouterr().out
    if missing:
        assert "index_required" in output
    else:
        assert "Unreviewed reference - not reviewed authority" in output
        assert "Source-declared date (not a freshness check)" in output
        assert "official_regulation" not in output


def test_legacy_pdf_marks_every_page_as_unreviewed(tmp_path, monkeypatch, no_network):
    from safetask.core import db, pdf_engine
    from pypdf import PdfReader
    monkeypatch.setattr(db, "get_incident", lambda _: dict(id="TEST", date="test",
        category="test", severity="test", formatted_narrative=("Neutral legacy narrative. " * 800)))
    target = tmp_path / "draft.pdf"
    assert pdf_engine.generate_incident_pdf("TEST", str(target))
    pages = PdfReader(target).pages
    assert len(pages) > 1
    for page in pages:
        text = page.extract_text()
        assert "UNREVIEWED DRAFT" in text
        assert "Policy sources and regulatory applicability have not been verified." in text
        assert "OFFICIAL CASINO SURVEILLANCE REPORT" not in text
