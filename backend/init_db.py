"""
Database initialization script
Creates tables and seeds initial data for development
"""

from app.database import engine, Base, SessionLocal
from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.models.material import Material, Sample
from datetime import datetime


def init_db():
    """Initialize database with tables and seed data"""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_hcp = db.query(HCP).first()
        if existing_hcp:
            print("Database already contains data. Skipping seed data.")
            return
        
        # Seed HCPs
        print("Seeding HCP data...")
        hcps = [
            HCP(
                name="Dr. Smith",
                specialty="Oncology",
                organization="City Hospital",
                contact_info="smith@cityhospital.com"
            ),
            HCP(
                name="Dr. Sharma",
                specialty="Cardiology",
                organization="Heart Center",
                contact_info="sharma@heartcenter.com"
            ),
            HCP(
                name="Dr. Johnson",
                specialty="Neurology",
                organization="Regional Medical",
                contact_info="johnson@regionalmed.com"
            ),
            HCP(
                name="Dr. Williams",
                specialty="Pediatrics",
                organization="Children's Hospital",
                contact_info="williams@childrenshospital.com"
            ),
            HCP(
                name="Dr. Garcia",
                specialty="Endocrinology",
                organization="University Medical Center",
                contact_info="garcia@umc.edu"
            )
        ]
        
        for hcp in hcps:
            db.add(hcp)
        db.commit()
        print(f"Added {len(hcps)} HCPs")
        
        # Seed Materials
        print("Seeding Material data...")
        materials = [
            Material(
                name="Product X Brochure",
                type="Brochure",
                description="Comprehensive product information brochure"
            ),
            Material(
                name="Clinical Trial Results PDF",
                type="PDF",
                description="Phase III clinical trial results summary"
            ),
            Material(
                name="Product Presentation",
                type="Presentation",
                description="Sales presentation deck for HCP meetings"
            ),
            Material(
                name="Peer-Reviewed Publication",
                type="PDF",
                description="Published research paper in medical journal"
            ),
            Material(
                name="Sample Kit Information",
                type="Brochure",
                description="Information about sample distribution program"
            )
        ]
        
        for material in materials:
            db.add(material)
        db.commit()
        print(f"Added {len(materials)} materials")
        
        # Seed Samples
        print("Seeding Sample data...")
        samples = [
            Sample(
                name="Product X Sample Pack",
                batch_number="BATCH-2024-001",
                quantity=100,
                description="30-day sample pack for patient trials"
            ),
            Sample(
                name="Product Y Sample Pack",
                batch_number="BATCH-2024-002",
                quantity=50,
                description="14-day sample pack for patient trials"
            ),
            Sample(
                name="Product Z Sample Pack",
                batch_number="BATCH-2024-003",
                quantity=75,
                description="7-day sample pack for patient trials"
            )
        ]
        
        for sample in samples:
            db.add(sample)
        db.commit()
        print(f"Added {len(samples)} samples")
        
        # Seed sample interactions
        print("Seeding sample interactions...")
        interactions = [
            Interaction(
                hcp_id=1,
                interaction_type="Meeting",
                date=datetime.now(),
                time="14:00",
                attendees="Dr. Smith, Dr. Jones",
                topics_discussed="Product X efficacy, Phase III trial results",
                sentiment="Positive",
                outcomes="Agreed to review clinical data, interested in samples",
                follow_up_actions="Send clinical trial PDF, Schedule follow-up in 2 weeks",
                materials_shared=[1, 2],
                samples_distributed=[{"id": 1, "quantity": 5}],
                ai_suggested_followups=[
                    "Schedule follow-up meeting in 2 weeks",
                    "Send clinical trial data PDF",
                    "Request referral to colleague"
                ]
            ),
            Interaction(
                hcp_id=2,
                interaction_type="Call",
                date=datetime.now(),
                time="10:30",
                attendees="Dr. Sharma",
                topics_discussed="Product Y introduction, pricing discussion",
                sentiment="Neutral",
                outcomes="Requested more information about pricing",
                follow_up_actions="Send pricing proposal, Schedule in-person meeting",
                materials_shared=[3],
                samples_distributed=[],
                ai_suggested_followups=[
                    "Send pricing proposal",
                    "Schedule in-person meeting",
                    "Prepare cost-benefit analysis"
                ]
            )
        ]
        
        for interaction in interactions:
            db.add(interaction)
        db.commit()
        print(f"Added {len(interactions)} sample interactions")
        
        print("\n✅ Database initialization completed successfully!")
        print("Summary:")
        print(f"  - {len(hcps)} HCPs")
        print(f"  - {len(materials)} Materials")
        print(f"  - {len(samples)} Samples")
        print(f"  - {len(interactions)} Sample Interactions")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
