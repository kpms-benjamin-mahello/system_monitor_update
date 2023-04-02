#!/usr/bin/python3


from system_monitor import scheduler, app
from system_monitor.docker.docker import running_containers
from system_monitor.system.systeminfo.c_system import system
#from system_monitor.mqtt_pub.publisher2 import publish_job
#from system_monitor.mqtt_sub.subscriber2 import subscribe_job
from system_monitor.routes.route import interval



if __name__ == '__main__':
    scheduler.add_job(id='Scheduled Task1', func=system, trigger="interval", seconds=interval)
    scheduler.add_job(id='Scheduled Task2', func=running_containers, trigger="interval", seconds=interval)
    #scheduler.add_job(id='Scheduled Task3', func=publish_job, trigger="interval", seconds=interval)
    #scheduler.add_job(id='Scheduled Task4', func=subscribe_job, trigger="interval", seconds=interval)
    scheduler.start()
    app.run(use_reloader=True, host='0.0.0.0', port=5002, debug=True)




