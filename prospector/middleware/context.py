import uuid
import falcon


class AuthMiddleware(object):

    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        account_id = req.get_header('Account-ID')

        challenges = ['Token type="Fernet"']

        if token is None:
            description = ('Please provide an auth token '
                           'as part of the request.')

            raise falcon.HTTPUnauthorized('Auth token required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

        if not self._token_is_valid(token, account_id):
            description = ('The provided auth token is not valid. '
                           'Please request a new token and try again.')

            raise falcon.HTTPUnauthorized('Authentication required',
                                          description,
                                          challenges,
                                          href='http://docs.example.com/auth')

    def _token_is_valid(self, token, account_id):
        return True


def set_context(req, resp):
    if not req.context.get('request_id'):
        req.context['request_id'] = str(uuid.uuid4())

    resp.set_header('request-id', req.context['request_id'])


class ContextMiddleware(object):
    """
    Set the Request Content and add custom header
    """
    def process_request(self, req, resp):
        set_context(req, resp)
