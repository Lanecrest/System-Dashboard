import { formatRate } from "./utils.js";

let prevNet = null;
let networkButton = null;
let dnsSelector = null;
let ipSelector = null;
let networkDisplay = null;

export function initNetworkModule() {
    dnsSelector = document.getElementById('dns-selector');
    ipSelector = document.getElementById('ip-checker');
    networkButton = document.getElementById('network-check');
    networkDisplay = document.getElementById('network');

    if (networkButton) {
        networkButton.addEventListener('click', async () => {
            try {
                networkButton.disabled = true;
                networkButton.textContent = '....';
                const response = await fetch('/api/matrix/net-check', { method: 'POST' });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                refreshNetworkInfo(data.network);
            } catch (e) {
                console.error('Check failed:', e);
            } finally {
                if (networkButton) {
                    networkButton.disabled = false;
                    networkButton.textContent = 'Ping';
                }
            }
        });
    }

    if (dnsSelector) {
        dnsSelector.addEventListener('change', async () => {
            try {
                await fetch('/api/matrix/set-dns', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ resolver: dnsSelector.value })
                });
            } catch (e) {
                console.error('Failed to update DNS resolver:', e);
            }
        });
    }

    if (ipSelector) {
        ipSelector.addEventListener('change', async () => {
            try {
                await fetch('/api/matrix/ip-check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ checker: ipSelector.value })
                });
            } catch (e) {
                console.error('Failed to update IP checker:', e);
            }
        });
    }
}

export async function refreshNetworkInfo(networkData) {
    // DNS Selection
    if (dnsSelector && dnsSelector.options.length === 0 && networkData.resolvers) {
        const frag = document.createDocumentFragment();
        networkData.resolvers.forEach(resolver => {
            const opt = document.createElement('option');
            opt.value = opt.textContent = resolver;
            frag.appendChild(opt);
        });
        dnsSelector.appendChild(frag);
    }
    if (dnsSelector) dnsSelector.value = networkData.dns;

    // IP API Selection
    if (ipSelector && ipSelector.options.length === 0 && networkData.checkers) {
        const frag = document.createDocumentFragment();
        networkData.checkers.forEach(checker => {
            const opt = document.createElement('option');
            opt.value = opt.textContent = checker;
            frag.appendChild(opt);
        });
        ipSelector.appendChild(frag);
    }
    if (ipSelector) ipSelector.value = networkData.ipapi;

    // IP Lines
    const net_status = networkData.connected ? 'Up' : 'Down';
    const lines = [
        ` Internet Status: ${net_status} (auto-ping: ${Math.ceil(networkData.counter)}s)`,
        ` Public IP: ${networkData.public_ip}`,
        ` Default Gateway: ${networkData.gateway}`,''
    ];
    const now = networkData.timestamp || Math.floor(Date.now()/1000);
    const dt = prevNet ? Math.max(1, now - prevNet.timestamp) : 0;

    // Network Traffic Line
    const totalRx = formatRate(networkData.total_bytes_recv, prevNet && prevNet.total_bytes_recv, dt);
    const totalTx = formatRate(networkData.total_bytes_sent, prevNet && prevNet.total_bytes_sent, dt);
    lines.push(` Total Traffic:`, `  ↓Rx: ${totalRx} | ↑Tx: ${totalTx}`,'');

    // NIC Lines
    const prevNicsMap = {};
    if (prevNet?.nic) {
        for (let i = 0; i < prevNet.nic.length; i++) {
            prevNicsMap[prevNet.nic[i].name] = prevNet.nic[i];
        }
    }
    const nics = networkData.nic || [];
    for (let i = 0; i < nics.length; i++) {
        const iface = nics[i];
        const hasIps = iface.ips && iface.ips.length;
        const nic_status = hasIps ? 'Up' : 'Down';
        lines.push(` ${iface.name}:`, `  Status: ${nic_status}`);
        if (iface.mac) lines.push(`  MAC: ${iface.mac}`);
        if (hasIps) {
            const v4 = [];
            const v6 = [];
            for (let j = 0; j < iface.ips.length; j++) {
                const ip = iface.ips[j];
                if (ip.includes('.')) v4.push(ip);
                else if (ip.includes(':')) v6.push(ip);
            }
            if (v4.length) lines.push(`  IPv4: ${v4.join(', ')}`);
            if (v6.length) lines.push(`  IPv6: ${v6.join(', ')}`);
        }
        const prevIface = prevNicsMap[iface.name];
        const rx = formatRate(iface.bytes_recv, prevIface?.bytes_recv, dt);
        const tx = formatRate(iface.bytes_sent, prevIface?.bytes_sent, dt);
        lines.push(`  ↓Rx: ${rx} | ↑Tx: ${tx}`, '');
    }

    if (networkDisplay) networkDisplay.textContent = lines.join('\n');
    prevNet = networkData;
}
