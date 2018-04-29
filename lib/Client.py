import logging
from esipy import App
from esipy import EsiClient
from esipy.cache import FileCache
import bravado.client
from pymongo import MongoClient
from bravado.client import SwaggerClient
from bravado.requests_client import RequestsClient
from bravado.requests_client import Authenticator

"""
Code borrowed and possibly modified slightly from: 
https://github.com/OrbitalEnterprises/eve-market-strategies
"""
user_agent="Alderith test app - alderith@gmail.com"
cache = FileCache(path="/tmp")
class __ExternalClientMap:
    """
    Internal class for all external clients
    """
    def __init__(self):
        self.client_map = {}
        bravado.client.log.setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)


    def get(self, client_type,key):
        if client_type not in self.client_map:
            return None
        return self.client_map[client_type][key]

    def set(self, client_type, key, value):
        if client_type not in self.client_map:
            self.client_map[client_type] = {}
        self.client_map[client_type][key] = value

def __mk_key__(*args):
    """
    Create a key by concatenating strings
    :param args: string arguments to concatenate
    :return: concatenated key
    """
    return "_".join(args)

__external_clients__ = __ExternalClientMap()



class SDE:
    @staticmethod
    def get(version=None):
        """
        Get a Swagger client for the Orbital Enterprises SDE service
        :param version: version of SDE to retrieve, defaults to 'latest'
        :return: a SwaggerClient for the requested SDE
        """
        global __external_clients__
        if version is None:
            version ='latest'
        sde_url = "https://evekit-sde.orbital.enterprises/latest/swagger.json"
        if version != 'latest':
            sde_url = "https://evekit-sde.orbital.enterprises/%s/api/ws/v%s/swagger.json" % (version, version)
        existing = __external_clients__.get('SDE', version)
        if existing is None:
            existing = SwaggerClient.from_url(sde_url,
                                              config={'use_models': False,
                                                      'validate_responses': False,
                                                      'also_return_response': True})
            __external_clients__.set('SDE', version, existing)
        return existing

class ESI:
    @staticmethod
    def get(release='latest', source='tranquility'):
        """
        Get a Swagger client for the EVE Swagger Interface
        :param release: ESI release.  One of 'latest', 'legacy' or 'dev'.
        :param source: ESI source.  One of 'tranquility' or 'singularity'.
        :return: a SwaggerClient for the EVE Swagger Interface
        """
        global __external_clients__
        existing = __external_clients__.get('ESI',__mk_key__(release,source))
        if existing is None:
            url = "https://esi.tech.ccp.is/%s/swagger.json?datasource=%s" % (release, source)
            existing = SwaggerClient.from_url(url,
                                              config={'use_models': False,
                                                      'validate_responses' : False,
                                                      'validate_swagger_spec': True,
                                                      'also_return_response': True})
            __external_clients__.set('ESI',__mk_key__(release,source),existing)
        return existing

class ESIPYAPP:
    @staticmethod
    def get(release='latest',source='tranquility'):
        """
        Lets try ESIpy instead of bravado...
        """
        global __external_clients__
        existing = __external_clients__.get('ESIPYAPP',__mk_key__(release,source))
        if existing is None:
            this_url = "https://esi.tech.ccp.is/%s/swagger.json?datasource=%s" % (release, source)
            print(this_url)
            existing = App.create(url=this_url)
            __external_clients__.set('ESIPYAPP',__mk_key__(release,source),existing)
        return existing
    
class ESIPY:
    @staticmethod
    def get(release='latest',source='tranquility'):
        """
        Lets try ESIpy instead of bravado...
        """
        global __external_clients__
        existing = __external_clients__.get('ESIPY',__mk_key__(release,source))
        if existing is None:
            existing = EsiClient(
                retry_requests=True,  # set to retry on http 5xx error (default False)
                header={'User-Agent': 'Jimmy - api test app:  alderith@gmail.com @grux on slack'},
                raw_body_only=True,  # default False, set to True to never parse response and only return raw JSON string content.
            )
            __external_clients__.set('ESIPY',__mk_key__(release,source),existing)
        return existing
class MONGO:
    @staticmethod
    def get():
        """
        Just a mongo client...
        """
        global __external_clients__
        existing = __external_clients__.get('MONGO',"to_do_versioning")
        if existing is None:
            existing = MongoClient('localhost',27017)
            __external_clients__.set('MONGO',"todo_versioning",existing)
        return existing
        

# print("hello world")
# #sde_client = SDE.get()
# esi_client = ESI.get()
# print(__mk_key__("hello","world","sup","reid"))
# market_groups = esi_client.Market.get_markets_groups().result()
# print(market_groups[1].headers['Expires'])
# print("'%s'" %(market_groups[1]))
# print(market_groups[1].headers)
# # sde_client = SwaggerCLient.from_url("https://evekit-sde.orbital
