#!/bin/bash

#
# Whether to enable USB networking interface in RPi Image for debugging
export PI_DEBUG=true

#
# Setup ARM emulation and packer
#

PACKER_VERSION="1.7.4"

# Update the system
echo "Updating Vagrant box..."
sudo apt-get update &>/dev/null
sudo apt-get -y upgrade &>/dev/null
sudo apt-get -y autoremove &>/dev/null
sudo apt-get clean

# Install required packages
echo "Installing build tools..."
sudo apt-get install -y \
  qemu-user-static \
  e2fsprogs \
  parted \
  qemu-utils \
  ca-certificates \
  dosfstools \
  gdisk \
  kpartx \
  libarchive-tools \
  git \
  golang-go \
  unzip &>/dev/null
sudo apt-get clean

# Download and install packer
command -v packer >/dev/null 2>&1 || {
  echo "Installing packer..."
  wget -q https://releases.hashicorp.com/packer/${PACKER_VERSION}/packer_${PACKER_VERSION}_linux_amd64.zip -O /tmp/packer.zip &>/dev/null
  sudo unzip /tmp/packer.zip -d /bin &>/dev/null
  rm /tmp/packer.zip
}

# Download and build packer-builder-arm
if [ ! -f /vagrant/packer-builder-arm ]; then
  echo "Installing packer-builder-arm provisioner..."
  git clone https://github.com/mkaczanowski/packer-builder-arm &>/dev/null
  cd packer-builder-arm
  go mod download &>/dev/null
  go build &>/dev/null
  cp packer-builder-arm /vagrant/
fi

# Build
cd /vagrant
echo "Building image..."
host raspbian.raspberrypi.org &>/dev/null # ensure updates will work
host archive.raspberrypi.org &>/dev/null # ensure updates will work
sudo PI_DEBUG=$PI_DEBUG packer build packer.json
