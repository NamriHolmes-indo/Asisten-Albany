import json
import os
import subprocess
from typing import List, Dict, Optional

JSON_FILE = "installed_apps.json"


def load_apps(json_file: str = JSON_FILE) -> List[Dict]:
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"File {json_file} tidak ditemukan")

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def search_apps(apps: List[Dict], keyword: str) -> List[Dict]:
    keyword = keyword.lower()
    return [app for app in apps if app.get("name") and keyword in app["name"].lower()]


def get_exe_path(app: Dict) -> Optional[str]:
    exe = app.get("exe_path")
    if exe and exe.lower().endswith(".exe") and os.path.exists(exe):
        return exe

    install_dir = app.get("install_location")
    if install_dir and os.path.exists(install_dir):
        for file in os.listdir(install_dir):
            if file.lower().endswith(".exe"):
                return os.path.join(install_dir, file)

    return None


def resolve_apps(apps: List[Dict]) -> List[Dict]:
    resolved = []

    for app in apps:
        exe_path = get_exe_path(app)
        if exe_path:
            new_app = dict(app)
            new_app["exe_path"] = exe_path
            resolved.append(new_app)

    return resolved


def open_application_and_wait(exe_path: str) -> int:
    exe_dir = os.path.dirname(exe_path)

    process = subprocess.Popen([exe_path], cwd=exe_dir)

    process.wait()
    return process.returncode


def launch_app_by_name(
    app_name: str,
    json_file: str = JSON_FILE,
    pick_index: int | None = None,
    wait: bool = True,
) -> Dict:
    """
    app_name   : keyword aplikasi
    pick_index : index pilihan (0-based) jika ada lebih dari 1
    wait       : tunggu sampai aplikasi ditutup
    """

    apps = load_apps(json_file)
    matches = search_apps(apps, app_name)
    resolved = resolve_apps(matches)

    if not resolved:
        raise RuntimeError("Aplikasi tidak ditemukan atau tidak punya executable")

    if len(resolved) > 1 and pick_index is None:
        return {"status": "multiple", "apps": resolved}

    app = resolved[pick_index or 0]

    if wait:
        exit_code = open_application_and_wait(app["exe_path"])
    else:
        subprocess.Popen([app["exe_path"]], cwd=os.path.dirname(app["exe_path"]))
        exit_code = None

    return {
        "status": "launched",
        "name": app.get("name"),
        "version": app.get("version"),
        "exe_path": app.get("exe_path"),
        "exit_code": exit_code,
    }
