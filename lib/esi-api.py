from esipy import App
from esipy import EsiClient
import sys
import pprint
import json

class myApp:
    pp = pprint.PrettyPrinter(indent=2)
    app = None
    client = None

    def main(self):
        print "setting up the app..."
        self.app = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")
        print "done. \n Setting up the client."

        self.client = EsiClient(
            retry_requests=True,  # set to retry on http 5xx error (default False)
            header={'User-Agent': 'Jimmy - api test app:  alderith@gmail.com'},
            raw_body_only=True,  # default False, set to True to never parse response and only return raw JSON string content.
        )
        print "done, after this it's all me and my calls."
        chars = ["alderith","gruxella","lord grapefruit","druzidelcastro"]

        try:
            # self.get_id_for_users(chars)
            # self.get_group_item_ids()
            self.get_orders_for_region(10000002)
        except Exception as err:
            self.pp.pprint(err)
#        self.get_user_info()
            
        # try:
        #     self.original_example()
        # except Exception as err:
        #     print "Error:: "
        #     print err
        #     e = sys.exc_info()[0]
        #     self.pp.pprint(e)

        # self.original_example()      
        # print "hello world"

    def get_orders_for_region(self,reg_id):
        count = 0;
        query = self.app.op['get_markets_region_id_orders'](
            order_type="all",
            region_id=reg_id,
            )
        response = self.client.request(query)
#        self.pp.pprint(response.raw)

        print "Attempting to parse json"
        data = json.loads(response.raw)
        print "done parsing json"
        print len(data)
#       self.pp.pprint(data)
#       return

        queries = []
        print "this dataset expires:"
        print response.header['Expires']
        print "we need this many pages:"
        size = response.header['X-Pages'][0]
        print size
        if(size > 1):
             for page in range(1,size+1):
#           for page in range(1,3):
                queries.append(
                    self.app.op['get_markets_region_id_orders'](
                        order_type="all",
                        region_id=reg_id,
                        page=page,
                    )
                )
        print "doing long request to CCP..."
#        results = self.client.multi_request(queries,None,None,size)
        results = self.client.multi_request(queries)
        print "done with long request"

        for result in results:
            # self.pp.pprint(result[1].header)
            # self.pp.pprint(result[1].data)
            data = json.loads(result[1].raw)
            count +=len(data)
            print "Running count = %d" %(count)
            print "is buy order? %r" % (data[0]['is_buy_order'])
            print "remaining volume: %d" % (data[0]['volume_remain'])

#       self.pp.pprint(results)
        print "Total orders = %d" % (count)
        return results
    

    def get_market_groups(self):
        query = self.app.op['get_markets_groups']()
        response = self.client.request(query)
        # self.pp.pprint(response.data)
        self.pp.pprint(response.header)
        print len(response.data)
        return response

    def get_group_item_ids(self):
        marketgroup_response = self.get_market_groups()
        groups = []
        count = 0
        for group in marketgroup_response.data:
            count+=1
            print group
            query = self.app.op['get_markets_groups_market_group_id'](
                market_group_id=group
            )
            response = self.client.request(query)
            groups.append(response.data)
            if count == 25:
                break
            # self.pp.pprint(response.data)
        self.pp.pprint(groups)

        
    def get_id_for_users(self,*user_array):
        users = []
        query = self.app.op['post_universe_ids'](
            names=user_array[0]
        )
        response = self.client.request(query)
        for char in response.data['characters']:
            print "%s id = %d" % (char['name'] ,char['id'])
        

    def get_user_info(self):
        query = self.app.op['post_universe_ids'](
            names=["Gruxella","Alderith"]
        )

        # query = self.app.op['get_characters_character_id'](
        #     character_id=712133937
        # )

        # query = self.app.op['get_characters_names'](
        #     character_ids=[712133937]
        # )
        response = self.client.request(query)
        print response.data

    def original_example(self):

        market_order_operation = self.app.op['get_markets_region_id_orders'](
            region_id=10000002,
            type_id=34,
            order_type='all',
        )

        # do the request
        print "did I get here? 2"
        response = self.client.request(market_order_operation)

        # use it: response.data contains the parsed result of the request.
        print response.data[0].price

        # to get the headers objects, you can get the header attribute
        print response.header
            

if __name__ == "__main__":
    my_app = myApp()
    my_app.main()
