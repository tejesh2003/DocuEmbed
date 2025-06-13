from pymilvus import connections, Collection, utility
from pymilvus.exceptions import MilvusException

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

collection_name = "docuembed_collection"

# Check if collection exists
if not utility.has_collection(collection_name):
    print(f"Collection '{collection_name}' does not exist.")
else:
    try:
        # Load collection
        collection = Collection(collection_name)

        # Load data into memory
        collection.load()

        # Get count of entities
        count = collection.num_entities
        print("Entity count:", count)

        if count == 0:
            print("ℹ Collection exists but has no data.")
        else:
            # Perform query including the 'file_id' field
            results = collection.query(
                expr="id >= 0",
                output_fields=["id", "file_id", "chunk", "embedding"],
                limit=10
            )

            # Print results
            for i, result in enumerate(results):
                print(f"Result {i+1}:")
                print("  ID:", result['id'])
                print("  File ID:", result['file_id'])
                print("  Chunk:", result['chunk'])
                print("  Embedding (first 5 dims):", result['embedding'][:5])

    except MilvusException as e:
        print(f"Unexpected error while accessing collection: {e}")
