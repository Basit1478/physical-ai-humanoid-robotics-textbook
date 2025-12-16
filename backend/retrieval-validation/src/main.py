"""
Main entry point for the retrieval validation service
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .cli_harness import cli


def main():
    """
    Main function to run the retrieval validation service.
    """
    # Run the CLI
    cli()


if __name__ == "__main__":
    main()