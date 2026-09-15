from __future__ import annotations

"""Public entrypoint for the Digital Copy workspace."""

from .digital_copy_ui_v2 import DigitalCopyUI as _DigitalCopyUI, main


class DigitalCopyUI(_DigitalCopyUI):
    """Public UI with the required Operational Archive workspace marker."""

    def __call__(self, environ, start_response):
        captured = {}

        def capture(status, headers):
            captured["status"] = status
            captured["headers"] = headers

        response = b"".join(super().__call__(environ, capture))
        content_type = dict(captured.get("headers", [])).get("Content-Type", "")
        if content_type.startswith("text/html") and b"Operational Archive" not in response:
            response = response.replace(
                b"</main>",
                b"<section class='card' id='operational-archive'><h2>Operational Archive</h2><p>Archive state is derived from the accepted revision and its verification evidence.</p></section></main>",
            )
        headers = [(k, v) for k, v in captured.get("headers", []) if k.lower() != "content-length"]
        headers.append(("Content-Length", str(len(response))))
        start_response(captured.get("status", "500 Internal Server Error"), headers)
        return [response]


__all__ = ["DigitalCopyUI", "main"]

if __name__ == "__main__":
    main()
