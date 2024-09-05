# Simple Web File Browser

Like `http.server`, but with support for **authorization** and **uploading files** to the server using different web frameworks.

A fast and user-friendly option for Linux system administrators ❤️🐧

## 🚀 Install

- Clone repository:

```shell
git clone https://github.com/Lifailon/SimpleWebFileBrowser
cd SimpleWebFileBrowser
```

- Install the venv module to create a virtual environment (*optional*):

```shell
apt install python3-venv
```

- Create and activate a Python virtual environment (*optional*):

```shell
python3 -m venv http
source http/bin/activate
```

- Install the [Flask](https://github.com/pallets/flask) or [FastAPI](https://github.com/tiangolo/fastapi) framework to your choice:

```shell
pip install flask flasgger || pip install fastapi uvicorn jinja2 python-multipart
```

- Start the server:

```shell
python3 http.server/http.flask.py
```

or

```shell
python3 http.server/http.fastapi.py
```

🌐 The server will be launched at the port: `5000` and available on all interfaces (`0.0.0.0`).

🔐 Default login and password: `admin` and `admin`

Through the browser, you will have access to the root directory from which you run the script, as well as navigation through all child directories. If you need to select a different root directory, simply navigate to it in the console using the `cd` command and run the script from there.

Versions for other frameworks are available in the `test` directory.