import { formatUptime } from "./utils.js";

let systemDisplay = null;

export function initSystemModule() {
    systemDisplay = document.getElementById('system');
}

export function refreshSystemInfo(systemData) {
    if (!systemData) return;
        const lines = [
            `  Device: ${systemData.device || 'Unknown'}`,
            `  Serial: ${systemData.serial || 'Unknown'}`,
            `  Arch: ${systemData.arch || 'Unknown'}`,
            `  OS: ${systemData.os || 'Unknown'} ${systemData.release || ''}`,
            `  Kernel: ${systemData.kernel || 'Unknown'}`,
            `  Host: ${systemData.host || 'Unknown'}`,
            `  Uptime: ${formatUptime(systemData.uptime || 0)}`
        ];

    if (systemData.battery) {
        const { percent, power_plugged, charging, secs_left } = systemData.battery;
        let status = "Discharging";

        if (power_plugged) {
            status = (charging || percent < 99) ? "Plugged In (Charging)" : "Plugged In (Idle)";
        }
        else if (secs_left && secs_left > 0) {
            status = `Discharging (${formatUptime(secs_left)})`;
        }
        else {
            status = "Discharging (Calculating...)";
        }
        lines.push(`  Battery: ${percent ?? 0}% [${status}]`);
    }

    if (systemDisplay) {
        systemDisplay.textContent = lines.join('\n');
    }
}
