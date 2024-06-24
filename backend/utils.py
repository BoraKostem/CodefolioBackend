from pymongo import MongoClient
import os
def get_db_handle(db_name, host, port, username, password):

 client = MongoClient(host= os.getenv('MONGO_HOST'),
                      port=int(os.getenv('MONGO_PORT')),
                      username= os.getenv('MONGO_USER'),
                      password= os.getenv('MONGO_PASS'),
                     )
 db_handle = client['codefolio']
 return db_handle, client