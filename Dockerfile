# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Build deps for the rgbmatrix C++ bindings. The official python image ships
# its own interpreter (with headers) under /usr/local, so no python*-dev apt
# package is needed — Debian's archive doesn't carry one for this version.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Build and install the LED matrix bindings (GPL-2.0, optional hardware dep).
# Pinned to the last upstream commit before the 2026 packaging rework: the
# newer pip-from-repo-root path needs Pillow's private C headers (Imaging.h)
# and does not build on a stock image. Keep this ref in sync with the
# `hardware` extra in pyproject.toml.
ARG RGBMATRIX_REF=2f72a32b3deea16d2b8e9b281d0475ef3b1d0d72
RUN pip install --no-cache-dir cython \
    && git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix \
    && git -C /opt/rpi-rgb-led-matrix checkout --quiet "${RGBMATRIX_REF}" \
    && make -C /opt/rpi-rgb-led-matrix build-python PYTHON="$(which python3)" \
    && pip install --no-cache-dir /opt/rpi-rgb-led-matrix/bindings/python

# Install the app (editable: fonts resolve relative to /app).
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY assets ./assets
RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "matrix_controller"]
