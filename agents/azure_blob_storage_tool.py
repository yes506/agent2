from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

load_dotenv("/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/config/.env")


def get_blob_service_client():
    credential = DefaultAzureCredential()
    blob_storage_account_name = os.getenv("AZURE_BLOB_STORAGE_ACCOUNT_NAME")
    blob_service_client = BlobServiceClient(account_url=f"https://{blob_storage_account_name}.blob.core.windows.net", credential=credential)
    return blob_service_client


def retrieve_blobs(blob_service_client, container_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return blob_list


def upload_blob(blob_service_client, container_name, blob_name, file_path):
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


if __name__ == "__main__":
    blob_service_client = get_blob_service_client()
    container_name = "travel"
    # blob_list = retrieve_blobs(blob_service_client, container_name)
    # for blob in blob_list:
    #     print(blob.name)

    file_path = "/Users/donghyeon/Desktop/development/ai-intelligence-app/agent2/samples/test01.txt"
    blob_name = "test01"
    upload_blob(blob_service_client, container_name, blob_name, file_path)
