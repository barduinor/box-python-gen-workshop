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


def print_folder_items_recursive(box_client: Client, folder_id: str, level: int = 0):
    """Get folder items recursively"""
    folder = box_client.folders.get_folder_by_id(folder_id)
    print_box_item(folder, level)
    box_items = get_folder_items(box_client, folder.id)
    for box_item in box_items.entries:
        if box_item.type == "folder":
            print_folder_items_recursive(box_client, box_item.id, level + 1)
        else:
            print_box_item(box_item, level + 1)


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


def main():
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # items = get_folder_items(client)
    # print_box_items(items)

    # # root folder id is always "0"
    # print_folder_items_recursive(client, "0")

    # workshop_folder = get_workshop_folder(client)
    # print_box_item(workshop_folder)

    # my_documents = create_box_folder(client, "my_documents", workshop_folder)
    # work = create_box_folder(client, "work", my_documents)

    # downloads = create_box_folder(client, "downloads", workshop_folder)
    # personal = create_box_folder(client, "personal", downloads)

    # print_folder_items_recursive(client, workshop_folder.id)

    # # copy folder
    # try:
    #     parent_arg = CreateFolderParent(my_documents.id)
    #     my_docs_personal = client.folders.copy_folder(personal.id, parent_arg, "personal")
    # except APIException as err:
    #     if err.code == "item_name_in_use":
    #         folder_id = err.context_info["conflicts"]["id"]
    #         my_docs_personal = client.folders.get_folder_by_id(folder_id)
    #         logging.info("Folder %s with id: %s already exists", my_docs_personal.name, my_docs_personal.id)
    #     else:
    #         raise err
    # print_folder_items_recursive(client, workshop_folder.id)

    # # update folder description
    # downloads = client.folders.update_folder_by_id(
    #     downloads.id, description="This is where my downloads go, remember to clean it once in a while"
    # )
    # print(f"{downloads.type.value} {downloads.id} {downloads.name}")
    # print(f"Description: {downloads.description}")

    # # Delete a folder
    # tmp = create_box_folder(client, "tmp", downloads)
    # tmp2 = create_box_folder(client, "tmp2", tmp)

    # print("--- Before the delete ---")
    # print_folder_items_recursive(client, downloads.id)
    # print("---")

    # try:
    #     client.folders.delete_folder_by_id(tmp.id)
    # except APIException as err:
    #     if err.code == "folder_not_empty":
    #         logging.info(f"Folder {tmp.name} is not empty, deleting recursively")
    #         # print(f"Folder {tmp.name} is not empty, deleting recursively")
    #         try:
    #             client.folders.delete_folder_by_id(tmp.id, recursive=True)
    #         except APIException as err_l2:
    #             raise err_l2
    #     else:
    #         raise err

    # print("--- After the delete ---")
    # print_folder_items_recursive(client, downloads.id)
    # print("---")

    # # Rename folder
    # print("Renaming personal downloads to games")
    # games = client.folders.update_folder_by_id(personal.id, name="games")
    # print_folder_items_recursive(client, downloads.id)
    # print("---")

    # print("Deleting games")
    # client.folders.delete_folder_by_id(games.id)
    # print_folder_items_recursive(client, downloads.id)
    # print("---")

    # print_folder_items_recursive(client, workshop_folder.id)


if __name__ == "__main__":
    main()
