# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# Build deps for the rgbmatrix C++ bindings (python3.11-dev matches the
# bookworm-based image's interpreter).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git python3.11-dev cython3 \
    && rm -rf /var/lib/apt/lists/*

# Build and install the LED matrix bindings (GPL-2.0, optional hardware dep).
RUN git clone --depth=1 https://github.com/hzeller/rpi-rgb-led-matrix.git /opt/rpi-rgb-led-matrix \
    && make -C /opt/rpi-rgb-led-matrix build-python PYTHON="$(which python3)" \
    && pip install --no-cache-dir /opt/rpi-rgb-led-matrix/bindings/python

# Install the app (editable: fonts resolve relative to /app).
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY assets ./assets
RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "matrix_controller"]
