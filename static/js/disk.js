import { formatBytes } from "./utils.js";

export function refreshDiskInfo(diskData) {
    const lines = [];
    for (const [mount, disk] of Object.entries(diskData)) {
        lines.push(` ${mount} (${disk.fs})`,`  ${formatBytes(disk.used)} / ${formatBytes(disk.total)} (${disk.percent}%)`,'');
    }

    document.getElementById('disk').textContent = lines.join('\n');
}