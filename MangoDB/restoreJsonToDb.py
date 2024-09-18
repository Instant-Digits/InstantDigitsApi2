import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError

mongoUri = 'mongodb://localhost:27017/instantDigitsDB'
databaseName = 'instantDigitsDB'
inputFile = 'instantDigitsDB.json'

def restoreJsonToMongodb(mongoUri, databaseName, inputFile):
    try:
        # Connect to MongoDB
        client = MongoClient(mongoUri)
        db = client[databaseName]

        # Load data from the JSON file
        with open(inputFile, 'r') as file:
            allData = json.load(file)

        # Iterate over each collection and insert data
        for collectionName, data in allData.items():
            collection = db[collectionName]
            # Replace existing data or insert new data
            collection.drop()  # Optional: Drop collection if you want to replace existing data
            if data:
                collection.insert_many(data)
                print(f'Data for collection "{collectionName}" restored successfully.')
            else:
                print(f'No data found for collection "{collectionName}".')

        print(f'Data restoration completed successfully from {inputFile}.')
    
    except PyMongoError as e:
        print(f'An error occurred while accessing MongoDB: {e}')
    except IOError as e:
        print(f'An error occurred while reading the file: {e}')
    except json.JSONDecodeError as e:
        print(f'An error occurred while decoding JSON: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    restoreJsonToMongodb(mongoUri, databaseName, inputFile)
