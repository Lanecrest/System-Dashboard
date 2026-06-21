import psutil, time, platform, os, subprocess, socket, json, urllib.request, ssl


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "..", "static", "config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
    timers = config_data["TIMERS"]
    INTERNET_CHECK = timers["internet_check_seconds"]
    DNS_RESOLVER = config_data.get("DNS_RESOLVERS", {})
    IP_CHECKER = config_data.get("IP_CHECKERS", {})
except Exception:
    INTERNET_CHECK = 60
    DNS_RESOLVER = {"Cloudflare": "1.1.1.1"}
    IP_CHECKER = {"icanhazip": "https://icanhazip.com"}
_dns_address = list(DNS_RESOLVER.keys())[0]
_ip_website = list(IP_CHECKER.keys())[0]

_cached_connected_status = False
_last_conn_check = 0
_cached_public_ip = None
_cached_gateway_ip = None

def set_dns_resolver(address):
    global _dns_address, _last_conn_check
    if address in DNS_RESOLVER:
        _dns_address = address

def set_ip_checker(website):
    global _ip_website, _cached_public_ip
    if website in IP_CHECKER:
        _ip_website = website

def _is_connected():
    dns_website = DNS_RESOLVER.get(_dns_address, DNS_RESOLVER[list(DNS_RESOLVER.keys())[0]])

    global _cached_connected_status, _last_conn_check, _cached_public_ip, _cached_gateway_ip
    now = time.time()
    if now - _last_conn_check > INTERNET_CHECK:
        _cached_public_ip = None
        _cached_gateway_ip = None
        s = None
        try:
            s = socket.create_connection((dns_website, 53), timeout=1)
            _cached_connected_status = True
        except OSError:
            _cached_connected_status = False
        finally:
            if s:
                s.close()
        _last_conn_check = now
    return _cached_connected_status

def _get_public_ip():
    user_agent = "System-Dashboard-Matrix"
    ip_website = IP_CHECKER.get(_ip_website, IP_CHECKER[list(IP_CHECKER.keys())[0]])

    global _cached_public_ip
    if not _is_connected():
        _cached_public_ip = None
        return "No Network Connection"
    if _cached_public_ip is not None:
        return _cached_public_ip
    try:
        ip_check = subprocess.check_output(["curl", "-A", user_agent, "-s", "-m", "2", ip_website], stderr=subprocess.DEVNULL).decode().strip()
        if ip_check:
            _cached_public_ip = ip_check
            return _cached_public_ip
    except Exception:
        pass
    try:
        req = urllib.request.Request(ip_website,  headers={'User-Agent': user_agent})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=2, context=context) as response:
            fallback_check = response.read().decode().strip()
            if fallback_check:
                _cached_public_ip = fallback_check
                return _cached_public_ip
    except Exception:
        pass
    _cached_public_ip = "Unable to Resolve"
    return _cached_public_ip

def _get_gateway_ip():
    global _cached_gateway_ip
    if _cached_gateway_ip is not None:
        return _cached_gateway_ip
    use_shell = False

    if platform.system() == "Windows":
        cmd = ["route", "print", "0.0.0.0"]
    elif platform.system() == "Darwin":
        cmd = "netstat -rn -f inet | grep default | awk '{print $2}' | head -n 1"
        use_shell = True
    else:
        cmd = "netstat -rn -4 | grep default | awk '{print $2}' | head -n 1"
        use_shell = True
    try:
        output = subprocess.check_output(cmd, shell=use_shell, stderr=subprocess.DEVNULL).decode().strip()
        if output:
            if platform.system() == "Windows":
                gateway_line = [line for line in output.splitlines() if "0.0.0.0" in line and "Default" not in line]
                if gateway_line:
                    _cached_gateway_ip = gateway_line[0].split()[2]
            else:
                _cached_gateway_ip = output
            if _cached_gateway_ip:
                return _cached_gateway_ip
    except Exception:
        pass
    _cached_gateway_ip = "Unknown"
    return _cached_gateway_ip

def _get_nic_info():
    if_addrs = psutil.net_if_addrs()
    io_counters = psutil.net_io_counters(pernic=True)
    nics = []
    for name, addrs in if_addrs.items():
        ips = []
        mac = None
        for a in addrs:
            fam = getattr(a.family, "name", str(a.family))
            if "LINK" in fam or "AF_PACKET" in fam:
                mac = a.address
            else:
                ips.append(a.address)
        counters = io_counters.get(name)
        nics.append({
            "name": name,
            "ips": ips,
            "mac": mac,
            "bytes_sent": counters.bytes_sent if counters else 0,
            "bytes_recv": counters.bytes_recv if counters else 0
        })
    return nics

def force_network_check():
    global _cached_connected_status, _last_conn_check, _cached_public_ip, _cached_gateway_ip
    _cached_connected_status = False
    _last_conn_check = 0
    _cached_public_ip = None
    _cached_gateway_ip = None

def get_network():
    total = psutil.net_io_counters()
    now = time.time()
    start_time = INTERNET_CHECK
    timer = now - _last_conn_check
    if timer >= start_time or _last_conn_check == 0:
        countdown = start_time
    else:
        countdown = start_time - timer
    return {
        "timestamp": int(time.time()),
        "total_bytes_sent": total.bytes_sent,
        "total_bytes_recv": total.bytes_recv,
        "nic": _get_nic_info(),
        "public_ip": _get_public_ip(),
        "gateway": _get_gateway_ip(),
        "connected": _is_connected(),
        "counter": int(countdown),
        "dns": _dns_address,
        "resolvers": list(DNS_RESOLVER.keys()),
        "ipapi": _ip_website,
        "checkers": list(IP_CHECKER.keys())
    }
