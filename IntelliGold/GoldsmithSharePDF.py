import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color, red,black,white, green, blue, lightgrey, lightslategray, wheat, maroon
import os
from reportlab.pdfbase import pdfmetrics
from PIL import Image
# Input data



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
    return "{:,.2f}".format(amount)

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

def download_image(image_url, save_path="outputs/temp_image.jpg"):
    """Downloads the image from a URL."""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            file.write(response.content)
        return save_path
    raise Exception(f"Failed to download image. Status code: {response.status_code}")


def resize_and_save_image(imagePath, output_path, target_width=None, target_height=None):
    if not target_width and not target_height:
        raise ValueError("Either target_width or target_height must be provided.")

    with Image.open(imagePath) as img:
        original_width, original_height = img.size

        if target_width:
            # Calculate new height while maintaining aspect ratio
            scale = target_width / original_width
            new_width = target_width
            new_height = int(original_height * scale)
        elif target_height:
            # Calculate new width while maintaining aspect ratio
            scale = target_height / original_height
            new_width = int(original_width * scale)
            new_height = target_height

        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)

        # Save the resized image
        resized_img.save(output_path)

    return (output_path, new_width, new_height)

def GoldSmithSharePDF(data):
    """Generates a PDF with each item's image and description."""
    pdf_file= os.path.join('outputs','GoldSmithShare.pdf')
    can = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    pageHeader=40
    footerHeight=pageHeader    
    
    l=height-pageHeader
    txStart=20
    paperWidth=width-txStart*2

    tx=txStart
    lspace=15
    data['firmName']=data['firmName'] if 'firmName' in data else 'Saghana Jewels'
    
    
    #gold smith task
    taskDate = data['track'][len(data['track'])-1]['timeStamp'].split(' ')[0] if  'track' in data and len(data['track'])>0 else data['date']
    can.setFont("Helvetica-Bold", 13)    
    VCenteredBoxText(can, tx,height- lspace*2, paperWidth,lspace,data['firmName'].upper()+'  Order No. : '+data['invoiceSN'] +'  Shared on : '+taskDate, 
                            align='center',fontColor=maroon)
    can.setFont("Helvetica-Bold", 8)
    VCenteredBoxText(can, tx,lspace, paperWidth,lspace, 'www.instantdigits.com', 
                     align='right',fontColor=blue)
    # Iterate through itemList
    index=0
    data['track'] = data['track'] if 'track' in data else False
    for item_id, item in data["itemList"].items():
        # Download image

        isImageAvailable = 'image' in item and item["image"] and  "url" in item["image"]
        
        index+=1
        can.setFont("Helvetica", 13)
        titleStr= f"{index}. {item['label']} | {item['weight']}g | Karad :{item['karad']}"
        titleStr += f" | Size :{item['size']}" if 'size' in item and item['size']  else ''

        titleStr += f" | {item['note']}" if 'note' in item else ''
        
        titleStr +=(' | '+data['track'][-1]['detail']['note']) if  data['track'] else ''
       

        titleStr += (' | '+item['T2']['detail']['note']) if not data['track'] and 'T2'in item and 'detail' in item['T2'] and 'note' in item['T2']['detail'] else ''
        
        titleStr += '' if isImageAvailable else ' | No Image!'
        
        lspace=18
        lHeight=VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                         fillColor=white,fontColor=black, fillHeight=lspace, heightOnly=True )  

        l-=lHeight
        VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                          fillColor=white,fontColor=black, fillHeight=lHeight )
        

        if isImageAvailable:
            # l-=lspace/3
            imagePath = download_image(item["image"]["url"])
            (imagePath, imWidth, imHeight)=resize_and_save_image(imagePath, imagePath,target_height=int((height-pageHeader*3-lspace)/2) )
            image = ImageReader(imagePath)        
            # Draw the image
            l-=imHeight
            tx=(paperWidth-imWidth)/2   
            can.drawImage(image, tx, l, width=imWidth, height=imHeight)
        else :
            imHeight=50
        tx=txStart
        l-=lspace/2
        if (l<imHeight and index <= (len(data["itemList"])-1)):
            can.showPage()
            l=height-pageHeader            
            tx=txStart
            lspace=15
            can.setFont("Helvetica-Bold", 13)    
            VCenteredBoxText(can, tx,height- lspace*2, paperWidth,lspace,data['firmName'].upper()+'  Order No. : '+data['invoiceSN'] +'  Shared on : '+taskDate, 
                            align='center',fontColor=maroon)
            can.setFont("Helvetica-Bold", 8)
            VCenteredBoxText(can, tx,lspace, paperWidth,lspace, 'www.instantdigits.com', 
                            align='right',fontColor=blue)
        
    
    can.save()
    return {'status':True,'file':pdf_file}

def OrderPDFExport(data):
    """Generates a PDF with each item's image and description."""
    pdf_file= os.path.join('outputs','OrderPDFExport.pdf')
    can = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    pageHeader=40
    footerHeight=pageHeader    
    
    l=height-pageHeader/2
    txStart=20
    paperWidth=width-txStart*2

    tx=txStart
    lspace=15
    data['firmName']=data['firmName'] if 'firmName' in data else 'Saghana Jewels'
    
    
    #gold smith task
    taskDate = data['track'][len(data['track'])-1]['timeStamp'].split(' ')[0] if  'track' in data and len(data['track'])>0 else data['date']
    can.setFont("Helvetica-Bold", 13)  
    l-=lspace  
    VCenteredBoxText(can, tx,l, paperWidth,lspace,data['firmName'].upper()+' ORDER NOTE', align='center',fontColor=maroon)
    can.setFont("Helvetica", 12)  

    l-=lspace*1.2
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Order No. : '+data['invoiceSN'], align='left',fontColor=maroon)

    tx+=paperWidth/3
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Order Date : '+data['date'], align='left',fontColor=maroon)

    tx+=paperWidth/3
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Created By : '+data['issuedby'].title(), align='left',fontColor=maroon)

    l-=lspace  
    tx=txStart
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Name : '+data['name'].title(), align='left',fontColor=maroon)

    tx+=paperWidth/3
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Delivery : '+data['txDate'], align='left',fontColor=maroon)

    tx+=paperWidth/3
    VCenteredBoxText(can, tx,l, paperWidth/3,lspace,'Total : '+formatCurrencyNew(data['total']+data['tax']), align='left',fontColor=maroon)

    
    if 'comment' in data and len(data['comment'])>0  :
        l-=lspace  
        tx=txStart
        VCenteredBoxText(can, tx,l, paperWidth/3,lspace,data['comment'], align='left',fontColor=maroon)

    tx=txStart
    can.setFont("Helvetica-Bold", 8)
    VCenteredBoxText(can, tx,lspace, paperWidth,lspace, 'www.instantdigits.com', 
                     align='right',fontColor=blue)
    # Iterate through itemList
    index=0
    l-=lspace*0.5
    for item_id, item in data["itemList"].items():
        # Download image

        isImageAvailable = 'image' in item and item["image"] and  "url" in item["image"]
        
        index+=1
        can.setFont("Helvetica", 13)
        titleStr= f"{index}. {item['label']} | {item['weight']}g | Karad :{item['karad']}"
        titleStr += f" | Size :{item['size']}" if 'size' in item and item['size']  else ''
        titleStr += f" | Price: {formatCurrencyNew(item['unitPrice'])}"
        

        titleStr += f" | {item['note']}" if 'note' in item else ''
       
        titleStr += '' if isImageAvailable else ' | No Image!'
        
        lspace=18
        lHeight=VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                         fillColor=white,fontColor=black, fillHeight=lspace, heightOnly=True )  

        l-=lHeight
        VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                          fillColor=white,fontColor=black, fillHeight=lHeight )
        

        if isImageAvailable:
            # l-=lspace/3
            imagePath = download_image(item["image"]["url"])
            (imagePath, imWidth, imHeight)=resize_and_save_image(imagePath, imagePath,target_height=int((height-pageHeader*3-lspace)/2.2) )
            image = ImageReader(imagePath)        
            # Draw the image
            l-=imHeight
            tx=(paperWidth-imWidth)/2   
            can.drawImage(image, tx, l, width=imWidth, height=imHeight)
        else :
            imHeight=50
        tx=txStart
        l-=lspace/2
        if (l<imHeight and index <= (len(data["itemList"])-1)):
            can.showPage()
            l=height-pageHeader            
            tx=txStart
            lspace=15
            can.setFont("Helvetica-Bold", 13)    
            VCenteredBoxText(can, tx,height- lspace*2, paperWidth,lspace,'Continued Page of Order No. : '+data['invoiceSN'], 
                            align='center',fontColor=maroon)
            can.setFont("Helvetica-Bold", 8)
            VCenteredBoxText(can, tx,lspace, paperWidth,lspace, 'www.instantdigits.com', 
                            align='right',fontColor=blue)
        
    
    can.save()
    return {'status':True,'file':pdf_file}



# Generate the PDF
if __name__ == "__main__":  
    data = {
  "balance": -3695,
#   "comment": "Good",
  "date": "2024-11-23",
  "invoiceSN": "987654",
  "isAvailableCredit": False,
  "issuedUID": "MP-02-2022-01-04-GOLDTEST100",
  "issuedby": "GOLDTEST100",
  "itemList": {
    "2024@11@23@11@45@02@127": {
      "id": "2024@11@23@11@45@02@127",
      "image": {
        "dirWithoutFirmID": "Order/2024-11-23 11:49:58_741.jpeg",
        "url": "https://firebasestorage.googleapis.com/v0/b/aidrevs-test.appspot.com/o/MP-GOLD-2021-11-02%2FOrder%2F2024-11-23%2011%3A49%3A58_741.jpeg?alt=media&token=432cc81d-cacf-4f55-8a82-7e5aa0e95c72"
      },
      "karad": "12",
      "label": "Kodi",
      "quantity": 1,
      "size": "46",
      "unit": "g",
      "unitPrice": "85",
      "weight": "28.000"
    },
    "2024@11@23@11@50@20@568": {
      "id": "2024@11@23@11@50@20@568",
      "image": {
        "dirWithoutFirmID": "Order/2024-11-23 11:50:43_154.jpeg",
        "url": "https://firebasestorage.googleapis.com/v0/b/aidrevs-test.appspot.com/o/MP-GOLD-2021-11-02%2FOrder%2F2024-11-23%2011%3A50%3A43_154.jpeg?alt=media&token=bca55788-a543-4add-a272-60e36cb7bd1b"
      },
      "karad": "25",
      "label": "Kodi",
      "quantity": 1,
      "size": "Shs",
      "unit": "g",
      "unitPrice": "454",
      "weight": "123.000"
    },
    "2024@12321@23@11@50@20@568": {
      "id": "2024@11@23@11@50@20@568",
      "image": {
        "dirWithoutFirmID": "Order/2024-11-23 11:50:43_154.jpeg",
        "url": "https://firebasestorage.googleapis.com/v0/b/aidrevs-test.appspot.com/o/MP-GOLD-2021-11-02%2FOrder%2F2024-11-23%2011%3A50%3A43_154.jpeg?alt=media&token=bca55788-a543-4add-a272-60e36cb7bd1b"
      },
      "karad": "25",
      "label": "Kodi",
      "quantity": 1,
      "unit": "g",
      "unitPrice": "454",
      "weight": "123.000"
    }
  },
  "itemNames": "Kodi,Kodi",
  "linkStamps": "",
  "name": "GOOD NAME",
  "nameAddress": "",
  "nameEmail": "",
  "nameID": "",
  "namePhone": "",
  "nameRef": "",
  "payAmount": 4234,
  "payMethods": [{ "type": "OrderPay", "label": "Order Pay", "amount": 4234 }],
  "purchase": False,
  "stockValueReduction": 0,
  "tax": 89.83,
  "taxHide": False,
  "taxPercentage": -20,
  "time": "11:51:06 am",
  "timeStamp": "2024-11-23 11:51:06_162",
  "total": 449.17,
  "txDate": "2024-11-30",
  "type": "Order_Processing",
  "track": [
    {
      "task": "Shared with GoldSmit",
      "timeStamp": "2024-11-23 11:51:39_763",
      "taskID": "T2",
      "isItemViseTask": True,
      "modal": "GoldSmithModal",
      "button": "Share with GoldSmit",
      "by": "GOLDTEST100",
      "detail": { "note": "Delivery Date : 2024-11-26, Fggg", "name": "Ggg" }
    }
  ],
  "jobtype": "goldSmithReport"
}
  
    print(GoldSmithSharePDF(data))

