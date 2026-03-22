docker build -t srgan-api .

docker run -d \
  -p 8021:8001 \
  -v ~/volumes/aiie-srgan-api:/code/models \
  -e MINIO_ENDPOINT=minio.astratech.vn \
  -e MINIO_ACCESS_KEY=bachnh \
  -e MINIO_SECRET_KEY=22122003 \
  -e MINIO_RETURN_ENDPOINT=minio.astratech.vn \
  -e MINIO_SECURE=true \
  --gpus all \
  --name srgan-api \
  srgan-api
