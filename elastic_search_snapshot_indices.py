#!/usr/bin/env python
######################################################################################
#                                                                                    #
# THIS PROGRAM IS TO CREATE A SNAPSHOT FOR ALL THE INDICES PRESENT IN ELASTICCLUSTER #
# & BACKUP THEM INTO S3 BUCKET.                                                      #
# V. 1.0                                                                             #
#                                                                                    #
######################################################################################
from datetime import datetime, timedelta
import requests, os
import datetime
from dateutil.parser import parse
from pprint import pprint
import re


def query_snapshot_repo_from_elasticsearch(elasticsearch_server_url='http://localhost:9200/'):
    """
    To query and confirm that snapshot repo exists and associated with elasticsearch
    """
    session = requests.Session()
    response = session.get(os.path.join(elasticsearch_server_url, '_snapshot', 'my_s3_backup'))
    indices_info = response.text
    print indices_info


def snapshot_elasticsearch_indices(elastic_server_url='http://localhost:9200/', snapshot_name='none'):
    """
    To take a snapshot for all the indices in elasticsearch cluster
    """
    cmd = "%s?wait_for_completion=true" %(snapshot_name)
    session = requests.Session()
    response = session.put(os.path.join(elastic_server_url, '_snapshot', 'my_s3_backup', cmd ))
    print response.text


def generate_datewise_snapshot_name(snapshot_name='none'):
    """
    To append, generate and return the snapshot name datewise 
    """
    now = datetime.datetime.now()
    snapshot = "%s-%s" %(snapshot_name, now.strftime("%Y-%m-%d_%H:%M"))
    return snapshot
    


def snapshot_status_elasticsearch_indices(elastic_server_url='http://localhost:9200/', snapshot_name='none'):
    """
    To verify the status of elasticsearch snapshot status
    """
    session = requests.Session()
    response = session.get(os.path.join(elastic_server_url, '_snapshot', 's3_dev_backup', snapshot_name, '_status'))
    print response.text


def main():
    elastic_cluster_url = 'http://elasticsearch-elb-145.us-east-2.elb.amazonaws.com:9200/'
    snapshot_name = 'snapshot_prod_elastic-cluster'

    # query snapshot repo and confirm it exists
    query_snapshot_repo_from_elasticsearch(elastic_cluster_url)

    # append the elasticcluster snapshot name
    snapshot_datetime_name = generate_datewise_snapshot_name(snapshot_name) 
    
    # take a snapshot for elasticsearch cluster
    snapshot_elasticsearch_indices(elastic_cluster_url, snapshot_datetime_name)

    # confirm the status of snapshot process ran for elasticsearch 
    snapshot_status_elasticsearch_indices(elastic_cluster_url, snapshot_datetime_name)

if __name__ == "__main__":
    main()
