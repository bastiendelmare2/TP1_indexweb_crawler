# Product Search Engine

This repository contains a search engine designed to index and query product data efficiently. Below is an overview of the repository structure and the functionality implemented.  

## Repository Structure

- **`indexes/`**  
  This directory contains the indexes used by the search engine to retrieve and rank results.  

- **`data/`**  
  This directory holds the source data used for building the search engine.  

- **`productsearchengine.py`**  
  This Python file contains the main `ProductSearchEngine` class, which implements the core functionalities of the search engine. Additionally, a test script is included to perform queries on the search engine. The results of these queries are saved in JSON format within the `search_results/` directory.  

- **`search_results/`**  
  Query results are stored here in JSON format for easy access and analysis.  

- **`test_weights_ranking.ipynb`**  
  This Jupyter Notebook explores the importance of the different weights used in the search engine and discusses the impact of modifying these weights in various contexts. Due to the limited size of the dataset, it is challenging to illustrate the full consequences of these changes. However, the notebook provides a discussion of use cases and scenarios where adjusting these weights could be beneficial.  

## Running the Search engine
To execute the search engine and see examples of queries with the default weighting configuration, use the following command:

   ```bash
   python productsearchengine.py
   ```
This will illustrate how the search engine works with an initial weighting setup, showing query results in JSON format stored in the search_results/ directory.t


## test_weights_ranking.ipynb

This Jupyter Notebook explores the importance of each weight used in the search engine and analyzes the impact of modifying them based on different contexts. Due to the limited size of the dataset, it is challenging to fully illustrate the consequences of such changes. However, the notebook provides valuable discussions on practical use cases and scenarios where adjusting these weights could be relevant and beneficial.
