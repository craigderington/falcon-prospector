import falcon
from falcon.media.validators.jsonschema import validate
from sqlalchemy.exc import IntegrityError
from prospector.db import models
from prospector.resources import BaseResource
from prospector.schemas import load_schema


class UserResource(BaseResource):
    """
    The User Class
    :return user, user_list
    """

    def on_get(self, req, resp):
        user = models.User.get_user_list(self.db.sdession)
        user = user.as_dict()

        resp.status = falcon.HTTP_200
        resp.media = {
            'user': user
        }

    @validate(load_schema('user_schema'))
    def on_post(self, req, resp):
        model = models.User(
            username=req.media.get('username'),
            password=req.media.get('password'),
            company_id=req.media.get('company_id')
        )

        try:
            model.save(self.db.session)
        except IntegrityError as err:
            raise falcon.HTTPBadRequest(
                'User Already Exists'
                'Error: {}'.format(str(err))
            )

        resp.status = falcon.HTTP_201
        resp.media = {
            'id': model.id
        }


