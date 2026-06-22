import psutil, socket, platform, os, subprocess, time, re

def _clean_os_string():
    os_name = platform.system()
    os_release = platform.release()

    try:
        if os_name == "Linux" and os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                info = dict(line.strip().replace('"', '').split("=", 1) for line in f if "=" in line)
            return info.get("NAME", "Linux"), info.get("VERSION_ID", "")
        elif os_name == "Darwin":
            if (mac_version := platform.mac_ver()[0]):
                return "macOS", mac_version
        elif os_name == "Windows":
            import ctypes
            winbrand = ctypes.WinDLL('winbrand.dll')
            winbrand.BrandingFormatString.restype = ctypes.c_wchar_p
            brand_name = winbrand.BrandingFormatString("%WINDOWS_LONG%")
            if brand_name:
                return brand_name, ""
            if (win_version := platform.win32_ver()[0]):
                return os_name, win_version
    except Exception:
        pass
    return os_name, os_release

_final_os, _final_release = _clean_os_string()

def _clean_kernel_string():
    os_name = platform.system()
    kernel_version = platform.version()

    if os_name == "Darwin":
        if ":" in kernel_version:
            return kernel_version.split(":")[0].strip()
    elif os_name == "Linux":
        return platform.release()
    return kernel_version

def _get_device_brand():
    os_name = platform.system()

    try:
        if os_name == "Linux":
            dmi_paths = ["/sys/class/dmi/id/sys_vendor", "/sys/class/dmi/id/product_family", "/sys/class/dmi/id/board_name",]
            try:
                parts = []
                for p in dmi_paths:
                    with open(p, "r") as f:
                        parts.append(f.read().strip())
                vendor, product, model = parts
                return f"{vendor} {product} ({model})"
            except OSError:
                return "Generic Linux Machine"
        elif os_name == "Darwin":
            vendor = "Apple"
            system_profile = subprocess.check_output("system_profiler SPHardwareDataType", shell=True).decode()
            product, model = "Mac", ""
            for line in system_profile.splitlines():
                if "Model Name:" in line:
                    product = line.split(":", 1)[1].strip()
                elif "Model Number:" in line:
                    model = line.split(":", 1)[1].strip()
            return f"{vendor} {product} ({model})" if (model) else f"{vendor} {product}"
        elif os_name == "Windows":
            wmic = subprocess.check_output(["wmic", "csproduct", "get", "vendor,version,name"], stderr=subprocess.DEVNULL).decode()
            lines = [l.strip() for l in wmic.splitlines() if l.strip()]
            if len(lines) >= 2:
                parts = re.split(r'\s{2,}', lines[1])
                if len(parts) >= 3:
                    model, vendor, product = parts[0], parts[1], parts[2]
                    if "To Be Filled" in vendor or "Default" in vendor:
                        return f"Custom Build ({model})"
                    return f"{vendor} {product} ({model})"
    except Exception:
        pass
    return "Unknown Device"

def _get_hardware_serial():
    os_name = platform.system()
    
    try:
        if os_name == "Linux":
            dmi_path = "/sys/class/dmi/id/product_serial"
            try:
                if os.path.exists(dmi_path):
                    with open(dmi_path, "r") as f:
                        if (serial := f.read().strip()) and "Not Specified" not in serial:
                            return serial
            except PermissionError:
                return "Access Denied (requires sudo/root)"
            except OSError:
                pass
        elif os_name == "Darwin":
            system_profile = subprocess.check_output(["system_profiler", "SPHardwareDataType"], stderr=subprocess.DEVNULL).decode()
            for line in system_profile.splitlines():
                if "serial number" in line.lower() and ":" in line:
                    if (serial := line.split(":", 1)[1].strip()):
                        return serial
        elif os_name == "Windows":
            wmic = subprocess.check_output(["wmic", "bios", "get", "serialnumber"], stderr=subprocess.DEVNULL).decode()
            lines = [l.strip() for l in wmic.splitlines() if l.strip()]
            if len(lines) >= 2:
                return lines[1]
    except Exception:
        pass
    return "N/A"

def _get_battery_info():
    battery = psutil.sensors_battery()

    if battery is not None:
        is_charging = battery.power_plugged and battery.secsleft == -1
        if battery.percent >= 100:
            is_charging = False
        return {
            "percent": round(battery.percent, 2),
            "secs_left": battery.secsleft,
            "power_plugged": battery.power_plugged,
            "charging": is_charging
        }
    return None

_STATIC_SYSTEM_INFO = {
    "device": _get_device_brand(),
    "serial": _get_hardware_serial(),
    "arch": platform.machine(),
    "os": _final_os,
    "release": _final_release,
    "kernel": _clean_kernel_string(),
    "host": socket.gethostname()
}

def get_system():
    system_data = _STATIC_SYSTEM_INFO.copy()
    system_data["uptime"] = int(time.time() - psutil.boot_time())
    if (battery_stats := _get_battery_info()):
        system_data["battery"] = battery_stats
    return system_data
