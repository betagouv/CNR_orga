FROM python:3.11.2-bullseye

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV GECKODRIVER_URL=https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux32.tar.gz
ENV APP_DIR="/app"

RUN useradd -U -m -d $APP_DIR app

RUN apt-get update && apt-get install -y --no-install-recommends firefox-esr

# Needed for behave test
RUN wget -qO- $GECKODRIVER_URL | tar xvz -C /usr/bin/

RUN python -m pip install --upgrade pip

COPY --chown=app:app . $APP_DIR

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r $APP_DIR/requirements/dev.txt

USER app

WORKDIR $APP_DIR

RUN python manage.py compilescss && python manage.py collectstatic --no-input

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
