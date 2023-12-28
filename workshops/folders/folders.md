# Folders
Folders, together with Files, are at the core of the Box API. 
Folders can be uploaded and downloaded, as well as hold important metadata information about the content.
They are the primary way to organize content in Box.
## Concepts
Box is not a file systems, but it does have a concept of folders, even if it is a somewhat virtual concept.
This is because of the users familiarity with file systems, and the need to organize content.
So a folder is essentially a container of items (files and folders), with a nested parent folder.

Folder id 0 is the root folder for the user, and it is the only folder that does not have a parent folder.
Folder names must be unique within the parent folder.


## Folder API
References to our documentation:
* [SDK Folder](https://github.com/box/box-python-sdk-gen/blob/main/docs/folders.md)
* [API Folder Guide](https://developer.box.com/guides/folders/)
* [API Reference](https://developer.box.com/reference/resources/folder/)


# Exercises
## Setup
Create a `folders_init.py` file on the root of the project and execute the following code:
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
INFO:root:Folder folders with id: 233715688542
```
`Each id is unique to your Box account, so your results will be different.`

Open your Box account and verify that the following content was uploaded:
```
- workshops
    - folders
```


Next, create a `folders.py` file on the root of the project that you will use to write your code:
```python
"""Box Folder workshop"""
import logging
from typing import Union

from box_sdk_gen.fetch import APIException
from utils.box_client_oauth import ConfigOAuth, get_client_oauth
from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import Folder, FolderMini, FileMini, WebLinkMini
from box_sdk_gen.managers.folders import Items, CreateFolderParent

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)


def main():
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")    

if __name__ == "__main__":
    main()
```

## List folder content
Create a method to list the content of a folder, by id.
Make the default folder id the root folder id.
List the contents of the root folder.
Add a couple of methods to print the folder and it's objects.

```python
def print_box_item(box_item: Union[FileMini, FolderMini, WebLinkMini], level: int = 0):
    """Basic print of a Box Item attributes"""
    print(f"{'   ' * level}({box_item.id}) {box_item.name}{'/' if box_item.type == 'folder' else ''}")


def print_box_items(box_items: Items):
    """Print items"""
    print("--- Items ---")
    for box_item in box_items.entries:
        print_box_item(box_item)
    print("-------------")


def get_folder_items(box_client: Client, box_folder_id: str = "0") -> Items:
    """Get folder items"""
    return box_client.folders.get_folder_items(folder_id=box_folder_id)
```
Call the method with the root folder:
```python
def main():
    ...

    items = get_folder_items(client)
    print_box_items(items)
```
Should result in something similar to:
```
--- Items ---
(216797257531) My Signed Documents/
(221723756896) UIE Samples/
(223095001439) workshops/
(1204688948039) Get Started with Box.pdf
-------------
```
## List folder content recursively
Create a method to list the content of a folder, by id, recursively.
```python
def print_folder_items_recursive(box_client: Client, folder_id: str, level: int = 0) -> Items:
    """Get folder items recursively"""
    folder = box_client.folders.get_folder_by_id(folder_id)
    print_box_item(folder, level)
    box_items = get_folder_items(box_client, folder.id)
    for box_item in box_items.entries:
        if box_item.type == "folder":
            print_folder_items_recursive(box_client, box_item.id, level + 1)
        else:
            print_box_item(box_item, level + 1)
```
Call the method with the root folder:
```python
def main():
    ...
    
    # root folder id is always "0"
    print_folder_items_recursive(client, "0")
```
Should result in something similar to:
```
(0) All Files/
   (223095001439) workshops/
      (233715688542) folders/
   (1204688948039) Get Started with Box.pdf
```

## Create a method to always return the folder `folders`
```python
def get_workshop_folder(box_client: Client) -> Folder:
    """Get workshop folder"""
    # root = box_client.folder(folder_id="0").get()
    workshops_folder_list = [
        box_item
        for box_item in box_client.folders.get_folder_items("0").entries
        if box_item.name == "workshops" and box_item.type == "folder"
    ]
    if workshops_folder_list == []:
        raise ValueError("'Workshop' folder not found")

    folders_folder_list = [
        box_item
        for box_item in box_client.folders.get_folder_items(workshops_folder_list[0].id).entries
        if box_item.name == "folders" and box_item.type == "folder"
    ]
    if folders_folder_list == []:
        raise ValueError("'Folders' folder not found")

    return folders_folder_list[0]
```
And then test it:
```python
def main():
    ...

    workshop_folder = get_workshop_folder(client)
    print_box_item(workshop_folder)
```
Result:
```
(233715688542) folders/
```
This example serves to illustrate how to navigate the folder structure, and as you can see this is not very practical.

There is no path navigation in Box, so make sure your app keeps track of the folder ids it needs to access.

## Creating folders
Create a method to create subfolder in a parent folder, returning the created folder.
If the folder already exists just return the exiting folder. 
```python
def create_box_folder(box_client: Client, folder_name: str, parent_folder: Folder) -> Folder:
    """create a folder in box"""

    try:
        parent_arg = CreateFolderParent(parent_folder.id)
        folder = box_client.folders.create_folder(
            folder_name,
            parent_arg,
        )
    except APIException as box_err:
        if box_err.code == "item_name_in_use":
            box_folder_id = box_err.context_info["conflicts"][0]["id"]
            folder = box_client.folders.get_folder_by_id(box_folder_id)
        else:
            raise box_err

    # logging.info("Folder %s with id: %s", folder.name, folder.id)
    return folder
```
And test it with:
```python
def main():
    ...

    my_documents = create_box_folder(client, "my_documents", workshop_folder)

    print_folder_items_recursive(client, workshop_folder.id)
```
Resulting in:
```
(233715688542) folders/
   (233720706445) my_documents/
```

## Creating a few more folders
Create a folder structure like this:
```
- workshops
    - folders
        - my_documents
            - work
        - downloads
            - personal
```
```python
def main():
    ...

    my_documents = create_box_folder(client, "my_documents", workshop_folder)
    work = create_box_folder(client, "work", my_documents)

    downloads = create_box_folder(client, "downloads", workshop_folder)
    personal = create_box_folder(client, "personal", downloads)

    print_folder_items_recursive(client, workshop_folder.id)
```    
Resulting in:
```
(233715688542) folders/
   (233716501320) downloads/
      (233715942209) personal/
   (233720706445) my_documents/
      (233720697399) work/
```
## Copy folders
Copy the `personal` folder to the `my_documents` folder.
If the folder already exists just return the exiting folder.
This is an example of how to handle error in Box.
```python
def main():
    ...

    # copy folder
    try:
        parent_arg = CreateFolderParent(my_documents.id)
        my_docs_personal = client.folders.copy_folder(personal.id, parent_arg, "personal")
    except APIException as err:
        if err.code == "item_name_in_use":
            folder_id = err.context_info["conflicts"]["id"]
            my_docs_personal = client.folders.get_folder_by_id(folder_id)
            logging.info("Folder %s with id: %s already exists", my_docs_personal.name, my_docs_personal.id)
        else:
            raise err
    print_folder_items_recursive(client, workshop_folder.id)
```


Resulting in:
```
(233715688542) folders/
   (233716501320) downloads/
      (233715942209) personal/
   (233720706445) my_documents/
      (233735763756) personal/
      (233720697399) work/
```

## Update a folder
Add a description to the `downloads` folder.
```python
    # update folder description
    downloads = client.folders.update_folder_by_id(
        downloads.id, description="This is where my downloads go, remember to clean it once in a while"
    )
    print(f"{downloads.type.value} {downloads.id} {downloads.name}")
    print(f"Description: {downloads.description}")
```
Resulting in:
```
folder 233716501320 downloads
Description: This is where my downloads go, remember to clean it once in a while
```
## Delete a folder
Create a new folder called `tmp` inside `downloads`
Create a new folder called `tmp2` inside `tmp`
Delete folder `tmp` and all its contents.

The delete method accepts a `recursive` parameter that can delete all content of the folder `no questions asked`.

So `be careful` when using it.

```python
    # Delete a folder
    tmp = create_box_folder(client, "tmp", downloads)
    tmp2 = create_box_folder(client, "tmp2", tmp)

    print("--- Before the delete ---")
    print_folder_items_recursive(client, downloads.id)
    print("---")

    try:
        client.folders.delete_folder_by_id(tmp.id)
    except APIException as err:
        if err.code == "folder_not_empty":
            logging.info(f"Folder {tmp.name} is not empty, deleting recursively")
            # print(f"Folder {tmp.name} is not empty, deleting recursively")
            try:
                client.folders.delete_folder_by_id(tmp.id, recursive=True)
            except APIException as err_l2:
                raise err_l2
        else:
            raise err

    print("--- After the delete ---")
    print_folder_items_recursive(client, downloads.id)
    print("---")

```
Resulting in:
```
--- Before the delete ---
(233716501320) downloads/
   (233715942209) personal/
   (233735689841) tmp/
      (233735634574) tmp2/
---
INFO:root:Folder tmp is not empty, deleting recursively
--- After the delete ---
(233716501320) downloads/
   (233715942209) personal/
---
```
## Rename a folder
Rename the `personal` folder under `downloads` to `games`.

What were you thinking? This is a corporate laptop!!!

Delete the `games` folder
```python
def main():
    ...

    # Rename folder
    print("Renaming personal downloads to games")
    games = client.folders.update_folder_by_id(personal.id, name="games")
    print_folder_items_recursive(client, downloads.id)
    print("---")

    print("Deleting games")
    client.folders.delete_folder_by_id(games.id)
    print_folder_items_recursive(client, downloads.id)
    print("---")

    print_folder_items_recursive(client, workshop_folder.id)
```
Resulting in:
```
Renaming personal downloads to games
(233716501320) downloads/
   (233738125394) games/
---
Deleting games
(233716501320) downloads/
---
```
## Extra Credit
There are many more methods you can try for the folder object.
Try them out and see what you can find:
* [Move](https://github.com/box/box-python-sdk-gen/blob/main/docs/folders.md#move-a-folder)
* [Create a Folder Lock](https://github.com/box/box-python-sdk-gen/blob/main/docs/folder_locks.md#create-folder-lock)
* [Get Folder Locks](https://github.com/box/box-python-sdk-gen/blob/main/docs/folder_locks.md#list-folder-locks)
* [Delete a Folder Lock](https://github.com/box/box-python-sdk-gen/blob/main/docs/folder_locks.md#delete-folder-lock)

# Final thoughts

`Folders` are the primary way to organize content in Box.

They are a virtual concept, but they are very familiar to users.

Folder id 0 is the root folder for the user, and it is the only folder that does not have a parent folder.

Folder names must be unique within the parent folder.

There is no path navigation in Box, so make sure your app keeps track of the folder ids it needs to access.








