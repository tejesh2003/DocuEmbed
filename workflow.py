from temporalio import workflow
from datetime import timedelta
from activities import fetch_document, parse_document, generate_embeddings, store_in_milvus

print("Workflow started:")

@workflow.defn
class DocIngestWorkflow:
    @workflow.run
    async def run(self, file_id: str, url: str, file_type: str) -> str:
        try:
            print("Workflow started inside:")

            content,file_type = await workflow.execute_activity(
                fetch_document,
                args=[url,file_type],
                start_to_close_timeout=timedelta(seconds=60)
            )

            parsed = await workflow.execute_activity(
                parse_document,
                args=[content, file_type], 
                start_to_close_timeout=timedelta(seconds=60)
            )

            embeddings = await workflow.execute_activity(
                generate_embeddings,
                args=[parsed],
                start_to_close_timeout=timedelta(seconds=60)
            )

            result = await workflow.execute_activity(
                store_in_milvus,
                args=[file_id, parsed, embeddings],
                start_to_close_timeout=timedelta(seconds=60)
            )

            return result

        except Exception as e:
            print(f"Workflow error: {e}")
            raise
