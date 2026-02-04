# # Import the FastAPI class
# from fastapi import FastAPI

import boto3
import json
from pydantic import BaseModel

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Import our new RAG handler function
from rag_handler import perform_rag

# Configuration
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
AWS_REGION = "us-east-1"

# Pydantic (Data validation library) Model for input
class ChatRequest(BaseModel):
    # This defines the structure of the request body for our /chat endpoint
    question: str

    # "private" is our flag to switch between RAG (private) and public mode
    private: bool = False

# Create an instance of the FastAPI class.. app will be the main point of interaction for our entire application
app = FastAPI(
    title="Bedrock Chatbot API",
    description="An API for a chatbot powered by Amazon Bedrock.",
    version="0.1.0",
)

# New from front-end connection
origins = [
    "http://localhost:3000", # The default URL for a React app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

# Initialize the Boto3 client for Bedrock that will communicate with AWS, We do this once when the app starts up.
# Boto3 will automatically find and use the credentials you set up
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION
)

# Define a "path operation" or "route"
@app.get("/")
async def root():
    # This is the function that runs when a request comes to "/"
    return {"message": "Hello! The Chatbot API is running."}


@app.post("/chat")
async def chat_handler(
    # Instead of a JSON body, we now expect form fields.
    # This is necessary for handling file uploads alongside data.
    question: str = Form(...), 
    private: bool = Form(...),
    # UploadFile is a special FastAPI type for files. We default it to None
    # so it's not required for public mode.
    file: UploadFile = File(None) 
):
    if private:
        # --- Private Mode (RAG) ---
        if file is None:
            return {"error": "A PDF file is required for private mode."}
        
        if file.content_type != 'application/pdf':
            return {"error": "Only PDF files are allowed in private mode."}
        
        # 'file.file' gives us a file-like stream object, which is what
        # our rag_handler's PdfReader needs.
        response = perform_rag(question, file.file)
        return {"response": response}
    else:
        # --- Public Mode (using Messages API) ---
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            })

            response = bedrock_client.invoke_model(
                body=body,
                modelId= MODEL_ID,
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = json.loads(response.get('body').read())
            completion = response_body['content'][0]['text']
            
            return {"response": completion}

        except Exception as e:
            return {"error": str(e)}