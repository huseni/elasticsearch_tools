# !/usr/bin/env python
#######################################################################################################################
#                                                                                                                     #
# THIS SCRIPT IS TO CHECK THE STATUS OF ELASTIC SERVICE LOGSTASH AND CAN START STOP, RESTART OR RETURN THE STATUS    #
# OF THE SERVICE.                                                                                                     #
#                                                                                                                     #
# THIS SHOULD BE DEPLOYED AND RUN PERIODICALLY TO CHECK THE CONSTANT STATUS OF THE SERVICES ON EACH CLUSTER NODE AND  #
# REMEDIATE IN CASE OF THE OUTAGE. IT IS TARGETED TO BE USED FOR THE SERVICES LIKE FILEBEAT, LOGSTASH, KIBANA AND     #
# ELASTICSEARCH CLUSTER NODES BY SUPPLYING THE APPROPRIATE PARMS                                                      #
# V. 1.0                                                                                                              #
# USAGE:                                                                                                              #
#       logstash_service_operations.py "start"                                                                        #
#       logstash_service_operations.py "stop"                                                                         #
#       logstash_service_operations.py "restart"                                                                      #
#       logstash_service_operations.py "status"                                                                       #
#                                                                                                                     #
#######################################################################################################################
import sys
import subprocess
import time
import os
import elastic_service_operations

try:
    import elastic_service_operations
except ImportError:
    print("ElasticServiceOperations is not importable. please make sure you have python installed properly")


def main():
    """
    This is the starting point of code execution
    :return:
    """
    # 'logstash' service related parameters. This can be modify if you want to reuse this class for the filebeat, kibana and logstash or even any other standard linux utility services.
    elastic_service = "logstash"  # This parameter value has to be the service name that you have running on the EC2 instance
    start_service_cmd = "service %s start" % elastic_service
    stop_service_cmd = "service %s stop" % elastic_service
    wait_time = 4

    # Logstash object to validate the service and operate
    service = elastic_service_operations.ElasticServiceOperations(elastic_service, start_service_cmd, stop_service_cmd, wait_time)

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