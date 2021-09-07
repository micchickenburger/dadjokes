[![Creative Commons Logo][CC]![Attribution Logo][BY]![Share Alike Logo][SA]][License]

Dad Jokes Keychain
========================================

The Dad Jokes keychain was a project I did as a Christmas gift for a dear friend of mine
who, thankfully for me, loves bad jokes.

## Preparations

To assemble, you will need:
* A Raspberry Pi Zero with Headers (you can solder your own headers on, too)
* A Waveshare 2.13 v2 e-Paper screen
* A UPS-Lite v1.2 battery module.  You could use a different battery, but then you will
  have to modify the case and you would lose the battery life indicator
* A fast micro SD card (8GB or larger recommended)
* A 3D printer or use of a 3D printing service to print the case
* A keyring. I printed an origami carabiner but any keyring will work
* A soldering iron and solder
* Superglue
* A pushbutton switch
* A 220 Ohm resistor
* ~10cm of 22AWG solid wire

If you want or need to debug/log into the system, you will also need a micro USB cable that
supports data transfer.

## Build

This project uses HashiCorp Vagrant to create a build environment for building the Raspberry
Pi image.  The build environment is based on Ubuntu Focal and the Raspberry Pi image is based
on Raspbian Lite and is built using HashiCorp Packer.

1. Install Vagrant
2. Build: `$ vagrant up`
3. Write to SD card: `$ sudo dd if=dadjokes.img of=/dev/disk4 bs=4096`.  Don't forget to
   replace `/dev/disk4` with the proper block device for your micro SD card

## Developing

By default all networking and video output services and interfaces are disabled to conserve
battery life.  There is a debug mode available during vagrant provision that will leave these
interfaces enabled so you can SSH into the device via the data microUSB interface.

```bash
# When provisioning
$ PI_DEBUG=true vagrant provision
# Configure your RNDIS interface with IPv4 address 10.0.0.1/24
$ ssh pi@10.0.0.2 # password is raspberry
# This project uses a systemd service
$ sudo systemctl status jokes
# View logs
$ sudo journalctl -u jokes
```

## Cleanup

When you're done you can free up disk space by destroying the vagrant environment and removing
the temporary files.

```bash
$ vagrant destroy
$ rm -rf dadjokes.img packer-builder-arm packer_cache .vagrant
```

## License

The font included in this project is [Indie Flower][Font] by Kimberly Geswein. It is released
under the [Open Font License][OFL].

The Dad Jokes content comes mostly from [@DadJokes][Jokes]. Some have been rewritten to better
fit the display, and to add variety to pronouns and minimize gender roles where they don't add
value to the joke.

All other content &copy;2020 Micah Henning. Licensed under
[Creative Commons Attribution-ShareAlike 4.0 International][License]

[License]: https://creativecommons.org/licenses/by-sa/4.0?ref=chooser-v1
[CC]: https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1 "Creative Commons"
[BY]: https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1 "Attribution Required"
[SA]: https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1 "Share Alike"
[Jokes]: https://twitter.com/dadjokes "Dad Jokes Twitter Feed"
[Font]: https://fonts.google.com/specimen/Indie+Flower?query=indie#about "Indie Flower"
[OFL]: https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL "Open Font License"
