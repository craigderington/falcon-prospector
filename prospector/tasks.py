import aumbry
import celery
import time
from datetime import datetime
from prospector.db.models import IPAddress, Person, Address
from prospector.db.manager import DBManager
import GeoIP
import reverse_geocoder as rg
from celery.utils.log import get_task_logger
from prospector.config import AppConfig
from sqlalchemy import exc

# database config
cfg = aumbry.load(aumbry.FILE, AppConfig, {'CONFIG_FILE_PATH': '../config/config.yaml'})
mgr = DBManager(cfg.db.connection)

app = celery.Celery(
    'tasks',
    broker='amqp://',
    backend='redis://localhost:6379/0'
)

# logger
logger = get_task_logger(__name__)

# open the geo data file once and store it in cache memory
gi = GeoIP.open('/var/lib/geoip/GeoLiteCity.dat', GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)


def get_location(ip_addr):
    gi_lookup = gi.record_by_addr(ip_addr)
    return gi_lookup


def reverse_geo_code(coordinates):
    """
    Reverse GeoCode from Coordinates
    :param coordinates: int: x, int y
    :return: location
    """
    location = rg.search(coordinates, mode=1)
    return location


@app.task
def coordinates_to_address(addr_pk_id):
    """
    Convert Address coordinates to a deliverable address
    :param addr_pk_id:
    :return: addr_pk_id
    """
    rec = Address.get_addr(addr_pk_id, mgr.session)
    coordinates = (rec.lat, rec.lon)
    location = reverse_geo_code(coordinates)

    if location is not None:
        state = location[0]['admin1']
        city = location[0]['name']
        county = location[0]['admin2']
        country = location[0]['cc']
        fields = (rec.city, rec.district, rec.region)

        if all(fields):
            logger.info('Data exists for record {}.  Skipping...'.format(str(addr_pk_id)))
        else:
            rec.city = city
            rec.district = county
            rec.region = state
            rec.save(mgr.session)
            logger.info('Address record {} was updated with City: {}, State: {} and County: {}'.format(
                addr_pk_id, city, state, county
            ))

    return addr_pk_id
