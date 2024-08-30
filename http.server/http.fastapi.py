from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED
import os
import base64

app = FastAPI()
# Корневая директория
BASE_DIR = os.getcwd()
# Ограничение размера файла для загрузки
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

HTML_TEMPLATE = '''
<!doctype html>
<title>Upload File</title>
<h1>Upload new File</h1>
<form action="/" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="hidden" name="path" value="{current_dir}">
  <input type="submit" value="Upload">
</form>
<br>
<h1>Files and Directories in "{current_dir}"</h1>
<ul>
{file_list_html}
</ul>
'''

# Пользовательские данные для базовой авторизации
USERNAME = "admin"
PASSWORD = "admin"

def basic_auth(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    scheme, credentials = auth.split(" ", 1)
    if scheme.lower() != "basic":
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    decoded_credentials = base64.b64decode(credentials).decode("utf-8")
    username, password = decoded_credentials.split(":", 1)

    if username != USERNAME or password != PASSWORD:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, auth: None = Depends(basic_auth), path: str = ""):
    current_dir = os.path.join(BASE_DIR, path)
    if not os.path.isdir(current_dir):
        raise HTTPException(status_code=404, detail="Directory not found")

    file_list_html = '<li><a href="/">< Root</a></li>'
    
    if path:
        parent_dir = os.path.dirname(path)
        file_list_html += '<li><a href="/?path={}"><< Back</a></li>'.format(parent_dir)

    for item in os.listdir(current_dir):
        item_path = os.path.join(path, item)
        if os.path.isdir(os.path.join(current_dir, item)):
            file_list_html += '<li><a href="/?path={}">{}/</a></li>'.format(item_path, item)
        else:
            file_list_html += '<li><a href="/files/{}">{}</a></li>'.format(item_path, item)
    
    return HTML_TEMPLATE.format(current_dir=path, file_list_html=file_list_html)

@app.post("/", response_class=HTMLResponse)
async def upload_file_post(request: Request, file: UploadFile = File(...), auth: None = Depends(basic_auth), path: str = Form("")):
    current_dir = os.path.join(BASE_DIR, path)
    if file:
        content = await file.read()
        if len(content) > MAX_CONTENT_LENGTH:
            raise HTTPException(status_code=413, detail="File too large")
        file_location = os.path.join(current_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(content)
        return RedirectResponse(url="/?path=" + path, status_code=302)
    return 'No file uploaded'

@app.get("/files/{file_path:path}", response_class=FileResponse)
async def get_file(file_path: str, auth: None = Depends(basic_auth)):
    full_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)