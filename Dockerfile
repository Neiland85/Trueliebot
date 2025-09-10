     develop
FROM python:3.11-slim@sha256:dbf1de478a55d6763afaa39c2f3d7b54b25230614980276de5cacdde79529d0c
FROM python:3.14.0rc1-slim
     main
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
