FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app
COPY pyproject.toml ./
COPY tsdl_cloud ./tsdl_cloud
RUN pip install --no-cache-dir .

RUN adduser --disabled-password --gecos "" --uid 10001 appuser
USER appuser

CMD ["sh", "-c", "uvicorn tsdl_cloud.app:application_from_environment --factory --host 0.0.0.0 --port ${PORT}"]

