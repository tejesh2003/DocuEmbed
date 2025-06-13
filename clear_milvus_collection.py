from pymilvus import connections, utility

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Check if collection exists
collection_name = "docuembed_collection"
if utility.has_collection(collection_name):
    utility.drop_collection(collection_name)
    print(f"Deleted collection: {collection_name}")
else:
    print(f"Collection '{collection_name}' not found.")
