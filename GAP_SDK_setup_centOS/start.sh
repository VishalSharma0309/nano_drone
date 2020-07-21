#!/bin/bash
# Populate build variables for conda
export CONDA_BUILD=1
# Activate the conda env
conda activate ./gap8_env
# Reset CFLAGS, because anaconda sets it and it fails to complete the build for RISC-V compiler
export CFLAGS=""
# enter SDK folder
cd ./gap_sdk
# Source the settings for V2 board
source ./configs/gapuino_v2.sh
# add toolchain bin folder to path
export PATH="/volume1/users/vsharma/gap8_env/lib/gap_riscv_toolchain/bin/:$PATH"
