import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import DocIngestWorkflow
from activities import fetch_document, parse_document, generate_embeddings, store_in_milvus

async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="doc-ingest-task-queue", 
        workflows=[DocIngestWorkflow],
        activities=[fetch_document, parse_document, generate_embeddings, store_in_milvus],
    )

    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
