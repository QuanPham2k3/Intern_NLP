import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=API_KEY)

def process_batch(input_file_path, endpoint, completion_window):
  # up load input file 
  with open(input_file_path, "rb") as file:
    upload_file = client.files.create(
      file=file,
      purpose="batch"
    ) 

  # creating the batch job
  batch_job = client.batches.create(
      input_file_id=upload_file.id,
      endpoint=endpoint,
      completion_window=completion_window, 
     
  )
  # monitor the batch job status
  while batch_job.status not in ["completed", "failed", 'cancelled']:
    batch_job = client.batches.retrieve(batch_job.id)
    print(f' Batch job status: {batch_job.status}..try again in 10 seconds')
    time.sleep(10)
    
  # Download the output file
  if batch_job.status == "completed":
    result_file_id = batch_job.output_file_id
    print(batch_job)
    result = client.files.content(result_file_id).content
    print(result)

    result_file_name = 'final_batch.jsonl'
    with open(result_file_name, 'wb') as f:
     f.write(result)
    
    return "Batch job completed successfully"
  else:
    print(f'Batch job failed with status {batch_job.status}')
    return None


input_file_path = 'input.jsonl'
endpoint = '/v1/chat/completions'
completion_window = '24h'

results = process_batch(input_file_path, endpoint, completion_window)
print(results)
