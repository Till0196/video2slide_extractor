FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

RUN pip install uv

COPY requirements.txt .
COPY pyproject.toml .

RUN uv pip install --system -r requirements.txt

FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

COPY video2slide_extractor.py .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh


ENTRYPOINT ["./entrypoint.sh"] 
