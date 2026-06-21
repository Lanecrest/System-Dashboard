// Convert Bytes
export function formatBytes(n) {
    if (n < 1024) return n.toFixed(2) + ' B';
    const units = ['KB','MB','GB','TB'];
    let i = -1;
    do { n = n / 1024; i++; } while (n >= 1024 && i < units.length-1);
    return n.toFixed(2) + ' ' + units[i];
}

// Convert Time
export function formatUptime(totalSeconds) {
    let s = Math.max(0, Math.floor(totalSeconds));
    const days = Math.floor(s / 86400); s %= 86400;
    const hours = Math.floor(s / 3600); s %= 3600;
    const minutes = Math.floor(s / 60);
    const seconds = s % 60;
    const parts = [];
    if (days) parts.push(`${days}d`);
    if (hours) parts.push(`${hours}h`);
    if (minutes) parts.push(`${minutes}m`);
    if (seconds || parts.length === 0) parts.push(`${seconds}s`);
    return parts.join(' ');
}

// Convert Rates
export function formatRate(nowVal, prevVal, dt) {
    if (!prevVal || dt <= 0) return formatBytes(nowVal);
    return formatBytes((nowVal - prevVal) / dt) + '/s';
}

// JSON Handling
export async function fetchJSON(path) {
    const res = await fetch(path);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return res.json();
}

// Export Data
export function initExportButton() {
    const exportButton = document.getElementById('export-stats');
    if (!exportButton) return;
    exportButton.addEventListener('click', async () => {
        try {
            exportButton.disabled = true;
            exportButton.textContent = 'Exporting...';
            const response = await fetch('/api/export-json');
            if (!response.ok) throw new Error('Network response was not ok');
            const blob = await response.blob();
            const disposition = response.headers.get('content-disposition');
            let filename = 'system_stats.json';
            if (disposition && disposition.includes('filename=')) {
                filename = disposition.split('filename=')[1].replace(/["']/g, '').trim();
            }
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(downloadUrl);
        }
        catch (e) {
            console.error('Export failed:', e);
        }
        finally {
            exportButton.disabled = false;
            exportButton.textContent = 'Export Stats';
        }
    });
}