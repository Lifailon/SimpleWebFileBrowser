import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.shortcuts import render
from django.urls import path
from django.core.exceptions import SuspiciousOperation
from django.core.management import execute_from_command_line
from django.middleware.csrf import get_token

settings.configure(
    DEBUG=True,
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    SECRET_KEY='your-secret-key',
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ],
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        },
    ],
)

CURRENT_DIR = os.getcwd()
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

HTML_TEMPLATE = '''
<!doctype html>
<title>Upload File</title>
<h1>Upload new File</h1>
<form action="/" method="post" enctype="multipart/form-data">
  <input type="file" name="file">
  <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
  <input type="submit" value="Upload">
</form>
<br>
<h1>Files in Directory</h1>
<ul>
{file_list_html}
</ul>
'''

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        if file.size > MAX_CONTENT_LENGTH:
            raise SuspiciousOperation("File too large")
        fs = FileSystemStorage(location=CURRENT_DIR)
        filename = fs.save(file.name, file)
        return HttpResponseRedirect('/')
    
    files = [f for f in os.listdir(CURRENT_DIR) if os.path.isfile(os.path.join(CURRENT_DIR, f))]
    file_list_html = ''.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files])
    csrf_token = get_token(request)
    return HttpResponse(HTML_TEMPLATE.format(csrf_token=csrf_token, file_list_html=file_list_html))

def get_file(request, filename):
    file_path = os.path.join(CURRENT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'))
    else:
        return HttpResponseNotFound('File not found')

urlpatterns = [
    path('', upload_file),
    path('files/<str:filename>/', get_file),
]

if __name__ == '__main__':
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5000'])
