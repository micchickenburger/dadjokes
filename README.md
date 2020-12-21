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
3. Write to SD card: `$ sudo dd if=raspberry-pi.img of=/dev/disk4 bs=4096`.  Don't forget to
   replace `/dev/disk4` with the proper block device for your micro SD card

## Cleanup

When you're done you can free up disk space by destroying the vagrant environment and removing
the temporary files.

```bash
$ vagrant destroy
$ rm -rf raspberry-pi.img packer-builder-arm packer_cache .vagrant
```

## License

The font included in this project is [Indie Flower](https://fonts.google.com/specimen/Indie+Flower?query=indie#about)
by Kimberly Geswein. It is released under the [Open Font License](https://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL).

The Dad Jokes content comes mostly from [@DadJokes](https://twitter.com/dadjokes). Some have
been rewritten to better fit the display, and to add variety to pronouns and minimize gender
roles where they don't add value to the joke.

All other content &copy;2020 Micah Henning.  All Rights Reserved.  Source code and 3D model
released under the MIT License.
