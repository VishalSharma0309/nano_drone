// https://github.com/VishalSharma0309/nano_drone
// Operating System: Ubuntu 18.04
// last updated: Aug 7, 2020


SETTING UP THE GAP-SDK


1. Installing the pre-requisites

sudo apt-get install -y build-essential git libftdi-dev libftdi1 doxygen python3-pip libsdl2-dev curl cmake libusb-1.0-0-dev scons gtkwave libsndfile1-dev rsync autoconf automake texinfo libtool pkg-config libsdl2-ttf-dev

curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash

	sudo usermod -a -G dialout <username>

	// Logout from your session and login again.

	touch 90-ftdi_gapuino.rules
	echo 'ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010", MODE="0666", GROUP="dialout"'> 90-ftdi_gapuino.rules
	echo 'ATTRS{idVendor}=="15ba", ATTRS{idProduct}=="002b", MODE="0666", GROUP="dialout"'>> 90-ftdi_gapuino.rules
	sudo mv 90-ftdi_gapuino.rules /etc/udev/rules.d/
	sudo udevadm control --reload-rules && sudo udevadm trigger

2. Install the Toolchain

	cd ~/nano_drone/gap_riscv_toolchain_ubuntu_18
	sudo ./install.sh
	
3. Configure the SDK

	source gap_sdk/sourceme.sh

	// and select the target board

	// or you can source the target board directly

	config/gapuino.sh : GAPuino GAP8 v1
	config/gapuino_v2.sh : GAPuino GAP8 v2
	config/gapoc_a.sh : Gapoc GAP8 v1
	configs/gapoc_a_v2.sh : Gapoc GAP8 v2

Note: I was working on config/gapuino.sh i.e GAPuino GAP8 v1

4. OpenOCD

	Read: http://openocd.org/doc-release/README

	Packags Required	
	- make
	- libtool
	- pkg-config >= 0.23 (or compatible)
	- autoconf >= 2.64
	- automake >= 1.9
	- texinfo

	export GAPY_OPENOCD_CABLE=interface/ftdi/olimex-arm-usb-ocd-h.cfg

5. Build SDK

	cd ~/gap_sdk
	make all

6. Getting the Autotiler
	
	make autotiler

Note: If unable to get a URL for the same, paste the following link when prompted
https://greenwaves-technologies.com/autotiler/

7. Getting nntool
	
	make nntool
	
	Note: make sure you have tensorflow 1.15.0 installed and not 2.0
	To install for python3 (upto 3.7):
	python3 -m pip install tensorflow==1.15.0

8. Compiling, running and debugging

	source ~/gap_sdk/configs/gapuino.sh
	- Refer to (1) to select which platform to choose
	- This file has to be sourced everytime for every terminal
	- Can be added to ~/.bashrc file as 
	
	Finally try a test project. First connect your GAPuino to your PCs USB port and then type:	
	
	cd ~/gap_sdk/examples/pmsis/helloworld
	make clean all run	

9. Setting up the GVSOC Virtual Platform
	
	cd ~/gap_sdk
	make gvsoc

10. To run a program on the GVSOC virtual platform

	source ~/gap_sdk/configs/gapuino.sh
	
	cd ~/gap_sdk/examples/pmsis/helloworld
	make clean all run platform=gvsoc

	// output should be
		 *** PMSIS HelloWorld ***

	Entering main controller
	[32 0] Hello World!
	Cluster master core entry
	[0 4] Hello World!
	[0 3] Hello World!
	[0 2] Hello World!
	[0 1] Hello World!
	[0 7] Hello World!
	[0 5] Hello World!
	[0 0] Hello World!
	[0 6] Hello World!
	Cluster master core exit
	Test success !

	// for more options on GVOC platform
	https://gvsoc.readthedocs.io/en/latest/


11. Debugging Programs
	cd ~/gap_sdk
	source configs/gapuino_v2.sh
	make clean all gdbserver

	// cd to the program to run
	riscv32-unknown-elf-gdb BUILD/GAP8/GCC_RISCV/test

	// Once gdb has loaded connect to the gdbserver on the target
	(gbd) target remote localhost:1234
	Remote debugging using localhost:1234

12. Documentation
	cd ~/gap_sdk
	make docs

	cd docs
	make pdf

	


