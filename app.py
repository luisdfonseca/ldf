import json, os
from flask import Flask, render_template, g, request, send_from_directory

app= Flask(__name__)

# # Load translations
with open('translations.json') as json_file:
    translations = json.load(json_file)

@app.before_request
def before_request():
    language = 'en'  # default language
    if request.view_args and 'language' in request.view_args:
        language = request.view_args['language']
    g.translations = translations.get(language, {})

@app.route('/', defaults={'language': 'en'})
@app.route('/<string:language>/')
# @app.route('/')
def index(language):
  # if language not in ['en', 'es']:
  #       abort(404)
  return render_template('index.html')


@app.route("/favicon.ico", defaults={'path': ''})
@app.route("/favicon.ico/<path:path>")
def favicon(path):
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/png')
