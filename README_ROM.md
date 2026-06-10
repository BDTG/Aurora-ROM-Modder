# Aurora ROM Modder for Xiaomi 14 Ultra (aurora)

Automated modding tool and overlays for customizing **Xiaomi 14 Ultra (aurora)** HyperOS 3 China ROM (Android 16).

## 🚀 Features

*   **Automated RRO Overlay Compiler:**
    *   Scans ROM partitions (`system`, `product`, `system_ext`) and automatically compiles RRO Overlay APKs for matching translation folders.
    *   Integrated **37 Vietnamese translation modules** sourced directly from the latest Xiaomi.eu translations.
*   **Kaorios-Toolbox System Integration:**
    *   Pre-installs `KaoriosToolbox.apk` into `/product/priv-app/KaoriosToolbox/` with custom permission whitelist to prevent bootloops.
    *   Includes `com.kousei.kaorios.xml` signatures whitelist.
*   **Bootloader Spoofing & Tweak Injector:**
    *   Automated injection of bootloader-hiding properties (`ro.boot.flash.locked=1`, `ro.boot.verifiedbootstate=green`, etc.) into `system/build.prop`, `product/build.prop`, and `system_ext/build.prop` files.
*   **EROFS Unpack/Repack Tools:**
    *   Uses GKI prebuilt `fsck.erofs` and `mkfs.erofs` to extract and pack EROFS partition images safely with proper owner (`--all-root`) and SELinux contexts.

## 📁 Repository Structure

*   `/tools/`: Extractor binaries (`payload-dumper-go`), resource compilers (`aapt2`, `android.jar`), and Kaorios assets.
*   `/vietnamese_translation/`: XML translations from Xiaomi.eu.
*   `/scratch/build_overlays.py`: Python automation script to compile RRO overlays.
*   `/flash_instructions.md`: Detailed flashing guide to bypass AVB and flash modded system partitions.

## 🛠️ Modding Workflow

### 1. Extract Partitions
Extract the partitions from `payload.bin` of the ROM zip:
```bash
./tools/payload-dumper-go -p system,product,system_ext payload.bin
```
Extract EROFS images:
```bash
./prebuilts/kernel-build-tools/linux-x86/bin/fsck.erofs --extract=./system_dir system.img
./prebuilts/kernel-build-tools/linux-x86/bin/fsck.erofs --extract=./product_dir product.img
./prebuilts/kernel-build-tools/linux-x86/bin/fsck.erofs --extract=./system_ext_dir system_ext.img
```

### 2. Build Translation Overlays
Run the python compiler:
```bash
python3 scratch/build_overlays.py
```
This compiles 37 overlay APKs and copies them directly into `product_dir/overlay/`.

### 3. Integrate Kaorios-Toolbox & Edit Props
*   Copy `KaoriosPatcher.apk` to `product_dir/priv-app/KaoriosToolbox/KaoriosToolbox.apk`.
*   Copy permissions XML to `product_dir/etc/permissions/com.kousei.kaorios.xml`.
*   Apply build.prop edits (locked bootloader properties).

### 4. Repack Images
```bash
# Repack system
./prebuilts/kernel-build-tools/linux-x86/bin/mkfs.erofs -z lz4 --all-root --mount-point=/ system.img system_dir

# Repack product
./prebuilts/kernel-build-tools/linux-x86/bin/mkfs.erofs -z lz4 --all-root --mount-point=/product product.img product_dir

# Repack system_ext
./prebuilts/kernel-build-tools/linux-x86/bin/mkfs.erofs -z lz4 --all-root --mount-point=/system_ext system_ext.img system_ext_dir
```

## 🛡️ Flashing
Follow the instructions in `flash_instructions.md` to flash the output images (`system.img`, `product.img`, `system_ext.img`) along with `vbmeta.img` and `vbmeta_system.img` with AVB verification disabled:
```bash
fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
fastboot flash --disable-verity --disable-verification vbmeta_system vbmeta_system.img
fastboot reboot fastboot
fastboot flash system system.img
fastboot flash product product.img
fastboot flash system_ext system_ext.img
```
