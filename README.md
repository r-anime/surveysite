# /r/anime Seasonal Surveys Website

Website for carrying out seasonal surveys for [/r/anime](https://www.reddit.com/r/anime/), replacing Google Forms. Built with [Django](https://www.djangoproject.com/) on the backend and [BootstrapVue](https://bootstrap-vue.org/) on the frontend.

## Features

* Survey form and auto-generated results pages.
* Anime images and (soon?) trailers.
* Takes into account anime removed or added during an ongoing survey.
* Reddit authentication.

## Requirements

* Python 3.6+
* django_allauth 0.44.0
* Django 3.1
* Pillow 8.0.1

## Setup

* Create the website's database: `python manage.py migrate`
* To the `django_site` table of the generated database, add your hostname.
* Create a superuser for the website: `python manage.py createsuperuser`
