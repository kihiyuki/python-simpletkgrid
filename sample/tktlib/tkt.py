# https://github.com/kihiyuki/tkinter-template
# Copyright (c) 2023 kihiyuki
# Released under the MIT license
# Supported Python versions: 3.8
# Requires: (using only Python Standard Library)
from typing import Optional, Union, Dict, Any, List, Tuple
from pathlib import Path
from tkinter import (
    Tk,
    ttk,
    Toplevel,
    Variable,
    StringVar,
    Entry,
    filedialog,
    messagebox,
    W,
    END,
)


FONTSIZE = 12
SCALE = 1.5
class LabelKw(dict):
    def __init__(self, fontsize: int = FONTSIZE):
        return super().__init__(
            font = ("", fontsize),
        )

    def specify_scale(self, scale: float) -> dict:
        _d = self.copy()
        _d["font"] = ("", int(_d["font"][1] * scale))
        return _d

    @property
    def big(self) -> dict:
        return self.specify_scale(SCALE)

    @property
    def small(self) -> dict:
        return self.specify_scale(1 / SCALE)


class GridKw(object):
    def __init__(self, maxcolumn: Optional[int] = None, sticky: str = W) -> None:
        self.row: int = 0
        self.column: int = 0
        self.columnspan: int = 1
        self.maxcolumn: Optional[int] = maxcolumn
        self.sticky: str = sticky
        return None

    def lf(self, n: int = 1) -> None:
        """Line feed"""
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


class _DictLikeObjects(object):
    def __init__(
        self,
        datatype,
        keys: Union[list, tuple, set, None] = None,
        defaultvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._datatype = datatype
        self._data: Dict[Any, self._datatype] = {}
        self.defaultvalue: Optional[str] = defaultvalue
        if keys is not None:
            for k in keys:
                self.add(k, **kwargs)
        return None

    def add(self, key: Any, defaultvalue: Optional[str] = None, **kwargs) -> None:
        if key in self._data.keys():
            raise KeyError(f"Key '{key}' already exists")
        self._data[key] = self._datatype(**kwargs)
        if defaultvalue is None:
            defaultvalue = self.defaultvalue
        if defaultvalue is None:
            self._data[key].set(key)
        else:
            self._data[key].set(defaultvalue)
        return None

    def get_instance(self, key: Any):
        return self._data[key]

    def get(self, key: Any) -> str:
        return self._data[key].get()

    def set(self, key: Any, value: str) -> None:
        return self._data[key].set(value)

    def __getitem__(self, key: Any):
        return self.get(key=key)

    def __setitem__(self, key: Any, value: str):
        return self.set(key=key, value=value)

    def items(self):
        return self._data.items()

class StringVars(_DictLikeObjects):
    def __init__(
        self,
        keys: Union[list, tuple, set, None] = None,
        defaultvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._data: Dict[Any, StringVar]
        return super().__init__(StringVar, keys=keys, defaultvalue=defaultvalue, **kwargs)


class SettableEntry(Entry):
    def set(self, value: str) -> None:
        self.delete(0, END)
        self.insert(END, value)
        return None


class BaseEntries(_DictLikeObjects):
    def __init__(
        self,
        keys: Union[list, tuple, set, None] = None,
        defaultvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._data: Dict[Any, SettableEntry]
        return super().__init__(SettableEntry, keys=keys, defaultvalue=defaultvalue, **kwargs)


class BaseGridObject(object):
    def __init__(self, frame: ttk.Frame) -> None:
        self._data: Dict[str, ttk.Widget] = dict()
        self.frame: ttk.Frame = frame
        self._nameid: int = 0
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
        if type(name) is not str:
            name = "GRIDOBJECT_"
        if name in self._data:
            # raise ValueError(f"Name '{name}' is always used")
            name += str(self._nameid)
        self._data[name] = __object
        self._nameid += 1
        return self._data[name].grid(**gridkw.pull(fullspan=fullspan))


class BaseLabels(BaseGridObject):
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
        return super().add(_obj, gridkw=gridkw, text=text, name=name, fullspan=fullspan)


class BaseButtons(BaseGridObject):
    def add(
        self,
        text: str,
        command,
        gridkw: GridKw,
        name: Optional[str] = None,
        fullspan: bool = False,
    ) -> None:
        _obj = ttk.Button(self.frame, text=text, command=command)
        return super().add(_obj, gridkw=gridkw, text=text, name=name, fullspan=fullspan)


class BaseRadioButtons(BaseGridObject):
    def add(
            self,
            text: str,
            value: Any,
            variable: Variable,
            gridkw: GridKw,
            name: Optional[str] = None,
            fullspan: bool = False,
        ) -> None:
        _obj = ttk.Radiobutton(self.frame, text=text, variable=variable, value=value)
        return super().add(_obj, gridkw=gridkw, text=text, name=name, fullspan=fullspan)


class Labels(BaseLabels):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw, labelkw: LabelKw) -> None:
        self._gridkw = gridkw
        self._labelkw = labelkw
        return super().__init__(frame)
    def add(self, text: Any, scale: Union[str, float] = 1.0, labelkw: Optional[LabelKw] = None, name: Optional[str] = None, fullspan: bool = False) -> None:
        if labelkw is None:
            labelkw = self._labelkw
        if type(scale) is str:
            if scale == "big":
                labelkw = labelkw.big
            elif scale == "small":
                labelkw = labelkw.small
        else:
            labelkw = labelkw.specify_scale(scale)
        return super().add(text, labelkw, self._gridkw, name, fullspan)


class Buttons(BaseButtons):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw) -> None:
        self._gridkw = gridkw
        return super().__init__(frame)
    def add(self, text: str, command, name: Optional[str] = None, fullspan: bool = False) -> None:
        return super().add(text, command, self._gridkw, name, fullspan)


class RadioButtons(BaseRadioButtons):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw) -> None:
        self._gridkw = gridkw
        return super().__init__(frame)
    def add(self, text: str, value: Any, variable: Variable, name: str = None, fullspan: bool = False) -> None:
        return super().add(text, value, variable, self._gridkw, name, fullspan)


class Entries(BaseEntries):
    def __init__(
        self,
        frame: ttk.Frame,
        gridkw: GridKw,
        keys: Union[list, tuple, set, None] = None,
        defaultvalue: Optional[str] = None,
        **kwargs,
    ) -> None:
        self._data: Dict[Any, SettableEntry]
        self._frame = frame
        self._gridkw = gridkw
        self.defaultwidth: int = 80
        return super().__init__(keys, defaultvalue, **kwargs)
    def add(self, key: Any, value: str, defaultvalue: Optional[str] = None, width: Optional[int] = None, **kwargs) -> None:
        if width is None:
            width = self.defaultwidth
        _ret =  super().add(key, defaultvalue, width=width, master=self._frame, **kwargs)
        self.set(key, value)
        self.get_instance(key).grid(**self._gridkw.pull())
        return _ret


def _init_gridobjects(
    frame: ttk.Frame,
    gridkw: GridKw,
    labelkw: LabelKw,
    label: bool,
    button: bool,
    radiobutton: bool,
    entry: bool,
) -> tuple:
    if label:
        labels = Labels(frame, gridkw, labelkw)
    else:
        labels = None
    if button:
        buttons = Buttons(frame, gridkw)
    else:
        buttons = None
    if radiobutton:
        radiobuttons = RadioButtons(frame, gridkw)
    else:
        radiobuttons = None
    if entry:
        entries = Entries(frame, gridkw, defaultvalue="")
    else:
        entries = None
    return (labels, buttons, radiobuttons, entries)


class RootWindow(Tk):
    def __init__(
        self,
        title: str = "",
        resizable: Union[bool, Tuple[bool]] = (False, False),
        maxcolumn: int = 4,
        padding: int = 20,
        label: bool = True,
        button: bool = True,
        radiobutton: bool = True,
        entry: bool = True,
        **kwargs,
    ) -> None:
        _ret = super().__init__(**kwargs)

        self.title(title)
        if type(resizable) is bool:
            resizable = (resizable, resizable)
        self.resizable(*resizable)
        self.frame = ttk.Frame(self, padding=padding)
        self.frame.grid()
        self.gridkw = GridKw(maxcolumn=maxcolumn)
        self.labelkw = LabelKw()
        self.stringvars = StringVars([], defaultvalue="")

        self.labels: Labels
        self.buttons: Buttons
        self.radiobuttons: RadioButtons
        self.entries: Entries
        self.labels, self.buttons, self.radiobuttons, self.entries = _init_gridobjects(
            frame=self.frame,
            gridkw=self.gridkw,
            labelkw=self.labelkw,
            label=label,
            button=button,
            radiobutton=radiobutton,
            entry=entry,
        )
        return _ret

    def lf(self) -> None:
        return self.gridkw.lf()

    def close(self, event=None) -> None:
        self.destroy()
        return None


class SubWindow(Toplevel):
    def __init__(
        self,
        title: str = "",
        resizable: Union[bool, Tuple[bool]] = (False, False),
        padding: int = 20,
        maxcolumn: int = 1,
        sticky: str = W,
        fontsize: int = FONTSIZE,
        label: bool = True,
        button: bool = True,
        radiobutton: bool = True,
        entry: bool = True,
        **kwargs,
    ) -> None:
        _ret = super().__init__(**kwargs)

        self.title(title)
        if type(resizable) is bool:
            resizable = (resizable, resizable)
        self.resizable(*resizable)
        self.grab_set()
        self.focus_set()
        self.frame = ttk.Frame(self, padding=padding)
        self.frame.grid()
        self.gridkw = GridKw(maxcolumn=maxcolumn, sticky=sticky)
        self.labelkw = LabelKw(fontsize=fontsize)

        self.labels: Labels
        self.buttons: Buttons
        self.radiobuttons: RadioButtons
        self.entries: Entries
        self.labels, self.buttons, self.radiobuttons, self.entries = _init_gridobjects(
            frame=self.frame,
            gridkw=self.gridkw,
            labelkw=self.labelkw,
            label=label,
            button=button,
            radiobutton=radiobutton,
            entry=entry,
        )
        return _ret

    def close(self, event=None) -> None:
        self.grab_release()
        self.destroy()
        return None


class dialog(object):
    @staticmethod
    def askopenpath(
        initialpath: Union[str, Path],
        mode: str = "f",
        returntype: str = "str",
    ) -> Union[str, Path, None]:
        """tkinter.filedialog.askopenfilename() / askdirectory()

        Args:
            mode: 'f'=file, 'd'=dir
            returntype: 'str', 'Path'
        """
        initialpath = Path(initialpath).resolve()
        if initialpath.is_dir():
            dirpath = str(initialpath)
            filename = None
        elif initialpath.parent.is_dir():
            dirpath = str(initialpath.parent)
            filename = str(initialpath.name)
        else:
            dirpath = None
            filename = None

        mode = mode.lower()
        if mode in {"f", "file"}:
            selectedpath = filedialog.askopenfilename(
                title="Choose a file",
                initialfile=filename,
                initialdir=dirpath,
            )
        elif mode in {"d", "dir", "directory"}:
            selectedpath = filedialog.askdirectory(
                title="Choose a directory",
                initialdir=dirpath,
            )
        else:
            raise ValueError(f"Invalid mode: '{mode}'")
        if len(selectedpath) > 0:
            if returntype == "str":
                return selectedpath
            elif returntype == "Path":
                return Path(selectedpath)
            else:
                raise ValueError(f"Invalid returntype: '{returntype}'")
        else:
            return None

    @staticmethod
    def asksave(
        data: Union[str, bytes],
        title: str = "Save file",
        mode: str = "t",
        filetypes: Optional[List[Tuple[str]]] = None,
        initialdir: Union[Path, str, None] = None,
        initialfile: Union[Path, str, None] = None,
        **kwargs,
    ) -> bool:
        """tkinter.filedialog.asksaveasfilename()

        Args:
            mode: 't'=text, 'b'=binary
            filetypes: example=[('CSV file', '.csv')]

        Retruns:
            bool: True=saved
        """
        _filepath = filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            initialfile=initialfile,
            **kwargs,
        )
        if len(_filepath) == 0:
            # cancel
            return False
        try:
            mode = "w" + mode
            with Path(_filepath).open(mode=mode) as f:
                f.write(data)
        except Exception as e:
            messagebox.showerror("File save error", str(e))
            return False
        messagebox.showinfo("File save", "Successfully saved.")
        return True
