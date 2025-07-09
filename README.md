docker build -t pointage_image:latest .

docker run -d -p port_host:port_container -v --name pointage pointage_image:latest
