from sanic import Sanic
from sanic.response import html, file
import os

app = Sanic(__name__)
CURRENT_DIR = os.getcwd()
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

@app.get('/')
async def index(request):
    files = [f for f in os.listdir(CURRENT_DIR) if os.path.isfile(os.path.join(CURRENT_DIR, f))]
    file_list_html = ''.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files])
    return html(f'''
    <!doctype html>
    <title>Upload File</title>
    <h1>Upload new File</h1>
    <form id="uploadForm" action="/" method="post" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    <br>
    <h1>Files in Directory</h1>
    <ul>
    {file_list_html}
    </ul>
    <script>
      document.getElementById('uploadForm').onsubmit = function() {{
        document.body.innerHTML += '<p>Uploading...</p>';
        var formData = new FormData(this);
        fetch(window.location.pathname, {{
          method: 'POST',
          body: formData
        }}).then(response => {{
          if (response.ok) {{
            window.location.reload();
          }} else {{
            document.body.innerHTML += '<p>Error uploading file</p>';
          }}
        }});
        return false;
      }};
    </script>
    ''')

@app.post('/')
async def upload_file(request):
    if 'file' in request.files:
        file = request.files['file'][0]
        if len(file.body) > MAX_CONTENT_LENGTH:
            return html('<h1>File too large</h1>')
        
        file_path = os.path.join(CURRENT_DIR, file.name)
        with open(file_path, 'wb') as f:
            f.write(file.body)

        return html('<h1>File uploaded successfully</h1><script>window.location.reload();</script>')
    return html('<h1>No file uploaded</h1>')

@app.get('/files/<filename>')
async def get_file(request, filename):
    file_path = os.path.join(CURRENT_DIR, filename)
    if os.path.exists(file_path):
        return await file(file_path)
    return html('<h1>File not found</h1>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
