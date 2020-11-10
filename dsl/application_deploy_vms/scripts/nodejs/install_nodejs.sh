echo "Install Epel Repositories"
sudo yum install -y epel-release

echo "Install Node.js"
sudo yum install -y nodejs

echo "Check Version"
node -v

echo "Configure firewall"
sudo firewall-cmd --permanent --zone=public --add-port=3000/tcp
sudo firewall-cmd --permanent --add-service='ssh'
sudo firewall-cmd --reload

sudo yum install -y wget
