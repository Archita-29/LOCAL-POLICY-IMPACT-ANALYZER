import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.models import Scheme, Region, SchemeRegionMapping, Mention, ImpactScore

def create_square_polygon(lat, lon, size=0.1):
    # Returns a WKT multipolygon roughly around the given lat, lon
    return f"MULTIPOLYGON((({lon} {lat}, {lon+size} {lat}, {lon+size} {lat+size}, {lon} {lat+size}, {lon} {lat})))"

def seed_india():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    try:
        # Check if we have more than a few schemes (if we already ran this)
        if db.query(Scheme).count() > 5:
            print("Database already has country-wide data. Skipping seeding.")
            return

        states_data = [
            {"state": "Andhra Pradesh", "capital": "Amaravati", "lat": 16.5062, "lon": 80.6480, "pop": 49386799,
             "schemes": [{"name": "YSR Rythu Bharosa", "cat": "Agriculture", "auth": "Dept of Agriculture", "desc": "Financial assistance to farmers."}]},
            {"state": "Arunachal Pradesh", "capital": "Itanagar", "lat": 27.0844, "lon": 93.6053, "pop": 1383727,
             "schemes": [{"name": "CMAAY", "cat": "Health", "auth": "Dept of Health", "desc": "Chief Minister's Arogya Arunachal Yojana for cashless healthcare."}]},
            {"state": "Assam", "capital": "Dispur", "lat": 26.1433, "lon": 91.7898, "pop": 31205576,
             "schemes": [{"name": "Orunodoi Scheme", "cat": "Welfare", "auth": "Finance Dept", "desc": "Monthly financial assistance to vulnerable families."}]},
            {"state": "Bihar", "capital": "Patna", "lat": 25.5941, "lon": 85.1376, "pop": 104099452,
             "schemes": [{"name": "Mukhyamantri Kanya Utthan Yojana", "cat": "Education", "auth": "Social Welfare Dept", "desc": "Promotes girls' education and tackles female foeticide."}]},
            {"state": "Chhattisgarh", "capital": "Raipur", "lat": 21.2514, "lon": 81.6296, "pop": 25545198,
             "schemes": [{"name": "Rajiv Gandhi Kisan Nyay Yojana", "cat": "Agriculture", "auth": "Dept of Agriculture", "desc": "Income support for farmers."}]},
            {"state": "Goa", "capital": "Panaji", "lat": 15.4909, "lon": 73.8278, "pop": 1458545,
             "schemes": [{"name": "Dayanand Social Security Scheme", "cat": "Welfare", "auth": "Directorate of Social Welfare", "desc": "Financial assistance to senior citizens and disabled."}]},
            {"state": "Gujarat", "capital": "Gandhinagar", "lat": 23.2156, "lon": 72.6369, "pop": 60439692,
             "schemes": [{"name": "Mukhyamantri Amrutam Yojana", "cat": "Health", "auth": "Health Dept", "desc": "Tertiary care for BPL families."}]},
            {"state": "Haryana", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "pop": 25351462,
             "schemes": [{"name": "Parivar Pehchan Patra", "cat": "Governance", "auth": "Haryana Govt", "desc": "Unique identity for families for scheme delivery."}]},
            {"state": "Himachal Pradesh", "capital": "Shimla", "lat": 31.1048, "lon": 77.1734, "pop": 6864602,
             "schemes": [{"name": "Himcare Scheme", "cat": "Health", "auth": "Dept of Health", "desc": "Cashless treatment for those not under Ayushman Bharat."}]},
            {"state": "Jharkhand", "capital": "Ranchi", "lat": 23.3441, "lon": 85.3096, "pop": 32988134,
             "schemes": [{"name": "Mukhyamantri Krishi Ashirwad Yojana", "cat": "Agriculture", "auth": "Agriculture Dept", "desc": "Financial support to farmers based on land holding."}]},
            {"state": "Karnataka", "capital": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "pop": 61095297,
             "schemes": [{"name": "Gruha Lakshmi Scheme", "cat": "Welfare", "auth": "Women and Child Dev", "desc": "Rs 2000 per month to female head of the family."}]},
            {"state": "Kerala", "capital": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366, "pop": 33406061,
             "schemes": [{"name": "LIFE Mission", "cat": "Housing", "auth": "Local Self Government", "desc": "Comprehensive housing scheme for the landless and homeless."}]},
            {"state": "Madhya Pradesh", "capital": "Bhopal", "lat": 23.2599, "lon": 77.4126, "pop": 72626809,
             "schemes": [{"name": "Ladli Behna Yojana", "cat": "Welfare", "auth": "Women & Child Dev", "desc": "Financial assistance to women for empowerment."}]},
            {"state": "Maharashtra", "capital": "Mumbai", "lat": 18.9690, "lon": 72.8205, "pop": 112374333,
             "schemes": [{"name": "Mukhyamantri Majhi Ladki Bahin Yojana", "cat": "Welfare", "auth": "Women & Child Dev", "desc": "Financial assistance to women."}]},
            {"state": "Manipur", "capital": "Imphal", "lat": 24.8170, "lon": 93.9368, "pop": 2855794,
             "schemes": [{"name": "Chief Minister-gi Hakshelgi Tengbang", "cat": "Health", "auth": "Health Dept", "desc": "Health assurance scheme for poor."}]},
            {"state": "Meghalaya", "capital": "Shillong", "lat": 25.5788, "lon": 91.8933, "pop": 2966889,
             "schemes": [{"name": "FOCUS Scheme", "cat": "Agriculture", "auth": "Agriculture Dept", "desc": "Financial assistance to producer groups."}]},
            {"state": "Mizoram", "capital": "Aizawl", "lat": 23.7271, "lon": 92.7176, "pop": 1097206,
             "schemes": [{"name": "SEDP", "cat": "Development", "auth": "Planning Dept", "desc": "Socio-Economic Development Policy."}]},
            {"state": "Nagaland", "capital": "Kohima", "lat": 25.6751, "lon": 94.1086, "pop": 1978502,
             "schemes": [{"name": "Chief Minister's Micro Finance Initiative", "cat": "Finance", "auth": "Finance Dept", "desc": "Credit support to entrepreneurs."}]},
            {"state": "Odisha", "capital": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "pop": 41974218,
             "schemes": [{"name": "KALIA Scheme", "cat": "Agriculture", "auth": "Agriculture Dept", "desc": "Krushak Assistance for Livelihood and Income Augmentation."}]},
            {"state": "Punjab", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "pop": 27743338,
             "schemes": [{"name": "Aam Aadmi Clinics", "cat": "Health", "auth": "Health Dept", "desc": "Free primary healthcare clinics."}]},
            {"state": "Rajasthan", "capital": "Jaipur", "lat": 26.9124, "lon": 75.7873, "pop": 68548437,
             "schemes": [{"name": "Chiranjeevi Swasthya Bima Yojana", "cat": "Health", "auth": "Health Dept", "desc": "Universal health insurance scheme."}]},
            {"state": "Sikkim", "capital": "Gangtok", "lat": 27.3389, "lon": 88.6065, "pop": 610577,
             "schemes": [{"name": "Sikkim Garib Awas Yojana", "cat": "Housing", "auth": "Rural Dev", "desc": "Housing for poor families."}]},
            {"state": "Tamil Nadu", "capital": "Chennai", "lat": 13.0827, "lon": 80.2707, "pop": 72147030,
             "schemes": [{"name": "Kalaignar Magalir Urimai Thittam", "cat": "Welfare", "auth": "Social Welfare", "desc": "Basic income scheme for women heads of families."}]},
            {"state": "Telangana", "capital": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "pop": 35003674,
             "schemes": [{"name": "Rythu Bandhu", "cat": "Agriculture", "auth": "Agriculture Dept", "desc": "Investment support scheme for farmers."}]},
            {"state": "Tripura", "capital": "Agartala", "lat": 23.8315, "lon": 91.2868, "pop": 3673917,
             "schemes": [{"name": "Mukhyamantri Cha Sramik Kalyan Prakalpa", "cat": "Welfare", "auth": "Labour Dept", "desc": "Welfare scheme for tea garden workers."}]},
            {"state": "Uttar Pradesh", "capital": "Lucknow", "lat": 26.8467, "lon": 80.9462, "pop": 199812341,
             "schemes": [{"name": "Mukhyamantri Kanya Sumangala Yojana", "cat": "Education", "auth": "Women & Child Dev", "desc": "Financial support for girls."}]},
            {"state": "Uttarakhand", "capital": "Dehradun", "lat": 30.3165, "lon": 78.0322, "pop": 10086292,
             "schemes": [{"name": "Mukhyamantri Swasthya Bima Yojana", "cat": "Health", "auth": "Health Dept", "desc": "Health insurance scheme."}]},
            {"state": "West Bengal", "capital": "Kolkata", "lat": 22.5726, "lon": 88.3639, "pop": 91276115,
             "schemes": [{"name": "Lakshmir Bhandar", "cat": "Welfare", "auth": "Women & Child Dev", "desc": "Financial assistance to female heads of households."}]},
            # Union Territories
            {"state": "Andaman and Nicobar Islands", "capital": "Port Blair", "lat": 11.6234, "lon": 92.7265, "pop": 380581,
             "schemes": [{"name": "ANISHI Scheme", "cat": "Health", "auth": "UT Admin", "desc": "Health insurance for islanders."}]},
            {"state": "Chandigarh", "capital": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "pop": 1055450,
             "schemes": [{"name": "Apni Beti Apna Dhan", "cat": "Welfare", "auth": "Social Welfare", "desc": "Financial assistance for girl child."}]},
            {"state": "Dadra and Nagar Haveli and Daman and Diu", "capital": "Daman", "lat": 20.3974, "lon": 72.8328, "pop": 586956,
             "schemes": [{"name": "Saraswati Vidya Yojana", "cat": "Education", "auth": "Education Dept", "desc": "Free education support."}]},
            {"state": "Delhi", "capital": "New Delhi", "lat": 28.6139, "lon": 77.2090, "pop": 16787941,
             "schemes": [{"name": "Farishte Dilli Ke", "cat": "Health", "auth": "Health Dept", "desc": "Free treatment for accident victims."}]},
            {"state": "Jammu and Kashmir", "capital": "Srinagar", "lat": 34.0837, "lon": 74.7973, "pop": 12267013,
             "schemes": [{"name": "SEHAT Scheme", "cat": "Health", "auth": "Health Dept", "desc": "Universal health coverage for J&K."}]},
            {"state": "Ladakh", "capital": "Leh", "lat": 34.1526, "lon": 77.5771, "pop": 274289,
             "schemes": [{"name": "Rewa Scheme", "cat": "Education", "auth": "Education Dept", "desc": "Financial assistance for coaching."}]},
            {"state": "Lakshadweep", "capital": "Kavaratti", "lat": 10.5667, "lon": 72.6417, "pop": 64473,
             "schemes": [{"name": "Lakshadweep Scholarship", "cat": "Education", "auth": "Education Dept", "desc": "Scholarship for higher education."}]},
            {"state": "Puducherry", "capital": "Puducherry", "lat": 11.9416, "lon": 79.8083, "pop": 1247953,
             "schemes": [{"name": "Perunthalaivar Kamarajar Scheme", "cat": "Education", "auth": "Education Dept", "desc": "Financial assistance to students."}]}
        ]

        new_regions = []
        new_schemes = []
        region_map = {}
        scheme_map = {}
        
        # Insert Regions and Schemes
        for item in states_data:
            state = item["state"]
            capital = item["capital"]
            
            # Create Region (Capital District)
            reg = Region(
                state=state,
                district=capital,
                geo_boundary=create_square_polygon(item["lat"], item["lon"]),
                population=item["pop"],
                demographic_stats={"literacy_rate": 80.0, "sex_ratio": 950, "urban_ratio": 50.0, "nfhs5_stunting_rate": 30.0}
            )
            db.add(reg)
            db.flush() # get id
            region_map[state] = reg
            
            # Create Schemes
            for sch in item["schemes"]:
                s = Scheme(
                    name=sch["name"],
                    launching_authority=f"{sch['auth']}, {state}",
                    category=sch["cat"],
                    launch_date=datetime.date(2020, 1, 1),
                    target_beneficiaries="Citizens of " + state,
                    budget_allocated=Decimal(item["pop"] * 10), # dummy budget
                    description=sch["desc"],
                    source_url=f"https://{state.replace(' ','').lower()}.gov.in"
                )
                db.add(s)
                db.flush()
                scheme_map[s.name] = s
                
                # Create Mapping
                mapping = SchemeRegionMapping(
                    scheme_id=s.id,
                    region_id=reg.id,
                    beneficiaries_reached=int(item["pop"] * 0.05),
                    budget_utilized=Decimal(item["pop"] * 8)
                )
                db.add(mapping)
                
                # Add Mentions
                m1 = Mention(
                    scheme_id=s.id,
                    source="News Portal",
                    raw_text=f"The {s.name} in {state} is showing great progress this year.",
                    language="en",
                    sentiment_score=Decimal("0.8"),
                    sentiment_label="Positive"
                )
                m2 = Mention(
                    scheme_id=s.id,
                    source="Twitter",
                    raw_text=f"Still waiting for benefits from {s.name}. Administration in {state} is slow.",
                    language="en",
                    sentiment_score=Decimal("-0.6"),
                    sentiment_label="Negative"
                )
                db.add_all([m1, m2])
                
                # Add Impact Score
                impact = ImpactScore(
                    scheme_id=s.id,
                    region_id=reg.id,
                    score=Decimal("75.50"),
                    reach_component=Decimal("70.00"),
                    sentiment_component=Decimal("60.00"),
                    adoption_component=Decimal("80.00"),
                    shap_explanations={
                        "features": {"reach_ratio": 0.7, "budget_utilization_ratio": 0.8, "average_sentiment": 0.1},
                        "base_value": 50.0,
                        "contributions": {"reach_ratio": 15.0, "budget_utilization_ratio": 10.0, "average_sentiment": 0.5}
                    },
                    model_version="v0_heuristic"
                )
                db.add(impact)

        db.commit()
        print("All states and UTs seeded successfully with genuine schemes.")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_india()
