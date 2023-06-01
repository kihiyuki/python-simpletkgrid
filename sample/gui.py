import subprocess
import webbrowser
from typing import Dict
from datetime import datetime
from pathlib import Path
from tkinter import (
    filedialog,
    messagebox,
    Entry,
    StringVar,
    END,
)

from .tktlib import (
    Config,
    RootWindow,
    SubWindow,
    Entries,
    dialog,
)
from .define import (
    __version__,
    APPNAME_FULL,
    URL,
    messages,
)


def main(config: Config, args) -> None:
    class AboutWindow(SubWindow):
        def __init__(self) -> None:
            ret = super().__init__(title="About", button=True, label=True)

            self.labels.add(APPNAME_FULL, self.labelkw.big, self.gridkw)
            self.labels.add(f"Website: {URL}", self.labelkw, self.gridkw)

            self.buttons.add("Open Website", self.open_url, self.gridkw)
            self.buttons.add("Close", self.close, self.gridkw)

            return ret

        def open_url(event=None) -> None:
            _ = webbrowser.open_new(URL)
            return None

    class ConfigWindow(SubWindow):
        def __init__(self, entry_width: int = 80) -> None:
            _ret = super().__init__(title="Config", fontsize=10, button=True, label=True)

            self.entries = Entries()

            def _filediag(
                k: str,
                mode: str = "f",
            ) -> None:
                _path = dialog.askopenpath(self.entries.get(k), mode=mode)
                if _path is not None:
                    self.entries.set(k, _path)
                return None

            for k, v in config.to_dict().items():
                self.labels.add(f"{k}({type(v).__name__}): {messages.config.__getattribute__(k)}", self.labelkw, self.gridkw, name=k)
                self.entries.add(k, master=self.frm, width=entry_width)
                self.entries.set(k, str(v))
                self.entries.get_instance(k).grid(**self.gridkw.pull())
                # if type(config.default[k]).__name__ in ["Path"]:
                #     self.buttons.add("Browse", lambda: _diag(k, "file"), self.gridkw, name=f"{k}_diag_btn")
                if k == "workdir":
                    self.buttons.add("Browse", lambda: _filediag("workdir", "dir"), self.gridkw, name=f"workdir_btn")

            self.buttons.add("Save[Enter]", self.save, self.gridkw, name="save")
            self.buttons.add("Cancel[ESC]", self.close, self.gridkw, name="cancel")
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
                self.close()
                messagebox.showinfo("Config", "Nothing changed.")
            elif messagebox.askyesno("Save config", f"Save to configfile and reload datafile?"):
                config.save(
                    section=args.config_section,
                    mode="overwrite",
                )

                # reload
                config.cast()
                self.close()
                # _reload(config=config)
                messagebox.showinfo("Config", "Saved.")
            return None

    class TestWindow01(SubWindow):
        def __init__(self) -> None:
            _ret = super().__init__(title="Config", fontsize=10, button=True, radiobutton=True)

            # ????
            self.var = StringVar()

            self.radiobuttons.add("A A A", "A123", self.var, self.gridkw)
            self.radiobuttons.add("BBBBB", "B123", self.var, self.gridkw)
            self.radiobuttons.add("CCC C", "C123", self.var, self.gridkw)

            self.buttons.add("Update[Enter]", self.update, self.gridkw, name="update")
            self.buttons.add("Cancel[ESC]", self.close, self.gridkw, name="cancel")
            self.bind("<Return>", self.update)
            self.bind("<Escape>", self.close)
            return _ret

        def update(self, event=None) -> None:
            val = self.var.get()
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

    def _export(event=None):
        export_file = filedialog.asksaveasfilename(
            filetypes = [("CSV file", ".csv")],
            defaultextension = "csv",
            title="Export",
            initialfile = "{}_{}.csv".format(
                "hoge",
                datetime.now().strftime("%Y%m%d%H%M%S"),
            ),
        )
        if len(export_file) == 0:
            return None
        # try:
        #     data.export(filepath=export_file)
        # except Exception as e:
        #     messagebox.showwarning("Export failed", e)
        # else:
        #     messagebox.showinfo("Export", f"Successfully saved.")
        return None

    def _about(event=None):
        aw = AboutWindow()

    def _config(event=None):
        cw = ConfigWindow()

    def _test01(event=None):
        tw01 = TestWindow01()

    root = RootWindow(maxcolumn=4, padding=20)
    root.title(APPNAME_FULL)
    root.resizable(False, False)
    root.buttons.add("[O]pen", _open, root.gridkw, name="open")
    root.gridkw.lf()

    # labels.add("Result", labelkw.big, gridkw, name="title.r", fullspan=True)
    root.buttons.add("Export", _export, root.gridkw, name="export")
    root.gridkw.lf()

    # labels.add("----", labelkw.big, gridkw, name="title.t2", fullspan=True)
    root.stringvars.add("test01")
    root.buttons.add("Test01", _test01, root.gridkw, name="test01")
    root.labels.add(root.stringvars.get_instance("test01"), root.labelkw, root.gridkw, name="test01.v")
    root.gridkw.lf()

    root.labels.add("Big Text", root.labelkw.big, root.gridkw, fullspan=True)
    root.labels.add("Medium Text", root.labelkw, root.gridkw, fullspan=True)
    root.labels.add("Small Text", root.labelkw.small, root.gridkw, fullspan=True)
    root.buttons.add("dummyBtn1", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn2", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn3", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn4", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn5", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn6", _do_nothing, root.gridkw)
    root.buttons.add("dummyBtn7", _do_nothing, root.gridkw)
    root.gridkw.lf()

    root.buttons.add("Config", _config, root.gridkw, name="config")
    # buttons.add("Reload[F5]", _reload, gridkw, name="reload")
    root.buttons.add("Quit[Esc]", root.close, root.gridkw, name="quit")
    root.gridkw.lf()

    # keybind
    root.bind("o", _open)
    root.bind("<F1>", _about)
    root.bind("<F5>", _do_nothing)
    root.bind("<Escape>", root.close)

    root.mainloop()
