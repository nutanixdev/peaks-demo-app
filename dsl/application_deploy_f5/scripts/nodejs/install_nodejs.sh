echo "Install Epel Repositories"
sudo yum install -y epel-release
sudo yum install -y nodejs

echo "Install Node.js"
curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
sudo yum install -y nodejs

echo "Configure firewall"
sudo firewall-cmd --permanent --zone=public --add-port=3000/tcp
sudo firewall-cmd --permanent --add-service='ssh'
sudo firewall-cmd --reload

sudo yum install -y wget

echo""
echo "Node Version"
node --version
echo""
echo "NPM Version"
npm --version
