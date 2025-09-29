import asyncio
import uuid

from temporalio.client import Client

import shared
import workflows


async def main():
    client = await Client.connect("localhost:7233")
    workflow_id = f"human-in-loop-workflow-{uuid.uuid4()}"

    handle = await client.start_workflow(
        workflows.HumanInTheLoopWorkflow.run,
        id=workflow_id,
        task_queue=shared.TASK_QUEUE_NAME,
    )

    print(f"Started workflow {workflow_id}")
    print("Workflow is waiting for human input...")
    print("Run the human input handler to provide the name:")
    print("  uv run python/src/human_input_handler.py")

    result = await handle.result()
    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())
