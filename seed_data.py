import json
from datetime import datetime, timedelta
from database import db
from models import Role, User, Hospital, Vehicle, VehicleVerification, EmergencyTrip, LocationUpdate, AuditLog

def seed_database():
    print("Seeding database with default roles, Pan-India hospitals, vehicles, and demonstration users...")
    
    # 1. Roles
    roles_data = [
        ('user', 'Standard citizen and private vehicle owner'),
        ('hospital', 'Authorized hospital emergency desk personnel'),
        ('police', 'Authorized police and emergency response command'),
        ('admin', 'System administrator with full supervisory privileges')
    ]
    roles = {}
    for name, desc in roles_data:
        r = Role.query.filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=desc)
            db.session.add(r)
        roles[name] = r
    db.session.commit()

    # 2. Comprehensive Pan-India Emergency Hospital Medical Registry
    pan_india_hospitals = [
        # --- DELHI NCR ---
        {
            'name': 'AIIMS (All India Institute of Medical Sciences) New Delhi',
            'address': 'Ansari Nagar East, Ring Road',
            'city': 'Delhi NCR',
            'latitude': 28.5672,
            'longitude': 77.2100,
            'phone': '+91 11 2658 8500',
            'emergency_contact': '+91 11 2658 8700',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Apex Trauma, Resuscitation, Cardiac & Neuro Emergency Center',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 80,
            'available_icu_beds': 18,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Safdarjung Hospital & Apex Trauma Centre',
            'address': 'Opposite AIIMS, Ring Road',
            'city': 'Delhi NCR',
            'latitude': 28.5700,
            'longitude': 77.2070,
            'phone': '+91 11 2616 5060',
            'emergency_contact': '+91 11 2616 5070',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Critical Trauma, Burns & Acute Emergency Department',
            'specialties_json': json.dumps(['trauma', 'general', 'cardiac', 'stroke']),
            'total_icu_beds': 60,
            'available_icu_beds': 12,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Fortis Escorts Heart Institute',
            'address': 'Okhla Road, New Friends Colony',
            'city': 'Delhi NCR',
            'latitude': 28.5606,
            'longitude': 77.2778,
            'phone': '+91 11 4713 5000',
            'emergency_contact': '+91 11 4713 5555',
            'trauma_level': 'Level 1 Cardiac Hub',
            'emergency_type': '24/7 Dedicated Interventional Cardiology, Cath Lab & Heart Attack ER',
            'specialties_json': json.dumps(['cardiac', 'general']),
            'total_icu_beds': 50,
            'available_icu_beds': 14,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Medanta - The Medicity',
            'address': 'CH Bakhtawar Singh Road, Sector 38',
            'city': 'Gurugram / Delhi NCR',
            'latitude': 28.4395,
            'longitude': 77.0427,
            'phone': '+91 124 414 1414',
            'emergency_contact': '+91 124 483 4567',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Super-Specialty Trauma, Neuro, Heart & Multi-Organ Critical Care',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 90,
            'available_icu_beds': 22,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Max Super Speciality Hospital Saket',
            'address': '1, 2 Press Enclave Marg, Saket',
            'city': 'Delhi NCR',
            'latitude': 28.5273,
            'longitude': 77.2155,
            'phone': '+91 11 2651 5050',
            'emergency_contact': '+91 11 4055 4055',
            'trauma_level': 'Level 1 Stroke & Trauma Hub',
            'emergency_type': '24/7 Comprehensive Stroke, Trauma & Cardiac Resuscitation',
            'specialties_json': json.dumps(['stroke', 'cardiac', 'trauma', 'general']),
            'total_icu_beds': 45,
            'available_icu_beds': 11,
            'is_verified': True,
            'is_demo': False
        },

        # --- MUMBAI & MAHARASHTRA ---
        {
            'name': 'KEM Hospital & Seth GS Medical College',
            'address': 'Acharya Donde Marg, Parel',
            'city': 'Mumbai',
            'latitude': 18.9986,
            'longitude': 72.8427,
            'phone': '+91 22 2410 7000',
            'emergency_contact': '+91 22 2410 7600',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Public Apex Trauma, Surgery & Multi-Specialty Resuscitation',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'obstetric', 'pediatric', 'general']),
            'total_icu_beds': 70,
            'available_icu_beds': 15,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Kokilaben Dhirubhai Ambani Hospital',
            'address': 'Rao Saheb Achutrao Patwardhan Marg, Andheri West',
            'city': 'Mumbai',
            'latitude': 19.1314,
            'longitude': 72.8256,
            'phone': '+91 22 4269 6969',
            'emergency_contact': '+91 22 4269 9999',
            'trauma_level': 'Level 1 Super-Specialty ER',
            'emergency_type': '24/7 Full-Spectrum Stroke Unit, Children ER, Cath Lab & Trauma Hub',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'general']),
            'total_icu_beds': 65,
            'available_icu_beds': 16,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Lilavati Hospital and Research Centre',
            'address': 'A-791, Bandra Reclamation, Bandra West',
            'city': 'Mumbai',
            'latitude': 19.0515,
            'longitude': 72.8290,
            'phone': '+91 22 2675 1000',
            'emergency_contact': '+91 22 2656 8000',
            'trauma_level': 'Level 1 Cardiac & Trauma Hub',
            'emergency_type': '24/7 Interventional Cardiology & Multi-Specialty Critical Care',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general']),
            'total_icu_beds': 40,
            'available_icu_beds': 10,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Ruby Hall Clinic & Apex Trauma Center',
            'address': '40, Sassoon Road, Sangamvadi',
            'city': 'Pune',
            'latitude': 18.5308,
            'longitude': 73.8770,
            'phone': '+91 20 6645 5100',
            'emergency_contact': '+91 20 6645 5200',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Neuro-Trauma, Cardiac ICU & Emergency Medical Services',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general', 'pediatric']),
            'total_icu_beds': 45,
            'available_icu_beds': 12,
            'is_verified': True,
            'is_demo': False
        },

        # --- BENGALURU & KARNATAKA ---
        {
            'name': 'Narayana Institute of Cardiac Sciences',
            'address': '258/A, Bommasandra Industrial Area, Anekal Taluk',
            'city': 'Bengaluru',
            'latitude': 12.8055,
            'longitude': 77.6975,
            'phone': '+91 80 7122 2222',
            'emergency_contact': '+91 80 7122 2200',
            'trauma_level': 'Level 1 Cardiac Hub',
            'emergency_type': '24/7 World-Class Interventional Cardiology, Heart Transplant & Cath Lab',
            'specialties_json': json.dumps(['cardiac', 'general']),
            'total_icu_beds': 80,
            'available_icu_beds': 20,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Manipal Hospital HAL Airport Road',
            'address': '98, HAL Old Airport Rd, Kodihalli',
            'city': 'Bengaluru',
            'latitude': 12.9587,
            'longitude': 77.6483,
            'phone': '+91 80 2502 4444',
            'emergency_contact': '+91 80 2502 3333',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Comprehensive Stroke, Trauma, Pediatric & Acute Emergency Care',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 70,
            'available_icu_beds': 17,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Aster CMI Hospital Hebbal',
            'address': 'No. 43/42, National Highway 44, Sahakar Nagar',
            'city': 'Bengaluru',
            'latitude': 13.0560,
            'longitude': 77.5910,
            'phone': '+91 80 4344 4344',
            'emergency_contact': '+91 80 4344 4999',
            'trauma_level': 'Level 1 Multi-Specialty ER',
            'emergency_type': '24/7 Neuro-Trauma, Pediatric Critical Care & Cardiac ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'general']),
            'total_icu_beds': 50,
            'available_icu_beds': 13,
            'is_verified': True,
            'is_demo': False
        },

        # --- CHENNAI & TAMIL NADU ---
        {
            'name': 'Apollo Hospitals Main Greams Road',
            'address': '21, Greams Lane, Off Greams Road, Thousand Lights',
            'city': 'Chennai',
            'latitude': 13.0604,
            'longitude': 80.2496,
            'phone': '+91 44 2829 0200',
            'emergency_contact': '1066',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 National Emergency Hub, Advanced Stroke, Cath Lab & Heart ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'obstetric', 'pediatric', 'general']),
            'total_icu_beds': 75,
            'available_icu_beds': 19,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Christian Medical College (CMC) Hospital',
            'address': 'Ida Scudder Road, Vellore',
            'city': 'Vellore / Tamil Nadu',
            'latitude': 12.9250,
            'longitude': 79.1350,
            'phone': '+91 416 228 1000',
            'emergency_contact': '+91 416 228 2000',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Premier Emergency, Trauma Resuscitation, Child & Maternity ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 85,
            'available_icu_beds': 21,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'MIOT International Hospital',
            'address': '4/112, Mount Poonamallee Rd, Manapakkam',
            'city': 'Chennai',
            'latitude': 13.0235,
            'longitude': 80.1770,
            'phone': '+91 44 4200 2288',
            'emergency_contact': '+91 44 2249 2288',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Orthopedic Trauma, Surgery & Critical Resuscitation ER',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'general']),
            'total_icu_beds': 50,
            'available_icu_beds': 12,
            'is_verified': True,
            'is_demo': False
        },

        # --- HYDERABAD & TELANGANA ---
        {
            'name': 'Apollo Health City Jubilee Hills',
            'address': 'Road No. 72, Film Nagar, Jubilee Hills',
            'city': 'Hyderabad',
            'latitude': 17.4165,
            'longitude': 78.4115,
            'phone': '+91 40 2360 7777',
            'emergency_contact': '1066',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Comprehensive Emergency Room, Acute Stroke & Cardiac Cath Lab',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 65,
            'available_icu_beds': 15,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Yashoda Hospitals Secunderabad',
            'address': 'Alexander Road, Karkhana, Secunderabad',
            'city': 'Hyderabad',
            'latitude': 17.4399,
            'longitude': 78.4983,
            'phone': '+91 40 4567 4567',
            'emergency_contact': '+91 40 4567 1111',
            'trauma_level': 'Level 1 Stroke & Trauma Hub',
            'emergency_type': '24/7 Neuro-Trauma, Emergency Thrombolysis & Cardiac Care',
            'specialties_json': json.dumps(['stroke', 'cardiac', 'trauma', 'general']),
            'total_icu_beds': 55,
            'available_icu_beds': 14,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'NIMS (Nizam\'s Institute of Medical Sciences)',
            'address': 'Punjagutta, Hyderabad',
            'city': 'Hyderabad',
            'latitude': 17.4225,
            'longitude': 78.4525,
            'phone': '+91 40 2348 9000',
            'emergency_contact': '+91 40 2348 9200',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Government Apex Emergency Resuscitation & Specialized Trauma',
            'specialties_json': json.dumps(['trauma', 'stroke', 'cardiac', 'general']),
            'total_icu_beds': 50,
            'available_icu_beds': 11,
            'is_verified': True,
            'is_demo': False
        },

        # --- KOLKATA & WEST BENGAL ---
        {
            'name': 'Apollo Multispeciality Hospitals Kolkata',
            'address': '58, Canal Circular Road, Kadapara, Kankurgachi',
            'city': 'Kolkata',
            'latitude': 22.5695,
            'longitude': 88.3980,
            'phone': '+91 33 2320 3040',
            'emergency_contact': '1066',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Interventional Cardiology, Trauma Surgery & Critical Care ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general']),
            'total_icu_beds': 60,
            'available_icu_beds': 14,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'AMRI Hospitals Dhakuria',
            'address': 'P-4 & 5, CIT Scheme LXXII, Block A, Gariahat Rd, Dhakuria',
            'city': 'Kolkata',
            'latitude': 22.5110,
            'longitude': 88.3680,
            'phone': '+91 33 6680 0000',
            'emergency_contact': '+91 33 6680 0100',
            'trauma_level': 'Level 1 Stroke & Cardiac Hub',
            'emergency_type': '24/7 Stroke Unit, Emergency Angioplasty & Acute Care',
            'specialties_json': json.dumps(['cardiac', 'stroke', 'trauma', 'general']),
            'total_icu_beds': 45,
            'available_icu_beds': 10,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'SSKM Hospital & IPGMER Apex Trauma Centre',
            'address': '244, AJC Bose Road, Bhowanipore',
            'city': 'Kolkata',
            'latitude': 22.5400,
            'longitude': 88.3430,
            'phone': '+91 33 2223 1589',
            'emergency_contact': '+91 33 2223 1599',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Apex Emergency Surgery, Trauma & Multi-Disciplinary Resuscitation',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 75,
            'available_icu_beds': 17,
            'is_verified': True,
            'is_demo': False
        },

        # --- KERALA (KOCHI, TRIVANDRUM, KOZHIKODE, THRISSUR) ---
        {
            'name': 'Aster Medcity Kochi',
            'address': 'Kuttisahib Road, Near Kothad Bridge, South Chittoor',
            'city': 'Kochi / Kerala',
            'latitude': 10.0545,
            'longitude': 76.2655,
            'phone': '+91 484 669 9999',
            'emergency_contact': '+91 484 669 9000',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Comprehensive Trauma, Cardiac, Pediatric ICU & Stroke ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 60,
            'available_icu_beds': 16,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Amrita Institute of Medical Sciences (AIMS)',
            'address': 'AIMS Ponekkara P.O., Edappally',
            'city': 'Kochi / Kerala',
            'latitude': 10.0326,
            'longitude': 76.2905,
            'phone': '+91 484 285 1234',
            'emergency_contact': '+91 484 285 8000',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Super-Specialty Resuscitation, Cath Lab, PICU & Neuro-Trauma',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 75,
            'available_icu_beds': 19,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'VPS Lakeshore Hospital',
            'address': 'NH 66 Bypass, Nettoor, Maradu',
            'city': 'Kochi / Kerala',
            'latitude': 9.9235,
            'longitude': 76.3180,
            'phone': '+91 484 270 1011',
            'emergency_contact': '+91 484 270 1022',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Multi-Specialty Trauma, Stroke & Emergency Resuscitation',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general']),
            'total_icu_beds': 45,
            'available_icu_beds': 12,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Apex Heart & Interventional Cardiac Institute',
            'address': 'Civic Center Boulevard, East Wing',
            'city': 'Kochi / Kerala',
            'latitude': 9.9750,
            'longitude': 76.3250,
            'phone': '+91 484 260 4400',
            'emergency_contact': '+91 484 260 4499',
            'trauma_level': 'Level 1 Cardiac Hub',
            'emergency_type': '24/7 Interventional Cardiology, Cath Lab & CCU',
            'specialties_json': json.dumps(['cardiac', 'general']),
            'total_icu_beds': 28,
            'available_icu_beds': 7,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'City General Trauma Center & Multi-Specialty ER',
            'address': 'Medical College Road, Central Hub',
            'city': 'Kochi / Kerala',
            'latitude': 9.9925,
            'longitude': 76.3021,
            'phone': '+91 484 280 1100',
            'emergency_contact': '+91 484 280 1199',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Comprehensive Trauma, Cardiac, Neuro & Surgical ER',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 35,
            'available_icu_beds': 9,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Mother & Child Emergency Hospital & NICU',
            'address': 'Green Valley Road, Central Avenue',
            'city': 'Kochi / Kerala',
            'latitude': 9.9680,
            'longitude': 76.3080,
            'phone': '+91 484 288 7700',
            'emergency_contact': '+91 484 288 7799',
            'trauma_level': 'Level 2 Maternity/NICU',
            'emergency_type': '24/7 Labor, Emergency C-Section, NICU & Pediatric Care',
            'specialties_json': json.dumps(['obstetric', 'pediatric', 'general']),
            'total_icu_beds': 24,
            'available_icu_beds': 8,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Government Medical College Hospital Trivandrum',
            'address': 'Medical College PO, Ulloor',
            'city': 'Trivandrum / Kerala',
            'latitude': 8.5241,
            'longitude': 76.9295,
            'phone': '+91 471 252 8300',
            'emergency_contact': '+91 471 252 8000',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 State Apex Trauma, Resuscitation & Multi-Specialty ER',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 70,
            'available_icu_beds': 15,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'KIMSHEALTH Trivandrum',
            'address': 'PB No.1, Anayara P.O.',
            'city': 'Trivandrum / Kerala',
            'latitude': 8.5080,
            'longitude': 76.9080,
            'phone': '+91 471 304 1000',
            'emergency_contact': '+91 471 304 1234',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Advanced Trauma, Interventional Cardiology & Stroke Unit',
            'specialties_json': json.dumps(['cardiac', 'stroke', 'trauma', 'general', 'pediatric']),
            'total_icu_beds': 50,
            'available_icu_beds': 12,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Baby Memorial Hospital Kozhikode',
            'address': 'Indira Gandhi Road, Arayidathupalam',
            'city': 'Kozhikode / Calicut',
            'latitude': 11.2615,
            'longitude': 75.7925,
            'phone': '+91 495 277 7777',
            'emergency_contact': '+91 495 272 3272',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Neuro-Trauma, Emergency Medicine & Cardiac Cath Lab',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general']),
            'total_icu_beds': 45,
            'available_icu_beds': 11,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Jubilee Mission Medical College & Hospital',
            'address': 'Bishop Alapatt Road, East Fort',
            'city': 'Thrissur / Kerala',
            'latitude': 10.5215,
            'longitude': 76.2285,
            'phone': '+91 487 243 2200',
            'emergency_contact': '+91 487 243 2345',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Burns & Trauma Emergency Center, Multi-Specialty Care',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'general', 'pediatric']),
            'total_icu_beds': 40,
            'available_icu_beds': 10,
            'is_verified': True,
            'is_demo': False
        },

        # --- NORTH, CENTRAL & WEST INDIA ---
        {
            'name': 'PGIMER (Post Graduate Institute of Medical Education & Research)',
            'address': 'Madhya Marg, Sector 12',
            'city': 'Chandigarh',
            'latitude': 30.7635,
            'longitude': 76.7760,
            'phone': '+91 172 274 7585',
            'emergency_contact': '+91 172 275 6565',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Regional Apex Trauma, Stroke, Critical Care & Multi-Specialty ER',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 80,
            'available_icu_beds': 18,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Sawai Man Singh (SMS) Medical College & Hospital',
            'address': 'JLN Marg, Ashok Nagar',
            'city': 'Jaipur / Rajasthan',
            'latitude': 26.8985,
            'longitude': 75.8150,
            'phone': '+91 141 251 8222',
            'emergency_contact': '+91 141 251 8333',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 State Apex Trauma, Resuscitation & Emergency Surgery',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 70,
            'available_icu_beds': 16,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'King George\'s Medical University (KGMU)',
            'address': 'Shah Mina Road, Chowk',
            'city': 'Lucknow / Uttar Pradesh',
            'latitude': 26.8685,
            'longitude': 80.9150,
            'phone': '+91 522 225 7450',
            'emergency_contact': '+91 522 225 7540',
            'trauma_level': 'Level 1 Apex Trauma Center',
            'emergency_type': '24/7 Apex Trauma Center, Critical Care & Emergency Medicine',
            'specialties_json': json.dumps(['trauma', 'cardiac', 'stroke', 'pediatric', 'obstetric', 'general']),
            'total_icu_beds': 75,
            'available_icu_beds': 17,
            'is_verified': True,
            'is_demo': False
        },
        {
            'name': 'Apollo Hospitals Ahmedabad',
            'address': 'Plot No. 1A, Bhat, GIDC Estate, Gandhinagar Highway',
            'city': 'Ahmedabad / Gujarat',
            'latitude': 23.1115,
            'longitude': 72.6320,
            'phone': '+91 79 6670 1800',
            'emergency_contact': '1066',
            'trauma_level': 'Level 1 Trauma Center',
            'emergency_type': '24/7 Comprehensive Emergency Medicine, Cath Lab & Trauma Surgery',
            'specialties_json': json.dumps(['cardiac', 'trauma', 'stroke', 'general']),
            'total_icu_beds': 55,
            'available_icu_beds': 14,
            'is_verified': True,
            'is_demo': False
        }
    ]

    created_hospitals = []
    for h_data in pan_india_hospitals:
        h = Hospital.query.filter_by(name=h_data['name']).first()
        if not h:
            h = Hospital(**h_data)
            db.session.add(h)
            db.session.flush()
        else:
            h.city = h_data['city']
            h.address = h_data['address']
            h.latitude = h_data['latitude']
            h.longitude = h_data['longitude']
            h.phone = h_data['phone']
            h.emergency_contact = h_data['emergency_contact']
            h.trauma_level = h_data['trauma_level']
            h.emergency_type = h_data['emergency_type']
            h.specialties_json = h_data['specialties_json']
            h.total_icu_beds = h_data['total_icu_beds']
            h.available_icu_beds = h_data['available_icu_beds']
        created_hospitals.append(h)
    db.session.commit()

    primary_hospital = created_hospitals[0]

    # 3. Demonstration Users
    demo_users_data = [
        {
            'name': 'Alex Mercer (Driver / Vehicle Owner)',
            'email': 'driver@emergency.org',
            'password': 'DemoUser123!',
            'phone': '+91 98470 12345',
            'role_id': roles['user'].id,
            'is_demo_account': True,
            'hospital_id': None,
            'badge_number': None,
            'department': 'Public Citizen'
        },
        {
            'name': 'Dr. Sarah Chen, MD (Emergency Triage Desk)',
            'email': 'hospital@emergency.org',
            'password': 'DemoHospital123!',
            'phone': '+91 98470 54321',
            'role_id': roles['hospital'].id,
            'is_demo_account': True,
            'hospital_id': primary_hospital.id,
            'badge_number': 'MD-ER-402',
            'department': 'Emergency Department'
        },
        {
            'name': 'Officer David Miller (Tactical Traffic Command)',
            'email': 'police@emergency.org',
            'password': 'DemoPolice123!',
            'phone': '+91 98470 99887',
            'role_id': roles['police'].id,
            'is_demo_account': True,
            'hospital_id': None,
            'badge_number': 'EP-TAC-902',
            'department': 'City Emergency Traffic Unit'
        },
        {
            'name': 'Administrator (EmergencyPass Supervisor)',
            'email': 'admin@emergency.org',
            'password': 'DemoAdmin123!',
            'phone': '+91 98470 00001',
            'role_id': roles['admin'].id,
            'is_demo_account': True,
            'hospital_id': None,
            'badge_number': 'EP-ADM-001',
            'department': 'Central Operations'
        }
    ]

    users = {}
    for u_data in demo_users_data:
        u = User.query.filter_by(email=u_data['email']).first()
        if not u:
            u = User(
                name=u_data['name'],
                email=u_data['email'],
                phone=u_data['phone'],
                role_id=u_data['role_id'],
                is_demo_account=u_data['is_demo_account'],
                hospital_id=u_data['hospital_id'],
                badge_number=u_data['badge_number'],
                department=u_data['department'],
                is_active=True
            )
            u.set_password(u_data['password'])
            db.session.add(u)
            db.session.flush()
        users[u_data['email']] = u
    db.session.commit()

    # 4. Registered Sample Vehicles for Demo User
    driver_user = users['driver@emergency.org']
    admin_user = users['admin@emergency.org']
    
    vehicles_data = [
        {
            'registration_number': 'KL-07-CC-4099',
            'vehicle_type': 'SUV',
            'make_model': 'Toyota Innova Crysta (2.4 VX)',
            'color': 'Pearl White',
            'is_verified': True,
            'verification_status': 'approved',
            'notes': 'Equipped with basic first-aid kit and dash hazard lights.'
        },
        {
            'registration_number': 'DL-01-AX-9921',
            'vehicle_type': 'Car',
            'make_model': 'Hyundai Creta (1.5 SX)',
            'color': 'Titan Grey',
            'is_verified': True,
            'verification_status': 'approved',
            'notes': 'Family commuter vehicle with emergency pass.'
        }
    ]

    for v_data in vehicles_data:
        v = Vehicle.query.filter_by(registration_number=v_data['registration_number']).first()
        if not v:
            v = Vehicle(
                user_id=driver_user.id,
                registration_number=v_data['registration_number'],
                vehicle_type=v_data['vehicle_type'],
                make_model=v_data['make_model'],
                color=v_data['color'],
                is_verified=v_data['is_verified'],
                verification_status=v_data['verification_status'],
                notes=v_data['notes']
            )
            db.session.add(v)
            db.session.flush()
            
            ver = VehicleVerification(
                vehicle_id=v.id,
                verified_by_id=admin_user.id,
                status='approved',
                document_reference='RC-DOC-2026-IND',
                reviewer_comments='Official registration and insurance verified by administrative audit.'
            )
            db.session.add(ver)
    db.session.commit()

    # 5. Add initial audit log
    if AuditLog.query.count() == 0:
        log = AuditLog(
            user_id=admin_user.id,
            action='SYSTEM_INITIALIZED',
            target_type='system',
            target_id='core',
            ip_address='127.0.0.1',
            user_agent='EmergencyPass System Seed Daemon',
            details_json='{"status": "initialized", "region": "Pan-India"}'
        )
        db.session.add(log)
        db.session.commit()

    print(f"Pan-India database seeded with {len(pan_india_hospitals)} premier & regional emergency centers.")
