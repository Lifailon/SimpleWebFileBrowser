from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, abort, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flasgger import Swagger
import os

app = Flask(__name__)
# Secret Key
app.secret_key = 'your_secret_key_here'
BASE_DIR = os.getcwd()
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

# Инициализация Swagger
swagger = Swagger(app)

USERS = {
    "admin": generate_password_hash("admin")
}

HTML_TEMPLATE = '''
<!doctype html>
<title>File Upload and Navigation</title>
<h1>Upload new File</h1>
<form action="{{ url_for('upload_file', path=current_path) }}" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="submit" value="Upload">
</form>
<br>
<h1>Files and Directories in "{{ current_path }}"</h1>
<ul>
{{ file_list_html | safe }}
</ul>
<br>
<a href="{{ url_for('logout') }}">Logout</a>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login
    ---
    tags:
      - authentication
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      302:
        description: Redirect to file upload page
      400:
        description: Invalid username or password
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and check_password_hash(USERS[username], password):
            session['username'] = username
            return redirect(request.args.get('next') or url_for('upload_file'))
        return 'Invalid username or password', 400
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
    '''

@app.route('/logout')
def logout():
    """
    User logout
    ---
    tags:
      - authentication
    responses:
      302:
        description: Redirect to login page
    """
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
@login_required
def upload_file(path=''):
    """
    File upload and directory navigation
    ---
    tags:
      - file management
    parameters:
      - name: path
        in: path
        type: string
        required: false
        description: Directory path
      - name: file
        in: formData
        type: file
        required: false
        description: File to upload
    responses:
      200:
        description: Successful operation
      404:
        description: Directory not found
      413:
        description: File too large
    """
    current_dir = os.path.join(BASE_DIR, path)
    if not os.path.isdir(current_dir):
        abort(404)

    if request.method == 'POST':
        file = request.files['file']
        if file:
            if len(file.read()) > MAX_CONTENT_LENGTH:
                return "File too large", 413
            file.seek(0)
            file.save(os.path.join(current_dir, file.filename))
            return redirect(url_for('upload_file', path=path))
    
    file_list_html = '<li><a href="{}">< Root</a></li>'.format(url_for('upload_file'))
    if path:
        parent_dir = os.path.dirname(path)
        file_list_html += '<li><a href="{}"><< Back</a></li>'.format(url_for('upload_file', path=parent_dir))
    
    for item in os.listdir(current_dir):
        item_path = os.path.join(path, item)
        if os.path.isdir(os.path.join(current_dir, item)):
            file_list_html += '<li><a href="{}">{}/</a></li>'.format(url_for('upload_file', path=item_path), item)
        else:
            file_list_html += '<li><a href="{}">{}</a></li>'.format(url_for('get_file', path=item_path), item)
    
    return render_template_string(HTML_TEMPLATE, file_list_html=file_list_html, current_path=path)

@app.route('/files/<path:path>')
@login_required
def get_file(path):
    """
    Get file
    ---
    tags:
      - file management
    parameters:
      - name: path
        in: path
        type: string
        required: true
        description: File path
    responses:
      200:
        description: File content
      404:
        description: File not found
    """
    directory, file = os.path.split(path)
    try:
        return send_from_directory(os.path.join(BASE_DIR, directory), file)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)