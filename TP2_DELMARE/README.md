# Indexer 📚

This project is an indexing tool designed to process JSONL files containing product information, extract relevant data (such as product ID, variant, reviews, etc.), and build indexes to facilitate search and analysis. The indexes are saved as JSON files for future use.
## Features 🌟

### Features of the Indexing Tool

- **Extraction of Information from URLs**: The program extracts the product ID and variant from product URLs.
- **Indexing Titles and Descriptions**: Creates inverted indexes with positions for product titles and descriptions.
- **Indexing Reviews**: Aggregates information about product reviews (total number of reviews, average rating, last rating).
- **Indexing Features**: Creates indexes for specific product attributes (brand, origin, flavor, container).
- **Saving Indexes**: The indexes are saved as JSON files for future use.

### Python Files  🐍

### Project Structure

- **`indexer.py`**: Contains the `Indexer` class, which implements the indexing logic.

- **`main.py`**: Entry point of the program, utilizes the `Indexer` class to execute the indexing pipeline.

## Implementation Choices 🛠️

The project was designed to offer efficient indexing for product data, focusing on enabling fast and relevant search results. Below are some of the key implementation decisions:

### 1. **Text Tokenization and Stopwords Removal**
   - **Why**: By tokenizing the text and removing common stopwords, we can reduce noise in the data and focus on the relevant terms. This ensures that the indexed data is more precise and search queries can be matched with higher accuracy.
   - **How**: The `tokenize_text` function processes the text by converting it to lowercase, removing punctuation, and filtering out stopwords. This results in a list of relevant tokens that will be used in the indexing process.

### 2. **Inverted Index for Titles and Descriptions**
   - **Why**: Titles and descriptions are essential components when users search for products. An inverted index allows for quick lookup of terms within these fields, enhancing search performance.
   - **How**: The `create_inverted_index_with_positions` function creates an index of tokens from the product titles and descriptions, along with their positions in the text. This makes it possible to perform full-text search and support ranked search results.

### 3. **Product Reviews Indexing**
   - **Why**: Reviews are crucial for assessing product quality. Indexing them allows users to filter or sort products based on review counts, average ratings, or the most recent ratings.
   - **How**: The `create_reviews_index` function aggregates review data such as the total number of reviews, the average rating, and the last rating, enabling the search engine to display products based on review metrics.

### 4. **Feature-Specific Indexing (e.g., Brand, Origin, Flavor, Container)**
   - **Why**: Product features such as brand, origin, and flavor are usefull for customers when filtering products. Creating separate indexes for these attributes allows users to perform targeted searches.
   - **How**: The `create_feature_index` function builds an inverted index for specific features. This way, when users search for a product by its features, the search engine can quickly identify and return relevant results.

### 5. **URL Parsing for Product Details**
   - **Why**: Extracting the product ID and variant directly from the URL ensures that each product is uniquely identifiable, which is crucial for precise indexing and searching.
   - **How**: The `extract_product_details_from_url` function uses regular expressions and URL parsing to extract the product ID and variant from the URL, enriching the data with these important details.

## Running the Code 🚀

To run the indexing tool, follow these steps:

### Prerequisites
Ensure that Python 3.x is installed on your machine. You will also need the following Python libraries:
- `json`
- `os`
- `re`
- `string`
- `collections`

You can install any missing libraries by running:
```bash
pip install -r requirements.txt
```

### Run the indexing pipeline:

```bash
python main.py
```

## Output 📂

The indexes will be saved in the `indexs/` directory (or your chosen folder) as JSON files such as:

- `index_title.json`
- `index_description.json`
- `index_reviews.json`
- `index_brand.json`
- `index_made_in.json`
- `index_flavor.json`
- `index_container.json`

With these indexes, you can efficiently search and analyze product data based on various attributes.


## Testing the Indexer Features 🧪

The `if __name__ == "__main__"` block in the code of indexer.py demonstrates the key functionalities of the indexer through various examples. This block serves as a simple test suite to verify that the indexing features work as expected. To execute it, just write on the terminal : 

```bash
python indexer.py
```