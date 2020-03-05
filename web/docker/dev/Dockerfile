FROM nginx:latest
ENV NODEJS_IP_ADDRESS=$NODEJS_IP_ADDRESS
RUN apt-get update \
    && apt-get install -y wget \
    && apt-get install -y iproute2
COPY web/src /usr/share/nginx/html/
RUN chmod 644 /usr/share/nginx/html/index.html \
    && chmod 755 /usr/share/nginx/html/js \
    && chmod 644 /usr/share/nginx/html/js/* \
    && chmod 755 /usr/share/nginx/html/css \
    && chmod 644 /usr/share/nginx/html/css/* \
    && chmod 755 /usr/share/nginx/html/images \
    && chmod 644 /usr/share/nginx/html/images/*
COPY web/bin/nginx-startup.sh /tmp/
RUN chmod +x /tmp/nginx-startup.sh
CMD ["/tmp/nginx-startup.sh"]
EXPOSE 80
