from zotero_mcp import __main__


def test_main_runs_stdio_transport(monkeypatch):
    calls = []
    monkeypatch.setattr(
        __main__.mcp, "run", lambda transport=None, **kwargs: calls.append(transport)
    )
    __main__.main()
    assert calls == ["stdio"]
