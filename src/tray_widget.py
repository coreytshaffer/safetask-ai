import os
import json
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

import sys

# Add triagecore to path
triagecore_path = Path(__file__).parent.parent / "triagecore"
if str(triagecore_path) not in sys.path:
    sys.path.insert(0, str(triagecore_path))

try:
    from triage_core.config import default_config
    ACTIVE_BACKEND = default_config.get_global("backend", "default_model", "Unknown")
except ImportError:
    ACTIVE_BACKEND = "local-model"

LEDGER_PATH = Path(".triagecore/ledger.jsonl")

def create_image():
    # Generate a simple 64x64 icon (a green circle on a dark background)
    image = Image.new('RGB', (64, 64), color=(15, 23, 42))
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill=(34, 197, 94))
    return image

def get_ledger_stats():
    """Reads the ledger and returns basic stats."""
    tasks_processed = 0
    energy_kwh = 0.0
    
    if not LEDGER_PATH.exists():
        return tasks_processed, energy_kwh
        
    try:
        with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("event_type") == "model_evaluated":
                        tasks_processed += 1
                        result = entry.get("details", {}).get("result", {})
                        if isinstance(result, dict):
                            energy_kwh += result.get("resource_usage", {}).get("energy_kwh_estimate", 0.0)
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass
        
    return tasks_processed, energy_kwh

class TriageTrayWidget:
    def __init__(self, webview_window=None):
        self.webview_window = webview_window
        self.icon = pystray.Icon("triagecore_tray", create_image(), "TriageCore Status")
        
        self.stats_text = "Stats loading..."
        self.icon.menu = self._build_menu()
        
        self.running = False
        
    def _build_menu(self):
        return pystray.Menu(
            item("TriageCore Desktop", lambda: None, enabled=False),
            item(lambda text: f"Backend: {ACTIVE_BACKEND}", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item(lambda text: self.stats_text, lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Show Dashboard", self.show_dashboard),
            item("Quit", self.quit_app)
        )

    def update_stats_loop(self):
        """Background loop to periodically update the menu stats."""
        while self.running:
            tasks, energy = get_ledger_stats()
            # Update dynamic text
            self.stats_text = f"Tasks: {tasks} | Energy Saved: {energy:.5f} kWh"
            # Update menu to trigger refresh
            self.icon.menu = self._build_menu()
            # On some OS, update_menu needs to be explicitly called
            if hasattr(self.icon, 'update_menu'):
                self.icon.update_menu()
            time.sleep(5)
            
    def show_dashboard(self, icon, item):
        if self.webview_window:
            # Tell pywebview to restore/focus the window
            self.webview_window.restore()
            self.webview_window.show()

    def quit_app(self, icon, item):
        self.running = False
        self.icon.stop()
        if self.webview_window:
            self.webview_window.destroy()

    def run(self):
        self.running = True
        # Start the background stats updater
        threading.Thread(target=self.update_stats_loop, daemon=True).start()
        # Run detached runs the icon loop in a background thread
        self.icon.run_detached()

def start_tray(webview_window=None):
    widget = TriageTrayWidget(webview_window=webview_window)
    widget.run()
    return widget
