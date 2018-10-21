FROM python:3.7-alpine3.7

# Create the group and user to be used in this container
RUN adduser -S -D -H gebruiker

# Create the working directory (and set it as the working directory)
RUN mkdir -p /srv/www/certificate_authority/web
WORKDIR /srv/www/certificate_authority/web

# Install the package dependencies (this step is separated
# from copying all the source code to avoid having to
# re-install all python packages defined in requirements.txt
# whenever any source code change is made)
COPY requirements.txt /srv/www/certificate_authority/web
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy the source code into the container
COPY . /srv/www/certificate_authority/web

RUN chown -R gebruiker /srv/www/certificate_authority/web
USER gebruiker
