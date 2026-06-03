import shutil
import subprocess
from typing import List, Optional

from logger import logger


class GDALWrapper:
    """
    A wrapper around common GDAL/OGR command line tools.
    For this MVP/portfolio, if the tools are not installed in the system PATH,
    it simulates their execution to allow the UI/CLI workflows to function.
    """

    def __init__(self):
        self.has_gdal = shutil.which("gdal_translate") is not None
        self.has_ogr = shutil.which("ogr2ogr") is not None
        if not self.has_gdal:
            logger.debug(
                "gdal_translate not found in PATH. Will use simulation fallback."
            )
        if not self.has_ogr:
            logger.debug("ogr2ogr not found in PATH. Will use simulation fallback.")

    def translate(
        self, input_path: str, output_path: str, args: Optional[List[str]] = None
    ) -> str:
        """Wraps gdal_translate"""
        if not args:
            args = []

        cmd = ["gdal_translate"] + args + [input_path, output_path]

        if self.has_gdal:
            logger.info(f"Running GDAL: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"GDAL Error: {result.stderr}")
                raise RuntimeError(f"GDAL Error: {result.stderr}")
            return result.stdout
        else:
            logger.info(
                f"[SIMULATED] GDAL not found in PATH. Simulating command: {' '.join(cmd)}"
            )
            # In simulation, we might just copy the file or create a dummy output
            with open(output_path, "w") as f:
                f.write("Simulated GDAL Translate Output\n")
            return "Simulated success."

    def ogr2ogr(
        self, input_path: str, output_path: str, args: Optional[List[str]] = None
    ) -> str:
        """Wraps ogr2ogr"""
        if not args:
            args = []

        cmd = ["ogr2ogr"] + args + [output_path, input_path]

        if self.has_ogr:
            logger.info(f"Running OGR: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"OGR Error: {result.stderr}")
                raise RuntimeError(f"OGR Error: {result.stderr}")
            return result.stdout
        else:
            logger.info(
                f"[SIMULATED] OGR not found in PATH. Simulating command: {' '.join(cmd)}"
            )
            with open(output_path, "w") as f:
                f.write("Simulated OGR Output\n")
            return "Simulated success."
