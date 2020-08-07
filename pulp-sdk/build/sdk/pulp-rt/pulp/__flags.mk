fc/archi = riscv
pe/archi = riscv
pulp_chip = pulp
pulp_chip_family = pulp
cluster/version = 5
fc_itc/version = 1
udma/cpi/version = 1
udma/i2c/version = 2
soc/fll/version = 1
udma/i2s/version = 2
udma/uart/version = 1
event_unit/version = 3
perf_counters = True
fll/version = 1
padframe/version = 1
udma/spim/version = 3
gpio/version = 3
udma/archi = 3
udma/version = 3
soc_eu/version = 2
PULP_LDFLAGS      += 
PULP_CFLAGS       += 
PULP_CL_ARCH_CFLAGS ?=  -march=rv32imfcxpulpv2 -mfdiv -D__riscv__
PULP_CL_CFLAGS    += -fdata-sections -ffunction-sections -I/home/vishal/nano_drone/pulp-sdk/pkg/sdk/dev/install/include/io -I/home/vishal/nano_drone/pulp-sdk/pkg/sdk/dev/install/include -include /home/vishal/nano_drone/pulp-sdk/build/sdk/pulp-rt/pulp/cl_config.h
PULP_CL_OMP_CFLAGS    += -fopenmp -mnativeomp
ifdef PULP_RISCV_GCC_TOOLCHAIN
PULP_CL_CC = $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc 
PULP_CC = $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc 
PULP_AR ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-ar
PULP_LD ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc
PULP_CL_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-objdump
PULP_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-objdump
else
PULP_CL_CC = $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc 
PULP_CC = $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc 
PULP_AR ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-ar
PULP_LD ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc
PULP_CL_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-objdump
PULP_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-objdump
endif
PULP_ARCH_CL_OBJDFLAGS ?= -Mmarch=rv32imfcxpulpv2
PULP_ARCH_OBJDFLAGS ?= -Mmarch=rv32imfcxpulpv2
PULP_FC_ARCH_CFLAGS ?=  -march=rv32imfcxpulpv2 -mfdiv -D__riscv__
PULP_FC_CFLAGS    += -fdata-sections -ffunction-sections -I/home/vishal/nano_drone/pulp-sdk/pkg/sdk/dev/install/include/io -I/home/vishal/nano_drone/pulp-sdk/pkg/sdk/dev/install/include -include /home/vishal/nano_drone/pulp-sdk/build/sdk/pulp-rt/pulp/fc_config.h
PULP_FC_OMP_CFLAGS    += -fopenmp -mnativeomp
ifdef PULP_RISCV_GCC_TOOLCHAIN
PULP_FC_CC = $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc 
PULP_CC = $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc 
PULP_AR ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-ar
PULP_LD ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-gcc
PULP_FC_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN)/bin/riscv32-unknown-elf-objdump
else
PULP_FC_CC = $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc 
PULP_CC = $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc 
PULP_AR ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-ar
PULP_LD ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-gcc
PULP_FC_OBJDUMP ?= $(PULP_RISCV_GCC_TOOLCHAIN_CI)/bin/riscv32-unknown-elf-objdump
endif
PULP_ARCH_FC_OBJDFLAGS ?= -Mmarch=rv32imfcxpulpv2
pulpRunOpt        += --dir=/home/vishal/nano_drone/pulp-sdk/build/sdk/pulp-rt/pulp
