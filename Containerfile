FROM python:3.12.6-slim-bookworm

RUN apt update
RUN apt install -y curl gcc git libgl1-mesa-glx libsqlite3-dev libxcb-cursor0 python3-pyqt6 sqlite3

ENV UV_PROJECT_ENVIRONMENT=/.venv/

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /opt

COPY ./pyproject.toml .
RUN /root/.local/bin/uv sync

ENTRYPOINT ["/root/.local/bin/uv", "run", "python", "-m", "pizero_bikecomputer"]

# podman run --rm -it -e DISPLAY=$DISPLAY -v "$(pwd)":/opt -v /tmp/.X11-unix:/tmp/.X11-unix pizerobike:latest bash
