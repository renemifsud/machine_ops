#!/bin/bash 

sudo dnf groupinstall 'development tools' -y
sudo dnf install -y bzip2-devel expat-devel gdbm-devel \
    ncurses-devel openssl-devel readline-devel \
    sqlite-devel tk-devel xz-devel zlib-devel libffi-devel gcc wget tar

PYT_VERSION=3.7.7
wget https://www.python.org/ftp/python/${PYT_VERSION}/Python-${PYT_VERSION}.tgz
tar -xf Python-${PYT_VERSION}.tgz
cd Python-${PYT_VERSION}
./configure --enable-optimizations
make altinstall