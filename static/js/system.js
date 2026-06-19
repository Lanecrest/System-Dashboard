import { formatUptime } from "./utils.js";

export function refreshSystemInfo(systemData) {
        const lines = [];
        lines.push(
        `  Device: ${systemData.device}`,
        `  Serial: ${systemData.serial}`,
        `  Arch: ${systemData.arch}`,
        `  OS: ${systemData.os} ${systemData.release}`,
        `  Kernel: ${systemData.kernel}`,
        `  Host: ${systemData.host}`,
        `  Uptime: ${formatUptime(systemData.uptime)}`,
        );
        if (systemData.battery) {
            let status = "Discharging";
            if (systemData.battery.power_plugged) {
                if (systemData.battery.charging) {
                    status = "Plugged In (Charging)";
                }
                else {
                    status = "Plugged In (Idle)";
                }
            }
            else if (systemData.battery.secs_left && systemData.battery.secs_left > 0) {
                status = `Discharging (${formatUptime(systemData.battery.secs_left)})`;
            }
            else {
                status = "Discharging (Calculating...)";
            }
            lines.push(`  Battery: ${systemData.battery.percent}% [${status}]`);
        }
        
        document.getElementById('system').textContent = lines.join('\n');
}