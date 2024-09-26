import os
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode

def GenerateShinolQRPDF(data, name, address='', output_dir='outputs'):
    # Get the absolute path of the output directory
    output_dir = os.path.abspath(output_dir)
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Define file paths
    pdf_file = os.path.join(output_dir, 'ShinolQR.pdf')
    image_file = os.path.join(output_dir, 'shinol.png')

    # Create the PDF canvas
    can = canvas.Canvas(pdf_file)

    # Generate the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=60,
        border=1,
    )
   
    qr.add_data(data)
    qr.make(fit=True)

    # Save the QR code image
    img = qr.make_image(fill_color="#000041", back_color="white")
    img.save(image_file)

    # Read the image for insertion into the PDF
    reader = ImageReader(image_file)
    
    # Add text and image to the PDF
    can.setFont("Times-Roman", 18)
    can.drawString(150, 760, name)
    can.setFont("Times-Roman", 13)
    can.drawString(150, 745, address)
    can.drawImage(reader, 150, 370, 300, 300)
    can.save()

    return pdf_file

# # Example usage
# pdf_path = GenerateShinolQRPDF('Shagananan', "SITE: INSTANT DIGITS")
# print(f"PDF saved at: {pdf_path}")
