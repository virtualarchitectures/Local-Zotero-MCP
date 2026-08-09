"""Thin HTTP wrapper around the Zotero desktop app's Local API."""

from __future__ import annotations

import httpx

BASE_URL = "http://127.0.0.1:23119/api"
LIBRARY_PATH = "/users/0"

NOT_RUNNING_MESSAGE = (
    "Could not reach Zotero. Make sure Zotero is running and that "
    "Settings → Advanced → 'Allow other applications on this "
    "computer to communicate with Zotero' is enabled."
)


class ZoteroClient:
    """Minimal client for read requests against the local Zotero library."""

    def __init__(self) -> None:
        self._http = httpx.Client(
            base_url=BASE_URL, follow_redirects=False, timeout=10.0
        )

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        """GET a library-relative path (e.g. "/items") and return the raw response."""
        try:
            response = self._http.get(f"{LIBRARY_PATH}{path}", params=params)
        except httpx.ConnectError as exc:
            raise ValueError(NOT_RUNNING_MESSAGE) from exc

        if response.status_code >= 400 and response.status_code != 302:
            raise ValueError(
                f"Zotero returned {response.status_code} for {path}: {response.text}"
            )
        return response

    def get_json(self, path: str, params: dict | None = None):
        return self.get(path, params).json()


client = ZoteroClient()
