echo "Updating MongoDB Repositories"
echo '[mongodb-org-5.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/5.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-5.0.asc' | sudo tee /etc/yum.repos.d/mongodb-org.repo

echo "Output repository list"
sudo yum repolist

echo "Install MongoDB"
sudo yum install -y mongodb-org

echo "Update mongod.conf to allow connections from anywhere"
sudo sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/g' /etc/mongod.conf 

echo "Enable MongoDB Service"
sudo systemctl enable mongod

echo "Start MongoDB Service"
sudo systemctl restart mongod

echo "Configure firewall"
sudo firewall-cmd --permanent --zone=public --add-port=27017/tcp
sudo firewall-cmd --permanent --add-service='ssh'
sudo firewall-cmd --reload

echo "Install wget"
sudo yum install -y wget

