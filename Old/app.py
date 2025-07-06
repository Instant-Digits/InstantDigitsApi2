# flask_ngrok_example.py
from flask import Flask, request, jsonify, send_file
from pyngrok import ngrok
from flask_cors import CORS, cross_origin
from ImageProcessing import FaceProcessing
from MangoDB import dbOperations
from pyngrok import ngrok
from IntelliGold import Main as IntelliGold
from Shinol.QRgenerate import GenerateShinolQRPDF
from FileUploaders.github import handleUploadRequest
import os

app = Flask(__name__)
#CORS(app, support_credentials=True)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024
mangoIsOn=dbOperations.checkMongoConnection()

#local file upload
BASE_FOLDER = os.path.join(os.getcwd(), 'public')
os.makedirs(BASE_FOLDER, exist_ok=True)


@app.route("/")
@cross_origin(supports_credentials=True)
def hello_world():
    return jsonify({'status':True,'apis':'v4.3.1'})


@app.route('/FaceCompareBase64', methods=['POST'])
def faceCompareBase64():
    data=request.get_json()
    img1 = data['img1']
    img2 = data['img2']
    uid = data['uid']
    result = FaceProcessing.compareFacesBase64(img1, img2, uid, dbOperations=dbOperations if mangoIsOn else False)
    print(result)    
    return jsonify(result)


@app.route('/ShinolQRGenerator',methods=["POST"])
def ShinolQRGenerator():
    data = request.get_json()
    enData = data['enData']
    label = data['label']
    address= data['address']
    filename = GenerateShinolQRPDF(enData, label, address)
    return send_file(filename)



# Insert or Update Document
@app.route('/UpdateADoc', methods=['POST'])
def insertOrUpdateDoc():
    if not mangoIsOn:
        return jsonify({'status':False, 'mes':'Database is NOT reachable.' }),404
    return jsonify(dbOperations.updateDoc(request.json)),200

# Delete Document
@app.route('/DeleteADoc', methods=['POST'])
def deleteDoc():
    if not mangoIsOn:
        return jsonify({'status':False, 'mes':'Database is NOT reachable.' }),404
    return jsonify(dbOperations.deleteADoc(request.json)),200

# Get Document
@app.route('/ReadADoc', methods=['POST'])
def getDoc():
    if not mangoIsOn:
        return jsonify({'status':False, 'mes':'Database is NOT reachable.' }),404
    return jsonify(dbOperations.getADoc(request.json)),200

# Query Documents
@app.route('/QueryACollection', methods=['POST'])
def queryDocs():
    if not mangoIsOn:
        return jsonify({'status':False, 'mes':'Database is NOT reachable.' }),404
    return jsonify(dbOperations.queryADocs(request.json)),200



@app.route('/IntelliGoldSpecialTasks', methods=['POST'])
def intelliGoldTasks():
    if not mangoIsOn:
        return jsonify({'status':False, 'mes':'Database is NOT reachable.' }),404

    out=IntelliGold.taskDivider(request.json, dbOperations=dbOperations)
    if 'file' in out and out['status']:
        return send_file(out['file'])
    return jsonify(out), 200

@app.route("/uploadFiles", methods=["POST"])
def uploadFiles():
    try:
        if "file" not in request.files:
            return jsonify({"status": False, "mes": "No file part", "out": {}}), 400
        file = request.files["file"]
        return handleUploadRequest(file)
    except Exception as e:
        return jsonify({"status": False, "mes": str(e), "out": {}}), 500


@app.route('/uploadFileLocal', methods=['POST'])
def uploadFile():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'No file uploaded or empty filename'}), 400

    folder = request.form.get('folder', '').strip()
    targetFolder = os.path.join(BASE_FOLDER, folder) if folder else BASE_FOLDER
    os.makedirs(targetFolder, exist_ok=True)

    savePath = os.path.join(targetFolder, file.filename)
    file.save(savePath)

    publicPath = f'/public/{folder}/{file.filename}' if folder else f'/public/{file.filename}'
    return jsonify({'status': True, 'mes': 'File uploaded successfully', 'out': publicPath})

if __name__ == '__main__':
    # ngrok.set_auth_token("2lAQy2D3FFFsk2Iq2nQV1WXTF0w_mHNMU9M8h8qw1LzL2JrV")
    # url = ngrok.connect(5000, bind_tls=True, hostname="pleasing-javelin-absolutely.ngrok-free.app")
    # print(f" * ngrok tunnel \"{url}\" -> \"http://127.0.0.1:5000\"")

    app.run(host='0.0.0.0', port=8000)#

