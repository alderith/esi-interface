import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import bravado
import Client
import logging
import sys
import pymongo
import time
import itertools
import json
import datetime
#from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)

class MarketUpdater():
    region = None
    client = None
    mongo_client = None
    def __init__(self,region='10000002'):
#        self.client = Client.ESI.get() # this is actually bravado
        self.client = Client.ESIPY.get()
        self.app = Client.ESIPYAPP.get()
        self.mongo_client = Client.MONGO.get()

    def send_query(self,query,max_retry=5): #default to 20 attempts
        result_valid = False
        result = None
        attempt = 0
        while(not result_valid and max_retry > attempt):
            attempt+=1
            try:
                # #This is the BRAVADO way
                # result = query
                result = self.client.request(query)
                if(result._Response__status == 200):                    
                    print("OK")
                    result_valid = True
                else:
                    print("BAD DATA")
                    result = None
                    continue
            except Exception as ex:
                print("error. Retrying. Error msg: %s" % (ex))
                time.sleep(1)
        return result            


    def query_market_groups(self):
        results = self.send_query(self.client.Market.get_markets_groups(user_agent=Client.user_agent).result(),1)
        print(results)
        
    def query_a_page(self,page=1,region='10000002'):
        print("Page: %d Region: %s" % (page,region))
        # This is the BRAVADO way:
#        results = self.send_query(self.client.Market.get_markets_region_id_orders(order_type="all",region_id=region,page=page,user_agent=Client.user_agent).result())
        query = self.app.op['get_markets_region_id_orders'](
            order_type="all",
            region_id=region,
            page=page
        )

        results = self.send_query(query)
        return results

    def query_all_pages(self,prev_data_expire_date,region='10000002'):
        results = []
        page_data = self.query_a_page(1,region)
        data = json.loads(page_data.raw) 
        page_count = int(page_data.header['X-Pages'][0])
        results.append([data,page_data.header])
        expire_date = datetime.datetime.strptime(page_data.header['Expires'][0],"%a, %d %b %Y %H:%M:%S %Z")
        if(prev_data_expire_date is None or prev_data_expire_date < expire_date):
            pass
            with ThreadPoolExecutor(max_workers=10)  as pool:
                for result in pool.map(self.query_a_page, range(2,page_count+1),itertools.repeat(region)):
                    data = json.loads(result.raw)
                    results.append([data,result.header])
        else:
            print("previous data is expired!")
            return None
        print(len(results))
        count = 0
        for item in results:
            count += len(item[0])
        # print("Total items: %d" % count)
        # print("Total pages: %d" % len(results))
        expire_date = datetime.datetime.strptime(results[0][1]['Expires'][0],"%a, %d %b %Y %H:%M:%S %Z")
        return results
    
    def update_market_for_region(self,prev_data_expire_date,region='10000002',update_db=True):
        query_time = datetime.datetime.utcnow()
        print("Querying Region %s" % region)
        results = self.query_all_pages(prev_data_expire_date,region)
        data = []
        if results is not None:
            for result in results:
#                print(result[1])
                for order in result[0]:
                      order['issued'] = datetime.datetime.strptime(order['issued'],"%Y-%m-%dT%H:%M:%SZ")
                      order['esi_update_time'] = datetime.datetime.strptime(result[1]['Last-Modified'][0],"%a, %d %b %Y %H:%M:%S %Z")
                      order['query_time'] = query_time
                      order['region_id'] = int(region)
                      order['esi_expire_time'] = datetime.datetime.strptime(result[1]['Expires'][0],"%a, %d %b %Y %H:%M:%S %Z")
                      data.append(order)
        print("About to insert %d items to DB" % len(data))
        db = self.mongo_client.eve_data
        if(len(data) > 0):
            db.market_data.insert_many(data)
        else:
            data = [{'esi_expire_time': datetime.datetime.strptime(results[0][1]['Expires'][0],"%a, %d %b %Y %H:%M:%S %Z")}]
        return data
            
                      
                      
    def main(self):
#        regions=['10000001','10000004']
        regions = ['10000001',   '10000002',   '10000003',   '10000004',   '10000005',   '10000006',   '10000007',   '10000008',   '10000009',   '10000010',   '10000011',   '10000012',   '10000013',   '10000014',   '10000015',   '10000016',   '10000017',   '10000018',   '10000019',   '10000020',   '10000021',   '10000022',   '10000023',   '10000025',   '10000027',   '10000028',   '10000029',   '10000030',   '10000031',   '10000032',   '10000033',   '10000034',   '10000035',   '10000036',   '10000037',   '10000038',   '10000039',   '10000040',   '10000041',   '10000042',   '10000043',   '10000044',   '10000045',   '10000046',   '10000047',   '10000048',   '10000049',   '10000050',   '10000051',   '10000052',   '10000053',   '10000054',   '10000055',   '10000056',   '10000057',   '10000058',   '10000059',   '10000060',   '10000061',   '10000062',   '10000063',   '10000064',   '10000065',   '10000066',   '10000067',   '10000068',   '10000069',   '11000001',   '11000002',   '11000003',   '11000004',   '11000005',   '11000006',   '11000007',   '11000008',   '11000009',   '11000010',   '11000011',   '11000012',   '11000013',   '11000014',   '11000015',   '11000016',   '11000017',   '11000018',   '11000019',   '11000020',   '11000021',   '11000022',   '11000023',   '11000024',   '11000025',   '11000026',   '11000027',   '11000028',   '11000029',   '11000030',   '11000031',   '11000032',   '11000033']
        last_updated = {}
        while True:
            for region in regions:
                if(last_updated.get(region) is None):
                    last_updated[region] = datetime.datetime.utcnow() - datetime.timedelta(seconds=600)
                    data = self.update_market_for_region(last_updated[region],region)
                    last_updated[region] = data[0]['esi_expire_time'] + datetime.timedelta(seconds=60)
                    data = None
                else:
                    if(last_updated[region] < datetime.datetime.utcnow()):
                        data = self.update_market_for_region(last_updated[region],region)
                        last_updated[region] = data[0]['esi_expire_time'] + datetime.timedelta(seconds=60)
                        data = None
                    else:
                        print("%s: data expires in: %s" % (region,last_updated[region] - datetime.datetime.utcnow()))
                        
#            print(last_updated)
            time.sleep(2)
            print("looping...")
        

# Bravado test        
#     def thread_test(self):
# #        region = '10000030'
#         region = '10000002'
#         print(Client.user_agent)
#         results = []
#         page_data = self.query_a_page(1,region)
#         print(len(page_data[0]))
#         print(page_data[1].headers)
#         page_count = int(page_data[1].headers['X-Pages'])
#         results.append(page_data)
#         with ThreadPoolExecutor(max_workers=10)  as pool:
#             for result in pool.map(self.query_a_page, range(2,page_count+1),itertools.repeat(region)):
#                 results.append(result)
#         print(len(results))
#         count = 0
#         for item in results:
#             print(item[1].headers['Last-Modified'])
#             count += len(item[0])
#             print(len(item[0]))
#         print("Total items: %d" % count)


updater = MarketUpdater()

print(".............")

#updater.send_query(self.client.Market.get_markets_groups().result(),"world?")
#updater.query_market_groups()

updater.main()
#updater.update_market_for_region(None)
#updater.thread_test)
#updater.esipy_thread_test()
