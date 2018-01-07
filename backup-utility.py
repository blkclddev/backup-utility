import configparser
import gcpstorage
import json
import logging
import os
import s3storage
import socket
import sys
import tarfile
import time


########################################################################################################################
# Pseudocode
#
# - Write messages to log file (include file in tar file)
#   - Initate logger
#   -
# - Send email with log file messages
########################################################################################################################
def main():
    if __name__ == "__main__":
        # Load configparser and config file
        config = configparser.ConfigParser()
        config.read("configuration.ini")

        # Initiate logger
        logging.basicConfig(
            filename=str(config.get("DEFAULT", "logfile")),
            level=logging.DEBUG
        )

        # Print message indicating start of script
        print("[+] Backup program starting. Output will be redirected to the backup log file.")

        # Set backup filename and destination
        backup_filename = createbackupfilename(config)
        logging.info("Setting backup file to: %s", backup_filename)


        # Call function to create backup
        logging.info("Starting local backup process")
        createbackup(backup_filename, config)

        # Call function to upload backup file to cloud destination
        logging.info("Starting cloud upload process")
        cloudupload(backup_filename, config)

        # Delete local backup file
        logging.info("Deleting backup file: %s", backup_filename)
        os.remove(backup_filename)

        # Delete local log file
        logging.info("Deleting local backup log file")
        os.remove(config.get("DEFAULT", "logfile"))

        # Print message indicating end of script
        print ("[+] Backup complete! Refer to backup log file for additional detail.")


# Function to create the full path, including file name of the backup tarfile
def createbackupfilename(config_file):
    # Check if local backup destination is empty; Set to CWD if so
    if not config_file.get("DEFAULT", "destination"):
        local_destination = str(os.getcwd())
    else:
        local_destination = str(config_file.get("DEFAULT", "destination"))

    # Check if local_destination has a trailing /; If not, add one
    if not local_destination.endswith("/"):
        local_destination = local_destination + "/"

    # Create backup filename
    backup_filename = str(
        "{host}_backup_{date}_{time}.tar.gz".format(host=socket.gethostname(), date=time.strftime("%d%m%Y"),
                                                    time=time.strftime("%H%M%S")))

    # Create backup full path
    backup_full_path = local_destination + backup_filename

    # Return backup full path
    return backup_full_path


# Function to create backup tar file
def createbackup(backupfile, config_file):
    # Check if backup file already exists & exit if it does
    if os.path.exists(backupfile):
        logging.info("%s already exists! Terminating program", backupfile)
        print("[-] ERROR: {file} already exists! Exiting now...".format(file=backupfile))
        sys.exit()

    # Initialize list to store final list of files/directories to be backed up
    backup_file_dir_list = []

    # Ensure all files and directories to be backed up exist
    config_file_dir_list = json.loads(config_file.get("BackupSource", "files"))
    for file in config_file_dir_list:
        if not os.path.exists(file):
            logging.warning("%s does not exist & will not be backed up!", file)
            print("[-] ERROR: {file_name} does not exist & will not be backed up!".format(file_name=file))
        else:
            backup_file_dir_list.insert(0, file)

    # Create tar file
    backup_archive = tarfile.open(backupfile, "x")

    # Add all files in the backup list to the archive
    for file in backup_file_dir_list:
        backup_archive.add(file)

    # Close the backup file
    backup_archive.close()


# Function to upload backup file to the cloud
def cloudupload(backup_file_path, config_file):
    # Retrieve the backup file name from the fullpath
    remote_filename = os.path.basename(backup_file_path)

    # Check if GCP is the desired destination
    if str.lower(config_file.get("RemoteDestination", "remotedest")) == "gcp":
        # Add log entry to indicate that GCP cloud storage was selected
        logging.info("GCP storage selected as cloud upload destination")

        # Retrieve and store project name
        project = str(config_file.get("GCPStorageInfo", "project"))

        # Retrieve and store the bucket name
        bucket = str(config_file.get("GCPStorageInfo", "bucket"))

        # Set GCP credneitals
        logging.info("Setting GCP credentials")
        gcpstorage.set_credentials(config_file.get("RemoteDestination", "keyfile"))

        # Upload local backup file to GCP bucket
        logging.info("Uploading local backup file to GCP storage")
        gcpstorage.upload_to_bucket(project, bucket, backup_file_path, remote_filename)

    # Check if AWS S3 is the desired destination
    elif str.lower(config_file.get("RemoteDestination", "remotedest")) == "s3":
        # Add log entry to indicate that AWS S3 cloud storage was selected
        logging.info("AWS S3 storage selected as cloud upload destination")

        # Create Remote file name including bucket folder
        remote_file_full_path = str(config_file.get("S3StorageInfo", "BucketFolder")) + "/" + remote_filename
        logging.info("Setting S3 remote file to: %s", remote_file_full_path)

        # Upload file to S3
        logging.info("Uploading file to S3 bucket (%s)", str(config_file.get("S3StorageInfo", "BucketName")))
        s3storage.upload_to_bucket(
            str(config_file.get("S3StorageInfo", "AccessKey")),
            str(config_file.get("S3StorageInfo", "SecretKey")),
            str(config_file.get("S3StorageInfo", "AssumedRole")),
            str(config_file.get("S3StorageInfo", "BucketName")),
            remote_file_full_path,
            backup_file_path
        )
    else:
        # If no cloud destination was configured or if an invalid value was provided
        logging.error("Blank or invalid cloud destination provided! Program will exit and local files will not be deleted.")
        sys.exit("[-] ERROR: Blank or invalid cloud destination provided. Exiting now...")


main()