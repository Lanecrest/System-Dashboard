import psutil, time, platform, subprocess, socket, urllib.request, ssl

_cached_connected_status = False
_last_conn_check = 0
_cached_public_ip = None
DNS_RESOLVER = {
    "Cloudflare": "1.1.1.1",
    "Google": "8.8.8.8",
    "0.0.0.0": "0.0.0.0"
}
_dns_address = list(DNS_RESOLVER.keys())[0]

def set_dns_resolver(address):
    global _dns_address, _last_conn_check
    if address in DNS_RESOLVER:
        _dns_address = address

def _is_connected():
    dns_website = DNS_RESOLVER.get(_dns_address, DNS_RESOLVER[list(DNS_RESOLVER.keys())[0]])

    global _cached_connected_status, _last_conn_check
    now = time.time()
    if now - _last_conn_check > 60:
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
    ip_website = "https://icanhazip.com"

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
    return "Unable to Resolve"

def _get_gateway_ip():
    os_name = platform.system()

    if os_name == "Windows":
        try:
            cmd = ["route", "print", "0.0.0.0"]
            gateway_check = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            gateway_line = [line for line in gateway_check.splitlines() if "0.0.0.0" in line and "Default" not in line]
            if gateway_line:
                return gateway_line[0].split()[2]
        except Exception:
            pass
    else:
        try:
            cmd = "netstat -rn | grep default | awk '{print $2}' | head -n 1"
            gateway_check = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
            if gateway_check:
                return gateway_check
        except Exception:
            pass
    return "Unknown"

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
    global _cached_connected_status, _last_conn_check, _cached_public_ip
    _cached_connected_status = False
    _last_conn_check = 0
    _cached_public_ip = None

def get_network():
    total = psutil.net_io_counters()
    now = time.time()
    start_time = 60
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
        "resolvers": list(DNS_RESOLVER.keys())
    }
