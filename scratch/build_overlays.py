import os
import shutil
import subprocess

workspace = "/home/bdtg/Desktop/AuroraKernel"
translation_dir = os.path.join(workspace, "vietnamese_translation/Vietnamese/main")
rom_dirs = [
    os.path.join(workspace, "extracted_20260610_160317/system_dir"),
    os.path.join(workspace, "extracted_20260610_160317/product_dir"),
    os.path.join(workspace, "extracted_20260610_160317/system_ext_dir")
]
output_overlay_dir = os.path.join(workspace, "extracted_20260610_160317/product_dir/overlay")
aapt2_path = os.path.join(workspace, "tools/aapt2")
android_jar = os.path.join(workspace, "tools/android.jar")
build_temp_dir = os.path.join(workspace, "scratch/build_temp")

# Ensure output and build directories exist
os.makedirs(output_overlay_dir, exist_ok=True)
if os.path.exists(build_temp_dir):
    shutil.rmtree(build_temp_dir)
os.makedirs(build_temp_dir, exist_ok=True)

def get_package_name(apk_path):
    try:
        res = subprocess.run([aapt2_path, "dump", "packagename", apk_path], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
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

print(f"Scanned {len(rom_apks)} APKs in ROM.")

# Scan translation directories
translation_folders = [f for f in os.listdir(translation_dir) if os.path.isdir(os.path.join(translation_dir, f))]

matches = []
for folder in translation_folders:
    folder_lower = folder.lower()
    key = folder_lower if folder_lower.endswith(".apk") else folder_lower + ".apk"
    if key in rom_apks:
        matches.append((folder, rom_apks[key]))

print(f"Found {len(matches)} matches. Starting RRO compile & link...")

success_count = 0
fail_count = 0
failed_apps = []

for idx, (folder, apk_info) in enumerate(sorted(matches)):
    app_name = folder.replace(".apk", "")
    pkg_name = apk_info["package"]
    src_res_dir = os.path.join(translation_dir, folder, "res")
    
    if not os.path.exists(src_res_dir):
        print(f"[{idx+1}/{len(matches)}] {app_name}: No res folder found in translation, skipping.")
        continue
        
    app_build_dir = os.path.join(build_temp_dir, app_name)
    os.makedirs(app_build_dir, exist_ok=True)
    
    # Copy res folder to build dir
    dest_res_dir = os.path.join(app_build_dir, "res")
    shutil.copytree(src_res_dir, dest_res_dir)
    
    # Create AndroidManifest.xml
    manifest_content = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{pkg_name}.overlay.vi"
    coreApp="true"
    android:versionCode="1"
    android:versionName="1.0">
    <uses-sdk android:minSdkVersion="30" android:targetSdkVersion="36"/>
    <overlay
        android:targetPackage="{pkg_name}"
        android:priority="99"
        android:isStatic="true"/>
    <application
        android:hasCode="false"
        android:extractNativeLibs="false"/>
</manifest>
"""
    manifest_path = os.path.join(app_build_dir, "AndroidManifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest_content)
        
    compiled_zip = os.path.join(app_build_dir, "compiled.zip")
    output_apk = os.path.join(output_overlay_dir, f"{app_name}OverlayVi.apk")
    
    # 1. Compile resources
    # We compile the resources using aapt2 compile
    compile_cmd = [
        aapt2_path, "compile",
        "--dir", dest_res_dir,
        "-o", compiled_zip
    ]
    
    compile_res = subprocess.run(compile_cmd, capture_output=True, text=True)
    if compile_res.returncode != 0:
        print(f"❌ [{idx+1}/{len(matches)}] {app_name}: Compilation failed.")
        print(f"Error:\n{compile_res.stderr}")
        fail_count += 1
        failed_apps.append((app_name, "compile", compile_res.stderr))
        continue
        
    # 2. Link resources
    # We link resources with android.jar to generate the APK
    link_cmd = [
        aapt2_path, "link",
        "-o", output_apk,
        "-I", android_jar,
        "--manifest", manifest_path,
        compiled_zip
    ]
    
    link_res = subprocess.run(link_cmd, capture_output=True, text=True)
    if link_res.returncode != 0:
        print(f"❌ [{idx+1}/{len(matches)}] {app_name}: Linking failed.")
        print(f"Error:\n{link_res.stderr}")
        fail_count += 1
        failed_apps.append((app_name, "link", link_res.stderr))
        # Remove partial file if exists
        if os.path.exists(output_apk):
            os.remove(output_apk)
        continue
        
    print(f"✅ [{idx+1}/{len(matches)}] {app_name}: Successfully compiled and linked. -> {os.path.basename(output_apk)}")
    success_count += 1

print("\n" + "="*50)
print(f"Build Completed!")
print(f"Successful: {success_count}/{len(matches)}")
print(f"Failed: {fail_count}/{len(matches)}")
if failed_apps:
    print("\nFailed apps summary:")
    for app, phase, err in failed_apps:
        # Show first 2 lines of error
        err_lines = err.strip().split("\n")[:2]
        err_summary = " | ".join(err_lines)
        print(f"- {app} ({phase}): {err_summary}")
print("="*50)
