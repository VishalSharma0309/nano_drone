// https://github.com/VishalSharma0309/nano_drone
// Operating System: CentOS 7
// last updated: July 6, 2020

1. Installing cmake

	wget https://cmake.org/files/v3.12/cmake-3.12.3.tar.gz
	tar zxvf cmake-3.*
	cd cmake-3.*
	./bootstrap --prefix=/usr/local
	make -j$(nproc)
	make install


