
from .dbSecialOperation import getSpecificCustomer

def taskDivider(data, dbOperations):
    out={'status':False, 'mes':'IntelliGold Subserver Not Running'}
    try : 
        if(data['jobtype']=='customerSummary'):
            
            out = getSpecificCustomer(data['collectionID'], data['customerID'], dbOperations)
    
        return out
    except Exception as e:
        print(e)
        return {'status':False, 'mes':'Thats an Error in server, Pls try Again!' }


