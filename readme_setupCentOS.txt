// https://github.com/VishalSharma0309/nano_drone
// Operating System: CentOS 7
// last updated: August 5, 2020

--------------------------------------------------------------
SETTING UP DEPENDENCIES
--------------------------------------------------------------

1. Install anaconda

	1.1 Download installer: 64-Bit Installer for Python 3.7
		https://www.anaconda.com/products/individual

	1.2 Run the following command and follow the prompts
		bash Anaconda-latest-Linux-x86_64.sh

	1.3 Refresh the terminal
		exec $SHELL


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
	
2. Getting the repository 

	git clone --recursive https://github.com/pulp-platform/pulp-riscv-gnu-toolchain

3. Activate conda environment

	conda activate pulp

4. Installation (PULP) 

	./configure --prefix=/volume1/users/vsharma/riscv --with-arch=rv32imc --with-cmodel=medlow --enable-multilib
	(please add --prefix as where you want to build the toolchain)
	
	make

6. PATH Defination: Add the following to your ~/.bashrc file
	
	For PULP SDK:
	export PULP_RISCV_GCC_TOOLCHAIN=/volume1/users/vsharma/riscv/bin
	
	For GAP SDK:
	export GAP_RISCV_GCC_TOOLCHAIN=/volume1/users/vsharma/riscv

-----------------------------------------------------------------------
SETTING UP GAP SDK	
-----------------------------------------------------------------------
	
1. Installing Pre-requisites
	
	conda install automake
	conda install pkg-config
	conda install libtool
	conda install -c psi4 gcc-5
