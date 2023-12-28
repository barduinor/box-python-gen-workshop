"""Box Shared links"""
import logging
from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import File, Folder
from box_sdk_gen.managers.shared_links_files import (
    AddShareLinkToFileSharedLink,
    AddShareLinkToFileSharedLinkAccessField,
    AddShareLinkToFileSharedLinkPermissionsField,
)
from box_sdk_gen.managers.shared_links_folders import (
    AddShareLinkToFolderSharedLink,
    AddShareLinkToFolderSharedLinkAccessField,
    AddShareLinkToFolderSharedLinkPermissionsField,
)

# from box_sdk_gen.managers.shared_links_folders

from utils.box_client_oauth import ConfigOAuth, get_client_oauth

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)


SHARED_LINKS_ROOT = "223783108378"
SAMPLE_FILE = "1293174201535"


def file_shared_link_update(
    client: Client,
    file_id: str,
    shared_link_args: AddShareLinkToFileSharedLink,
) -> File:
    return client.shared_links_files.add_share_link_to_file(
        file_id=file_id, shared_link=shared_link_args, fields=["shared_link"]
    )


def folder_shared_link_update(
    client: Client,
    folder_id: str,
    shared_link_args,
) -> Folder:
    return client.shared_links_folders.add_share_link_to_folder(
        folder_id=folder_id, shared_link=shared_link_args, fields=["shared_link"]
    )


def file_from_shared_link(client: Client, link: str, password: str = None) -> File:
    box_api = f"shared_link={link}&shared_link_password={password}"
    return client.shared_links_files.find_file_for_shared_link(box_api)


def folder_from_shared_link(client: Client, link: str, password: str = None) -> Folder:
    box_api = f"shared_link={link}&shared_link_password={password}"
    return client.shared_links_folders.find_folder_for_shared_link(box_api)


def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # Make sure file exists
    file = client.files.get_file_by_id(SAMPLE_FILE)

    # shared_link_args = AddShareLinkToFileSharedLink(
    #     access=AddShareLinkToFileSharedLinkAccessField.OPEN,
    #     permissions=AddShareLinkToFileSharedLinkPermissionsField(
    #         can_download=True,
    #         can_preview=True,
    #     ),
    # )
    # file_shared_link = file_shared_link_update(
    #     client,
    #     SAMPLE_FILE,
    #     shared_link_args,
    # )
    # print(f"\nShared link for {file.name}: {file_shared_link.shared_link}")

    shared_link_args = AddShareLinkToFileSharedLink(
        access=AddShareLinkToFileSharedLinkAccessField.OPEN,
        permissions=AddShareLinkToFileSharedLinkPermissionsField(
            can_download=False,
            can_preview=True,
        ),
    )
    file_shared_link = file_shared_link_update(
        client,
        SAMPLE_FILE,
        shared_link_args,
    )
    print(f"\nShared link for {file.name}: {file_shared_link.shared_link}")

    # Make sure the folder exists
    folder = client.folders.get_folder_by_id(SHARED_LINKS_ROOT)

    shared_link_args = AddShareLinkToFolderSharedLink(
        access=AddShareLinkToFolderSharedLinkAccessField.OPEN,
        permissions=AddShareLinkToFolderSharedLinkPermissionsField(
            can_download=True,
            can_preview=True,
        ),
    )
    folder_shared_link = folder_shared_link_update(client, SHARED_LINKS_ROOT, shared_link_args)
    print(f"\nShared link for {folder.name}: {folder_shared_link.shared_link}")

    # shared_link_args = AddShareLinkToFileSharedLink(
    #     access=AddShareLinkToFileSharedLinkAccessField.OPEN,
    #     permissions=AddShareLinkToFileSharedLinkPermissionsField(
    #         can_download=True,
    #         can_preview=True,
    #     ),
    # )
    # file_shared_link = file_shared_link_update(
    #     client,
    #     SAMPLE_FILE,
    #     shared_link_args,
    # )
    # print(f"\nDownload URL for {file.name}: {file_shared_link.shared_link.download_url}")

    item_a = file_from_shared_link(client, file_shared_link.shared_link.url)
    print(f"\nItem from shared link: {item_a.name} is a {item_a.type.value} ({item_a.id})")

    item_b = folder_from_shared_link(client, folder_shared_link.shared_link.url)
    print(f"\nItem from shared link: {item_b.name} is a {item_b.type.value} ({item_b.id})")


if __name__ == "__main__":
    main()
