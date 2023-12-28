"""Box Collaborations"""
import logging
from box_sdk_gen.fetch import APIException
from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import Collaborations, Collaboration

from box_sdk_gen.managers.user_collaborations import (
    CreateCollaborationItem,
    CreateCollaborationItemTypeField,
    CreateCollaborationAccessibleBy,
    CreateCollaborationAccessibleByTypeField,
    CreateCollaborationRole,
    UpdateCollaborationByIdRole,
)

from utils.box_client_oauth import ConfigOAuth, get_client_oauth

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)


COLLABORATION_ROOT = "237027983333"
SAMPLE_FILE = "1373026823928"
SAMPLE_EMAIL = "YOUR_EMAIL+collab@gmail.com"


def create_file_collaboration(
    client: Client,
    item_id: str,
    user_email: str,
    role: CreateCollaborationRole,
) -> Collaboration:
    item = CreateCollaborationItem(
        type=CreateCollaborationItemTypeField.FILE,
        id=item_id,
    )
    accessible_by = CreateCollaborationAccessibleBy(
        type=CreateCollaborationAccessibleByTypeField.USER,
        login=user_email,
    )

    try:
        collaboration = client.user_collaborations.create_collaboration(
            item=item,
            accessible_by=accessible_by,
            role=role,
        )
    # return collaboration if user is already a collaborator
    except APIException as err:
        if err.status == 400 and err.code == "user_already_collaborator":
            # User is already a collaborator let's update the role
            collaborations = (
                client.list_collaborations.get_file_collaborations(
                    file_id=item_id,
                )
            )
            for collaboration in collaborations.entries:
                if collaboration.accessible_by.login == user_email:
                    collaboration_updated = (
                        client.user_collaborations.update_collaboration_by_id(
                            collaboration_id=collaboration.id,
                            role=role,
                        )
                    )
                    return collaboration_updated

    return collaboration


def print_file_collaboration(client: Client, collaboration: Collaboration):
    print(f"Collaboration: {collaboration.id}")

    print(f" Collaborator: {collaboration.accessible_by.login} ")
    print(f"         Role: {collaboration.role.value}")
    print(f"       Status: {collaboration.status.value}")

    return collaboration


def list_file_collaborations(client: Client, file_id: str) -> Collaborations:
    collaborations = client.list_collaborations.get_file_collaborations(
        file_id=file_id
    )
    print(f"\nFile {file_id} has {len(collaborations.entries)} collaborations")
    for collaboration in collaborations.entries:
        print_file_collaboration(client=client, collaboration=collaboration)


def update_file_collaboration(
    client: Client, collaboration_id: str, role: UpdateCollaborationByIdRole
) -> Collaboration:
    collaboration = client.user_collaborations.update_collaboration_by_id(
        collaboration_id=collaboration_id,
        role=role,
    )
    return collaboration


def delete_file_collaboration(client: Client, collaboration_id: str):
    client.user_collaborations.delete_collaboration_by_id(
        collaboration_id=collaboration_id,
    )


def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # Create a collaboration
    collaboration = create_file_collaboration(
        client=client,
        item_id=SAMPLE_FILE,
        user_email=SAMPLE_EMAIL,
        role=CreateCollaborationRole.EDITOR,
    )
    print(f"\nCreated collaboration: {collaboration.id}")

    # print collaboration details
    print_file_collaboration(client=client, collaboration=collaboration)

    # List collaborations
    list_file_collaborations(client=client, file_id=SAMPLE_FILE)

    # Update collaboration
    collaboration = update_file_collaboration(
        client=client,
        collaboration_id=collaboration.id,
        role=UpdateCollaborationByIdRole.VIEWER,
    )
    print(f"\nUpdated collaboration: {collaboration.id}")
    print_file_collaboration(client=client, collaboration=collaboration)

    # Delete collaboration
    delete_file_collaboration(client=client, collaboration_id=collaboration.id)
    list_file_collaborations(client=client, file_id=SAMPLE_FILE)


if __name__ == "__main__":
    main()
