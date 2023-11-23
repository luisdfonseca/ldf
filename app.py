import json, os, requests, pdb, jwt
from flask import Flask, render_template, g, request, send_from_directory, jsonify
from datetime import datetime as date

app= Flask(__name__)

GHOST_API_KEY = os.getenv('GHOST_API_KEY','')
GHOST_ADMIN_API_KEY = os.getenv('GHOST_ADMIN_API_KEY','')

GHOST_API_KEY_ES = os.getenv('GHOST_API_KEY_ES','')
GHOST_ADMIN_API_KEY_ES = os.getenv('GHOST_ADMIN_API_KEY_ES','')

URL = "https://luis-daniel-fonseca.ghost.io/"
URL_ES = "https://luis-daniel-fonseca-2.ghost.io/"

# # Load translations
with open('translations.json') as json_file:
    translations = json.load(json_file)

def get_posts(language):
  headers = {
      "Accept-Version": "v5.0",
  }

  url = URL
  key = GHOST_API_KEY

  if language == 'es':
    url = URL_ES
    key = GHOST_API_KEY_ES

  response = requests.get("%sghost/api/content/posts/" % url,
              headers=headers, params={'key': key, 'limit': '10','include':'tags'})

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

  posts = get_posts(language)

  return render_template('index.html', posts=posts)

@app.route("/en/lan", methods=['GET'])
def lan():
    return render_template('lan.html')


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

    site_url = URL
    admin_key = GHOST_ADMIN_API_KEY

    if language == 'es':
      site_url = URL_ES
      admin_key = GHOST_ADMIN_API_KEY_ES

    # Get email from form
    email = request.form['email']

    if 'X-Forwarded-For' in request.headers:
      ip_address = request.headers['X-Forwarded-For']
    else:
      ip_address = request.remote_addr

    geo_data = get_geolocation(ip_address)
    geolocation_data = {}

    print(geo_data)

    if geo_data:
      geolocation_data = {
        "country_code": geo_data["countryCode"],
        "country_code3":"NA",
        "continent_code":"NA",
        "region": geo_data["regionName"],
        "ip": ip_address,
        "longitude": geo_data["lon"],
        "accuracy": 0,
        "latitude": geo_data["lat"],
        "timezone": geo_data["timezone"],
        "city": geo_data["city"],
        "organization": geo_data["org"],
        "asn": geo_data["as"],
        "country": geo_data["country"],
        "area_code":"NA",
        "organization_name": geo_data["org"]
      }

    print(ip_address)
    print(geolocation_data)

    # Split the key into ID and SECRET
    id, secret = admin_key.split(':')
    print(id)
    # print(secret)
    # print(email)

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
    url = '%s/ghost/api/admin/members/' % site_url
    print(url)
    headers = {'Authorization': 'Ghost {}'.format(token)}
    body = {"members": [{"email": email, 'geolocation': geolocation_data}]}

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


def get_geolocation(ip_address):
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    if response.status_code == 200:
        return response.json()
    else:
        return {}


def get_ghost_members():
  site_url = URL
  admin_key = GHOST_ADMIN_API_KEY

  # if language == 'es':
  #   site_url = URL_ES
  #   admin_key = GHOST_ADMIN_API_KEY_ES

  # Split the key into ID and SECRET
  id, secret = admin_key.split(':')
  # print(id)
  # print(secret)

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

  url = '%s/ghost/api/admin/members/' % site_url

  headers = {'Authorization': 'Ghost {}'.format(token)}

  r = requests.get(url, headers=headers)

  return(r.json())




