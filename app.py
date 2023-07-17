import json, os, requests, pdb
from flask import Flask, render_template, g, request, send_from_directory

app= Flask(__name__)

GHOST_API_KEY = os.getenv('GHOST_API_KEY','')

# # Load translations
with open('translations.json') as json_file:
    translations = json.load(json_file)

def get_posts():
  headers = {
      "Accept-Version": "v5.0",
  }

  response = requests.get("https://luis-daniel-fonseca.ghost.io/ghost/api/content/posts/",
              headers=headers, params={'key': GHOST_API_KEY, 'limit': '10','include':'tags'})

  # To print the response text
  # print(response.text)
  # pdb.set_trace()
  posts_with_images = [post for post in response.json()["posts"] if post["feature_image"]]
    # limit to first 3 posts
  posts_with_images = posts_with_images[:3]

  return posts_with_images

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

  if GHOST_API_KEY:
    posts = get_posts()

  return render_template('index.html', posts=posts)


@app.route("/favicon.ico", defaults={'path': ''})
@app.route("/favicon.ico/<path:path>")
def favicon(path):
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/png')
