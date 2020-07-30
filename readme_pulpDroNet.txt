// https://github.com/VishalSharma0309/nano_drone
// Operating System: Ubuntu 18.04
// last updated: Aug 7, 2020



SETTING UP THE ENVIRONMENT

1. Installing the PULP-SDK
        2.1 Ubuntu dependencies
        sudo apt install git python3-pip python-pip gawk texinfo libgmp-dev libmpfr-dev libmpc-dev swig3.0 libjpeg-dev lsb-core doxygen python-sphinx sox graphicsmagick-libmagick-dev-compat libsdl2-dev libswitch-perl libftdi1-dev cmake scons libsndfile1-dev
        sudo pip3 install artifactory twisted prettytable sqlalchemy pyelftools 'openpyxl==2.6.4' xlsxwriter pyyaml numpy configparser pyvcd
        sudo pip2 install configparser

* NOTE: if "pip install" doesn't work, try "python3 -m pip install" or see if pi
p and python3 are using the same version of python

* NOTE: for Ubuntu 18 or newer, it is needed to configure the default gcc versio
n to 5 as more recent gcc versions make the build fail

To check: g++ --version

To change: 
	i. Install packages
        sudo apt-get install gcc-5 g++-5

        ii. Install alternatives
        sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 10

        sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 10

        sudo update-alternatives --install /usr/bin/cc cc /usr/bin/gcc 30
        sudo update-alternatives --set cc /usr/bin/gcc

        sudo update-alternatives --install /usr/bin/c++ c++ /usr/bin/g++ 30
        sudo update-alternatives --set c++ /usr/bin/g++

        iii. Configure Alternatives
        sudo update-alternatives --config gcc
        sudo update-alternatives --config g++


2 Setting up pulp-riscv-gnu-toolchain 

	sudo -s
	
	apt install git python3-pip python-pip gawk texinfo libgmp-dev libmpfr-dev libmpc-dev swig3.0 libjpeg-dev lsb-core doxygen python-sphinx sox graphicsmagick-libmagick-dev-compat libsdl2-dev libswitch-perl libftdi1-dev cmake scons libsndfile1-dev
	
	pip3 install twisted prettytable artifactory sqlalchemy pyelftools xlsxwriter pyyaml numpy configparser pyvcd
	pip3 install openpyxl==2.6.4
	pip2 install configparser

	cd /opt

	mkdir riscv

	cd ~/nano_drone/pulp-riscv-gnu-toolchain

	apt-get install autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev

	./configure --prefix=/opt/riscv --with-arch=rv32imc --with-cmodel=medlow --enable-multilib

	make

	export PATH=$PATH:/opt/riscv/bin
	export PULP_RISCV_GCC_TOOLCHAIN=/opt/riscv

3. Setting up PULP-SDK
	
	cd ~/nano_drone/pulp-builder

	NOTE: The git clone command for pulp-builder doesn't clone the sub-modules properly for some reason
		To make this work we have to remove all the folders created for these sub-modules and git clone them individually

	Removing the sub-module folders (empty)
	
	sudo rm -rf json-tools plptest pulp-configs pulp-runtime runner

	Git Cloning these individually
	
	sudo -s
	git clone https://github.com/pulp-platform/json-tools.git
	git clone https://github.com/pulp-platform/plptest.git
	git clone https://github.com/pulp-platform/pulp-configs.git
	git clone https://github.com/pulp-platform/pulp-runtime.git
	git clone https://github.com/pulp-platform/runner.git
	
	source configs/pulp.sh

	./scripts/build-runtime

	
	cd ~/pulp-sdk

	source configs/pulp.sh

	make all

	export PULP_SDK_HOME=/home/vishal/pulp-sdk


	3.1 Install Simulation and implementation

		Install QuestaSim
	
		cd ~/nano_drone/pulpissimo
		git submodule init
		git submodule update

		./update-ips

		source setup/vsim.sh

		make clean build
	
		
		3.1.1 Verify that the following packages are installed with the proper version

		autoconf --version >=2.64 (mine is 2.69)
		automake --version >=1.14 (mine is 1.15.1)
		pkg-config --version >= 0.23 (mine is 0.29.1) 				
		texinfo (mine is 6.5.0.dfsg.1-2)
		make (mine is 4.1)
		libtool (mine is 2.4.6)
		libusb-1.0 (mine is 2:1.0.21-2)
		libftdi (mine is 0.20-4build3)
		libusb-0.1 or libusb-compat-0.1 for some older drivers (mine is 0.1-4)


		3.1.2 Install Microprocessor programming and debugging
		
		cd /opt/riscv/pulp-sdk

		source sourceme.sh && ./pulp-tools/bin/plpbuild checkout build --p openocd --stdout


4. Download the Basic Kernels
	
	cd ./pulp-dronet
	git submodule init 
	git submodule update 

	To check if its done correctly
	ls ~/pulp-dronet/src/autotiler 

	Result should be something like this
	get_tiler.py  include  LICENSE  Makefile  src

	
5. Install the Autotiler

	cd ~/pulp-dronet/src/autotiler
	make all			
	
	To check 
	ls ~/pulp-dronet/autotiler/src
	Result should be like
	libtile.a  libtile.dronet.a
	
	

6. Download the datasets
	
	PULP-DroNet dataset considered:
 		i. Himax Dataset https://github.com/pulp-platform/Himax_Dataset
    		ii. Udacity Dataset https://github.com/pulp-platform/Udacity_Dataset
    		iii. Zurich Bicycle Dataset https://github.com/pulp-platform/Zurich_Bicycle_Dataset

				
	cd ./pulp-dronet
	git submodule init -- dataset/
	git submodule update -- dataset/



7. Compile PULP-DroNet

For platform, compilation and target settings set it in the autocompiler/src/config.h file

sudo apt-get install gtk2.0

To configure the PULP-SDK executing in your terminal
source ~/pulp-sdk/configs/gap.sh

Depending upon your target platform source one of the below scripts
source ~/pulp-sdk/configs/platform-gvsoc.sh  // virtual platform (currently used by me)
source ~/pulp-sdk/configs/platform-board.sh  // if target is either PULP-Shield or GAPuino board


cd ./pulp-dronet/src

make clean conf all

/* THIS COMMAND IS NOT WORKING

Error message:
AttributeError: 'NoneType' object has no attribute 'name'
/home/vishal/pulp-sdk/pkg/sdk/dev/install/rules/pulp_rt.mk:55: recipe for target 'genconf' failed
make: *** [genconf] Error 1

*/	





	

