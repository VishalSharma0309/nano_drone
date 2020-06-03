// https://github.com/VishalSharma0309/nano_drone
// last updated: June 3, 2020

-----------------------------------------------------------------------------------------
Objective: To find a suitable protocol to connect two cameras with GAP8 (gapuino for now)
-----------------------------------------------------------------------------------------

Available Camera Interfaces:

	1. CPI (Camera Parallel Interface)		
		dedicated pinout in GAP8

	2. CSI (Camera Serial Interface)
		2.1 CSI-1
		2.2 CSI-2
		2.3 CSI-3

	3. UART

	4. SPI

	5. I2C


1. Camera Parallel Interface
-----------------------------

Consists of two portions:
	1.1 I2C Control Signals
	1.2 Parallel Bus for image data itself

1.1 I2C Control Signals
-----------------------

	* I2C bus is used to control the various registers of the camera module
	* Consists of two signals: SDA (data) and SCK (clock)
	* I2C signals are connected in a daisy-chain multi-drop configuration
	* Multiple devices can be connected to a single bus in a daisy-chain, multi-drop configuration	

	* The MCU provides the I2C master used to communicate with the camera configuration interface
	* A common 7 or 10-bit addressing scheme is used by the I2C master to identify and select a particular I2C slave for communication


1.2 Parallel Data Signals
-------------------------

	* 8-bit parallel link connects to the video data bus for an image sensor
	* Provides Vertical SYNC (VSYNC), Horizontal SYNC (HSYNC) and Pixel Clock (PCLK) timing signals
	* The parallel interface is Unidirectional (camera to MCU)



-------------------------------
TYPICAL INTERCONNECTION
-------------------------------

Required PINS: 
SDA, SCL, D7:0, PCLK, VSYNC, HREF


--------------------------------
GAP8 CPI
--------------------------------

The CPI interface is 8 bits wide and can communicate at speeds up to 50MHz. VSYNC, HSYNC and PCLK are provided by the camera.

	* uDMA CPI interface registers

	1. RX_SADDR: CPI buffer base address configuration register
	2. RX_SIZE: CPI buffer size configuration register
	3. RX_CFG:  CPI stream configuration register
	4. CFG_GLOB: CPI Global configuration register
	5. CFG_LL: CPI Lower Left corner configuration register
	6. CFG_UR: CPI Upper Right corner configuration register
	7. CFG_SIZE: CPI Horizontal Resolution configuration register
	8. CFG_FILTER: CPI RGB coefficients configuration register


--------------------------------
FRAME RATES
--------------------------------

			  Maximum supported PCLK
Theoretical Frame Rate =  ____________________________________________

			  Horizontal size * Vertical size * Bytes/Pixel

Bytes/pixel = 2 (since each pixel takes 2 PCLK cycles- one for each byte) 

	* In practice, the actual rate is slower.
