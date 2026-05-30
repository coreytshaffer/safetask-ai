# SafeTask AI - Zero-Dependency Local Static Server & CORS-Bypass Proxy
# Serves static files on port 8080 and proxies "/api/*" to LM Studio on port 1234

import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os
import sys

PORT = 8080
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default request logger to keep console logs clean
        pass

    def do_OPTIONS(self):
        # Respond to CORS preflight requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def handle_proxy(self):
        # Proxy requests from /api/* to LM_STUDIO_URL/*
        path_suffix = self.path[5:]  # Strip "/api/"
        target_url = f"{LM_STUDIO_URL}/{path_suffix}"
        
        # Read the body content if present
        content_length = int(self.headers.get('Content-Length', 0))
        req_body = self.rfile.read(content_length) if content_length > 0 else None
        
        # Forward headers, ensuring Content-Type and Authorization are kept
        headers = {
            "Content-Type": self.headers.get("Content-Type", "application/json")
        }
        if "Authorization" in self.headers:
            headers["Authorization"] = self.headers["Authorization"]

        # Build and send proxy request to LM Studio
        req = urllib.request.Request(
            target_url,
            data=req_body,
            headers=headers,
            method=self.command
        )
        
        try:
            with urllib.request.urlopen(req, timeout=300) as response:
                self.send_response(response.status)
                
                # Forward back headers safely
                for key, val in response.getheaders():
                    if key.lower() not in ['transfer-encoding', 'connection', 'content-length']:
                        self.send_header(key, val)
                
                # Inject browser CORS bypass headers
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            err_response = {
                "error": {
                    "message": f"Could not connect to LM Studio at {LM_STUDIO_URL}. Please confirm that LM Studio is active and 'Start Server' is enabled.",
                    "details": str(e)
                }
            }
            self.wfile.write(json.dumps(err_response).encode('utf-8'))

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_proxy()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.handle_proxy()
        else:
            self.send_error(404, "File not found")

def run():
    # Force bypass of system environment proxies for localhost/local APIs
    proxy_support = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)

    # Anchor server execution context in script folder location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Configure socket server with reuse enabled to prevent port locks
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
            print("=============================================================")
            print("         SafeTask AI Local Server & Proxy Active")
            print("=============================================================")
            print(f" Serving safe compliance PWA at: http://localhost:{PORT}")
            print(f" CORS bypass API proxy directed to: {LM_STUDIO_URL}")
            print(" Keep this terminal open while operating SafeTask AI.")
            print("=============================================================")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down local server...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal Server Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()
