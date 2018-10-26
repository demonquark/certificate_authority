FROM python:3.7-alpine3.8

# Create the group and user to be used in this container
RUN adduser -S -D -H gebruiker

# Copy the config file
RUN mkdir -p /srv/www/certificate_authority/config
COPY config.ini /srv/www/certificate_authority/config/
COPY requirements.txt /srv/www/certificate_authority/config/
ENV CONFIG_FILE /srv/www/certificate_authority/config/config.ini

# Install the package dependencies (this step is separated
# from copying all the source code to avoid having to
# re-install all python packages defined in requirements.txt
# whenever any source code change is made)
RUN pip install --no-cache-dir -r /srv/www/certificate_authority/config/requirements.txt
RUN pip install gunicorn

# Create the working directory (and set it as the working directory)
RUN mkdir -p /srv/www/certificate_authority/site
WORKDIR /srv/www/certificate_authority/site

RUN chown -R gebruiker /srv/www/certificate_authority
USER gebruiker
