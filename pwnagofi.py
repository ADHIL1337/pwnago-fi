import os
import logging
import subprocess
from pwnagotchi import plugins
from threading import Lock
from flask import Flask, request, render_template_string

class WifiControl(plugins.Plugin):
    __author__ = 'your_email@example.com'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin connects to and disconnects from a WiFi network.'

    def __init__(self):
        self.ready = False
        self.lock = Lock()
        self.connected = False

    def on_loaded(self):
        logging.info("WifiControl: plugin loaded")
        self.ready = True

    def connect_to_wifi(self, ssid, password):
        """
        Connect to a WiFi network.
        """
        try:
            result = subprocess.run(
                ["nmcli", "d", "wifi", "connect", ssid, "password", password],
                capture_output=True, text=True, check=True)
            logging.info(f"WifiControl: Connected to {ssid}")
            self.connected = True
        except subprocess.CalledProcessError as e:
            logging.error(f"WifiControl: Failed to connect to {ssid}: {e.stderr}")
            self.connected = False

    def disconnect_from_wifi(self):
        """
        Disconnect from the current WiFi network.
        """
        try:
            result = subprocess.run(
                ["nmcli", "d", "disconnect", "wlan0"],
                capture_output=True, text=True, check=True)
            logging.info("WifiControl: Disconnected from WiFi")
            self.connected = False
        except subprocess.CalledProcessError as e:
            logging.error(f"WifiControl: Failed to disconnect from WiFi: {e.stderr}")

    def on_internet_available(self, agent):
        """
        Called when there's internet connectivity.
        """
        if not self.ready or self.lock.locked():
            return

        with self.lock:
            # Flask app to get user input for SSID and password
            app = Flask(__name__)

            @app.route('/', methods=['GET', 'POST'])
            def index():
                if request.method == 'POST':
                    ssid = request.form['ssid']
                    password = request.form['password']
                    self.connect_to_wifi(ssid, password)
                return render_template_string('''
                    <form method="post">
                        SSID: <input type="text" name="ssid"><br>
                        Password: <input type="password" name="password"><br>
                        <input type="submit" value="Connect">
                    </form>
                    <form method="post" action="/disconnect">
                        <input type="submit" value="Disconnect">
                    </form>
                ''')

            @app.route('/disconnect', methods=['POST'])
            def disconnect():
                self.disconnect_from_wifi()
                return "Disconnected"

            app.run(port=5000)   
