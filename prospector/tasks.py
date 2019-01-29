import aumbry
import celery
import time
from datetime import datetime
from prospector.db.models import IPAddress, Person
from prospector.db.manager import DBManager
import GeoIP
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

# Open the geo data file once and store it in cache memory
gi = GeoIP.open('/var/lib/geoip/GeoLiteCity.dat', GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)


@app.task
def get_location(ip_addr):
    gi_lookup = gi.record_by_addr(ip_addr)
    return gi_lookup


@app.task
def get_ip_for_geo_locate(ip_pk_id):
    """
    Geolocate an IPAddress
    :param ip_pk_id
    :return: ip
    """
    return '.'.join(str(i) for i in range(4))


@app.task
def add(x, y):
    """
    :param int x:
    :param int y:
    :return: int
    """
    return x + y


@app.task
def generate_ips():
    """
    Generate IP Addresses
    :return: list
    """
    # create IP addresses
    today = datetime.now()

    for i in range(0, 255):
        for p in range(0, 255):
            for a in range(0, 255):
                for d in range(0, 255):
                    ip = '{}.{}.{}.{}'.format(str(i), str(p), str(a), str(d))

                    # call get_location
                    try:
                        geo_data = get_location(ip)

                        if not geo_data:

                            geo_data = {
                                'country_name': 'GeoIP Lookup failed',
                                'city': 'Unknown',
                                'time_zone': 'Unknown',
                                'longitude': 0.00,
                                'latitude': 0.00,
                                'metro_code': 'Unknown',
                                'country_code': None,
                                'country_code3': None,
                                'dma_code': None,
                                'area_code': None,
                                'postal_code': None,
                                'region': 'Unknown',
                                'region_name': 'Unknown',
                                'traffic_type': 'Unknown'
                            }

                        try:

                            new_ip = IPAddress(
                                created_date=today,
                                ip=ip,
                                city=geo_data['city'],
                                time_zone=geo_data['time_zone'],
                                longitude=geo_data['longitude'],
                                latitude=geo_data['latitude'],
                                metro_code=geo_data['metro_code'],
                                dma_code=geo_data['dma_code'],
                                area_code=geo_data['area_code'],
                                postal_code=geo_data['postal_code'],
                                region=geo_data['region'],
                                region_name=geo_data['region_name']
                            )

                            new_ip.save(mgr.session)
                            logger.info('IP: {}'.format(str(ip)))
                            logger.info('GeoLocate: {}'.format(str(geo_data)))
                            time.sleep(0.25)

                        except exc.SQLAlchemyError as db_err:
                            logger.warning('{}'.format(str(db_err)))

                    except Exception as err:
                        logger.warning('Unable to call GeoLocate: {}'.format(str(err)))

    return ip


def geo_locate():
    """
    Test GeoIP
    ip = '142.196.239.189'
    :return: geoip dict
    """

    ip = '142.196.239.189'
    geo_data = get_location(ip)
    print('IP: {}, GeoData: {}'.format(str(ip), str(geo_data)))
