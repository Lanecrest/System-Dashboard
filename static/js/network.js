import { formatRate } from "./utils.js";

let prevNet = null;
export async function refreshNetworkInfo(networkData) {
    // DNS Selection
    const dns = document.getElementById('dns-selector');
    if (dns && dns.options.length === 0 && networkData.resolvers) {
        networkData.resolvers.forEach(resolver => {
            const opt = document.createElement('option');
            opt.value = resolver;
            opt.textContent = resolver;
            dns.appendChild(opt);
        });
    }
    dns.value = networkData.dns;
    // IP Lines
    const net_status = networkData.connected ? 'Up' : 'Down';
    const lines = [
        ` Internet Status: ${net_status} (auto-retry: ${Math.ceil(networkData.counter)}s)`,
        ` Public IP: ${networkData.public_ip}`,
        ` Default Gateway: ${networkData.gateway}`,''
    ];
    const now = networkData.timestamp || Math.floor(Date.now()/1000);
    const dt = prevNet ? Math.max(1, now - prevNet.timestamp) : 0;
    // Network Traffic Line
    const totalRx = formatRate(networkData.total_bytes_recv, prevNet && prevNet.total_bytes_recv, dt);
    const totalTx = formatRate(networkData.total_bytes_sent, prevNet && prevNet.total_bytes_sent, dt);
    lines.push(` Total Traffic:`, `  ↓Rx: ${totalRx} | ↑Tx: ${totalTx}`,'');
    for (const iface of networkData.nic) {
        // Adapter Status Line
        const nic_status = (iface.ips && iface.ips.length) ? 'Up' : 'Down';
        lines.push(` ${iface.name}:`,`  Status: ${nic_status}`);
        // MAC Address Line
        if (iface.mac) lines.push(`  MAC: ${iface.mac}`);
        // IP v4 & v6 Lines
        if (iface.ips && iface.ips.length) {
            const v4 = iface.ips.filter(ip => ip.includes('.'));
            const v6 = iface.ips.filter(ip => ip.includes(':'));
            if (v4.length) lines.push(`  IPv4: ${v4.join(', ')}`);
            if (v6.length) lines.push(`  IPv6: ${v6.join(', ')}`);
        }
        // Adapter Traffic Lines
        const prevIface = prevNet && prevNet.nic && prevNet.nic.find(i => i.name === iface.name);
        const rx = formatRate(iface.bytes_recv, prevIface && prevIface.bytes_recv, dt);
        const tx = formatRate(iface.bytes_sent, prevIface && prevIface.bytes_sent, dt);
        lines.push(`  ↓Rx: ${rx} | ↑Tx: ${tx}`,'');
    }

    document.getElementById('network').textContent = lines.join('\n');
    prevNet = networkData;
}