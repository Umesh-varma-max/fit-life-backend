# seed_trainers_doctors.py
"""
Seed script: Populate trainers and doctors tables with sample Indian data.
Run: python seed_trainers_doctors.py
"""

from app import create_app
from extensions import db
from models.trainer import Trainer
from models.doctor import Doctor

TRAINERS = [
    {
        "name": "Rahul Sharma",
        "specialization": "Weight Loss, HIIT, Functional Training",
        "location": "Andheri, Mumbai",
        "contact_email": "rahul.sharma@fitpro.com",
        "contact_phone": "+91-9876543210",
        "rating": 4.8,
        "available": True
    },
    {
        "name": "Priya Singh",
        "specialization": "Yoga, Flexibility, Meditation",
        "location": "Koramangala, Bangalore",
        "contact_email": "priya.singh@yogalife.com",
        "contact_phone": "+91-9876543211",
        "rating": 4.9,
        "available": True
    },
    {
        "name": "Arjun Nair",
        "specialization": "Strength Training, Bodybuilding",
        "location": "Banjara Hills, Hyderabad",
        "contact_email": "arjun.nair@ironfit.com",
        "contact_phone": "+91-9876543212",
        "rating": 4.7,
        "available": True
    },
    {
        "name": "Sneha Patel",
        "specialization": "Zumba, Dance Fitness, Cardio",
        "location": "SG Highway, Ahmedabad",
        "contact_email": "sneha.patel@dancefit.com",
        "contact_phone": "+91-9876543213",
        "rating": 4.6,
        "available": True
    },
    {
        "name": "Vikram Reddy",
        "specialization": "CrossFit, Martial Arts, Endurance",
        "location": "Jubilee Hills, Hyderabad",
        "contact_email": "vikram.reddy@crossfitindia.com",
        "contact_phone": "+91-9876543214",
        "rating": 4.5,
        "available": True
    },
    {
        "name": "Anjali Deshmukh",
        "specialization": "Pilates, Posture Correction, Rehab",
        "location": "Deccan, Pune",
        "contact_email": "anjali.d@pilatesworks.com",
        "contact_phone": "+91-9876543215",
        "rating": 4.8,
        "available": True
    },
    {
        "name": "Karan Kapoor",
        "specialization": "Sports Training, Athletics, Speed",
        "location": "Connaught Place, Delhi",
        "contact_email": "karan.k@sportspro.com",
        "contact_phone": "+91-9876543216",
        "rating": 4.4,
        "available": True
    },
]

DOCTORS = [
    {
        "name": "Dr. Priya Mehta",
        "specialization": "Dietitian & Nutritionist",
        "hospital": "Apollo Wellness Center, Mumbai",
        "contact_email": "dr.priya@apollowellness.com",
        "contact_phone": "+91-9812345678",
        "available_slots": ["Mon 10am-1pm", "Wed 3pm-6pm", "Fri 10am-1pm"],
        "rating": 4.9
    },
    {
        "name": "Dr. Arun Kumar",
        "specialization": "Sports Medicine",
        "hospital": "Fortis Hospital, Delhi",
        "contact_email": "dr.arun@fortis.com",
        "contact_phone": "+91-9812345679",
        "available_slots": ["Tue 9am-12pm", "Thu 2pm-5pm"],
        "rating": 4.8
    },
    {
        "name": "Dr. Sunita Rao",
        "specialization": "Endocrinologist (Diabetes & Metabolism)",
        "hospital": "Manipal Hospital, Bangalore",
        "contact_email": "dr.sunita@manipal.com",
        "contact_phone": "+91-9812345680",
        "available_slots": ["Mon 2pm-5pm", "Wed 9am-12pm", "Sat 10am-1pm"],
        "rating": 4.7
    },
    {
        "name": "Dr. Rajesh Gupta",
        "specialization": "Cardiologist (Heart & Fitness)",
        "hospital": "Max Super Speciality, Delhi",
        "contact_email": "dr.rajesh@maxhospital.com",
        "contact_phone": "+91-9812345681",
        "available_slots": ["Tue 10am-1pm", "Fri 3pm-6pm"],
        "rating": 4.9
    },
    {
        "name": "Dr. Meera Joshi",
        "specialization": "Physiotherapist (Injury Recovery)",
        "hospital": "Kokilaben Hospital, Mumbai",
        "contact_email": "dr.meera@kokilaben.com",
        "contact_phone": "+91-9812345682",
        "available_slots": ["Mon-Fri 9am-12pm"],
        "rating": 4.6
    },
    {
        "name": "Dr. Vikram Iyer",
        "specialization": "Ayurvedic & Holistic Health",
        "hospital": "Kerala Ayurveda Center, Kochi",
        "contact_email": "dr.vikram@keralaayurveda.com",
        "contact_phone": "+91-9812345683",
        "available_slots": ["Mon-Sat 10am-4pm"],
        "rating": 4.5
    },
]


def seed():
    """Insert trainers and doctors if tables are empty."""
    app = create_app()
    with app.app_context():
        # Seed trainers
        trainer_count = Trainer.query.count()
        if trainer_count == 0:
            for t in TRAINERS:
                db.session.add(Trainer(**t))
            db.session.commit()
            print(f"✅ Seeded {len(TRAINERS)} trainers successfully!")
        else:
            print(f"⚠️  Trainers table already has {trainer_count} records. Skipping.")

        # Seed doctors
        doctor_count = Doctor.query.count()
        if doctor_count == 0:
            for d in DOCTORS:
                db.session.add(Doctor(**d))
            db.session.commit()
            print(f"✅ Seeded {len(DOCTORS)} doctors successfully!")
        else:
            print(f"⚠️  Doctors table already has {doctor_count} records. Skipping.")


if __name__ == '__main__':
    seed()
