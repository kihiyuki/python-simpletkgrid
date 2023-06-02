import subprocess
import webbrowser
from datetime import datetime
from tkinter import (
    messagebox,
)

from .tktlib import (
    Config,
    RootWindow,
    SubWindow,
    dialog,
)
from .define import (
    APPNAME_FULL,
    URL,
    messages,
)


def main(config: Config, args) -> None:
    class AboutWindow(SubWindow):
        def __init__(self) -> None:
            _ret = super().__init__(title="About")
            self.labels.add(APPNAME_FULL, fontscale="big")
            self.labels.add(f"Website: {URL}")
            self.buttons.add("Open Website", self.open_url)
            self.buttons.add("Close[ESC]", self.close)
            self.bind("<Escape>", self.close)
            return _ret

        def open_url(event=None) -> None:
            _ = webbrowser.open_new(URL)
            return None

    class ConfigWindow(SubWindow):
        def __init__(self, entry_width: int = 80) -> None:
            _ret = super().__init__(title="Config", fontsize=10)
            self.entries.defaultwidth = entry_width

            def _filediag(
                k: str,
                mode: str = "f",
            ) -> None:
                _path = dialog.askopenpath(self.entries.get(k), mode=mode)
                if _path is not None:
                    self.entries.set(k, _path)
                return None

            for k, v in config.to_dict().items():
                self.labels.add(f"{k}({type(v).__name__}): {messages.config.__getattribute__(k)}")
                self.entries.add(k, str(v))
                # if type(config.default[k]).__name__ in ["Path"]:
                #     self.buttons.add("Browse", lambda: _diag(k, "file"))
                if k == "workdir":
                    self.buttons.add("Browse", lambda: _filediag("workdir", "dir"))

            self.buttons.add("Save[Enter]", self.save)
            self.buttons.add("Cancel[ESC]", self.close)
            self.bind("<Return>", self.save)
            self.bind("<Escape>", self.close)

            return _ret

        def save(self, event=None) -> None:
            _changed = False
            for k, entry in self.entries.items():
                v = entry.get()
                if str(v) != str(config[k]):
                    _changed = True
                    config[k] = v

            if not _changed:
                messagebox.showinfo("Config", "Nothing changed.")
                self.close()
            elif messagebox.askyesno("Save config", f"Save to configfile and reload datafile?"):
                config.save(section=args.config_section, mode="overwrite")
                config.cast()
                messagebox.showinfo("Config", "Saved.")
                self.close()
            return None

    class TestWindow01(SubWindow):
        def __init__(self) -> None:
            _ret = super().__init__(title="Config", fontsize=10, button=True, radiobutton=True)
            self.stringvars.add("key1", defaultvalue="")
            self.radiobuttons.add("A A A", "A123", self.stringvars["key1"])
            self.radiobuttons.add("BBBBB", "B123", self.stringvars["key1"])
            self.radiobuttons.add("CCC C", "C123", self.stringvars["key1"])

            self.buttons.add("Update[Enter]", self.update)
            self.buttons.add("Cancel[ESC]", self.close)
            self.bind("<Return>", self.update)
            self.bind("<Escape>", self.close)
            return _ret

        def update(self, event=None) -> None:
            val = self.stringvars.get("key1")
            if len(val) > 0:
                root.stringvars.set("test01", val)
                self.close()
            else:
                messagebox.showwarning("Warning", f"Please select.")
            return None

    def _do_nothing(event=None) -> None:
        return None

    def _open(event=None) -> None:
        subprocess.Popen(["explorer",  config["workdir"]], shell=True)
        return None

    def _export(event=None) -> None:
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = "hoge_" + now
        extention = ".txt"
        dialog.asksave(
            "hogefuga:" + now,
            filetypes=[("Text file", extention)],
            initialdir=config["workdir"],
            initialfile=filename+extention,
        )
        return None

    def _about(event=None):
        AboutWindow()
        return None

    def _config(event=None):
        ConfigWindow()
        return None

    def _test01(event=None):
        TestWindow01()
        return None

    root = RootWindow(
        title=APPNAME_FULL,
        resizable=False,
        maxcolumn=4,
        padding=20,
    )
    root.buttons.add("[O]pen workdir", _open)
    root.lf()

    root.buttons.add("Export to file", _export)
    root.lf()

    root.stringvars.add("test01")
    root.buttons.add("Test01", _test01)
    root.labels.add(root.stringvars["test01"])
    root.lf()

    root.labels.add("Label(fontscale=2.0)", fontscale=2.0, fullspan=True)
    root.labels.add("Label(fontscale='big')", fontscale="big", fullspan=True)
    root.labels.add("Label(normal)", fullspan=True)
    root.labels.add("Label(fontscale='small')", fontscale="small", fullspan=True)

    root.buttons.add("dummyBtn1", _do_nothing, columnspan=3, width=30)
    root.buttons.add("dummyBtn2", _do_nothing)
    root.buttons.add("dummyBtn3", _do_nothing)
    root.buttons.add("dummyBtn3", _do_nothing)
    root.buttons.add("dummyBtn3", _do_nothing)
    root.lf()

    root.buttons.add("About[F1]", _about)
    root.buttons.add("[C]onfig", _config)
    root.buttons.add("Reload[F5]", _do_nothing)
    root.buttons.add("Quit[Esc]", root.close)
    root.lf()

    # keybind
    root.bind("o", _open)
    root.bind("c", _config)
    root.bind("<F1>", _about)
    root.bind("<F5>", _do_nothing)
    root.bind("<Escape>", root.close)

    root.mainloop()
