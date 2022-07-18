FROM python:3.10

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app .


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
