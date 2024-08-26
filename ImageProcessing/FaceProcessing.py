import cv2
import face_recognition
from base64 import decodebytes
import base64
import io
from PIL import Image
import os
from .Encording import loadEncodings, saveEncodings
import logging

logging.basicConfig(
    filename='ImageProcessing.log',  # Log file
    level=logging.ERROR,  # Minimum level of severity to log
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

logger = logging.getLogger()

encodingsFile='encodings.pkl'

encodingsDict = loadEncodings(encodingsFile)

def NoofFaces(image_path):
    image = cv2.imread(image_path)
    face_enc = face_recognition.face_encodings(image)
    return len(face_enc)


def AnomalyDetections(faceLocation, imgFile): #mobile phone photo dection
    img = cv2.imread(imgFile)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    #detect face location
    (fy, fx2, fy2, fx)=faceLocation
    # cv2.rectangle(img, (fx, fy), (fx2, fy2), (0, 0, 255), 2)
    (fw, fh)= (fx2-fx, fy2-fy)

    # Perform Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)


    # Find contours in the edges image
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    # Iterate over each contour
    for contour in contours:
        # Approximate the contour to a polygon
        polygon = cv2.approxPolyDP(contour, 0.1 * cv2.arcLength(contour, True), True)

        # Check if the polygon has 4 0r 3 0r 2 sides
        if len(polygon) <5 and len(polygon) >1:


            # filter small sizes
            x, y, w, h = cv2.boundingRect(polygon)
            if(w<50 or h<50 or( x==0 and y==0)):
                continue

            elif (fx>=x and fy>=y and (y+h)>=(fy+fh) and (x+w)>=(fx+fw) ):
                return True #anaomaly detected

    return False #anaomaly not detected

def compareFaces(knownImagePath, unknownImagePath, uid,  threshold=48):
    global encodingsDict ,encodingsFile
    knownEncodings = encodingsDict.get(uid, [])
    if len(knownEncodings) == 0:
        logging.error('No known encodings found. Encoding new face. uid ' + uid)
        try:
            knownImage = face_recognition.load_image_file(knownImagePath)
            knownImageEncodings = face_recognition.face_encodings(knownImage)
            if len(knownImageEncodings) == 0:
                {'status':False, 'mes':'The Face not Detected in Reference Image.' }

            # Add the new encoding to the list of known encodings for the UID
            knownEncodings.append(knownImageEncodings[0])
            encodingsDict[uid] = knownEncodings
            saveEncodings(encodingsFile, encodingsDict)
        except Exception as e:
            logging.error(f"Error Code FP#1: {e} for {uid}")
            return {'status':False, 'mes':'Error Code FP#1' }

    try:
        # Load the unknown image and encode the face
        unknownImage = face_recognition.load_image_file(unknownImagePath)
        unknownEncoding = face_recognition.face_encodings(unknownImage)

        if len(unknownEncoding) == 0:
            return {'status':False, 'mes':'The Face not Detected, Pls try again!' }
        elif(len(unknownEncoding)>1):
            return {'status':False, 'mes':'More than one faces detected, Pls try again!' }

        unknownEncoding = unknownEncoding[0]
        match = face_recognition.compare_faces(knownEncodings, unknownEncoding)

        
        # Check if there is a match based on the threshold
        if any(match):
            distance = face_recognition.face_distance(knownEncodings, unknownEncoding)
            accuracy = round(100 - (min(distance) * 100))
            if threshold < accuracy < 95:
                encodingsDict[uid].append(unknownEncoding)
                saveEncodings(encodingsFile, encodingsDict)

            return {'status':True, 'mes':'The Faces Matched', 'accuracy':accuracy }
        
        return {'status':False, 'mes':'The Faces miss-matched' }

    except Exception as e:
        logging.error(f"Error Code FP#1: {e} for {uid}")
        return {'status':False, 'mes':'Thats an Error FP#1, Pls try Again!' }
    


def decodeBase64Image(base64_string):
    """Decode a base64 string to a PIL Image."""
    try:
        # Remove the data URL scheme if it is present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode the base64 string into bytes
        image_data = base64.b64decode(base64_string)
        
        # Convert bytes data to a PIL Image
        return io.BytesIO(image_data)
    except Exception as e:
        logging.error(f"Error decoding base64 image: {e}")
        raise

def decodeBase64ImageResize(base64_string, max_size=(800, 800) ):
    """Decode a base64 string to a PIL Image and resize it."""
    try:
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail(max_size)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes.seek(0)
        
        return image_bytes
    except Exception as e:
        logging.error(f"Error decoding and resizing base64 image: {e}")
        raise


def compareFacesBase64(knownImageBase64, unknownImageBase64, uid, threshold=48):
    global encodingsDict ,encodingsFile
    knownEncodings = encodingsDict.get(uid, [])

    if len(knownEncodings) == 0:
        logging.error(f'No known encodings found. Encoding new face. UID: {uid}')
        try:
            # Decode base64 string and convert to a file-like object
            known_image_file = decodeBase64Image(knownImageBase64)
            
            # Load the known image using face_recognition
            known_image = face_recognition.load_image_file(known_image_file)
            knownImageEncodings = face_recognition.face_encodings(known_image)

            if len(knownImageEncodings) == 0:
                return {'status': False, 'mes': 'The face was not detected in the reference image.'}

            # Add the new encoding to the list of known encodings for the UID
            knownEncodings.append(knownImageEncodings[0])
            encodingsDict[uid] = knownEncodings
            saveEncodings(encodingsFile, encodingsDict)
        except Exception as e:
            logging.error(f"Error Code FP#1: {e} for {uid}")
            return {'status': False, 'mes': 'Error Code FP#1'}

    try:
        # Decode base64 string and convert to a file-like object
        unknown_image_file = decodeBase64Image(unknownImageBase64)
        
        # Load the unknown image using face_recognition
        unknown_image = face_recognition.load_image_file(unknown_image_file)
        unknownEncodings = face_recognition.face_encodings(unknown_image)

        if len(unknownEncodings) == 0:
            return {'status': False, 'mes': 'The face was not detected, please try again!'}
        elif len(unknownEncodings) > 1:
            return {'status': False, 'mes': 'More than one face detected, please try again!'}

        unknownEncoding = unknownEncodings[0]
        match = face_recognition.compare_faces(knownEncodings, unknownEncoding)

        # Check if there is a match based on the threshold
        if any(match):
            distance = face_recognition.face_distance(knownEncodings, unknownEncoding)
            accuracy = round(100 - (min(distance) * 100))
            if threshold < accuracy < 95:
                encodingsDict[uid].append(unknownEncoding)
                saveEncodings(encodingsFile, encodingsDict)

            return {'status': True, 'mes': 'The faces matched', 'accuracy': accuracy}

        return {'status': False, 'mes': 'The faces did not match'}

    except Exception as e:
        logging.error(f"Error Code FP#1: {e} for {uid}")
        return {'status': False, 'mes': 'That\'s an error FP#1, please try again!'}



def FaceCompareBase64(img1, img2, uid):
    newImg1 =uid+'test1.jpg'
    newImg2 =uid+'test2.jpg'
    base64img =  str.encode(img1)
    with open(newImg1,"wb") as f:
        f.write(decodebytes(base64img))

    base64img =  str.encode(img2)
    with open(newImg2,"wb") as f:
        f.write(decodebytes(base64img))
    result =compareFaces( newImg1, newImg2, uid)
    os.remove(newImg1)
    os.remove(newImg2)
    return result


# print(faceCompare('im7.jpg', 'facetest.jpg'))