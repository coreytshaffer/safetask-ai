import pytest
from pathlib import Path
import sys

# Ensure src is in the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qgis_runner.runner import QGISRunner
from review_engine.harness.checker import CyberneticHarness

def test_load_recipe():
    recipes_dir = Path(__file__).parent.parent / "qgis" / "recipes"
    runner = QGISRunner(recipes_dir=str(recipes_dir))
    
    recipe = runner.load_recipe("clear_lake_context")
    assert recipe is not None
    assert recipe.name == "Clear Lake Context Map"
    assert len(recipe.layers) == 3

def test_map_harness_integration():
    policy_dir = Path(__file__).parent.parent / "policy"
    harness = CyberneticHarness(str(policy_dir))
    
    # Simulate a map request that triggers the sensitive location rule
    text = "Map generation requested for 39°00'00\"N"
    packet = harness.evaluate(text)
    
    assert packet.decision_state == "require_review"

def test_map_generation(tmp_path):
    recipes_dir = Path(__file__).parent.parent / "qgis" / "recipes"
    output_dir = tmp_path / "exports"
    
    runner = QGISRunner(recipes_dir=str(recipes_dir), output_dir=str(output_dir))
    recipe = runner.load_recipe("clear_lake_context")
    
    metadata = runner.generate_map(recipe, lat=39.0, lon=-122.8, decision_state="allow")
    
    assert metadata.recipe_id == "clear_lake_context"
    assert metadata.harness_decision == "allow"
    
    exported_png = Path(metadata.exported_files[0])
    exported_json = Path(metadata.exported_files[1])
    
    assert exported_png.exists()
    assert exported_json.exists()
