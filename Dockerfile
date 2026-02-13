FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv

RUN uv sync --no-dev

RUN uv run playwright install chromium
RUN uv run playwright install-deps chromium

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uv", "run", "heya", "web", "--host", "0.0.0.0", "--port", "7860"]
