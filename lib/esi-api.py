from esipy import App
from esipy import EsiClient
import sys
import pprint

class myApp:
    pp = pprint.PrettyPrinter(indent=2)
    app = None
    client = None

    def main(self):
        self.app = App.create(url="https://esi.tech.ccp.is/latest/swagger.json?datasource=tranquility")

        self.client = EsiClient(
            retry_requests=True,  # set to retry on http 5xx error (default False)
            header={'User-Agent': 'Jimmy - api test app:  alderith@gmail.com'},
            raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
        )

        self.get_user_info()
            
        # try:
        #     self.original_example()
        # except Exception as err:
        #     print "Error:: "
        #     print err
        #     e = sys.exc_info()[0]
        #     self.pp.pprint(e)

        # self.original_example()      
        # print "hello world"

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
    print "hello"
    my_app.main()
    print "world"
