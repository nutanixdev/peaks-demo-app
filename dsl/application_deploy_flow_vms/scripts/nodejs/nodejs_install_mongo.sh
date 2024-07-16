sudo apt-get update -y
sudo apt-get install -y mongodb-org


echo "Enable MongoDB Service"
sudo systemctl disable mongod

echo "Start MongoDB Service"
sudo service mongod stop

