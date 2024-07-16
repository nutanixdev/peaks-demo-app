sudo lvdisplay

sudo pvcreate /dev/sdb

sudo vgextend ubuntu-vg /dev/sdb

sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv

sudo resize2fs /dev/ubuntu-vg/ubuntu-lv

df -h
