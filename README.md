
```
Role: Act as a python devloper to build a Retrieval-Augmented Generation (RAG) pipeline that works with PDF documents, using ChromaDB and LangChain, and provides a user interface via Streamlit.
🎯 Project Objective
Deliver a complete system that:
* Accepts and parses PDF files as input.
* Converts content into embeddings for vector-based retrieval.
* Stores the vector data in a suitable vector store (e.g., ChromaDB).
* Utilizes LangChain for retrieval-augmented response generation.
* Provides a functional and interactive user interface built with Streamlit.
* Includes clear and modular code, with the following documentation:
   * README.md: High-level overview and usage guide.
   * STEPS.md: Step-by-step documentation of the entire pipeline from ingestion to generation.
🚧 Development Phases
Phase One: Environment & Setup
* Initialize the project and set up a clean working environment.
* Identify and install only the tools and libraries necessary for this use case.
* Create a modular directory structure that supports separation of concerns (UI, logic, utilities, etc.).
* Prepare version control 
* use UV-astral for python env managements
Phase Two: PDF Ingestion & Vector Storage
* Implement functionality to parse PDF documents and extract clean text.
* Chunk the extracted content to optimize context for retrieval.
* Generate vector embeddings for these chunks.
* Store the vector data using a persistent and query-efficient storage backend.
✅ Assumptions must be explicitly stated if a particular embedding model or method is used.
Phase Three: RAG Pipeline Development
* Set up the retrieval pipeline using LangChain (or equivalent).
* Implement logic to retrieve relevant chunks based on user queries.
* Generate responses using language models, grounded in retrieved context.
* Ensure modular, testable, and maintainable code.
Phase Four: UI Development
* Design and implement a Streamlit interface that allows users to:
   * Upload PDF files
   * Enter natural language queries
   * View system-generated responses
* Ensure responsiveness, usability, and smooth integration with backend components.
Phase Five: Documentation & QA
* Create clear, user-friendly documentation:
   * README.md: What the project is, how to use it, and features.
   * STEPS.md: Technical breakdown of each phase and how components are connected.
* Conduct quality checks to validate:
   * End-to-end functionality
   * Usability of the UI
   * Error handling and logging
🔍 Final Notes
* ❗ No assumptions should be made unless explicitly stated.
* All architectural or tooling choices (e.g., PDF parsing library, embedding model, vector database) must be based on current technical requirements, and clearly declared in the implementation.
* Outputs should prioritize clarity, reproducibility, and real-world functionality over theoretical explanations.
* make sure to ask user for any doubt or ambiguity you have and thus helps you to thinks and judge the user requirements
```
```
📋 Project Specification Summary

LLMs: Ollama + Gemini integration
Embeddings: Default sentence-transformers (SBERT) in ChromaDB
PDFs: Simple text-only documents
Storage: ChromaDB with in-memory + local persistence options
Features: Chat history, document references, single→multiple PDF support
Scope: MVP for local development
```

# RAG Pipeline Project Structure

## Directory Structure
```
rag-pdf-pipeline/
├── README.md
├── STEPS.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── llm_handler.py
│   │   └── embedding_handler.py
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── vector_store.py
│   │   └── document_store.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py
│   │   └── text_chunker.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   └── generator.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── ui/
│   ├── __init__.py
│   ├── streamlit_app.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── file_upload.py
│   │   ├── chat_interface.py
│   │   └── settings.py
│   └── styles/
│       └── main.css
├── data/
│   ├── uploads/
│   ├── vector_db/
│   └── chat_history/
├── tests/
│   ├── __init__.py
│   ├── test_pdf_processor.py
│   ├── test_vector_store.py
│   └── test_rag_pipeline.py
└── scripts/
    ├── setup.bat
    └── run.bat
```