# Copyright (C) 2018 Krishna Moniz

# This image functions a base for Celery workers, and thus does not contain ENV or CMD.
# The starting CMD and ENV variables should be specified in your docker-compose.yaml
# The app files should also be copied by binding a volume
# Likely setup:
# services:
#   worker:
#       volumes:
#           - ./web:/srv/www/certificate_authority/site
#           - ./config:/srv/www/certificate_authority/config/custom
#       environment:
#           - CONFIG_FILE=/srv/www/certificate_authority/config/custom/config.ini
#       command: celery worker -A celery.tasks --loglevel=info
# For deployment, you should make a new Dockerfile incorporating the above.
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

# Start the target image
FROM python:3.6-alpine3.8

# Create the user to be used in this image
RUN adduser -S -D -H gebruiker

# Copy the configuration files to the image (and a copy of the Dockerfile for reference)
RUN mkdir -p /srv/www/certificate_authority/config
COPY requirements.txt /srv/www/certificate_authority/config/
COPY Dockerfile /srv/www/certificate_authority/config/

# Install the required python packages for Celery
# This step is done at the image level, to avoid having to
# re-install python packages whenever we restart a container.
RUN pip install --no-cache-dir -r /srv/www/certificate_authority/config/requirements.txt

# Create the working directory (and set it as the working directory)
RUN mkdir -p /srv/www/certificate_authority/site
WORKDIR /srv/www/certificate_authority/site

# Give the user ownership of the working directory
RUN chown -R gebruiker /srv/www/certificate_authority
USER gebruiker
