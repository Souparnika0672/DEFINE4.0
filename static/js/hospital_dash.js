/**
 * EmergencyPass — Hospital ER Command Triage Desk
 */

let hospitalSocket = null;

function initHospitalDashboard(hospitalId) {
    if (typeof io === 'undefined') return;

    hospitalSocket = io();

    hospitalSocket.on('connect', () => {
        console.log(`Hospital ER Desk connected for Hospital #${hospitalId}`);
        hospitalSocket.emit('join_hospital_room', { hospital_id: hospitalId });
    });

    // Receive incoming emergency alerts
    hospitalSocket.on('incoming_emergency_alert', (data) => {
        playEmergencyAudioChime();
        renderIncomingTripCard(data);
        showBrowserNotification(`INCOMING EMERGENCY: ${data.vehicle_reg}`, data.message);
    });

    // Receive live telemetry movement
    hospitalSocket.on('hospital_trip_update', (data) => {
        const etaBadge = document.getElementById(`trip-eta-${data.trip_id}`);
        if (etaBadge && data.remaining_eta_min !== undefined) {
            etaBadge.innerText = `${data.remaining_eta_min} min ETA`;
        }
    });
}

function renderIncomingTripCard(trip) {
    const container = document.getElementById('incoming-emergencies-container');
    if (!container) return;

    // Remove empty state message if present
    const emptyState = document.getElementById('no-incoming-state');
    if (emptyState) emptyState.style.display = 'none';

    const cardId = `trip-card-${trip.trip_id}`;
    if (document.getElementById(cardId)) return; // Already rendered

    const cardHtml = `
        <div id="${cardId}" class="card-dark card-emergency mb-3 animate__animated animate__fadeInDown">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <span class="badge bg-danger mb-2">INCOMING ACTIVE TRANSIT</span>
                    <h5 class="mb-1 text-white">${trip.vehicle_reg} — ${trip.vehicle_type}</h5>
                    <p class="text-muted small mb-1">${trip.user_name} (${trip.user_phone})</p>
                    <p class="text-warning small mb-2"><b>Emergency:</b> ${trip.emergency_type}</p>
                </div>
                <div class="text-end">
                    <span id="trip-eta-${trip.trip_id}" class="badge bg-primary fs-6 mb-2">${trip.eta_minutes} min ETA</span>
                    <div class="text-muted small">${trip.distance_km} km away</div>
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.1);">
            <form action="/hospital/acknowledge/${trip.trip_id}" method="POST" class="row g-2 align-items-center">
                <div class="col-md-4">
                    <select name="status" class="form-select form-select-sm form-select-dark">
                        <option value="accepted">Accept & Prepare ER Bay</option>
                        <option value="standby">Standby / In Transit</option>
                        <option value="patient_arrived">Mark Patient Arrived</option>
                        <option value="diverted">Divert (Capacity Full)</option>
                    </select>
                </div>
                <div class="col-md-5">
                    <input type="text" name="notes" placeholder="Triage notes / ER room number" class="form-control form-control-sm form-control-dark">
                </div>
                <div class="col-md-3 text-end">
                    <button type="submit" class="btn btn-sm btn-primary-custom w-100">Submit Triage</button>
                </div>
            </form>
        </div>
    `;

    container.insertAdjacentHTML('afterbegin', cardHtml);
}

function playEmergencyAudioChime() {
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
        osc.frequency.setValueAtTime(1174.66, audioCtx.currentTime + 0.15); // D6
        gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.5);
    } catch (e) {
        console.log('Audio chime not supported');
    }
}

function showBrowserNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, { body: body, icon: '/static/favicon.ico' });
    }
}
