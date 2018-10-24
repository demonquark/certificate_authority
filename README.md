# certificate_authority
Python implementation of a certificate authority to issue client certificates

# Instructions

Build all of the images in preparation for running your application:
```
$ docker-compose build
```

Using Docker Compose to run the multi-container application (in daemon mode):
```
$ docker-compose up -d
```

View the logs from the different running containers:
```
$ docker-compose logs
```

Stop all of the containers that were started by Docker Compose:
```
$ docker-compose stop
```

Bash into a specific container:
```
$ docker-compose run nginx /bin/sh
```

Check the containers that are running:
```
$ docker ps
```

Stop all running containers:
```
$ docker stop $(docker ps -aq)
```

Delete all running containers:
```
$ docker rm -f $(docker ps -aq)
```

Delete all created Docker images (note the `"^certificate-authority"` filter)
```
$ docker rmi $(docker image ls | grep "^certificate-authority" | awk '{print $3}')
```

Read a certificate file
```
$ openssl s_client -connect google.nl:443 -showcerts
```

Send a client request to the api
```
curl -v \
  --cacert ./nginx/root_ca/cert.pem \
  https://www.kris.local:8080/

```

Send a client request to the api
```
curl -v \
--cacert ./nginx/root_ca/cert.pem \
--cert ./nginx/client_crt/cert.pem \
--key ./nginx/client_crt/key.pem \
https://api.kris.local:8080/dienst/

```

Generate a more secure Diffie-Hellman parameter for nginx
```
openssl dhparam -out /etc/nginx/dhparam/dhparam.pem 4096
```

Create a pkcs file for the client certificate. You can import the pkcs12 file in Firefox.
```
openssl pkcs12 -export -in cert.pem -inkey key.pem -name "api.kris.local" -out client.p12
```