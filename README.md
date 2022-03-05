# web-server
 This project is about creating a secure and scalable web server using python as the language choice.
 For you to run the web server on your local machine please follow the following steps:
 1. clone the project into a folder .
 2. open the project using any IDE of your choice 
 3. There is a requirements.txt file containing libralies used in the project, open your terminal and type pip install -r requirements.txt  which will install the libralies
 4. run the project using the run button 
 5. click the url in the console log.
 6. you have a working server serving files the server resides waiting for clients' requests

# Service Running in linux
for you to run th server as a service on linuc you have to create a service file in this path  /etc/systemd/system/<yourservicefile>.service next you hvae to include some info on the file as follows:
 
 //////////////// using vim for editing or nano in linux//////////////////////////////

               [unit]

               After=multi-user.target

               [service]

               Type=exec

               ExecStart=/user/bin/python3 /<pathofthescript>/<script>.py

               [install]

               WantedBy=multi-user.target
 
 //////////////////////////////end of file/////////////////////////////////////////////
 
 
 then you have to start the service through the following command in a sudo mode
 
               systemctl start <yourservicefile>.service
 
if you want to change the configuration files due to post changes you have to use the following command
 
               systemctl stop <yourservicefile>.service
 
then after changing the service file you have to reload  the daemon setting and restart the services as follows
 
               systemctl daemon-reload
 
               systemctl start <yourservicefile>.service
 
               systemctl status <yourservicefile>.service {to check the running status of the service}
 
for you to get a sticking service that is to restart it after the computer restarts then
 
               systemctl enable <yourservicefile>.service
