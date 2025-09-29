import asyncio
import uuid

from temporalio.client import Client

import shared
import workflows


async def main():
    # Connect to local Temporal server
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        workflows.HelloWorldWorkflow,
        "Hacker",
        id=f"hello-world-workflow-{uuid.uuid4()}",
        task_queue=shared.TASK_QUEUE_NAME,
    )
    print("Workflow result:", result)


if __name__ == "__main__":
    asyncio.run(main())
