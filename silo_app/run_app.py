# -*- coding: utf-8 -*-
import os
import sys
import socket
import threading
import time
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8501


def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def wait_for_server(host: str, port: int, timeout: float = 30.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if is_port_open(host, port):
            return True
        time.sleep(0.25)
    return False


def open_browser_once() -> None:
    url = f"http://{HOST}:{PORT}"
    if wait_for_server(HOST, PORT, timeout=30):
        webbrowser.open_new(url)


def project_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent


def main() -> None:
    url = f"http://{HOST}:{PORT}"

    if is_port_open(HOST, PORT):
        webbrowser.open_new(url)
        return

    root = project_root()
    sys.path.insert(0, str(root))

    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_PORT"] = str(PORT)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = HOST
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"

    app_path = str(root / "app" / "main.py")

    threading.Thread(target=open_browser_once, daemon=True).start()

    from streamlit.web import cli as stcli

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.headless=true",
        f"--server.address={HOST}",
        f"--server.port={PORT}",
        "--server.fileWatcherType=none",
        "--browser.gatherUsageStats=false",
        f"--browser.serverAddress={HOST}",
        "--global.developmentMode=false",
    ]

    sys.exit(stcli.main())


if __name__ == "__main__":
    main()