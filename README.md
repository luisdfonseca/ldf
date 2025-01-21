# ldf

## Dev

**Requirements**

- Python 3.11.4

```
#install python
pyenv install 3.11.4

git clong ldf.git

cd ldf

# setup python env
python -m venv venv

# load venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

export GHOST_API_KEY=''

# using gunicorn PORT:8000
gunicorn app:app

# using flask  PORT:5000
export FLASK_APP=app.py
flask run
flask run --port 8080
```

## Deployment

```
sudo docker compose build
sudo docker compose down
sudo docker compose up -d
```


## Index

```
    {% include 'portfolio.html' %}

    {% include 'separator.html' %}

    {% include 'skills.html' %}

    {% include 'separator.html' %}

    {% include 'testimonials.html' %}

    {% include 'separator.html' %}
```

## Subscribe Embedded form 
``` html

<form action="https://luisdanielfonseca.com/subscribe-and-redirect" method="POST" style="max-width: 400px; margin: 20px auto; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif;">
  <h3 style="text-align: center; color: #333; margin-bottom: 20px;">Subscribe to Our Updates</h3>
  
  <!-- Language field dynamically set via JavaScript -->
  <input type="hidden" name="language" value="{{language}}" />
  
  <input type="hidden" name="source" value="ldf-coding-questions" />

  <label for="email" style="display: block; font-size: 14px; color: #555; margin-bottom: 5px;">Your Email</label>
  <input type="email" id="email" name="email" required placeholder="Enter your email" style="width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px;">

  <button type="submit" style="display: block; width: 100%; padding: 10px; background-color: #007BFF; color: #fff; font-size: 16px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; text-align: center;">
    Subscribe
  </button>

  <p style="font-size: 12px; color: #777; margin-top: 10px; text-align: center;">
    By subscribing, you agree to receive updates from us. You can unsubscribe anytime.
  </p>
</form>

<script>
  // Extract the language parameter from the URL
  const urlParams = new URLSearchParams(window.location.search);
  const language = urlParams.get('language') || 'en'; // Default to 'en' if not specified

  // Set the hidden language input value
  document.querySelector('input[name="language"]').value = language;
</script>

```
