FROM python:3.14-slim

WORKDIR /app

COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && apt-get update \
    && apt-get install -y --no-install-recommends texlive-latex-extra texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

COPY backend /app/backend
COPY data /app/data
COPY templates /app/templates

ENV PYTHONPATH=/app
EXPOSE 5001

CMD ["sh", "-c", "alembic -c /app/backend/alembic.ini upgrade head && python -m backend.run"]
