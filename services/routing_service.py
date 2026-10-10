import requests
from flask import current_app
from services.hospital_service import haversine_distance, estimate_travel_time

def get_route_and_eta(origin_lat, origin_lng, dest_lat, dest_lng):
    """
    Autonomous multi-engine routing system.
    Requires ZERO manual setup from the user.
    Automatically queries high-speed OSRM routing networks with instant Haversine fallback.
    """
    # Public high-performance routing engines (Zero-key required)
    routing_endpoints = [
        f"https://router.project-osrm.org/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson",
        f"https://routing.openstreetmap.de/routed-car/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
    ]
    
    headers = {'User-Agent': 'EmergencyPass/2.0 (Emergency Coordination Engine)'}

    for url in routing_endpoints:
        try:
            res = requests.get(url, headers=headers, timeout=3.5)
            if res.status_code == 200:
                data = res.json()
                if data.get('code') == 'Ok' and data.get('routes'):
                    route = data['routes'][0]
                    distance_km = round(route.get('distance', 0) / 1000.0, 2)
                    raw_duration_sec = route.get('duration', 0)
                    duration_min = max(1.0, round((raw_duration_sec / 60.0) * 0.85, 1)) # Emergency priority speed
                    
                    geojson_coords = route.get('geometry', {}).get('coordinates', [])
                    leaflet_coords = [[coord[1], coord[0]] for coord in geojson_coords]
                    
                    return {
                        'success': True,
                        'coordinates': leaflet_coords,
                        'distance_km': distance_km,
                        'duration_min': duration_min,
                        'is_fallback': False,
                        'service': 'Autonomous OpenStreetMap Driving Engine (Managed)'
                    }
        except Exception:
            continue

    # Guaranteed Direct Haversine Interpolation
    dist_km = round(haversine_distance(origin_lat, origin_lng, dest_lat, dest_lng), 2)
    dur_min = estimate_travel_time(dist_km, avg_speed_kmh=38.0)
    
    steps = 12
    coords = []
    for i in range(steps + 1):
        t = i / steps
        lat = origin_lat + (dest_lat - origin_lat) * t
        lng = origin_lng + (dest_lng - origin_lng) * t
        coords.append([round(lat, 6), round(lng, 6)])

    return {
        'success': True,
        'coordinates': coords,
        'distance_km': dist_km,
        'duration_min': dur_min,
        'is_fallback': True,
        'service': 'Haversine Direct Highway Highway Interpolation (Offline Ready)'
    }
