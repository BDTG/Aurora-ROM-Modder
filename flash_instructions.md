# Hướng dẫn Flash ROM Mod & Kernel Custom cho Xiaomi 14 Ultra (aurora)

Tài liệu này hướng dẫn chi tiết quy trình flash các phân vùng đã mod (Việt hóa RRO, tích hợp Kaorios-Toolbox, ẩn bootloader) kết hợp với Kernel Aurora tùy chỉnh (dựng từ mã nguồn, tích hợp KernelSU-Next và underclock CPU) lên thiết bị của bạn.

---

## 📂 Danh sách các Tệp tin đã chuẩn bị

Toàn bộ các tệp tin cần thiết được lưu trữ tại thư mục [extracted_20260610_160317/](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/):

1.  **Phân vùng hệ thống đã Mod:**
    *   [system.img](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/system.img) (Đã ẩn bootloader & bảo mật trong [build.prop](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/system_dir/system/build.prop)).
    *   [product.img](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/product.img) (Đã tích hợp 37 gói Việt hóa RRO Overlay, ứng dụng [KaoriosToolbox.apk](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/product_dir/priv-app/KaoriosToolbox/KaoriosToolbox.apk) và file phân quyền [com.kousei.kaorios.xml](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/product_dir/etc/permissions/com.kousei.kaorios.xml)).
    *   [system_ext.img](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/system_ext.img) (Đã thêm cấu hình ẩn bootloader).
2.  **Phân vùng bảo mật gốc (dùng để bypass AVB):**
    *   [vbmeta.img](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/vbmeta.img)
    *   [vbmeta_system.img](file:///home/bdtg/Desktop/AuroraKernel/extracted_20260610_160317/vbmeta_system.img)
3.  **Kernel Custom & KernelSU-Next:**
    *   [Aurora-Kernel-aurora-GKI-v1.1-Optimized.zip](file:///home/bdtg/Desktop/AuroraKernel/Aurora-Kernel-aurora-GKI-v1.1-Optimized.zip) (Chứa nhân `Image` và các module đã tối ưu hóa mạng BBR/RAM ZRAM).

---

## ⚠️ LƯU Ý QUAN TRỌNG TRƯỚC KHI THỰC HIỆN

> [!CAUTION]
> *   **KHÔNG ĐƯỢC khóa lại Bootloader (`fastboot oem lock`)** sau khi đã flash ROM mod hoặc Kernel tùy chỉnh. Thiết bị sẽ bị hard-brick ngay lập tức.
> *   Đảm bảo máy đã được unlock bootloader thành công.
> *   Sao lưu toàn bộ dữ liệu quan trọng và phân vùng EFS (IMEI) qua TWRP trước khi tiến hành để phòng ngừa rủi ro.

---

## 🛠️ Quy trình các bước thực hiện

### Bước 1: Vô hiệu hóa tính năng Android Verified Boot (AVB)
Do chúng ta thay đổi cấu trúc phân vùng hệ thống (`system`, `product`, `system_ext`), hệ thống bảo mật AVB sẽ chặn khởi động gây bootloop nếu không được tắt:

1.  Đưa thiết bị vào chế độ **Fastboot** (Nhấn giữ Nguồn + Giảm âm lượng).
2.  Chạy các lệnh sau trên máy tính (đảm bảo terminal đang ở thư mục chứa file img):
    ```bash
    fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
    fastboot flash --disable-verity --disable-verification vbmeta_system vbmeta_system.img
    ```

### Bước 2: Flash các Phân vùng Dynamic qua Fastbootd
Trên Snapdragon 8 Gen 3 (Android 14/15/16), các phân vùng logic nằm trong `super` cần được flash ở chế độ **Fastbootd**:

1.  Chuyển từ chế độ Fastboot sang chế độ **Fastbootd**:
    ```bash
    fastboot reboot fastboot
    ```
    *(Màn hình điện thoại sẽ chuyển sang giao diện Recovery có chữ "fastbootd")*
2.  Tiến hành flash lần lượt các phân vùng đã mod:
    ```bash
    fastboot flash system system.img
    fastboot flash product product.img
    fastboot flash system_ext system_ext.img
    ```
3.  Xóa dữ liệu (Factory Reset) nếu bạn chuyển từ ROM gốc chưa mod hoặc bị lỗi (Khuyên dùng):
    ```bash
    fastboot -w
    ```

### Bước 3: Nạp Kernel Aurora tùy chỉnh (Có KernelSU-Next)
Cách flash nhân GKI đã compile:

1.  Khởi động máy vào Recovery tùy chỉnh (như TWRP).
2.  Sao chép tệp zip [Aurora-Kernel-aurora-GKI-v1.1-Optimized.zip](file:///home/bdtg/Desktop/AuroraKernel/Aurora-Kernel-aurora-GKI-v1.1-Optimized.zip) vào bộ nhớ máy.
3.  Chọn cài đặt (Install) tệp zip này từ TWRP để flash nhân và các module tương thích vào phân vùng `boot`.
4.  Reboot hệ thống.

---

## 🎯 Cấu hình sau khi khởi động thành công

Sau khi máy khởi động vào màn hình chính, bạn thực hiện các bước sau để kích hoạt tiếng Việt và tối ưu hóa ẩn root:

1.  **Kích hoạt Tiếng Việt:** 
    *   Vào **Settings (Cài đặt) -> Additional Settings -> Languages & input -> Languages** và chọn **Tiếng Việt**. Nhờ RRO Overlays, toàn bộ hệ thống đã được dịch chuẩn theo Xiaomi.eu.
2.  **Ứng dụng Kaorios-Toolbox:**
    *   Mở ứng dụng **Kaorios-Toolbox** (đã được cài sẵn trong khay ứng dụng hệ thống).
    *   Bật tính năng bypass bảo mật, ẩn bootloader và thiết lập các ứng dụng cần ẩn root thông qua menu trực quan của ứng dụng.
3.  **KernelSU-Next:**
    *   Cài đặt app quản lý `KernelSU` (manager) để cấp quyền root cho các ứng dụng cần thiết và kích hoạt Zygisk để bổ sung tính năng an toàn hệ thống.
