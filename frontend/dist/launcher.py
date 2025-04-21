#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import traceback


# Determine if we're running as a PyInstaller bundle
def get_base_path():
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))


BACKEND_CONTAINER = "currency-backend-container"
BACKEND_IMAGE = "currency-backend"  # the name/tag you built/pulled
HOST_PORT = "8000"

FRONTEND_EXE = "main.exe"


def run_cmd(cmd):
    print(f"Running command: {' '.join(cmd)}")
    # Use CREATE_NO_WINDOW flag to hide console window
    startupinfo = None
    if os.name == "nt":  # Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        startupinfo=startupinfo,
    )
    if result.stdout:
        print("Command output:", result.stdout)
    if result.stderr:
        print("Command error:", result.stderr)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def container_exists(name):
    print(f"Checking if container {name} exists...")
    code, out, _ = run_cmd(
        ["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"]
    )
    exists = name in out.splitlines()
    print(f"Container {name} exists: {exists}")
    return exists


def container_running(name):
    print(f"Checking if container {name} is running...")
    code, out, _ = run_cmd(
        ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"]
    )
    running = name in out.splitlines()
    print(f"Container {name} is running: {running}")
    return running


def start_or_run_backend():
    try:
        if container_exists(BACKEND_CONTAINER):
            if not container_running(BACKEND_CONTAINER):
                print(f"Starting existing container `{BACKEND_CONTAINER}`…")
                code, _, err = run_cmd(["docker", "start", BACKEND_CONTAINER])
                if code != 0:
                    print("❌ Failed to start container:", err)
                    sys.exit(1)
        else:
            print(
                f"Creating & starting container `{BACKEND_CONTAINER}` from image `{BACKEND_IMAGE}`…"
            )
            code, _, err = run_cmd(
                [
                    "docker",
                    "run",
                    "-d",
                    "-p",
                    f"{HOST_PORT}:8000",
                    "--name",
                    BACKEND_CONTAINER,
                    BACKEND_IMAGE,
                ]
            )
            if code != 0:
                print("❌ Failed to run container:", err)
                sys.exit(1)

        # give it a few seconds to boot
        print("Waiting for back‑end to come up…")
        time.sleep(3)
    except Exception as e:
        print("❌ Error starting backend:", str(e))
        traceback.print_exc()
        sys.exit(1)


def launch_frontend():
    try:
        # Get the base path where all files are located
        base_path = get_base_path()
        exe = os.path.join(base_path, FRONTEND_EXE)

        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for executable at: {exe}")
        print(f"Directory contents: {os.listdir(base_path)}")

        if not os.path.exists(exe):
            print(f"❌ Cannot find `{FRONTEND_EXE}` at {exe}")
            sys.exit(1)

        print("Starting frontend application...")
        # Windows: use startfile
        try:
            print(f"Attempting to start {exe}")
            # Use CREATE_NO_WINDOW flag to hide console window
            startupinfo = None
            if os.name == "nt":  # Windows
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            subprocess.Popen([exe], startupinfo=startupinfo)
            print("Successfully started frontend")
        except Exception as e:
            print("❌ Error starting frontend:", str(e))
            traceback.print_exc()
            sys.exit(1)
    except Exception as e:
        print("❌ Error launching frontend:", str(e))
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        print("Starting launcher...")
        start_or_run_backend()
        launch_frontend()
        print("Launcher completed successfully")
        # Keep the console open for a few seconds to see any output
        time.sleep(5)
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        traceback.print_exc()
        input("Press Enter to exit...")  # Keep console open to see error
        sys.exit(1)
