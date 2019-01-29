import falcon
from falcon.media.validators.jsonschema import validate
from sqlalchemy.exc import IntegrityError
from prospector.db import models
from prospector.resources import BaseResource
from prospector.schemas import load_schema


class CompanyResource(BaseResource):
    """
    The Company Resource
    :return company
    """

    def on_get(self, req, resp, id):
        data = models.Company.get_list(self.db.session)
        company = data.as_dict()

        resp.status = falcon.HTTP_200
        resp.media = {
            'result': company
        }

    @validate(load_schema('company_schema'))
    def on_post(self, req, resp):
        model = models.Company(
            name=req.media.get('name'),
            address=req.media.get('address'),
            city=req.media.get('city'),
            state=req.media.get('state'),
            zip_code=req.media.get('zip_code'),
            sub_type='Premium',
            status='ACTIVE'
        )

        try:
            model.save(self.db.session)
        except IntegrityError as err:
            raise falcon.HTTPBadRequest(
                'Company already exists '
                'Error: {}'.format(str(err))
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }
