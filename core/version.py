import falcon
import simplejson as json


class VersionItem:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):

        result = {"version": 'MyEMS 1.0.3 (Community Edition)',
                  "release-date": '20210215',
                  "website": "https://myems.io"}
        resp.body = json.dumps(result)

