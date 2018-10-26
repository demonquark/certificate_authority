FROM nginx:1.14.0-alpine

# Copy the configuration files
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY certificate_authority.conf /etc/nginx/conf.d/

# Install openssl
RUN apk update && apk add openssl

# Create a dhparam
RUN mkdir -p /etc/nginx/dhparam
RUN openssl dhparam -out /etc/nginx/dhparam/dhparam.pem 4096

