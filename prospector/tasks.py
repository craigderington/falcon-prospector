import aumbry
import celery
import time
from datetime import datetime
from prospector.db.models import IPAddress, Person, Address, ZipCode
from prospector.db.manager import DBManager
import GeoIP
import reverse_geocoder as rg
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from prospector.config import AppConfig
from sqlalchemy import exc
from random import randint

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

# celery beat
app.conf.beat_schedule = {
    "sum-two-numbers": {
        "task": "tasks.add",
        "schedule": 10.0
    },
    "Update Zip Codes": {
        "task": "tasks.get_addr_for_update",
        "schedule": 30.0
    }
}


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


@app.task
def update_zipcode(addr_pk_id):
    """
    Take a given address, return a zipcode and update the address record
    :param addr_pk_id:
    :return:
    """

    try:
        addr = Address.get_addr(addr_pk_id, mgr.session)
        if addr:
            addr_fields = (addr.city, addr.region, addr.postcode)

            # check the existing address fields
            if all(addr_fields):
                try:
                    addr.processed = 1
                    addr.save(mgr.session)
                    logger.info('All address data exists for Addr: {}, skipping...'.format(str(addr_pk_id)))

                except exc.SQLAlchemyError as db_err:
                    logger.critical('Could not save record: {}'.format(str(db_err)))

            else:
                # address fields missing, query the zip code database for matching data
                try:
                    data = ZipCode.query_for_code(addr.city, addr.region, mgr.session)

                    if data:
                        try:
                            addr.postcode = data.postal_code
                            addr.processed = 1
                            addr.save(mgr.session)
                            logger.info('Addr ID: {} updated with zip code: {}'.format(str(addr.id), str(data.postal_code)))

                        except exc.SQLAlchemyError as db_err:
                            logger.critical('Could not save record: {}'.format(str(db_err)))

                    else:
                        addr.processed = 1
                        addr.save(mgr.session)
                        logger.info('Address zip code not found for: {}.  Marking Processed'.format(str(addr.id)))

                except exc.SQLAlchemyError as db_err:
                    logger.critical('Can not query the zip code data {}'.format(str(db_err)))

    except exc.SQLAlchemyError as db_err:
        logger.critical('Database error: {}'.format(str(db_err)))

    # return the addr_pk_id
    return addr_pk_id


@app.task
def get_addr_for_update():
    """
    Get the records with incomplete addresses
    :param addr_pk_id:
    :return: none
    """

    addr_list = Address.get_update_list(mgr.session)
    counter = 0

    for addr in addr_list:
        update_zipcode.delay(addr.id)
        counter += 1

    logger.info('Air dropped {} into the update queue'.format(str(counter)))
    return counter


@app.task
def add():
    return randint(1000, 10000) * randint(3, 21)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # periodic task executes every 30 seconds
    sender.add_periodic_task(30.0, get_addr_for_update, name='Get Address for Update')

    sender.add_periodic_task(
        crontab(hour=0, minute=2),
        add(12, 35),
        name='Sum Two Numbers'
    )

