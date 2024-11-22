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
    for item_id, item in data["itemList"].items():
        # Download image
        imagePath = download_image(item["image"]["url"])
        (imagePath, imWidth, imHeight)=resize_and_save_image(imagePath, imagePath,target_height=int((height-pageHeader*3-lspace)/2) )
        image = ImageReader(imagePath)
        index+=1
        can.setFont("Helvetica-Bold", 13)
        titleStr= f"{index}. {item['label']} | {item['weight']}g | Karad :{item['karad']} | Size :{item['size']} | {item['note']}"
        
        titleStr += item['T2']['detail']['note'] if 'T2'in item and 'detail' in item['T2'] and 'note' in item['T2']['detail'] else ''
        lHeight=VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                         fillColor=white,fontColor=black, fillHeight=lspace, heightOnly=True )  
       
        l-=lHeight
        VCenteredBoxText(can, tx, l, paperWidth,lspace,titleStr,
                          fillColor=white,fontColor=black, fillHeight=lHeight )
        l-=lspace/2
        # Draw the image
        l-=imHeight
        tx=(paperWidth-imWidth)/2   
        can.drawImage(image, tx, l, width=imWidth, height=imHeight)
        tx=txStart
        l-=lspace
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

# Generate the PDF
if __name__ == "__main__":  
    data = {
            "balance": 668,
            "comment": "Fgbvvg",
            "date": "2024-11-17",
            "invoiceSN": "Vg",
            "isAvailableCredit": False,
            "issuedUID": "MP-02-2022-01-04-GOLDTEST100",
            "issuedby": "GOLDTEST100",
            "itemList": {
                "2024@11@17@01@49@36@555": {
                    "id": "2024@11@17@01@49@36@555",
                    "image": {
                        "dirWithoutFirmID": "Order/2024-11-17 01:49:58_698.jpeg",
                        "url": "https://firebasestorage.googleapis.com/v0/b/aidrevs-test.appspot.com/o/MP-GOLD-2021-11-02%2FOrder%2F2024-11-17%2001%3A49%3A58_698.jpeg?alt=media&token=71839feb-f35d-48d7-ad63-143a8775bac3"
                    },
                    "karad": "22",
                    "label": "Gggg, Gggg Gggg, Gggg Gggg, Gggg Gggg, Gggg Gggg, Gggg Gggg, Gggg",
                    "note": "Qdf",
                    "quantity": 1,
                    "size": "Wff",
                    "unit": "g",
                    "unitPrice": "1234",
                    "weight": "1266.000"
                },
            },
            "name": "Rav",
        }  
    print(GoldSmithSharePDF(data))

