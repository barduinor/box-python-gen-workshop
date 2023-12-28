""" Searching Box exercises"""
import logging
from typing import List, Union

from box_sdk_gen.client import BoxClient as Client

from box_sdk_gen.schemas import Items, FileMini, FolderMini, WebLinkMini, SearchResults, SearchResultsWithSharedLinks

from box_sdk_gen.managers.search import SearchForContentContentTypes

from utils.box_client_oauth import ConfigOAuth, get_client_oauth

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)


def print_box_item(box_item: Union[FileMini, FolderMini, WebLinkMini]):
    """Basic print of a Box Item attributes"""
    print(f"Type: {box_item.type.value} ID: {box_item.id} Name: {box_item.name}")


def print_search_results(items: Items):
    """Print search results"""
    print("--- Search Results ---")
    for item in items.entries:
        print_box_item(item)
    print("--- End Search Results ---")


def simple_search(
    client: Client,
    query: str,
    content_types: List[SearchForContentContentTypes] = None,
    result_type: str = None,
    ancestor_folder_ids: List[str] = None,
) -> Union[SearchResults, SearchResultsWithSharedLinks]:
    """Search by query in any Box content"""

    return client.search.search_for_content(
        query=query,
        content_types=content_types,
        type=result_type,
        ancestor_folder_ids=ancestor_folder_ids,
    )


def main():
    conf = ConfigOAuth()
    client = get_client_oauth(conf)

    user = client.users.get_user_me()
    print(f"\nHello, I'm {user.name} ({user.login}) [{user.id}]")

    # # Simple Search
    # search_results = simple_search(client, "apple")
    # print_search_results(search_results)

    # # Expanded Search
    # search_results = simple_search(client, "apple banana")
    # print_search_results(search_results)

    # # "Exact" Search
    # search_results = simple_search(client, '"apple banana"')
    # print_search_results(search_results)

    # # Operators Search
    # search_results = simple_search(client, "apple NOT banana")
    # print_search_results(search_results)

    # # Operators Search
    # search_results = simple_search(client, "apple AND pineapple")
    # print_search_results(search_results)

    # # Operators Search
    # search_results = simple_search(client, "pineapple OR banana")
    # print_search_results(search_results)

    # # More Searches
    # search_results = simple_search(client, "ananas")
    # print_search_results(search_results)

    # # Search only in name
    # search_results = simple_search(
    #     client,
    #     "ananas",
    #     content_types=[
    #         "name",
    #     ],
    # )
    # print_search_results(search_results)

    # # Search in name and description
    # search_results = simple_search(
    #     client,
    #     "ananas",
    #     content_types=[
    #         "name",
    #         "description",
    #     ],
    # )
    # print_search_results(search_results)

    # # Search for folders only
    # search_results = simple_search(client, "apple", result_type="folder")
    # print_search_results(search_results)

    # # Search banana
    # search_results = simple_search(client, "banana")

    # print("--- Search Results ---")
    # for item in search_results.entries:
    #     print(f"Type: {item.type.value} ID: {item.id} Name: {item.name} Folder: {item.parent.name}")
    # print("--- End Search Results ---")

    # # Ancestor Search

    # # Make sure folders exist
    # folder_apple_banana = client.folders.get_folder_by_id("231320711952")
    # folder_banana_apple = client.folders.get_folder_by_id("231320108594")

    # # But we only need the ids
    # search_results = simple_search(
    #     client,
    #     "banana",
    #     ancestor_folder_ids=[folder_apple_banana.id, folder_banana_apple.id],
    #     result_type="file",
    # )

    # print("--- Search Results ---")
    # for item in search_results.entries:
    #     print(f"Type: {item.type.value} ID: {item.id} Name: {item.name} Folder: {item.parent.name}")
    # print("--- End Search Results ---")


if __name__ == "__main__":
    main()
