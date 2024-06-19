import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import os
from apache_beam import window
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, AccumulationMode, AfterCount


input_subscription = ''

output_topic = ''
options = PipelineOptions()
options.view_as(StandardOptions).streaming = True

p = beam.Pipeline(options=options)

def encode_byte_string(element):
   print(element)
   element = str(element)
   return element.encode('utf-8')

def custom_timestamp(elements):
  unix_timestamp = elements[7]
 
  return beam.window.TimestampedValue(elements, int(unix_timestamp))

pubsub_data = (
                p 
                | 'Read from pub sub' >> beam.io.ReadFromPubSub(subscription= input_subscription)
                | 'Remove extra chars' >> beam.Map(lambda data: (data.rstrip().lstrip()))
                | 'Split Row' >> beam.Map(lambda row : row.split(','))
                | 'Filter By Country' >> beam.Filter(lambda elements : (elements[1] == "Mumbai" or elements[1] == "Bangalore"))
                #| 'Apply custom timestamp and extract pieces sold' >> beam.Map(custom_timestamp) 
                | 'Form Key Value pair' >> beam.Map(lambda elements : (elements[3], int(elements[4])))
                # Please change the time of gap of window duration and period accordingly
                | 'Window' >> beam.WindowInto(window.Sessions(25))
                | 'Sum values' >> beam.CombinePerKey(sum)
                | 'Encode to byte string' >> beam.Map(encode_byte_string)
                | 'Write to pus sub' >> beam.io.WriteToPubSub(output_topic)
              )

result = p.run()
result.wait_until_finish()