#Saghana Report Generators

# main.py in read folder
import sys
import os
from datetime import datetime
import calendar
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, red,black,white, green, gray, lightgrey, lightslategray, wheat, maroon
import os
from reportlab.pdfbase import pdfmetrics


# Add the gold folder to the Python path
# Dynamically set the path to MangoDB directory
base_dir = os.path.dirname(os.path.abspath(__file__))
mango_db_dir = os.path.join(base_dir, '..', 'MangoDB')
sys.path.insert(0, mango_db_dir)
from dbOperations import queryADocs 

firmID='SUK-GOLD-2022-09-16'

#Read The data from DB
def ReadGoldSavingData(firmID):
    data = queryADocs({
        'collectionID':firmID+'_Receipts',
            'filters':{
                'type':{"$in":['Paid_GoldSaving', 'Redemption_GoldSaving']}
            }})
    if (data['status']):
        return(data['data'])
    return []


def getCurrentMonth():
    return datetime.now().strftime('%b-%y')


def compareDates(refMonth, month):
    # Convert the date strings to datetime objects
    refMonth = datetime.strptime(refMonth, '%b-%y')
    month = datetime.strptime(month, '%b-%y')
    
    # Compare the dates
    if refMonth < month:
        return 1
    elif refMonth > month:
        return -1
    else:
        return 0

def list15Months(inputDateStr):
    startDate = datetime.strptime(inputDateStr, '%B-%Y')
    monthsList = []
    currentDate = startDate

    for _ in range(15):  # Generate 15 months
        monthsList.append(currentDate.strftime('%b-%y'))
        nextMonth = currentDate.month + 1
        if nextMonth > 12:  # If December, go to January of next year
            currentDate = currentDate.replace(year=currentDate.year + 1, month=1)
        else:
            currentDate = currentDate.replace(month=nextMonth)

    return monthsList

def outRageDateAdjust(date): #Tx date adjustment which out of months
    year, month, day = map(int, date.split('-'))
    last_day_of_month = calendar.monthrange(year, month)[1]
    
    if day > last_day_of_month:
        day = last_day_of_month
    
    tx_date = datetime(year, month, day)
    return tx_date.strftime('%Y-%m-%d')

def sortTransactionsByDate(transactions):
    return sorted(transactions, key=lambda x: datetime.strptime(x['txDate'], '%Y-%m-%d'))
  
def convertTxDateToShortFormat(date, short=True):
    try:        
        tx_date =datetime.strptime(date, '%Y-%m-%d')
        
        if short:
            return tx_date.strftime('%b-%y')  # Format: Jan-24
        else:
            return tx_date.strftime('%B-%Y')  # Format: January-2024
    
    except ValueError as e:
        print(f"Error converting date: {date}, {e}")
        return None

def monthDifference(startMonthStr, endMonthStr):
    startDate = datetime.strptime(startMonthStr, '%B-%Y')
    endDate = datetime.strptime(endMonthStr, '%B-%Y')
    
    monthDiff = (endDate.year - startDate.year) * 12 + endDate.month - startDate.month
    return monthDiff

def GetFormatedDatas(firmID):
    data= ReadGoldSavingData(firmID)

    customerDict={}       
    for reg in data:
        if 'nameRef' not in reg:
            continue
        if reg['type']=='trash':
            continue
        # print(reg)
        if reg['nameID'] not in customerDict :
            customerDict[reg['nameID']]= {
                'name':reg['name'].title()+' ('+reg['nameRef']+')',
                'nameRef':reg['nameRef'],
                'regs':[],
                'redeems':[]            
            }
        reg['txDate']=outRageDateAdjust(reg['txDate']) #31 on feb
        reg.update({'txDateMonth': convertTxDateToShortFormat(reg['txDate'])})
        if reg['type']=='Paid_GoldSaving':
            customerDict[reg['nameID']]['regs'].append(reg)
        else:
            customerDict[reg['nameID']]['redeems'].append(reg)

    joinedMonthDict={}
    for (id, details) in customerDict.items():
        customerDict[id]['regs']=sortTransactionsByDate(details['regs'])
        totalPaid=0
        totalRedeem=0
        for x in customerDict[id]['regs']:
            totalPaid+=x['payAmount']
            txDateMonth = convertTxDateToShortFormat(x['txDate'], short=True)
            if txDateMonth not in customerDict[id]:
                customerDict[id][txDateMonth]=0

            customerDict[id][txDateMonth]+=x['payAmount']

            # print(x)
        for x in customerDict[id]['redeems']:
            totalRedeem+=x['payAmount']


        first = customerDict[id]['regs'][0]
        last =  customerDict[id]['regs'][-1]

        customerDict[id]['joinedDate']=first['txDate']
        customerDict[id]['lastPaid'] = last['txDate']
        customerDict[id]['totalPaid'] = totalPaid
        customerDict[id]['totalRedeem'] = totalRedeem

        joinedMonth=convertTxDateToShortFormat(first['txDate'], short=False)
        if joinedMonth  not in joinedMonthDict:
            joinedMonthDict[joinedMonth]=[]

        joinedMonthDict[joinedMonth].append(id) #months : customer id


    def sortDateKeys(keys):
        return sorted(keys, key=lambda x: datetime.strptime(x, '%B-%Y'))

    joinedMonthDict = {key :joinedMonthDict[key] for key in sortDateKeys(joinedMonthDict.keys())}
    
    summary=[]
    joinedCustomer = []
    for (month, cusIdList) in joinedMonthDict.items():
        if(len(summary)>0):
            lastMonth = summary[-1]
            summary.append(
                {'month':month,
                'joinedCus':len(cusIdList),
                'totalCus':lastMonth['totalCus']+len(cusIdList),
                'monthPaid':0,
                'notPaidCus':0,
                'totalPaid':lastMonth['totalPaid']})

        else:
            summary=[{
                'month':month,
                'joinedCus':len(cusIdList),
                'totalCus':len(cusIdList),
                'monthPaid':0,
                'notPaidCus':0,
                'totalPaid':0,
            }]
        monthPaid=0
        notPaidCus=0
        joinedCustomer+=cusIdList

        for id in joinedCustomer:
            regsMonth = [ reg for reg in customerDict[id]['regs'] if convertTxDateToShortFormat(reg['txDate'], short=False)==month]
            if (len(regsMonth)>0):
                for x in regsMonth:
                   monthPaid+=x['payAmount'] 
            elif (monthDifference(convertTxDateToShortFormat(customerDict[id]['joinedDate'], short=False), month)<=15):
                notPaidCus+=1
        summary[-1].update({'monthPaid':monthPaid,
                'notPaidCus':notPaidCus,
                'totalPaid':summary[-1]['totalPaid']+monthPaid})
  
    joinedMonthDict = {key :joinedMonthDict[key] for key in sortDateKeys(joinedMonthDict.keys())[::-1] }
    
    return [joinedMonthDict, customerDict, summary]



#------------------------------------------------------------------------------------------------------------
#report gerenation
if not os.path.exists('outputs'):
    os.makedirs('outputs')


def formatCurrencyNew(amount):
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Invalid input: amount must be a number or a string representing a number.")
    amount=round(amount, 2)
    if not isinstance(amount, (float, int)):
        raise TypeError("Invalid input type: amount must be a float, int, or string representing a number.")
    formatted_amount = "{:,.2f}".format(amount)
    return formatted_amount

def VCenteredBoxText(can, x, y, width, height, string, padding=3, align='left', 
                     heightOnly=False, fillColor=False, fillHeight=False, fontColor=black):

    font=(can._fontname, can._fontsize)
    strLenth = can.stringWidth(string[0] if type(string)==list else string, font[0], font[1])
    face = pdfmetrics.getFont(font[0]).face
    strH = (face.ascent - face.descent) / 1000 *  font[1]*0.85

    def BoxLines(width):
        if(strLenth<width):
            return [string]

        words = string.split()
        boxList=[]
        strStart=''
               
        for word in words:
            if  len(strStart)==0 or (can.stringWidth(strStart+word,font[0], font[1])<width):
                strStart=strStart+word+' '
            else:
                boxList.append(strStart)
                strStart=word+' '
        if (len(boxList)==0 or boxList[-1]!=strStart):
            boxList.append(strStart)
        return boxList
    
    if(width<5):#srtight line
        can.drawString(x+padding, y+(height-strH)/2,string)
        return height

    
    strLines = string if type(string)==list else BoxLines(width-padding)

    if(heightOnly):
        return len(strLines)*height

    if(fillColor):
        can.setFillColor(fillColor) 
        can.setStrokeColor(fillColor) 
        can.rect(x,y,width,(fillHeight or len(strLines)*height), stroke=0, fill=True)
        can.setFillColor(black)
    
    if(fontColor):
        can.setFillColor(fontColor)

    verticalPadding = ((fillHeight if fillHeight and fillHeight>len(strLines)*height else  height)-strH)/2
    y=len(strLines)*height+y
    for line in strLines:
        y=y-height
        strLenth = can.stringWidth(line,font[0], font[1])
        if(align=='right'):
            can.drawRightString(x+width-padding, y+verticalPadding,line)
        elif (align=='center'):
            padding=(width-strLenth)/2
            can.drawString(x+padding, y+verticalPadding,line)
        else:
            can.drawString(x+padding, y+verticalPadding,line)
        
    can.setFillColor(black)
    return len(strLines)*height


def createHeader(can,l, table, paperWidth, lspace, txStart, fillHeight=False, fillColor=False, fontColor=False):
    tx = txStart  # Initialize tx for header
    fillColor = fillColor or Color(225/255, 225/255, 225/255, alpha=1)
    can.setFont("Helvetica-Bold", 12)
    for head in table:
        width = paperWidth * 0.01 * head['width']
        VCenteredBoxText(can, tx, l, width, lspace, head['title'], align='center', fillColor=fillColor, fillHeight= fillHeight or lspace, fontColor=fontColor)
        tx += width

def GenerateGoldSavingReportPDF(firmID):    
    pdf_file= os.path.join('outputs','ReportPDF.pdf')
    [joinedMonthDict, customerDict, summary]=GetFormatedDatas(firmID)

    can = canvas.Canvas(pdf_file, pagesize=A4)
    txStart=20
   

    pageHeader=40
    footerHeight=pageHeader
    top=842-pageHeader 
    lspace=15
    l=top
    paperWidth=595-txStart*2

    tx=txStart
    lspace=11.5
    can.setFont("Helvetica", 9)

    currentMonth = getCurrentMonth()


    # summary page
    table = [
            {'title': 'Joined Month', 'width': 20, 'id': 'month', 'align':'left', 'isCurrency':False},
            {'title': 'New Customers', 'width': 20, 'id': 'joinedCus', 'align':'center', 'isCurrency':False},
            {'title': 'Total Customers', 'width': 20, 'id': 'totalCus', 'align':'center','isCurrency':False},
            {'title': 'Month Payment', 'width': 20, 'id': 'monthPaid', 'align':'right','isCurrency':True},
             {'title': 'Not Paid Customers', 'width': 20, 'id': 'notPaidCus', 'align':'center', 'isCurrency':False},
        ]
    #Header
    can.setFont("Helvetica-Bold", 10)

    VCenteredBoxText(can, tx*3, l,paperWidth,lspace,'Reported : '+datetime.now().strftime('%Y-%m-%d %I:%M %p')+' EDT', padding=tx*3, align='right' )
    can.setFont("Helvetica-Bold", 30)
    l=top*0.95
    lspace=40
    l-=lspace
    VCenteredBoxText(can, tx*3, l,paperWidth-tx*3,lspace,'The Gold Saving Summary', fontColor=maroon )
    lspace=20
    can.setFont("Helvetica-Bold", 10)
    l-=3*lspace
    createHeader(can,l, table, paperWidth, lspace, txStart, fillHeight=2*lspace , fillColor=lightslategray, fontColor=white)
    i=0            
    for monthSummary in summary[::-1]:
        i+=1
        fillColor = Color(225/255, 225/255, 225/255, alpha=1) if i%2 == 0 else white

        
        l-=lspace
        tx=txStart 
        for content in table:               
            width = paperWidth * 0.01 * content['width']                
            if ( content['id'] in monthSummary):
                can.setFont("Helvetica", 12)
                VCenteredBoxText(can, tx, l, width, lspace,
                                 formatCurrencyNew(monthSummary[content['id']]) if content['isCurrency'] else str(monthSummary[content['id']]), 
                                align=content['align'], fillColor=fillColor, fillHeight=lspace)
            tx+=width
    can.showPage()
    tx=txStart
    l=top

    for (joinedMonth, cusList) in joinedMonthDict.items():

        if(l<pageHeader):
            can.showPage()
            l=top


        lspace=18
        l-=lspace+5
        can.setFont("Helvetica-Bold", 12)
        VCenteredBoxText(can, tx, l,paperWidth,lspace,'    Joined in '+joinedMonth+'    Joined no of Customers : '+str(len(cusList)), fillColor=lightslategray,fontColor=white, fillHeight=lspace )  
        
        monthsList =list15Months(joinedMonth)
        monthsList=monthsList[:15]

        # Create the table
        table = [
            {'title': 'Name', 'width': 12, 'id': 'name', 'align':'left'}
        ] + [
            {'title': month.split('-')[0], 'width': 80 / len(monthsList), 'id': month, 'align':'center', 'isMonth' :True} 
            for month in monthsList
        ] + [
            {'title': 'Paid', 'width': 8, 'id': 'totalPaid', 'align':'center'}
        ]

        #Header
        lspace=15
        can.setFont("Helvetica-Bold", 10)
        l-=lspace
        createHeader(can,l, table, paperWidth, lspace, txStart)
        i=0
        for id in cusList:

            if(l<pageHeader):
                can.showPage()
                l=top
                l-=lspace
                i=0
                createHeader(can,l, table, paperWidth, lspace, txStart)

            customer= customerDict[id]
            i+=1
            fillColor = Color(225/255, 225/255, 225/255, alpha=1) if i%2 == 0 else white

            width = paperWidth * 0.01 * table[0]['width'] 
            height =VCenteredBoxText(can, tx, l, width, lspace,str(customer['name']),heightOnly=True, 
                                     fillHeight=lspace)
            l-=height
            tx=txStart 
            for content in table:               
                width = paperWidth * 0.01 * content['width']                
                if ( content['id'] in customer):
                    can.setFont("Helvetica", 12)
                    VCenteredBoxText(can, tx, l, width, lspace,str(customer[content['id']]) , 
                                    align=content['align'], fillColor=fillColor, fillHeight=height)
                elif compareDates(currentMonth,content['id'] )<=0:
                    # print(content['id'] ,currentMonth)
                    can.setFont("Helvetica-Bold", 12)
                    VCenteredBoxText(can, tx, l, width, lspace,'X' , 
                                    align=content['align'],fontColor=red, fillColor=fillColor, fillHeight=height)
                else:
                     VCenteredBoxText(can, tx, l, width, lspace,'' , 
                                    align=content['align'],fontColor=red, fillColor=fillColor, fillHeight=height)

                tx+= width
            tx=txStart
    can.save()   
    return {'status':True,'file':pdf_file}

if __name__ == "__main__":
    file = GenerateGoldSavingReportPDF(firmID)
    
