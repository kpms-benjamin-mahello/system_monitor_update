from flask import render_template, jsonify, redirect, url_for, request, flash
import werkzeug
from system_monitor import app, api, Resource
import json
import subprocess
import os

from system_monitor.system.systemAddress import system_ip
import pandas as pd

with open('config.json') as f:
    data = json.load(f)

app.secret_key = 'secret_key'

# /systemdata
system_path = 'system_data.csv'

# /dockerdata
docker_path = 'docker.csv'


# simple API
class System_Json(Resource):
    def get(self):
        system_data = pd.read_csv(system_path)
        system_data = system_data.to_dict()
        return {'System data': system_data}, 200


class Docker_Json(Resource):
    def get(self):
        docker_data = pd.read_csv(docker_path)
        docker_data = docker_data.to_dict()
        return {'Docker data': docker_data}, 200


api.add_resource(System_Json, '/systemjson')
api.add_resource(Docker_Json, '/dockerjson')

interval = data["SystemMonitor"]["interval_time_sec"]


# Endpoints
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html', title="Home Page")


@app.route('/system')
def my_system():
    with open("system_data.csv") as file:
        return render_template('system_page.html', data=file, number=interval, title='Machine Monitor Page')


@app.route('/docker')
def my_docker():
    with open("docker.csv") as file:
        return render_template('docker_page.html', data=file, number=interval, title='Docker Monitor Page')


@app.route("/help")
def help_page():
    return render_template('help.html', title='Help Page')


@app.route("/dockerhelp")
def docker_help_page():
    return render_template('docker_help.html', title='Docker Help Page')

@app.route("/log")
def Log_page():
    logs = []
    ids = []
    with open("docker.csv") as f:
        for line in f:
            ids.append(line.split(",")[1])
    for item in ids:
        with open(f"{item}.html", "r") as f:
            logs.append(f.read())
    return render_template('log.html', logs=logs)



# Reboot the system
@app.route("/reboot", methods=['GET', 'POST'])
def reboot():
    password = "merlin#0"
    subprocess.run(f"echo {password} | sudo -S reboot", shell=True, check=True)
    return "System is rebooting", 200



@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        with open('config.json', 'r') as f:
            config_data = json.load(f)

        config_data['SystemMonitor']['interval_time_sec'] = int(request.form['interval_time_sec'])
        config_data['SystemMonitor']['ethernetPort'] = request.form['ethernetPort']
        config_data['SystemMonitor']['disk'] = request.form['disk']

        config_data['MQTT']['MQTTBroker'] = request.form['MQTTBroker']
        config_data['MQTT']['mqtt_user'] = request.form['mqtt_user']
        config_data['MQTT']['mqtt_password'] = request.form['mqtt_password']
        config_data['MQTT']['mqtt_port'] = request.form['mqtt_port']
        config_data['MQTT']['sendDocker'] = request.form.get('sendDocker') == 'True'
        config_data['MQTT']['sendSystem'] = request.form.get('sendSystem') == 'True'
        config_data['MQTT']['sendAsMQTT'] = request.form.get('sendAsMQTT') == 'True'

        config_data['SYSTEM_INFO']['version'] = request.form['version']
        config_data['SYSTEM_INFO']['BA'] = request.form['BA']
        config_data['SYSTEM_INFO']['MASCHINE'] = request.form['MASCHINE']

        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=4)

        flash('Config file updated successfully.', 'success')
        return redirect(url_for('home_page'))

    with open('config.json', 'r') as f:
        config_data = json.load(f)

    return render_template('config.html', config=config_data)


# Error Handler
@app.errorhandler(werkzeug.exceptions.NotFound)
def Notfound(e):
    return jsonify(error=str(e)), e.code
