import argparse
import dataclasses
import json
import sys
from pathlib import Path

from review_engine.harness.checker import CyberneticHarness
from logger import logger
from notebook.db import NotebookDB
from notebook.parser import DictationParser
from rag.indexer import DocumentIndexer
from rag.retriever import DocumentRetriever
from analysis.spatial_preprocessor import SpatialPreprocessor


def main():
    parser = argparse.ArgumentParser(
        description="FieldAware Cybernetic Ecology Harness CLI"
    )
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")

    # Existing actions
    for action in [
        "serve", "check", "index", "search", "dictate", "map", 
        "export", "gdal", "analyze", "folium", "cite", "sync", "identify"
    ]:
        subparsers.add_parser(action)

    # New preprocess-spatial command
    parser_preprocess = subparsers.add_parser('preprocess-spatial', help='Preprocess a spatial file (e.g. reproject to EPSG:4326 and simplify)')
    parser_preprocess.add_argument('input_file', help='Path to the input spatial file (Shapefile, GeoJSON, etc.)')
    parser_preprocess.add_argument('output_file', help='Path to save the standardized GeoJSON')
    parser_preprocess.add_argument('--tolerance', type=float, default=0.001, help='Geometry simplification tolerance (default: 0.001)')

    parser.add_argument(
        "text",
        nargs="?",
        help="Text to evaluate, search query, dictation, or recipe ID",
    )
    parser.add_argument(
        "--policy-dir", default="policy", help="Path to policy directory"
    )
    parser.add_argument(
        "--docs-dir", default="data/documents", help="Path to documents directory"
    )
    parser.add_argument(
        "--lm-studio-url",
        default="http://192.168.0.100:1234/v1/chat/completions",
        help="LM Studio API URL",
    )

    args = parser.parse_args()

    if args.action == "check":
        if not args.text:
            print("Error: check action requires text argument")
            return
        harness = CyberneticHarness(args.policy_dir)
        packet = harness.evaluate(args.text, artifact_name="cli_input")

        print(f"Decision: {packet.decision_state.upper()}")
        if packet.decision_state != "allow":
            print("\n--- Review Packet ---")
            print(json.dumps(dataclasses.asdict(packet), indent=2))

    elif args.action == "index":
        logger.info("Indexing documents started via CLI.")
        print("Indexing documents...")
        indexer = DocumentIndexer()
        indexer.index_directory(args.docs_dir)

    elif args.action == "search":
        if not args.text:
            print("Error: search action requires text argument as query")
            return
        print(f"Searching for: '{args.text}'\n")
        retriever = DocumentRetriever()
        cards = retriever.search(args.text)

        for idx, card in enumerate(cards):
            print(f"--- Result {idx+1} ---")
            print(f"Title: {card.metadata.title}")
            print(f"Source: {card.metadata.source} ({card.metadata.authority_level})")
            print(f"Freshness: {card.metadata.freshness_date}")
            print(f"Snippet: {card.content[:200]}...")
            print()

    elif args.action == "dictate":
        if not args.text:
            print("Error: dictate action requires unstructured text argument")
            return

        logger.info("Parsing dictation with LM Studio...")
        print("Parsing dictation with LM Studio...")
        p = DictationParser(api_url=args.lm_studio_url)
        note = p.parse(args.text)

        print(f"\nExtracted Note Details:")
        print(f"  Site: {note.site_id}")
        print(f"  Time: {note.timestamp}")
        print(f"  Notes: {note.notes}")

        print("\nRunning through Cybernetic Ecology Harness...")
        harness = CyberneticHarness(args.policy_dir)
        packet = harness.evaluate(note.notes, artifact_name="field_dictation")

        if packet.decision_state in ["require_review", "block"]:
            print(
                f"\n[BLOCKED] Dictation triggered boundary: {packet.decision_state.upper()}"
            )
            print("Cannot save note until reviewed. Review Packet generated:")
            print(json.dumps(dataclasses.asdict(packet), indent=2))
        else:
            if packet.decision_state == "warn":
                print(f"\n[WARNING] Note has warnings but will be saved:")
                print(json.dumps(dataclasses.asdict(packet), indent=2))

            logger.info("Saving dictation to local SQLite Database...")
            print("\nSaving to local SQLite Database...")
            db = NotebookDB()
            db.insert_note(note)
            print("Note successfully saved.")

    elif args.action == "map":
        if not args.text:
            print("Error: map action requires recipe id as text argument")
            return

        print(f"Loading map recipe: {args.text}")
        from qgis_runner.runner import QGISRunner

        runner = QGISRunner()
        recipe = runner.load_recipe(args.text)

        if not recipe:
            print(f"Recipe '{args.text}' not found.")
            return

        print("Checking coordinates against Cybernetic Harness...")
        harness = CyberneticHarness(args.policy_dir)
        simulated_input = "Map generation requested for simulated lake"
        packet = harness.evaluate(simulated_input, artifact_name="map_generation")

        if packet.decision_state in ["require_review", "block"]:
            print(
                f"\n[BLOCKED] Map request triggered boundary: {packet.decision_state.upper()}"
            )
            print("Cannot generate map without review. Review Packet generated:")
            print(json.dumps(dataclasses.asdict(packet), indent=2))
        else:
            print("\nGenerating simulated QGIS map...")
            mockup_path = r"C:\Users\corey\.gemini\antigravity-ide\brain\35107869-e9a8-427d-a323-cadc8baa2e69\clear_lake_qgis_mockup_1780377746106.png"
            metadata = runner.generate_map(
                recipe, 39.0, -122.8, packet.decision_state, mockup_path=mockup_path
            )

            print("Map and metadata generated successfully!")
            print(json.dumps(dataclasses.asdict(metadata), indent=2))

    elif args.action == "export":
        if not args.text:
            print(
                "Error: export action requires a base filename as text argument (e.g. recipe_id_timestamp)"
            )
            return

        logger.info(f"Generating export bundle for: {args.text}")
        print(f"Generating export bundle for: {args.text}")
        from export_engine import ExportEngine

        engine = ExportEngine()

        db = NotebookDB()
        notes = db.get_all_notes()
        notes.sort(key=lambda x: x.timestamp, reverse=True)
        recent_notes = notes[:5]

        try:
            zip_path = engine.generate_export_bundle(
                base_filename=args.text,
                site_id="Clear Lake",
                notes=recent_notes,
                review_packet=None,
            )
            logger.info(f"Successfully generated export bundle: {zip_path}")
            print(f"Successfully generated export bundle: {zip_path}")
        except Exception as e:
            logger.error(f"Failed to generate export bundle: {e}")
            print(f"Failed to generate export bundle: {e}")

    elif args.action == "gdal":
        if not args.text:
            print(
                "Error: gdal action requires a subcommand as text argument (e.g. translate, vector-clip)"
            )
            return

        from qgis_runner.gdal_wrapper import GDALWrapper

        wrapper = GDALWrapper()

        if args.text == "translate":
            print("Running GDAL Translate (simulated/actual)")
            wrapper.translate("input.tif", "output.tif")
        elif args.text == "vector-clip":
            print("Running OGR Vector Clip (simulated/actual)")
            wrapper.ogr2ogr("input.shp", "output.shp", ["-clipsrc", "clip.shp"])
        else:
            print(f"Unknown gdal subcommand: {args.text}")

    elif args.action == "analyze":
        if not args.text:
            print(
                "Error: analyze action requires script path as text argument (e.g. scripts/example_analysis.py)"
            )
            return

        logger.info(f"Running analysis script: {args.text}")
        print(f"Running analysis script: {args.text}")
        from analysis.sandbox import AnalysisSandbox

        try:
            sandbox = AnalysisSandbox()
            result = sandbox.run_script(args.text)
            print("Analysis complete. New note added to NotebookDB.")
            print("Result Summary:")
            print(result.get("notes", ""))
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            print(f"Analysis failed: {e}")

    elif args.action == "folium":
        print("Generating interactive Folium map...")
        logger.info("Generating interactive Folium map...")
        from qgis_runner.folium_map import FoliumMapGenerator

        try:
            generator = FoliumMapGenerator()
            output_path = generator.generate_interactive_map()
            print(f"Interactive map generated successfully: {output_path}")
        except Exception as e:
            print(f"Failed to generate interactive map: {e}")
            
    elif args.action == "cite":
        if not args.text:
            print("Error: cite action requires a DOI or title string (e.g. '10.1038/s41586-020-2649-2')")
            return
            
        print(f"Resolving citation for: {args.text}")
        from rag.citation import CrossrefResolver
        resolver = CrossrefResolver()
        
        # Check if it looks like a DOI (contains a slash and starts with 10.)
        if args.text.startswith("10.") and "/" in args.text:
            result = resolver.resolve_doi(args.text)
        else:
            result = resolver.search_title(args.text)
            
        if result:
            print("\n--- Citation Found ---")
            print(f"Title: {result['title']}")
            print(f"Authors: {result['authors']}")
            print(f"Journal: {result['journal']} ({result['year']})")
            print(f"DOI: {result['url']}")
            print("\nFormatted:")
            print(result['formatted_citation'])
            print("----------------------")
        else:
            print("\nCould not resolve citation. You may be offline, or the query returned no results.")

    elif args.action == "sync":
        from notebook.git_sync import GitSync
        print("Starting Git peer-to-peer sync...")
        sync = GitSync()
        success = sync.sync(remote="origin", branch="main")
        if success:
            print("Sync complete. Rebuilding SQLite cache...")
            db = NotebookDB()
            print("SQLite cache rebuilt.")
        else:
            print("Sync failed. Ensure you have network access or a local peer reachable.")

    elif args.action == "identify":
        from analysis.vision import VisionAnalyzer
        if not args.text:
            print("Error: Please provide the path to an image. (e.g. cli.py identify path/to/image.jpg)")
            sys.exit(1)
        
        print(f"Loading local vision model for {args.text}...")
        analyzer = VisionAnalyzer()
        results = analyzer.identify_species(args.text)
        
        if results:
            print("\nTop Predictions:")
            for i, res in enumerate(results):
                label = res.get('label', 'Unknown')
                score = res.get('score', 0.0)
                print(f"  {i+1}. {label} (Confidence: {score:.1%})")
        else:
            print("\nCould not classify the image.")

    elif args.action == "preprocess-spatial":
        import sys
        if not hasattr(args, 'input_file') or not hasattr(args, 'output_file') or not args.input_file or not args.output_file:
            print("Error: Please provide an input file and an output file path.")
            print("Usage: cli.py preprocess-spatial <input> <output> [--tolerance 0.001]")
            sys.exit(1)
            
        print(f"Starting preprocessing pipeline for {args.input_file}...")
        try:
            out_path = SpatialPreprocessor.process_pipeline(args.input_file, args.output_file, args.tolerance)
            print(f"Successfully preprocessed spatial data. Saved to {out_path}")
        except Exception as e:
            print(f"Spatial preprocessing failed: {e}")

    elif args.action == "serve":
        import os
        import sys

        import uvicorn

        # Add src to pythonpath so web.app resolves
        sys.path.insert(0, str(Path(__file__).parent))
        # Ensure we run from the project root so data/exports resolves
        os.chdir(Path(__file__).parent.parent)
        print("Starting FieldAware Local Dashboard on http://127.0.0.1:8000")
        uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=False)

    elif args.action == "desktop":
        from desktop import run_desktop

        run_desktop()


if __name__ == "__main__":
    main()
