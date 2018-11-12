# UNDER CONSTRUCTION
The current version of this code is **incomplete**.
The goal of this project is to set up a docker network with certificate authority. Users should be able to:
- Register with the certificate authority and receive a pkcs12 package containing a key and TLS certificate
- Sign data with private keys
- Use their received pkcs12 key client authority to access and verify the signed data

As of now, **the code does not work**.
- The client authority code can be run from the command line (see `/ca/app/ca.py`)
- The project uses nginx as a reverse proxy (see `/builds/nginx/`)
- The project uses celery to manage background tasks

## Containers
There are 4 services
- API: this service is public facing and requires client authorization
- WEB: this service is public facing and does not require client authorization
- DIENST: this service uses private keys to digitally sign data
- CA: this service is the certificate authority

As with the rest of the code, this read me is also not complete. The text below is just some notes that might be useful during development.

# certificate_authority
Python implementation of a certificate authority to issue client certificates.

This version of the implementation is not complete

## Instructions

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

# Configuration files

- In the root/docker folder (.): `docker-compose.yaml`
- In the root/docker folder (.): `.env`
- In the web build folder (./builds/web): `config.ini`
- In the nginx build folder (./builds/nginx): `certificate_authority.conf`

## custom configuration
### web
For web buids, you can overwrite the default config.ini by specifying the `CONFIG_FILE` environment variable in docker-compose. Eg:
```
services
  custom_web:
    image: certificate-authority_web:latest
    environment:
      - CONFIG_FILE=/srv/www/certificate_authority/site/custom_config.ini
    volumes:
      - ./web:/srv/www/certificate_authority/site
```
### nginx
Not implemented
