# Files
File objects represent individual files in Box. They can be used to download a file's contents, upload new versions, and perform other common file operations (move, copy, delete, etc.).


## Concepts
File objects represent individual files in Box. They can be used to download a file's contents, upload new versions, and perform other common file operations such as move, copy, and delete.

## Files API
References to our documentation:
* [SDK Files](https://github.com/box/box-python-sdk-gen/blob/main/docs/files.md)
* [API Folder Guide](https://developer.box.com/guides/files/)
* [API Reference](https://developer.box.com/reference/resources/file/)


# Exercises
## Setup
Create a `files_init.py` file on the root of the project and execute the following code:
```python
"""create sample content to box"""
import logging
from utils.box_client_oauth import ConfigOAuth, get_client_oauth

from workshops.files.create_samples import create_samples

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)

conf = ConfigOAuth()


def main():
    client = get_client_oauth(conf)
    create_samples(client)


if __name__ == "__main__":
    main()
```
Result:
```
INFO:root:Folder workshops with id: 223095001439
INFO:root:Folder files with id: 223097997181
```
Grab the id of the `files` folder you'll need it later
Open your Box account and verify that the following content was created:
```
- All Files
    - workshops
        -files
```


Next, create a `files.py` file on the root of the project that you will use to write your code.
Create a global constant named `SAMPLE_FOLDER` and make it equal to the id of the `files` folder.

```python
"""Box Files workshop"""
import logging
import os
from typing import Iterable
import shutil

from box_sdk_gen.fetch import APIException
from utils.box_client_oauth import ConfigOAuth, get_client_oauth
from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import File, Files, FileMini, Folder, FileFullRepresentationsEntriesStatusStateField
from box_sdk_gen.managers.files import GetFileThumbnailByIdExtension
from box_sdk_gen.managers.uploads import (
    PreflightFileUploadCheckParent,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)
from box_sdk_gen.utils import ByteStream

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)

SAMPLE_FOLDER = "223097997181"

def main():
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

if __name__ == "__main__":
    main()

```

## New file upload
Create a method named `upload_file` that receives a `client` and a `file_path` and uploads the file to a specific folder.

```python
def upload_file(client: Client, file_path: str, folder_id: str) -> File:
    """Upload a file to a Box folder"""

    # upload new file
    upload_arg = UploadFileAttributes(
        file_name, UploadFileAttributesParentField(folder_id))
    files: Files = client.uploads.upload_file(upload_arg, file=open(file_path, "rb"))
    box_file = files.entries[0]

    return box_file
```
Then upload the `workshops/files/content_samples/sample_file.txt` file to the `files` folder.
```python
def main():
    ...

    # make sure the folder exists
    sample_folder = client.folders.get_folder_by_id(SAMPLE_FOLDER)

    sample_file = upload_file(client, sample_folder.id, "workshops/files/content_samples/sample_file.txt")
    print(f"Uploaded {sample_file.name} to folder [{sample_folder.name}]")
```
Should result in something similar to:
```
Uploaded sample_file.txt to folder [files]
```
## New file version upload
Files in Box have versions, you can upload a new version of a file by using the `upload` method of the file object.
Modify the `upload_file` method to upload a new file or a new version depending if the file exists or not.

```python
def upload_file(client: Client, file_path: str, folder_id: str) -> File:
    """Upload a file to a Box folder"""

    file_name = os.path.basename(file_path)

    try:
        # upload new file
        upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
        files: Files = client.uploads.upload_file(upload_arg, file=open(file_path, "rb"))
        box_file = files.entries[0]
    except APIException as err:
        if err.code == "item_name_in_use":
            logging.warning("File already exists, updating contents")
            box_file_id = err.context_info["conflicts"]["id"]
            try:
                # upload new version
                upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
                files: Files = client.uploads.upload_file_version(box_file_id, upload_arg, file=open(file_path, "rb"))
                box_file = files.entries[0]
            except APIException as err2:
                logging.error("Failed to update %s: %s", box_file.name, err2)
                raise err2
        else:
            raise err

    return box_file
```
Then run your script again, it should result in something similar to:
```
WARNING:root:File already exists, updating contents
Uploaded sample_file.txt to folder [files]
```

## Preflight check
There is another option to check if a file can be accepted by box before uploading it.
It typically checks for file name duplication and file size, in case you have exceeded your quota.
Modify the `upload_file` method to use the `preflight_check` method of the folder object:

```python
def upload_file(client: Client, file_path: str, folder_id: str) -> File:
    """Upload a file to a Box folder"""

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    try:
        # pre-flight check
        pre_flight_arg = PreflightFileUploadCheckParent(id=folder_id)
        client.uploads.preflight_file_upload_check(file_name, file_size, pre_flight_arg)

        # upload new file
        upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
        files: Files = client.uploads.upload_file(upload_arg, file=open(file_path, "rb"))
        box_file = files.entries[0]
    except APIException as err:
        if err.code == "item_name_in_use":
            logging.warning("File already exists, updating contents")
            box_file_id = err.context_info["conflicts"]["id"]
            try:
                # upload new version
                upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
                files: Files = client.uploads.upload_file_version(box_file_id, upload_arg, file=open(file_path, "rb"))
                box_file = files.entries[0]
            except APIException as err2:
                logging.error("Failed to update %s: %s", box_file.name, err2)
                raise err2
        else:
            raise err

    return box_file
```
Then run the script again.

Resulting in:
```
WARNING:root:File already exists, updating contents
Uploaded sample_file.txt to folder [files]
```
From a code perspective it isn't much different, so why should I use th preflight check?
The preflight check is a good way to validate if a file can be uploaded before actually uploading it.
Imagine running out of space quota after a long upload, it would be a waste of time and resources.
Also the preflight check uses an `OPTIONS` http request which is faster than the `POST` request used by the `upload` method.

## Download file
Now let's try to download the file we just uploaded.
Create a method named `download_file` that receives a `file` and a `local_path` and downloads the file.

```python
def download_file(client: Client, file_id: str, local_path_to_file: str):
    """Download a file from Box"""
    file_stream: ByteStream = client.downloads.download_file(file_id)

    with open(local_path_to_file, "wb") as file:
        shutil.copyfileobj(file_stream, file)
```
Then download the `sample_file.txt` file to the root of your project.
```python
    download_file(client, sample_file.id, "./sample_file_downloaded.txt")

    for local_file in os.listdir("./"):
        if local_file.endswith(".txt"):
            print(local_file)
```
Resulting in:
```
WARNING:root:File already exists, updating contents
Uploaded sample_file.txt to folder [files]
requirements.txt
sample_file_downloaded.txt
```

## Download a ZIP
When you need to download multiple files and folders at once, you can use the `download_zip` method of the `client` object.
Create a method named `download_zip` that receives a `client` and a list of `items` and downloads the folder as a zip file to a `local_path`.

```python
def download_zip(client: Client, local_path_to_zip: str, items: List[CreateZipDownloadItemsArg]):
    """Download a zip file from Box"""

    file_name = os.path.basename(local_path_to_zip)
    zip_download = client.zip_downloads.create_zip_download(items, file_name)

    # ## fix this hack ## #
    # the zip_download.download_url is a full url that includes the id like this:
    # https://dl.boxcloud.com/2.0/zip_downloads/2r6IQDsU33XfcSWpZ6I-Dug==rnTAVzm2vntcB4P1XK12QdfxYIRTQVYp47UbJoUdZfhPL0VfWxm0NSgDo9TH/content
    # we need to parse it and get only the id

    # get the id from the url
    url_parts = zip_download.download_url.split("/")
    zip_download_id = url_parts[5]

    file_stream: ByteStream = client.zip_downloads.get_zip_download_content(zip_download_id)

    with open(local_path_to_zip, "wb") as file:
        shutil.copyfileobj(file_stream, file)
```
Then lets zip the entire `root` folder:
```python
def main():
    ...

    # folder 0 represents the user root folder and is always available
    user_root = client.folders.get_folder_by_id("0")

    zip_items_arg = []

    for item in client.folders.get_folder_items(user_root.id).entries:
        item_arg = CreateZipDownloadItemsArg(type=item.type, id=item.id)
        zip_items_arg.append(item_arg)

    print("Downloading zip")
    download_zip(client, "./sample_zip_downloaded.zip", zip_items_arg)

    for local_file in os.listdir("./"):
        if local_file.endswith(".zip"):
            print(local_file)    
```
Resulting in:
```
Downloading zip
sample_zip_downloaded.zip

```
If you open the zip file you should see all content stored by your user.
Note that the `items` list can be any combination of `files` and `folders`.

## File information
Now that we have some files to play with, let's explore the file object, as it has a tremendous amount of information.
The first thing is to get the file object, we can do that by using the `file` method of the `client` object.

Update the SAMPLE_FILE python constant with the id of the sample file inside your Box `All Files/workshops/files/` folder.
In my case:
```python
SAMPLE_FILE = "1289038683607"
```
Create a method that returns a file object based on the file id:
```python
def file_to_json(client: Client, file_id: str) -> str:
    """Get a file from Box"""
    file: File = client.files.get_file_by_id(file_id)
    file_json = json.dumps(file.to_dict(), indent=2)
    return file_json
```
Test this method on your main method:
```python
def main():
    ...

    file_json = file_to_json(client, SAMPLE_FILE)
    print(file_json)
```
and you should get something like:
```json
{
  "id": "1289038683607",
  "type": "file",
  "etag": "13",
  "sequence_id": "13",
  "name": "sample_file.txt",
  "sha1": "715a6fe7d575e27934e16e474c290048829ffc54",
  "file_version": {
    "id": "1480058958687",
    "type": "file_version",
    "sha1": "715a6fe7d575e27934e16e474c290048829ffc54"
  },
  "description": "This is a sample file",
  "size": 42,
  ...
  "item_status": "active"
}
```
There are many more properties you can explore, check the [API Reference](https://developer.box.com/reference/resources/file/) for more information.

## Update a file
Now that we have a file object, let's try to update it.

Create a method that updates the description of a file:
```python
def file_update_description(client: Client, file_id: str, description: str) -> File:
    return client.files.update_file_by_id(file_id, description=description)
```
Change the description of the previous file:
```python
def main():
    ...

    file = client.files.get_file_by_id(SAMPLE_FILE)
    print(f"{file.id} {file.name} {file.description}")

    file = file_update_description(client, SAMPLE_FILE, f"Updating the description at {datetime.datetime.now()}")

    file = client.files.get_file_by_id(SAMPLE_FILE)
    print(f"{file.id} {file.name} {file.description}")
```
Resulting in:
```
1289038683607 sample_file.txt
1289038683607 sample_file.txt Updating the description at 2023-11-02 17:21:05.377487
```
## List the contents of a folder
We need a method to list the contents of a folder.
Add this method to your `files.py` file:
```python
def folder_list_contents(client: Client, folder_id: str):
    folder = client.folders.get_folder_by_id(folder_id)
    items = client.folders.get_folder_items(folder_id)
    print(f"\nFolder [{folder.name}] content:")
    for item in items.entries:
        print(f"   {item.type.value} {item.id} {item.name}")
```

## Copy a file
Now lets duplicate the file we just updated, and list the folder contents:
We can do this directly in our main method:
```python
def main():
    ...

try:
        client.files.copy_file(SAMPLE_FILE, CopyFileParentArg(SAMPLE_FOLDER), name="sample_file_copy.txt")
    except APIException as err:
        if err.code == "item_name_in_use":
            logging.warning("Duplicate File already exists")
        else:
            raise err
    folder_list_contents(client, SAMPLE_FOLDER)
```
The try block is there to prevent the script from copying the file, if the file duplicate already exists, since we'll be running this script multiple times.

Resulting in:
```
Folder [files] content:
   file 1289038683607 sample_file.txt
   file 1351886955787 sample_file_copy.txt
```

## Move a file
Now lets move the file we just copied to the root of the box account:
```python
def main():
    ...

    try:
        file_moved = client.files.update_file_by_id(file_copied_id, parent=CopyFileParentArg("0"))
        file_moved_id = file_moved.id
    except APIException as err:
        if err.code == "item_name_in_use":
            logging.warning("File already exists, we'll use it")
            file_moved_id = err.context_info["conflicts"]["id"]
        else:
            raise err

    folder_list_contents(client, "0")
```
Again we need a `try` block.

Resulting in:
```
Folder [All Files] content:
   folder 216797257531 My Signed Documents
   folder 221723756896 UIE Samples
   folder 223095001439 workshops
   file 1204688948039 Get Started with Box.pdf
   file 1351892000645 sample_file_copy.txt
```

## Delete a file
Finally we'll delete the file we just copied:
```python
def main():
    ...

    client.files.delete_file_by_id(file_moved_id)
    folder_list_contents(client, "0")
```
Resulting in:
```
Folder [All Files] content:
   folder 216797257531 My Signed Documents
   folder 221723756896 UIE Samples
   folder 223095001439 workshops
   file 1204688948039 Get Started with Box.pdf
   file 1351892000645 sample_file_copy.txt
```

## Extra Credit
There are many more methods you can try for the file object.
Try them out and see what you can find:
* Create a method to rename a file.
* Create a method that returns the complete path (operating system style) of a file object
* Implement the chunked upload method
* Implement the manual upload method 


# Final thoughts
`File` objects are very powerful, they allow you to perform many operations on files. This workshop only scratched the surface of what you can do with them.
We'll explore more of them in the other workshops.









