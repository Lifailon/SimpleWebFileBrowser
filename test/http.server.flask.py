from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, abort
import os

app = Flask(__name__)
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
{{ file_list_html | safe }}
</ul>
'''

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if len(file.read()) > MAX_CONTENT_LENGTH:
                return "File too large", 413
            file.seek(0)
            file.save(os.path.join(CURRENT_DIR, file.filename))
            return redirect(url_for('upload_file'))
    
    files = [f for f in os.listdir(CURRENT_DIR) if os.path.isfile(os.path.join(CURRENT_DIR, f))]
    file_list_html = ''.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files])
    return render_template_string(HTML_TEMPLATE, file_list_html=file_list_html)

@app.route('/files/<filename>')
def get_file(filename):
    try:
        return send_from_directory(CURRENT_DIR, filename)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
