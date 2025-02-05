import json
import math
import re
import os
import string
from datetime import datetime
from typing import Dict, List, Set, Tuple
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
# STOPWORDS
STOPWORDS = stopwords.words("english")

class ProductSearchEngine:
    def __init__(self, index_directory: str = "indexs/"):
        """Initialize the search engine by loading required indexes and product data."""
        # Load all indexes from the specified directory
        with open(f"{index_directory}brand_index.json", "r") as f:
            self.brand_index = json.load(f)
        with open(f"{index_directory}description_index.json", "r") as f:
            self.description_index = json.load(f)
        with open(f"{index_directory}domain_index.json", "r") as f:
            self.domain_index = json.load(f)
        with open(f"{index_directory}origin_index.json", "r") as f:
            self.origin_index = json.load(f)
        with open(f"data/origin_synonyms.json", "r") as f:
            self.origin_synonyms = json.load(f)
        with open(f"{index_directory}reviews_index.json", "r") as f:
            self.reviews_index = json.load(f)
        with open(f"{index_directory}title_index.json", "r") as f:
            self.title_index = json.load(f)

        # Load product data
        self.products = {}
        with open(f"data/rearranged_products.jsonl", "r") as f:
            for line in f:
                product = json.loads(line)
                self.products[product["url"]] = product

        # Create a directory to store search results if it doesn't exist
        base_path = os.path.dirname(index_directory.rstrip('/'))
        self.results_directory = os.path.join(base_path, "search_results")
        os.makedirs(self.results_directory, exist_ok=True)

    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess the text by removing punctuation, replacing synonyms, and removing stopwords."""
        if not text:
            return []

        # Convert to lowercase and remove punctuation
        text = text.lower().translate(str.maketrans('', '', string.punctuation))

        # Replace words with their synonyms
        tokens = []
        for word in text.split():
            # Replace synonyms with the main term
            for main_term, synonyms in self.origin_synonyms.items():
                if word in synonyms or word == main_term:
                    word = main_term
                    break
            tokens.append(word)

        # Remove stopwords
        tokens = [word for word in tokens if word not in STOPWORDS]

        return tokens

    def enrich_query_with_origin_synonyms(self, query_tokens: List[str]) -> List[str]:
        """Enhance query tokens with origin synonyms."""
        enriched_tokens = query_tokens.copy()
        for country, synonyms in self.origin_synonyms.items():
            if country in query_tokens:
                enriched_tokens.extend(synonyms)
            for synonym in synonyms:
                if synonym in query_tokens:
                    enriched_tokens.append(country)
                    enriched_tokens.extend(
                        [s for s in synonyms if s != synonym])
        return list(set(enriched_tokens))

    def filter_documents_by_any_token(self, query_tokens: List[str]) -> Set[str]:
        """Filter documents that contain at least one of the query tokens."""
        matching_documents = set()

        for token in query_tokens:
            # Check all indexes for the token
            if token in self.title_index:
                matching_documents.update(self.title_index[token].keys())
            if token in self.description_index:
                matching_documents.update(self.description_index[token].keys())
            if token in self.brand_index:
                matching_documents.update(self.brand_index[token])
            if token in self.origin_index:
                matching_documents.update(self.origin_index[token])

        return matching_documents

    def filter_documents_by_all_tokens(self, query_tokens: List[str]) -> Set[str]:
        """Filter documents that contain all query tokens."""
        if not query_tokens:
            return set()

        matching_documents = self.filter_documents_by_any_token([query_tokens[0]])

        for token in query_tokens[1:]:
            token_documents = self.filter_documents_by_any_token([token])
            matching_documents.intersection_update(token_documents)

        return matching_documents

    def exact_match_search(self, query: str) -> Set[str]:
        """Search for documents with an exact match to the query."""
        normalized_query = query.lower().strip()
        matching_documents = set()

        for doc_url, product in self.products.items():
            # Title match
            if normalized_query == product['title'].lower().strip():
                matching_documents.add(doc_url)
            # Brand match
            if 'brand' in product and normalized_query == product['brand'].lower().strip():
                matching_documents.add(doc_url)
            # Origin match
            if 'product_features' in product and 'made in' in product['product_features']:
                if normalized_query == product['product_features']['made in'].lower().strip():
                    matching_documents.add(doc_url)

        return matching_documents

    def calculate_bm25_score(self, doc_url: str, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> float:
        """Calculate BM25 score for a given document."""
        score = 0
        doc = self.products[doc_url]
        doc_text = f"{doc['title']} {doc['description']}"
        doc_tokens = self.preprocess_text(doc_text)

        # Document length normalization
        avg_doc_length = 300  # Approximate average document length
        doc_length = len(doc_tokens)

        for token in query_tokens:
            # Calculate term frequency in document
            tf = doc_tokens.count(token)

            # Calculate inverse document frequency
            doc_count = len(self.title_index.get(token, {})) + \
                len(self.description_index.get(token, {}))
            if doc_count == 0:
                continue

            idf = math.log(
                (len(self.products) - doc_count + 0.5) / (doc_count + 0.5))

            # Calculate BM25 score for this term
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += idf * (numerator / denominator)

        return score

    def compute_document_ranking(self, doc_url: str, query: str, query_tokens: List[str],
                                 bm25_weight: float = 0.4, exact_match_weight: float = 2.0,
                                 review_weight: float = 0.3, title_match_weight: float = 0.2,
                                 origin_match_weight: float = 0.1) -> Dict[str, float]:
        """Calculate the ranking score for a document using multiple criteria with adjustable weights."""
        doc = self.products[doc_url]
        scores = {
            'bm25_score': 0,
            'exact_match_score': 0,
            'review_score': 0,
            'title_match_score': 0,
            'origin_match_score': 0
        }

        # 1. BM25 score (adjustable weight)
        scores['bm25_score'] = self.calculate_bm25_score(doc_url, query_tokens) * bm25_weight

        # 2. Exact match bonus (adjustable weight)
        if (query.lower().strip() == doc['title'].lower().strip() or
            ('brand' in doc and query.lower().strip() == doc['brand'].lower().strip()) or
            ('product_features' in doc and 'made in' in doc['product_features'] and
             query.lower().strip() == doc['product_features']['made in'].lower().strip())):
            scores['exact_match_score'] = exact_match_weight

        # 3. Review score (adjustable weight)
        if doc_url in self.reviews_index:
            review_data = self.reviews_index[doc_url]
            base_review_score = (review_data['mean_mark'] * 0.3 +
                                 min(review_data['total_reviews'], 10) * 0.1)
            scores['review_score'] = base_review_score * review_weight

        # 4. Title match score (adjustable weight)
        title_tokens = self.preprocess_text(doc['title'])
        title_matches = sum(
            1 for token in query_tokens if token in title_tokens)
        scores['title_match_score'] = title_matches * title_match_weight

        # 5. Origin match score (adjustable weight)
        if 'product_features' in doc and 'made in' in doc['product_features']:
            origin = doc['product_features']['made in'].lower()
            if origin in query_tokens:
                scores['origin_match_score'] = origin_match_weight

        # Calculate final score
        scores['final_score'] = sum(scores.values())
        return scores

    def _save_search_results(self, results: Dict) -> None:
        """Save the search results to a JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        query_slug = re.sub(r'[^a-z0-9]+', '_',
                            results['metadata']['query'].lower())
        filename = f"search_{query_slug}_{timestamp}.json"
        filepath = os.path.join(self.results_directory, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def execute_search(self, query: str, search_mode: str = 'any', save_results: bool = False,
                       bm25_weight: float = 0.4, exact_match_weight: float = 2.0,
                       review_weight: float = 0.3, title_match_weight: float = 0.2,
                       origin_match_weight: float = 0.1) -> Dict:
        """Perform a search with adjustable weights for ranking."""
        # Tokenize and normalize query
        query_tokens = self.preprocess_text(query)
        query_tokens = [
            token for token in query_tokens if token not in STOPWORDS]
        enriched_tokens = self.enrich_query_with_origin_synonyms(query_tokens)

        # Get matching documents based on search mode
        if search_mode == 'exact':
            matching_documents = self.exact_match_search(query)
        elif search_mode == 'all':
            matching_documents = self.filter_documents_by_all_tokens(
                enriched_tokens)
        else:
            matching_documents = self.filter_documents_by_any_token(
                enriched_tokens)

        # Rank documents with adjustable weights
        rankings = {}
        for doc_url in matching_documents:
            rankings[doc_url] = self.compute_document_ranking(
                doc_url, query, enriched_tokens, bm25_weight, exact_match_weight,
                review_weight, title_match_weight, origin_match_weight)

        # Sort documents by final score
        sorted_rankings = sorted(
            rankings.items(), key=lambda item: item[1]['final_score'], reverse=True)

        # Prepare search results
        results = {
            "metadata": {
                "query": query,
                "search_mode": search_mode,
                "document_count": len(sorted_rankings)
            },
            "ranked_documents": sorted_rankings
        }

        if save_results:
            self._save_search_results(results)

        return results

if __name__ == "__main__":
    # Initialize search engine
    search_engine = ProductSearchEngine()

    # Example queries for testing
    test_queries = [
        "Box of Chocolate Candy",
        "comfortable footbed",
        "Available in black, red, nude, and silver",
        "Cat-Ear Beanie america"
    ]

    # Test each query with all search types
    search_types = ['all', 'exact', 'any']

    # Define custom weights for testing
    custom_weights = {
        "bm25_weight": 0.5,
        "exact_match_weight": 1.5,
        "review_weight": 0.2,
        "title_match_weight": 0.3,
        "origin_match_weight": 0.1
    }

    for query in test_queries:
        print(f"\nTesting query: {query}")
        for search_type in search_types:
            print(f"\nSearch type: {search_type}")
            results = search_engine.execute_search(query, search_mode=search_type, save_results=True, **custom_weights)
            print(f"Found {results['metadata']['document_count']} documents")
            
            # Display the top 3 results
            for i, (doc_url, doc_data) in enumerate(results['ranked_documents'][:3], 1):
                print(f"\n{i}. {search_engine.products[doc_url]['title']} (Score: {doc_data['final_score']:.3f})")
                print(f"URL: {doc_url}")
                for component, score in doc_data.items():
                    if component != 'final_score':
                        print(f"  - {component}: {score:.3f}")
                if 'description' in search_engine.products[doc_url] and search_engine.products[doc_url]['description']:
                    print(f"Description: {search_engine.products[doc_url]['description'][:200]}...")