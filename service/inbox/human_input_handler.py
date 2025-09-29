import asyncio

from temporalio.client import Client

import shared


async def main():
    client = await Client.connect("localhost:7233")

    print("Human input handler started. Monitoring for workflows waiting for input...")
    print("Press Ctrl+C to exit.\n")

    while True:
        workflows = client.list_workflows(f'TaskQueue="{shared.TASK_QUEUE_NAME}"')

        async for workflow_info in workflows:
            if workflow_info.workflow_type == "HumanInTheLoopWorkflow":
                handle = client.get_workflow_handle(workflow_info.id)

                status = await handle.query("get_status")

                if status == "waiting_for_name":
                    print(f"\nWorkflow {workflow_info.id} is waiting for a name.")
                    name = input("Enter name: ")

                    await handle.signal("submit_name", name)
                    print(f"Submitted name '{name}' to workflow {workflow_info.id}")

        await asyncio.sleep(2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nHuman input handler stopped.")
