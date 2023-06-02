# https://github.com/kihiyuki/tkinter-template
# Copyright (c) 2023 kihiyuki
# Released under the MIT license
# Supported Python versions: 3.8
# Requires: (using only Python Standard Library)
from .config import Config
from .tkt import (
    RootWindow,
    SubWindow,
    dialog,
)

__all__ = [
    "Config",
    "RootWindow",
    "SubWindow",
    "dialog",
]
__version__ = "0.1.2"
