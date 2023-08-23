# This program will generate traffic for ACME Fitness Shop App. It simulates both Authenticated and Guest user scenarios. You can run this program either from Command line or from
# the web based UI. Refer to the "locust" documentation for further information. 
from time import sleep
from locust import HttpUser, task, SequentialTaskSet, between
import random
import logging

# List of users (pre-loaded into ACME Fitness shop)
users = ["phoebe"]

# GuestUserBrowsing simulates traffic for a Guest User (Not logged in)
class UserBrowsing(SequentialTaskSet):
    def on_start(self):
        self.getProducts()
    def listCatalogItems(self):
        products = []
        response = self.client.get("/products")
        if response.ok:
            items = response.json()["data"]
            for item in items:
                products.append(item["id"])
        return products
    def getProductDetails(self, id):
        details = {}
        response = self.client.get("/products/"+id)
        if response.ok:
            details = response.json()["data"]
            logging.debug("getProductDetails: " + str(details))
        return details
    def getProductImages(self,id):
        details = self.getProductDetails(id)
        if details:
            for x in range(1, 4):
                self.client.get(details["imageUrl"+str(x)])
    def getProductName(self, id):
        name = ""
        details = self.getProductDetails(id)
        if details:
            name = details["name"]
        logging.debug("NAME: "+name+ " for id: "+id)
        return name

    @task
    def getProducts(self):
        logging.debug("User - Get Products")
        self.client.get("/products")
    @task(2)
    def getProduct(self):
        logging.debug("User - Get a product")
        products = self.listCatalogItems()
        id = random.choice(products)
        response = self.client.get("/products/"+ id)
        if response.ok:
            product = response.json()
            logging.debug("Product info - " +  str(product))
    @task
    def getImages(self):
        logging.debug("User - Get images of random product")
        products = self.listCatalogItems()
        id = random.choice(products)
        self.getProductImages(id)
    @task(2)
    def index(self):
        self.client.get("/")

# AuthUserBrowsing simulates traffic for Authenticated Users (Logged in)
class AuthUserBrowsing(UserBrowsing):
    Order_Info = { "userid":"8888",
                "firstname":"Eric",
                "lastname": "Cartman",
                "address":{
                    "street":"20 Riding Lane Av",
                    "city":"San Francisco",
                    "zip":"10201",
                    "state": "CA",
                    "country":"USA"},
                "email":"jblaze@marvel.com",
                "delivery":"UPS/FEDEX",
                "card":{
                    "type":"amex/visa/mastercard/bahubali",
                    "number":"349834797981", 
                    "expMonth":"12",
                    "expYear": "2030",
                    "ccv":"123"
                },
                "cart":[
                    {"id":"1234", "description":"redpants", "quantity":"1", "price":"4"},
                    {"id":"5678", "description":"bluepants", "quantity":"1", "price":"4"}
                ],
                "total":"100"}

    def on_start(self):
        self.login()
    def removeProductFromCart(self, userid, productid):
        response = self.client.post("/cart/item/modify/"+userid, json={"itemid": productid, "quantity": 0})
        if response.ok:
            logging.debug("Auth User - Removed item: "+productid+" for user: "+userid)
        else:
            logging.warning("failed to remove cart entry. item: "+productid+" for user: "+userid)

    @task
    def login(self):
        user = random.choice(users)
        logging.debug("Auth User - Login user " + user)
        response = self.client.post("/acme-login/", json={"username": user, "password":"vmware1!"})
        if response.ok:
            body = response.json()
            self.user.userid = body["token"]
    @task(2)
    def addToCart(self):
        products = self.listCatalogItems()
        productid = random.choice(products)
        if not self.user.userid:
            logging.warning("Not logged in, skipping 'Add to Cart'")
            return
        logging.debug("Add to Cart for user " + self.user.userid)
        details = self.getProductDetails(productid)
        cart = self.client.post("/cart/item/add/" + self.user.userid, json={
                  "name": details["name"],
                  "price": details["price"],
                  "shortDescription": "Test add to cart",
                  "quantity": random.randint(1,2),
                  "itemid": productid
                })
    @task
    def removeFromCart(self):
        products = self.listCatalogItems()
        productid = random.choice(products)
        self.removeProductFromCart(self.user.userid, productid)
    @task
    def checkout(self):
        if not self.user.userid:
            logging.warning("Not logged in, skipping 'Add to Checkout'")
            return
        userCart = self.client.get("/cart/items/" + self.user.userid).json()
        order = self.client.post("/order/add/"+ self.user.userid, json=self.Order_Info)
class UserBehavior(SequentialTaskSet):
    tasks = [AuthUserBrowsing, UserBrowsing]
class WebSiteUser(HttpUser):
    sleep(3)
    tasks = [UserBehavior]
    userid = ""
    wait_time = between(0.5, 3)
