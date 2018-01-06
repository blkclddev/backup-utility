#Backup Utility

##Description
This program will backup the selected files into a tarfile and then upload that tarfile to a cloud storage service.

* Currently only GCP & S3 storage services are supported. 

##Requirements
See requirements.txt for more details on the python packages required

##Authentication
Authentication to the respective cloud service will be handled within the functions for that service.

* The gcpstorage file has a function to set a temporary environment variable to the keyfile.
* The s3storafe modules use keys to log in as an initial user and then STS to assume the permissions of another role
##Usage
The program can be called directly without any options. All configuration parameters are present in the configuration.ini file.

Example:
~~~~
python backup-utility.py

~~~~

##Testing
This program was developed under Linux using Python 3.6. There may be adjustments needed if you are using a different operating system or a different version of Python (EX: version 2)