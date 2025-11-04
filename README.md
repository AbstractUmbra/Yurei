# Yurei

A save-editor for Phasmophobia, written in Python.

For this to work, you must know and be able to access your save file for Phasmophobia. Their default locations are as follows:-

Windows:
```
%USERPROFILE%\AppData\LocalLow\Kinetic Games\Phasmophobia\SaveFile.txt
```

> [!TIP]
> We have support for loading this default file path on Windows due to it's location being static, Linux does not have this benefit, below is the relative path to the save location

Linux:
```
<SteamLibraryLocation>/steamapps/compatdata/739630/pfx/
```

## Installation

This project will likely never exist on PyPi (or pip for those who call it that), so you'll need to install from GitHub:

```sh
pip install 'git+https://github.com/AbstractUmbra/Yurei'
# or
uv add 'git+https://github.com/AbstractUmbra/Yurei'
# etc
```

Once installed you can then run the app with the `yurei` executable.
If you use the `web` extra, you can use the `yurei-web`, but this is experimental and (as of the commit date) currently does not work on Python 3.14+.


#### To-Do list

- [x] Money
- [x] Levels and Prestige values
- [x] Gear unlock and addition
- [x] Achievement managment
- [x] Easter Egg management
- [ ] Ghost/spirit values, death and encounter


#### Help wanted

If you're good at design/visuals then I'd love for you to help make this prettier. I for one am terrible at making things look nice.
