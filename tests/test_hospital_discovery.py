import json
import pytest
from app import create_app
from database import db
from models import Hospital
from services.hospital_service import find_nearby_hospitals, haversine_distance, classify_emergency_type, is_ineligible_clinic, hospital_matches_emergency

@pytest.fixture
def app_ctx():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Seed Pan-India test hospitals with distinct specialties & cities
        h_delhi = Hospital(
            name='AIIMS New Delhi Apex Trauma Center',
            address='Ansari Nagar',
            city='Delhi NCR',
            latitude=28.5672,
            longitude=77.2100,
            phone='011-26588500',
            trauma_level='Level 1 Apex Trauma Center',
            emergency_type='24/7 Comprehensive Trauma & Cardiac ER',
            specialties_json=json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general'])
        )
        h_mumbai = Hospital(
            name='KEM Hospital & Apex Trauma Center Mumbai',
            address='Parel',
            city='Mumbai',
            latitude=18.9986,
            longitude=72.8427,
            phone='022-24107000',
            trauma_level='Level 1 Trauma Center',
            emergency_type='24/7 Multi-Specialty ER',
            specialties_json=json.dumps(['cardiac', 'trauma', 'stroke', 'general'])
        )
        h_bengaluru = Hospital(
            name='Narayana Institute of Cardiac Sciences Bengaluru',
            address='Bommasandra',
            city='Bengaluru',
            latitude=12.8055,
            longitude=77.6975,
            phone='080-71222222',
            trauma_level='Level 1 Cardiac Hub',
            emergency_type='24/7 Cath Lab & Cardiac Care',
            specialties_json=json.dumps(['cardiac', 'general'])
        )
        h_chennai = Hospital(
            name='Apollo Hospitals Greams Road Chennai',
            address='Greams Lane',
            city='Chennai',
            latitude=13.0604,
            longitude=80.2496,
            phone='044-28290200',
            trauma_level='Level 1 Trauma Center',
            emergency_type='24/7 Emergency & Stroke Hub',
            specialties_json=json.dumps(['cardiac', 'trauma', 'stroke', 'obstetric', 'pediatric', 'general'])
        )
        h_kochi = Hospital(
            name='Aster Medcity Kochi',
            address='Cheranalloor',
            city='Kochi / Kerala',
            latitude=10.0545,
            longitude=76.2655,
            phone='0484-6699999',
            trauma_level='Level 1 Trauma Center',
            emergency_type='24/7 Multi-Specialty & PICU',
            specialties_json=json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general'])
        )
        h_eye = Hospital(
            name='National Eye Care & Laser Clinic',
            address='Ring Road',
            city='Delhi NCR',
            latitude=28.5600,
            longitude=77.2000,
            phone='011-99999999',
            trauma_level='Outpatient Clinic',
            emergency_type='Daycare Cataract Surgery',
            specialties_json=json.dumps(['general'])
        )
        h_dental = Hospital(
            name='Apollo White Dental Lounge',
            address='Koramangala',
            city='Bengaluru',
            latitude=12.9300,
            longitude=77.6200,
            phone='080-88888888',
            trauma_level='Outpatient Clinic',
            emergency_type='Dental Clinic',
            specialties_json=json.dumps(['general'])
        )

        db.session.add_all([h_delhi, h_mumbai, h_bengaluru, h_chennai, h_kochi, h_eye, h_dental])
        db.session.commit()
        yield app
        db.drop_all()

def test_ineligible_clinic_filter():
    assert is_ineligible_clinic("National Eye Care & Laser Clinic") is True
    assert is_ineligible_clinic("Apollo White Dental Lounge") is True
    assert is_ineligible_clinic("Kottakkal Arya Vaidya Sala Ayurvedic Clinic") is True
    assert is_ineligible_clinic("Cosmetic Skin & Hair Transplant Center") is True
    
    assert is_ineligible_clinic("AIIMS New Delhi Apex Trauma Center") is False
    assert is_ineligible_clinic("Narayana Institute of Cardiac Sciences") is False
    assert is_ineligible_clinic("Aster Medcity Kochi") is False

def test_pan_india_discovery(app_ctx):
    # From Delhi coordinates
    delhi_lat, delhi_lng = 28.5672, 77.2100

    results = find_nearby_hospitals(delhi_lat, delhi_lng, emergency_type="Cardiac Arrest / Acute Chest Pain", scope='all_india')
    names = [h['name'] for h in results]

    # Must contain top hospitals across India
    assert 'AIIMS New Delhi Apex Trauma Center' in names
    assert 'Narayana Institute of Cardiac Sciences Bengaluru' in names
    assert 'Aster Medcity Kochi' in names
    assert 'Apollo Hospitals Greams Road Chennai' in names

    # Must NEVER contain eye clinics or dental clinics
    assert 'National Eye Care & Laser Clinic' not in names
    assert 'Apollo White Dental Lounge' not in names

def test_city_filter(app_ctx):
    delhi_lat, delhi_lng = 28.5672, 77.2100

    # Filter by Bengaluru city
    bengaluru_results = find_nearby_hospitals(delhi_lat, delhi_lng, emergency_type="Cardiac Arrest / Acute Chest Pain", city_filter="Bengaluru")
    b_names = [h['name'] for h in bengaluru_results]

    assert 'Narayana Institute of Cardiac Sciences Bengaluru' in b_names
    assert 'AIIMS New Delhi Apex Trauma Center' not in b_names
