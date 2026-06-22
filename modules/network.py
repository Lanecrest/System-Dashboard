import psutil, time, platform, os, subprocess, socket, json, re, urllib.request, ssl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "..", "static", "config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)
    timers = config_data["TIMERS"]
    INTERNET_CHECK = timers["internet_check_seconds"]
    DNS_RESOLVER = config_data.get("DNS_RESOLVERS", {})
    IP_CHECKER = config_data.get("IP_CHECKERS", {})
except Exception: # Backup if config.json is corrupted/missing
    INTERNET_CHECK = 60
    DNS_RESOLVER = {"Cloudflare": "1.1.1.1"}
    IP_CHECKER = {"icanhazip": "https://icanhazip.com"}
_dns_address = next(iter(DNS_RESOLVER))
_ip_website = next(iter(IP_CHECKER))

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
    dns_website = DNS_RESOLVER.get(_dns_address, next(iter(DNS_RESOLVER)))

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
    ip_website = IP_CHECKER.get(_ip_website, next(iter(IP_CHECKER)))

    global _cached_public_ip
    if not _is_connected():
        _cached_public_ip = None
        return "No Network Connection"
    if _cached_public_ip is not None:
        return _cached_public_ip
    try:
        req = urllib.request.Request(ip_website, headers={'User-Agent': user_agent})
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, timeout=2, context=context) as response:
            if (ip_check := response.read().decode().strip()):
                _cached_public_ip = ip_check
                return _cached_public_ip
    except Exception:
        pass
    _cached_public_ip = "Unable to Resolve"
    return _cached_public_ip

def _get_gateway_ip():
    global _cached_gateway_ip
    if _cached_gateway_ip is not None:
        return _cached_gateway_ip
    current_os = platform.system()
    if current_os == "Windows":
        cmd = ["ipconfig"]
        use_shell = False
    elif current_os == "Darwin":
        cmd = "route -n get default | awk '/gateway:/ {print $2}'"
        use_shell = True
    else:
        cmd = "ip route show default | awk '{print $3}'"
        use_shell = True
    try:
        if (output := subprocess.check_output(cmd, shell=use_shell, stderr=subprocess.DEVNULL).decode().strip()):
            if current_os == "Windows":
                if (match := re.search(r"Default Gateway.*:\s*([\d\.]+)", output)):
                    _cached_gateway_ip = match.group(1)
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
    connection = _is_connected()
    timer = now - _last_conn_check
    countdown = INTERNET_CHECK if (timer >= INTERNET_CHECK or _last_conn_check == 0) else (INTERNET_CHECK - timer)
    return {
        "timestamp": int(time.time()),
        "total_bytes_sent": total.bytes_sent,
        "total_bytes_recv": total.bytes_recv,
        "nic": _get_nic_info(),
        "public_ip": _get_public_ip(),
        "gateway": _get_gateway_ip(),
        "connected": connection,
        "counter": int(countdown),
        "dns": _dns_address,
        "resolvers": list(DNS_RESOLVER.keys()),
        "ipapi": _ip_website,
        "checkers": list(IP_CHECKER.keys())
    }
