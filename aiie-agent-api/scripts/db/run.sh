docker run -d \
  --name postgres \
  -e POSTGRES_DB=temp \
  -e POSTGRES_USER=archer \
  -e POSTGRES_PASSWORD=Astra@2025!@#$ \
  -p 30432:5432 \
  -v ~/volumes/postgres:/var/lib/postgresql/data \
  postgres:latest