docker build -t sd-api .

docker run -d \
 -p 8022:8002 \
 -e MINIO_ENDPOINT=minio.astratech.vn \
 -e MINIO_ACCESS_KEY=bachnh \
 -e MINIO_SECRET_KEY=22122003 \
 -e MINIO_RETURN_ENDPOINT=minio.astratech.vn \
 -v ~/volumes/aiie-sd-api/models:/code/models \
 -v ~/volumes/aiie-sd-api/cache:/root/.cache/huggingface \
 --gpus all \
 --name=sd-api sd-api