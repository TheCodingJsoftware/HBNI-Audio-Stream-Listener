# HBNI Audio Stream Listener (Desktop version)

A Desktop version of the [mobile app](https://play.google.com/store/apps/details?id=com.thecodingjsoftware.hutteritechurch)

When downloading the release of this program, you might get errors sayings its a virus, its not. View the source if you wish. Microsoft doesn't recognize that its a valid piece of software as it has no valid licenses.

Development setup is as follows

first install virtual env with: `pip install virtualenv`

create virtual env with:

`virtualenv venv`

then activate venv
(in vscode you can simply close and reopen your terminal)
If you get an execution policy error, open powershell and run the following command:

`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted`

then install all the required libraries:

`pip install win10toast pyqt5 miniaudio pyinstaller pyqtdarktheme`

To build the project:

`pyinstaller -F --icon=icons/icon.ico --hidden-import=_cffi_backend main.py`
