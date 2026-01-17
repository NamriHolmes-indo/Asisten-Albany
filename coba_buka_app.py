import json
import os
import subprocess

JSON_FILE = "installed_apps.json"


def load_apps():
    if not os.path.exists(JSON_FILE):
        print("❌ File installed_apps.json tidak ditemukan")
        return []

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_apps(apps, keyword):
    keyword = keyword.lower()
    return [app for app in apps if app.get("name") and keyword in app["name"].lower()]


def get_exe_path(app):
    exe = app.get("exe_path")
    if exe and exe.lower().endswith(".exe") and os.path.exists(exe):
        return exe

    install_dir = app.get("install_location")
    if install_dir and os.path.exists(install_dir):
        for file in os.listdir(install_dir):
            if file.lower().endswith(".exe"):
                return os.path.join(install_dir, file)

    return None


def open_application(exe_path):
    exe_dir = os.path.dirname(exe_path)

    try:
        process = subprocess.Popen([exe_path], cwd=exe_dir)
        process.wait()
        print("🛑 Aplikasi sudah ditutup")
    except Exception as e:
        print(f"❌ Gagal membuka aplikasi: {e}")


def main():
    apps = load_apps()
    if not apps:
        return

    keyword = input("Masukkan nama aplikasi: ").strip()
    if not keyword:
        print("❌ Nama aplikasi kosong")
        return

    matches = search_apps(apps, keyword)

    if not matches:
        print("❌ Aplikasi tidak ditemukan")
        return

    resolved_apps = []

    for app in matches:
        exe_path = get_exe_path(app)
        app["_resolved_exe"] = exe_path
        resolved_apps.append(app)

    if len(resolved_apps) == 1:
        app = resolved_apps[0]
        print("\nAplikasi ditemukan:")
        print(f"- Nama  : {app.get('name')}")
        print(f"- Versi : {app.get('version')}")
        print(f"- Path  : {app.get('_resolved_exe')}")
    else:
        print("\nDitemukan lebih dari satu aplikasi:")
        for i, app in enumerate(resolved_apps, start=1):
            print(f"{i}. {app.get('name')} (Version: {app.get('version')})")
            print(f"   Path: {app.get('_resolved_exe')}")

        while True:
            try:
                choice = int(input("\nPilih nomor aplikasi: "))
                if 1 <= choice <= len(resolved_apps):
                    app = resolved_apps[choice - 1]
                    break
                else:
                    print("❌ Nomor tidak valid")
            except ValueError:
                print("❌ Masukkan angka")

    exe_path = app.get("_resolved_exe")

    if not exe_path:
        print("❌ File executable tidak ditemukan")
        return

    print(f"\n✅ Membuka: {app.get('name')}")
    print(f"📂 Path: {exe_path}")
    open_application(exe_path)


if __name__ == "__main__":
    main()
