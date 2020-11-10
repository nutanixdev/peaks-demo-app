echo "Updating MongoDB Repositories"
echo '[mongodb-org-3.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/3.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-3.4.asc' | sudo tee /etc/yum.repos.d/mongodb-org.repo

echo "Output repository list"
sudo yum repolist

echo "Install MongoDB"
sudo yum install -y mongodb-org

echo "Enable MongoDB Service"
sudo systemctl disable mongod

echo "Start MongoDB Service"
sudo systemctl stop mongod

