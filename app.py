# flask_ngrok_example.py
from flask import Flask, request, jsonify
from pyngrok import ngrok
from flask_cors import CORS, cross_origin
from ImageProcessing import FaceProcessing
from MangoDB import dbOperations

app = Flask(__name__)
CORS(app, support_credentials=True)

mangoIsOn=dbOperations.checkMongoConnection()


@app.route("/")
@cross_origin(supports_credentials=True)
def hello_world():
    return jsonify({'status':True,'apis':'v3.2.1'})


@app.route('/FaceCompareBase64', methods=['POST'])
def faceCompareBase64():
    data=request.get_json()
    img1 = data['img1']
    img2 = data['img2']
    uid = data['uid']
    result = FaceProcessing.compareFacesBase64(img1, img2, uid, dbOperations=dbOperations if mangoIsOn else False)
    print(result)    
    return jsonify(result)



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


if __name__ == '__main__':
    # ngrok.set_auth_token("2lAQy2D3FFFsk2Iq2nQV1WXTF0w_mHNMU9M8h8qw1LzL2JrV")
    # url = ngrok.connect(5000, bind_tls=True, hostname="pleasing-javelin-absolutely.ngrok-free.app")
    # print(f" * ngrok tunnel \"{url}\" -> \"http://127.0.0.1:5000\"")

    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)#
    