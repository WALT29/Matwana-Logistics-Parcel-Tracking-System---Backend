from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates, back_populates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()


class User(db.Model,SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)  # (customers,admin or customer service)
    
    # the relationshjps
    sent_parcels = db.relationship('Parcel', foreign_keys='Parcel.sender_id', back_populates='sender')
    received_parcels = db.relationship('Parcel', foreign_keys='Parcel.recipient_id', back_populates='recipient')
    parcels = db.relationship('UserParcelAssignment', back_populates='user', cascade='all, delete-orphan')

    @validates('phone_number')
    def validate_phone(self, key, phone_number):
        if not phone_number.is_digit() or len(phone_number) !=10:
            raise ValueError("Phone number must be 10 digits and contain only numbers.")
        return phone_number
    
    @validates('email')
    def validate_email(self,key,email):
        if email and '@' not in email:
            raise ValueError("Please enter a valid email format")
        
    
    def __repr__(self):
        return f'<User {self.name}, Role: {self.role}>'


class Parcel(db.Model,SerializerMixin):
    __tablename__ = 'parcels'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    tracking_number = db.Column(db.String, unique=True, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='Pending')  # (pending,in_transit,delivered)
    shipping_cost = db.Column(db.Float)

    #the foreign ids
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))

    # the relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_parcels')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='received_parcels')
    vehicle = db.relationship('Vehicle', back_populates='parcels')
    
    customer_service_assignments = db.relationship('UserParcelAssignment', back_populates='parcel', cascade='all, delete-orphan')

    @validates('weight')
    def validate_weight(self, key, weight):
        assert weight > 0, "Weight must be positive number"
        return weight

    def calculate_shipping_cost(self):
        location_rate = Location.query.filter_by(origin=self.origin, destination=self.destination).first()
        if location_rate:
            self.shipping_cost = location_rate.cost_per_kg * self.weight
        else:
            raise ValueError(f"No shipping rate available for {self.origin} to {self.destination}")

    def __repr__(self):
        return f'<Parcel {self.tracking_number}, {self.status}, Cost: {self.shipping_cost}>'


class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String, unique=True, nullable=False)
    driver_name = db.Column(db.String, nullable=False)
    driver_phone = db.Column(db.String, nullable=False)

    parcels = db.relationship('Parcel', back_populates='vehicle')

    def __repr__(self):
        return f'<Vehicle {self.number_plate}, Driver: {self.driver_name}>'

class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    current_location = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)  
    updated_at = db.Column(db.DateTime, default=db.func.now())

    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'))
    parcel = db.relationship('Parcel')

    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))

    def __repr__(self):
        return f'<Shipment {self.id}, {self.current_location}>'

# we have used this table for calculating the rates this table is only used by the admin who sets different rates
class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    cost_per_kg = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Location {self.origin} to {self.destination}, Cost: {self.cost_per_kg} per kg>'


class UserParcelAssignment(db.Model,SerializerMixin):
    __tablename__ = 'user_parcel_assignments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) #this is a customer service user
    parcel_id = db.Column(db.Integer, db.ForeignKey('parcels.id'))

    user = db.relationship('User', back_populates='parcels')
    parcel = db.relationship('Parcel', back_populates='customer_service_assignments')

    def __repr__(self):
        return f'<UserParcelAssignment User: {self.user_id}, Parcel: {self.parcel_id}>'
