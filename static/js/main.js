import { fetchJSON } from "./utils.js";
import { initThemeToggle, initCardCollapse } from "./theme.js";
import { refreshSystemInfo } from "./system.js";
import { refreshCPUInfo } from "./cpu.js";
import { refreshMemoryInfo } from "./memory.js";
import { refreshDiskInfo } from "./disk.js";
import { refreshNetworkInfo, initNetworkCheck, initDNSSelector, initIPSelector } from "./network.js";

let config = {
    TIMERS: {
        frontend_refresh_seconds: 1.5
    }
};

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

async function initDashboard() {
    try {
        const data = await fetchJSON('/static/config.json');
        if (data) config = data; 
    }
    catch (e) {
        console.warn("Failed to load config.json (missing or corrupt). Using defaults.");
    }

    initThemeToggle();
    initCardCollapse();
    initNetworkCheck();
    initDNSSelector();
    initIPSelector();

    const refreshInterval = config.TIMERS?.frontend_refresh_seconds * 1000;
    updateDashboard();
    setInterval(updateDashboard, refreshInterval);
}

initDashboard();