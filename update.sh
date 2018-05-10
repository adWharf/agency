docker stop agency || true
docker rm -v agency || true
docker build -t agency .
docker run -v 5000:5000 --rm --name agency agency