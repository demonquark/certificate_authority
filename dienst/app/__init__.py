from flask import Flask, request
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    print(request.headers)
    value = request.headers['X-Ssl-Client-Finger']

    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dienst service</title>
</head>
<body>
    <h1>Dienst service</h1>
    <p>This page was served from the dienst service. {}.</p>
</body>
</html>""".format(value)
