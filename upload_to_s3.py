import os
import sys
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

AWS_S3_BUCKET_NAME = 'warrantywiz'
AWS_REGION = 'us-east-1'
AWS_ACCESS_KEY = 'AKIAZQ3DUXPKMAG7BK4L123'
AWS_SECRET_KEY = 'iPfAORPNAY1+f2IxwoE+aBnbhi1WqfmfLUDf4r0e123'

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
base_folder = f"{ROOT_PATH}/Extended warranty insurance/"

paths_to_s3_folders = {
    'automation/automation script': 'automation script',
    'requirement/epic response': 'requirement',
    'requirement/Extended warranty insurance_FinalReport.docx': 'requirement',
    'tester/regression': 'regression',
    'tester/test case': 'test case'
}

def create_folders_in_s3(folders, bucket_name):
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        for folder in folders:
            # Add a trailing slash to create a "directory" in S3
            s3_key = folder + '/'
            print(f"Creating folder: {s3_key}")
            s3_client.put_object(Bucket=bucket_name, Key=s3_key)
        return True
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(e)
        return False

def upload_to_aws(paths_to_s3_folders, base_folder, bucket_name):
    s3_client = boto3.client(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    try:
        for local_path, s3_folder in paths_to_s3_folders.items():
            full_path = os.path.join(base_folder, local_path)
            if os.path.isdir(full_path):
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        local_file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(local_file_path, base_folder)
                        s3_key = os.path.join(s3_folder, relative_path).replace("\\", "/")
                        
                        print(f"Uploading file: {local_file_path} to S3 key: {s3_key}")
                        s3_client.upload_file(local_file_path, bucket_name, s3_key)
            elif os.path.isfile(full_path):
                s3_key = os.path.join(s3_folder, os.path.basename(local_path)).replace("\\", "/")
                print(f"Uploading file: {full_path} to S3 key: {s3_key}")
                s3_client.upload_file(full_path, bucket_name, s3_key)
            else:
                print(f"Path not found: {full_path}")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
    except Exception as e:
        print(e)
        return False

if __name__ == '__main__':
    # Create folder structure in S3
    folders_to_create = set(f'{folder}/' for folder in paths_to_s3_folders.values())
    created_folders = create_folders_in_s3(folders_to_create, AWS_S3_BUCKET_NAME)
    if created_folders:
        print("Folders created successfully.")
    
    # Upload files to S3
    uploaded = upload_to_aws(paths_to_s3_folders, base_folder, AWS_S3_BUCKET_NAME)
    print("Upload Successful:", uploaded)







