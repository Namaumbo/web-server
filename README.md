# web-server
 This project is about creating a secure and scalable web server using python as the language choice.
 For you to run the web server on your local machine please follow the following steps:
 1. clone the project into a folder .
 2. open the project using any IDE of your choice 
 3. There is a requirements.txt file containing libralies used in the project, open your terminal and type pip install -r requirements.txt  which will install the libralies
 4. run the project using the run button 
 5. click the url in the console log.
 6. you have a working server serving files the server resides waiting for clients' requests

# Running a Server as a Service In linux

	1.find a .service file in the clone folder
	
	2.open the file with any editor to the change the path of the script
	
		->add your script path on the line below in the .service file
		
		->ExecStart=/user/bin/python3 /<pathofthescript>/main.py
		
	3.copy the file into /etc/systemd/system
	
	4.On terminal do the following commands
	
		->systemctl daemon-reload  --to update the changes 	
		->systemctl start <servicename> --to start your service
		->sytemctl status <servicename> --to check the status of your service
		
	5.For a service to run automatically even when you reboot your PC do
	
		->systemctl enable <servicename>
		
	6.And finally stop the service anytime by running the command below
		->systemctl stop <servicename>
		
#logrotation
	1.first copy Logs folder into /var/log	.
	2.find a log.conf file in the folder
	3.copy the file into /etc/logrotate.d/
	4.To test if it is working do dry-run command
		->logrotate -d /etc/logrotate.d/Logs
			
