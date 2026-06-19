import psutil, socket, platform, os, subprocess, time

def _clean_os_string():
    os_name = platform.system()
    os_release = platform.release()

    try: 
        if os_name == "Linux" and os.path.exists("/etc/os-release"):
            info = dict(line.strip().replace('"', '').split("=", 1) for line in open("/etc/os-release") if "=" in line)
            return info.get("NAME", "Linux"), info.get("VERSION_ID", "")
        elif os_name == "Darwin":
            mac_version = platform.mac_ver()[0]
            if mac_version:
                return "macOS", mac_version
        elif os_name == "Windows":
            import ctypes
            winbrand = ctypes.WinDLL('winbrand.dll')
            winbrand.BrandingFormatString.restype = ctypes.c_wchar_p
            brand_name = winbrand.BrandingFormatString("%WINDOWS_LONG%")
            if brand_name:
                return brand_name, ""
            win_version = platform.win32_ver()[0]
            if win_version:
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
            if all(os.path.exists(p) for p in dmi_paths):
                vendor, product, model = [open(p, "r").read().strip() for p in dmi_paths]
                return f"{vendor} {product} ({model})"
            return "Generic Linux Machine"
        elif os_name == "Darwin":
            vendor = "Apple"
            system_profile = subprocess.check_output("system_profiler SPHardwareDataType", shell=True).decode()
            product = next((line.split(":", 1)[1].strip() for line in system_profile.splitlines() if "Model Name:" in line), "Mac")
            model = next((line.split(":", 1)[1].strip() for line in system_profile.splitlines() if "Model Number:" in line), "")
            if model:
                return f"{vendor} {product} ({model})"
            return f"{vendor} {product}"
        elif os_name == "Windows":
            vendor = subprocess.check_output("wmic csproduct get vendor", shell=True).decode().split('\n')[1].strip()
            product = subprocess.check_output("wmic csproduct get version", shell=True).decode().split('\n')[1].strip()
            model = subprocess.check_output("wmic csproduct get name", shell=True).decode().split('\n')[1].strip()
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
                    serial = open(dmi_path, "r").read().strip()
                    if serial and "Not Specified" not in serial:
                        return serial
            except PermissionError:
                return "Access Denied (requires sudo/root)"
        elif os_name == "Darwin":
            system_profile = subprocess.check_output("system_profiler SPHardwareDataType", shell=True).decode()
            for line in system_profile.split("\n"):
                if "serial number" in line.lower() and ":" in line:
                    serial = line.split(":", 1)[1].strip()
                    if serial:
                        return serial
        elif os_name == "Windows":
            serial = subprocess.check_output("wmic bios get serialnumber", shell=True).decode().split('\n')[1].strip()
            if serial:
                return serial
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
    battery_stats = _get_battery_info()
    if battery_stats:
        system_data["battery"] = battery_stats
    return system_data
