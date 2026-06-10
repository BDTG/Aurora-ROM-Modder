import os
import subprocess

workspace = "/home/bdtg/Desktop/AuroraKernel"
translation_dir = os.path.join(workspace, "vietnamese_translation/Vietnamese/main")
rom_dirs = [
    os.path.join(workspace, "extracted_20260610_160317/system_dir"),
    os.path.join(workspace, "extracted_20260610_160317/product_dir"),
    os.path.join(workspace, "extracted_20260610_160317/system_ext_dir")
]
aapt2_path = os.path.join(workspace, "tools/aapt2")

def get_package_name(apk_path):
    try:
        res = subprocess.run([aapt2_path, "dump", "packagename", apk_path], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception as e:
        return None

# Scan all APKs in ROM
rom_apks = {}
for rom_dir in rom_dirs:
    if not os.path.exists(rom_dir):
        continue
    for root, dirs, files in os.walk(rom_dir):
        for file in files:
            if file.endswith(".apk"):
                apk_path = os.path.join(root, file)
                pkg = get_package_name(apk_path)
                if pkg:
                    rom_apks[file.lower()] = {
                        "name": file,
                        "path": apk_path,
                        "package": pkg
                    }

print(f"Scanned {len(rom_apks)} unique APKs in ROM.")

# Scan translation directories
translation_folders = [f for f in os.listdir(translation_dir) if os.path.isdir(os.path.join(translation_dir, f))]

matches = []
for folder in translation_folders:
    folder_lower = folder.lower()
    # Direct match or close match (e.g. without .apk extension)
    key = folder_lower if folder_lower.endswith(".apk") else folder_lower + ".apk"
    if key in rom_apks:
        matches.append((folder, rom_apks[key]))
    else:
        # Try some fuzzy matching, e.g. miuihome vs home, etc.
        # But direct match is safest first.
        pass

print(f"Found {len(matches)} direct translation matches:")
for idx, (folder, info) in enumerate(sorted(matches)):
    print(f"{idx+1}. Translation: {folder} -> ROM APK: {info['name']} (Package: {info['package']})")
