from app import app, db
from models import Property, Reservation, Financial, Staff, Log, Settings
from datetime import date, timedelta
import random

def seed_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("Cleared database.")

        print("Seeding data...")

        # 0. Initialize Settings
        Settings.set('price_min_percent', '70')  # Min 70% of base price
        Settings.set('price_max_percent', '150')  # Max 150% of base price
        Settings.set('price_step_percent', '8')  # Adjust by 8% each time
        Settings.set('auto_pricing_enabled', 'true')
        Settings.set('low_occupancy_threshold', '20')
        Settings.set('high_occupancy_threshold', '70')

        # Initial System Logs
        db.session.add(Log(event_type="Operations", category="System", message="System initialization started"))
        db.session.add(Log(event_type="Operations", category="System", message="Database cleared and ready for seeding"))

        # 1. Properties (25+ properties)
        prop_types = ["Villa", "Apartment", "House", "Cabin", "Studio", "Penthouse", "Loft", "Cottage"]
        locations = ["Malibu", "Seattle", "Aspen", "NYC", "Miami", "Austin", "Chicago", "Denver", "San Diego", "Boston", "San Francisco", "Nashville"]
        adjectives = ['Sunset', 'Urban', 'Cozy', 'Modern', 'Luxury', 'Seaside', 'Mountain', 'City', 'Rustic', 'Vintage', 'Grand', 'Hidden', 'Sunny', 'Golden']
        
        props = []
        for i in range(25):
            p_type = random.choice(prop_types)
            base_price = random.randint(80, 800)
            title = f"{random.choice(adjectives)} {p_type} {random.randint(1, 100)}"
            props.append(Property(
                title=title,
                type=p_type,
                base_price=base_price,
                address=f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Cedar', 'Maple', 'Elm'])} St, {random.choice(locations)}",
                status=random.choice(['Clean', 'Clean', 'Clean', 'Dirty', 'Maintenance'])
            ))
            
        db.session.add_all(props)
        db.session.commit()
        db.session.add(Log(event_type="Operations", category="System", message=f"Successfully onboarded {len(props)} properties"))
        
        # Reload to get IDs
        props = Property.query.all()

        # 2. Staff
        staff = [
            Staff(name="Alice Johnson", role="Manager", contact="555-0101"),
            Staff(name="Bob Smith", role="Cleaner", contact="555-0102"),
            Staff(name="Charlie Davis", role="Maintenance", contact="555-0103"),
            Staff(name="Diana Prince", role="Cleaner", contact="555-0104"),
            Staff(name="Evan Wright", role="Concierge", contact="555-0105"),
            Staff(name="Fiona Green", role="Manager", contact="555-0106")
        ]
        db.session.add_all(staff)
        db.session.add(Log(event_type="Operations", category="System", message=f"Registered {len(staff)} staff members"))

        # 3. Reservations & Financials
        today = date.today()
        
        for prop in props:
            for _ in range(random.randint(3, 8)):
                start_delta = random.randint(-60, 60)
                duration = random.randint(2, 14)
                
                check_in = today + timedelta(days=start_delta)
                check_out = check_in + timedelta(days=duration)
                
                amount = prop.base_price * duration
                
                res = Reservation(
                    property_id=prop.id,
                    guest_name=random.choice(["John", "Jane", "Mike", "Sarah", "David", "Emily", "Chris", "Jessica"]) + " " + random.choice(["Doe", "Smith", "Brown", "Wilson", "Lee"]),
                    check_in=check_in,
                    check_out=check_out,
                    amount_paid=amount
                )
                db.session.add(res)
                db.session.add(Financial(property_id=prop.id, category="Income", amount=amount, date=check_in))

            for _ in range(random.randint(1, 4)):
                expense_date = today + timedelta(days=random.randint(-30, 0))
                db.session.add(Financial(
                    property_id=prop.id, 
                    category=random.choice(["Utility", "Repair", "Tax", "Cleaning"]), 
                    amount=random.randint(50, 500), 
                    date=expense_date
                ))

        db.session.commit()
        db.session.add(Log(event_type="Operations", category="System", message="System Seed Complete. Ready for autonomous operations"))
        db.session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
