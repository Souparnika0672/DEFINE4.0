/**
 * EmergencyPass — Police & Emergency Tactical Response Command
 */

let policeSocket = null;
let policeMap = null;
let activeVehicleMarkers = {};

function initPoliceDashboard() {
    policeMap = initLeafletMap('police-tactical-map', 9.9816, 76.2999, 12);

    if (typeof io !== 'undefined') {
        policeSocket = io();
        
        policeSocket.on('connect', () => {
            console.log('Police Command Center connected.');
            policeSocket.emit('join_police_channel');
        });

        policeSocket.on('new_emergency_trip', (trip) => {
            addPoliceVehicleMarker(trip);
            playEmergencyAudioChime();
        });

        policeSocket.on('police_vehicle_moved', (data) => {
            if (activeVehicleMarkers[data.trip_id]) {
                activeVehicleMarkers[data.trip_id].setLatLng([data.latitude, data.longitude]);
            }
        });

        policeSocket.on('trip_ended_signal', (data) => {
            if (activeVehicleMarkers[data.trip_id]) {
                policeMap.removeLayer(activeVehicleMarkers[data.trip_id]);
                delete activeVehicleMarkers[data.trip_id];
            }
        });
    }

    // Load initial active trips
    fetch('/api/active-emergencies')
        .then(res => res.json())
        .then(data => {
            if (data.success && data.trips) {
                data.trips.forEach(t => addPoliceVehicleMarker(t));
            }
        });
}

function addPoliceVehicleMarker(trip) {
    if (activeVehicleMarkers[trip.id]) return;

    const marker = L.marker([trip.current_lat, trip.current_lng], { icon: createVehicleIcon(true) });
    marker.bindPopup(`
        <div style="font-family: sans-serif; min-width: 200px;">
            <span class="badge bg-danger">EMERGENCY VEHICLE</span>
            <h6 style="margin: 6px 0 2px 0;">${trip.vehicle_reg}</h6>
            <small style="color: #64748b;">${trip.vehicle_model} (${trip.vehicle_color})</small><br>
            <div style="margin-top: 4px; font-size: 13px;">
                <b>Destination:</b> ${trip.hospital_name || 'Nearest ER'}<br>
                <b>ETA:</b> ~${trip.estimated_time_minutes} mins
            </div>
            <hr style="margin: 6px 0;">
            <button onclick="flagSuspiciousTrip('${trip.id}')" class="btn btn-sm btn-outline-danger w-100" style="font-size: 11px;">
                Flag Suspicious Misuse
            </button>
        </div>
    `);
    marker.addTo(policeMap);
    activeVehicleMarkers[trip.id] = marker;
}

function flagSuspiciousTrip(tripId) {
    const reason = prompt(`Please specify the reason for flagging Trip ${tripId}:`, 'suspicious_frequent_activation');
    if (!reason) return;
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/incidents/report';
    
    const tripInput = document.createElement('input');
    tripInput.name = 'trip_id';
    tripInput.value = tripId;
    form.appendChild(tripInput);

    const reasonInput = document.createElement('input');
    reasonInput.name = 'reason';
    reasonInput.value = reason;
    form.appendChild(reasonInput);

    const notesInput = document.createElement('input');
    notesInput.name = 'evidence_notes';
    notesInput.value = 'Flagged from Police Command Tactical Map Inspector.';
    form.appendChild(notesInput);

    document.body.appendChild(form);
    form.submit();
}
