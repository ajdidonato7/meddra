import os
import openai
from dotenv import load_dotenv
import pymongo
import pprint
import boto3
import json
import requests

load_dotenv()
aws_access_key_id = 'TODO - AWS ACCESS KEY ID'
aws_secret_access_key = 'TODO - AWS SECRET KEY'
aws_session_token = "TODO - AWS SESSION TOKEN"
openai.api_key = "TODO - OPENAI API KEY"


def get_embedding_from_openai(text, model="text-embedding-3-small"):

    response = openai.embeddings.create(
        model=model,
        input=text,
        encoding_format="float"
    )

    embedding = response.data[0].embedding
    return embedding

def get_embedding_from_titan(input_text):
    try:
        # Initialize the Bedrock client
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name="us-east-1",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )

        # Prepare the request body
        request_body = {}
        if input_text:
            request_body["inputText"] = input_text
        # request_body["embeddingConfig"] = {"outputEmbeddingLength": 1024}

        body = json.dumps(request_body)

        # Invoke the model
        response = bedrock.invoke_model(
            body=body,
            modelId="amazon.titan-embed-text-v2:0",
            accept="application/json",
            contentType="application/json"
        )

        # Parse the response
        response_body = json.loads(response.get('body').read())
        embedding = response_body.get("embedding")
        return embedding
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def get_embedding_from_voyage(input_text):

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

def main():

    text_to_embed = "what are the races in texas district 11?"
    print(f"Generating embedding for: '{text_to_embed}'")
    
    try:
        embedding = get_embedding_from_voyage(text_to_embed)
        embedding = embedding.get("data", [{}])[0].get("embedding", [])
        client = pymongo.MongoClient("TODO - MONGODB CONNECTION STRING")
        db = client["TODO - DATABASE NAME"]
        collection = db["TODO - COLLECTION NAME"]

        results = collection.aggregate(
            [
                {
                    '$vectorSearch': {
                        'queryVector': embedding,
                        'path': 'voyage-3-large',
                        # 'path': 'openai-text-3',
                        # 'path': 'BSON-Float32-Embedding',
                        'numCandidates': 5,
                        # 'index': 'elect',
                        # 'index': 'elect-openai',
                        'index': 'elect-voyage',
                        'limit': 5
                    }
                },
                {
                    '$project': {
                        'embedding_text': 1,
                    }
                }
            ]
        )
        list_results = list(results)
        for result in list_results:
            pprint.pprint(result)

        
    except Exception as e:
        print(f"Error generating embedding: {e}")

if __name__ == "__main__":
    main()