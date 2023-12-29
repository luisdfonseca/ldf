import json, os, requests, pdb, jwt
from flask import Flask, render_template, g, request, send_from_directory, jsonify
from datetime import datetime as date

from dotenv import load_dotenv
load_dotenv()


app= Flask(__name__)

GHOST_API_KEY = os.getenv('GHOST_API_KEY','')
GHOST_ADMIN_API_KEY = os.getenv('GHOST_ADMIN_API_KEY','')

GHOST_API_KEY_ES = os.getenv('GHOST_API_KEY_ES','')
GHOST_ADMIN_API_KEY_ES = os.getenv('GHOST_ADMIN_API_KEY_ES','')

URL = os.getenv('URL','')
URL_ES = os.getenv('URL_ES','')

non_language_specific_urls = ['choose-language']

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
  posts_with_images = posts_with_images[:6]

  return posts_with_images

@app.before_request
def before_request():

  if request.path.strip('/') in non_language_specific_urls:
          g.language = 'default'
          g.translations = {}
  else:
    language = 'en'
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

@app.route("/choose-language", methods=['GET'])
def lan():
    return render_template('landing-pages/lan.html')

@app.route("/<string:language>/test", methods=['GET'])
def test(language):
    print(get_ghost_members())
    return render_template('index.html')

@app.route("/<string:language>/coding-interview-study-guide", methods=['GET'])
def coding_questions(language):
    return render_template('landing-pages/page-coding-questions.html')


@app.route("/<string:language>/guia-de-estudio-para-entrevistas-de-programacion", methods=['GET'])
def coding_questions_es(language):
    return render_template('landing-pages/page-coding-questions.html')



@app.route("/favicon.ico", defaults={'path': ''})
@app.route("/favicon.ico/<path:path>")
def favicon(path):
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.png', mimetype='image/png')

# @app.route('/subscribe', methods=['POST'])
# def subscribe():
#   language = request.form.get('language', 'en')
#   email = request.form['email']
#   source = request.form['source']

#   site_url, admin_key = get_site_info(language)

#   if is_spam_request(request):
#     return jsonify({'status': 'success', 'message': 'Thanks'}), 200

#   if member_exists_in_ghost(email, language):
#       return handle_existing_member(email, source, language)

#   geolocation_data = get_geolocation_data(request)

#   token = create_jwt_token(admin_key)
#   response = create_ghost_member(site_url, email, geolocation_data, source, token)

#   return prepare_response(response, language)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    '''
      <Response [201]>
      {"members":[{"id":"42523523","uuid":"r24r34-454354-2435243","email":"luis@gmail.com",
      "name":null,"note":"{'status': 'fail', 'message': 'reserved range', 'query': '127.0.0.1'}",
      "geolocation":null,"subscribed":true,"created_at":"2023-11-27T13:01:44.000Z","updated_at":"2023-11-27T13:01:44.000Z","labels":[]
      ,"subscriptions":[],"avatar_image":"https://www.gravatar.com/avatar/54325grtg?s=250&r=g&d=blank","comped":false,
      "email_count":0,"email_opened_count":0,"email_open_rate":null,"status":"free","last_seen_at":null,"attribution":{"id":null,"type":null,"url":null,
      "title":null,"referrer_source":"Integration: ldf home","referrer_medium":"Admin API","referrer_url":null},"tiers":[],
      "email_suppression":{"suppressed":false,"info":null},"newsletters":[{"id":"641ff2aba664ef0031087514","name":"Luis Daniel Fonseca","description":null,"status":"active"}]}]}

      <Response [422]>
      {"errors":[{"message":"Validation error, cannot save member.",
      "context":"Member already exists. Attempting to add member with existing email address","type":"ValidationError","details":null,"property":"email","help":null,
      "code":null,"id":"3a446010-8d25-11ee-b121-e1b0984af7d1","ghostErrorCode":null}]}

    '''
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
    source = request.form['source']

    if member_exists_in_ghost(email, language):
      if source == 'ldf-coding-questions' and not check_member_label_in_ghost(email, language, 'ldf-coding-questions'):
        # we need to update the user with the new label
        # and send email using zapier webhook
        return jsonify({'status': 'success', 'message': 'Please check your email.'}), 200
      return jsonify({'status': 'error', 'message': 'User already exists'}), 400

    if 'X-Forwarded-For' in request.headers:
      ip_address = request.headers['X-Forwarded-For']
    else:
      ip_address = request.remote_addr

    geolocation_data = get_geolocation(ip_address)

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
    body = {"members": [{"email": email, 'note': str(geolocation_data)}]}

    body["members"][0]["labels"] = []

    if geolocation_data["status"] == 'success':
      body["members"][0]["labels"].append({"name": geolocation_data["country"],"slug": geolocation_data["countryCode"]})

    if source:
      body["members"][0]["labels"].append({"name": source, "slug": source})

    r = requests.post(url, json=body, headers=headers)

    print(r)
    print(r.text)

    translations_temp = translations.get(language, {})

    success_msg = translations_temp['signup-success-message']
    error_msg = translations_temp['signup-failure-message']

    if r.status_code == 201:  # Assuming 201 is the success status code from the API
      if source == 'ldf-coding-questions':
        if language == 'en':
          success_msg = success_msg + ' Please check your email.'
        elif language == 'es':
          success_msg = success_msg + ' Por favor revisa tu correo electrónico.'

      return jsonify({'status': 'success', 'message': success_msg}), 200
    else:
      return jsonify({'status': 'error', 'message': error_msg}), 400

def get_site_info(language):
    if language == 'es':
        return URL_ES, GHOST_ADMIN_API_KEY_ES
    return URL, GHOST_ADMIN_API_KEY

def is_spam_request(request):
    return request.form.get('name') or request.form.get('phone')

def get_geolocation_data(request):
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    return get_geolocation(ip_address)

def get_geolocation(ip_address):
    """
    success response:
    {
        "query": "174.165.78.217",
        "status": "success",
        "continent": "North America",
        "continentCode": "NA",
        "country": "United States",
        "countryCode": "US",
        "region": "FL",
        "regionName": "Florida",
        "city": "Portland",
        "district": "",
        "zip": "534543",
        "lat": 52345,
        "lon": 2435,
        "timezone": "America/Los_Angeles",
        "offset": -28800,
        "currency": "USD",
        "isp": "Comcast Cable Communications, LLC",
        "org": "Comcast Cable Communications, LLC",
        "as": "AS33490 Comcast Cable Communications, LLC",
        "asname": "COMCAST-33490",
        "mobile": false,
        "proxy": false,
        "hosting": false
    }

    fail res:
    {'status': 'fail', 'message': 'reserved range', 'query': '127.0.0.1'}
    """
    response = requests.get(f'http://ip-api.com/json/{ip_address}')
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def handle_existing_member(email, source, language):
    if source == 'ldf-coding-questions' and not check_member_label_in_ghost(email, language, 'ldf-coding-questions'):
        # Update the user with the new label
        # (Add relevant code here)
        pass
    return jsonify({'status': 'error', 'message': 'User already exists'}), 400

def create_jwt_token(admin_key):
    id, secret = admin_key.split(':')
    iat = int(datetime.now().timestamp())
    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
    payload = {'iat': iat, 'exp': iat + 5 * 60, 'aud': '/admin/'}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

def create_ghost_member(site_url, email, geolocation_data, source, token):
    url = f'{site_url}/ghost/api/admin/members/'
    headers = {'Authorization': f'Ghost {token}'}
    body = {"members": [{"email": email, 'note': str(geolocation_data)}]}

    # Add labels based on geolocation and source
    body["members"][0]["labels"] = []
    if geolocation_data.get("status") == 'success':
        body["members"][0]["labels"].append({"name": geolocation_data["country"], "slug": geolocation_data["countryCode"]})
    if source:
        body["members"][0]["labels"].append({"name": source, "slug": source})

    return requests.post(url, json=body, headers=headers)

def prepare_response(response, language):
    translations_temp = translations.get(language, {})
    success_msg = translations_temp.get('signup-success-message', 'Success')
    error_msg = translations_temp.get('signup-failure-message', 'Error')

    if response.status_code == 201:  # Assuming 201 is the success status code
        return jsonify({'status': 'success', 'message': success_msg}), 200
    return jsonify({'status': 'error', 'message': error_msg}), 400

def member_exists_in_ghost(email, language="en"):
  '''
    member does not exist
    {'members': [], 'meta': {'pagination': {'page': 1, 'limit': 15, 'pages': 1, 'total': 0, 'next': None, 'prev': None}}}
  '''
  response = get_ghost_members(email, language)

  print(response)  

  if response['members']:
    return True

  return False


def check_member_label_in_ghost(email, language, label_name):
  '''
    'labels': [{'id': '655f10b4116a4d00012f85ca', 'name': 'United States', 'slug': 'us', 
    'created_at': '2023-11-23T08:43:32.000Z', 'updated_at': '2023-11-23T08:43:32.000Z'}]
  '''
  response = get_ghost_members(email, language)

  print(response)  

  for label in response['members'][0]['labels']:
    if label_name == label['name']:
      return True

  return False


def get_ghost_members(email=None, language="en"):
  site_url = URL
  admin_key = GHOST_ADMIN_API_KEY

  if language == 'es':
    site_url = URL_ES
    admin_key = GHOST_ADMIN_API_KEY_ES

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

  from urllib.parse import quote

  if email:
    encoded_email = quote(email)
    url = """%s/ghost/api/admin/members?filter=email:%s""" % (site_url, encoded_email)
  else:
    url = "%s/ghost/api/admin/members/" % site_url

  headers = {'Authorization': 'Ghost {}'.format(token)}

  r = requests.get(url, headers=headers, params={'include':'tags'})

  return(r.json())