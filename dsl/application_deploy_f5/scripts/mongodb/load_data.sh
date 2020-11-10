# Stay out of home dir as some issues arise with SSH Key auth if tar file is unpacked incorrectly.
cd /tmp/

echo "Download MongoDB insert script"
sudo wget --user @@{Artifactory Credential.username}@@ --password @@{Artifactory Credential.secret}@@ -O /tmp/db.tar.gz  http://@@{artifactory_ip}@@:8081/artifactory/@@{project_name}@@-local-repo/@@{project_name}@@@@{build_number}@@/db.tar.gz 
cd /tmp/

echo "Unpack MongoDB insert script"
sudo tar xvfz /tmp/db.tar.gz -C /tmp/

echo "Load MongoDB data"
mongo demodb < /tmp/collections.json

