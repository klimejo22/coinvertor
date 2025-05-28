FROM nginx:alpine

COPY key.pem /etc/nginx/ssl/key.pem

COPY cert.pem /etc/nginx/ssl/cert.pem

COPY nginx.conf /etc/nginx/nginx.conf

COPY frontend/ /usr/share/nginx/html/
