import boto3
import json
from pypdf import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import BedrockEmbeddings

# Initialize the Bedrock client. This will be used to create embeddings
# and to invoke the LLM for the final answer generation.
bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
bedrock_embeddings_client = BedrockEmbeddings(client=bedrock_client)

def perform_rag(question: str, file_stream):
    """
    Performs entire RAG process on given PDF file stream.
    1. Reads and extracts text from the PDF.
    2. Splits the text into smaller, manageable chunks.
    3. Converts these chunks into numerical vectors (embeddings) and stores them.
    4. Finds the most relevant chunks based on the user's question.
    5. Feeds the question and relevant chunks to my LLM to generate an answer.
    """
    # 1. Read and Extract
    print("Step 1: Reading PDF content...")
    pdf_reader = PdfReader(file_stream)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    if not text:
        return "Could not extract text from the PDF. The document might be empty or unscannable."

    # 2. Split
    # We split because LLMs have limited context windows (the amount of text they
    # can look at at once), so we break the document into smaller pieces.

    print("Step 2: Splitting text into chunks...")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,  # Max size of each chunk
        chunk_overlap=200, # Overlap helps maintain context between chunks
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # 3. Embed and Store
    # This is where we create the Vector Database in memory.
    # `BedrockEmbeddings` converts each text chunk into a vector.
    # `FAISS.from_texts` stores these vectors for efficient searching.
    print("Step 3: Creating vector store from text chunks...")
    vector_store = FAISS.from_texts(chunks, bedrock_embeddings_client)
    print("Vector store created successfully.")
    
    print("Step 4: Performing similarity search...")
    docs = vector_store.similarity_search(question, k=3) # Retrieve the top 3 most relevant chunks

    # 4. Retrieve
    # This performs a semantic search. It finds the text chunks whose meaning is closest to the meaning of the user's question

    # This is the retrieved context from the RAG
    context = " ".join([doc.page_content for doc in docs]) # Find this

    # 4. Generate (with Messages API for Claude 3.5 Sonnet)
    # This is the "Augmented" part of RAG. We create a new, detailed prompt
    # that gives the LLM clear instructions and the retrieved context.
    print("Step 5: Invoking model with augmented prompt...")

    # The System Prompt gives the LLM its persona and core instructions.
    # This is critical for forcing it to use only the provided context.
    system_prompt = """You are a helpful chatbot. Based ONLY on the following context, please answer the user's question. If the context does not contain the answer, state that you do not have enough information to answer."""

    # We combine the retrieved context and the original question in the user's message.
    user_message_content = f"<context>\n{context}\n</context>\n\nQuestion: {question}"

     # We build the request body according to the Messages API specification.
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31", # Required for Messages API
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_message_content}]
            }
        ]
    })

    try:
        response = bedrock_client.invoke_model(
            body=body,
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            accept="application/json",
            contentType="application/json",
        )
        
        response_body = json.loads(response.get('body').read())
        # The answer is inside the 'content' block.
        completion = response_body['content'][0]['text']
        
        return completion

    except Exception as e:
        print(f"Error invoking model: {e}")
        return "There was an error generating the response."