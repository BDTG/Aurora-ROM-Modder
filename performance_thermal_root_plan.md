# Kế hoạch Tùy chỉnh Kernel: Tối ưu Mát máy (Cool-first), Underclock & Root (Xiaomi 14 Ultra)

Tài liệu này hướng dẫn chi tiết phương pháp tùy biến mã nguồn kernel của **Xiaomi 14 Ultra (aurora - Snapdragon 8 Gen 3 / Kernel 6.1)** nhằm đạt được ba mục tiêu cốt lõi:
1. **Root cấp nhân sạch** bằng **KernelSU-Next** (vượt qua các cơ chế phát hiện root của ứng dụng ngân hàng và game).
2. **Hạ xung (Underclock) CPU & GPU** để loại bỏ các dải tần số đỉnh tiêu thụ điện năng và tỏa nhiệt cực lớn, giữ máy hoạt động ở vùng hiệu năng tối ưu (Sweet Spot).
3. **Tinh chỉnh bộ điều phối tác vụ (WALT Scheduler)** giúp máy hoạt động hằng ngày (daily) cực kỳ mát mẻ, tránh tăng nhiệt độ đột ngột (thermal spikes).

---

## 🛡️ Phần 1: Tích hợp KernelSU-Next (Root cấp nhân)

KernelSU-Next hoạt động trong không gian nhân (kernel space), mang lại khả năng ẩn root tốt hơn và ổn định hơn trên Android 14.

### 1. Nhúng mã nguồn KernelSU-Next
Chạy lệnh này từ thư mục gốc của cây nhân (`msm-kernel`):
```bash
cd msm-kernel
# Chạy script tải và tích hợp tự động KernelSU-Next vào mã nguồn
curl -LSs "https://raw.githubusercontent.com/tiann/KernelSU/main/kernel/setup.sh" | bash -s main
```

### 2. Loại bỏ kiểm tra GKI Protected Exports
Để tránh xung đột chữ ký KMI (Kernel Module Interface) khi nạp driver KernelSU, hãy xóa các định nghĩa xuất hàm được bảo vệ của Android GKI trước khi compile:
```bash
rm -f common/android/abi_gki_protected_exports_*
```

### 3. Cấu hình Defconfig cho KernelSU
Thêm các tùy chọn sau vào cuối file config GKI mặc định (`common/arch/arm64/configs/gki_defconfig`):
```ini
CONFIG_KSU=y
CONFIG_OVERLAY_FS=y
CONFIG_KPROBES=y
CONFIG_HAVE_KPROBES=y
CONFIG_KPROBE_EVENTS=y
```

---

## ❄️ Phần 2: Hạ xung nhịp (Underclock) CPU & GPU

Snapdragon 8 Gen 3 (SM8650) là chip rất mạnh nhưng tỏa nhiệt lượng cực lớn khi các nhân CPU và GPU chạy ở xung nhịp tối đa. Việc hạ nhẹ xung nhịp đỉnh giúp giảm đáng kể mức tiêu thụ điện năng (giảm tới 30-40% điện năng tiêu thụ đỉnh của SoC) mà không làm giảm đáng kể trải nghiệm thực tế, đặc biệt là game nặng như **Honkai: Star Rail** ở mức 60 FPS.

### 1. Hạ xung CPU (CPU Underclocking)
Snapdragon 8 Gen 3 sử dụng thiết kế 8 nhân (1+5+2 hoặc 1+3+2+2). Chúng ta sẽ giới hạn tần số tối đa (Fmax) của các cụm nhân:
- **Nhân Prime (1x Cortex-X4)**: Mặc định ~3.3 GHz $\rightarrow$ Hạ xung xuống **2.6 GHz - 2.8 GHz**.
- **Nhân Gold (5x Cortex-A720)**: Mặc định ~3.2 GHz / 3.0 GHz $\rightarrow$ Hạ xung xuống **2.4 GHz - 2.6 GHz**.
- **Nhân Silver (2x Cortex-A520)**: Giữ nguyên mặc định ~2.3 GHz để đảm bảo các tác vụ nền mượt mà.

#### Cách thực hiện trong Device Tree:
Chỉnh sửa trong tệp bảng tần số CPU của Qualcomm:
- **Đường dẫn**: `msm-kernel/arch/arm64/boot/dts/vendor/qcom/pineapple.dtsi` (hoặc các file DTS tương ứng trong Device Tree của Xiaomi).
- Tìm kiếm các node `cpu_opp_table` (Operating Performance Points).
- Vô hiệu hóa hoặc giới hạn các mức tần số cao nhất bằng cách chỉnh sửa thuộc tính `opp-supported-hw` hoặc xóa bỏ các mức tần số đỉnh trong bảng.

*Ví dụ cấu hình giới hạn tần số CPU tối đa trong init script hoặc Driver CPUFreq:*
Một cách an toàn và dễ kiểm soát hơn là giới hạn tần số CPU tối đa thông qua driver cpufreq (`msm-kernel/drivers/cpufreq/qcom-cpufreq-hw.c`) hoặc cấu hình mặc định trong file config bằng cách giới hạn chính sách tần số tối đa khi khởi động.

### 2. Hạ xung GPU (GPU Underclocking)
GPU Adreno 750 mặc định chạy ở xung nhịp lên tới **903 MHz - 1000 MHz** ở mức tải cao nhất, gây nóng máy rất nhanh. Hạ xung trần GPU xuống **600 MHz - 680 MHz** giúp GPU hoạt động cực kỳ mát mẻ mà vẫn thừa sức duy trì 60 FPS mượt mà trong Honkai: Star Rail ở thiết lập đồ họa thích hợp.

#### Cách thực hiện trong Device Tree:
- **Đường dẫn**: `msm-kernel/arch/arm64/boot/dts/vendor/qcom/pineapple-gpu.dtsi`
- Tìm node đại diện cho GPU KGSL (`msm-gpu` hoặc `qcom,kgsl-3d0`).
- Dưới thuộc tính `qcom,gpu-pwrlevels`, hãy xóa hoặc vô hiệu hóa các mức năng lượng (Power Levels) cao nhất đại diện cho các tần số trên 680 MHz.
- Đặt mức tần số tối đa mặc định (`qcom,gpu-pwrlevel-default`) về mức tần số mong muốn (ví dụ Level tương đương 600 MHz hoặc 680 MHz).

---

## 🍃 Phần 3: Tinh chỉnh WALT Scheduler cho Daily Mát máy

Để máy sử dụng hằng ngày (lướt web, mạng xã hội, xem video) không bị ấm hoặc nóng lên đột ngột, ta cần điều chỉnh Bộ điều phối tác vụ **WALT (Window Assisted Load Tracking)** để các tác vụ nhẹ được giữ lại ở các nhân tiết kiệm điện (Silver/Gold nhỏ) lâu hơn, ngăn không cho chúng kích hoạt nhân Prime (Cortex-X4) một cách không cần thiết.

### 1. Điều chỉnh Ngưỡng Di Trú Tác Vụ (Migration Thresholds)
- **Tệp tin nguồn**: `msm-kernel/kernel/sched/walt/sched-walt.c` (hoặc tinh chỉnh qua giá trị sysctl khởi động).
- **Ngưỡng Up-migrate (`sysctl_sched_group_upmigrate`)**: Tăng từ mặc định (thường là 95) lên **98**. Điều này có nghĩa là tải của nhóm tác vụ phải cực kỳ nặng (chạm ngưỡng 98% năng lực của nhân hiện tại) thì WALT mới di chuyển tác vụ đó lên cụm nhân lớn hơn.
- **Ngưỡng Down-migrate (`sysctl_sched_group_downmigrate`)**: Giảm xuống **75 - 80** (mặc định khoảng 85). Điều này giúp giữ các tác vụ đã giảm tải ở lại cụm nhân nhỏ lâu hơn, tránh việc chuyển dịch liên tục giữa nhân lớn và nhân nhỏ gây hao pin và tăng nhiệt.

### 2. Tinh chỉnh Thời gian phản hồi của CPU Governor
- Mặc định governor `schedutil` điều tiết tần số dựa trên tải của bộ điều phối.
- Chúng ta sẽ cấu hình tăng nhẹ tham số `rate_limit_us` (ví dụ từ 500us lên **2000us - 4000us**) cho cụm nhân Prime và Gold. Việc này làm chậm quá trình tăng tần số CPU đối với các tác vụ nhỏ có tính chất nhất thời (như load quảng cáo, hoạt ảnh ngắn), giúp CPU không bị giật xung lên tần số cao nhất vô ích, từ đó giữ nhiệt độ SoC ổn định hơn.

---

## 🌡️ Phần 4: Giữ nguyên Ngưỡng Nhiệt độ Bảo vệ (Safety-first Thermal Policy)

Khác với các bản kernel tùy biến tập trung vào điểm số Benchmark (thường tăng hoặc vô hiệu hóa ngưỡng nhiệt), bản kernel này sẽ **giữ nguyên ngưỡng nhiệt độ mặc định của Xiaomi** hoặc thậm chí cấu hình để quá trình giảm hiệu năng (thermal throttling) diễn ra mượt mà và sớm hơn một chút khi nhiệt độ pin đạt 42°C.
- Việc này kết hợp với **Underclock** (đã giảm lượng nhiệt tỏa ra từ gốc) sẽ tạo ra một lớp bảo vệ kép: Máy rất khó nóng lên, và nếu có nóng lên do nhiệt độ môi trường ngoài, hệ thống vẫn sẽ hạ xung nhịp kịp thời để bảo vệ tuổi thọ pin và linh kiện.

---

## 🔒 Phần 5: Ẩn Trạng thái Bootloader ở Cấp Nhân (Kernel-level Spoofing)

Khi mở khóa bootloader, bootloader của Qualcomm (ABL) sẽ truyền các tham số trạng thái bảo mật vào kernel thông qua dòng lệnh khởi động (kernel command line / bootconfig). Để ẩn trạng thái unlocked ở mức sâu nhất, tránh bị các cơ chế kiểm tra phần cứng phát hiện:

### 1. Thay đổi báo cáo dòng lệnh khởi động (cmdline spoofing)
- **Tệp tin chỉnh sửa**: `msm-kernel/fs/proc/cmdline.c`
- **Cách thực hiện**: Can thiệp vào hàm hiển thị cmdline để khi bất kỳ ứng dụng user space nào (hoặc Google Play Services) đọc tệp `/proc/cmdline`, nhân sẽ trả về chuỗi thông tin giả lập trạng thái đã khóa:
  * Thay thế chuỗi `androidboot.verifiedbootstate=orange` $\rightarrow$ `androidboot.verifiedbootstate=green`
  * Thay thế chuỗi `androidboot.flash.locked=0` $\rightarrow$ `androidboot.flash.locked=1`
  * Thay thế hoặc loại bỏ `androidboot.vbmeta.device_state=unlocked`.

### 2. Can thiệp driver Device Tree Node của Android
Hệ điều hành Android cũng đọc trạng thái bảo mật thông qua cấu trúc Device Tree giả lập tại `/sys/firmware/devicetree/base/firmware/android/`.
- **Tệp tin chỉnh sửa**: `msm-kernel/drivers/of/fdt.c` (hoặc các driver Qualcomm đọc thuộc tính androidboot).
- Đảm bảo các thuộc tính sau luôn trả về giá trị an toàn:
  * `verifiedbootstate` luôn trả về `"green"`
  * `flash.locked` luôn trả về `"1"`

---

## 🚀 Kế hoạch Thực hiện Chi tiết

### Bước 1: Chuẩn bị mã nguồn và Môi trường
Tham khảo tài liệu [aurora_kernel_build_plan.md](file:///home/bdtg/Desktop/AuroraKernel/aurora_kernel_build_plan.md) để tải đúng nhánh mã nguồn kernel Xiaomi 14 Ultra (`aurora-u-oss`) và thiết lập hệ thống build Kleaf.

### Bước 2: Tích hợp Root & Apply Patches
1. Tải và nhúng mã nguồn KernelSU-Next.
2. Xóa các file bảo vệ exports GKI.
3. Áp dụng các patch sửa đổi `/fs/proc/cmdline.c` và `/drivers/of/fdt.c` để ẩn trạng thái mở khóa bootloader cấp nhân.

### Bước 3: Sửa Device Tree để Underclock GPU & CPU
1. Mở `pineapple-gpu.dtsi` để hạ trần GPU.
2. Điều chỉnh cpufreq driver hoặc device tree của CPU để giới hạn xung nhịp tối đa các cụm nhân lớn.

### Bước 4: Chỉnh sửa WALT Scheduler trong `sched-walt.c`
Thay đổi các giá trị mặc định của `sysctl_sched_group_upmigrate` và `sysctl_sched_group_downmigrate` trực tiếp trong mã nguồn để đảm bảo cấu hình mát máy luôn hoạt động độc lập với các app tối ưu hiệu năng bên thứ ba.

### Bước 5: Biên dịch & Đóng gói
1. Tiến hành compile bằng công cụ Kleaf (Bazel):
   ```bash
   python3 msm-kernel/build_with_bazel.py -t aurora gki
   ```
2. Đóng gói file `Image` thu được vào AnyKernel3 zip để flash qua Recovery hoặc Kernel Flasher.
