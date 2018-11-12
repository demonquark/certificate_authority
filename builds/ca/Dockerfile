# Copyright (C) 2018 Krishna Moniz

# This image functions a base for Flask apps, and thus does not contain ENV or CMD.
# The starting CMD and ENV variables should be specified in your docker-compose.yaml
# The app files should also be copied by binding a volume
# Likely setup:
# services:
#   web:
#       volumes:
#           - ./web:/srv/www/certificate_authority/site
#           - ./config:/srv/www/certificate_authority/config/custom
#       environment:
#           - FLASK_APP=run.py
#           - FLASK_ENV=development
#           - PYTHONUNBUFFERED=1
#           - CONFIG_FILE=/srv/www/certificate_authority/config/custom/config.ini
#       command: gunicorn -b :8000 --access-logfile - --error-logfile - app:app
# For deployment, you should make a new Dockerfile incorporating the above 
# (Well... technically not the above, but the production version of the above).

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Start a builder image
FROM python:3.6-alpine3.8 as builder

# Install gcc on the builder
RUN apk update \
    && apk add --virtual build-dependencies \
        build-base \
        gcc \
        python-dev \
        musl-dev \
        libffi-dev \
        openssl-dev

# Install / compile the required packages on the builder
# Some packages will be built using gcc
# This step is done at the image level, to avoid having to
# re-install python packages whenever we restart a container.
COPY requirements.txt .
RUN pip install -r requirements.txt


# Start the target image
FROM python:3.6-alpine3.8

# Create the group and user to be used in this image
RUN adduser -S -D -H gebruiker

# Copy / install the required packages from the builder cache
COPY --from=builder /root/.cache /root/.cache
COPY --from=builder requirements.txt .
RUN pip install -r requirements.txt && rm -rf /root/.cache && rm -f requirements.txt

RUN  apk update \
  && apk add openssl \
  && rm -rf /var/cache/apk/*

# Copy the configuration files to the image (and a copy of the Dockerfile for reference)
RUN mkdir -p /srv/www/certificate_authority/config
COPY config.ini /srv/www/certificate_authority/config/
COPY requirements.txt /srv/www/certificate_authority/config/
COPY Dockerfile /srv/www/certificate_authority/config/
ENV CONFIG_FILE /srv/www/certificate_authority/config/config.ini

# Install gunicorn 
RUN pip install gunicorn

# Create the working directory (and set it as the working directory)
RUN mkdir -p /srv/www/certificate_authority/site
WORKDIR /srv/www/certificate_authority/site

# Give the user ownership of the working directory
RUN chown -R gebruiker /srv/www/certificate_authority
USER gebruiker
