import subprocess
import signal
import gi
import os
import json
import tomllib
import argparse
import colorsys

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
DEBUG = False

def rgb_to_hsl(rgb):
    r, g, b = [x for x in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = h * 360
    s = s * 100
    l = l * 100
    return h, s, l

def safe_execution(command, message):
    if not isinstance(command, list):
        return
    if not all(isinstance(x, str) for x in command):
        return
    if not isinstance(message, str):
        return
        
    output = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = output.communicate()
    stdout, stderr = stdout.decode().strip(), stderr.decode().strip()
    if DEBUG: print(f"\tstdout: {stdout}\n\tstderr: {stderr}")
    try:
        if json.loads(stdout)["error"]:
            subprocess.Popen(["notify-send", "-u", "critical", "ElgatoControlCenter", f"Error: {json.loads(stdout)['error']}"])
            return
        if stderr:
            subprocess.Popen(["notify-send", "-u", "critical", "ElgatoControlCenter", f"Error: {stderr}"])
    except KeyError:
        subprocess.Popen(["notify-send", "-u", "normal", "ElgatoControlCenter", message])

class TrayApp:
    def __init__(self, ip, port):
        # Save the IP and port of the Elgato device
        self.ip = ip
        self.port = port

        # Create an AppIndicator object (system tray)
        self.indicator = AppIndicator3.Indicator.new(
            "tray_icon",
            "weather-clear",  # Use an icon from the system
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        # self.indicator.set_attention_icon("indicator-messages-new")

        # Create a right-click menu
        self.menu = Gtk.Menu()

        # Add menu items
        task_toggle_power_item = Gtk.MenuItem(label="Toggle Power")
        task_toggle_power_item.connect("activate", self.run_toggle_power)
        self.menu.append(task_toggle_power_item)

        task_set_color_item = Gtk.MenuItem(label="Set Color")
        task_set_color_item.connect("activate", self.run_set_color)
        self.menu.append(task_set_color_item)

        # Add temperature levels
        task_set_temperature_menu = Gtk.MenuItem(label="Set Temperature")
        task_set_temperature_submenu = Gtk.Menu()
        task_set_temperature_menu.set_submenu(task_set_temperature_submenu)

        for level in [2900, 4000, 5000, 6500, 7000]:
            item = Gtk.MenuItem(label=f"{level}K")
            item.connect("activate", self.run_set_temperature, level)
            task_set_temperature_submenu.append(item)

        self.menu.append(task_set_temperature_menu)

        # Add brightness levels
        task_brightness_menu = Gtk.MenuItem(label="Set Brightness")
        task_brightness_submenu = Gtk.Menu()
        task_brightness_menu.set_submenu(task_brightness_submenu)

        for level in [0, 25, 50, 75, 100]:
            item = Gtk.MenuItem(label=f"{level}%")
            item.connect("activate", self.run_set_brightness, level)
            task_brightness_submenu.append(item)

        self.menu.append(task_brightness_menu)

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)

        # Show all the menu items
        self.menu.show_all()

        # Set the menu for the tray icon
        self.indicator.set_menu(self.menu)

    def show_color_picker(self):
        dialog = Gtk.ColorChooserDialog(title="Choose a color", transient_for=None)
        dialog.set_position(Gtk.WindowPosition.CENTER)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            color = dialog.get_rgba()
            dialog.destroy()
            # return (r, g, b) tuple and name of the color
            return (color.red, color.green, color.blue), color.to_string()
        else:
            dialog.destroy()
            return None

    def run_toggle_power(self, _):
        global DEBUG
        if DEBUG: print("Toggling Power")
        safe_execution(["ecc-api", "--ip", self.ip, "--port", str(self.port), "--toggle"], "Toggling Power")

    def run_set_color(self, _):
        rgbcolor, colorname = self.show_color_picker()
        if rgbcolor is None:
            return
        if DEBUG: print(f"Setting color to {rgbcolor}")
        h, s, _l = rgb_to_hsl(rgbcolor)
        safe_execution(["ecc-api", "--ip", self.ip, "--port", str(self.port), "--hue", str(h), "--saturation", str(s)], f"Changing Color to {colorname}")

    def run_set_temperature(self, _, temperature):
        temperature = int((temperature - 2900) / (7000 - 2900) * (344 - 143) + 143)
        if DEBUG: print(f"Setting temperature to {temperature}")
        safe_execution(["ecc-api", "--ip", self.ip, "--port", str(self.port), "--temperature", str(temperature)], f"Setting Temperature to {temperature}")

    def run_set_brightness(self, _, level):
        brightness = int(level)
        if DEBUG: print(f"Setting brightness to {brightness}")
        safe_execution(["ecc-api", "--ip", self.ip, "--port", str(self.port), "--brightness", str(brightness)], f"Setting Brightness to {brightness}")

    def quit(self, _):
        Gtk.main_quit()


def read_config(config_path=None):
    global DEBUG
    # Open $HOME/.config/elgatocontrolcenter/config.toml
    if config_path is None:
        config_path = os.path.expanduser("~/.config/elgatocontrolcenter/config.toml")
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            os.system("notify-send -u critical 'Error ElgatoControlCenter' 'Config file not found'")
            exit(1)
    else:
        if not os.path.exists(config_path):
            os.system("notify-send -u critical 'Error ElgatoControlCenter' 'Config file not found'")
            exit(1)
    
    if DEBUG: print(f"Reading config from {config_path}")

    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError:
        os.system("notify-send -u critical 'Error ElgatoControlCenter' 'Config file is not a valid TOML file'")
        exit(1)

    try:
        ip = config["network"]["ip"]
        port = config["network"]["port"]
    except KeyError:
        os.system("notify-send -u critical 'Error ElgatoControlCenter' 'Config file is missing required fields'")
        exit(1)
    return ip, port


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ECC System Tray")
    parser.add_argument("--debug", help="Enable debug mode", action="store_true")
    parser.add_argument("--config", help="Select a config file (default path in ~/.config/elgatocontrolcenter/)", type=str)
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug

    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow Ctrl+C to close the app

    ip, port = read_config(args.config)
    print(f"Attaching to {ip}:{port}...")
    app = TrayApp(ip=ip, port=port)
    Gtk.main()

if __name__ == "__main__":
    main()