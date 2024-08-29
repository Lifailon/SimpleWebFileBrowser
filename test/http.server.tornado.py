import tornado.ioloop
import tornado.web
import os

CURRENT_DIR = os.getcwd()
MAX_CONTENT_LENGTH = 100 * 1024 * 1024

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        files = [f for f in os.listdir(CURRENT_DIR) if os.path.isfile(os.path.join(CURRENT_DIR, f))]
        file_list_html = ''.join([f'<li><a href="/files/{file}">{file}</a></li>' for file in files])
        self.write(f'''
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
        ''')

    def post(self):
        file = self.request.files['file'][0]
        if len(file.body) > MAX_CONTENT_LENGTH:
            self.set_status(413)
            self.write("File too large")
            return
        
        with open(os.path.join(CURRENT_DIR, file.filename), 'wb') as f:
            f.write(file.body)
        
        self.redirect('/')

class FileHandler(tornado.web.RequestHandler):
    def get(self, filename):
        file_path = os.path.join(CURRENT_DIR, filename)
        if os.path.exists(file_path):
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', f'attachment; filename="{filename}"')
            with open(file_path, 'rb') as f:
                self.write(f.read())
        else:
            self.set_status(404)
            self.write("File not found")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/files/(.*)", FileHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    tornado.ioloop.IOLoop.current().start()
