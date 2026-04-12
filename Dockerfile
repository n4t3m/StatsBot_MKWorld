
FROM mcr.microsoft.com/devcontainers/python:1-3.13

WORKDIR /app

COPY . .

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_LINK_MODE=copy

RUN uv sync --no-dev

CMD [ "uv", "run", "src/main.py"]