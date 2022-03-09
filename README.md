# [/r/anime Seasonal Surveys Website](https://survey.r-anime.moe/) [![deploy status](https://img.shields.io/github/deployments/r-anime/surveysite/production?label=deploy)](https://github.com/r-anime/surveysite/deployments/activity_log?environment=production)

Website for carrying out seasonal surveys for [/r/anime](https://www.reddit.com/r/anime/). Built with [Django](https://www.djangoproject.com/) as the backend and [Vue.js](https://vuejs.org/) & [Bootstrap](https://getbootstrap.com/) on the frontend.

## Features

* Survey form and auto-generated results pages.
* Takes into account anime removed or added during an ongoing survey.
* Reddit authentication.
* Admin page for editing the database.

## Requirements

* Python 3.9+.
* Node.js. This project was made using v14, other versions are untested.
  * A global install of [Vue CLI](https://cli.vuejs.org/) v5.

## Setup

This project consists of a Django back-end in the root folder, and a Node.js & Vue.js front-end in `./frontend/` that will also be served by Django - the index page will be served as a Django template, while all other files will be static files for Django.

### Environment Variables
* `WEBSITE_SECRET` should be a strong, secure [secret key](https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key) for Django.
* `WEBSITE_REDDIT_OAUTH_CLIENT_ID` should be the client ID of the Reddit OAuth app.
* `WEBSITE_REDDIT_OAUTH_SECRET` should be the secret of the Reddit OAuth app.
* `WEBSITE_DEBUG` should be set to something to enable debug mode.
* `WEBSITE_ALLOWED_HOSTS` should be [a list of host/domain names](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-ALLOWED_HOSTS) Django should serve, seperated by semicolons (`;`). This list is optional if debug mode is enabled.
* `WEBSITE_USE_HTTPS` should be set to something if the application is hosted via HTTPS. This will enable an additional session security option, and OAuth redirect URIs will use HTTPS as well.

### Running the Project

Before we either start debugging or deploying the project, we first have to take care of a couple things:

* Create Django's database: `python manage.py migrate`.
* Add your host/domain name(s) to the `django_site` table of the generated database. This includes `localhost:8000`/`127.0.0.1:8000`!
* Create a superuser for Django: `python manage.py createsuperuser`.

#### Debugging

* Set the environment variables.
* In `./frontend/`, run `npm run debug`. This will build the front-end to `./frontend/dist/` and watch the source code for changes.
* In the root folder, run `python manage.py runserver` to start up the Django server.
* By default, Django will serve everything at `localhost:8000`.

For debugging with Visual Studio Code, a workspace has been included with debugging configurations set - put all environment variables in an `.env` file in the root folder and run everything with F5.

#### Deploying

Install all packages, and perform in arbitrary order:

* Run Django migrations using `python manage.py migrate`
* Collect all static files of Django: `python manage.py collectstatic --noinput`
* Build `./frontend`: `vue-cli-service build` (or `npm run build`)

Use your favorite server to [deploy the Django application](https://docs.djangoproject.com/en/4.0/howto/deployment/).
