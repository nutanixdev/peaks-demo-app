sudo mv /etc/yum.repos.d/CentOS-Base.repo /tmp/CentOS-Base.repo.bak
sudo bash -c 'cat << \EOF > /etc/yum.repos.d/CentOS-Base.repo
[base]
name=CentOS-$releasever - Base
#mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
baseurl=http://archive.kernel.org/centos-vault/7.9.2009/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
EOF'
sudo yum clean all

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

