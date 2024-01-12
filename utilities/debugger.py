"""Debugger utility for VS Code.

Based on: https://blog.theodo.com/2020/05/debug-flask-vscode/
"""

import os


def initialize_if_needed():
    """Initialize the debugger if needed."""

    USE_DEBUGGER = os.getenv("DEBUGGER", "False").lower() in ("true", "1", "t")

    if USE_DEBUGGER:
        import multiprocessing

        pid = multiprocessing.current_process().pid
        if pid and pid > 1:
            import debugpy

            PORT_DEBUGGER = int(os.getenv("PORT_DEBUGGER", 10001))
            IP = "0.0.0.0"
            debugpy.listen((IP, PORT_DEBUGGER))
            print(f"🔌 Debugger is listening on http://{IP}:{PORT_DEBUGGER}", flush=True)
            print("⏳ Waiting for VS Code debugger to be attached, press F5 in VS Code.", flush=True)
            debugpy.wait_for_client()
            print("🎉 VS Code debugger attached, enjoy debugging...", flush=True)
