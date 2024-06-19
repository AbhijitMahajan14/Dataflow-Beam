import os
import time 
from google.cloud import pubsub_v1

if __name__ == "__main__":
    project = ''
    pubsub_topic = ''
    input_file = '' 

    publisher = pubsub_v1.PublisherClient()

    with open(input_file, 'rb') as ifp:
        header = ifp.readline()  
        for line in ifp:
            event_data = line 
            print('Publishing {0} to {1}'.format(event_data, pubsub_topic))
            publisher.publish(pubsub_topic, event_data)
            time.sleep(1)    