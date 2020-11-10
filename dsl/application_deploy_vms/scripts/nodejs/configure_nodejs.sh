sudo mkdir -p /var/www/html/

echo '#!/bin/bash
export MONGODB_HOST='@@{Mongo DB.address}@@'
/usr/bin/node /var/www/html/app.js' | sudo tee /var/www/html/runnode.sh

sudo chmod 700 /var/www/html/runnode.sh

echo '[Unit]
Description=NodeJs app

[Service]
ExecStart=/var/www/html/runnode.sh
Restart=always
User=root
Group=root
Environment=PATH=/usr/bin:/usr/local/bin
Environment=NODE_ENV=production
WorkingDirectory=/var/www/html

[Install]
WantedBy=multi-user.target' | sudo tee /etc/systemd/system/nodejsapp.service

cd /var/www/html/
sudo wget --user @@{Artifactory Credential.username}@@ --password @@{Artifactory Credential.secret}@@ -O /var/www/html/nodejs-app.tar.gz http://@@{artifactory_ip}@@:8081/artifactory/@@{project_name}@@-local-repo/@@{project_name}@@@@{build_number}@@/nodejs-app.tar.gz
sudo tar xvfz /var/www/html/nodejs-app.tar.gz

sudo systemctl start nodejsapp
sudo systemctl enable nodejsapp

