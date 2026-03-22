docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -v ~/volumes/minio/data:/data \
  -e "MINIO_ROOT_USER=bachnh" \
  -e "MINIO_ROOT_PASSWORD=22122003" \
  --name minio \
  minio/minio server /data --console-address ":9001"