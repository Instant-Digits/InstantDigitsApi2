import os
from fastapi import UploadFile

def saveUploadedFile(file: UploadFile, folder: str, baseFolder: str) -> dict:
    """Save an uploaded file to the specified subdirectory under baseFolder."""
    if not file or not file.filename:
        return {"status": False, "mes": "No file provided"}
    # Prevent directory traversal or invalid folder names
    if folder and (".." in folder or folder.startswith("/")):
        return {"status": False, "mes": "Invalid subdirectory name"}
    targetFolder = os.path.join(baseFolder, folder.strip()) if folder else baseFolder
    os.makedirs(targetFolder, exist_ok=True)
    savePath = os.path.join(targetFolder, file.filename)
    with open(savePath, "wb") as buffer:
        buffer.write(file.file.read())
    publicPath = f'/{folder}/{file.filename}' if folder else f'/{file.filename}'
    return {"status": True, "mes": "File uploaded successfully", "out": publicPath}

def deleteFileByRelativePath(relativePath: str, baseFolder: str) -> dict:
    """Delete a file by its relative path under baseFolder, with safety checks."""
    if not relativePath:
        return {"status": False, "mes": "No file path provided"}
    if ".." in relativePath or relativePath.startswith("/"):
        return {"status": False, "mes": "Invalid file path"}
    absPath = os.path.abspath(os.path.join(baseFolder, relativePath.lstrip("/\\")))
    if not absPath.startswith(baseFolder):
        return {"status": False, "mes": "Invalid file path"}
    if not os.path.isfile(absPath):
        return {"status": False, "mes": "File does not exist"}
    try:
        os.remove(absPath)
        return {"status": True, "mes": "File deleted successfully"}
    except Exception as e:
        return {"status": False, "mes": f"Error deleting file: {str(e)}"}