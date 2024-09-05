from pymongo import MongoClient, ASCENDING, DESCENDING, errors


# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/instantDigitsDB')
db = client['instantDigitsDB']

def checkMongoConnection(uri="mongodb://localhost:27017/"):
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)  # 5 seconds timeout
        client.admin.command('ping')  # Ping the server
        print("MongoDB is running.")
        return True
    except errors.ServerSelectionTimeoutError:
        print("MongoDB is not reachable.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Helper function to validate parameters
def validateParams(params, requiredKeys):
    missingKeys = [key for key in requiredKeys if key not in params]
    if missingKeys:
        return f"Missing parameters: {', '.join(missingKeys)}"
    return None

def updateDoc(data):        
    errorMessage = validateParams(data, ['collectionID', 'documentID', 'data'])
    if errorMessage:
        return {"status": False, "mes": errorMessage}
    
    collectionId = data.get('collectionID')
    documentId = data.get('documentID')
    documentData = data.get('data')
    
    collection = db[collectionId]
    try:
        result = collection.update_one(
            {"_id": documentId},
            {"$set": documentData},
            upsert=True
        )
        if result.upserted_id:
            return {"status": True, "mes": "Document inserted successfully"}
        else:
            return {"status": True, "mes": "Document updated successfully"}
    except Exception as e:
        return {"status": False, "mes": str(e)}
    

def deleteADoc(data):        
    errorMessage = validateParams(data, ['collectionID', 'documentID'])
    if errorMessage:
        return {"status": False, "mes": errorMessage}
    
    collectionId = data.get('collectionID')
    documentId = data.get('documentID')
    collection = db[collectionId]
    try:
        result = collection.delete_one({"_id": documentId})
        if result.deleted_count > 0:
            return {"status": True, "mes": "Document deleted successfully"}
        else:
            return {"status": False, "mes": "Document not found"}
    except Exception as e:
        return {"status": False, "mes": str(e)}
    

def getADoc(data):
    collectionId = data.get('collectionID')
    documentId = data.get('documentID')
    
    if not collectionId:
        return {"status": False, "mes": "Missing parameter: collectionID"}
    if not documentId:
        return {"status": False, "mes": "Missing parameter: documentID"}
    
    collection = db[collectionId]
    try:
        document = collection.find_one({"_id": documentId})
        if document:
            return {"status": True, "mes": "Document retrieved successfully", "data": document}
        else:
            return {"status": False, "mes": "Document not found"}
    except Exception as e:
        return {"status": False, "mes": str(e)}
    


def queryADocs(data):
    collectionId = data.get('collectionID')    
    if not collectionId:
        return {"status": False, "mes": "Missing parameter: collectionID"}
    filters = data.get('filters', {})
    fields = data.get('fields', {})
    orderBy = data.get('orderBy', '')
    limit = data.get('limit', 0)  # Add support for limit (pagination)
    filters['type'] =filters['type'] if 'type' in filters else { "$ne": 'Trash' }
    
    try:
        sort = []
        if orderBy:
            orderBy = orderBy.split(',')
            for sortField in orderBy:
                try:
                    field, direction = sortField.split(':')
                    sort.append((field, ASCENDING if direction.lower() == 'asc' else DESCENDING))
                except ValueError:
                    return {"status": False, "mes": f"Invalid orderBy format: {sortField}"}

        collection = db[collectionId]
        cursor = collection.find(filters, fields)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit:
            cursor = cursor.limit(limit)
        documents = list(cursor)
        return {"status": True, "mes": "Documents retrieved successfully", "data": documents}
    except Exception as e:
        return {"status": False, "mes": str(e)}