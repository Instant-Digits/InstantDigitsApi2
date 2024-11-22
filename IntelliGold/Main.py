
from .dbSecialOperation import getSpecificCustomer
from .SaghanaGoldSaving import GenerateGoldSavingReportPDF
from .GoldsmithSharePDF import GoldSmithSharePDF

def taskDivider(data, dbOperations):
    out={'status':False, 'mes':'IntelliGold Subserver Not Running'}
    try : 
        if(data['jobtype']=='customerSummary'):            
            out = getSpecificCustomer(data['collectionID'], data['customerID'], dbOperations)
        elif data['jobtype']=='goldSavingReport':
            out = GenerateGoldSavingReportPDF(data['firmID'])
        elif data['jobtype']=='goldSmithReport':
            out = GoldSmithSharePDF(data)

        return out
    except Exception as e:
        print(e)
        return {'status':False, 'mes':'Thats an Error in server, Pls try Again!' }




