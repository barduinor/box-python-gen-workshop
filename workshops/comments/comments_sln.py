"""Box File Comments"""

import logging

from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.fetch import APIException
from box_sdk_gen.schemas import File, Comment

from box_sdk_gen.managers.comments import CreateCommentItem, CreateCommentItemTypeField

from utils.box_client_oauth import ConfigOAuth, get_client_oauth

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)


COMMENTS_ROOT = "223269791429"
SAMPLE_FILE = "1290064263703"


def file_comments_print(client: Client, file: File):
    """Print all comments for a file"""
    comments = client.comments.get_file_comments(file.id)
    print(f"\nComments for file {file.name} ({file.id}):")
    print("-" * 10)
    for comment in comments.entries:
        if comment.is_reply_comment:
            print(">" * 2, end="")
        print(f"{comment.message} by {comment.created_by.name} ({comment.created_at})")
    print("-" * 10)


def file_comment_add(client: Client, file: File, message: str) -> Comment:
    """Add a comment to a file"""
    item_arg = CreateCommentItem(id=file.id, type=CreateCommentItemTypeField.FILE)
    return client.comments.create_comment(message, item=item_arg)


def file_comment_reply(client: Client, comment: Comment, message: str) -> Comment:
    """Reply to a comment"""
    item_arg = CreateCommentItem(id=comment.id, type=CreateCommentItemTypeField.COMMENT)
    return client.comments.create_comment(message, item_arg)


def file_comment_delete(client: Client, comment: Comment):
    """Delete a comment"""
    try:
        client.comments.delete_comment_by_id(comment.id)
    except APIException as err:
        if err.status != 404:
            raise err


def main():
    """Simple script to demonstrate how to use the Box SDK"""
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    file = client.files.get_file_by_id(SAMPLE_FILE)

    # print file comments
    file_comments_print(client, file)

    # add first comment
    comment = file_comment_add(client, file, "This is a comment")
    file_comments_print(client, file)

    # add another comment
    comment = file_comment_add(client, file, "What is this file about?")
    file_comments_print(client, file)

    # reply to the last comment
    comment_reply = file_comment_reply(client, comment, "I hear you!!! This is a sample file")
    file_comments_print(client, file)

    # delete all comments
    file_comment_delete(client, comment_reply)
    comments = client.comments.get_file_comments(file.id)
    for comment in comments.entries:
        file_comment_delete(client, comment)
    file_comments_print(client, file)


if __name__ == "__main__":
    main()
