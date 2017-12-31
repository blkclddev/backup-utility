import configparser
import gcpstorage
import json
import os
import socket
import sys
import tarfile
import time
########################################################################################################################
# Pseudocode
#
# - Upload tar file
# - Delete tar file
# - Send message
########################################################################################################################
def main():
    if __name__ == "__main__":
        # Load configparser and config file
        config = configparser.ConfigParser()
        config.read("configuration.ini")

        # Set backup filename and destination
        backup_filename = createBackupFilename(config)

        # Call function to create backup
        createBackup(backup_filename, config)

        # Call function to upload backup file to cloud destination
        cloudUpload(backup_filename,config)

        # Delete local backup file
        print("[+] Deleting file {file}".format(file=backup_filename))
        os.remove(backup_filename)

# Function to create the full path, including file name of the backup tarfile
def createBackupFilename(config_file):
    # Check if local backup destination is empty; Set to CWD if so
    if not config_file.get("General", "destination"):
        local_destination = str(os.getcwd())
    else:
        local_destination = str(config_file.get("General", "destination"))

    # Check if local_destination has a trailing /; If not, add one
    if not local_destination.endswith("/"):
        local_destination = local_destination + "/"

    # Create backup filename
    backup_filename = str("{host}_backup_{date}_{time}.tar.gz".format(host=socket.gethostname(), date=time.strftime("%d%m%Y"),
                                                           time=time.strftime("%H%M%S")))

    # Create backup full path
    backup_full_path = local_destination + backup_filename

    # Return backup full path
    return backup_full_path

# Function to create backup tar file
def createBackup(backupFile, config_file):
    # Check if backup file already exists & exit if it does
    if os.path.exists(backupFile):
        print("[-] ERROR: {file} already exists! Exiting now...".format(file=backupFile))
        sys.exit()

    # Initialize list to store final list of files/drectories to be backed up
    backup_file_dir_list = []

    # Ensure all files and directories to be backed up exist
    config_file_dir_list = json.loads(config_file.get("BackupSource", "files"))
    for file in config_file_dir_list:
        if not os.path.exists(file):
            print("[-] ERROR: {file_name} does not exist & will not be backed up!".format(file_name=file))
        else:
            backup_file_dir_list.insert(0,file)

    # Create tar file
    backup_archive = tarfile.open(backupFile, "x")

    # Add all files in the backup list to the archive
    for file in backup_file_dir_list:
        backup_archive.add(file)

    # Close the backup file
    backup_archive.close()

# Function to upload backup file to the cloud
def cloudUpload(backup_file_path, config_file):
    # Check if GCP is the desired destination
    if str.lower(config_file.get("RemoteDestination", "remotedest")) == "gcp":
        print("[+] GCP Backup selected")

        # Retrieve and store project name
        project = str(config_file.get("RemoteDestination","project"))

        # Retrieve and store the bucket name
        bucket = str(config_file.get("RemoteDestination","bucket"))

        # Retrieve the backup file name from the fullpath
        remote_filename = os.path.basename(backup_file_path)

        # Set GCP credneitals
        print("[+] Setting GCP credentials")
        gcpstorage.set_credentials(config_file.get("RemoteDestination","keyfile"))

        # Upload local backup file to GCP bucket
        print("[+] Uploading local backup file to GCP storage")
        gcpstorage.upload_to_bucket(project,bucket,backup_file_path,remote_filename)

    elif str.lower(config_file.get("RemoteDestination","remotedest")) == "s3":
        sys.exit("[+] WARNING: S3 selected as remote destination, but is not currently supported! Exiting now...")
    else:
        sys.exit("[-] ERROR: No remote destination configured. Exiting now...")

main()