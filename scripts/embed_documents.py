#!/usr/bin/env python3
"""Document embedding script for Elasticsearch.

This script reads documents from a directory and embeds them into Elasticsearch
using Ollama embeddings.

Usage:
    python scripts/embed_documents.py <directory_path>
    python scripts/embed_documents.py <directory_path> --recursive
    python scripts/embed_documents.py <directory_path> --pattern "*.md"
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_elasticsearch import ElasticsearchStore
from langchain_core.documents import Document
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

from src.config.config import Config
from src.utils.docker import ensure_elasticsearch_running

console = Console()


def load_documents(directory: Path, pattern: str = "*.*", recursive: bool = False) -> List[Document]:
    """Load documents from directory.

    Args:
        directory: Directory containing documents
        pattern: File pattern to match (e.g., "*.md", "*.txt")
        recursive: Whether to search subdirectories

    Returns:
        List of loaded documents
    """
    documents = []
    glob_pattern = f"**/{pattern}" if recursive else pattern

    for file_path in directory.glob(glob_pattern):
        if not file_path.is_file():
            continue

        try:
            # Determine loader based on file extension
            suffix = file_path.suffix.lower()

            if suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
            elif suffix in [".docx", ".doc"]:
                loader = Docx2txtLoader(str(file_path))
            elif suffix in [".md", ".markdown", ".txt", ".text", ".py", ".js", ".ts", ".java", ".go"]:
                # Use TextLoader for text-based files
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                # Try as text file with error handling
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                except UnicodeDecodeError:
                    console.print(f"✗ Skipping binary file: {file_path.name}", style="yellow")
                    continue

            docs = loader.load()

            # Add metadata
            for doc in docs:
                doc.metadata["source"] = str(file_path)
                doc.metadata["filename"] = file_path.name

            documents.extend(docs)
            console.print(f"✓ Loaded: [cyan]{file_path.name}[/cyan]")

        except Exception as e:
            console.print(f"✗ Failed to load {file_path.name}: {e}", style="yellow")

    return documents


def split_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Split documents into chunks.

    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks

    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_documents(documents)


def embed_documents(
    documents: List[Document],
    index_name: str,
    batch_size: int = 50
) -> None:
    """Embed documents into Elasticsearch.

    Args:
        documents: List of documents to embed
        index_name: Elasticsearch index name
        batch_size: Number of documents to process at once
    """
    # Initialize embeddings with dedicated embedding model
    console.print("\n🔧 Initializing embedding model...", style="cyan")
    start_init = time.time()

    embeddings = OllamaEmbeddings(
        model=Config.OLLAMA_EMBEDDING_MODEL,
        base_url=Config.OLLAMA_BASE_URL
    )

    init_time = time.time() - start_init
    console.print(f"✓ Model initialized in {init_time:.2f}s", style="green")

    # Initialize Elasticsearch store
    console.print("🔧 Connecting to Elasticsearch...", style="cyan")
    vector_store = ElasticsearchStore(
        es_url=Config.ELASTICSEARCH_URL,
        index_name=index_name,
        embedding=embeddings,
    )
    console.print("✓ Connected to Elasticsearch", style="green")

    # Embed documents in batches
    total_docs = len(documents)
    total_batches = (total_docs + batch_size - 1) // batch_size

    console.print(f"\n📝 Embedding {total_docs} document chunks in {total_batches} batches...")
    console.print(f"   Batch size: {batch_size} documents")
    console.print()

    start_time = time.time()
    successful_docs = 0
    failed_batches = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[cyan]Processing batches...",
            total=total_docs
        )

        for batch_idx in range(0, total_docs, batch_size):
            batch_num = (batch_idx // batch_size) + 1
            batch = documents[batch_idx:batch_idx + batch_size]
            batch_start = time.time()

            try:
                # Update progress description with current batch
                progress.update(
                    task,
                    description=f"[cyan]Batch {batch_num}/{total_batches} ({len(batch)} docs)"
                )

                vector_store.add_documents(batch)

                batch_time = time.time() - batch_start
                successful_docs += len(batch)

                # Calculate speed
                docs_per_sec = len(batch) / batch_time if batch_time > 0 else 0

                progress.update(task, advance=len(batch))

                # Log batch completion
                console.print(
                    f"  ✓ Batch {batch_num}/{total_batches}: "
                    f"{len(batch)} docs in {batch_time:.2f}s "
                    f"({docs_per_sec:.1f} docs/s)",
                    style="dim"
                )

            except Exception as e:
                batch_time = time.time() - batch_start
                failed_batches.append((batch_num, str(e)))

                console.print(
                    f"\n  ✗ Batch {batch_num}/{total_batches} failed after {batch_time:.2f}s: {e}",
                    style="red"
                )
                console.print(f"     Batch range: {batch_idx} to {batch_idx + len(batch)}")

                # Ask user if they want to continue
                response = console.input("\n  Continue with next batch? [y/N]: ")
                if response.lower() != 'y':
                    raise

    elapsed_time = time.time() - start_time
    avg_speed = successful_docs / elapsed_time if elapsed_time > 0 else 0

    # Print summary
    console.print("\n" + "="*60, style="cyan")
    console.print("📊 Embedding Summary", style="bold cyan")
    console.print("="*60, style="cyan")

    table = Table(show_header=False, box=None)
    table.add_column("Label", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Total documents", str(total_docs))
    table.add_row("Successfully embedded", f"{successful_docs} ({successful_docs/total_docs*100:.1f}%)")
    table.add_row("Failed batches", str(len(failed_batches)))
    table.add_row("Total time", f"{elapsed_time:.2f}s")
    table.add_row("Average speed", f"{avg_speed:.2f} docs/s")

    console.print(table)

    if failed_batches:
        console.print("\n⚠️  Failed batches:", style="yellow")
        for batch_num, error in failed_batches:
            console.print(f"  - Batch {batch_num}: {error}", style="yellow")

    if successful_docs == total_docs:
        console.print("\n✅ All documents embedded successfully!", style="bold green")
    elif successful_docs > 0:
        console.print(f"\n⚠️  Partial success: {successful_docs}/{total_docs} documents embedded", style="yellow")
    else:
        console.print("\n❌ No documents were embedded", style="bold red")
        raise Exception("Embedding failed completely")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Embed documents into Elasticsearch using Ollama"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing documents"
    )
    parser.add_argument(
        "--pattern",
        default="*.*",
        help="File pattern to match (default: *.*)"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Search subdirectories recursively"
    )
    parser.add_argument(
        "--index",
        default=Config.ELASTICSEARCH_INDEX,
        help=f"Elasticsearch index name (default: {Config.ELASTICSEARCH_INDEX})"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size for splitting documents (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for embedding (default: 50)"
    )

    args = parser.parse_args()

    # Validate directory
    if not args.directory.exists():
        console.print(f"❌ Directory not found: {args.directory}", style="bold red")
        sys.exit(1)

    if not args.directory.is_dir():
        console.print(f"❌ Not a directory: {args.directory}", style="bold red")
        sys.exit(1)

    # Display configuration
    console.print("\n[bold cyan]Document Embedding Configuration[/bold cyan]")
    console.print(f"  Directory: {args.directory}")
    console.print(f"  Pattern: {args.pattern}")
    console.print(f"  Recursive: {args.recursive}")
    console.print(f"  Index: {args.index}")
    console.print(f"  Chunk Size: {args.chunk_size}")
    console.print(f"  Chunk Overlap: {args.chunk_overlap}")
    console.print(f"  Ollama Embedding Model: {Config.OLLAMA_EMBEDDING_MODEL}")
    console.print()

    try:
        # Ensure Elasticsearch is running
        console.print("🐳 Checking Elasticsearch...")
        if not ensure_elasticsearch_running():
            console.print("❌ Failed to start Elasticsearch", style="bold red")
            sys.exit(1)

        # Load documents
        console.print("\n📂 Loading documents...")
        documents = load_documents(args.directory, args.pattern, args.recursive)

        if not documents:
            console.print("⚠️  No documents found", style="yellow")
            sys.exit(0)

        console.print(f"\n✓ Loaded {len(documents)} documents")

        # Split documents
        console.print("\n✂️  Splitting documents into chunks...")
        chunks = split_documents(
            documents,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )
        console.print(f"✓ Created {len(chunks)} chunks")

        # Embed documents
        embed_documents(chunks, args.index, args.batch_size)

        console.print("\n🎉 Done!", style="bold green")

    except KeyboardInterrupt:
        console.print("\n\n⚠️  Interrupted by user", style="yellow")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
