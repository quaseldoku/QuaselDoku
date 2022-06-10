from flask import Flask
import sys

if len(sys.argv) != 2:
    print('please provide path to static html files')
    sys.exit(0)

doku_path = sys.argv[1]
app = Flask(__name__, static_url_path='/', static_folder=doku_path)

@app.route('/')

@app.route('/<path:path>')
def serve_sphinx_docs(path='index.html'):
    return app.send_static_file(path)

app.run(debug=False, host='0.0.0.0')