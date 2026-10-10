/**
 * EmergencyPass — Leaflet Interactive Map Module
 * Uses Free, Open-Source OpenStreetMap Tile Provider (Zero API Key Required, No Watermarks)
 */

let emergencyMap = null;
let vehicleMarker = null;
let hospitalMarker = null;
let routePolyline = null;
let hospitalMarkersLayer = null;

function initLeafletMap(containerId, centerLat = 9.9816, centerLng = 76.2999, zoom = 13) {
    if (emergencyMap) {
        try {
            emergencyMap.remove();
        } catch (e) {
            console.warn('Map cleanup notice:', e);
        }
    }

    emergencyMap = L.map(containerId, {
        zoomControl: true,
        attributionControl: true
    }).setView([centerLat, centerLng], zoom);

    // Official Free OpenStreetMap Standard Tiles (Zero API key required, 100% watermark-free)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
        maxZoom: 19,
        crossOrigin: true
    }).addTo(emergencyMap);

    return emergencyMap;
}

function createVehicleIcon(isEmergency = true) {
    const iconHtml = `
        <div class="custom-map-icon vehicle-icon ${isEmergency ? 'pulse-danger' : ''}">
            <div style="background: linear-gradient(135deg, #ef4444, #b91c1c); color: #ffffff; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 2.5px solid #ffffff; box-shadow: 0 0 18px rgba(239, 68, 68, 0.9); font-size: 20px;">
                🚨
            </div>
        </div>
    `;
    return L.divIcon({
        html: iconHtml,
        className: 'vehicle-div-icon',
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -22]
    });
}

function createHospitalIcon(badgeType = 'hospital') {
    let iconChar = '🏥';
    let bgGradient = 'linear-gradient(135deg, #10b981, #047857)';
    let shadowColor = 'rgba(16, 185, 129, 0.85)';

    if (badgeType === 'cardiac') {
        iconChar = '❤️';
        bgGradient = 'linear-gradient(135deg, #e11d48, #9f1239)';
        shadowColor = 'rgba(225, 29, 72, 0.85)';
    } else if (badgeType === 'trauma') {
        iconChar = '🚨';
        bgGradient = 'linear-gradient(135deg, #f97316, #c2410c)';
        shadowColor = 'rgba(249, 115, 22, 0.85)';
    } else if (badgeType === 'stroke') {
        iconChar = '🧠';
        bgGradient = 'linear-gradient(135deg, #8b5cf6, #6d28d9)';
        shadowColor = 'rgba(139, 92, 246, 0.85)';
    } else if (badgeType === 'maternity' || badgeType === 'obstetric') {
        iconChar = '🤰';
        bgGradient = 'linear-gradient(135deg, #ec4899, #be185d)';
        shadowColor = 'rgba(236, 72, 153, 0.85)';
    } else if (badgeType === 'pediatric') {
        iconChar = '👶';
        bgGradient = 'linear-gradient(135deg, #06b6d4, #0e7490)';
        shadowColor = 'rgba(6, 182, 212, 0.85)';
    }

    const iconHtml = `
        <div class="custom-map-icon hospital-icon">
            <div style="background: ${bgGradient}; color: #ffffff; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; border: 2px solid #ffffff; box-shadow: 0 0 14px ${shadowColor}; font-size: 19px;">
                ${iconChar}
            </div>
        </div>
    `;
    return L.divIcon({
        html: iconHtml,
        className: 'hospital-div-icon',
        iconSize: [38, 38],
        iconAnchor: [19, 19],
        popupAnchor: [0, -20]
    });
}

function renderTripRoute(originLat, originLng, destLat, destLng, routeCoords = null) {
    if (!emergencyMap) return;

    // Add or update vehicle marker
    if (!vehicleMarker) {
        vehicleMarker = L.marker([originLat, originLng], { icon: createVehicleIcon(true) }).addTo(emergencyMap);
        vehicleMarker.bindPopup(`
            <div style="font-family: sans-serif; min-width: 170px; padding: 4px;">
                <b style="font-size: 14px; color: #ef4444;">🚨 Active Emergency Transit</b><br>
                <span style="font-size: 12px; color: #334155;">Live GPS Corridor Broadcast</span>
            </div>
        `);
    } else {
        vehicleMarker.setLatLng([originLat, originLng]);
    }

    // Add or update hospital destination marker
    if (destLat && destLng) {
        if (!hospitalMarker) {
            hospitalMarker = L.marker([destLat, destLng], { icon: createHospitalIcon('hospital') }).addTo(emergencyMap);
            hospitalMarker.bindPopup(`
                <div style="font-family: sans-serif; min-width: 180px; padding: 4px;">
                    <b style="font-size: 14px; color: #10b981;">🏥 Receiving Hospital ER</b><br>
                    <span style="font-size: 12px; color: #334155;">Trauma Bay & Medical Team Prepared</span>
                </div>
            `);
        } else {
            hospitalMarker.setLatLng([destLat, destLng]);
        }
    }

    // Draw route polyline
    if (routeCoords && routeCoords.length > 0) {
        if (routePolyline) {
            emergencyMap.removeLayer(routePolyline);
        }
        routePolyline = L.polyline(routeCoords, {
            color: '#ef4444',
            weight: 6,
            opacity: 0.9,
            dashArray: '10, 6',
            smoothFactor: 1
        }).addTo(emergencyMap);

        const bounds = L.latLngBounds(routeCoords);
        emergencyMap.fitBounds(bounds, { padding: [45, 45] });
    }
}

function renderHospitalListMarkers(hospitals, onHospitalClick = null) {
    if (!emergencyMap) return;

    if (hospitalMarkersLayer) {
        emergencyMap.removeLayer(hospitalMarkersLayer);
    }
    hospitalMarkersLayer = L.layerGroup().addTo(emergencyMap);

    const bounds = [];
    hospitals.forEach((h, index) => {
        let iconType = 'hospital';
        const specs = h.specialties || [];
        if (specs.includes('cardiac')) iconType = 'cardiac';
        else if (specs.includes('trauma')) iconType = 'trauma';
        else if (specs.includes('stroke')) iconType = 'stroke';
        else if (specs.includes('obstetric') || specs.includes('maternity')) iconType = 'maternity';
        else if (specs.includes('pediatric')) iconType = 'pediatric';

        const marker = L.marker([h.latitude, h.longitude], { icon: createHospitalIcon(iconType) });
        marker.bindPopup(`
            <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 210px; padding: 4px;">
                <div style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 2px;">${h.name}</div>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">📍 ${h.address}</div>
                <div style="display: inline-block; background: #e0f2fe; color: #0369a1; font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-bottom: 4px;">
                    ${h.trauma_level || 'Emergency Center'}
                </div>
                <div style="font-size: 13px; font-weight: 700; color: #dc2626; margin-top: 4px;">
                    ⚡ ${h.distance_km} km • ~${h.estimated_time_min} mins
                </div>
                <div style="font-size: 11px; color: #059669; font-weight: 600; margin-top: 2px;">
                    🛏️ ICU Beds: ${h.available_icu_beds || 5} Available
                </div>
            </div>
        `);
        if (onHospitalClick) {
            marker.on('click', () => onHospitalClick(h, index + 1));
        }
        marker.addTo(hospitalMarkersLayer);
        bounds.push([h.latitude, h.longitude]);
    });

    if (bounds.length > 0) {
        emergencyMap.fitBounds(bounds, { padding: [35, 35] });
    }
}
