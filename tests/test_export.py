import os
import zipfile
import pytest
from pathlib import Path
import sys

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from export_engine import ExportEngine

def test_export_engine_bundle_generation(tmp_path):
    # Setup
    templates_dir = Path(__file__).parent.parent / "qgis" / "recipes"
    output_dir = tmp_path / "exports"
    
    engine = ExportEngine(templates_dir=str(templates_dir), output_dir=str(output_dir))
    
    # Create dummy notes
    class DummyNote:
        def __init__(self, ts, msg):
            self.timestamp = ts
            self.notes = msg
            
    notes = [
        DummyNote("2026-06-01T12:00:00Z", "Saw a cool bird."),
        DummyNote("2026-06-01T12:05:00Z", "Water temp is 20C.")
    ]
    
    # Generate bundle
    base_filename = "test_export_123"
    zip_path = engine.generate_export_bundle(
        base_filename=base_filename,
        site_id="Test Site",
        notes=notes,
        review_packet=None
    )
    
    assert os.path.exists(zip_path)
    
    # Verify contents of zip
    with zipfile.ZipFile(zip_path, 'r') as zf:
        namelist = zf.namelist()
        assert f"{base_filename}_report.md" in namelist
        assert f"{base_filename}_manifest.txt" in namelist
        
        # Read the manifest
        with zf.open(f"{base_filename}_manifest.txt") as f:
            manifest_content = f.read().decode('utf-8')
            assert "FILE_NOT_FOUND" in manifest_content or ".png" in manifest_content
            assert "_report.md" in manifest_content
            
        # Read the report
        with zf.open(f"{base_filename}_report.md") as f:
            report_content = f.read().decode('utf-8')
            assert "Test Site" in report_content
            assert "Saw a cool bird." in report_content
            assert "Water temp is 20C." in report_content
