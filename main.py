from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
import os

from ImageProcessing import FaceProcessing
from MangoDB import dbOperations
from IntelliGold import Main as IntelliGold
from Shinol.QRgenerate import GenerateShinolQRPDF
from FileUploaders.Files import saveUploadedFile, deleteFileByRelativePath

app = FastAPI(title="Instant Digits API", version="v4.3.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set BASE_FOLDER to one directory up from current, named 'PublicFiles'
BASE_FOLDER = os.path.abspath(os.path.join(os.getcwd(), '..', 'PublicFiles'))
os.makedirs(BASE_FOLDER, exist_ok=True)
app.mount("/public", StaticFiles(directory=BASE_FOLDER), name="public")

mangoIsOn = dbOperations.checkMongoConnection()

@app.get("/")
async def hello_world():
    return {"status": True, "apis": "v4.3.1"}

@app.post("/FaceCompareBase64")
async def face_compare_base64(request: Request):
    data = await request.json()
    img1 = data['img1']
    img2 = data['img2']
    uid = data['uid']
    result = FaceProcessing.compareFacesBase64(img1, img2, uid, dbOperations=dbOperations if mangoIsOn else False)
    return result

@app.post("/ShinolQRGenerator")
async def shinol_qr_generator(request: Request):
    data = await request.json()
    enData = data['enData']
    label = data['label']
    address = data['address']
    filename = GenerateShinolQRPDF(enData, label, address)
    return FileResponse(filename)

@app.post("/UpdateADoc")
async def insert_or_update_doc(request: Request):
    if not mangoIsOn:
        return JSONResponse({'status': False, 'mes': 'Database is NOT reachable.'}, status_code=404)
    data = await request.json()
    return dbOperations.updateDoc(data)

@app.post("/DeleteADoc")
async def delete_doc(request: Request):
    if not mangoIsOn:
        return JSONResponse({'status': False, 'mes': 'Database is NOT reachable.'}, status_code=404)
    data = await request.json()
    return dbOperations.deleteADoc(data)

@app.post("/ReadADoc")
async def get_doc(request: Request):
    if not mangoIsOn:
        return JSONResponse({'status': False, 'mes': 'Database is NOT reachable.'}, status_code=404)
    data = await request.json()
    return dbOperations.getADoc(data)

@app.post("/QueryACollection")
async def query_docs(request: Request):
    if not mangoIsOn:
        return JSONResponse({'status': False, 'mes': 'Database is NOT reachable.'}, status_code=404)
    data = await request.json()
    return dbOperations.queryADocs(data)

@app.post("/IntelliGoldSpecialTasks")
async def intelli_gold_tasks(request: Request):
    if not mangoIsOn:
        return JSONResponse({'status': False, 'mes': 'Database is NOT reachable.'}, status_code=404)
    data = await request.json()
    out = IntelliGold.taskDivider(data, dbOperations=dbOperations)
    if 'file' in out and out['status']:
        return FileResponse(out['file'])
    return out


@app.post("/files/uploadAFile")
async def upload_file_local(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("")
):
    return saveUploadedFile(file, folder, BASE_FOLDER)

@app.post("/files/deleteAFile/")
async def deleteFile(payload: dict = Body(...)):
    relativePath = payload.get("url")
    return deleteFileByRelativePath(relativePath, BASE_FOLDER)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)