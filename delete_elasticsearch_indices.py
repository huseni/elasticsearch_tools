#!/usr/bin/env python
######################################################################################
#                                                                                    #
# THIS PROGRAM IS TO IDENTIFY ALL THE ELASTIC INDICES WHICH ARE OLDER THAN 180 DAYS  #
# AND DELETE THEM FROM THE ELASTICSEARCH CLUSTER.                                    #
# V. 1.0                                                                             #
#                                                                                    #
######################################################################################
from datetime import datetime, timedelta
import requests, os
import datetime
from dateutil.parser import parse
from pprint import pprint
import re
#from elasticsearch import Elasticsearch


def calculate_datetime_delta():
    """
    Calculate the delta-time for indices
    """
    datetime_now = datetime.datetime.now()
    one_months_ago = datetime_now - timedelta(days=(1 * 365) / 12)
    return str(datetime_now), str(one_months_ago)


def filter_indices_to_delete(open_indices_list):
    """
    Filter the indices for the specific criteria to close - older than 180 days
    """
    now_datetime, one_months_old_datetime = calculate_datetime_delta()
    print("****************** datetime calculation ****************")
    print("current date: %s" % now_datetime)
    print("six month old date: %s" % one_months_old_datetime)
    a = str(now_datetime)
    ax = a.split()
    now_date = ax[0]
    system_date = parse(now_date)

    # generate the list of indices to be deleted
    print ("************************** calculated delta datetime ************************")
    indices_tobe_deleted = list()
    for i in open_indices_list:
        i = str(i)
        c = i.split('-')
        clist = c[1]
        index_date = parse(clist)
        day_difference = system_date - index_date
        print system_date, index_date, day_difference.days, "days"
        if day_difference.days > 180:
            print("Index to be deleted : %s" % i)
            indices_tobe_deleted.append(i)
    return indices_tobe_deleted

def delete_elastic_indices(filtered_indices_list=None, elastic_server_url='http://localhost:9200/'):
    """
    Delete elastic indices for the elasticsearch cluster
    """
    session = requests.Session()
    for index in filtered_indices_list:
        index = str(index)
        response = session.delete(os.path.join(elastic_server_url, index))
        print response.text


def query_indices_from_elasticsearch(elasticsearch_server_url='http://localhost:9200/', indices_file=None):
    """
    To produce the list of indices to be deleted
    """
    session = requests.Session()
    response = session.get(os.path.join(elasticsearch_server_url, '_cat', 'indices?v'))
    indices_info = response.text
    with open(indices_file, "w") as text_file:
        text_file.write("%s" % indices_info)
    return indices_file


def get_closed_indices_list(indics_file=None):
    """
    To filter the indices to be deleted
    :return:
    """
    indices = list()
    if indics_file:
        with open(indics_file) as f:
            line = f.readline()[1:]
            for index_line in f:
                neglects_list = (".kibana", "blogs", "elastalert_status", "kibana-int")
                if not any(s in index_line for s in neglects_list):
                    pattern = re.compile(r'(.*?) (open|close)\s*(logstash-.*?( |$))', re.IGNORECASE)
                    found_pattern = pattern.search(index_line)
                    index_status = found_pattern.group(2).strip()
                    index_name = found_pattern.group(3).strip()
                    if "close" in index_status:
                        print("open index : %s" % index_name)
                        indices.append(index_name)
            return indices

def main():
    elastic_cluster_url = 'http://elasticsearch-lb-1745.us-east-2.elb.amazonaws.com:9200/'
    file_location = '/opt/devops/cron/indices.txt'

    # Query the indices information from the elastic-search clusters
    index_file = query_indices_from_elasticsearch(elastic_cluster_url, file_location)

    # Parse the indices information and get the 'closed' indices list
    indices_list = get_closed_indices_list(index_file)

    # Filter the 'closed' indices which are older than 60 days
    indices_to_delete = filter_indices_to_delete(indices_list)
    print("********************* filtered indices list ********************")
    for i in indices_to_delete:
        print(i)

    # Delete the indices older than 180 days
    delete_elastic_indices(indices_to_delete, elastic_cluster_url)


if __name__ == "__main__":
    main()
