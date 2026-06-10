# Tài liệu Tổng hợp Kinh nghiệm & Lưu ý Biên dịch Kernel và Mod ROM (Xiaomi 14 Ultra)

Tài liệu này tổng hợp toàn bộ các lưu ý kỹ thuật quan trọng rút ra từ quá trình build Kernel GKI và mod ROM HyperOS 3 (Android 16) nhằm giúp bạn tránh các lỗi hệ thống (như bootloop, mất quyền root, lỗi phân quyền) trong tương lai.

---

## 1. 🔍 KINH NGHIỆM BIÊN DỊCH KERNEL (GKI)

### A. Tích hợp KernelSU-Next hoặc KernelSU gốc
*   **Vị trí mã nguồn:** Mã nguồn KernelSU-Next phải được tích hợp ở mức driver (trong thư mục `msm-kernel/drivers/kernelsu/` hoặc liên kết trực tiếp vào cây nhân).
*   **Cấu hình nhân (`defconfig`):** Cần đảm bảo các cờ cấu hình `CONFIG_KSU=y` và các cờ bảo mật liên quan được bật. Với nhân GKI hiện đại, việc tích hợp qua các file cấu hình phân vùng `gki_defconfig` là bắt buộc.
*   **Quy trình build:** Sử dụng Bazel (`build_with_bazel.py`) để biên dịch. Luôn chạy dọn dẹp bộ nhớ cache (`bazel clean` hoặc xóa thư mục `out/`) nếu thay đổi cấu hình phần cứng hoặc Driver để tránh lỗi cache biên dịch cũ.

### B. CPU Underclock (Hạ xung mát máy)
*   **Can thiệp Device Tree (`dtb`/`dtbo`):** Các thiết lập giới hạn xung nhịp CPU/GPU hoặc điện áp nằm trong Device Tree hoặc module điều khiển xung nhịp (`qcom-cpufreq-hw.ko`).
*   **Lưu ý module nhân:** Khi biên dịch kernel GKI, các driver quan trọng như điều khiển xung nhịp và lập lịch (`qcom-cpufreq-hw.ko`, `sched-walt.ko`) được biên dịch dưới dạng module nhân độc lập (`.ko`). Bạn bắt buộc phải đóng gói các tệp `.ko` mới này đi kèm với tệp nhân `Image` để hệ thống load đúng driver khi khởi động.

### C. Đóng gói Flashable ZIP (AnyKernel3)
*   **Đường dẫn Block Device:** Trong file cấu hình `anykernel.sh`, phải khai báo chính xác đường dẫn phân vùng boot của thiết bị. Với Xiaomi 14 Ultra (aurora), đường dẫn là `block=/dev/block/bootdevice/by-name/boot`.
*   **Vị trí module nhân:** Các module `.ko` cần được đặt trong thư mục `modules/vendor/lib/modules/` bên trong zip AnyKernel3 để script tự động chèn vào phân vùng `vendor_dlkm` hoặc ramdisk khi flash.

---

## 2. 🏗️ KINH NGHIỆM TÙY BIẾN & MOD ROM (EROFS)

### A. Giải nén phân vùng (Unpacking)
*   **Sử dụng `fsck.erofs`:** Sử dụng lệnh `fsck.erofs --extract=<thư_mục_đích> <tệp_ảnh.img>` để giải nén.
*   **Tránh quyền root (`sudo`):** Không nên sử dụng `sudo` khi giải nén trừ khi thực sự cần thiết. `fsck.erofs` sẽ tự động giữ nguyên các thuộc tính phân quyền (`0755`, `0644`, `setuid`...) của file gốc dưới quyền người dùng hiện tại của bạn.

### B. Việt hóa bằng RRO Overlay (Tối ưu nhất)
*   **Định dạng Manifest:** File `AndroidManifest.xml` của các ứng dụng Overlay tiếng Việt RRO phải chứa các thuộc tính đặc thù sau để HyperOS nhận diện và kích hoạt tự động:
    *   `coreApp="true"` trong thẻ `<manifest>`.
    *   `android:isStatic="true"` và `android:priority="99"` trong thẻ `<overlay>`.
    *   `android:hasCode="false"` trong thẻ `<application>` để báo hiệu đây chỉ là gói tài nguyên không chứa code thực thi.
*   **Biên dịch AAPT2:** Luôn liên kết với tệp SDK nền tảng mới nhất (ví dụ: [android.jar](file:///home/bdtg/Desktop/AuroraKernel/tools/android.jar) API 35 hoặc 36) bằng lệnh `aapt2 link` để đảm bảo hệ thống không bị lỗi crash khi load tài nguyên overlay mới.
*   **Thư mục đích:** Copy toàn bộ file `.apk` overlay đã build vào `/product/overlay/`.

### C. Tích hợp Ứng dụng Hệ thống (priv-app) & Whitelist Permissions
*   **Vị trí tệp:** Đặt ứng dụng (như `KaoriosToolbox.apk`) vào `/product/priv-app/KaoriosToolbox/KaoriosToolbox.apk` và thiết lập quyền `0644`.
*   **Cấp quyền chữ ký đặc quyền (Signature/Privapp Permissions):** Nếu ứng dụng yêu cầu các quyền hệ thống sâu, bắt buộc phải khai báo whitelist XML trong `/product/etc/permissions/com.kousei.kaorios.xml` với quyền `0644`. Nếu thiếu file này, thiết bị sẽ bị **bootloop liên tục (lỗi PackageManager)** do ứng dụng priv-app yêu cầu quyền hệ thống mà không được whitelist.

### D. Ẩn Bootloader ở mức ROM
*   **Chèn build.prop:** Thêm các dòng cấu hình ẩn bootloader vào cuối tất cả các tệp `build.prop` có trong ROM (`system`, `product`, `system_ext`) để ghi đè các cấu hình trước đó:
    ```properties
    ro.boot.flash.locked=1
    ro.boot.verifiedbootstate=green
    ro.boot.veritymode=enforcing
    ro.boot.warranty_bit=0
    ro.boot.selinux=enforcing
    ro.secure=1
    ro.debuggable=0
    ro.force.debuggable=0
    ```

### E. Đóng gói lại phân vùng EROFS (Repacking)
*   **Tham số bắt buộc 1: `--all-root`:** Khi chạy `mkfs.erofs`, bắt buộc phải thêm cờ `--all-root`. Cờ này ép tất cả các tệp tin trong ảnh đĩa đầu ra thuộc quyền sở hữu của `root:root` (UID 0: GID 0). Nếu thiếu cờ này, các tệp tin sẽ mang UID/GID của người dùng Linux trên máy tính của bạn (ví dụ `1000:1000`), khiến Android không thể đọc được file hệ thống và bị bootloop ngay lập tức.
*   **Tham số bắt buộc 2: `--mount-point`:** 
    *   Phân vùng `system` sử dụng `--mount-point=/`.
    *   Phân vùng `product` sử dụng `--mount-point=/product`.
    *   Phân vùng `system_ext` sử dụng `--mount-point=/system_ext`.
    *   *Lý do:* Giúp hệ điều hành map đúng nhãn bảo mật SELinux cho các tệp tin bên trong phân vùng khi mount vào cây hệ thống.
*   **Thuật toán nén:** Sử dụng `-z lz4` để build nhanh, hoặc `-z lz4hc` để tối ưu dung lượng phân vùng đầu ra (lz4hc nén tốt hơn nhưng build lâu hơn).

---

## 3. 🛡️ QUY TRÌNH FLASH AN TOÀN (BYPASS AVB)
Do hệ thống phân vùng gốc đã bị thay đổi chữ ký mã hóa, bạn **bắt buộc** phải tắt xác thực AVB (Android Verified Boot) khi flash:
1.  Luôn flash `vbmeta.img` và `vbmeta_system.img` với cờ vô hiệu hóa trước khi flash phân vùng mod:
    ```bash
    fastboot flash --disable-verity --disable-verification vbmeta vbmeta.img
    fastboot flash --disable-verity --disable-verification vbmeta_system vbmeta_system.img
    ```
2.  Sau đó khởi động vào chế độ **Fastbootd** (`fastboot reboot fastboot`) để flash các phân vùng động (`system`, `product`, `system_ext`) rồi mới flash kernel.
