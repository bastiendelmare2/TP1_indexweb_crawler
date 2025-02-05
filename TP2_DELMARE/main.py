from indexer import Indexer

# Configuration
INPUT_FILE = "input/products.jsonl"
FILTERED_FILE = "filtered_products.jsonl"
INDEX_FOLDER = "indexs"

# Create an instance of Indexer
indexer = Indexer(INPUT_FILE, FILTERED_FILE, INDEX_FOLDER)

# Execute the pipeline
indexer.execute_pipeline()