#!/bin/bash
sed -i 's/NODEJS_IP_ADDRESS/'${NODEJS_IP_ADDRESS}'/' /usr/share/nginx/html/js/data.js
sed -i 's/WEB_IP_ADDRESS/'`ip address show dev eth0 | grep "inet" | grep -v "inet6" | cut -d '/' -f1 | cut -d ' ' -f6`'/' /usr/share/nginx/html/index.html
sed -i 's/WEB_SERVER_NAME/'${HOSTNAME}'/' /usr/share/nginx/html/index.html
exec nginx -g 'daemon off;'
