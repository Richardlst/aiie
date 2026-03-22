docker rm -f agent-api
docker rmi agent-api

docker build -t agent-api .

docker run -d --env-file .env.production -p 8000:8000 --name "agent-api" agent-api