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

sudo yum install -y epel-release
sudo yum install -y nginx

sudo systemctl start nginx

sudo firewall-cmd --permanent --zone=public --add-service=http 
sudo firewall-cmd --permanent --zone=public --add-service=https
sudo firewall-cmd --reload

sudo yum install -y wget
