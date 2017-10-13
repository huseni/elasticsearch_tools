# !/usr/bin/env python
#######################################################################################################################
#                                                                                                                     #
# THIS SCRIPT IS TO CHECK THE STATUS OF YOUR ELASTIC SERVICES OR ANY SERVICES DEPENDING UPON YOUR INPUT AND START,    #
# STOP, RESTART OR RETURN THE STATUS OF THE SERVICE.                                                                  #
#                                                                                                                     #
# THIS SHOULD BE DEPLOYED AND RUN PERIODICALLY TO CHECK THE CONSTANT STATUS OF THE SERVICES ON EACH CLUSTER NODE AND  #
# REMEDIATE IN CASE OF THE OUTAGE. IT IS TARGETED TO BE USED FOR THE SERVICES LIKE FILEBEAT, LOGSTASH, KIBANA AND     #
# ELASTICSEARCH CLUSTER NODES BY SUPPLYING THE APPROPRIATE PARMS                                                      #
# V. 1.0                                                                                                              #
# USAGE:                                                                                                              #
#       elastic_service_operations.py "start"                                                                         #
#       elastic_service_operations.py "stop"                                                                          #
#       elastic_service_operations.py "restart"                                                                       #
#       elastic_service_operations.py "status"                                                                        #
#                                                                                                                     #
#######################################################################################################################

import sys
import subprocess
import time
import os


class ElasticServiceOperations(object):
    """
    This class is to define the framework to check the specific elastic stack process is running or not. If running and and want to restart, check only the status or stop or start operations are possible
    """
    # Default class member attribute settings
    elastic_service = None
    start_service_cmd = None
    stop_service_cmd = None
    wait_time = 6
    file_name = None
    check_service_process = None
    find_service_id = None
	

    def __init__(self, elastic_service, start_service_cmd, stop_service_cmd, wait_time):
        """
        This is to initialize the object with the specific elastic service for which we want to start, stop and wait to validate the service status
        :param elastic_service:
        :param start_service_cmd:
        :param stop_service_cmd:
        :param wait_time:
        """
        self.elastic_service = elastic_service
        self.start_service_cmd = start_service_cmd
        self.stop_service_cmd = stop_service_cmd
        self.wait_time = wait_time
        self.file_name = os.path.basename(__file__)
        self.find_service_id = 'ps -ef | grep -v grep | grep %s | /usr/bin/awk \'{print $2}\'' % self.elastic_service
        self.check_service_process = "ps -ef | grep -v grep | grep %s | wc -l" % self.elastic_service

    def is_service_running(self):
        """
        To Check if elastic stack service process is running on the ec2 instance. It returns the status in the true or false boolean variable
        """
        p_status = True
        elastic_service_ = subprocess.Popen(self.check_service_process, stdout=subprocess.PIPE, shell=True)
        out, err = elastic_service_.communicate()
        if int(out) < 1:
            p_status = False
        return p_status

    def start_service(self):
        """
        To check the service status on the ec2 host and if not running then attempt to start and return the status of the action on the stdout
        """
        # a = is_running(tomcat_process)
        if self.is_service_running():
            print("%s service is already running. No action may be necessary" % self.elastic_service)
        else:
            print("Attempting to start the service %s ..." % self.elastic_service)
            rc = subprocess.Popen(self.start_service_cmd, stdout=subprocess.PIPE, shell=True)
            if rc > 0:
                print("%s service started successfully" % self.elastic_service)
            else:
                print("Error while starting the %s service" % self.elastic_service)

    def stop_service(self):
        """
        To check the service status on the ec2 host and if running then attempt to stop and return the status of the action on the stdout.
        """
        if self.is_service_running():
            print("Attempting to stop the service %s ..." % self.elastic_service)
            subprocess.Popen(self.stop_service_cmd, stdout=subprocess.PIPE, shell=True)
            time.sleep(self.wait_time)
            if self.is_service_running():
                t_pid = subprocess.Popen([self.find_service_id], stdout=subprocess.PIPE, shell=True)
                out, err = t_pid.communicate()
                subprocess.Popen(["kill -9 " + out], stdout=subprocess.PIPE, shell=True)
                print("service is failed to shutdown, so killed with PID " + out)
        else:
            print("%s service process is not running" % self.elastic_service)

    def script_usage(self):
        """
        To provide the usage details about how do you run this script with the required commandline parameters.
        """
        print ("Usage: python " + self.file_name + " start|stop|status|restart")
        print "or"
        print ("Usage: <path>/" + self.file_name + " start|stop|status|restart")

    def service_status(self):
        """
        To Check the service process and compute the status of it.
        """
        if self.is_service_running():
            t_pid = subprocess.Popen(self.find_service_id, stdout=subprocess.PIPE, shell=True)
            out, err = t_pid.communicate()
            print("%s service process is running with PID %s" % (self.elastic_service, out))
        else:
            print("%s service process is not running" % self.elastic_service)

    def restart_service(self):
        """
        To restart the current running or stop service as necessary.
        """
        self.stop_service()
        time.sleep(10)
        self.start_service()


def main():
    """
    This is the starting point of code execution
    :return:
    """
	
    # 'Elasticsearch' service related parameters. This can be modify if you want to reuse this class for the filebeat, kibana and logstash or even any other standard linux utility services.
    elastic_service = "elasticsearch"  # This parameter value has to be the service name that you have running on the EC2 instance
    start_service_cmd = "service %s start" % elastic_service
    stop_service_cmd = "service %s stop" % elastic_service
    wait_time = 4

    # Elasticsearch object to validate the service and operate
    service = ElasticServiceOperations(elastic_service, start_service_cmd, stop_service_cmd, wait_time)

    # Check for the number of commandline arguments. It must be '2'
    if len(sys.argv) != 2:
        print ("ERROR: Missing mandatory required arguments")
        service.script_usage()
        sys.exit(0)
    else:
        action = sys.argv[1]

    # Start the elastic service server
    if action == 'stop':
        service.stop_service()

    # Status the elastic service server
    if action == 'status':
        service.service_status()

    # Start the elastic service server
    if action == 'start':
        service.start_service()

    # Start the elastic service server
    if action == 'restart':
        service.restart_service()
    
# Main execution point
if __name__ == '__main__':
    main()