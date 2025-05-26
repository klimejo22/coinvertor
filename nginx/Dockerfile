FROM nginx:alpine

COPY ../scripts/wait-for-it.sh /wait-for-it.sh

RUN chmod +x /wait-for-it.sh

COPY nginx/nginx.conf /etc/nginx/nginx.conf

COPY nginx/frontend/ /usr/share/nginx/html/

CMD ["/wait-for-it.sh", "api:8000", "--", "nginx", "-g", "daemon off;"]
