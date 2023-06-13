from dataclasses import dataclass

__version__ = "0.0.1"

DEFAULT_WORKDIR = "."
# NOTE: values must be int or float or str
DEFAULT_CONFIG = dict(
    workdir = ".",
    n = 30,
)

APPNAME = "sample"
APPNAME_LONG = "Sample-tool"
APPNAME_FULL = f"{APPNAME_LONG} (Ver: {__version__})"
URL = "https://github.com/kihiyuki/tkinter-template"

class messages(object):
    @dataclass(frozen=True)
    class _CommonMessages(object):
        replace: str = "already exists. Do you want to replace(overwrite) it?"
    common = _CommonMessages()

    @dataclass(frozen=True)
    class __OptionMessages(object):
        background: str = "Background mode"
        workdir: str = "Working directory path"
        configfile: str = "Configuration file path"
        configsection: str = "Configuration section name"
    option = __OptionMessages()

    @dataclass(frozen=True)
    class __ConfigMessages(object):
        workdir: str = "Working directory path"
        n: str = "Number of XXX (If null, xxx all.)"
    config = __ConfigMessages()
