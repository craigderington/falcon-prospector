import falcon
from falcon.media.validators.jsonschema import validate
from sqlalchemy.exc import IntegrityError
from prospector.db import models
from prospector.resources import BaseResource
from prospector.schemas import load_schema


class IPAddressResource(BaseResource):
    """
    The IPAddress Resource
    :return ip
    """

    def on_get(self, req, resp, ip):
        ips = models.IPAddress.get_list(self.db.session)
        address = ips.as_dict()

        resp.status = falcon.HTTP_200
        resp.media = {
            'result': address
        }

    @validate(load_schema('ipaddress_schema'))
    def on_post(self, req, resp):
        model = models.IPAddress(
            ip=req.media.get('ipaddress'),
            city=req.media.get('city'),
            time_zone=req.media.get('time_zone'),
            area_code=req.media.get('area-code'),
            metro_code=req.media.get('metro_code'),
            dma_code=req.media.get('dma_code'),
            postal_code=req.media.get('postal_code'),
            region=req.media.get('region'),
            region_name=req.media.get('region_name'),
            latitude=-req.media.get('latitude'),
            longitude=req.media.get('longitude')
        )

        try:
            model.save(self.db.session)
        except IntegrityError as err:
            raise falcon.HTTPBadRequest(
                'IP Address Already Exists'
                'Error: {}'.format(str(err))
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }
