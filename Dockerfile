FROM python:2.7
MAINTAINER Ümit Seren

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

COPY . /srv/web
RUN chmod 755 /srv/web/web-entrypoint.sh

WORKDIR /srv/web/arapheno
ENTRYPOINT ["/srv/web/web-entrypoint.sh"]
CMD ["manage.py"]