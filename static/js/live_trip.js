/**
 * EmergencyPass — Live Trip Telemetry & Synchronization
 */

let socket = null;
let currentTripId = null;
let pollingInterval = null;

function setupLiveTripSync(tripId, hospitalId) {
    currentTripId = tripId;
    
    // Connect Socket.IO
    if (typeof io !== 'undefined') {
        socket = io();

        socket.on('connect', () => {
            console.log('Connected to Emergency Telemetry Hub');
            socket.emit('join_trip', { trip_id: tripId });
        });

        // Vehicle moved event
        socket.on('vehicle_moved', (data) => {
            if (data.trip_id === tripId) {
                updateLiveVehiclePosition(data);
            }
        });

        // Hospital acknowledgement received
        socket.on('hospital_ack_update', (data) => {
            if (data.trip_id === tripId) {
                updateHospitalAckUI(data);
            }
        });

        // Trip completed/ended
        socket.on('trip_ended_signal', (data) => {
            if (data.trip_id === tripId) {
                const banner = document.getElementById('trip-completed-banner');
                if (banner) banner.style.display = 'block';
            }
        });
    }

    // Secondary Polling Fallback (every 4 seconds)
    pollingInterval = setInterval(() => {
        fetchTripStatusPolling(tripId);
    }, 4000);
}

function updateLiveVehiclePosition(data) {
    // Update marker on Leaflet map
    if (typeof vehicleMarker !== 'undefined' && vehicleMarker) {
        vehicleMarker.setLatLng([data.latitude, data.longitude]);
    }

    // Update telemetry UI indicators
    const etaEl = document.getElementById('live-eta-val');
    if (etaEl && data.remaining_eta_min !== undefined) {
        etaEl.innerText = `${data.remaining_eta_min} min`;
    }

    const distEl = document.getElementById('live-dist-val');
    if (distEl && data.remaining_distance_km !== undefined) {
        distEl.innerText = `${data.remaining_distance_km} km`;
    }

    const timeEl = document.getElementById('last-telemetry-time');
    if (timeEl && data.timestamp) {
        timeEl.innerText = data.timestamp;
    }
}

function updateHospitalAckUI(data) {
    const badge = document.getElementById('hospital-ack-badge');
    const noteEl = document.getElementById('hospital-ack-notes');
    if (badge) {
        badge.className = 'badge bg-success';
        badge.innerText = `STATUS: ${data.status.toUpperCase()}`;
    }
    if (noteEl && data.notes) {
        noteEl.innerHTML = `<div class="alert alert-info mt-2 mb-0"><b>Hospital Note:</b> ${data.notes}</div>`;
    }
}

function fetchTripStatusPolling(tripId) {
    fetch(`/api/emergency/trip/${tripId}/status`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.trip) {
                const trip = data.trip;
                if (trip.status === 'completed' || trip.status === 'reached') {
                    const badge = document.getElementById('trip-status-badge');
                    if (badge) badge.innerText = 'ARRIVED AT HOSPITAL';
                }
            }
        })
        .catch(err => console.log('Polling sync check', err));
}
