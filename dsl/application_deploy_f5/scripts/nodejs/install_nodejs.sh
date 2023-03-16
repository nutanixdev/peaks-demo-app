sudo yum install -y wget
curl "https://nodejs.org/dist/v17.9.1/node-v17.9.1-linux-x64.tar.gz" > "$HOME/nodejs.tar.gz"

sleep 3

tar xvf nodejs.tar.gz

sleep 3

sudo mkdir /usr/local/bin/nodejs
sudo mv node-v17.9.1-linux-x64/* /usr/local/bin/nodejs/
ls -al node-v17.9.1-linux-x64
rm -rf node-v17.9.1-linux-x64

export PATH=$PATH:/usr/local/bin/nodejs/bin
echo "PATH=$PATH:/usr/local/bin/nodejs/bin" >> ~/.bashrc

echo""
echo "Node Version"
node --version
echo""
echo "NPM Version"
npm --version

