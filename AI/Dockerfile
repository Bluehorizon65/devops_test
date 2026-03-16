FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# OpenCV in headless containers still requires these shared libraries.
RUN apt-get update \
	&& apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
	&& rm -rf /var/lib/apt/lists/*

COPY api_requirements.txt ./
RUN pip install --no-cache-dir -r api_requirements.txt

COPY . .

ENV PORT=8005
EXPOSE 8005

CMD ["uvicorn", "rooftop_fastapi:app", "--host", "0.0.0.0", "--port", "8005"]
