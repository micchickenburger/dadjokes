#!/bin/bash

echo Updating system...
sudo apt-get update && sudo apt-get -y upgrade

echo Installing required sofware...
sudo apt-get install -y busybox-syslogd git i2c-tools python3 python3-pip python3-pil python3-numpy wiringpi
cd /tmp
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz
tar zxvf bcm2835-1.60.tar.gz
cd bcm2835-1.60/
./configure && make && sudo make install
sudo pip3 install RPi.GPIO spidev smbus2
cd .. && git clone https://github.com/waveshare/e-Paper
mv e-Paper/RaspberryPi_JetsonNano/python/lib/waveshare_epd /usr/lib/python3/dist-packages/

echo Creating systemd service...
ln -s /etc/systemd/system/jokes.service /etc/systemd/system/multi-user.target.wants/jokes.service
sudo chmod +x /usr/bin/jokes.py

echo Cleaning up...
sudo apt-get remove --purge -y triggerhappy logrotate dphys-swapfile rsyslog
sudo apt-get autoremove -y --purge
sudo apt-get clean
cd / && sudo rm -rf /tmp/bcm* && sudo rm -rf /tmp/e-Paper

echo Disabling Radios, HDMI, and system LED to conserve power...
echo 'dtoverlay=pi3-disable-wifi' | sudo tee -a /boot/config.txt
echo 'dtoverlay=pi3-disable-bt' | sudo tee -a /boot/config.txt
sudo sed -i '/^exit 0/i /usr/bin/tvservice -o' /etc/rc.local
echo 'dtparam=act_led_trigger=none' | sudo tee -a /boot/config.txt

echo Disabling unnecessary services to conserve power...
rm /etc/systemd/system/multi-user.target.wants/wpa_supplicant.service
rm /etc/systemd/system/timers.target.wants/{apt-daily,apt-daily-upgrade,man-db}.timer

echo Enabling i2c and spi for waveshare and ups-lite support...
echo 'dtparam=spi=on' | sudo tee -a /boot/config.txt
echo 'dtparam=i2c_arm=on' | sudo tee -a /boot/config.txt
echo 'i2c-dev' | sudo tee -a /etc/modules

if [ "$PI_DEBUG" = true ]; then
  echo Enable USB0 network interface for Debugging purposes...
  sudo sed -i '$ s/rootwait/rootwait modules-load=dwc2,g_ether/' /boot/cmdline.txt
  echo 'dtoverlay=dwc2' | sudo tee -a /boot/config.txt
  sudo touch /boot/ssh
  echo 'interface usb0' | sudo tee -a /etc/dhcpcd.conf
  echo 'static ip_address=10.0.0.2' | sudo tee -a /etc/dhcpcd.conf
  echo 'static routers=10.0.0.1' | sudo tee -a /etc/dhcpcd.conf
  echo 'static domain_name_servers=1.1.1.1' | sudo tee -a /etc/dhcpcd.conf
else
  echo Making filesystem readonly to extend sd card life...
  # Insert `fastboot noswap ro` immediately after rootwait
  sudo sed -i '$ s/rootwait/rootwait fastboot noswap ro/' /boot/cmdline.txt
  # Remove the init script to resize the disk since this won't work in readonly
  sudo sed -i 's/init=.*//' /boot/cmdline.txt
  # Add ro options to block devices in /etc/fstab
  sudo sed -i '/^PARTUUID/s/defaults/defaults,ro/g' /etc/fstab
  # Add tmpfs mountpoints to fstab
  echo 'tmpfs        /tmp            tmpfs   nosuid,nodev         0       0' | sudo tee -a /etc/fstab
  echo 'tmpfs        /var/log        tmpfs   nosuid,nodev         0       0' | sudo tee -a /etc/fstab
  echo 'tmpfs        /var/tmp        tmpfs   nosuid,nodev         0       0' | sudo tee -a /etc/fstab
  # Create symlinks for common system files to tmpfs
  sudo rm -rf /var/lib/dhcp /var/lib/dhcpcd5 /var/spool /etc/resolv.conf /var/lib/systemd/random-seed
  sudo ln -s /tmp /var/lib/dhcp
  sudo ln -s /tmp /var/lib/dhcpcd5
  sudo ln -s /tmp /var/spool
  sudo touch /tmp/dhcpcd.resolv.conf
  sudo ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf
  sudo ln -s /tmp/random-seed /var/lib/systemd/random-seed
  # Systemd should create random-seed file on startup
  sudo sed -i '/^ExecStart=/i ExecStartPre=/bin/echo "" > /tmp/random-seed' /lib/systemd/system/systemd-random-seed.service
  # Disable services that require rw fs
  sudo rm /etc/systemd/system/multi-user.target.wants/regenerate_ssh_host_keys.service
  sudo rm /etc/systemd/system/sysinit.target.wants/systemd-timesyncd.service
  sudo rm /etc/systemd/system/dbus-org.freedesktop.timesync1.service
  sudo rm /etc/systemd/system/multi-user.target.wants/dhcpcd.service
  sudo systemctl disable resize2fs_once.service
fi
