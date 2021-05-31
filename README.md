# [/r/anime Seasonal Surveys Website](https://survey.r-anime.moe/) [![deploy status](https://img.shields.io/github/deployments/r-anime/surveysite/production?label=deploy)](https://github.com/r-anime/surveysite/deployments/activity_log?environment=production)

Website for carrying out seasonal surveys for [/r/anime](https://www.reddit.com/r/anime/). Built with [Django](https://www.djangoproject.com/) as the backend and [BootstrapVue](https://bootstrap-vue.org/) (Bootstrap and embedded Vue.js) on the frontend.

## Features

* Survey form and auto-generated results pages.
* Takes into account anime removed or added during an ongoing survey.
* Reddit authentication.
* Admin page for editing the database.

## Requirements

Python 3.6+, and all dependencies in `requirements.txt`.

## Setup

* Add the following environment variables:
  * `WEBSITE_SECRET` should be a strong, secure [secret key](https://docs.djangoproject.com/en/3.1/ref/settings/#secret-key) for Django.
  * `WEBSITE_REDDIT_OAUTH_CLIENT_ID` should be the client ID of the Reddit OAuth app.
  * `WEBSITE_REDDIT_OAUTH_SECRET` should be the secret of the Reddit OAuth app.
  * `WEBSITE_DEBUG` should be set to something to enable debug mode.
  * `WEBSITE_ALLOWED_HOSTS` should be [a list of host/domain names](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-ALLOWED_HOSTS) Django should serve, seperated by semicolons (`;`). This list is optional if debug mode is enabled.
  * `WEBSITE_USE_HTTPS` should be set to something if the application is hosted via HTTPS. This will enable an additional session security option, and OAuth redirect URIs will use HTTPS as well.
* Create the website's database: `python manage.py migrate`.
* Add your host/domain name(s) to the `django_site` table of the generated database.
* Create a superuser for the website: `python manage.py createsuperuser`.
