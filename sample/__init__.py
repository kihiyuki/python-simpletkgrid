from argparse import ArgumentParser
from typing import Optional, List
from pathlib import Path

from .gui import main as gui_main
from .configlib import Config, DEFAULTSECT
from .define import (
    __version__,
    APPNAME,
    APPNAME_FULL,
    DEFAULT_WORKDIR,
    DEFAULT_CONFIG,
    messages,
)


__all__ = (
    "__version__",
    "main",
)


def main(args: Optional[List[str]] = None) -> None:
    parser = ArgumentParser()

    parser_mode = parser.add_mutually_exclusive_group()
    parser_mode.add_argument(
        "--background",
        action="store_true",
        help=messages.option.background)

    parser.add_argument(
        "--workdir", "-w",
        required=False, default=".",
        help=messages.option.workdir)
    parser.add_argument(
        "--configfile",
        required=False, default=f"{APPNAME}.ini",
        help=messages.option.configfile)
    parser.add_argument(
        "--config-section",
        required=False, default=DEFAULTSECT,
        help=messages.option.configsection)
    parser.add_argument(
        "--version", "-V",
        action='version',
        version=APPNAME_FULL)

    args = parser.parse_args(args)

    if args.workdir is None:
        workdirpath = Path(DEFAULT_WORKDIR)
    else:
        workdirpath = Path(args.workdir)
    configfilepath = Path(args.configfile)
    if not configfilepath.is_absolute():
        configfilepath = workdirpath / args.configfile
    config_section: str = args.config_section
    background_mode: bool = args.background

    # Load configuration file
    kwargs_config = dict(
        section=config_section,
        notfound_ok=True,
        default=DEFAULT_CONFIG,
        cast=False,
        strict_cast=False,
        strict_key=True,
    )
    if configfilepath.is_file():
        config = Config(configfilepath, **kwargs_config)
    else:
        config = Config(DEFAULT_CONFIG, **kwargs_config)
        config.save(configfilepath)

    if args.workdir is not None:
        config["workdir"] = args.workdir

    # config.conv()

    if background_mode:
        pass
    else:
        return gui_main(config=config, args=args)

    return None
