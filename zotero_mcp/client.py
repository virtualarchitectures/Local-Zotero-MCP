"""Thin HTTP wrapper around the Zotero desktop app's Local API."""

from __future__ import annotations

import httpx

BASE_URL = "http://127.0.0.1:23119/api"
USER_LIBRARY_PATH = "/users/0"

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

    def _resolve(self, path: str, library: str | None) -> str:
        if library is None:
            return path
        prefix = USER_LIBRARY_PATH if library == "user" else f"/groups/{library}"
        return f"{prefix}{path}"

    def get(
        self, path: str, params: dict | None = None, library: str | None = "user"
    ) -> httpx.Response:
        """GET a path and return the raw response.

        Args:
            path: A library-relative path (e.g. "/items"), or, when
                `library` is None, a path relative to the API root (e.g.
                "/itemTypes") for endpoints that aren't library-scoped.
            library: "user" for the personal library (default), a group ID
                for a group library, or None for non-library-scoped
                endpoints.
        """
        url = self._resolve(path, library)
        try:
            response = self._http.get(url, params=params)
        except httpx.ConnectError as exc:
            raise ValueError(NOT_RUNNING_MESSAGE) from exc

        if response.status_code >= 400 and response.status_code != 302:
            raise ValueError(
                f"Zotero returned {response.status_code} for {path}: {response.text}"
            )
        return response

    def get_json(
        self, path: str, params: dict | None = None, library: str | None = "user"
    ):
        return self.get(path, params, library).json()


client = ZoteroClient()
