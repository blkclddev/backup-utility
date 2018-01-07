import boto3


########################################################################################################################
# Authentication
#   This script is designed to assume the permissions for a role under your AWS accont using STS.
#   Initial login is accomplished using a access key and secrete access key for a normal user. From
#   there the user assumes the permissions of a different role to upload to S3.
#
#   The thought here is twofold:
#       1. The initial user is unprivileged, having the rights only to assume the needed role.
#       2. The assumed role has very specific permissions only to perform the needed actions
#
#   While the script implements the STS assume role function, configuration of the permissions is up to you.
########################################################################################################################

# Function to upload file to S3 bucket
def upload_to_bucket(aws_access_key_id, aws_secret_access_key, assumed_role_arn, bucket_name, remote_file_name,
                     local_file_name):
    # Authenticate and create secure token service client connection
    sts_client = boto3.client(
        "sts",
        aws_access_key_id=str(aws_access_key_id),
        aws_secret_access_key=str(aws_secret_access_key)
    )

    # Assume temporary AWS role
    sts_assumed_role = sts_client.assume_role(
        RoleArn=str(assumed_role_arn),
        RoleSessionName="PyBackupUtilitySession"
    )

    # Store credentials from assumed role
    sts_assumed_role_credentials = sts_assumed_role["Credentials"]

    # Create an S3 resource connection using assumed role credentials
    s3_connection = boto3.resource(
        "s3",
        aws_access_key_id=sts_assumed_role_credentials["AccessKeyId"],
        aws_secret_access_key=sts_assumed_role_credentials['SecretAccessKey'],
        aws_session_token=sts_assumed_role_credentials['SessionToken'],
    )

    # Upload file to bucket
    file_data = open(local_file_name, "rb")
    s3_connection.Bucket(str(bucket_name)).put_object(
        Key=str(remote_file_name),
        Body=file_data
    )


# Main function
def main():
    # Check if the script is running as standalone
    if __name__ == "__main__":
        print("ERROR: This module is designed to be imported by other Python programs.")


main()
