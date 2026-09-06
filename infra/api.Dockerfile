FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY ml/recsys ./ml/recsys
RUN pip install --no-cache-dir uv && uv sync --locked --no-dev

COPY apps/api ./apps/api

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/apps/api

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
