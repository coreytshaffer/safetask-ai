"""A03a preserves real runtime creation entirely in disposable workspaces."""
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("shoreline", [False, True])
def test_local_storage_versioning_logging_and_optional_map(tmp_path, shoreline):
    (tmp_path / ".gitignore").write_bytes((ROOT / ".gitignore").read_bytes())
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    # The child imports logger only after cwd is isolated. No source checkout is mutated.
    code = textwrap.dedent('''
        import importlib.util
        import json
        from pathlib import Path
        import py_compile
        import socket
        import subprocess
        import sys

        root, shoreline = Path(sys.argv[1]), sys.argv[2] == "True"
        sys.path.insert(0, str(root / "src"))
        def denied(*args, **kwargs):
            raise AssertionError("No network permitted in runtime creation tests")
        socket.create_connection = denied
        socket.socket.connect = denied
        from logger import logger
        from notebook.db import NotebookDB
        from notebook.schema import FieldNote

        assert not Path("data/field_notes.db").exists()
        notebook = NotebookDB()
        note = FieldNote(site_id="SYNTHETIC-TEST", timestamp="2000-01-01T00:00:00Z",
                         notes="Synthetic observation for runtime test only", id="synthetic-test",
                         coordinates="39.02, -122.75")
        notebook.insert_note(note)
        assert notebook.get_all_notes() == [note]
        assert Path("data/notes/.git").is_dir()
        committed = subprocess.check_output(["git", "-C", "data/notes", "show", "HEAD:synthetic-test.md"])
        assert b"Synthetic observation" in committed
        # The SQLite cache can be rebuilt from the same versioned Markdown.
        rebuilt = NotebookDB(db_path="src/data/field_notes.db")
        assert rebuilt.get_all_notes() == [note]
        logger.info("SYNTHETIC-LOG-MARKER")
        assert "SYNTHETIC-LOG-MARKER" in Path("data/logs/fieldaware.log").read_text()

        spec = importlib.util.spec_from_file_location("pitlens_test_db", root / "pitlens-table-games/pitlens/database.py")
        pit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pit)
        Path("pitlens-table-games").mkdir()
        pit.DB_PATH = str(Path("pitlens-table-games/pitlens.db").resolve())
        assert not Path(pit.DB_PATH).exists()
        pit.init_db()
        with pit.get_db_connection() as conn:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert tables == {"game_sessions", "rounds", "active_bet_shots", "wagers", "player_decisions", "review_flags", "reports"}

        if shoreline:
            path = Path("data/clear-lake-watch-repo/data/lake-shoreline.json")
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"rings": [{"points": [
                {"latitude": 39.0, "longitude": -122.7},
                {"latitude": 39.1, "longitude": -122.7},
                {"latitude": 39.0, "longitude": -122.8}]}]}))
        from qgis_runner.folium_map import FoliumMapGenerator
        output = Path(FoliumMapGenerator().generate_interactive_map())
        rendered = output.read_text()
        assert "SYNTHETIC-TEST" in rendered
        assert ("Clear Lake Shoreline Vector" in rendered) == shoreline

        Path("scratch/__pycache__").mkdir(parents=True)
        py_compile.compile(str(root / "src/notebook/schema.py"), cfile="scratch/__pycache__/schema.pyc", doraise=True)
        assert Path("scratch/__pycache__/schema.pyc").exists()
        # Only the copied ignore file is publishable; all runtime outputs stay local.
        other = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"]).decode().splitlines()
        assert other == [".gitignore"], other
        assert not subprocess.check_output(["git", "ls-files"])
    ''')
    env = os.environ.copy()
    # Isolate Git behavior for the test-owned notes repository (no host hooks/signing).
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_COUNT="2", GIT_CONFIG_KEY_0="commit.gpgsign", GIT_CONFIG_VALUE_0="false",
               GIT_CONFIG_KEY_1="core.hooksPath", GIT_CONFIG_VALUE_1=str(tmp_path / "no-hooks"))
    result = subprocess.run([sys.executable, "-B", "-c", code, str(ROOT), str(shoreline)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
