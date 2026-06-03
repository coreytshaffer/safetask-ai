import pytest
import sys
from pathlib import Path

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qgis_runner.gdal_wrapper import GDALWrapper

def test_gdal_translate_fallback(tmp_path):
    wrapper = GDALWrapper()
    # Force mock simulation
    wrapper.has_gdal = False
    
    input_file = tmp_path / "in.tif"
    output_file = tmp_path / "out.tif"
    
    res = wrapper.translate(str(input_file), str(output_file))
    
    assert res == "Simulated success."
    assert output_file.exists()
    
def test_ogr2ogr_fallback(tmp_path):
    wrapper = GDALWrapper()
    wrapper.has_ogr = False
    
    input_file = tmp_path / "in.shp"
    output_file = tmp_path / "out.shp"
    
    res = wrapper.ogr2ogr(str(input_file), str(output_file))
    
    assert res == "Simulated success."
    assert output_file.exists()
