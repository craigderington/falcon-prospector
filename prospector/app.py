#!.env/bin/python
# -*- code: utf-8 -*-
# prospector/app.py

import json
import falcon
from celery.result import AsyncResult
from prospector.tasks import get_ip_for_geo_locate
from prospector.db.manager import DBManager
from prospector.middleware.context import ContextMiddleware
from prospector.resources import ipaddresses, persons


class ProspectorService(falcon.API):
    """
    The Base Prospector Service Class
    :return service
    """
    def __init__(self, cfg):
        super(ProspectorService, self).__init__(
            middleware=[ContextMiddleware()]
        )

        self.cfg = cfg

        mgr = DBManager(self.cfg.db.connection)
        mgr.setup()

        ipaddress_resource = ipaddresses.IPAddressResource(mgr)
        person_resource = persons.PersonResource(mgr)

        self.add_route('/ipaddress/<:string>', ipaddress_resource)
        self.add_route('/person/<:string>', person_resource)

    def start(self):
        """
        Convenience method when Gunicorn calls run()
        :return: custom worker
        """
        pass

    def stop(self):
        """
        Convenience method for stopping all Gunicorn workers
        :return: none
        """
        pass


class StartTask(object):
    """
    Start a Celery Task Instance
    :return celery.task
    """

    def on_get(self, req, resp, *, ip):
        # start task
        task = get_ip_for_geo_locate.delay(ip)
        resp.status = falcon.HTTP_200
        # return task_id to client
        result = {'task_id': task.id}
        resp.body = json.dumps(result)


class TaskStatus(object):
    """
    Task Status Class
    :return celery.task.status
    """

    def on_get(self, req, resp, *, task_id):
        # get result of task by task_id and generate content to client
        task_result = AsyncResult(task_id)
        result = {'status': task_result.status, 'result': task_result.result}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(result)
