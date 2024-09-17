from typing import Any, Dict, List, Optional

import requests

from logs import general_log, return_log


class NotionAdapter:
    """Adapter class to fetch Notion API configuration details."""

    def __init__(self, config: Dict[str, Any]):
        general_log.logger.info(
            "Initializing NotionAdapter with provided configuration."
        )
        self.token = config["notion"]["token"]
        self.url = config["notion"]["url"]

    def get_headers(self) -> Dict[str, str]:
        """Return the headers required for Notion API requests."""
        general_log.logger.info("Generating headers for Notion API requests.")
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        return_log.logger.info(f"Headers: {headers}")
        return headers

    def get_base_url(self) -> str:
        """Return the Notion base URL."""
        general_log.logger.info("Fetching base URL for Notion API.")
        return_log.logger.info(f"Base URL: {self.url}")
        return self.url


class NotionRequestFactory:
    """Factory class to create Notion API requests."""

    def __init__(self, config: Dict[str, Any], database_id: str, type: str = "main"):
        general_log.logger.info(
            "Initializing NotionRequestFactory with config and database_id."
        )
        self.notion_adapter = NotionAdapter(config)
        self.type = type
        self.database_id = database_id
        return_log.logger.info(f"Database ID: {self.database_id}")

    def create_page(self, data: Dict[str, Any]) -> requests.Response:
        """
        Create a new page in the Notion database.

        Args:
            data (dict): The page properties.

        Returns:
            Response: The response from the Notion API.
        """
        general_log.logger.info("Creating a new page in the Notion database.")
        create_url = f"{self.notion_adapter.get_base_url()}/pages"
        payload = {
            "parent": {"database_id": self.database_id},
            "properties": data,
        }
        return_log.logger.info(f"Payload for creating page: {payload}")
        response = requests.post(
            create_url, headers=self.notion_adapter.get_headers(), json=payload
        )
        general_log.logger.info("Page creation request sent.")
        return_log.logger.info(
            f"Response from Notion API: {response.status_code} - {response.text}"
        )
        return response

    def get_pages(self, num_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve pages from the Notion database.

        Args:
            num_pages (Optional[int]): The number of pages to fetch. If None, fetch all.

        Returns:
            List[Dict]: The list of pages.
        """
        general_log.logger.info(
            f"Fetching pages from Notion database with num_pages={num_pages}."
        )
        query_url = (
            f"{self.notion_adapter.get_base_url()}/databases/{self.database_id}/query"
        )
        get_all = num_pages is None
        page_size = 100 if get_all else num_pages

        payload = {"page_size": page_size}
        return_log.logger.info(f"Initial payload for fetching pages: {payload}")
        response = requests.post(
            query_url, json=payload, headers=self.notion_adapter.get_headers()
        )
        if response.status_code == 504:
            pass # TODO handle timeout error
        return_log.logger.info(f"Response from Notion API: {response.status_code} - {response.text}")
        
        data = response.json()
        return_log.logger.info(f"Initial response data: {data}")
        results = data.get("results", [])
        while data.get("has_more") and get_all:
            general_log.logger.info(
                "Fetching additional pages from Notion (pagination)."
            )
            payload["start_cursor"] = data["next_cursor"]
            response = requests.post(
                query_url, json=payload, headers=self.notion_adapter.get_headers()
            )
            data = response.json()
            return_log.logger.info(f"Additional response data: {data}")
            results.extend(data.get("results", []))

        general_log.logger.info(f"Total pages fetched: {len(results)}")
        return results

    def update_page(self, page_id: str, data: Dict[str, Any]) -> requests.Response:
        """
        Update a page in the Notion database.

        Args:
            page_id (str): The ID of the page to update.
            data (dict): The properties to update.

        Returns:
            Response: The response from the Notion API.
        """
        general_log.logger.info(f"Updating page with ID: {page_id}.")
        update_url = f"{self.notion_adapter.get_base_url()}/pages/{page_id}"
        payload = {"properties": data}
        return_log.logger.info(f"Payload for updating page: {payload}")
        response = requests.patch(
            update_url, headers=self.notion_adapter.get_headers(), json=payload
        )
        general_log.logger.info(f"Page update request sent for page ID: {page_id}.")
        return_log.logger.info(
            f"Response from Notion API: {response.status_code} - {response.text}"
        )
        return response
    
    def get_type(self) -> str:
        return self.type


# def process_pages(notion_request_factory: NotionRequestFactory):
#     """Process pages from Notion, iterating through properties."""
#     pages = notion_request_factory.get_pages()

#     for page in pages:
#         page_id = page["id"]
#         props = page["properties"]
#         status = props["STATUS"]["formula"]["string"]
#         code = props["CÓDIGO"]["title"][0]["text"]["content"]
#         subject = props["MATÉRIA"]["rich_text"][0]["text"]["content"]
#         new_grid = props["NOVA GRADE"]["checkbox"]
#         priority = props["PRIORIDADE"]["rollup"]["number"]
#         grade = props["NOTA"]["number"]
#         year = props["ANO"]["rich_text"][0]["text"]["content"]
#         prerequisites = props["PRÉ-REQUISITO(S)"]["relation"]
#         prerequisites_status = props["STATUS DOS PRÉ-REQUISITOS"]["rollup"]["array"]
#         release = props["LIBERA"]["relation"]
#         workload = props["CH"]["number"]
#         left = props["FALTAM"]["rollup"]["number"]
#         pass
