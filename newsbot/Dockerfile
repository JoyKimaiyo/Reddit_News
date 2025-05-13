# newsbot/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY newsbot.py .

EXPOSE 8501
CMD ["streamlit", "run", "newsbot.py", "--server.port=8501", "--server.address=0.0.0.0"]