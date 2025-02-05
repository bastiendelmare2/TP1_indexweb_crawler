import json
import os
import re
import string
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

class Indexer:
    STOPWORDS = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
        "yours", "youre", "yourself", "yourselves", "he", "him", "his", "himself", "she", 
        "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
        "theirs", "themselves", "what", "which", "who", "whom", "this", "that", 
        "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", 
        "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
        "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", 
        "at", "by", "for", "with", "about", "against", "between", "into", "through", 
        "during", "before", "after", "above", "below", "to", "from", "up", "down", 
        "in", "out", "on", "off", "over", "under", "again", "further", "then", 
        "once", "here", "there", "when", "where", "why", "how", "all", "any", 
        "both", "each", "few", "more", "most", "other", "some", "such", "no", 
        "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", 
        "t", "can", "will", "just", "don", "should", "now"
    }

    def __init__(self, input_file, filtered_file, index_folder):
        self.input_file = input_file
        self.filtered_file = filtered_file
        self.index_folder = index_folder

    def extract_product_details_from_url(self, url):
        """Extracts product ID and variant from the URL."""
        try:
            match = re.search(r"/product/(\d+)", url)
            product_id = match.group(1) if match else None

            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            variant_id = query_params.get("variant", [None])[0]

            return {"product_id": product_id, "variant": variant_id}
        except Exception as e:
            print(f"Error parsing URL: {url}. Error: {e}")
            return {"product_id": None, "variant": None}

    def load_jsonl_data(self):
        """Loads data from a JSONL file."""
        if not os.path.exists(self.input_file):
            print(f"Error: File {self.input_file} does not exist.")
            return []
        
        data = []
        with open(self.input_file, "r", encoding="utf-8") as file:
            for line in file:
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
        return data

    def save_jsonl_data(self, data):
        """Saves data to a JSONL file."""
        with open(self.filtered_file, "w", encoding="utf-8") as file:
            for doc in data:
                file.write(json.dumps(doc, ensure_ascii=False) + "\n")

    def tokenize_text(self, text):
        """Tokenizes text by removing punctuation and stopwords."""
        if not text:
            return []
        text = text.lower().translate(str.maketrans('', '', string.punctuation))
        return [word for word in text.split() if word not in self.STOPWORDS]

    def create_inverted_index_with_positions(self, field, data):
        """Builds an inverted index with positions for a given field."""
        index = defaultdict(lambda: defaultdict(list))
        for doc in data:
            tokens = self.tokenize_text(doc.get(field, ""))
            for pos, token in enumerate(tokens):
                index[token][doc['url']].append(pos)
        return index

    def create_reviews_index(self, data):
        """Creates an index for reviews including total count, average rating, and last rating."""
        index = {}
        for doc in data:
            reviews = doc.get("product_reviews", [])
            if reviews:
                total_reviews = len(reviews)
                avg_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews
                last_rating = reviews[-1].get("rating", None)
                index[doc['url']] = {"total_reviews": total_reviews, "average_rating": avg_rating, "last_rating": last_rating}
        return index

    def create_feature_index(self, data, feature_key):
        """Builds an inverted index for a specific feature (e.g., color, container)."""
        index = defaultdict(set)
        for doc in data:
            feature_value = doc.get("product_features", {}).get(feature_key, "")
            for token in self.tokenize_text(str(feature_value)):
                index[token].add(doc['url'])
        return {token: list(urls) for token, urls in index.items()}

    def save_index_to_file(self, index, filename):
        """Saves an index to a JSON file."""
        os.makedirs(self.index_folder, exist_ok=True)
        with open(os.path.join(self.index_folder, filename), "w", encoding="utf-8") as file:
            json.dump(index, file, indent=4, ensure_ascii=False)

    def execute_pipeline(self):
        """Executes the full pipeline."""
        data = self.load_jsonl_data()
        if not data:
            print("No data loaded.")
            return
        
        # Extract product information from URL
        filtered_data = [doc | self.extract_product_details_from_url(doc.get("url", "")) for doc in data]
        self.save_jsonl_data(filtered_data)
        print("Filtered data saved.")
        
        # Build indexes
        title_index = self.create_inverted_index_with_positions("title", filtered_data)
        description_index = self.create_inverted_index_with_positions("description", filtered_data)
        reviews_index = self.create_reviews_index(filtered_data)
        brand_index = self.create_feature_index(filtered_data, "brand")
        origin_index = self.create_feature_index(filtered_data, "made in")
        color_index = self.create_feature_index(filtered_data, "flavor")
        container_index = self.create_feature_index(filtered_data, "container")
        
        # Save indexes
        self.save_index_to_file(title_index, "index_title.json")
        self.save_index_to_file(description_index, "index_description.json")
        self.save_index_to_file(reviews_index, "index_reviews.json")
        self.save_index_to_file(brand_index, "index_brand.json")
        self.save_index_to_file(origin_index, "index_made_in.json")
        self.save_index_to_file(color_index, "index_flavor.json")
        self.save_index_to_file(container_index, "index_container.json")
        
        print("All indexes generated and saved!")


if __name__ == "__main__":
    # Configuration des fichiers
    INPUT_FILE = "input/products.jsonl"
    FILTERED_FILE = "filtered_products.jsonl"
    INDEX_FOLDER = "indexs"

    # Création d'une instance de Indexer
    indexer = Indexer(INPUT_FILE, FILTERED_FILE, INDEX_FOLDER)

    # Exemple 1 : Chargement des données JSONL
    print("Exemple 1 : Chargement des données JSONL")
    data = indexer.load_jsonl_data()
    if data:
        print(f"Nombre de documents chargés : {len(data)}")
        print(f"Premier document : {data[0]}")
    print("\n")

    # Exemple 2 : Extraction des informations d'une URL
    print("Exemple 2 : Extraction des informations d'une URL")
    url = "https://web-scraping.dev/product/1?variant=orange-small"
    product_details = indexer.extract_product_details_from_url(url)
    print(f"Informations extraites de l'URL : {product_details}")
    print("\n")

    # Exemple 3 : Tokenisation d'un texte
    print("Exemple 3 : Tokenisation d'un texte")
    text = "This is a sample text for tokenization, with some stopwords like 'and' or 'the'."
    tokens = indexer.tokenize_text(text)
    print(f"Texte tokenisé : {tokens}")
    print("\n")

    # Exemple 4 : Création d'un index inversé avec positions pour les titres
    print("Exemple 4 : Création d'un index inversé avec positions pour les titres")
    title_index = indexer.create_inverted_index_with_positions("title", data)
    print(f"Index de titre (extrait) : {dict(list(title_index.items())[:2])}")  # Affiche un extrait de l'index
    print("\n")

    # Exemple 5 : Création d'un index des avis
    print("Exemple 5 : Création d'un index des avis")
    reviews_index = indexer.create_reviews_index(data)
    print(f"Index des avis (extrait) : {dict(list(reviews_index.items())[:1])}")  # Affiche un extrait de l'index
    print("\n")

    # Exemple 6 : Création d'un index pour une caractéristique (marque)
    print("Exemple 6 : Création d'un index pour une caractéristique (marque)")
    brand_index = indexer.create_feature_index(data, "brand")
    print(f"Index de marque (extrait) : {dict(list(brand_index.items())[:2])}")  # Affiche un extrait de l'index
    print("\n")

    # Exemple 7 : Sauvegarde d'un index dans un fichier JSON
    print("Exemple 7 : Sauvegarde d'un index dans un fichier JSON")
    indexer.save_index_to_file(brand_index, "index_brand_example.json")
    print(f"Index de marque sauvegardé dans 'index_brand_example.json'.")
    print("\n")

    # Exemple 8 : Exécution complète du pipeline
    print("Exemple 8 : Exécution complète du pipeline")
    indexer.execute_pipeline()
    print("Pipeline exécuté avec succès. Vérifiez les fichiers dans le dossier 'indexs'.")