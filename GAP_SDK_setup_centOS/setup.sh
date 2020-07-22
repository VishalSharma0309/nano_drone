#!/bin/bash
# Disable automatic base env of anaconda
# https://stackoverflow.com/a/54560785
conda config --set auto_activate_base false
# Create conda env
conda create -p ./gap8_env
# Populate build variables for conda
export CONDA_BUILD=1
# Activate the conda env
conda activate ./gap8_env
# Reset CFLAGS, because anaconda sets it and it fails to complete the build for RISC-V compiler
export CFLAGS=""
# Start installing packages
# Switch to python version 3.7.6
conda install python=3.7.6
# Bulid essentials
conda install -y gxx_linux-64 -c defaults
conda install -y -c conda-forge glib 
# GIT
conda install -y git
# LIBFTDI
conda install -y -c m-labs libftdi

#LIBFTDI1
#NOT FOUND
#DOXYGEN
conda install -y -c conda-forge doxygen
#PIP
conda install -y -c conda-forge pip
#LIBSDL2
conda install -y -c conda-forge sdl2
#curl
conda install -y -c conda-forge curl
#CMAKE
conda install -y -c conda-forge cmake
#LIBUSB
conda install -y -c conda-forge libusb
#SCONS
conda install -y -c conda-forge scons
#GTKWAVE
conda install -y -c tfors gtkwave
#LIBSNDFILE
conda install -y -c conda-forge libsndfile
#rsync
conda install -y -c conda-forge rsync
#autoconf
conda install -y -c conda-forge autoconf
#automake
conda install -y -c conda-forge automake
#texinfo
conda install -y -c conda-forge texinfo
#libtool
conda install -y -c conda-forge libtool
#pkg_config
conda install -y -c conda-forge pkg-config 
#git lfs
conda install -y -c conda-forge git-lfs
# Make symlink for libftdi
cp ./gap8_env/bin/libftdi1-config ./gap8_env/bin/libftdi-config
# Clone git
#git clone https://github.com/GreenWaves-Technologies/gap_sdk.git
#git clone https://github.com/GreenWaves-Technologies/gap_riscv_toolchain_ubuntu_18.git
#Install toolchain
cd ./gap_riscv_toolchain_ubuntu_18
./install_new.sh
# Install subprojet
cd ../gap_sdk
git submodule update --init --recursive
# Intall requirements
# Remove explicit versions from file
conda install -y -c conda-forge --file requirements.txt
# Load config for gapuino_v2
source ./configs/gapuino_v2.sh
# add toolchain bin folder to path
export PATH="/volume1/users/vsharma/nano_drone/gap8_env/lib/gap_riscv_toolchain/bin/:$PATH"

# Make the SDK
make all
# Install requests python
conda install -y -c anaconda requests 
# Make the autotiler
#Enter information in dialog !
make autotiler
# Intall wget
conda install -y wget
#Update tensorflow in
#./gap_sdk/tools/nntool/requirements.txt from 1.14 to 1.15
# Make nntool
make nntool -j 4
# libudev for openocd
conda install -y -c conda-forge libudev-cos6-x86_64
conda install -y -c conda-forge libudev-devel-cos6-x86_64
#conda install -y -c pwwang glibc214 
# Make openocd
make openocd -j 4
