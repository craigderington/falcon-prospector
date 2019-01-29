import falcon
from falcon.media.validators.jsonschema import validate
from sqlalchemy.exc import IntegrityError
from prospector.db import models
from prospector.resources import BaseResource
from prospector.schemas import load_schema


class PersonResource(BaseResource):
    """
    The Person Resource
    :return person
    """

    def on_get(self, req, resp):
        person = models.Person.get_person_list(self.db.sdession)
        person = person.as_dict()

        resp.status = falcon.HTTP_200
        resp.media = {
            'person': person
        }

    @validate(load_schema('person_schema'))
    def on_post(self, req, resp):
        model = models.Person(
            first_name=req.media.get('first-name'),
            last_name=req.media.get('last-name'),
            email=req.media.get('email'),
            cell_phone=req.media.get('cell-phone'),
            address1=req.media.get('address1'),
            address2=req.media.get('address2'),
            city=req.media.get('city'),
            state=req.media.get('state'),
            zip_code=req.media.get('zip_code')
        )

        try:
            model.save(self.db.session)
        except IntegrityError as err:
            raise falcon.HTTPBadRequest(
                'Person Already Exists'
                'Error: {}'.format(str(err))
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }
