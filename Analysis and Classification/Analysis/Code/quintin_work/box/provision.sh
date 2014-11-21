#!/bin/bash

echo "Script Start";

echo "Getting root access";
sudo -s

echo "Updating the OS";
apt-get update;
debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password vagrant';
debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password vagrant';

echo "Installing needed packages"
apt-get -y install make mysql-server vim git mysql-client nginx

echo "Installing Python packages..."
apt-get -y install make python-mysqldb python-tk
python /vagrant/python-libs/get-pip.py
pip install numpy
echo "Done installing Python dependencies"


echo "Restarting services"
service mysql restart

echo "done!"