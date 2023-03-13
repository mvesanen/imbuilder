docker build -t imbuilder .
docker tag imbuilder:latest mvesanen/imbuilder:latest
docker push mvesanen/imbuilder:latest
