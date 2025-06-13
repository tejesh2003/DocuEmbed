import asyncio
from temporalio.client import Client
from workflow import DocIngestWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    
    handle = await client.start_workflow(
        workflow=DocIngestWorkflow,
        args=("sample-file-id", "https://drive.google.com/uc?export=download&id=11qMQPCRqIxpAqPds75KLkancOd5WgQs1","pdf"),
        id="docuembed-workflow-001",
        task_queue="doc-ingest-task-queue"
    )
    
    result = await handle.result()
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main())
