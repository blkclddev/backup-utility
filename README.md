#Backup Utility

##Description
This program will backup the selected files into a tarfile and then upload that tarfile to a cloud storage service.

* Currently only GCP storage buckets are supported.

##Requirements
See requirements.txt for more details on the python packages required

##Authentication
Authentication to the respective cloud service will be handled within the functions for that service. For example, the gcpstorage file has a function to set a temporary environment variable to the keyfile.

##Usage
The program can be called directly without any options. All configuration parameters are present in the configuration.ini file.

Example:
~~~~
python backup-utility.py

~~~~

##Testing
This program was developed under Linux using Python 3.6. There may be adjustments needed if you are using a different operating system or a different version of Python (EX: version 2)