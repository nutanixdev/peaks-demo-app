cd /var/www/html
sudo rm *
sudo wget --user @@{Artifactory Credential.username}@@ --password @@{Artifactory Credential.secret}@@ http://@@{artifactory_ip}@@:8081/artifactory/@@{project_name}@@-local-repo/@@{project_name}@@@@{build_number}@@/web.tar.gz
sudo tar xvfz web.tar.gz
sleep 2

sudo sed -i 's/NODEJS_IP_ADDRESS/@@{NodeJS.address}@@/' /var/www/html/js/data.js
sudo sed -i 's/WEB_IP_ADDRESS/'`/usr/sbin/ip address show dev ens3 | grep "inet" | grep -v "inet6" | cut -d '/' -f1 | cut -d ' ' -f6`'/' /var/www/html/index.html
sudo sed -i 's/WEB_SERVER_NAME/'`hostname`'/' /var/www/html/index.html

sudo chmod 644 index.html
sudo chmod 755 css/
sudo chmod 755 js/
sudo chmod 755 images/
sudo chmod 644 css/*
sudo chmod 644 js/*
sudo chmod 644 images/*
