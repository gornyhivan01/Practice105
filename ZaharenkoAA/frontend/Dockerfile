FROM python:3.10-alpine
WORKDIR /app
COPY static/ static/
CMD ["python", "-m", "http.server", "3000", "--directory", "static"]