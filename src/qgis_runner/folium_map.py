import sys
from datetime import datetime
from pathlib import Path

import folium
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from logger import logger
from notebook.db import NotebookDB


class FoliumMapGenerator:
    """Generates interactive HTML maps from field notebook data using folium."""

    def __init__(self, db_path="data/field_notes.db"):
        self.db = NotebookDB(db_path=db_path)
        self.exports_dir = Path("data/exports")
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def generate_interactive_map(self, output_filename="interactive_map.html"):
        """Generates an interactive map plotting all field notes with coordinates."""
        try:
            logger.info("Gathering field notes for interactive map generation...")
            notes = self.db.get_all_notes()

            # Default center: Clear Lake, CA roughly
            default_center = [39.02, -122.75]

            # Find the first valid coordinate to use as the map center, otherwise use default
            map_center = default_center
            for note in notes:
                if note.coordinates:
                    try:
                        # Assuming coordinates are stored as "lat, lon"
                        lat_str, lon_str = note.coordinates.split(",")
                        map_center = [float(lat_str.strip()), float(lon_str.strip())]
                        break
                    except Exception:
                        continue

            logger.info(f"Initializing folium map centered at {map_center}")
            # Create a base map
            f_map = folium.Map(location=map_center, zoom_start=12, control_scale=True)

            # Add markers for each note
            marker_count = 0
            for note in notes:
                if note.coordinates:
                    try:
                        lat_str, lon_str = note.coordinates.split(",")
                        lat = float(lat_str.strip())
                        lon = float(lon_str.strip())

                        # Create popup content
                        popup_html = f"""
                        <div style="min-width: 200px;">
                            <b>Site:</b> {note.site_id}<br>
                            <b>Time:</b> {note.timestamp}<br>
                            <b>Observer:</b> {note.observer}<br>
                            <hr>
                            <p>{note.notes}</p>
                        </div>
                        """

                        # Use different marker colors based on confidence level if available
                        color = "blue"
                        if note.confidence_level == "high":
                            color = "green"
                        elif note.confidence_level == "low":
                            color = "orange"

                        folium.Marker(
                            location=[lat, lon],
                            popup=folium.Popup(popup_html, max_width=300),
                            tooltip=f"Observation: {note.site_id}",
                            icon=folium.Icon(color=color, icon="info-sign"),
                        ).add_to(f_map)
                        marker_count += 1
                    except Exception as e:
                        logger.warning(
                            f"Failed to parse coordinates '{note.coordinates}' for note {note.id}: {e}"
                        )

            # -------------------------------------------------------------
            # OFFLINE GEOSPATIAL ENHANCEMENT: Lake Shoreline Vector Overlay
            # -------------------------------------------------------------
            shoreline_path = Path("data/clear-lake-watch-repo/data/lake-shoreline.json")
            if shoreline_path.exists():
                logger.info("Found offline vector shoreline data. Rendering on map...")
                try:
                    with open(shoreline_path, "r", encoding="utf-8") as f:
                        shoreline_data = json.load(f)
                        if "rings" in shoreline_data:
                            for ring in shoreline_data["rings"]:
                                if "points" in ring:
                                    polygon_coords = [(p["latitude"], p["longitude"]) for p in ring["points"]]
                                    folium.Polygon(
                                        locations=polygon_coords,
                                        color="#3388ff",
                                        weight=2,
                                        fill=True,
                                        fill_opacity=0.2,
                                        tooltip="Clear Lake Shoreline Vector",
                                    ).add_to(f_map)
                except Exception as e:
                    logger.warning(f"Failed to plot lake shoreline: {e}")

            # -------------------------------------------------------------
            # OFFLINE GEOSPATIAL ENHANCEMENT: FHABS Warning Markers
            # -------------------------------------------------------------
            live_json_path = Path("data/sensors/live.json")
            if live_json_path.exists():
                logger.info("Found cached FHABS live data. Rendering markers on map...")
                try:
                    with open(live_json_path, "r", encoding="utf-8") as f:
                        live_data = json.load(f)
                        if "mapMarkers" in live_data:
                            for marker in live_data["mapMarkers"]:
                                lat = marker.get("latitude")
                                lon = marker.get("longitude")
                                adv = marker.get("advisory", "Unknown")
                                name = marker.get("siteName", "Unknown Site")
                                
                                # Assign color based on severity
                                adv_lower = adv.lower()
                                if "danger" in adv_lower:
                                    m_color = "red"
                                elif "warning" in adv_lower:
                                    m_color = "orange"
                                elif "caution" in adv_lower:
                                    m_color = "lightred"
                                elif "visual" in adv_lower:
                                    m_color = "purple"
                                else:
                                    m_color = "gray"

                                popup_html = f"""
                                <div style="min-width: 150px;">
                                    <h4 style="color: {m_color}; margin: 0;">FHABS: {adv}</h4>
                                    <b>Site:</b> {name}<br>
                                    <b>Date:</b> {marker.get("isoDate", "")}<br>
                                    <hr>
                                    <p>Imported via Pre-Departure Sync</p>
                                </div>
                                """

                                folium.Marker(
                                    location=[lat, lon],
                                    popup=folium.Popup(popup_html, max_width=300),
                                    tooltip=f"FHABS {adv}: {name}",
                                    icon=folium.Icon(color=m_color, icon="warning-sign"),
                                ).add_to(f_map)
                except Exception as e:
                    logger.warning(f"Failed to plot FHABS markers: {e}")

            output_path = self.exports_dir / output_filename
            f_map.save(str(output_path))

            logger.info(
                f"Successfully generated interactive map at {output_path} with {marker_count} markers."
            )
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate interactive map: {e}")
            raise
