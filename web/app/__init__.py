from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Web service</title>
</head>
<body>
    <h1>Web service</h1>
    <p>This page was served from the web service.</p>
</body>
</html>"""


@app.route('/other')
def other():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Web service</title>
</head>
<body>
    <h1>Other service</h1>
    <p>This page should be loaded from another page ({}).</p>
</body>
</html>""".format(str(request.args.get('a')))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404