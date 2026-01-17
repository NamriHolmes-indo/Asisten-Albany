import winreg
import json
import os
import re

REGISTRY_PATHS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]


def clean_exe_path(path):
    if not path:
        return None

    path = path.split(",")[0].strip('" ').strip()

    if path.lower().endswith(".exe") and os.path.exists(path):
        return path

    return None


def find_exe_in_folder(folder):
    if not folder or not os.path.exists(folder):
        return None

    for file in os.listdir(folder):
        if file.lower().endswith(".exe"):
            return os.path.join(folder, file)

    return None


def extract_exe_from_uninstall(uninstall_string):
    if not uninstall_string:
        return None

    match = re.search(r"([A-Z]:\\.*?\.exe)", uninstall_string)
    if match and os.path.exists(match.group(1)):
        return match.group(1)

    return None


def get_installed_apps():
    apps = []

    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for reg_path in REGISTRY_PATHS:
            try:
                with winreg.OpenKey(root, reg_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:

                                def get_value(name):
                                    try:
                                        return winreg.QueryValueEx(subkey, name)[0]
                                    except:
                                        return None

                                name = get_value("DisplayName")
                                if not name:
                                    continue

                                install_location = get_value("InstallLocation")
                                display_icon = get_value("DisplayIcon")
                                uninstall_string = get_value("UninstallString")

                                exe_path = (
                                    find_exe_in_folder(install_location)
                                    or clean_exe_path(display_icon)
                                    or extract_exe_from_uninstall(uninstall_string)
                                )

                                if not exe_path:
                                    continue

                                apps.append(
                                    {
                                        "name": name,
                                        "version": get_value("DisplayVersion"),
                                        "publisher": get_value("Publisher"),
                                        "install_location": install_location,
                                        "exe_path": exe_path,
                                    }
                                )

                        except Exception:
                            continue
            except FileNotFoundError:
                continue

    return apps


if __name__ == "__main__":
    applications = get_installed_apps()

    with open("installed_apps.json", "w", encoding="utf-8") as f:
        json.dump(applications, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(applications)} aplikasi valid (.exe) tersimpan")
