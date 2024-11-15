import logging
from flask import render_template_string, request, abort
from pwnagotchi import plugins

TEMPLATE = """
{% extends "base.html" %}
{% set active_page = "plugins" %}
{% block title %}
    WiFi Config
{% endblock %}

{% block content %}
    <h2>WiFi Configuration</h2>
    <form method="post" action="/plugins/wificonfig/save">
        <label for="ssid">SSID:</label><br>
        <input type="text" id="ssid" name="ssid"><br><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <input type="submit" value="Save">
    </form>
{% endblock %}
"""

class WiFiConfig(plugins.Plugin):
    __author__ = 'your_username'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'This plugin allows the user to configure WiFi settings.'

    def __init__(self):
        self.ready = False

    def on_config_changed(self, config):
        self.config = config
        self.ready = True

    def on_loaded(self):
        """
        Gets called when the plugin gets loaded
        """
        logging.info("WiFiConfig plugin loaded.")

    def on_webhook(self, path, request):
        if not self.ready:
            return "Plugin not ready"

        if not path or path == "/":
            return render_template_string(TEMPLATE)

        if request.method == "POST" and path == "save":
            ssid = request.form.get('ssid')
            password = request.form.get('password')
            if ssid and password:
                # Save the SSID and password to the config
                self.config['main']['wifi']['ssid'] = ssid
                self.config['main']['wifi']['password'] = password
                return "WiFi settings updated successfully!"
            else:
                return "SSID and password are required!", 400

        abort(404)
