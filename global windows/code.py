import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
import os
from apache_beam import window
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, AccumulationMode, AfterCount,Repeatedly

input_subscription = ''


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

def calculateProfit(elements):
  buy_rate = elements[5]
  sell_price = elements[6]
  products_count = int(elements[4])
  profit = (int(sell_price) - int(buy_rate)) * products_count
  elements.append(str(profit))
  return elements

pubsub_data = (
                p 
                | 'Read from pub sub' >> beam.io.ReadFromPubSub(subscription= input_subscription)
                | 'Remove extra chars' >> beam.Map(lambda data: (data.rstrip().lstrip()))
                | 'Split Row' >> beam.Map(lambda row : row.split(','))
                | 'Filter By Country' >> beam.Filter(lambda elements : (elements[1] == "Mumbai" or elements[1] == "Bangalore"))
                | 'Create Profit Column' >> beam.Map(calculateProfit)
                | 'Apply custom timestamp' >> beam.Map(custom_timestamp) 
                | 'Form Key Value pair' >> beam.Map(lambda elements : (elements[0], int(elements[7])))
                # Please change the time of gap of window duration and period accordingly
                | 'Window' >> beam.WindowInto(window.GlobalWindows(), trigger=Repeatedly(AfterCount(10)), accumulation_mode=AccumulationMode.DISCARDING)
                | 'Sum values' >> beam.CombinePerKey(sum)
                | 'Encode to byte string' >> beam.Map(encode_byte_string)
               # | 'Write to pus sub' >> beam.io.WriteToPubSub(output_topic)
              )

result = p.run()
result.wait_until_finish()