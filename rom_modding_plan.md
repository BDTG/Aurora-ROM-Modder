# Kế hoạch Mod ROM: HyperOS 3 (China Base) & ROM Custom AOSP (Xiaomi 14 Ultra)

Tài liệu này hướng dẫn chi tiết quy trình nghiên cứu, chuẩn bị công cụ và các bước thực hiện để mod ROM cho **Xiaomi 14 Ultra (tên mã: aurora)**. Kế hoạch được chia làm hai hướng đi chính tùy thuộc vào nhu cầu sử dụng của bạn:
*   **Hướng A:** Mod ROM HyperOS 3 gốc Trung Quốc (China Stable/Beta) để bổ sung tiếng Việt, dịch vụ Google, sửa lỗi thông báo và tối ưu hóa thời lượng pin/nhiệt độ.
*   **Hướng B:** Biên dịch hoặc tùy biến ROM Custom AOSP (như Evolution X, LineageOS, PixelOS) mang giao diện thuần Google, mượt mà và tối giản.

---

## 🏗️ Cấu trúc Phân vùng trên Snapdragon 8 Gen 3 (Android 14/15)

Trước khi thực hiện mod ROM, bạn cần hiểu cấu trúc phân vùng hiện đại của Xiaomi 14 Ultra:
1.  **Phân vùng Động (Dynamic Partitions - Virtual A/B):** 
    *   Hầu hết các phân vùng hệ điều hành (`system`, `system_ext`, `product`, `vendor`, `odm`, `mi_ext`) được gộp chung vào một phân vùng vật lý duy nhất là **`super.img`**.
    *   Định dạng hệ thống tệp tin mặc định là **EROFS** (Enhanced Read-Only File System), có đặc tính nén cao và chỉ đọc.
2.  **Khởi động (Boot Images):**
    *   `init_boot.img`: Chứa Ramdisk dùng để mount các phân vùng và chạy đoạn mã khởi động ban đầu. Đây là nơi chứa Magisk hoặc KernelSU (nếu dùng phương pháp ramdisk root).
    *   `boot.img`: Chứa nhân Kernel (GKI `Image`).
    *   `vendor_boot.img`: Chứa các driver thiết bị ban đầu và device tree nhị phân (`dtb`).

---

## 🛠️ Hướng A: Mod ROM HyperOS 3 (Base China)

ROM nội địa Trung Quốc có ưu điểm là nhận được bản cập nhật sớm nhất, tính năng độc quyền mượt mà, nhưng thiếu tiếng Việt, không cài sẵn Google Services, bị trễ thông báo do cơ chế quản lý pin nghiêm ngặt và chứa nhiều ứng dụng rác (bloatware).

### 1. Chuẩn bị Công cụ trên Linux (Ubuntu)
Để trích xuất và sửa đổi ROM, ta cần các công cụ dòng lệnh sau:
```bash
sudo apt update && sudo apt install -y android-sdk-libsparse-utils lz4 brotli p7zip-full
# Tải công cụ giải nén payload.bin của ROM fastboot/recovery
curl -Lo payload-dumper-go https://github.com/ssut/payload-dumper-go/releases/download/v1.2.2/payload-dumper-go_1.2.2_linux_amd64
chmod +x payload-dumper-go
sudo mv payload-dumper-go /usr/local/bin/
```

### 2. Quy trình Trích xuất và Unpack Phân vùng (Unpacking)
1.  Tải ROM Recovery (dạng `.zip`) hoặc ROM Fastboot (dạng `.tgz`) của HyperOS 3 China cho Xiaomi 14 Ultra.
2.  Giải nén file và tìm tệp `payload.bin`.
3.  Trích xuất các phân vùng logic từ `payload.bin`:
    ```bash
    payload-dumper-go -p system,product,system_ext,mi_ext payload.bin
    ```
4.  **Unpack EROFS Image:** 
    Vì các phân vùng logic dạng `.img` sử dụng định dạng EROFS, bạn cần sử dụng công cụ `extract.erofs` hoặc fsck của erofs để trích xuất nội dung ra thư mục chỉnh sửa:
    ```bash
    # Trích xuất phân vùng system
    fsck.erofs --extract=./system_dir system.img
    ```

### 3. Các Tùy biến & Mod cốt lõi (Modding)
Sau khi giải nén các thư mục hệ thống, ta thực hiện các chỉnh sửa sau:

*   **Việt hóa (Thêm Tiếng Việt từ nguồn Xiaomi.eu - Áp dụng Phương án 2: RRO Overlay):**
    *   **Nguồn dịch thuật**: Sử dụng các tệp XML dịch thuật Tiếng Việt chính thức từ kho lưu trữ của **Xiaomi.eu** dành cho HyperOS 3.
    *   **Quy trình kỹ thuật RRO Overlay (Chính thức)**:
        1. **Tạo cấu trúc gói Overlay**: Với mỗi ứng dụng hệ thống cần Việt hóa (ví dụ: `com.android.settings`, `com.android.systemui`), ta tạo một thư mục RRO tương ứng có chứa file `AndroidManifest.xml` tối giản và thư mục tài nguyên `res/values-vi/strings.xml`.
           * *Ví dụ tệp `AndroidManifest.xml` cho RRO Settings*:
             ```xml
             <manifest xmlns:android="http://schemas.android.com/apk/res/android"
                 package="com.android.settings.overlay.vi">
                 <overlay android:targetPackage="com.android.settings" android:priority="99"/>
             </manifest>
             ```
        2. **Biên dịch RRO APK**: Sử dụng công cụ `aapt2` từ Android SDK để đóng gói các thư mục tài nguyên này thành các file `.apk` overlay chỉ chứa tài nguyên mà không có mã thực thi:
           ```bash
           aapt2 link -o SettingsOverlayVi.apk -I "$ANDROID_SDK/platforms/android-34/android.jar" --manifest AndroidManifest.xml -R values-vi/strings.xml
           ```
        3. **Nạp vào hệ thống**: Sao chép tất cả các tệp `.apk` overlay đã biên dịch vào thư mục `/product/overlay/` của ROM trước khi repack EROFS. Khi máy khởi động, Android OS sẽ tự động liên kết các chuỗi Tiếng Việt vào ứng dụng đích mà không làm thay đổi file ứng dụng gốc.
    *   **Kích hoạt ngôn ngữ**: Chỉnh sửa cấu hình khu vực và ngôn ngữ trong `product/etc/sysconfig/` và file cấu hình `build.prop` để hệ thống mở tùy chọn hiển thị Tiếng Việt trong phần Thiết lập.
*   **Tích hợp Google Services (GApps):**
    *   ROM China của Xiaomi 14 Ultra thường đã tích hợp sẵn khung Google Play Services trong nhân, chỉ bị ẩn.
    *   Kích hoạt dịch vụ Google bằng cách cài ứng dụng Google Play Store làm ứng dụng hệ thống (`product/priv-app/GooglePlayStore`) hoặc kích hoạt qua tệp cấu hình `google.xml` trong thư mục `etc/permissions` của phân vùng `product`.
*   **Debloat (Xóa bỏ App rác):**
    *   Xóa bỏ các ứng dụng không cần thiết trong `system/app`, `product/app`, và `product/priv-app` (ví dụ: các app trợ lý ảo Mi AI, các kho ứng dụng GetApps, dịch vụ tài chính Mi Pay, v.v.).
*   **Sửa lỗi chậm thông báo (Notification Fix):**
    *   ROM China tự động đóng băng các ứng dụng nền để tiết kiệm pin.
    *   Chỉnh sửa danh sách trắng khởi chạy (`auto-start blacklist`) trong `product/etc/sysconfig/miui-default-power-save.xml` hoặc loại bỏ giới hạn của dịch vụ MIUI Power Keeper.
*   **Bypass kiểm tra chữ ký (Signature Verification Bypass):**
    *   Chỉnh sửa tệp `services.jar` trong `/system/framework/` (dùng công cụ `Haystack` hoặc `Lucky Patcher` dòng lệnh) để tắt cơ chế xác thực APK của hệ thống, cho phép cài đặt các ứng dụng mod hoặc hạ cấp ứng dụng hệ thống dễ dàng.
*   **Tích hợp Kaorios-Toolbox (Play Integrity Fix & Spoofing):**
    *   **Tích hợp ứng dụng quản lý:** Sao chép file APK Kaorios-Toolbox mới nhất tải từ [Wuang26/Kaorios-Toolbox](https://github.com/Wuang26/Kaorios-Toolbox) vào phân vùng `/product/priv-app/KaoriosToolbox/KaoriosToolbox.apk` và thiết lập quyền `0644`. Điều này đảm bảo khi người dùng khởi động ROM sẽ có sẵn công cụ quản lý.
    *   **Tích hợp Framework Patch (Kaorios Patcher):** Chạy script patch của Kaorios trực tiếp trên file `services.jar` và `framework.jar` của ROM gốc trước khi repack để tối ưu hóa tích hợp sâu ở mức hệ thống, tránh xung đột bootloop khi cài đặt module sau này.
    *   **Hỗ trợ Play Integrity & Unlimited Photos:** Hướng dẫn người dùng kích hoạt Zygisk trong **KernelSU-Next** đã compile sẵn ở nhân, sau đó nạp module Kaorios qua ứng dụng quản lý để kích hoạt tính năng bypass kiểm tra bảo mật của Google và mở khóa backup Google Photos không giới hạn.
*   **Ẩn trạng thái Bootloader ở mức ROM (User Space Bootloader Spoofing):**
    *   **Can thiệp tệp prop khởi động**: Chỉnh sửa file `system/build.prop` hoặc `product/build.prop` để thiết lập các giá trị an toàn:
        * `ro.boot.flash.locked=1`
        * `ro.boot.verifiedbootstate=green`
        * `ro.secure=1`
        * `ro.debuggable=0`
    *   **Override qua init script**: Chèn các lệnh ghi đè thuộc tính bảo mật vào các file script khởi động hệ thống (`*.rc` trong vendor hoặc system) để đảm bảo các thuộc tính unlocked không bị rò rỉ ra user space.
    *   **Phối hợp với Zygisk Spoofing**: Sử dụng chức năng ẩn bootloader của **Kaorios-Toolbox** để ẩn trạng thái mở khóa bootloader ở tầng runtime (khi ứng dụng chạy), giúp vượt qua kiểm tra Play Integrity và các ứng dụng ngân hàng mà không cần lock bootloader phần cứng.

### 4. Đóng gói lại và Tạo ROM Custom Flashable (Repacking)
Sau khi chỉnh sửa xong thư mục, ta phải đóng gói ngược lại thành file `.img` định dạng EROFS và nén thành zip cài đặt.
1.  **Đóng gói phân vùng EROFS:**
    ```bash
    # Sử dụng công cụ make_erofs
    make_erofs -I 9 -z lz4hc -d ./system_dir system.img
    ```
2.  **Đóng gói file zip cài đặt qua Recovery (TWRP) hoặc Flash qua Fastboot**:
    *   Tạo script cài đặt hoặc file `flash_all.sh` tự động flash từng phân vùng đã mod vào máy chủ.

---

## 🍀 Hướng B: Xây dựng & Tùy biến ROM Custom AOSP

Nếu bạn muốn trải nghiệm Android thuần khiết, hiệu năng ổn định, không chịu các cơ chế dịch vụ nền ẩn của MIUI/HyperOS, ROM Custom AOSP là lựa chọn tối ưu.

### 1. Sử dụng ROM Custom AOSP có sẵn (Tối ưu hóa)
Đối với hầu hết lập trình viên đơn lẻ, việc xây dựng hoàn chỉnh cây nguồn (Device Tree) từ đầu cho Snapdragon 8 Gen 3 là rất phức tạp và mất hàng tuần. Do đó, hướng đi hiệu quả là:
1.  Tìm bản ROM AOSP dạng Stable/Beta đã được cộng đồng build sẵn cho Xiaomi 14 Ultra (ví dụ: Evolution X hoặc LineageOS).
2.  Tải về, unpack các phân vùng hệ thống (`system.img`, `product.img`).
3.  **Tùy biến (Modding):**
    *   Loại bỏ hoặc thay thế các ứng dụng mặc định bằng ứng dụng Google (nếu ROM không kèm GApps).
    *   Tích hợp sâu cấu hình kernel mát máy (đã dựng ở phần trước) bằng cách thay thế file `Image` trong `boot.img` và tích hợp sẵn root **KernelSU-Next**.
    *   Thêm các tweak tối ưu hóa âm thanh (Dolby Atmos) và Camera (Leica Camera port từ HyperOS sang AOSP).

### 2. Biên dịch ROM AOSP từ mã nguồn (Building from Source - Nâng cao)
Nếu bạn có đủ tài nguyên (Server CPU 32+ cores, 64GB+ RAM, 500GB SSD trống), bạn có thể tự build ROM AOSP từ mã nguồn (ví dụ: LineageOS):

*   **Bước 1: Khởi tạo mã nguồn ROM AOSP**
    ```bash
    repo init -u https://github.com/LineageOS/android.git -b lineage-21.0
    repo sync -c -j$(nproc)
    ```
*   **Bước 2: Thiết lập Device Tree cho Xiaomi 14 Ultra (aurora)**
    *   Do Xiaomi 14 Ultra dùng chung cấu trúc nền tảng `pineapple` với Xiaomi 14 / 14 Pro, bạn cần clone các Device Tree tương thích:
        *   Device Tree: `device/xiaomi/aurora`
        *   Hardware/HALs: `hardware/xiaomi`
        *   Vendor Blobs: `vendor/xiaomi/aurora` (trích xuất độc quyền từ ROM gốc bằng công cụ `extract-files.sh`).
*   **Bước 3: Tích hợp Kernel mát máy và hạ xung đã tối ưu**
    *   Thay thế mã nguồn kernel mặc định trong cây ROM AOSP bằng mã nguồn kernel đã tùy chỉnh hạ xung nhịp CPU/GPU của bạn (`msm-kernel`).
*   **Bước 4: Biên dịch**
    ```bash
    source build/envsetup.sh
    lunch lineage_aurora-userdebug
    mka bacon -j$(nproc)
    ```

---

## 🛡️ Các Lưu ý Cực kỳ Quan trọng khi Flash ROM Mod

Snapdragon 8 Gen 3 sử dụng cơ chế bảo mật nghiêm ngặt. Bất kỳ sự thay đổi nào đối với phân vùng hệ thống đều sẽ làm hỏng cấu trúc mã hóa xác thực (Android Verified Boot).

1.  **Vô hiệu hóa AVB (Android Verified Boot):**
    *   Khi flash ROM đã mod phân vùng hệ thống, bạn **BẮT BUỘC** phải flash file `vbmeta.img` đã được tắt tính năng xác thực:
        ```bash
        fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
        ```
    *   Nếu không flash vbmeta patched, điện thoại sẽ bị kẹt ở màn hình khởi động (Bootloop) hoặc hiện thông báo cảnh báo bảo mật màu đỏ và tắt máy.
2.  **Khóa/Mở khóa Bootloader:**
    *   Tuyệt đối **KHÔNG ĐƯỢC KHOÁ LẠI BOOTLOADER (fastboot oem lock)** sau khi đã flash ROM mod hoặc Kernel tùy chỉnh. Máy sẽ bị Hard Brick ngay lập tức và chỉ có thể cứu bằng tài khoản Authorized Mi Account của hãng.
3.  **Sao lưu phân vùng EFS (IMEI):**
    *   Trước khi tiến hành flash bất kỳ ROM nào, hãy dùng TWRP backup lại các phân vùng `efs`, `sec`, `fsg` (chứa IMEI và thông tin sóng điện thoại) để tránh mất sóng vĩnh viễn nếu xảy ra lỗi.
