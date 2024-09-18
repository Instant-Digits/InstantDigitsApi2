from pymongo import MongoClient



db_name = 'instantDigitsDBTest'

if(input("do Your want to delete this DB (y/n)?"+db_name)!='y'):
	exit() 
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/'+db_name)

# Select the database you want to delete
#db_name = 'yourDatabaseName'

# Drop the database
client.drop_database(db_name)

print(f"Database '{db_name}' deleted successfully.")
