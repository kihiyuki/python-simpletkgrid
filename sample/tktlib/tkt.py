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
    CENTER,
    END,
)


FONTSIZE = 12
FONTSCALE = 1.5
class LabelKw(dict):
    def __init__(self, fontsize: int = FONTSIZE):
        return super().__init__(
            font = ("", fontsize),
            # anchor = CENTER,
        )

    def get_customized(
        self,
        font: Optional[str] = None,
        fontscale: Union[float, str, None] = None,
    ) -> dict:
        _d = self.copy()

        # font
        if font is not None:
            _d["font"] = (font, _d["font"][1])

        # fontscale
        if fontscale is not None:
            def _scalefont(x: tuple, fontscale: float) -> tuple:
                return (x[0], int(x[1] * fontscale))
            if type(fontscale) is str:
                if fontscale == "big":
                    _d["font"] = _scalefont(_d["font"], FONTSCALE)
                elif fontscale == "small":
                    _d["font"] = _scalefont(_d["font"], 1 / FONTSCALE)
            else:
                _d["font"] = _scalefont(_d["font"], fontscale)
        return _d

    @property
    def big(self) -> dict:
        return self.get_customized(fontscale="big")

    @property
    def small(self) -> dict:
        return self.get_customized(fontscale="small")


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

    def next(self, n: int = 1) -> None:
        self.column += n
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

    def pull(self, columnspan: Optional[int] = None, fullspan: bool = False) -> Dict[str, Any]:
        if fullspan:
            columnspan = self.maxcolumn
        elif columnspan is None:
            columnspan = self.columnspan
        _ret = dict(
            row = self.row,
            column = self.column,
            columnspan = columnspan,
            sticky = self.sticky,
        )
        if fullspan:
            self.lf()
        else:
            self.next(columnspan)
        return _ret


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

    def get(self, key: Any) -> str:
        return self._data[key].get()

    def set(self, key: Any, value: str) -> None:
        return self._data[key].set(value)

    def __getitem__(self, key: Any):
        return self._data[key]

    def __setitem__(self, key: Any, value: str):
        return self._data.__setitem__(key, value)

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
    def __init__(self, frame: ttk.Frame, defaultwidth: Optional[int] = None) -> None:
        self._data: Dict[str, ttk.Widget] = dict()
        self._nameid: int = 0
        self.frame = frame
        self.defaultwidth = defaultwidth
        return None

    def _update_kwargs(
        self,
        kwargs: dict,
        gridkw: Optional[GridKw],
        columnspan: Optional[int],
    ) -> dict:
        # width
        if "width" in kwargs:
            pass
        elif self.defaultwidth is not None:
            if columnspan is not None:
                pass
            elif gridkw is not None:
                columnspan = gridkw.columnspan
            else:
                columnspan = 1
            kwargs["width"] = self.defaultwidth * columnspan
            if columnspan > 1:
                kwargs["width"] += int((columnspan - 1) * 1.9)  # XXX: hardcode
        return kwargs

    def add(
        self,
        __object,
        gridkw: GridKw,
        text: Optional[str] = None,
        name: Optional[str] = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
    ) -> None:
        if name is None:
            name = text
        if type(name) is not str:
            name = "GRIDOBJECT"
        if name in self._data:
            _unique = False
            for _ in range(1000):
                _name = f"{name}_{self._nameid}"
                if _name not in self._data:
                    _unique = True
                    name = _name
                    break
                self._nameid += 1
            if not _unique:
                raise ValueError(f"Name '{name}' is always used")
        self._data[name] = __object
        self._nameid += 1
        return self._data[name].grid(**gridkw.pull(columnspan=columnspan, fullspan=fullspan))


class BaseLabels(BaseGridObject):
    def add(
        self,
        text: Any,
        labelkw: LabelKw,
        gridkw: GridKw,
        name: Optional[str] = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
        **kwargs,  # Label
    ) -> None:
        _kwargs = kwargs.copy()
        _kwargs.update(labelkw)
        kwargs = self._update_kwargs(kwargs, gridkw=gridkw, columnspan=columnspan)
        if type(text) is str:
            _obj = ttk.Label(self.frame, text=text, **_kwargs)
        else:
            _obj = ttk.Label(self.frame, textvariable=text, **_kwargs)
        return super().add(_obj, gridkw=gridkw, text=text, name=name, columnspan=columnspan, fullspan=fullspan)


class BaseButtons(BaseGridObject):
    def add(
        self,
        text: str,
        command,
        gridkw: GridKw,
        name: Optional[str] = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
        **kwargs,  # Button
    ) -> None:
        kwargs = self._update_kwargs(kwargs, gridkw=gridkw, columnspan=columnspan)
        _obj = ttk.Button(self.frame, text=text, command=command, **kwargs)
        return super().add(_obj, gridkw=gridkw, text=text, name=name, columnspan=columnspan, fullspan=fullspan)


class BaseRadioButtons(BaseGridObject):
    def add(
            self,
            text: str,
            value: Any,
            variable: Variable,
            gridkw: GridKw,
            name: Optional[str] = None,
            columnspan: Optional[int] = None,
            fullspan: bool = False,
            **kwargs,  # RadioButton
        ) -> None:
        kwargs = self._update_kwargs(kwargs, gridkw=gridkw, columnspan=columnspan)
        _obj = ttk.Radiobutton(self.frame, text=text, variable=variable, value=value, **kwargs)
        return super().add(_obj, gridkw=gridkw, text=text, name=name, columnspan=columnspan, fullspan=fullspan)


class Labels(BaseLabels):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw, labelkw: LabelKw) -> None:
        self._gridkw = gridkw
        self._labelkw = labelkw
        return super().__init__(frame)
    def add(
        self,
        text: Any,
        labelkw: Optional[LabelKw] = None,
        name: Optional[str] = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
        font: Optional[str] = None,  # get_customized
        fontscale: Union[float, str, None] = None,  # get_customized
        **kwargs,  # Label
    ) -> None:
        if labelkw is None:
            labelkw = self._labelkw
        return super().add(text, labelkw.get_customized(font=font, fontscale=fontscale), self._gridkw, name, columnspan, fullspan, **kwargs)


class Buttons(BaseButtons):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw) -> None:
        self._gridkw = gridkw
        return super().__init__(frame)
    def add(
        self,
        text: str,
        command,
        name: Optional[str] = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
        **kwargs,  # Button
    ) -> None:
        return super().add(text, command, self._gridkw, name, columnspan, fullspan, **kwargs)


class RadioButtons(BaseRadioButtons):
    def __init__(self, frame: ttk.Frame, gridkw: GridKw) -> None:
        self._gridkw = gridkw
        return super().__init__(frame)
    def add(
        self,
        text: str,
        value: Any,
        variable: Variable,
        name: str = None,
        columnspan: Optional[int] = None,
        fullspan: bool = False,
        **kwargs,  # RadioButton
    ) -> None:
        return super().add(text, value, variable, self._gridkw, name, columnspan, fullspan, **kwargs)


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
    def add(
        self,
        key: Any,  # set
        value: str,  # set
        defaultvalue: Optional[str] = None,  # BaseEntries
        width: Optional[int] = None,  # BaseEntries
        **kwargs,  # Entry
    ) -> None:
        if width is None:
            width = self.defaultwidth
        _ret =  super().add(key, defaultvalue, width=width, master=self._frame, **kwargs)
        self.set(key, value)
        self._data[key].grid(**self._gridkw.pull(fullspan=True))
        return _ret


def _init_gridobjects(
    frame: ttk.Frame,
    gridkw: GridKw,
    labelkw: LabelKw,
    defaultwidth: Optional[int],
    label: bool,
    button: bool,
    radiobutton: bool,
    entry: bool,
) -> tuple:
    if label:
        labels = Labels(frame, gridkw, labelkw)
        labels.defaultwidth = defaultwidth
    else:
        labels = None
    if button:
        buttons = Buttons(frame, gridkw)
        buttons.defaultwidth = defaultwidth
    else:
        buttons = None
    if radiobutton:
        radiobuttons = RadioButtons(frame, gridkw)
        radiobuttons.defaultwidth = defaultwidth
    else:
        radiobuttons = None
    if entry:
        entries = Entries(frame, gridkw, defaultvalue="")
        entries.defaultwidth = defaultwidth
    else:
        entries = None
    return (labels, buttons, radiobuttons, entries)


class RootWindow(Tk):
    def __init__(
        self,
        title: str = "",
        resizable: Union[bool, Tuple[bool]] = (False, False),
        padding: int = 20,
        maxcolumn: int = 4,
        sticky: str = W,
        fontsize: int = FONTSIZE,
        defaultwidth: Optional[int] = None,
        label: bool = True,
        button: bool = True,
        radiobutton: bool = True,
        entry: bool = True,
        **kwargs,  # Tk
    ) -> None:
        _ret = super().__init__(**kwargs)

        self.title(title)
        if type(resizable) is bool:
            resizable = (resizable, resizable)
        self.resizable(*resizable)
        self.frame = ttk.Frame(self, padding=padding)
        self.frame.grid()
        self.gridkw = GridKw(maxcolumn=maxcolumn, sticky=sticky)
        self.labelkw = LabelKw(fontsize=fontsize)
        self.stringvars = StringVars([], defaultvalue="")

        self.labels: Labels
        self.buttons: Buttons
        self.radiobuttons: RadioButtons
        self.entries: Entries
        self.labels, self.buttons, self.radiobuttons, self.entries = _init_gridobjects(
            frame=self.frame,
            gridkw=self.gridkw,
            labelkw=self.labelkw,
            defaultwidth=defaultwidth,
            label=label,
            button=button,
            radiobutton=radiobutton,
            entry=entry,
        )
        return _ret

    def lf(self, n: int = 1) -> None:
        self.gridkw.lf(1)
        for _ in range(n - 1):
            self.labels.add("", fullspan=True)
        return None

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
        defaultwidth: Optional[int] = None,
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
        self.stringvars = StringVars([], defaultvalue="")

        self.labels: Labels
        self.buttons: Buttons
        self.radiobuttons: RadioButtons
        self.entries: Entries
        self.labels, self.buttons, self.radiobuttons, self.entries = _init_gridobjects(
            frame=self.frame,
            gridkw=self.gridkw,
            labelkw=self.labelkw,
            defaultwidth=defaultwidth,
            label=label,
            button=button,
            radiobutton=radiobutton,
            entry=entry,
        )
        return _ret

    def lf(self, n: int = 1) -> None:
        self.gridkw.lf(1)
        for _ in range(n - 1):
            self.labels.add("", fullspan=True)
        return None

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
