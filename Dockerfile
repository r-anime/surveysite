FROM node:lts AS frontend-builder

WORKDIR /build
COPY ./frontend /build
RUN npm ci
RUN npm run build

# ---

FROM python:3.11-alpine AS backend
RUN apk add build-base python3-dev jpeg-dev zlib-dev libffi-dev
ENV LIBRARY_PATH=/lib:/usr/lib

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt gunicorn --no-cache-dir

COPY . /app
COPY --from=frontend-builder /build/dist /app/frontend/dist
RUN DJANGO_SECRET_KEY=static python3 ./manage.py collectstatic
EXPOSE 8000
ENTRYPOINT ["python3"]
CMD ["/usr/local/bin/gunicorn", "surveysite.wsgi", "--bind", "0.0.0.0:8000"]

# ---

FROM nginx:alpine AS static

COPY --from=backend /app/static /usr/share/nginx/html
COPY ./static-nginx.conf /etc/nginx/conf.d/default.conf
RUN find /usr/share/nginx/html -type f | xargs gzip -k
EXPOSE 80
