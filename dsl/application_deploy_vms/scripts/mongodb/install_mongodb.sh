sudo apt-get update -y
sudo apt-get install -y mongodb-org

sudo sed -i 's/  bindIp: 127.0.0.1/  bindIpAll: true/' /etc/mongod.conf 


echo "Enable MongoDB Service"
sudo systemctl enable mongod

echo "Start MongoDB Service"
sudo service mongod restart


