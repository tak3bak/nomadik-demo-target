FROM python:3.9-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# VULNERABILITY: No non-root user created, runs as root by default
CMD ["python", "config.py"]
