from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from starlette.requests import Request
import os

app = FastAPI()
CURRENT_DIR = os.getcwd()
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

HTML_TEMPLATE = '''
<!doctype html>
<title>Upload File</title>
<h1>Upload new File</h1>
<form action="/" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="submit" value="Upload">
</form>
<br>
<h1>Files in Directory</h1>
<ul>
{file_list_html}
</ul>
'''

@app.get("/", response_class=HTMLResponse)
async def upload_file(request: Request):
    files = os.listdir(CURRENT_DIR)
    file_list_html = ''.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files if os.path.isfile(os.path.join(CURRENT_DIR, file))])
    return HTML_TEMPLATE.replace("{file_list_html}", file_list_html)

@app.post("/", response_class=HTMLResponse)
async def upload_file_post(request: Request, file: UploadFile = File(...)):
    if file:
        content = await file.read()
        if len(content) > MAX_CONTENT_LENGTH:
            raise HTTPException(status_code=413, detail="File too large")
        file_location = os.path.join(CURRENT_DIR, file.filename)
        with open(file_location, "wb") as f:
            f.write(content)
        return RedirectResponse(url="/", status_code=302)
    return 'No file uploaded'

@app.get("/files/{filename}", response_class=FileResponse)
async def get_file(filename: str):
    file_path = os.path.join(CURRENT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
