/**
 * EmergencyPass — Road Vicinity Driver Alert Client
 */

let driverSocket = null;

function initDriverVicinityAlerts() {
    if (typeof io === 'undefined') return;

    driverSocket = io();
    driverSocket.on('connect', () => {
        driverSocket.emit('join_driver_channel');
    });

    driverSocket.on('driver_proximity_alert', (data) => {
        showDriverAlertBanner(data);
    });

    driverSocket.on('trip_ended_signal', (data) => {
        hideDriverAlertBanner();
    });
}

function showDriverAlertBanner(alertData) {
    let banner = document.getElementById('driver-alert-banner');
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'driver-alert-banner';
        banner.className = 'driver-alert-banner';
        document.body.appendChild(banner);
    }

    banner.innerHTML = `
        <div class="d-flex align-items-start gap-3">
            <div style="font-size: 2.2rem; line-height: 1;">⚠️</div>
            <div class="flex-grow-1">
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <span class="badge bg-danger">EMERGENCY VEHICLE APPROACHING</span>
                    <button onclick="hideDriverAlertBanner()" class="btn-close btn-close-white" style="font-size: 0.75rem;"></button>
                </div>
                <h6 class="text-white mb-1">${alertData.vehicle_reg} (${alertData.vehicle_type || 'Car'})</h6>
                <p class="small text-light mb-2">Heading towards <b>${alertData.hospital_name}</b>. Approx. ${alertData.eta_minutes} mins away.</p>
                <div class="p-2 rounded" style="background: rgba(230, 57, 70, 0.2); border: 1px solid rgba(230, 57, 70, 0.4); font-size: 0.8rem; color: #ffccd5;">
                    🛡️ <b>Safety Advisory:</b> Please stay alert, yield the fast lane, and give way only when safe. Do not violate traffic signals.
                </div>
            </div>
        </div>
    `;

    banner.style.display = 'block';
    
    // Play alert tone
    if (typeof playEmergencyAudioChime === 'function') {
        playEmergencyAudioChime();
    }
}

function hideDriverAlertBanner() {
    const banner = document.getElementById('driver-alert-banner');
    if (banner) banner.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    initDriverVicinityAlerts();
});
