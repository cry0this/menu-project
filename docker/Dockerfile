FROM python:3.10.5-alpine3.16

ENV PYTHONPATH=/app

WORKDIR /app

ADD app /app/
ADD requirements-pipenv.txt Pipfile* /app/

RUN : \
    && apk add --no-cache \
        firefox \
        xvfb \
        wget \
        tzdata \
        logrotate \
        font-noto \
    && pip3 install -r requirements-pipenv.txt \
    && pipenv install --system --deploy \
    && rm -rf /var/cache/apk/* \
    ;

RUN : \
    && wget -O /tmp/geckodriver.tgz https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz \
    && tar -xf /tmp/geckodriver.tgz -C /usr/bin/ \
    && rm /tmp/geckodriver.tgz \
    ;

RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime

ADD docker/cron.conf /etc/crontabs/root
ADD docker/logrotate.conf /etc/logrotate.d/menu-generator

ENTRYPOINT [ "/bin/ash", "-c" ]
CMD ["/usr/sbin/crond -f -l2 -d2"]
