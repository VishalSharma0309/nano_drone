# NANO DRONE PROJECT

### Objective:
To develop an autonomous nano drone with an end-to-end closed-loop visual pipeline for autonomous navigation based on a CNN based model

### Repository Structure

```
nano_drone
│   README.md
│   readme_GAPSDK.txt (to setup GAP SDK)
|   readme_gvsoc.txt (to setup and use GVSOC on GAP SDK and PULP SDK)
|   readme_multiCameraInterfacing.txt (research on interfacing multi-cameras on GAP SoC)
|   readme_pulpDroNet.txt (to setup PULP DroNet)
|   readme_vncsteps.txt (to vnc into remote PCs)
|   tasks.txt (weekly meeting notes)
│
└───gap_riscv_toolchain_ubuntu_18
│   │   install.sh
│   │   README.md
│   │
│   └───bin
│   └───include    
│   └───lib    
│   └───libexec    
│   └───riscv32-unknown-elf
|   └───share
|
└───gap_sdk
│   │   requirements.txt
│   │   README.md
|   |   sourceme.sh 
│   │
│   └───applications
|   |   └───audio_4chan_vocIP
|   |   └───BilinearResize
|   |   └───CannyEdgeDetection
|   |   └───FaceDetection
|   |   └───jpeg_encoder
|   |   └───MultiScalePedestrianDetector
|   |   └───WaterMeter
│   └───build    
│   └───configs    
│   └───docs    
│   └───examples
|   |   └───autotiler
|   |   └───native
|   |   |   └───freeRTOS
|   |   |   └───mbed
|   |   |   └───mbed-gapoc
|   |   |   └───pulpos
|   |   └───nntool
|   |   └───pmsis
|   |       └───devices
|   |       └───helloworld
|   |       └───test_features
|   |       └───test_periph
|   |        
|   └───gvsoc
|   └───install
|   └───libs
|   └───PlatformIO
|   └───rtos
|   └───tools
|
└───Papers (relevant research papers)
└───pmsis_api
|   |   LICENSE
|   |
|   └───docs
|   └───include
|   └───jenkins
|   └───tools
|
└───pulp-dronet
|   |   README.md
|   |   LICENSE_README.md
|   |   LICENSE.apache.md
|   └───bin
|   └───dataset
|   └───imgs
|   └───PULP-Shield
|   └───src
|   └───wieghts
|  
└───reference_manuals
|        
'''