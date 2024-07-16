sudo apt update -y
sudo apt install -y nginx

sudo ufw allow 'Nginx HTTP'

sudo service nginx restart

sudo apt install -y wget

echo "complete"
