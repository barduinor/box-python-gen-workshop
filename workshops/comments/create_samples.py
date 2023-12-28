"""Uploads or Creates samples for exercises."""
import pathlib
import os
import logging

from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import Folder, File, Files
from box_sdk_gen.managers.folders import CreateFolderParent
from box_sdk_gen.managers.uploads import (
    PreflightFileUploadCheckParent,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)
from box_sdk_gen.fetch import APIException

logging.getLogger(__name__)


def create_box_folder(client: Client, folder_name: str, parent_folder: Folder) -> Folder:
    """create a folder in box"""

    try:
        folder = client.folders.create_folder(folder_name, CreateFolderParent(id=parent_folder.id))
    except APIException as err:
        if err.code == "item_name_in_use":
            folder_id = err.context_info["conflicts"][0]["id"]
            folder = client.folders.get_folder_by_id(folder_id)
        else:
            raise err

    logging.info("Folder %s with id: %s", folder.name, folder.id)
    return folder


def folder_upload(
    client: Client,
    box_base_folder: Folder,
    local_folder_path: str,
) -> Folder:
    """upload a folder to box"""

    local_folder = pathlib.Path(local_folder_path)

    for item in local_folder.iterdir():
        if item.is_dir():
            new_box_folder = create_box_folder(client, item.name, box_base_folder)
            logging.info(" Folder %s", item.name)
            folder_upload(client, new_box_folder, str(item))
        else:
            file = file_upload(client, str(item), box_base_folder)
            logging.info(" \tUploaded %s (%s) %s bytes", file.name, file.id, file.size)

    return box_base_folder


def file_upload(client: Client, file_path: str, folder: Folder) -> File:
    """upload a file to box"""

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    file_id = None
    try:
        pre_flight_arg = PreflightFileUploadCheckParent(id=folder.id)
        client.uploads.preflight_file_upload_check(file_name, file_size, pre_flight_arg)
    except APIException as err:
        if err.code == "item_name_in_use":
            file_id = err.context_info["conflicts"]["id"]
        else:
            raise err

    upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder.id))
    if file_id is None:
        # upload new file
        files: Files = client.uploads.upload_file(upload_arg, file=open(file_path, "rb"))
        file = files.entries[0]
    else:
        # upload new version
        files: Files = client.uploads.upload_file_version(file_id, upload_arg, file=open(file_path, "rb"))
        file = files.entries[0]

    return file


def create_samples(client: Client):
    """Uploads sample content to Box."""
    wks_folder = create_box_folder(client, "workshops", client.folders.get_folder_by_id("0"))

    comments_folder = create_box_folder(client, "comments", wks_folder)
    folder_upload(client, comments_folder, "workshops/comments/content_samples/")
