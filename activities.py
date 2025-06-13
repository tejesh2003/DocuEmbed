from temporalio import activity
import aiohttp
import asyncio
from pymilvus import utility, connections, Collection, CollectionSchema, FieldSchema, DataType

# fetch_document activity
@activity.defn
async def fetch_document(url: str, file_type: str) -> tuple[bytes, str]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
        
        file_type = file_type.lower().lstrip(".")
        if file_type == "xls":
            file_type = "xlsx"
        elif file_type not in {"txt", "pdf", "doc", "docx", "xlsx"}:
            raise ValueError(f"Unsupported file type: {file_type}")

        return content, file_type
            
    except Exception as e:
        raise RuntimeError(f"Failed to fetch document from {url}: {e}")

#parse_document activity
@activity.defn
async def parse_document(content: bytes, file_type: str) -> list[str]:
    def _parse():
        from io import BytesIO
        from unstructured.chunking.title import chunk_by_title
        from unstructured.partition.text import partition_text
        from unstructured.partition.pdf import partition_pdf
        from unstructured.partition.docx import partition_docx
        from unstructured.partition.doc import partition_doc
        from unstructured.partition.xlsx import partition_xlsx

        file_like = BytesIO(content)

        if file_type == "txt":
            elements = partition_text(file=file_like)
        elif file_type == "pdf":
            elements = partition_pdf(file=file_like)
        elif file_type == "docx":
            elements = partition_docx(file=file_like)
        elif file_type == "doc":
            elements = partition_doc(file=file_like)
        elif file_type == "xlsx":
            elements = partition_xlsx(file=file_like)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        chunks = chunk_by_title(elements)
        return [chunk.text for chunk in chunks if chunk.text.strip()]

    return await asyncio.to_thread(_parse)

#generate_embeddings activity
@activity.defn
async def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    await asyncio.sleep(1)
    return [[float(len(chunk))] * 10 for chunk in chunks]

#store_in_milvus activity
@activity.defn
async def store_in_milvus(file_id: str, chunks: list[str], embeddings: list[list[float]]) -> None:
    from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType

    connections.connect(alias="default", host="localhost", port="19530")

    collection_name = "docuembed_collection"

    if collection_name not in utility.list_collections():
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=len(embeddings[0])),
        ]
        schema = CollectionSchema(fields, description="Document Embeddings")
        collection = Collection(name=collection_name, schema=schema)
        collection.create_index(
            field_name="embedding",
            index_params={
                "index_type": "IVF_FLAT",
                "metric_type": "L2",
                "params": {"nlist": 128},
            },
        )
    else:
        collection = Collection(name=collection_name)

    collection.load()

    file_id_column = [file_id] * len(chunks)
    data_to_insert = [file_id_column, chunks, embeddings]
    collection.insert(data_to_insert)
    collection.flush()

    print(f"Stored {len(chunks)} chunks for file_id '{file_id}' into Milvus collection '{collection_name}'.")
