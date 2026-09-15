from __future__ import annotations

"""Public entrypoint for the Digital Copy workspace."""

from .digital_copy_ui_impl import DigitalCopyUI, main

__all__ = ["DigitalCopyUI", "main"]

if __name__ == "__main__":
    main()
