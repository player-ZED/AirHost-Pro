from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50)) # Apartment, House, Villa
    base_price = db.Column(db.Float)
    address = db.Column(db.String(200))
    status = db.Column(db.String(20)) # Clean, Dirty, Maintenance

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'base_price': self.base_price,
            'address': self.address,
            'status': self.status
        }

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    guest_name = db.Column(db.String(100))
    check_in = db.Column(db.Date)
    check_out = db.Column(db.Date)
    amount_paid = db.Column(db.Float)
    
    property = db.relationship('Property', backref='reservations')

class Financial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    category = db.Column(db.String(50)) # Income, Repair, Utility
    amount = db.Column(db.Float)
    date = db.Column(db.Date)

    property = db.relationship('Property', backref='financials')

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.String(50)) # Manager, Cleaner
    contact = db.Column(db.String(50))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_type = db.Column(db.String(50)) # Operations, Pricing, Financial
    category = db.Column(db.String(50)) # Booking, Maintenance, Alert, System
    message = db.Column(db.String(200))

    def to_dict(self):
        return {
            'time': self.timestamp.strftime('%I:%M:%S %p'),
            'event_type': self.event_type,
            'category': self.category,
            'message': self.message
        }

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True)
    value = db.Column(db.String(100))
    
    @staticmethod
    def get(key, default=None):
        setting = Settings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set(key, value):
        setting = Settings.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = Settings(key=key, value=str(value))
            db.session.add(setting)
        db.session.commit()
