import chromadb
from chromadb.utils import embedding_functions
from chromadb.errors import NotFoundError
import os

# Prefer the DB_PATH declared by vector_store so both modules agree
try:
    from src.engine.vector_store import DB_PATH as VECTOR_DB_PATH
except Exception:
    VECTOR_DB_PATH = None

# Fallback to a package-relative path if vector_store is unavailable
if VECTOR_DB_PATH:
    DB_PATH = os.path.abspath(VECTOR_DB_PATH)
else:
    DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "embeddings", "chroma_db"))

print(f"--- ATTEMPTING TO LOAD DB FROM: {DB_PATH} ---")
COLLECTION_NAME = "shl_assessments"


class Retriever:
    """
    Retriever class for semantic search of SHL assessments.

    Uses ChromaDB and sentence transformers to find relevant assessments
    based on semantic similarity to the query.
    """
    def __init__(self):
        """Initialize the retriever with ChromaDB and embedding function."""
        # Ensure the DB path exists (Chromadb will create files on write), but warn if missing
        if not os.path.exists(DB_PATH):
            # do not raise here; allow higher-level code to trigger a rebuild from CSV
            raise FileNotFoundError(f"ChromaDB path not found at {DB_PATH}.")

        # Connect to the persistent ChromaDB (explicit named arg for compatibility)
        self.client = chromadb.PersistentClient(path=DB_PATH)

        # Initialize the embedding function with a sentence transformer model
        self.embed_func = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Try to get the collection; if it doesn't exist, attempt to create it (empty) so queries won't fail
        try:
            self.collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embed_func
            )
        except Exception:
            # If the collection is not found, create an empty collection. This allows the app to run
            # and the vector_store initializer to populate it later.
            try:
                self.collection = self.client.create_collection(
                    name=COLLECTION_NAME,
                    embedding_function=self.embed_func
                )
            except Exception as e:
                raise RuntimeError(f"Failed to get or create Chroma collection: {e}")

    def search(self, query, n_results=15):
        """
        Search for assessments matching the query.

        Args:
            query (str): The search query
            n_results (int): Number of results to return

        Returns:
            list: Ranked list of assessment dictionaries
        """
        try:
            # Query the vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Format the results into a clean list of dictionaries
            cleaned_results = []
            for i in range(len(results['ids'][0])):
                item = {
                    "id": results['ids'][0][i],
                    "score": results['distances'][0][i],  # Lower distance = better match
                    "document": results['documents'][0][i],
                    **results['metadatas'][0][i]  # Include all metadata fields
                }
                cleaned_results.append(item)

            return cleaned_results

        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []


if __name__ == "__main__":
    # Test the retriever with a sample query
    retriever = Retriever()
    test_query = "I need a Java developer who is good at teamwork"
    print(f"\n🔍 Testing Query: '{test_query}'\n")

    matches = retriever.search(test_query)

    for m in matches:
        print(f" - [{m['score']:.4f}] {m['name']} ({m['test_type']})")
