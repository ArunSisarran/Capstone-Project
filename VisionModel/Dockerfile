FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.14.0 "torchvision==0.29.*" --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY serve.py ingredients.csv ./
COPY runs/merged-v2/best.pt runs/merged-v2/best.pt

EXPOSE 8000
CMD ["python", "serve.py", "--port", "8000"]