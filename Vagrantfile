# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"
  config.vm.synced_folder "./", "/vagrant", disabled: false
  config.vm.provider "vmware_desktop" do |v|
    v.linked_clone = false
    v.ssh_info_public = true
  end
  config.vm.provision "build", type: "shell", :path => "build.sh", privileged: false, env: {
    "DADJOKES_MODE" => ENV["DADJOKES_MODE"],
    "PI_DEBUG" => ENV["PI_DEBUG"]
  }
end
