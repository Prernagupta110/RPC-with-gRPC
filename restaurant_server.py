import grpc
from concurrent import futures
from proto import restaurant_pb2
from proto import restaurant_pb2_grpc
import sys

RESTAURANT_ITEMS_FOOD = ["chips", "fish", "burger", "pizza", "pasta", "salad"]
RESTAURANT_ITEMS_DRINK = ["water", "fizzy drink",
                          "juice", "smoothie", "coffee", "beer"]
RESTAURANT_ITEMS_DESSERT = ["ice cream", "chocolate cake",
                            "cheese cake", "brownie", "pancakes", "waffles"]


class Restaurant(restaurant_pb2_grpc.RestaurantServicer):
    def process_order(self, order_id, items, item_category):  # Add 'self' parameter here
        status = restaurant_pb2.RestaurantResponse.Status.ACCEPTED
        it = []

        for i in items:
            it.append(restaurant_pb2.items(itemName=i))

            if i not in item_category:
                status = restaurant_pb2.RestaurantResponse.Status.REJECTED

        return restaurant_pb2.RestaurantResponse(itemMessage=it, orderID=order_id, status=status)

    def FoodOrder(self, request, context):
        return self.process_order(request.orderID, request.items, RESTAURANT_ITEMS_FOOD)

    def DrinkOrder(self, request, context):
        return self.process_order(request.orderID, request.items, RESTAURANT_ITEMS_DRINK)

    def DessertOrder(self, request, context):
        return self.process_order(request.orderID, request.items, RESTAURANT_ITEMS_DESSERT)

    def MealOrder(self, request, context):
        meal_orderID = request.orderID
        items = request.items
        it = []

        if len(items) != 3:
            return self.create_rejected_response(items, meal_orderID)

        for i, item in enumerate(items):
            it.append(restaurant_pb2.items(itemName=item))
        
            if i == 0 and item not in RESTAURANT_ITEMS_FOOD or \
               i == 1 and item not in RESTAURANT_ITEMS_DRINK or \
               i == 2 and item not in RESTAURANT_ITEMS_DESSERT:
               return self.create_rejected_response(items, meal_orderID)

        return self.create_accepted_response(it, meal_orderID)

    def create_rejected_response(self, items, meal_orderID):
        it = [restaurant_pb2.items(itemName=i) for i in items]
        return restaurant_pb2.RestaurantResponse(
            itemMessage=it,
            orderID=meal_orderID,
            status=restaurant_pb2.RestaurantResponse.Status.REJECTED
    )

    def create_accepted_response(self, item_messages, meal_orderID):
        return restaurant_pb2.RestaurantResponse(
            itemMessage=item_messages,
            orderID=meal_orderID,
            status=restaurant_pb2.RestaurantResponse.Status.ACCEPTED
    )

def serve():   
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServicer_to_server(Restaurant(), server)  
    port= sys.argv[1]
    str = "localhost:{0}".format(port)
    server.add_insecure_port(str) 
    server.start() 
    server.wait_for_termination()
    # Logic goes here
    # Remember to start the server on localhost and a port defined by the first command line argument

if __name__ == '__main__':
    serve()



