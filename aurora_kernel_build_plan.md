# Kế hoạch Biên dịch: Kernel cho Xiaomi 14 Ultra (aurora)

Tài liệu này phác thảo quy trình từng bước để thiết lập môi trường, đồng bộ hóa các kho lưu trữ mã nguồn (repositories) và biên dịch kernel tùy chỉnh cho **Xiaomi 14 Ultra (tên mã: aurora)** sử dụng nhánh phần mềm nguồn mở Android 14 (`aurora-u-oss`).

---

## 📋 Yêu cầu & Thiết lập Môi trường

Các nhân kernel Android hiện đại (từ Android 13 trở đi) sử dụng **Kleaf**, một hệ thống build dựa trên Bazel. Một trong những lợi ích lớn nhất của Kleaf là nó tự động tải xuống và sử dụng các bộ công cụ hermetic toolchain (các phiên bản Clang, GCC và các tệp nhị phân liên kết) tương thích. Bạn không cần phải cài đặt trình biên dịch chéo (cross-compiler) thủ công.

### 1. Yêu cầu Hệ thống Máy chủ (Host)
*   **Hệ điều hành:** Linux (khuyến nghị sử dụng Ubuntu 22.04 LTS trở lên).
*   **Phần cứng:** Tối thiểu 16 GB RAM (khuyến nghị 32 GB) và hơn 150 GB dung lượng đĩa trống.
*   **Mở khóa Bootloader (Unlocked Bootloader):** Bắt buộc phải được mở khóa để có thể flash các phân vùng boot/vendor đã biên dịch vào Xiaomi 14 Ultra.

### 2. Cài đặt các Gói Phụ thuộc
Chạy lệnh sau trên máy chủ build của bạn để cài đặt các tiện ích hệ thống và thư viện cần thiết:
```bash
sudo apt update && sudo apt install -y \
    build-essential bc bison flex libssl-dev libelf-dev cpio \
    rsync git git-lfs python3 curl libncurses-dev squashfs-tools \
    android-sdk-libsparse-utils
```

### 3. Cài đặt Công cụ Repo của Google
Android Common Kernel yêu cầu công cụ `repo` của Google để thực hiện đồng bộ hóa mã nguồn.
```bash
mkdir -p ~/.bin
PATH="${HOME}/.bin:${PATH}"
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/.bin/repo
chmod a+rx ~/.bin/repo
```

---

## 🗄️ Cấu trúc Thư mục Workspace

Để biên dịch thành công, các repository phải được đặt trong một sơ đồ thư mục chính xác. Hệ thống Bazel sẽ phân tích các đường dẫn tương đối so với thư mục gốc (workspace root).

```
workspace_root/                   <-- Thư mục gốc build dự án (ví dụ: /home/bdtg/Desktop/AuroraKernel)
├── WORKSPACE                     <-- Liên kết tượng trưng (Symlink) trỏ đến msm-kernel/bazel.WORKSPACE
├── BUILD.bazel                   <-- Liên kết tượng trưng (Symlink) trỏ đến msm-kernel/BUILD.bazel
├── build/                        <-- Đồng bộ từ Android GKI (Hệ thống build Kleaf)
├── common/                       <-- Đồng bộ từ Android GKI (Mã nguồn kernel chung)
├── msm-kernel/                   <-- Mã nguồn Xiaomi Kernel OpenSource (nhánh aurora-u-oss)
│   ├── arch/arm64/boot/dts/
│   │   └── vendor/               <-- Device Tree của Xiaomi (kernel_devicetree)
│   │       ├── qcom/
│   │       ├── BUILD.bazel
│   │       └── Makefile
│   ├── build_with_bazel.py
│   └── ...
├── vendor/
│   └── qcom/
│       └── opensource/           <-- Trình điều khiển ngoài cây (Out-of-tree drivers - Tùy chọn, clone nếu cần)
│           ├── camera-kernel/
│           ├── audio-kernel/
│           ├── display-drivers/
│           └── wlan/
└── prebuilts/                    <-- Đồng bộ từ GKI (Các công cụ hermetic)
```

---

## 📥 Đồng bộ hóa Mã nguồn

Thực hiện các lệnh sau theo trình tự để khởi tạo workspace GKI và clone các repository của Xiaomi.

### Bước 1: Khởi tạo Workspace AOSP GKI (Android 14 - Kernel 6.1)
Khởi tạo và đồng bộ hóa repository Android Common Kernel (ACK):
```bash
# Khởi tạo cây thư mục GKI
repo init -u https://android.googlesource.com/kernel/manifest -b android14-6.1
repo sync -c -j$(nproc)
```

### Bước 2: Clone Xiaomi Kernel OpenSource
Tải về cây nguồn kernel của Xiaomi cho nền tảng Pinehurst/Pineapple (Snapdragon 8 Gen 3) và đặt tên thư mục là `msm-kernel`:
```bash
git clone -b aurora-u-oss https://github.com/MiCode/Xiaomi_Kernel_OpenSource.git msm-kernel
```

### Bước 3: Clone Device Tree của Xiaomi
Clone các tệp tin device tree vào thư mục con `vendor` đã được thiết lập sẵn trong `msm-kernel`:
```bash
git clone -b aurora-u-oss https://github.com/MiCode/kernel_devicetree.git msm-kernel/arch/arm64/boot/dts/vendor
```

### Bước 4: Clone các Driver ngoài cây (Tùy chọn nhưng Khuyến nghị)
Nếu quá trình build kernel của bạn yêu cầu các mô-đun driver ngoài của nhà sản xuất, hãy clone chúng vào đường dẫn `vendor/qcom/opensource`:
```bash
mkdir -p vendor/qcom/opensource

# Camera Kernel
git clone -b aurora-u-oss https://github.com/MiCode/vendor_qcom_opensource_camera-kernel.git vendor/qcom/opensource/camera-kernel

# WLAN Driver
git clone -b aurora-u-oss https://github.com/MiCode/vendor_qcom_opensource_wlan.git vendor/qcom/opensource/wlan

# Audio Kernel
git clone -b aurora-u-oss https://github.com/MiCode/vendor_qcom_opensource_audio-kernel.git vendor/qcom/opensource/audio-kernel

# Display Drivers
git clone -b aurora-u-oss https://github.com/MiCode/vendor_qcom_opensource_display-drivers.git vendor/qcom/opensource/display-drivers
```

### Bước 5: Liên kết Cấu hình Workspace
Tạo các symlink ở thư mục gốc để kích hoạt các cấu hình Bazel của Xiaomi:
```bash
ln -sf msm-kernel/bazel.WORKSPACE WORKSPACE
ln -sf msm-kernel/BUILD.bazel BUILD.bazel
```

---

## 🛠️ Biên dịch Kernel

Sau khi cấu trúc thư mục đã được thiết lập đầy đủ, bạn có thể bắt đầu quá trình biên dịch.

### Phương pháp A: Build bằng Bazel/Kleaf (Khuyến nghị)
Sử dụng script build wrapper chính thức từ Qualcomm để gọi Bazel và trích xuất các sản phẩm biên dịch:

```bash
# Thực hiện tại thư mục gốc workspace:
python3 msm-kernel/build_with_bazel.py -t aurora gki
```
*   `-t aurora gki` định nghĩa hồ sơ chipset mục tiêu (`aurora` cho Xiaomi 14 Ultra) và cấu hình bản build (`gki` để tương thích với Generic Kernel Image).
*   Các sản phẩm đầu ra (bao gồm file ảnh kernel `Image`, các tệp device tree compiled `*.dtb` và các mô-đun driver `*.ko`) sẽ được tạo ra tại thư mục `out/msm-kernel-aurora-gki/dist/`.

> [!TIP]
> Nếu bạn muốn tùy chỉnh các thông số cấu hình kernel trước khi biên dịch (ví dụ: kích hoạt KernelSU hoặc tinh chỉnh governor), bạn có thể chạy menuconfig trước:
> ```bash
> python3 msm-kernel/build_with_bazel.py -t aurora gki --menuconfig
> ```

---

## ⚠️ Cảnh báo Flash & Các Bước Khôi phục

Việc nạp (flash) một kernel tùy chỉnh lên các thiết bị Snapdragon 8 Gen 3 hiện đại (sử dụng phân vùng động & GKI) đòi hỏi sự thận trọng cao.

> [!CAUTION]
> Các nhân Android hiện đại thực thi nghiêm ngặt cơ chế GKI (Generic Kernel Image) và KMI (Kernel Module Interface). Nếu kernel được biên dịch có chữ ký KMI khác với ROM gốc của bạn, các mô-đun của bên thứ ba (Wi-Fi, Audio, Camera) sẽ không thể tải được, dẫn đến tình trạng bootloop hoặc lỗi phần cứng.

### Các Bước Khôi phục Khuyến nghị:
1.  **Sao lưu các tệp ảnh phân vùng gốc:** Trước khi flash, hãy trích xuất các file `boot.img`, `vendor_boot.img`, và `init_boot.img` gốc từ gói ROM fastboot hiện tại của thiết bị.
2.  **Đóng gói lại Kernel (Repack):** Sử dụng các công cụ như [AnyKernel3](https://github.com/osm0sis/AnyKernel3) để đóng gói file `Image` và các mô-đun `*.ko` đã biên dịch của bạn. AnyKernel3 chèn trực tiếp kernel vào boot image mà không sửa đổi các thiết lập khác, giảm thiểu tối đa nguy cơ bootloop.
3.  **Flash boot image:**
    ```bash
    fastboot flash boot boot.img
    # Hoặc đối với các thiết bị hiện đại:
    fastboot flash init_boot init_boot.img
    ```
4.  **Khôi phục Khẩn cấp:** Nếu điện thoại bị bootloop, hãy đưa máy về chế độ fastboot và nạp lại các tệp ảnh gốc đã sao lưu:
    ```bash
    fastboot flash boot boot_stock.img
    fastboot flash init_boot init_boot_stock.img
    fastboot reboot
    ```
