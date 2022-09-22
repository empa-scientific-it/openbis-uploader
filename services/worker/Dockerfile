FROM python:3.10-slim-bullseye

RUN adduser --system --no-create-home worker

COPY worker/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY worker/app ./app


COPY data-discovery/app/datastore/tasks/ /app/


ENV PYTHONBREAKPOINT 0
USER worker
CMD ["python3", "app/main.py"]