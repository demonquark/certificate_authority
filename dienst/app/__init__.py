from flask import Flask
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dienst service</title>
</head>
<body>
    <h1>Dienst service</h1>
    <p>This page was served from the dienst service. etc.</p>
</body>
</html>"""
