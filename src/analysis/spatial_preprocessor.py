import geopandas as gpd
from pathlib import Path
from shapely.geometry import shape

from logger import logger

class SpatialPreprocessor:
    """
    Handles preprocessing of raw spatial data (Shapefiles, GeoPackages, GeoJSONs)
    to standardize them for the FieldAware workbench (EPSG:4326, simplified geometries).
    """

    def __init__(self, input_filepath: str):
        self.input_filepath = Path(input_filepath)
        self.gdf = None

        if not self.input_filepath.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_filepath}")

    def ingest(self):
        """Reads the spatial file into a GeoDataFrame."""
        logger.info(f"Ingesting spatial file: {self.input_filepath}")
        try:
            self.gdf = gpd.read_file(self.input_filepath)
            logger.info(f"Successfully loaded {len(self.gdf)} features.")
        except Exception as e:
            logger.error(f"Failed to ingest spatial file: {e}")
            raise

    def standardize_crs(self, target_crs="EPSG:4326"):
        """Reprojects the geometry to the target CRS (default: WGS 84)."""
        if self.gdf is None:
            raise ValueError("No data loaded. Call ingest() first.")
            
        if self.gdf.crs is None:
            logger.warning("Input data has no CRS defined. Assuming EPSG:4326.")
            self.gdf.set_crs(target_crs, inplace=True)
        elif self.gdf.crs.to_string() != target_crs:
            logger.info(f"Reprojecting from {self.gdf.crs} to {target_crs}...")
            self.gdf = self.gdf.to_crs(target_crs)
            logger.info("Reprojection complete.")
        else:
            logger.info(f"Data is already in {target_crs}.")

    def simplify_geometry(self, tolerance=0.001):
        """
        Simplifies geometries to reduce file size and rendering load on offline web maps.
        Tolerance is in the units of the CRS (degrees for EPSG:4326).
        """
        if self.gdf is None:
            raise ValueError("No data loaded. Call ingest() first.")
            
        logger.info(f"Simplifying geometries with tolerance {tolerance}...")
        self.gdf['geometry'] = self.gdf['geometry'].simplify(tolerance, preserve_topology=True)
        logger.info("Simplification complete.")

    def export_geojson(self, output_filepath: str):
        """Exports the processed GeoDataFrame to a standard GeoJSON file."""
        if self.gdf is None:
            raise ValueError("No data loaded. Call ingest() first.")
            
        out_path = Path(output_filepath)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Exporting processed data to {out_path}...")
        self.gdf.to_file(out_path, driver="GeoJSON")
        logger.info("Export complete.")
        return str(out_path)

    @classmethod
    def process_pipeline(cls, input_filepath: str, output_filepath: str, tolerance=0.001):
        """Runs the complete preprocessing pipeline."""
        processor = cls(input_filepath)
        processor.ingest()
        processor.standardize_crs()
        processor.simplify_geometry(tolerance)
        return processor.export_geojson(output_filepath)
