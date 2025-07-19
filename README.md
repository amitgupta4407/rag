
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

