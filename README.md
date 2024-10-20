# ElgatoControlCenter System Tray

<br>
<div align="center">

![Language](https://img.shields.io/github/languages/top/zzampax/ecc-systray.svg?style=for-the-badge&labelColor=black&logo=python&logoColor=blue&label=Python)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Github](https://img.shields.io/badge/GitHub-000000?style=for-the-badge&logo=github&logoColor=white)
![WAM](https://img.shields.io/badge/SYSTRAY-FOR%20THE%20WIN-blue?style=for-the-badge&labelColor=black)

<img src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Flogohistory.net%2Fwp-content%2Fuploads%2F2023%2F06%2FPython-Emblem.png&f=1&nofb=1&ipt=a018b428f114a05b49eada45b3f352996c1b518bc5379b98554fd55e482f92e2&ipo=images" alt="ECC" height="300px">
</div>
<br>

This project is a simple GTK-based Python executable that interfaces itself with the [ecc-api](https://github.com/zzampax/ecc-api) written in RUST. 
It is meant to provide a lightweight GUI controller to simplify the usage of the API.
## Config file
The script needs fetches the IP and port of the Elgato device via a `config.toml` file, it can be manually provided with the `--config` flag or be put in the `~/.config/elgatocontrolcenter/` directory.
### Example
```toml
[network]
ip = "192.168.17.11"
port = 9123
```
## Running the code
Before running the code it is essential to install the `requirements.txt` dependencies, it is recommended to use a python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
> Use the appropriate `activate` accordingly (eg. `activate.fish` for `fish` shell)
```bash
pip3 install -r requirements.txt
```
The code is then runnable as following:
```bash
python3 main.py
```
> For debugging purposes:
> ```bash
> python3 main.py --debug
> ```