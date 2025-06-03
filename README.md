# MedDRA Vector Search

A vector search application for querying the Medical Dictionary for Regulatory Activities (MedDRA) using semantic similarity. This tool enables efficient retrieval of relevant medical terms and concepts through natural language queries.

## Overview

This application implements a Retrieval-Augmented Generation (RAG) system specifically designed for MedDRA data. It uses vector embeddings to perform semantic search across medical terminology, making it easier to find related terms and concepts within the MedDRA hierarchy.

## Features

- **Semantic Search**: Find relevant medical terms using natural language queries
- **Vector Embeddings**: Leverages advanced embedding models for accurate similarity matching
- **Interactive Interface**: Clean, user-friendly Streamlit web interface
- **MedDRA Integration**: Specialized for Medical Dictionary for Regulatory Activities data
- **Fast Retrieval**: Efficient vector search for quick results

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:
```bash
streamlit run rag.py
```

The application will open in your default web browser, typically at `http://localhost:8501`.

## How It Works

The system processes MedDRA dictionary data by:
1. Converting medical terms and descriptions into vector embeddings
2. Storing vectors in an efficient search index
3. Matching user queries against the vector database
4. Returning the most semantically similar medical terms

## MedDRA Dictionary

The Medical Dictionary for Regulatory Activities (MedDRA) is a rich and highly specific standardized medical terminology used for regulatory communication and evaluation of data pertaining to medicinal products for human use.

## Requirements

See `requirements.txt` for a complete list of dependencies.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your license information here]

## Support

For questions or issues, please open an issue in this repository.
