import streamlit as st
import streamlit.components.v1 as components
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from google.cloud import bigquery
from vertexai.generative_models import (
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)


def query_bigquery(query, location='asia-south1'):
    CREDS = r'path/to/credentials.json'
    client = bigquery.Client.from_service_account_json(json_credentials_path=CREDS)
    job = client.query(query).to_dataframe()
    # print(job)
    
    return job

def single_turn_gemini(prompt):
    vertexai.init(project="your-project", location="your-region")
    model = GenerativeModel(
        "gemini-1.5-flash-001"
    )
    response = model.generate_content(prompt)

class GeminiChat:
    
    def __init__(self):
        vertexai.init(project="your-project", location="your-region")
        self.model = GenerativeModel(
            "gemini-1.5-flash-001"
        )
        self.chat = None
        self.mime_type = "application/pdf"
        self.document1 = Part.from_uri(
        mime_type="application/pdf",
        uri="gs://URI_TO_PDF")
        self.generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0,
        "top_p": 0.95,
        }

        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        self.chat = self.model.start_chat()

    def startNewChat(self):
        self.chat = self.model.start_chat()

    def convertToQuery(self, prompt):
        text1 = f"""Refer the above pdf and create a bigquery query that shows {prompt}
        Other Details:
        Project ID = your-project
        Dataset ID = your-dataset

        Think step by step. """

        return self.chat.send_message(
        [self.document1, text1],
        generation_config=self.generation_config,
        safety_settings=self.safety_settings
        )
    
    def askGemini(self, prompt):
        return self.model.generate_content(
        [self.document1, prompt],
        generation_config=self.generation_config,
        safety_settings=self.safety_settings
        )
    
    def askGeminiChat(self, prompt):
        return self.chat.send_message(
        [self.document1, prompt],
        generation_config=self.generation_config,
        safety_settings=self.safety_settings
        )
