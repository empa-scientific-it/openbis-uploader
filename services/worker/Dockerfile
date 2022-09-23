FROM python:3.10-slim-bullseye

RUN adduser --system --no-create-home worker

COPY data-discovery/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir supervisor


COPY data-discovery/app/ .
RUN pip install -e .

COPY openbis-configuration/ .
RUN pip install -e instance_creator/


COPY worker/supervisord.conf datastore/

RUN rm .env



# USER worker
ENV PYTHONBREAKPOINT 0
ENV REDIS_HOST=
ENV REDIS_PASSWORD=
ENV REDIS_PORT=
CMD ["supervisord", "-d", "/datastore", "-n"]