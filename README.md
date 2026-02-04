# Bedrock RAG Chatbot API

A robust, high-performance Enterprise Knowledge Retrieval Platform designed to allow employees to query private company documents and chat with intelligent conversational AI capabilities in a manner that avoids hallucination and irrelevant context. This project features a dual-mode processing engine: a public mode for general knowledge queries using Claude 3.5 Sonnet, and a private, Retrieval-Augmented Generation (RAG) mode for context-aware analysis of uploaded documents.

---

## 🛠️ Tech Stack

-   **Runtime:** Python 3.9+
-   **Framework:** FastAPI
-   **Frontend:** React
-   **LLM Provider:** Amazon Bedrock (Anthropic Claude 3.5 Sonnet)
-   **Vector Search:** FAISS (In-Memory Vector Store)
-   **Orchestration:** LangChain
-   **Database:** SQLite (Metadata Logging)
-   **ORM:** SQLAlchemy
-   **Cloud Storage:** AWS S3
-   **PDF Processing:** pypdf

---

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.9 or higher
*   An AWS Account with access enabled for **Claude 3.5 Sonnet** and **Titan Embeddings G1**.
*   AWS CLI installed and configured.

### 2. Installation
Clone the repository and create a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment & Credential Setup
This project utilizes the AWS SDK (`boto3`), which automatically looks for credentials configured via the AWS CLI.

Run the following command and input your Access Key ID and Secret Access Key:
```bash
aws configure
```
*Region Recommendation: `us-east-1` (Virginia) or `us-west-2` (Oregon) for Bedrock availability.*

### 4. Database Initialization
The SQLite database (`chatbot_metadata.db`) and the `documents` table are automatically initialized via SQLAlchemy the first time the server is run. No manual migration scripts are required.

### 5. Running the Server
Start the development server with hot-reload enabled:
```bash
uvicorn main:app --reload
```
*Server will start on `http://127.0.0.1:8000`*

---

## 📡 Usage Patterns

### 1. Public Mode (Standard LLM)
Utilizes the direct Messages API from Anthropic to answer general knowledge questions.
*   **Latency:** Low (<1s)
*   **Context:** General Training Data

### 2. RAG Mode (Private Context)
The core feature of the platform. Users can toggle "Enable RAG Mode" to inject private data into the LLM's context window.

*   **Ingestion Pipeline:**
    1.  User uploads a PDF or selects an existing file from AWS S3.
    2.  System extracts text and splits it into 1000-character chunks (200-char overlap).
    3.  Chunks are embedded using Titan Embeddings and stored in a FAISS vector index.
    4.  Top 3 semantic matches are retrieved and injected into the System Prompt.

---

## 🏗️ Architecture & Design Decisions

### 1. Dual-Mode Logic Engine
**Why this approach?**
A key constraint was distinguishing between general queries and strict, document-based queries.
*   **Public Mode:** Utilizes the raw power of **Claude 3.5 Sonnet** via the Bedrock Messages API for unrestricted generation.
*   **Private Mode:** Enforces a strict **RAG Pipeline**. The system generates a specialized System Prompt that explicitly forbids the model from using outside knowledge, reducing hallucinations and ensuring answers are grounded solely in the uploaded PDF.

### 2. Provenance Tracking 
In RAG systems, "Hallucination" is a major risk. To mitigate this, I implemented a strict audit trail.
*   **The Schema:** A `ChatInteraction` table links to a `Document` table via an association table.
*   **The Benefit:** We do not just store the answer; we store the *provenance*. Every answer generated in RAG mode is database-linked to the specific document ID that provided the context. This allows for future auditability (e.g., "Which document led the AI to claim X?").

### 3. Context-Aware Prompt Engineering
I implemented a strict system prompt to prevent knowledge leakage from outside the document.

*   **The Problem:** LLMs tend to use their pre-trained knowledge to fill in gaps, which is dangerous when dealing with private data.
*   **The Fix:** The prompt is dynamically constructed with XML tags (`<context>...</context>`). The System Instruction explicitly states: *"If the context does not contain the answer, state that you do not have enough information."* This forces the model to admit ignorance rather than hallucinate.

---

## 🔍 Matching Logic Analysis (RAG)

During development, particular attention was paid to the "Retrieval" phase of the RAG pipeline to ensure accuracy.

| Pipeline Stage | Implementation Detail | Reasoning |
| :--- | :--- | :--- |
| **Ingestion** | `pypdf` stream reading | Direct memory stream reading prevents disk I/O bottlenecks. |
| **Splitting** | `CharacterTextSplitter` | Chunk size of 1000 chars with 200 overlap ensures context isn't lost at arbitrary cut-off points. |
| **Embedding** | `Titan Embeddings G1` | Native AWS integration provides low-latency vector generation compared to external APIs. |
| **Augmentation** | `<context>` Tags | XML tagging allows Claude to clearly distinguish between user instructions and retrieved data. |

---

## 🤖 AI Integration Details

I integrated the **Claude 3.5 Sonnet** model using the modern Anthropic Messages API format.

### 1. Prompt Engineering
To satisfy the constraint "Our chatbot should only respond based off of what was uploaded," I utilized **Negative Constraints**.

*   **The Prompt:** *"If the context does not contain the answer, say 'I do not have enough information to answer.'"*
*   **The Result:** This prevents the LLM from filling in gaps with its training data. If a user asks "What is the capital of France?" while uploading a PDF about Solar Panels, the system correctly refuses to answer.

### 2. Resilience & Error Handling
*   **Retry Logic:** Implemented `botocore.config` with `adaptive` retry mode to handle AWS `ThrottlingException` events gracefully.
*   **Input Validation:** The system validates file types (PDF only) and presence before attempting any expensive embedding operations.

---

## 🔍 System Logic Analysis

During stress testing, I evaluated the RAG system's ability to switch contexts and handle ambiguity.

| Scenario | Input Type | Logic Path | Outcome |
| :--- | :--- | :--- | :--- |
| **General Query** | "What is the capital of France?" | **Public Mode** -> Bedrock Direct Invocation | Returns "Paris" (General Knowledge) |
| **Specific Query** | "What is the deductible in this policy?" | **RAG Mode** -> PDF Upload -> FAISS Search -> Context Injection | Returns exact value from PDF |
| **Out of Context** | "Who won the 1998 World Cup?" (Inside a Medical PDF) | **RAG Mode** -> FAISS Search (Low Similarity) -> Strict Prompt | Returns "I do not have enough information in the provided text." |
| **S3 Retrieval** | Select file from Sidebar | **S3 Mode** -> Boto3 `get_object` -> Stream to Memory -> RAG | Zero-latency download; treated as local stream |

---

<div align="center">

## Thank You!
Aarya Vijayaraghavan

</div>
```