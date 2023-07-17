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