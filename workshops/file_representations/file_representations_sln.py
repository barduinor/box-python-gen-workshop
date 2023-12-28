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


def do_request(url: str, access_token: str):
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.content


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


def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # make sure the file exists
    # file_docx = client.files.get_file_by_id(FILE_DOCX)

    # file_docx_representations = file_representations(client, file_docx)
    # file_representations_print(file_docx.name, file_docx_representations)

    # file_docx_representations_png = file_representations(client, file_docx, "[jpg?dimensions=320x320]")
    # file_representations_print(file_docx.name, file_docx_representations_png)

    # access_token = client.auth.retrieve_token().access_token
    # representation_download(access_token, file_docx_representations_png[0], file_docx.name)

    # file_docx_thumbnail = file_thumbnail(client, file_docx, GetFileThumbnailByIdExtension.JPG, min_h=94, min_w=94)

    # with open(file_docx.name.replace(".", "_").replace(" ", "_") + "_thumbnail.jpg", "wb") as file:
    #     shutil.copyfileobj(file_docx_thumbnail, file)
    # print(f"\nThumbnail for {file_docx.name} saved to {file_docx.name.replace('.', '_')}_thumbnail.jpg")

    # # Make sure the file exists
    # file_ppt = client.files.get_file_by_id(FILE_PPTX)
    # print(f"\nFile {file_ppt.name} ({file_ppt.id})")

    # file_ppt_repr_pdf = file_representations(client, file_ppt, "[pdf]")
    # file_representations_print(file_ppt.name, file_ppt_repr_pdf)
    # access_token = client.auth.retrieve_token().access_token
    # representation_download(access_token, file_ppt_repr_pdf[0], file_ppt.name)

    # folder = client.folders.get_folder_by_id(DEMO_FOLDER)
    # folder_list_representation_status(client, folder, "extracted_text")

    # file_ppt_repr = file_representations(client, file_ppt, "[extracted_text]")
    # file_representations_print(file_ppt.name, file_ppt_repr)

    # access_token = client.auth.retrieve_token().access_token

    # if file_ppt_repr[0].status.state == "none":
    #     info_url = file_ppt_repr[0].info.url
    #     do_request(info_url, access_token)

    # file_ppt_repr = file_representations(client, file_ppt, "[extracted_text]")
    # file_representations_print(file_ppt.name, file_ppt_repr)

    # representation_download(access_token, file_ppt_repr[0], file_ppt.name)


if __name__ == "__main__":
    main()
