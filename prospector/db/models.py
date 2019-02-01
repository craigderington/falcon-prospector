import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

SAModel = declarative_base()


class User(SAModel):
    """
    The Company User Class
    """
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(255), unique=True, nullable=False)
    password = sa.Column(sa.String(255), nullable=False)
    company_id = sa.Column(sa.Integer, sa.ForeignKey('companies.id'), nullable=False)
    company = relationship('Company')
    token = sa.Column(sa.String(1024), unique=True)
    last_login = sa.Column(sa.DateTime, nullable=False, onupdate=datetime.now)

    def __init__(self, username, password, company_id):
        self.username = username
        self.set_password(password)
        self.company_id = company_id
        self.set_token()

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def as_dict(self):
        return {
            'username': self.username,
            'company': self.company
        }

    @classmethod
    def get_user_list(cls, session):
        models = []

        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models

    def save(self, session):
        with session.begin():
            session.add(self)

    def set_token(self):
        self.token = secrets.token_urlsafe(1024)


class Company(SAModel):
    """
    The Company Class
    """
    __tablename__ = 'companies'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), unique=True, nullable=False)
    address = sa.Column(sa.String(255), nullable=False)
    address2 = sa.Column(sa.String(50), nullable=True)
    city = sa.Column(sa.String(255), nullable=False)
    state = sa.Column(sa.String(2), unique=True, nullable=False)
    zip_code = sa.Column(sa.String(255), nullable=False)
    zip_4 = sa.Column(sa.String(4), nullable=True)
    p_contact = sa.Column(sa.String(255), unique=True, nullable=True)
    p_contact_number = sa.Column(sa.String(20), unique=True, nullable=True)
    secret_passphrase = sa.Column(sa.String(255), unique=True, nullable=False)
    subscription_type = sa.Column(sa.String(255), nullable=True)
    subscription_status = sa.Column(sa.String(20), nullable=False, default='ACTIVE')
    subscription_date = sa.Column(sa.DateTime, onupdate=datetime.now)

    def __init__(self, name, address, city, state, zip_code,
                 sub_type, status):
        self.name = name
        self.address = address
        self.city = city
        self.state = state.upper().strip()
        self.subscription_type = sub_type
        self.subscription_status = status

    def __repr__(self):
        if self.name:
            return '{} {} {}'.format(
                self.name,
                self.address,
                self.state
            )

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'company': self.name,
            'city': self.city,
            'state': self.state,
            'postal_code': self.zip_code
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_list(cls, session):
        models = []

        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models


class IPAddress(SAModel):
    """
    The IPAddress Class
    :return ip_address
    """

    __tablename__ = 'ipaddress'

    id = sa.Column(sa.Integer, primary_key=True)
    created_date = sa.Column(sa.DateTime, onupdate=datetime.now)
    ip = sa.Column(sa.String(15), index=True)
    city = sa.Column(sa.String(255))
    time_zone = sa.Column(sa.String(50))
    longitude = sa.Column(sa.String(50))
    latitude = sa.Column(sa.String(50))
    metro_code = sa.Column(sa.String(3))
    dma_code = sa.Column(sa.String(3))
    area_code = sa.Column(sa.String(3))
    postal_code = sa.Column(sa.String(10))
    region = sa.Column(sa.String(255))
    region_name = sa.Column(sa.String(255))

    def __init__(self, created_date, ip, city, time_zone, longitude, latitude,
                 metro_code, dma_code, area_code, postal_code, region, region_name):

        self.created_date = created_date
        self.ip = ip

    def __repr__(self):
        return '{}'.format(
            self.ip
        )

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'city': self.city,
            'metro_code': self.metro_code,
            'dma_code': self.dma_code,
            'postal_code': self.postal_code,
            'region_name': self.region_name,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_ip_addr(cls, ip_pk_id, session):
        ip_addr = []
        with session.begin():
            query = session.query(cls).filter(
                cls.id == ip_pk_id
            )
            ip_addr = query.first()

        return ip

    @classmethod
    def get_list(cls, session):
        models = []
        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models


class Person(SAModel):
    """
    The Person Class
    :return person obj
    """

    __tablename__ = 'persons'
    id = sa.Column(sa.Integer, primary_key=True)
    ipaddress_id = sa.Column(sa.Integer, sa.ForeignKey('ipaddress.id'))
    created_date = sa.Column(sa.DateTime, onupdate=datetime.now)
    first_name = sa.Column(sa.String(255))
    last_name = sa.Column(sa.String(255))
    email = sa.Column(sa.String(255))
    home_phone = sa.Column(sa.String(15))
    cell_phone = sa.Column(sa.String(15))
    address1 = sa.Column(sa.String(255))
    address2 = sa.Column(sa.String(255))
    city = sa.Column(sa.String(255))
    state = sa.Column(sa.String(2))
    zip_code = sa.Column(sa.String(5))
    zip_4 = sa.Column(sa.Integer)
    credit_range = sa.Column(sa.String(50))
    car_year = sa.Column(sa.String(10))
    car_make = sa.Column(sa.String(255))
    car_model = sa.Column(sa.String(255))

    def __init__(self, ipaddress_id, created_date, first_name, last_name, email, cell_phone,
                 address1, address2, city, state, zip_code):
        self.ipaddress_id = ipaddress_id
        self.created_date = created_date
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.cell_phone = cell_phone
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip_code = zip_code

    def __repr__(self):
        return '{} {} {}'.format(
            self.first_name,
            self.last_name,
            self.created_date
        )

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'created_date': self.created_date,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'cell_phone': self.cell_phone,
            'address': self.address1,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'credit_range': self.credit_range,
            'car_year': self.car_year,
            'car_make': self.car_make,
            'car_mode': self.car_model
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_person_list(cls, session):
        models = []
        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models


class Address(SAModel):
    """
    Address Class
    :return address obj
    """

    __tablename__ = 'address'
    id = sa.Column(sa.Integer, primary_key=True)
    lon = sa.Column(sa.Float, nullable=True, default=0.00)
    lat = sa.Column(sa.Float, nullable=True, default=0.00)
    number = sa.Column(sa.Integer, nullable=False)
    street = sa.Column(sa.String(100), nullable=False)
    unit = sa.Column(sa.String(50), nullable=True)
    city = sa.Column(sa.String(100), nullable=False)
    district = sa.Column(sa.String(50), nullable=True)
    region = sa.Column(sa.String(50), nullable=True)
    postcode = sa.Column(sa.String(10), nullable=False)
    unique_id = sa.Column(sa.String(50), nullable=True)

    def __init__(self, lat, lon, number, street, unit, city, district, region, postcode, unique_id):
        self.lat = lat
        self.lon = lon
        self.number = number
        self.street = street
        self.unit = unit
        self.city = city
        self.district = district
        self.region = region
        self.postcode = postcode
        self.unique_id = unique_id

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'lat': self.lat,
            'lon': self.lon,
            'number': self.number,
            'street': self.street,
            'unit': self.unit,
            'city': self.city,
            'district': self.district,
            'region': self.region,
            'postcode': self.postcode,
            'unique_id': self.unique_id
        }

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_addr(cls, addr_pk_id, session):
        addr = []
        with session.begin():
            query = session.query(cls).filter(
                cls.id == addr_pk_id
            )
            addr = query.first()

        return addr

    @classmethod
    def get_list(cls, session):
        models = []
        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models

    @classmethod
    def get_update_list(cls, session):
        addr_list = []
        with session.begin():
            query = session.query(cls).filter(
                cls.postcode == ''
            ).limit(1000)

            addr_list = query.all()

        return addr_list


class ZipCode(SAModel):
    """
    Zipcode Class
    :return zipcode
    """
    __tablename__ = 'zipcodes'
    id = sa.Column(sa.Integer, primary_key=True)
    country_code = sa.Column(sa.String(2), nullable=False)
    postal_code = sa.Column(sa.String(20), nullable=False, unique=True)
    city_name = sa.Column(sa.String(180), nullable=False)
    state = sa.Column(sa.String(100), nullable=False)
    state_abbr = sa.Column(sa.String(20), nullable=False)
    county = sa.Column(sa.String(100), nullable=False)
    county_code = sa.Column(sa.String(20), nullable=False)
    community = sa.Column(sa.String(100), nullable=False)
    community_code = sa.Column(sa.String(20), nullable=False)
    latitude = sa.Column(sa.Float, nullable=False)
    longitude = sa.Column(sa.Float, nullable=False)
    accuracy = sa.Column(sa.Integer)

    def __init__(self, postal_code, city_name, state, county, latitude, longitude, accuracy):
        self.postal_code = postal_code
        self.city_name = city_name
        self.state = state
        self.county = county
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy

    def __repr__(self):
        return '{}'.format(self.postal_code)

    def as_dict(self):
        return {
            'postal_code': self.postal_code,
            'city_name': self.city_name,
            'state': self.state,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy
        }

    def get_coordinates(self):
        return '{} {}'.format(self.latitude, self.longitude)

    def save(self, session):
        with session.begin():
            session.add(self)

    @classmethod
    def get_list(cls, session):
        models = []
        with session.begin():
            query = session.query(cls)
            models = query.all()

        return models

    @classmethod
    def get_zip_code(cls, postal_code, session):
        zipcode = []
        with session.begin():
            query = session.query(cls).filter(
                cls.postal_code == postal_code
            )

            zipcode = query.first()

        return zipcode

    @classmethod
    def query_for_codes(cls, city, state, session):
        zipcode = []
        with session.begin():
            query = session.query(cls).filter(
                cls.state == state,
                cls.city_name == city
            )

            zipcode = query.first()

        return zipcode

