// https://github.com/VishalSharma0309/nano_drone
// Operating System: Ubuntu 18.04
// last updated: June 2, 2020


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

2. Download and Install the toolchain

	Clone the GAP8 SDK and GAP8/RISC-V toolchain

	git clone https://github.com/GreenWaves-Technologies/gap_sdk.git
	git clone https://github.com/GreenWaves-Technologies/gap_riscv_toolchain_ubuntu_18.git

3. Configure the SDK

	source gap_sdk/sourceme.sh

	// and select the target board

	// or you can source the target board directly

	config/gapuino.sh : GAPuino GAP8 v1
	config/gapuino_v2.sh : GAPuino GAP8 v2
	config/gapoc_a.sh : Gapoc GAP8 v1
	configs/gapoc_a_v2.sh : Gapoc GAP8 v2



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

	cd gap_sdk
	make all

6. Getting the Autotiler
	
	make autotiler

7. Getting nntool
	
	make nntool
	
	Note: make sure you have tensorflow 1.15.0 installed and not 2.0

8. Compiling, running and debugging

	source ~/gap_sdk/configs/gapuino_v2.sh
	// refer to (3) to select which platform to choose
	// this file has to be sourced everytime for every terminal
	// can be added to ~/.bashrc file

	// Finally try a test project. First connect your GAPuino to your PCs USB port and then type:	
	cd ~/gap_sdk/examples/pmsis/helloworld
	make clean all run	

9. Setting up the GVSOC Virtual Platform
	
	cd ~/gap_sdk
	make gvsoc

10. To run a program on the virtual platform

	source ~/gap_sdk/configs/gapuino_v2.sh
	// refer to (3) to select which platform to choose
	// this file has to be sourced everytime for every terminal
	// can be added to ~/.bashrc file

	// for example the program used in (8)	
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

	


