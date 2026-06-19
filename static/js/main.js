import { fetchJSON, initNetworkCheck, initDNSSelector } from "./utils.js";
import { initThemeToggle, initCardCollapse } from "./theme.js";
import { refreshSystemInfo } from "./system.js";
import { refreshCPUInfo } from "./cpu.js";
import { refreshMemoryInfo } from "./memory.js";
import { refreshDiskInfo } from "./disk.js";
import { refreshNetworkInfo } from "./network.js";

initThemeToggle();
initCardCollapse();
initNetworkCheck(refreshNetworkInfo);
initDNSSelector(refreshNetworkInfo);

async function updateDashboard() {
    try {
        const data = await fetchJSON('/api/matrix');
        refreshSystemInfo(data.system);
        refreshCPUInfo(data.cpu);
        refreshMemoryInfo(data.memory);
        refreshDiskInfo(data.disk);
        refreshNetworkInfo(data.network);
    }
    catch (e) {
        const errMsg = 'Error fetching matrix updates: ' + e.message;
        document.getElementById('system').textContent = errMsg;
        document.getElementById('cpu').textContent = errMsg;
        document.getElementById('memory').textContent = errMsg;
        document.getElementById('disk').textContent = errMsg;
        document.getElementById('network').textContent = errMsg;
    }
}

updateDashboard();
setInterval(updateDashboard, 1500);