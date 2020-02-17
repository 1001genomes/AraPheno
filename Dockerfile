FROM python:2.7

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

COPY . /srv/web
RUN chmod 755 /srv/web/web-entrypoint.sh /srv/web/write_version.sh

ARG GIT_BRANCH
ENV GIT_BRANCH $GIT_BRANCH

ARG GIT_COMMIT
ENV GIT_COMMIT $GIT_COMMIT

ARG BUILD_NUMBER
ENV BUILD_NUMBER $BUILD_NUMBER

ARG BUILD_URL
ENV BUILD_URL $BUILD_URL

RUN /srv/web/write_version.sh /srv/web/arapheno/phenotypedb/__init__.py

WORKDIR /srv/web/arapheno
ENTRYPOINT ["/srv/web/web-entrypoint.sh"]
CMD ["manage.py"]