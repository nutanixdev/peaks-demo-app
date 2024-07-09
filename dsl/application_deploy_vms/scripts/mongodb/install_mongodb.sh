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

