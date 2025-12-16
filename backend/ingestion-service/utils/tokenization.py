"""
Tokenization utilities for the ingestion service
"""
import tiktoken
from typing import List, Tuple
import re


def count_tokens(text: str, model_name: str = "gemini-2.5-flash") -> int:
    """
    Count the number of tokens in a text using tiktoken.
    """
    try:
        # Try to get the encoding for the specific model
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # Fallback to cl100k_base encoding (used by gpt-3.5-turbo and gpt-4)
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def chunk_text(text: str, min_tokens: int = 500, max_tokens: int = 1200, overlap: int = 100) -> List[dict]:
    """
    Split text into chunks based on token count with overlap.

    Args:
        text: Input text to chunk
        min_tokens: Minimum tokens per chunk
        max_tokens: Maximum tokens per chunk
        overlap: Number of tokens to overlap between chunks

    Returns:
        List of dictionaries containing chunk text and metadata
    """
    if not text.strip():
        return []

    # Split text into sentences to maintain semantic boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)

    if len(sentences) == 1 and len(sentences[0]) < 100:
        # If it's a very short text, just return it as one chunk
        return [{
            'text': text,
            'token_count': count_tokens(text),
            'start_pos': 0,
            'end_pos': len(text)
        }]

    chunks = []
    current_chunk = ""
    current_token_count = 0
    start_pos = 0

    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        sentence_token_count = count_tokens(sentence)

        # If adding this sentence would exceed max_tokens
        if current_token_count + sentence_token_count > max_tokens and current_chunk:
            # Save the current chunk
            chunks.append({
                'text': current_chunk.strip(),
                'token_count': current_token_count,
                'start_pos': start_pos,
                'end_pos': start_pos + len(current_chunk)
            })

            # Start a new chunk with overlap
            if overlap > 0:
                # Find previous text to include as overlap
                overlap_text = _get_overlap_text(chunks, overlap)
                current_chunk = overlap_text + sentence + " "
                current_token_count = count_tokens(overlap_text) + sentence_token_count
                start_pos = start_pos + len(chunks[-1]['text']) - len(overlap_text)
            else:
                current_chunk = sentence + " "
                current_token_count = sentence_token_count
                start_pos = start_pos + len(chunks[-1]['text']) + 1

            i += 1
        else:
            # Add sentence to current chunk
            current_chunk += sentence + " "
            current_token_count += sentence_token_count
            i += 1

            # If we've reached a reasonable chunk size, save it
            if current_token_count >= min_tokens and i < len(sentences):
                # Check if adding next sentence would exceed max_tokens
                if i < len(sentences):
                    next_sentence_token_count = count_tokens(sentences[i])
                    if current_token_count + next_sentence_token_count > max_tokens:
                        # Save current chunk
                        chunks.append({
                            'text': current_chunk.strip(),
                            'token_count': current_token_count,
                            'start_pos': start_pos,
                            'end_pos': start_pos + len(current_chunk)
                        })

                        # Start new chunk with overlap
                        if overlap > 0:
                            overlap_text = _get_overlap_text(chunks, overlap)
                            current_chunk = overlap_text
                            current_token_count = count_tokens(overlap_text)
                            start_pos = start_pos + len(chunks[-1]['text']) - len(overlap_text)
                        else:
                            current_chunk = ""
                            current_token_count = 0
                            start_pos = start_pos + len(chunks[-1]['text']) + 1

    # Add the final chunk if it has content
    if current_chunk.strip():
        chunks.append({
            'text': current_chunk.strip(),
            'token_count': current_token_count,
            'start_pos': start_pos,
            'end_pos': start_pos + len(current_chunk)
        })

    return chunks


def _get_overlap_text(chunks: List[dict], overlap_tokens: int) -> str:
    """
    Get text from the end of previous chunks for overlap.
    """
    if not chunks:
        return ""

    last_chunk = chunks[-1]['text']
    last_chunk_tokens = count_tokens(last_chunk)

    if last_chunk_tokens <= overlap_tokens:
        return last_chunk + " "

    # We need to find the text that represents approximately overlap_tokens
    # from the end of the last chunk
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(last_chunk)

    # Take the last overlap_tokens tokens
    overlap_tokens_list = tokens[-overlap_tokens:]
    overlap_text = encoding.decode(overlap_tokens_list)

    return overlap_text + " "


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and normalizing.
    """
    if not text:
        return ""

    # Remove extra whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = text.strip()

    return text