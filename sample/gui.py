import subprocess
import webbrowser
from typing import Optional, Union, Dict, Any
from datetime import datetime
from pathlib import Path
from tkinter import (
    Tk,
    ttk,
    filedialog,
    messagebox,
    Toplevel,
    Entry,
    Variable,
    StringVar,
    END,
    W,
)

from .configlib import Config
from .define import (
    __version__,
    APPNAME_FULL,
    URL,
    messages,
)


class LabelKw(dict):
    def __init__(self, fontsize: int = 12):
        return super().__init__(
            font = ("", fontsize),
        )

    @property
    def big(self, ratio: float = 1.5):
        _d = self.copy()
        _d["font"] = ("", int(_d["font"][1] * ratio))
        return _d


class GridKw(object):
    def __init__(self, maxcolumn: Optional[int] = None, sticky: str = W) -> None:
        self.row: int = 0
        self.column: int = 0
        self.columnspan: int = 1
        self.maxcolumn: Optional[int] = maxcolumn
        self.sticky: str = sticky
        return None

    def lf(self, n: int = 1) -> None:
        self.row += n
        self.column = 0
        return None

    def next(self) -> None:
        self.column += 1
        if self.maxcolumn is None:
            pass
        elif self.column >= self.maxcolumn:
            self.lf()
        return None

    def set(self, row: Optional[int] = None, column: Optional[int] = None) -> None:
        if row is not None:
            self.row = row
        if column is not None:
            self.column = column
        return None

    def pull(self, fullspan: bool = False) -> dict:
        row = self.row
        column = self.column
        sticky = self.sticky
        columnspan = self.columnspan
        if fullspan:
            columnspan = self.maxcolumn
            self.lf()
        else:
            self.next()
        return dict(
            row = row,
            column = column,
            columnspan = columnspan,
            sticky = sticky,
        )


class StringVars(object):
    def __init__(self, keys: Union[list, tuple, set], defaltvalue: Optional[str] = None) -> None:
        self._data: Dict[Any, StringVar] = dict()
        for k in keys:
            self._data[k] = StringVar()
            if defaltvalue is None:
                self._data[k].set(k)
            else:
                self._data[k].set(defaltvalue)
        return None

    def get(self, key: Any) -> str:
        return self._data[key]

    def set(self, key: Any, value: str) -> None:
        return self._data[key].set(value)

    def __getitem__(self, key: Any):
        return self.get(key=key)

    def __setitem__(self, key: Any, value: str):
        return self.set(key=key, value=value)


class GridObject(object):
    def __init__(self, frame: ttk.Frame) -> None:
        self._data: Dict[str, ttk.Widget] = dict()
        self.frame: ttk.Frame = frame
        return None

    def add(
        self,
        __object,
        gridkw: GridKw,
        text: Optional[str] = None,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        if name is None:
            name = text
        if name in self._data:
            raise ValueError(f"Name '{name}' is always used")
        self._data[name] = __object
        return self._data[name].grid(**gridkw.pull(fullspan=fullspan))


class RadioButtons(GridObject):
    def add(
            self,
            text: str,
            value: Any,
            variable: Variable,
            gridkw: GridKw,
            name: str = None,
            fullspan: bool = False,
        ) -> None:
        _obj = ttk.Radiobutton(self.frame, text=text, variable=variable, value=value)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class Buttons(GridObject):
    def add(
        self,
        text: str,
        command,
        gridkw: GridKw,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        _obj = ttk.Button(self.frame, text=text, command=command)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class Labels(GridObject):
    def add(
        self,
        text: Any,
        labelkw: LabelKw,
        gridkw: GridKw,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        if type(text) is str:
            _obj = ttk.Label(self.frame, text=text, **labelkw)
        else:
            _obj = ttk.Label(self.frame, textvariable=text, **labelkw)
        return super().add(_obj, gridkw, text=text, name=name, fullspan=fullspan)


class SubWindow(Toplevel):
    def __init__(
        self,
        title: str,
        resizable: bool = False,
        padding: int = 20,
        maxcolumn: int = 1,
        sticky: str = W,
        fontsize: int = 12,
        button: bool = False,
        label: bool = False,
        radiobutton: bool = False,
    ) -> None:
        _ret = super().__init__()

        self.title(title)
        self.resizable(resizable, resizable)
        self.grab_set()
        self.focus_set()

        self.frm = ttk.Frame(self, padding=padding)
        self.frm.grid()

        self.gridkw = GridKw(maxcolumn=maxcolumn, sticky=sticky)
        self.labelkw = LabelKw(fontsize=fontsize)

        if button:
            self.buttons = Buttons(self.frm)
        if label:
            self.labels = Labels(self.frm)
        if radiobutton:
            self.radiobuttons = RadioButtons(self.frm)

        return _ret

    def close(self, event=None) -> None:
        self.grab_release()
        self.destroy()
        return None


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

            self.entries: Dict[str, Entry] = dict()

            def _diag(
                k: str,
                type_: str = "file",
            ) -> None:
                _initialfile = Path(self.entries[k].get())
                _initialdir = _initialfile.parent
                if _initialdir.is_dir():
                    _initialdir = str(_initialdir)
                else:
                    _initialdir = None
                if _initialfile.is_file():
                    _initialfile = _initialfile.name
                else:
                    if _initialfile.is_dir():
                        _initialdir = _initialfile
                    _initialfile = None

                if type_ == "file":
                    _path = filedialog.askopenfilename(
                        title="Choose a file",
                        initialfile=_initialfile,
                        initialdir=_initialdir,
                    )
                elif type_ == "dir":
                    _path = filedialog.askdirectory(
                        title="Choose a directory",
                        initialdir=_initialdir,
                    )
                else:
                    raise ValueError(f"invalid type: {type_}")

                # Entry.set
                self.entries[k].delete(0, END)
                self.entries[k].insert(END, _path)
                return None

            for k, v in config.to_dict().items():
                self.labels.add(f"{k}({type(v).__name__}): {messages.config.__getattribute__(k)}", self.labelkw, self.gridkw, name=k)
                self.entries[k] = Entry(self.frm, width=entry_width)
                self.entries[k].insert(END, str(v))
                self.entries[k].grid(**self.gridkw.pull())
                # if type(config.default[k]).__name__ in ["Path"]:
                #     self.buttons.add("Browse", lambda: _diag(k, "file"), self.gridkw, name=f"{k}_diag_btn")
                if k == "workdir":
                    self.buttons.add("Browse", lambda: _diag("workdir", "dir"), self.gridkw, name=f"workdir_btn")

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
                vars.set("test01", val)
                self.close()
            else:
                messagebox.showwarning("Warning", f"Please select.")
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

    def _close(event=None):
        root.destroy()

    def _config(event=None):
        cw = ConfigWindow()

    def _test01(event=None):
        tw01 = TestWindow01()

    root = Tk()
    root.title(APPNAME_FULL)
    root.resizable(False, False)
    frm = ttk.Frame(root, padding=20)
    frm.grid()

    gridkw = GridKw(maxcolumn=4)
    labelkw = LabelKw()

    buttons = Buttons(frm)
    labels = Labels(frm)

    vars = StringVars(["test01"], defaltvalue="")
    # _reload(config=config)

    # labels.add(datasetinfo.get("date"), labelkw, gridkw, name="date", fullspan=True)
    # labels.add("Dataset info", labelkw.big, gridkw, name="title.d", fullspan=True)
    # for k in ["datafile", "workdir"]:
    #     labels.add(datasetinfo.get(k), labelkw, gridkw, name=k, fullspan=True)
    # for k in ["count_all", "count_annotated"]:
    #     labels.add(datasetinfo.get(k), labelkw, gridkw, name=k, fullspan=True)

    # labels.add("Working directory", labelkw.big, gridkw, name="title.w", fullspan=True)
    buttons.add("[O]pen", _open, gridkw, name="open")
    gridkw.lf()

    # labels.add("Result", labelkw.big, gridkw, name="title.r", fullspan=True)
    buttons.add("Export", _export, gridkw, name="export")
    gridkw.lf()

    # labels.add("----", labelkw.big, gridkw, name="title.t2", fullspan=True)
    buttons.add("Test01", _test01, gridkw, name="test01")
    labels.add(vars.get("test01"), labelkw, gridkw, name="test01.v")
    gridkw.lf()

    # labels.add("----", labelkw.big, gridkw, name="title.t", fullspan=True)
    buttons.add("Config", _config, gridkw, name="config")
    # buttons.add("Reload[F5]", _reload, gridkw, name="reload")
    buttons.add("Quit[Esc]", _close, gridkw, name="quit")
    gridkw.lf()

    # keybind
    root.bind("o", _open)
    root.bind("<F1>", _about)
    # root.bind("<F5>", _reload)
    root.bind("<Escape>", _close)

    root.mainloop()
