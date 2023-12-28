# File Representations
A representation is an alternative asset for a file stored in Box. These assets can be PDFs, thumbnails, or text extractions.

Representations are automatically generated for the supported file types, either when uploading to Box or when requesting the asset.


## Concepts
Consider file representations as document avatars.
Representations go way beyond thumbnails, they are a way to access the content of a file without having to download it or get a pdf version of a document, even if the document is not a pdf.

This feature has become more relevant with the rise of AI and LLM, as it allows you to extract the content of a file and use it for other purposes, for example sending it to OpenAI.

Not all representations are available for all file types. For example, you can't get a text representation of an image file.

## File Representations API
References to our documentation:
* [SDK Files](https://github.com/box/box-python-sdk-gen/blob/main/docs/files.md#getting-additional-fields)
* [API Guide](https://developer.box.com/guides/representations/)
* [API Reference ](https://developer.box.com/reference/get-files-id/)
* [Supported file types](https://developer.box.com/guides/representations/supported-file-types/)


# Exercises
## Setup
Create a `files_representations_init.py` file on the root of the project and execute the following code:
```python
"""create sample content to box"""
import logging
from utils.box_client_oauth import ConfigOAuth, get_client_oauth

from workshops.file_representations.create_samples import create_samples

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
INFO:root:Folder file_representations with id: 223939315135
INFO:root:      Uploaded Single Page.docx (1294096878155) 11723 bytes
INFO:root:      Uploaded JS-Small.js (1294098434302) 3249 bytes
INFO:root:      Uploaded HTML.html (1294094879490) 2087 bytes
INFO:root:      Uploaded Document (PDF).pdf (1294102659923) 792687 bytes
INFO:root:      Uploaded Audio.mp3 (1294103505129) 2772151 bytes
INFO:root:      Uploaded Preview SDK Sample Excel.xlsx (1294097951585) 83418 bytes
INFO:root:      Uploaded JSON.json (1294102660561) 583 bytes
INFO:root:      Uploaded ZIP.zip (1294105019347) 41687 bytes
INFO:root:      Uploaded Document (Powerpoint).pptx (1294096083753) 57947 bytes
```

Next, create a `files_representations.py` file on the root of the project that you will use to write your code.
Create a global constant named `DEMO_FOLDER` and make it equal to the id of the `file_representations` folder, in my case `223939315135`.

Create a global constants for each file with their file id that you got on the previous step.
In my case:
```python
DEMO_FOLDER = 223939315135
FILE_DOCX   = 1294096878155
FILE_JS     = 1294098434302
FILE_HTML   = 1294094879490
FILE_PDF    = 1294102659923
FILE_MP3    = 1294103505129
FILE_XLSX   = 1294097951585
FILE_JSON   = 1294102660561
FILE_ZIP    = 1294105019347
FILE_PPTX   = 1294096083753
```

```python
"""Box File representations"""
import logging
import json
import requests
import shutil
from typing import List

from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import File, FileMini, Folder, FileFullRepresentationsEntriesStatusStateField, FileFullRepresentationsEntriesField
from box_sdk_gen.managers.files import GetFileThumbnailByIdExtension

from utils.box_client_oauth import ConfigOAuth, get_client_oauth

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)

DEMO_FOLDER = 223939315135
FILE_DOCX = 1294096878155
FILE_JS = 1294098434302
FILE_HTML = 1294094879490
FILE_PDF = 1294102659923
FILE_MP3 = 1294103505129
FILE_XLSX = 1294097951585
FILE_JSON = 1294102660561
FILE_ZIP = 1294105019347
FILE_PPTX = 1294096083753

def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")


if __name__ == "__main__":
    main()

```


## List all representations for a file
Let's start by creating a couple of methods that list and print all representation for a file object:
```python
def obj_dict(obj):
    return obj.__dict__


def file_representations_print(file_name: str, representations: List[FileFullRepresentationsEntriesField]):
    json_str = json.dumps(representations, indent=4, default=obj_dict)
    print(f"\nFile {file_name} has {len(representations)} representations:\n")
    print(json_str)


def file_representations(client: Client, file: FileMini, rep_hints: str = None) -> List[FileFullRepresentationsEntriesField]:
    """Get file representations"""
    file = client.files.get_file_by_id(file.id, fields=["name", "representations"], x_rep_hints=rep_hints)
    return file.representations.entries
```
Then use it in your main method with the `FILE_DOCX`:
```python
def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # make sure the file exists
    file_docx = client.files.get_file_by_id(FILE_DOCX)

    file_docx_representations = file_representations(client, file_docx)
    file_representations_print(file_docx.name, file_docx_representations)
```
Resulting in:
```
Hello, I'm Free Dev 001 [25428698627]

File Single Page.docx has 9 representations:
...
```
Quite a lot info there, let's check this one that represents a file thumbnail:
```json
    {
        "representation": "jpg",
        "properties": {
            "dimensions": "32x32",
            "paged": "false",
            "thumb": "true"
        },
        "info": {
            "url": "https://api.box.com/2.0/internal_files/1294096878155/versions/1415005971755/representations/jpg_thumb_32x32"
        }
    },
```

## Get a specific representation
In order to get a specific representation, you need to use the `representation hints` parameter on the method.
For example, to get the png 320x320 representation of the `FILE_DOCX`:
```python
def main():
    ...

    file_docx_representations_png = file_representations(client, file_docx, "[jpg?dimensions=320x320]")
    file_representations_print(file_docx.name, file_docx_representations_png)
```
Resulting in:
```json
[
    {
        "content": {
            "url_template": "https://public.boxcloud.com/api/2.0/internal_files/1294096878155/versions/1478711934034/representations/jpg_320x320/content/{+asset_path}"
        },
        "info": {
            "url": "https://api.box.com/2.0/internal_files/1294096878155/versions/1478711934034/representations/jpg_320x320"
        },
        "properties": {
            "dimensions": "320x320",
            "paged": "false",
            "thumb": "false"
        },
        "representation": "jpg",
        "status": {
            "state": "success"
        }
    }
]
```
Notice that the `state` is `success`, this means that the representation has been generated. If the representation is not available then the state will be `none`, `pending`, etc.

## Download the representation
Now that we have the `url_template` we can download the representation.
First let's create the simplest method to download a file from a url:
```python
def do_request(url: str, access_token: str):
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.content
```
Next let's create a representation download method:
```python
def representation_download(access_token: str, file_representation: FileFullRepresentationsEntriesField, file_name: str):
    if file_representation.status.state != FileFullRepresentationsEntriesStatusStateField.SUCCESS:
        print(f"Representation {file_representation.representation} is not ready")
        return

    url_template = file_representation.content.url_template
    url = url_template.replace("{+asset_path}", "")
    file_name = file_name.replace(".", "_").replace(" ", "_") + "." + file_representation.representation

    content = do_request(url, access_token)

    with open(file_name, "wb") as file:
        file.write(content)

    print(f"Representation {file_representation.representation} saved to {file_name}")

```
And finally use it in your main method:
```python
def main():
    ...

    access_token = client.auth.retrieve_token().access_token
    representation_download(access_token, file_docx_representations_png[0], file_docx.name)
```
My end result:
```json
[
    {
        "representation": "jpg",
        "properties": {
            "dimensions": "320x320",
            "paged": "false",
            "thumb": "false"
        },
        "info": {
            "url": "https://api.box.com/2.0/internal_files/1294096878155/versions/1415005971755/representations/jpg_320x320"
        },
        "status": {
            "state": "success"
        },
        "content": {
            "url_template": "https://public.boxcloud.com/api/2.0/internal_files/1294096878155/versions/1415005971755/representations/jpg_320x320/content/{+asset_path}"
        }
    }
]
Representation jpg saved to Single_Page_docx.jpg
```
And a new file has been downloaded to my local folder:

![Single Page_docx.jpg](./img/Single%20Page_docx.jpg)

## Get thumbnail representation
The python SDK as a helper method to get the thumbnail representation of a file:

Let's create a specific method for it:
```python
def file_thumbnail(
    client: Client, file: File, extension: GetFileThumbnailByIdExtension, min_h: int, min_w: int
) -> bytes:
    """Get file thumbnail"""
    thumbnail = client.files.get_file_thumbnail_by_id(
        file_id=file.id,
        extension=extension,
        min_height=min_h,
        min_width=min_w,
    )
    if not thumbnail:
        raise Exception(f"Thumbnail for {file.name} not available")
    return thumbnail
```
Notice that the requested thumbnail is not always available. If not we're generating an  exception, in which case you should select another representation.

Let's use it in our main method:
```python
def main():
    ...

    file_docx_thumbnail = file_thumbnail(client, 
                                        file_docx, 
                                        GetFileThumbnailByIdExtension.JPG, 
                                        min_h=94, 
                                        min_w=94)

    with open(file_docx.name.replace(".", "_").replace(" ", "_") + "_thumbnail.jpg", "wb") as file:
        shutil.copyfileobj(file_docx_thumbnail, file)
    print(f"\nThumbnail for {file_docx.name} saved to {file_docx.name.replace('.', '_')}_thumbnail.jpg")
```
Resulting in:
```
Thumbnail for Single Page.docx saved to Single Page_docx_thumbnail.jpg
```
And I have a new file on my local folder:

![Single Page_docx_thumbnail.jpg](./img/Single_Page_docx_thumbnail.jpg)

## Get PDF representation
Some documents can be converted to PDF, let's try it with the `FILE_PPTX`:
```python
def main():
    ...

    # Make sure the file exists
    file_ppt = client.files.get_file_by_id(FILE_PPTX)
    print(f"\nFile {file_ppt.name} ({file_ppt.id})")

    file_ppt_repr_pdf = file_representations(client, file_ppt, "[pdf]")
    file_representations_print(file_ppt.name, file_ppt_repr_pdf)
    access_token = client.auth.retrieve_token().access_token
    representation_download(access_token, file_ppt_repr_pdf[0], file_ppt.name)
```
resulting in:
```
Representation pdf saved to Document_(Powerpoint)_pptx.pdf
```
And a new file on my local folder:

[Document_(Powerpoint)_pptx.pdf](./img/Document_(Powerpoint)_pptx.pdf)

## Generate representations
Representations may not always be available.

Let's create a method that lists the status for a certain representation for all files in a folder:
```python
def folder_list_representation_status(client: Client, folder: Folder, representation: str):
    items = client.folders.get_folder_items(folder.id).entries
    print(f"\nChecking for {representation} status in folder [{folder.name}] ({folder.id})")
    for item in items:
        if isinstance(item, FileMini):
            file_repr = file_representations(client, item, "[" + representation + "]")
            if file_repr:
                state = file_repr[0].status.state.value
            else:
                state = "not available"
            print(f"File {item.name} ({item.id}) state: {state}")
```
And look for `extracted_text` representation on the `DEMO_FOLDER`:
```python
def main():
    ...

    folder = client.folder(DEMO_FOLDER).get()
    folder_list_representation_status(folder, "extracted_text")
```
Which results in:
```
Checking for extracted_text status in folder [file_representations] (223939315135)
File Audio.mp3 (1294103505129) state: not available
File Document (PDF).pdf (1294102659923) state: none
File Document (Powerpoint).pptx (1294096083753) state: none
File HTML.html (1294094879490) state: none
File JS-Small.js (1294098434302) state: none
File JSON.json (1294102660561) state: none
File Preview SDK Sample Excel.xlsx (1294097951585) state: none
File Single Page.docx (1294096878155) state: none
File ZIP.zip (1294105019347) state: not available
```
No luck there, in my case I don't have a single text representation available.
However for the ones where the status is none, we can request them to be generated. We do this by executing and HTTP GET on the info URL.
Let's start by specifically request all details for the `[extracted_text]` representation of the `FILE_PPTX`:
```python
def main()
    ...

    file_ppt_repr = file_representations(client, file_ppt, "[extracted_text]")
    file_representations_print(file_ppt.name, file_ppt_repr)
```
Resulting in:
```json
File Document (Powerpoint).pptx has 1 representations:

[
    {
        "content": {
            "url_template": "https://public.boxcloud.com/api/2.0/internal_files/1294096083753/versions/1478709361496/representations/extracted_text/content/{+asset_path}"
        },
        "info": {
            "url": "https://api.box.com/2.0/internal_files/1294096083753/versions/1478709361496/representations/extracted_text"
        },
        "properties": {
            "dimensions": null,
            "paged": null,
            "thumb": null
        },
        "representation": "extracted_text",
        "status": {
            "state": "none"
        }
    }
]

```
Now we get the `info url` to trigger the text generation, and list the representation again:
```python
def main()
    ...

    access_token = client.auth.retrieve_token().access_token

    if file_ppt_repr[0].status.state == "none":
        info_url = file_ppt_repr[0].info.url
        do_request(info_url, access_token)

    file_ppt_repr = file_representations(client, file_ppt, "[extracted_text]")
    file_representations_print(file_ppt.name, file_ppt_repr)
```
We can see that the state changed to `pending`:
```json
[
    {
        "representation": "extracted_text",
        "properties": {},
        "info": {
            "url": "https://api.box.com/2.0/internal_files/1294096083753/versions/1415005153353/representations/extracted_text"
        },
        "status": {
            "state": "pending"
        },
        "content": {
            "url_template": "https://public.boxcloud.com/api/2.0/internal_files/1294096083753/versions/1415005153353/representations/extracted_text/content/{+asset_path}"
        }
    }
]
```
## Get text representation
Once it changes to success, all we need to do is download the representation:
```python
def main()
    ...

    representation_download(access_token, file_ppt_repr[0], file_ppt.name)
```
And a new file showed up on my local folder:

[Document_(Powerpoint)_pptx.extracted_text](./img/Document_(Powerpoint)_pptx.extracted_text)

## Extra Credit
There are more image representations available:
* Check out a few more representations for each file in the `DEMO_FOLDER`

# Final thoughts
Although the Python SDK does provide a specific method to get thumbnails for a document, most of the time, you'll be using the generic methods:
1. `client.files.get_file_by_id(file.id, fields=["representations"])` to get the list all the representations available for a file
2. `client.files.get_file_by_id(file.id, fields=["representations"], x_rep_hints=rep_hints)` to get a specific representation
3. Download the representation using the `url_template` provided by the previous method if it is available.
4. If the representations are showing a `state` of `none` then you can trigger them by doing a `HTTP GET` using the `info_url`

