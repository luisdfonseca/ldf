import json, os, requests, pdb, jwt
from flask import Flask, render_template, g, request, send_from_directory, jsonify
from datetime import datetime as date

app= Flask(__name__)

GHOST_API_KEY = os.getenv('GHOST_API_KEY','')
GHOST_ADMIN_API_KEY = os.getenv('GHOST_ADMIN_API_KEY','')

URL = "https://luis-daniel-fonseca.ghost.io/"

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
    g.language = language
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



@app.route('/subscribe', methods=['POST'])
def subscribe():
    language = request.form.get('language', 'en')

    phone = request.form.get('phone')
    name = request.form.get('name')
    if name or phone:
        # This submission is likely a spam bot
        return "Thanks", 200


    # Get email from form
    email = request.form['email']

    # Split the key into ID and SECRET
    id, secret = GHOST_ADMIN_API_KEY.split(':')
    print(id)
    print(secret)
    print(email)

    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/admin/'
    }

    # Create the token (including decoding secret)
    token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

    # Make an authenticated request to create a post
    url = '%s/ghost/api/admin/members/' % URL
    print(url)
    headers = {'Authorization': 'Ghost {}'.format(token)}
    body = {"members": [{"email": email}]}

    r = requests.post(url, json=body, headers=headers)

    print(r)
    print(r.text)

    translations_temp = translations.get(language, {})

    success_msg = translations_temp['signup-success-message']
    error_msg = translations_temp['signup-failure-message']

    if r.status_code == 201:  # Assuming 201 is the success status code from the API
      return jsonify({'status': 'success', 'message': success_msg}), 200
    else:
      return jsonify({'status': 'error', 'message': error_msg}), 400