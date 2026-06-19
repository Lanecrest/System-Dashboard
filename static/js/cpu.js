export function refreshCPUInfo(cpuData) {
    const lines = [];
    lines.push(` ${cpuData.physical}c/${cpuData.logical}t @ ${cpuData.freq.max} MHz (${cpuData.percent}%) `);
        cpuData.per_core_percent.forEach((usage, index) => {
            lines.push(`  Core ${index}: ${usage}%`);
        });

    document.getElementById('cpu').textContent = lines.join('\n');
}