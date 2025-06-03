import pymongo
import boto3
import json
import os
import openai
from dotenv import load_dotenv
import argparse
import requests
from pymongo import UpdateOne

# MongoDB connection
client = pymongo.MongoClient("TODO - MONGODB CONNECTION STRING")
db = client["TODO - DATABASE NAME"]
collection = db["TODO - COLLECTION NAME"]

# AWS credentials and Bedrock setup
aws_access_key_id = 'TODO - AWS ACCESS KEY ID'
aws_secret_access_key = 'TODO - AWS SECRET KEY'
aws_session_token = 'TODO - AWS SESSION TOKEN'

openai.api_key = "TODO - OPENAI API KEY"



def get_embedding_from_openai(text, model="text-embedding-3-small"):

    response = openai.embeddings.create(
        model=model,
        input=text,
        encoding_format="float"
    )

    embedding = response.data[0].embedding
    return embedding


def get_embedding_titan(input_text):

    # Initialize the Bedrock client
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
    )
    
    try:
        # Prepare the request body for embedding
        request_body = {
            "inputText": input_text,
            # "embeddingConfig": {"outputEmbeddingLength": 384}
        }
        body = json.dumps(request_body)

        # Invoke the model for embedding generation
        response = bedrock_client.invoke_model(
            body=body,
            modelId="amazon.titan-embed-text-v2:0",
            accept="application/json",
            contentType="application/json"
        )

        # Parse the response
        response_body = json.loads(response['Body'].read())
        embedding = response_body.get("embedding")
        return embedding
    except Exception as e:
        print(f"An error occurred while generating embedding: {e}")
        return None
    
def get_embedding_voyage(input_text):


    api_key = "TODO - VOYAGE API KEY"
    
    # Voyage AI API endpoint for embeddings
    url = "https://api.voyageai.com/v1/embeddings"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "voyage-3-large",
        "input": input_text,
        "input_type": "query" # Can be "query" or "document" depending on your use case
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None



documents = [
  {
    "llt_name": "Abdominal pain",
    "llt_code": "10000081",
    "pt_name": "Abdominal pain",
    "pt_code": "10000081"
  },
  {
    "llt_name": "Pain abdominal",
    "llt_code": "10033374",
    "pt_name": "Abdominal pain",
    "pt_code": "10000081"
  },
  {
    "llt_name": "Tummy ache",
    "llt_code": "10045148",
    "pt_name": "Abdominal pain",
    "pt_code": "10000081"
  },
  {
    "llt_name": "Stomach pain",
    "llt_code": "10042101",
    "pt_name": "Abdominal pain",
    "pt_code": "10000081"
  },
  {
    "llt_name": "Belly pain",
    "llt_code": "10004687",
    "pt_name": "Abdominal pain",
    "pt_code": "10000081"
  },
  {
    "llt_name": "Headache",
    "llt_code": "10019211",
    "pt_name": "Headache",
    "pt_code": "10019211"
  },
  {
    "llt_name": "Throbbing headache",
    "llt_code": "10058140",
    "pt_name": "Headache",
    "pt_code": "10019211"
  },
  {
    "llt_name": "Intermittent headache",
    "llt_code": "10059296",
    "pt_name": "Headache",
    "pt_code": "10019211"
  },
  {
    "llt_name": "Cephalgia",
    "llt_code": "10008196",
    "pt_name": "Headache",
    "pt_code": "10019211"
  },
  {
    "llt_name": "Head pain",
    "llt_code": "10019233",
    "pt_name": "Headache",
    "pt_code": "10019211"
  },
  {
    "llt_name": "Tension headache",
    "llt_code": "10043269",
    "pt_name": "Tension headache",
    "pt_code": "10043269"
  },
  {
    "llt_name": "Band-like headache",
    "llt_code": "10004087",
    "pt_name": "Tension headache",
    "pt_code": "10043269"
  },
  {
    "llt_name": "Tension-type headache",
    "llt_code": "10043270",
    "pt_name": "Tension headache",
    "pt_code": "10043269"
  },
  {
    "llt_name": "Nausea",
    "llt_code": "10028813",
    "pt_name": "Nausea",
    "pt_code": "10028813"
  },
  {
    "llt_name": "Feeling sick",
    "llt_code": "10016256",
    "pt_name": "Nausea",
    "pt_code": "10028813"
  },
  {
    "llt_name": "Queasiness",
    "llt_code": "10037612",
    "pt_name": "Nausea",
    "pt_code": "10028813"
  },
  {
    "llt_name": "Sick to stomach",
    "llt_code": "10040368",
    "pt_name": "Nausea",
    "pt_code": "10028813"
  },
  {
    "llt_name": "Vomiting",
    "llt_code": "10047700",
    "pt_name": "Vomiting",
    "pt_code": "10047700"
  },
  {
    "llt_name": "Throwing up",
    "llt_code": "10043578",
    "pt_name": "Vomiting",
    "pt_code": "10047700"
  },
  {
    "llt_name": "Emesis",
    "llt_code": "10014893",
    "pt_name": "Vomiting",
    "pt_code": "10047700"
  },
  {
    "llt_name": "Being sick",
    "llt_code": "10004689",
    "pt_name": "Vomiting",
    "pt_code": "10047700"
  },
  {
    "llt_name": "Diarrhoea",
    "llt_code": "10012735",
    "pt_name": "Diarrhoea",
    "pt_code": "10012735"
  },
  {
    "llt_name": "Diarrhea",
    "llt_code": "10012727",
    "pt_name": "Diarrhoea",
    "pt_code": "10012735"
  },
  {
    "llt_name": "Loose stools",
    "llt_code": "10024749",
    "pt_name": "Diarrhoea",
    "pt_code": "10012735"
  },
  {
    "llt_name": "Watery stools",
    "llt_code": "10047548",
    "pt_name": "Diarrhoea",
    "pt_code": "10012735"
  },
  {
    "llt_name": "Frequent bowel movements",
    "llt_code": "10017225",
    "pt_name": "Diarrhoea",
    "pt_code": "10012735"
  },
  {
    "llt_name": "Constipation",
    "llt_code": "10011224",
    "pt_name": "Constipation",
    "pt_code": "10011224"
  },
  {
    "llt_name": "Difficulty passing stools",
    "llt_code": "10012878",
    "pt_name": "Constipation",
    "pt_code": "10011224"
  },
  {
    "llt_name": "Hard stools",
    "llt_code": "10019030",
    "pt_name": "Constipation",
    "pt_code": "10011224"
  },
  {
    "llt_name": "Infrequent bowel movements",
    "llt_code": "10021781",
    "pt_name": "Constipation",
    "pt_code": "10011224"
  },
  {
    "llt_name": "Fatigue",
    "llt_code": "10016256",
    "pt_name": "Fatigue",
    "pt_code": "10016256"
  },
  {
    "llt_name": "Tiredness",
    "llt_code": "10043890",
    "pt_name": "Fatigue",
    "pt_code": "10016256"
  },
  {
    "llt_name": "Exhaustion",
    "llt_code": "10015368",
    "pt_name": "Fatigue",
    "pt_code": "10016256"
  },
  {
    "llt_name": "Feeling tired",
    "llt_code": "10016264",
    "pt_name": "Fatigue",
    "pt_code": "10016256"
  },
  {
    "llt_name": "Weariness",
    "llt_code": "10047562",
    "pt_name": "Fatigue",
    "pt_code": "10016256"
  },
  {
    "llt_name": "Dizziness",
    "llt_code": "10013573",
    "pt_name": "Dizziness",
    "pt_code": "10013573"
  },
  {
    "llt_name": "Dizzy",
    "llt_code": "10013578",
    "pt_name": "Dizziness",
    "pt_code": "10013573"
  },
  {
    "llt_name": "Light-headedness",
    "llt_code": "10024264",
    "pt_name": "Dizziness",
    "pt_code": "10013573"
  },
  {
    "llt_name": "Feeling faint",
    "llt_code": "10016248",
    "pt_name": "Dizziness",
    "pt_code": "10013573"
  },
  {
    "llt_name": "Vertigo",
    "llt_code": "10047386",
    "pt_name": "Vertigo",
    "pt_code": "10047386"
  },
  {
    "llt_name": "Spinning sensation",
    "llt_code": "10041549",
    "pt_name": "Vertigo",
    "pt_code": "10047386"
  },
  {
    "llt_name": "Room spinning",
    "llt_code": "10039287",
    "pt_name": "Vertigo",
    "pt_code": "10047386"
  },
  {
    "llt_name": "Rash",
    "llt_code": "10037844",
    "pt_name": "Rash",
    "pt_code": "10037844"
  },
  {
    "llt_name": "Skin rash",
    "llt_code": "10040785",
    "pt_name": "Rash",
    "pt_code": "10037844"
  },
  {
    "llt_name": "Skin eruption",
    "llt_code": "10040773",
    "pt_name": "Rash",
    "pt_code": "10037844"
  },
  {
    "llt_name": "Skin reaction",
    "llt_code": "10040799",
    "pt_name": "Rash",
    "pt_code": "10037844"
  },
  {
    "llt_name": "Pruritus",
    "llt_code": "10037087",
    "pt_name": "Pruritus",
    "pt_code": "10037087"
  },
  {
    "llt_name": "Itching",
    "llt_code": "10023237",
    "pt_name": "Pruritus",
    "pt_code": "10037087"
  },
  {
    "llt_name": "Itchy skin",
    "llt_code": "10023245",
    "pt_name": "Pruritus",
    "pt_code": "10037087"
  },
  {
    "llt_name": "Skin itching",
    "llt_code": "10040778",
    "pt_name": "Pruritus",
    "pt_code": "10037087"
  },
  {
    "llt_name": "Insomnia",
    "llt_code": "10022437",
    "pt_name": "Insomnia",
    "pt_code": "10022437"
  },
  {
    "llt_name": "Sleeplessness",
    "llt_code": "10040887",
    "pt_name": "Insomnia",
    "pt_code": "10022437"
  },
  {
    "llt_name": "Difficulty sleeping",
    "llt_code": "10012884",
    "pt_name": "Insomnia",
    "pt_code": "10022437"
  },
  {
    "llt_name": "Can't sleep",
    "llt_code": "10007296",
    "pt_name": "Insomnia",
    "pt_code": "10022437"
  },
  {
    "llt_name": "Sleep disturbance",
    "llt_code": "10040838",
    "pt_name": "Insomnia",
    "pt_code": "10022437"
  },
  {
    "llt_name": "Anxiety",
    "llt_code": "10002855",
    "pt_name": "Anxiety",
    "pt_code": "10002855"
  },
  {
    "llt_name": "Nervousness",
    "llt_code": "10029086",
    "pt_name": "Anxiety",
    "pt_code": "10002855"
  },
  {
    "llt_name": "Worry",
    "llt_code": "10048017",
    "pt_name": "Anxiety",
    "pt_code": "10002855"
  },
  {
    "llt_name": "Feeling anxious",
    "llt_code": "10016235",
    "pt_name": "Anxiety",
    "pt_code": "10002855"
  },
  {
    "llt_name": "Depression",
    "llt_code": "10012378",
    "pt_name": "Depression",
    "pt_code": "10012378"
  },
  {
    "llt_name": "Feeling depressed",
    "llt_code": "10016241",
    "pt_name": "Depression",
    "pt_code": "10012378"
  },
  {
    "llt_name": "Low mood",
    "llt_code": "10024855",
    "pt_name": "Depression",
    "pt_code": "10012378"
  },
  {
    "llt_name": "Sadness",
    "llt_code": "10039418",
    "pt_name": "Depression",
    "pt_code": "10012378"
  },
  {
    "llt_name": "Hypertension",
    "llt_code": "10020772",
    "pt_name": "Hypertension",
    "pt_code": "10020772"
  },
  {
    "llt_name": "High blood pressure",
    "llt_code": "10020126",
    "pt_name": "Hypertension",
    "pt_code": "10020772"
  },
  {
    "llt_name": "Elevated blood pressure",
    "llt_code": "10014644",
    "pt_name": "Hypertension",
    "pt_code": "10020772"
  },
  {
    "llt_name": "Raised blood pressure",
    "llt_code": "10037798",
    "pt_name": "Hypertension",
    "pt_code": "10020772"
  },
  {
    "llt_name": "Hypotension",
    "llt_code": "10021097",
    "pt_name": "Hypotension",
    "pt_code": "10021097"
  },
  {
    "llt_name": "Low blood pressure",
    "llt_code": "10024758",
    "pt_name": "Hypotension",
    "pt_code": "10021097"
  },
  {
    "llt_name": "Decreased blood pressure",
    "llt_code": "10011780",
    "pt_name": "Hypotension",
    "pt_code": "10021097"
  },
  {
    "llt_name": "Blood pressure drop",
    "llt_code": "10005330",
    "pt_name": "Hypotension",
    "pt_code": "10021097"
  },
  {
    "llt_name": "Tachycardia",
    "llt_code": "10042772",
    "pt_name": "Tachycardia",
    "pt_code": "10042772"
  },
  {
    "llt_name": "Fast heart rate",
    "llt_code": "10016160",
    "pt_name": "Tachycardia",
    "pt_code": "10042772"
  },
  {
    "llt_name": "Rapid heartbeat",
    "llt_code": "10037832",
    "pt_name": "Tachycardia",
    "pt_code": "10042772"
  },
  {
    "llt_name": "Racing heart",
    "llt_code": "10037747",
    "pt_name": "Tachycardia",
    "pt_code": "10042772"
  },
  {
    "llt_name": "Bradycardia",
    "llt_code": "10006093",
    "pt_name": "Bradycardia",
    "pt_code": "10006093"
  },
  {
    "llt_name": "Slow heart rate",
    "llt_code": "10040887",
    "pt_name": "Bradycardia",
    "pt_code": "10006093"
  },
  {
    "llt_name": "Slow pulse",
    "llt_code": "10040888",
    "pt_name": "Bradycardia",
    "pt_code": "10006093"
  },
  {
    "llt_name": "Dyspnoea",
    "llt_code": "10013968",
    "pt_name": "Dyspnoea",
    "pt_code": "10013968"
  },
  {
    "llt_name": "Shortness of breath",
    "llt_code": "10040368",
    "pt_name": "Dyspnoea",
    "pt_code": "10013968"
  },
  {
    "llt_name": "Breathing difficulty",
    "llt_code": "10006271",
    "pt_name": "Dyspnoea",
    "pt_code": "10013968"
  },
  {
    "llt_name": "Breathlessness",
    "llt_code": "10006281",
    "pt_name": "Dyspnoea",
    "pt_code": "10013968"
  },
  {
    "llt_name": "Chest pain",
    "llt_code": "10008479",
    "pt_name": "Chest pain",
    "pt_code": "10008479"
  },
  {
    "llt_name": "Chest discomfort",
    "llt_code": "10008469",
    "pt_name": "Chest pain",
    "pt_code": "10008479"
  },
  {
    "llt_name": "Chest tightness",
    "llt_code": "10008500",
    "pt_name": "Chest pain",
    "pt_code": "10008479"
  },
  {
    "llt_name": "Thoracic pain",
    "llt_code": "10043515",
    "pt_name": "Chest pain",
    "pt_code": "10008479"
  },
  {
    "llt_name": "Dry mouth",
    "llt_code": "10013781",
    "pt_name": "Dry mouth",
    "pt_code": "10013781"
  },
  {
    "llt_name": "Mouth dryness",
    "llt_code": "10028130",
    "pt_name": "Dry mouth",
    "pt_code": "10013781"
  },
  {
    "llt_name": "Xerostomia",
    "llt_code": "10048232",
    "pt_name": "Dry mouth",
    "pt_code": "10013781"
  },
  {
    "llt_name": "Lack of saliva",
    "llt_code": "10023479",
    "pt_name": "Dry mouth",
    "pt_code": "10013781"
  },
  {
    "llt_name": "Weight gain",
    "llt_code": "10047899",
    "pt_name": "Weight increased",
    "pt_code": "10047896"
  },
  {
    "llt_name": "Weight increase",
    "llt_code": "10047896",
    "pt_name": "Weight increased",
    "pt_code": "10047896"
  },
  {
    "llt_name": "Putting on weight",
    "llt_code": "10037406",
    "pt_name": "Weight increased",
    "pt_code": "10047896"
  },
  {
    "llt_name": "Weight loss",
    "llt_code": "10047900",
    "pt_name": "Weight decreased",
    "pt_code": "10047895"
  },
  {
    "llt_name": "Weight decrease",
    "llt_code": "10047895",
    "pt_name": "Weight decreased",
    "pt_code": "10047895"
  },
  {
    "llt_name": "Losing weight",
    "llt_code": "10024847",
    "pt_name": "Weight decreased",
    "pt_code": "10047895"
  },
  {
    "llt_name": "Blurred vision",
    "llt_code": "10005886",
    "pt_name": "Vision blurred",
    "pt_code": "10047513"
  },
  {
    "llt_name": "Vision blurred",
    "llt_code": "10047513",
    "pt_name": "Vision blurred",
    "pt_code": "10047513"
  },
  {
    "llt_name": "Fuzzy vision",
    "llt_code": "10017452",
    "pt_name": "Vision blurred",
    "pt_code": "10047513"
  }
]

# update_list = []
insert_list = []
counter = 0

for document in documents:
    text_field = document.get('llt_name')
    if text_field:
        request_result = get_embedding_voyage(text_field)
        embedding = request_result.get("data", [{}])[0].get("embedding", [])
        if embedding:
            document["embedding"] = embedding
            # Append the update operation
            insert_list.append(document)

        # Execute all updates in bulk if the list is not empty


    counter += 1
    if counter == 300:
        if insert_list:
            result = collection.insert_many(insert_list)
        counter = 0
        
result = collection.insert_many(insert_list)

# Close the connection
client.close()
