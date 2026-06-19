import { formatBytes } from "./utils.js";

export function refreshMemoryInfo(memoryData) {
    const lines = [];
    lines.push(` Total:`, `  ${formatBytes(memoryData.used)} / ${formatBytes(memoryData.total)} (${memoryData.percent}%)`,'');
    lines.push(` Top 10 Processes:`)
    if (memoryData.per_process && memoryData.per_process.length) {
        memoryData.per_process.forEach((p) => {
            lines.push(`  ${p.name}: ${formatBytes(p.memory_info.rss)} (${p.memory_percent.toFixed(1)}%)`);
        });
    }

    document.getElementById('memory').textContent = lines.join('\n');
}