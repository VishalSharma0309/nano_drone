// https://github.com/VishalSharma0309/nano_drone
// Operating System: CentOS 7
// last updated: July 6, 2020

--------------------------------------------------------------
SETTING UP DEPENDENCIES
--------------------------------------------------------------

1. Install anaconda

	1.1 Download installer: 64-Bit Installer for Python 3.7
		https://www.anaconda.com/products/individual

	1.2 Run the following command and follow the prompts
		bash Anaconda-latest-Linux-x86_64.sh

	1.3 Open a new terminal for the changes to take effect


2. Create a virtual environment to install dependencies

	conda env create -f pulpsdk.yml

	here pulpsdk.yml is an argument. (please find this file in the repository as nano_drone/pulpsdk.yml)

3. To activate this environment, use

	conda activate pulp

4. Installing python3
	
	4.1 Installing pyenv
		
		curl https://pyenv.run | bash
		
		exec $SHELL

	4.2 Source them in ~/.bashrc

		export PATH="/users/micasgst/vsharma/.pyenv/bin:$PATH"
		eval "$(pyenv init -)"
		eval "$(pyenv virtualenv-init -)"

	4.3 Installing python2 and python3
		
		pyenv install 2.7.14
		pyenv install 3.6.3

 		exec $SHELL

	4.4 Declaring them as global

		pyenv global 3.6.3
		pyenv global 2.7.14

		exec $SHELL

	4.5 Test 
		
		python --version (should give 2.7.14)
		python3 --version (should give 3.6.3)


----------------------------------------------------------------
SETTING UP PULP-RISCV-GNU-TOOLCHAIN
----------------------------------------------------------------

1. Creating directory for installation

	mkdir riscv
	cd riscv

2. Getting the repository

	git clone --recursive https://github.com/pulp-platform/pulp-riscv-gnu-toolchain

3. Installing prerequisites

	yumdownloader --destdir ~/rpm --resolve autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev

4. Activate conda environment

	conda activate pulp

5. Installation (PULP) 

	./configure --prefix=/users/micasgst/vsharma/riscv --with-arch=rv32imc --with-cmodel=medlow --enable-multilib
	(where /users/micasgst/vsharma/ is the home directory, you can obtain yours by cd and then pwd)
	
	make

6. PATH Defination: Add the following to your ~/.bashrc file

	export PULP_RISCV_GCC_TOOLCHAIN=/users/micasgst/vsharma/riscv
	export VSIM_PATH=/users/micasgst/vsharma/pulpissimo/sim




	

	

