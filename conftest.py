from __future__ import annotations

import inspect

import httpx


def _patch_httpx_for_starlette_testclient() -> None:
    signature = inspect.signature(httpx.Client.__init__)
    if "app" in signature.parameters:
        return

    original_init = httpx.Client.__init__

    def patched_init(self, *args, app=None, **kwargs):  # noqa: ANN001
        return original_init(self, *args, **kwargs)

    httpx.Client.__init__ = patched_init  # type: ignore[assignment]


_patch_httpx_for_starlette_testclient()
