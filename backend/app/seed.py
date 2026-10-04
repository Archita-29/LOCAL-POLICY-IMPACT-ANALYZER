import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, Base, engine
from app.models.models import Scheme, Region, SchemeRegionMapping, Mention, ImpactScore

def seed_db():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables verified/created.")

    db: Session = SessionLocal()

    try:
        # Check if we already have data to prevent double seeding
        if db.query(Scheme).first() is not None:
            print("Database already has data. Skipping seeding.")
            return

        # 1. Seed Schemes
        schemes = [
            Scheme(
                name="Sanjay Gandhi Niradhar Anudan Yojana",
                launching_authority="Department of Social Justice and Special Assistance, Maharashtra",
                category="Social Welfare & Pension",
                launch_date=datetime.date(1980, 10, 2),
                target_beneficiaries="Destitute individuals, elderly, disabled, widows, orphans",
                budget_allocated=Decimal("250000000.00"),
                description="Provides a monthly financial assistance of Rs. 1000 to individuals who are destitute, elderly, disabled, or widows without any active source of income.",
                source_url="https://sjsa.maharashtra.gov.in"
            ),
            Scheme(
                name="MahaDBT Post-Matric Scholarship",
                launching_authority="Directorate of Higher Education, Maharashtra",
                category="Education & Scholarship",
                launch_date=datetime.date(2018, 8, 1),
                target_beneficiaries="Students belonging to reserved categories (SC/ST/OBC) and low-income families",
                budget_allocated=Decimal("1500000000.00"),
                description="Reimburses tuition fees, exam fees, and maintenance allowance directly to the bank accounts of students pursuing higher education.",
                source_url="https://mahadbt.maharashtra.gov.in"
            )
        ]
        db.add_all(schemes)
        db.commit()
        print("Schemes seeded successfully.")

        # 2. Seed Regions (Districts in Maharashtra)
        # We store geo_boundary as WKT (Well-Known Text) representing simplified district boundaries
        regions = [
            Region(
                state="Maharashtra",
                district="Pune",
                geo_boundary="MULTIPOLYGON(((73.7 18.4, 74.0 18.4, 74.0 18.7, 73.7 18.7, 73.7 18.4)))",
                population=9429408,
                demographic_stats={
                    "literacy_rate": 86.1,
                    "sex_ratio": 915,
                    "urban_ratio": 61.0,
                    "nfhs5_stunting_rate": 28.5
                }
            ),
            Region(
                state="Maharashtra",
                district="Mumbai",
                geo_boundary="MULTIPOLYGON(((72.7 18.9, 72.9 18.9, 72.9 19.2, 72.7 19.2, 72.7 18.9)))",
                population=12442373,
                demographic_stats={
                    "literacy_rate": 89.2,
                    "sex_ratio": 838,
                    "urban_ratio": 100.0,
                    "nfhs5_stunting_rate": 25.1
                }
            ),
            Region(
                state="Maharashtra",
                district="Nagpur",
                geo_boundary="MULTIPOLYGON(((78.9 21.0, 79.2 21.0, 79.2 21.3, 78.9 21.3, 78.9 21.0)))",
                population=4653570,
                demographic_stats={
                    "literacy_rate": 88.4,
                    "sex_ratio": 951,
                    "urban_ratio": 68.3,
                    "nfhs5_stunting_rate": 31.2
                }
            )
        ]
        db.add_all(regions)
        db.commit()
        print("Regions/Districts seeded successfully.")

        # Refresh objects to get generated IDs
        scheme_sanjay = db.query(Scheme).filter_by(name="Sanjay Gandhi Niradhar Anudan Yojana").first()
        scheme_mahadbt = db.query(Scheme).filter_by(name="MahaDBT Post-Matric Scholarship").first()

        region_pune = db.query(Region).filter_by(district="Pune").first()
        region_mumbai = db.query(Region).filter_by(district="Mumbai").first()
        region_nagpur = db.query(Region).filter_by(district="Nagpur").first()

        # 3. Seed Mappings
        mappings = [
            # Sanjay Gandhi Yojana mapping
            SchemeRegionMapping(
                scheme_id=scheme_sanjay.id,
                region_id=region_pune.id,
                beneficiaries_reached=45000,
                budget_utilized=Decimal("45000000.00")  # target approx 50000
            ),
            SchemeRegionMapping(
                scheme_id=scheme_sanjay.id,
                region_id=region_mumbai.id,
                beneficiaries_reached=32000,
                budget_utilized=Decimal("32000000.00")  # target approx 40000
            ),
            SchemeRegionMapping(
                scheme_id=scheme_sanjay.id,
                region_id=region_nagpur.id,
                beneficiaries_reached=28000,
                budget_utilized=Decimal("28000000.00")  # target approx 30000
            ),
            # MahaDBT mapping
            SchemeRegionMapping(
                scheme_id=scheme_mahadbt.id,
                region_id=region_pune.id,
                beneficiaries_reached=120000,
                budget_utilized=Decimal("360000000.00")
            ),
            SchemeRegionMapping(
                scheme_id=scheme_mahadbt.id,
                region_id=region_mumbai.id,
                beneficiaries_reached=85000,
                budget_utilized=Decimal("255000000.00")
            ),
            SchemeRegionMapping(
                scheme_id=scheme_mahadbt.id,
                region_id=region_nagpur.id,
                beneficiaries_reached=75000,
                budget_utilized=Decimal("225000000.00")
            )
        ]
        db.add_all(mappings)
        db.commit()
        print("Scheme-Region Mappings seeded successfully.")

        # 4. Seed Mentions (with simulated sentiment and labels)
        mentions = [
            # Sanjay Gandhi Scheme Mentions
            Mention(
                scheme_id=scheme_sanjay.id,
                source="Dainik Jagran",
                raw_text="संजय गांधी निराधार योजना के लाभार्थियों को पिछले तीन महीनों से पेंशन नहीं मिली है। पेंशनभोगी काफी संकट में हैं।",
                language="hi",
                sentiment_score=Decimal("-0.8500"),
                sentiment_label="Negative",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=5),
                url="https://www.jagran.com/maharashtra/pune-welfare-delay"
            ),
            Mention(
                scheme_id=scheme_sanjay.id,
                source="Twitter",
                raw_text="Sanjay Gandhi Niradhar pension ke 1000 rupees me aajkal kya hota hai? Pls increase it to 2000. Price rise is too high.",
                language="hi-en",
                sentiment_score=Decimal("-0.6000"),
                sentiment_label="Negative",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=2),
                url="https://twitter.com/user/status/123"
            ),
            Mention(
                scheme_id=scheme_sanjay.id,
                source="Loksatta",
                raw_text="पुणे जिल्हा प्रशासनाने संजय गांधी निराधार योजनेअंतर्गत ३००० नवीन लाभार्थ्यांना मंजुरी दिली. आता त्यांना नियमित पेन्शन मिळणार.",
                language="hi",  # Loksatta is Marathi, but let's label as Hindi for simulator or IndicBERT
                sentiment_score=Decimal("0.7500"),
                sentiment_label="Positive",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                url="https://www.loksatta.com/pune/sanjay-gandhi-yojana-new-approvals"
            ),
            Mention(
                scheme_id=scheme_sanjay.id,
                source="Reddit",
                raw_text="My grandmother gets Sanjay Gandhi Niradhar pension. Even though the amount is small (1k/month), it helps her with her basic medicines. Distribution has been regular in Nagpur.",
                language="en",
                sentiment_score=Decimal("0.6500"),
                sentiment_label="Positive",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=4),
                url="https://reddit.com/r/nagpur/sanjay-gandhi-pension"
            ),
            # MahaDBT Scheme Mentions
            Mention(
                scheme_id=scheme_mahadbt.id,
                source="Twitter",
                raw_text="MahaDBT scholarship received today! Account credit ho gaya. Thanks Maharashtra gov for timely transfer this year.",
                language="hi-en",
                sentiment_score=Decimal("0.9000"),
                sentiment_label="Positive",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                url="https://twitter.com/student/status/456"
            ),
            Mention(
                scheme_id=scheme_mahadbt.id,
                source="Dainik Bhaskar",
                raw_text="महाडीबीटी स्कॉलरशिप पोर्टल पर सर्वर डाउन होने से छात्र परेशान हैं। आवेदन करने की अंतिम तिथि बढ़ाने की मांग की जा रही है।",
                language="hi",
                sentiment_score=Decimal("-0.7000"),
                sentiment_label="Negative",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                url="https://www.bhaskar.com/education/mahadbt-server-down"
            ),
            Mention(
                scheme_id=scheme_mahadbt.id,
                source="Reddit",
                raw_text="Is anyone else facing verification pending status at department level in MahaDBT for post-matric OBC scholarship? It's pending for 2 months.",
                language="hi-en",
                sentiment_score=Decimal("-0.4000"),
                sentiment_label="Negative",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=6),
                url="https://reddit.com/r/maharashtra/mahadbt-pending"
            ),
            Mention(
                scheme_id=scheme_mahadbt.id,
                source="Maharashtra Times",
                raw_text="महाडीबीटी पोर्टलच्या माध्यमातून लाखो विद्यार्थ्यांना थेट बँक खात्यात शिष्यवृत्ती जमा झाली आहे. यामुळे पारदर्शकता वाढली आहे.",
                language="hi",
                sentiment_score=Decimal("0.8500"),
                sentiment_label="Positive",
                published_date=datetime.datetime.utcnow() - datetime.timedelta(days=2),
                url="https://maharashtratimes.com/education/mahadbt-scholarship-direct-benefit-transfer"
            )
        ]
        db.add_all(mentions)
        db.commit()
        print("Mentions seeded successfully.")

        # 5. Compute and seed initial heuristic Impact Scores (Phase 2 format)
        # target_beneficiaries targets:
        # Sanjay Gandhi: 50,000 for Pune, 40,000 for Mumbai, 30,000 for Nagpur
        # MahaDBT: 130,000 for Pune, 90,000 for Mumbai, 80,000 for Nagpur
        targets = {
            (scheme_sanjay.id, region_pune.id): 50000,
            (scheme_sanjay.id, region_mumbai.id): 40000,
            (scheme_sanjay.id, region_nagpur.id): 30000,
            (scheme_mahadbt.id, region_pune.id): 130000,
            (scheme_mahadbt.id, region_mumbai.id): 90000,
            (scheme_mahadbt.id, region_nagpur.id): 80000,
        }

        # Budget allocations (pro-rated by district population ratio for calculation)
        # Pune: 9.4M, Mumbai: 12.4M, Nagpur: 4.6M. Total state pop: 26.4M.
        # Ratios: Pune: 0.35, Mumbai: 0.47, Nagpur: 0.18
        pop_ratios = {
            region_pune.id: Decimal("0.35"),
            region_mumbai.id: Decimal("0.47"),
            region_nagpur.id: Decimal("0.18"),
        }

        for mapping in db.query(SchemeRegionMapping).all():
            target_ben = targets[(mapping.scheme_id, mapping.region_id)]
            reach_ratio = float(mapping.beneficiaries_reached) / target_ben
            
            # Budget allocated to district
            total_budget = db.query(Scheme).get(mapping.scheme_id).budget_allocated
            district_budget_allocated = total_budget * pop_ratios[mapping.region_id]
            budget_ratio = float(mapping.budget_utilized) / float(district_budget_allocated)
            
            # Average sentiment score for this scheme
            avg_sentiment_res = db.query(Mention).filter_by(scheme_id=mapping.scheme_id).all()
            avg_sent = 0.0
            if avg_sentiment_res:
                avg_sent = sum([float(m.sentiment_score or 0) for m in avg_sentiment_res]) / len(avg_sentiment_res)
            
            # Normalize sentiment from [-1, 1] to [0, 1]
            sentiment_norm = (avg_sent + 1.0) / 2.0

            # Cap ratios at 1.0 to avoid scores > 100
            reach_ratio = min(reach_ratio, 1.0)
            budget_ratio = min(budget_ratio, 1.0)

            # Heuristic weights
            w_reach = 0.4
            w_budget = 0.3
            w_sentiment = 0.3

            score = 100.0 * (
                w_reach * reach_ratio +
                w_budget * budget_ratio +
                w_sentiment * sentiment_norm
            )

            # Create mock SHAP explanations based on the inputs
            shap_ex = {
                "features": {
                    "reach_ratio": round(reach_ratio, 3),
                    "budget_utilization_ratio": round(budget_ratio, 3),
                    "average_sentiment": round(avg_sent, 3)
                },
                "base_value": 50.00,
                "contributions": {
                    "reach_ratio": round((reach_ratio - 0.5) * w_reach * 100, 2),
                    "budget_utilization_ratio": round((budget_ratio - 0.5) * w_budget * 100, 2),
                    "average_sentiment": round((sentiment_norm - 0.5) * w_sentiment * 100, 2)
                }
            }

            impact_score = ImpactScore(
                scheme_id=mapping.scheme_id,
                region_id=mapping.region_id,
                score=Decimal(f"{score:.2f}"),
                reach_component=Decimal(f"{reach_ratio * 100:.2f}"),
                sentiment_component=Decimal(f"{sentiment_norm * 100:.2f}"),
                adoption_component=Decimal(f"{budget_ratio * 100:.2f}"),
                shap_explanations=shap_ex,
                computed_at=datetime.datetime.utcnow(),
                model_version="v0_heuristic"
            )
            db.add(impact_score)

        db.commit()
        print("Heuristic Impact Scores seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
