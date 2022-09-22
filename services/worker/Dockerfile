FROM python:3.10-slim-bullseye

RUN adduser --system --no-create-home worker

COPY data-discovery/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY data-discovery/app/ .
RUN pip install -e .

ENV PYTHONBREAKPOINT 0
USER worker
CMD ["python3", "datastore/worker/main.py", "default"]