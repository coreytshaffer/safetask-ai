import os
import sys
import threading
import time
from pathlib import Path

import requests
import uvicorn
import webview

# Add src to pythonpath so web.app resolves
sys.path.insert(0, str(Path(__file__).parent))


def start_server():
    # Ensure we run from the project root so data/exports resolves
    os.chdir(Path(__file__).parent.parent)
    from dotenv import load_dotenv
    load_dotenv()
    host_ip = os.environ.get("HOST_IP", "127.0.0.1")
    uvicorn.run("web.app:app", host=host_ip, port=8000, reload=False)


def check_server():
    """Wait for the FastAPI server to be ready before rendering the window."""
    import os
    from dotenv import load_dotenv
    load_dotenv()
    host_ip = os.environ.get("HOST_IP", "127.0.0.1")
    url = f"http://{host_ip}:8000/"
    for _ in range(50):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.1)
    return False


def run_desktop():
    print("Initializing Cybernetic Ecology Desktop Environment...")

    # Start the server in a daemon thread so it dies when the window closes
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Booting local intelligence nodes...")
    if check_server():
        print("Nodes ready. Launching interface.")

        host_ip = os.environ.get("HOST_IP", "127.0.0.1")
        # Create a chromeless, native window pointing to the local dashboard
        webview.create_window(
            title="FieldAware Cybernetic Workbench",
            url=f"http://{host_ip}:8000",
            width=1280,
            height=850,
            text_select=True,
            zoomable=True,
            frameless=False,  # Set to True for a fully custom drag region, False for standard native window
            background_color="#0f172a",  # Matches our dark mode bg
        )

        # Start the GUI event loop
        webview.start()
        print("Shutting down local intelligence nodes...")
    else:
        print("Critical Failure: Local server could not start.")


if __name__ == "__main__":
    run_desktop()
