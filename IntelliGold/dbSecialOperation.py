
# IntelliGold/dbSecialOperation.py

from .Functions import formatDateToMonthYear, findMissingMonths

def getSpecificCustomer(collectionID,customerID, dbOperations):
    receipts = dbOperations.queryADocs({
            'collectionID':collectionID,
            'filters':{
                'nameID':customerID
            }
        })
    receipts=receipts['data']
    paidMonths=[]
    out={'totalyPaid': 0,
    'balance': 0,
    'lastPaidFor': False,
    'lastPayementDate':False,
    'unPaidMonths': []}
    for receipt in receipts:
        if 'Redemption' in  receipt['type']:
            out['balance']-=receipt['payAmount']
        else:
            if(not out['lastPaidFor']):
                out['lastPaidFor']=formatDateToMonthYear(receipt['txDate'])
                out['lastPayementDate']=receipt['date']    
            out['totalyPaid']+=receipt['payAmount']
            paidMonths.append(receipt['txDate'])
            out['balance']+=receipt['payAmount']
    out['unPaidMonths']=findMissingMonths(paidMonths)
    return {'status':True, 'out':out}