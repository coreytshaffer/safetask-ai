import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

from .schema import MapExportMetadata, MapRecipe


class QGISRunner:
    def __init__(
        self, recipes_dir: str = "qgis/recipes", output_dir: str = "data/exports"
    ):
        self.recipes_dir = Path(recipes_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_recipe(self, recipe_id: str) -> Optional[MapRecipe]:
        recipe_path = self.recipes_dir / f"{recipe_id}.json"
        if not recipe_path.exists():
            return None

        with open(recipe_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return MapRecipe(**data)

    def generate_map(
        self,
        recipe: MapRecipe,
        lat: float,
        lon: float,
        decision_state: str,
        mockup_path: Optional[str] = None,
    ) -> MapExportMetadata:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_filename = f"{recipe.id}_{timestamp}"

        png_path = self.output_dir / f"{base_filename}.png"
        meta_path = self.output_dir / f"{base_filename}_meta.json"

        # In a full production environment, this would call PyQGIS or qgis_process.
        # For this MVP/portfolio, we simulate the output by copying a mockup image if available.
        # This prevents the system from crashing if QGIS paths are not perfectly configured.

        if mockup_path and Path(mockup_path).exists():
            shutil.copy(mockup_path, png_path)
            print(f"Simulated QGIS rendering complete. Map saved to {png_path}")
        else:
            # Create a dummy file if no mockup is provided
            with open(png_path, "w") as f:
                f.write("Simulated Map Output")

        metadata = MapExportMetadata(
            recipe_id=recipe.id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            center_coordinates=f"{lat}, {lon}",
            exported_files=[str(png_path), str(meta_path)],
            harness_decision=decision_state,
        )

        with open(meta_path, "w", encoding="utf-8") as f:
            # We use __dict__ here for simplicity, but in production we'd use dataclasses.asdict
            import dataclasses

            json.dump(dataclasses.asdict(metadata), f, indent=2)

        return metadata
