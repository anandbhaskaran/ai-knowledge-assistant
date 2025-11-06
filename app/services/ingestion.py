import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import glob

from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline

from app.services.retriever import get_global_index, clear_collection
from app.core.config import settings

# Get logger
logger = logging.getLogger(__name__)

def extract_date_from_file(file_path: str) -> str:
    """
    Extract date from filename or metadata

    This is a simplified version - in a production system, you might
    extract dates from file metadata or content

    Args:
        file_path: Path to the file

    Returns:
        Formatted date string (YYYY-MM-DD)
    """
    # For demonstration, we'll use file modification time
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except Exception:
        # Default to today if we can't get the date
        return datetime.now().strftime("%Y-%m-%d")

def extract_metadata_from_file(file_path: str) -> Dict[str, Any]:
    """
    Extract basic metadata from a file

    Args:
        file_path: Path to the file

    Returns:
        Dictionary of metadata
    """
    basename = os.path.basename(file_path)
    title = os.path.splitext(basename)[0].replace("_", " ").title()
    date = extract_date_from_file(file_path)

    return {
        "source": basename,
        "title": title,
        "date": date,
        "file_path": file_path
    }

def get_file_content(file_path: str) -> str:
    """
    Read and return file content as text

    Args:
        file_path: Path to the file

    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.warning(f"Could not read file content from {file_path}: {e}")
        return ""


def extract_simple_metadata(file_path: str, content: str) -> Dict[str, Any]:
    """
    Extract minimal metadata from a file and its content.

    Args:
        file_path: Path to the file
        content: Text content of the file

    Returns:
        Dictionary of simple metadata
    """
    # Basic metadata
    basename = os.path.basename(file_path)
    file_date = extract_date_from_file(file_path)
    title = os.path.splitext(basename)[0].replace("_", " ").title()

    # Get content length for basic metrics
    word_count = len(content.split())

    # Simplified metadata
    metadata = {
        "source": basename,
        "title": title,
        "date": file_date,
        "file_path": file_path,
        "word_count": word_count
    }

    return metadata

def ingest_articles(directory_path: str, recursive: bool = True, clear_data: bool = False) -> bool:
    """
    Ingest articles from a directory into the vector store

    Args:
        directory_path: Path to directory containing articles
        recursive: Whether to recursively search for files
        clear_data: Whether to clear existing data before ingestion

    Returns:
        True if ingestion was successful, False otherwise
    """
    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return False

    # Clear existing data if requested
    if clear_data:
        logger.info("Clearing existing vector store data before ingestion")
        clear_collection()

    try:
        # Load documents from directory
        documents = SimpleDirectoryReader(
            directory_path,
            recursive=recursive
        ).load_data()

        if not documents:
            logger.warning(f"No documents found in {directory_path}")
            return False

        logger.info(f"Loaded {len(documents)} documents from {directory_path}")

        # Create node parser for text splitting
        node_parser = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=200
        )

        # Process documents
        for doc in documents:
            file_path = doc.metadata.get("file_path", "unknown")

            # Get document content
            content = doc.get_content()

            # Extract simplified metadata
            metadata = extract_simple_metadata(file_path, content)

            # Log metadata extraction
            logger.info(f"Simple metadata extracted for {os.path.basename(file_path)}: {len(metadata)} attributes")

            # Update document metadata
            doc.metadata.update(metadata)

        # Create ingestion pipeline
        pipeline = IngestionPipeline(
            transformations=[node_parser]
        )

        # Process documents
        nodes = pipeline.run(documents=documents)

        # Get index and insert nodes
        index = get_global_index()
        index.insert_nodes(nodes)

        logger.info(f"Successfully ingested {len(documents)} documents")
        return True
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        return False

def ingest_file(file_path: str, clear_data: bool = False) -> bool:
    """
    Ingest a single file into the vector store

    Args:
        file_path: Path to the file
        clear_data: Whether to clear existing data before ingestion

    Returns:
        True if ingestion was successful, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    # Clear existing data if requested
    if clear_data:
        logger.info("Clearing existing vector store data before ingestion")
        clear_collection()

    try:
        # Create directory containing the file
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Load document
        documents = SimpleDirectoryReader(
            directory,
            filename_as_id=True,
            file_extractor=None,
            required_exts=[os.path.splitext(filename)[1][1:]],  # Extension without dot
        ).load_data()

        if not documents:
            logger.warning(f"No documents loaded from {file_path}")
            return False

        logger.info(f"Loaded document from {file_path}")

        # Create node parser for text splitting
        node_parser = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=200
        )

        # Process document
        for doc in documents:
            # Get document content
            content = doc.get_content()

            # Extract simplified metadata
            metadata = extract_simple_metadata(file_path, content)

            # Log metadata extraction
            logger.info(f"Simple metadata extracted for {os.path.basename(file_path)}: {len(metadata)} attributes")

            # Update document metadata
            doc.metadata.update(metadata)

        # Create ingestion pipeline
        pipeline = IngestionPipeline(
            transformations=[node_parser]
        )

        # Process document
        nodes = pipeline.run(documents=documents)

        # Get index and insert nodes
        index = get_global_index()
        index.insert_nodes(nodes)

        logger.info(f"Successfully ingested {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error ingesting file {file_path}: {e}")
        return False

# CLI entry point
def main():
    """CLI entry point for ingestion"""
    import argparse

    parser = argparse.ArgumentParser(description="Ingest articles into the vector store")
    parser.add_argument("path", help="Path to file or directory to ingest")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recursively process directories")
    parser.add_argument("--clear", "-c", action="store_true", help="Clear existing data before ingestion")

    args = parser.parse_args()

    # Check if path is a file or directory
    if os.path.isfile(args.path):
        success = ingest_file(args.path, clear_data=args.clear)
    elif os.path.isdir(args.path):
        success = ingest_articles(args.path, args.recursive, clear_data=args.clear)
    else:
        logger.error(f"Path not found: {args.path}")
        success = False

    if success:
        logger.info("Ingestion completed successfully")
    else:
        logger.error("Ingestion failed")

if __name__ == "__main__":
    main()