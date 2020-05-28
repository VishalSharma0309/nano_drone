STEPS TO VNC INTO A WINDOWS SERVER

	1. SSH into helium
		ssh -X userid@ssh.esat.kuleuven.be

	2. SSH into servername
		ssh servername.esat.kuleuven.be

	3. Launch vncserver
		vncserver :3

	4. Close this connection
		exit
		exit

	5. Create a SSH Tunnel
		ssh -L 5903:servername.esat.kuleuven.be:5903 userid@ssh.esat.kuleuven.be

	// Note that we are using 5903 because we launched vncserver ':3'

	6. Open VNC Viewer
	
	7. Connect to the server
		using the ip: 127.0.0.1:3

	8. Connect to thanos through the following command:
		/esat/europa1/users/astandae/Software/FreeRDP/bin/xfreerdp +clipboard /cert-ignore /v:windowsservername /u:userid /multimon


	9. Creating a shortcut for the above command:
		
		// add the following lines of code into the ~/.bashrc file of the linux server used to VNC into windows one
		alias freerdp="/esat/europa1/users/astandae/Software/FreeRDP/bin/xfreerdp"
		alias windowsservername="freerdp +clipboard /cert-ignore /v:windowsservername /u:userid /multimon"


