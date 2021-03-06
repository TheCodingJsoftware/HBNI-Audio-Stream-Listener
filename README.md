# HBNI Audio Stream Listener (Desktop version)
<p align="center">
  <img height="200" src="https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/blob/main/icons/hbni_logo_dark.png" />
</p>

[![image](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)](https://play.google.com/store/apps/details?id=com.thecodingjsoftware.hutteritechurch)
[![image](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/releases)
[![image](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/releases)
[![image](https://img.shields.io/badge/Google_Play-414141?style=for-the-badge&logo=google-play&logoColor=white)](https://play.google.com/store/apps/details?id=com.thecodingjsoftware.hutteritechurch)

## Preview:
<p align="center">
  <img height="400" src="https://user-images.githubusercontent.com/25397800/150418509-4d36d37f-a528-48c7-9e0a-a13946ef6b87.png" />
  <img height="400" src="https://user-images.githubusercontent.com/25397800/150418964-d82e17b7-780a-4d66-bbe3-c4507a9c0b93.png" />
</p>

## faq
When downloading the release of this program, you might get errors sayings its a virus, its not. View the source if you wish. Microsoft doesn't recognize that its a valid piece of software as it has no valid licenses.

What's the command prompt for? Can't help it, until I find a better way to listen to streams lives. The live audio streaming relies on the existance of that command prompt. There are workaround that do work, that are explained at the bottom.

Why does the program restart when stopping a stream? A continuation from the above comment. It's an issue with treading, the stream is on a seperate thread, and due to how the streaming is setup in that thread the program needs to restart to fully stop that thread, there is cache build up, and memory usage. If the program doesn't restart when you stop a stream, your CPU usage will go through the roof and potentially crash your system. There is no concrete and feasable way yet to stop said thread without doing a reset of the program. This is an issue with [miniaudio](https://github.com/mackron/miniaudio).

## Development setup

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

## Disable command prompt

This is for more technical users to follow and setup. 
1. Rename the `HBNI Audio Stream Listener.exe` -> `main.exe`
2. Download this file: [HBNI Audio Stream Listener.exe](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/blob/a45f1d266b34e2efb68ae9461083466a3e2faa62/HBNI%20Audio%20Stream%20Listener.exe) and place it into the same directory as `main.exe` 
3. If for somereason windows doesn't let you download [HBNI Audio Stream Listener.exe](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/blob/a45f1d266b34e2efb68ae9461083466a3e2faa62/HBNI%20Audio%20Stream%20Listener.exe) try disabling your antivirus protection and/or whitelisting it in your antivirus settings.
4. If all that worked then running the [HBNI Audio Stream Listener.exe](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/blob/a45f1d266b34e2efb68ae9461083466a3e2faa62/HBNI%20Audio%20Stream%20Listener.exe) file should disable the command prompt, and work as intended. If it doesn't, email me or open up an [issue](https://github.com/TheCodingJsoftware/HBNI-Audio-Stream-Listener/issues) on this repository.
