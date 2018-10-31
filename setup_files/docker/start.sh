docker volume create --name neuroboun_postgresql-volume
docker build -f ./Dockerfile-postgres -t neuroboun_postgres ../../../NeuroBoun

docker build -f ./Dockerfile-python -t neuroboun_python ../../../NeuroBoun

docker-compose up -d
