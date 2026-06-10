# Aurora Kernel for Xiaomi 14 Ultra (aurora)

Custom GKI Kernel based on Xiaomi's official kernel sources for **Xiaomi 14 Ultra (aurora)** on Snapdragon 8 Gen 3 (pineapple platform).

## 🚀 Features

*   **GKI Compliant:** Fully compatible with Android Common Kernel GKI v6.1+.
*   **KernelSU-Next Integration:** Integrated root manager at the kernel level for stealth and security.
*   **Thermal & CPU Optimizations (Underclock):**
    *   Optimized CPU frequency table for Snapdragon 8 Gen 3 to reduce device temperature and save battery.
    *   Hạ xung nhịp các nhân lớn (Prime & Gold cores) và tinh chỉnh điện áp để máy mát hơn, hiệu năng ổn định không bị throttle khi tải nặng.
*   **Custom Modules:** Compiled custom kernel modules (`qcom-cpufreq-hw.ko`, `sched-walt.ko`) to override default scheduler and scaling behaviors.

## 📁 Repository Structure

*   `/msm-kernel/`: The main kernel source tree.
*   `/msm-kernel/KernelSU-Next/`: KernelSU-Next source driver.
*   `/prebuilts/`: Clang compiler toolchain and GKI build tools.
*   `/AnyKernel3/`: Flashable zip packaging template for custom recoveries.

## 🛠️ Compilation

To compile the kernel using the Android Bazel build system, run:
```bash
./msm-kernel/build_with_bazel.py -t aurora
```

After building, the kernel image (`Image`) and modules (`.ko` files) will be located in the `out/` directory.

## 📦 Packaging

To generate the flashable zip:
1.  Copy the compiled `Image` file to `AnyKernel3/Image`.
2.  Copy compiled `.ko` modules to `AnyKernel3/modules/vendor/lib/modules/`.
3.  Zip the contents of the `AnyKernel3` directory:
    ```bash
    cd AnyKernel3
    zip -r9 ../Aurora-Kernel-aurora-GKI-v1.0.zip *
    ```
