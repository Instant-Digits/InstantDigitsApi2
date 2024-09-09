import json
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from MangoDB.backupUpload import uploadOrUpdateFile
from datetime import datetime

mongoUri = 'mongodb://localhost:27017/instantDigitsDB'
databaseName = 'instantDigitsDB'
outputFile = 'instantDigitsDB.json'

def get_current_timestamp():
    """Return the current date and time in YYYY-MM-DD HH:MM:SS format."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def backupMongodbToJson(mongoUri, databaseName, outputFile):
    try:
        client = MongoClient(mongoUri)
        db = client[databaseName]

        collections = db.list_collection_names()

        allData = {}

        # Iterate over each collection and compile the data
        for collectionName in collections:
            collection = db[collectionName]
            cursor = collection.find()
            data = list(cursor)

            # Add collection data to the dictionary
            allData[collectionName] = data

        # Write all data to a single JSON file
        with open(outputFile, 'w') as file:
            json.dump(allData, file, default=str, indent=4)

        print(f'[{get_current_timestamp()}] Backup completed! All collections have been exported to {outputFile}.')
        return True

    except PyMongoError as e:
        print(f'[{get_current_timestamp()}] An error occurred while accessing MongoDB: {e}')
        return False
    except IOError as e:
        print(f'[{get_current_timestamp()}] An error occurred while writing to file: {e}')
        return False
    except Exception as e:
        print(f'[{get_current_timestamp()}] An unexpected error occurred: {e}')
        return False

if __name__ == "__main__":
    try:
        # Perform the backup
        backup_success = backupMongodbToJson(mongoUri, databaseName, outputFile)
        
        if backup_success:
            try:
                # Upload the backup file if the backup was successful
                fileId = '11yTcMg33Gh_zQmTVNdozaZ3dvX3pe53A'
                uploadOrUpdateFile(outputFile, fileId=fileId)
                print(f'[{get_current_timestamp()}] File upload completed successfully.')
            except Exception as e:
                print(f'[{get_current_timestamp()}] An error occurred while uploading the file: {e}')
        else:
            print(f'[{get_current_timestamp()}] Backup was not successful. File upload was skipped.')
    
    except Exception as e:
        print(f'[{get_current_timestamp()}] An unexpected error occurred in the main execution: {e}')
