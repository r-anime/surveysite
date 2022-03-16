# [/r/anime Seasonal Surveys Website](https://survey.r-anime.moe/) [![deploy status](https://img.shields.io/github/deployments/r-anime/surveysite/production?label=deploy)](https://github.com/r-anime/surveysite/deployments/activity_log?environment=production)

Website for carrying out seasonal surveys for [/r/anime](https://www.reddit.com/r/anime/). Built with [Django](https://www.djangoproject.com/) as the backend and [Vue.js](https://vuejs.org/) & [Bootstrap](https://getbootstrap.com/) on the frontend.

## Requirements

* Python 3.9+.
* Node.js v14+.
  * For development, a global install of [Vue CLI (`@vue/cli`)](https://cli.vuejs.org/) v5 may be useful.

## Setup

This project consists of a Django back-end in the root folder, and a static Vue.js front-end in `./frontend/` - the front-end will be built and served as static files by Django.

### Environment Variables
* `WEBSITE_SECRET`: a strong, secure [secret key](https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key) for Django.
* `WEBSITE_REDDIT_OAUTH_CLIENT_ID`: the client ID of the Reddit OAuth app.
* `WEBSITE_REDDIT_OAUTH_SECRET`: the secret of the Reddit OAuth app.
* `WEBSITE_DEBUG`: presence of this variable enabled debug mode.
* `WEBSITE_ALLOWED_HOSTS`: [a list of host/domain names](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-ALLOWED_HOSTS) Django should serve, seperated by semicolons (`;`). This list is optional if debug mode is enabled.
* `WEBSITE_USE_HTTPS`: presence of this indicates whether the application is hosted via HTTPS.

### Running the Project

Before either debugging or deploying the project:

* Create Django's database: `python manage.py migrate`.
* Add host/domain name(s) to the `django_site` table of the generated database. This includes `localhost:8000`/`127.0.0.1:8000`!
* Create a superuser for Django: `python manage.py createsuperuser`.

#### Debugging

* Set the environment variables.
* In `./frontend/`, run `npm run debug`. This will build the front-end to `./frontend/dist/` and watch the source code for changes.
* In the root folder, run `python manage.py runserver` to start up the Django server.
* By default, Django will serve everything at `localhost:8000`.

#### Deploying

Install all packages, and perform in arbitrary order:

* Run Django migrations using `python manage.py migrate`
* Collect all static files of Django: `python manage.py collectstatic --noinput`
* Build `./frontend`: `vue-cli-service build` (or `npm run build`)

Use your favorite server to [deploy the Django application](https://docs.djangoproject.com/en/3.2/howto/deployment/).
