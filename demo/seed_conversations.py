
import asyncio
from temporalio.client import Client
from workflow.daily_interaction_workflow import DailyInteractionWorkflow, DailyInteractionRequest

async def main():
    client = await Client.connect("localhost:7233")

    users = [f"user{i}" for i in range(1, 6)]

    # Start a catchball workflow
    await client.start_workflow(
        DailyInteractionWorkflow.run,
        DailyInteractionRequest(
            mode='catchball',
            users=users,
            prompt="Discuss the quarterly results and propose a strategy for the next quarter.",
            initial_state={"topic": "Quarterly Results"}
        ),
        id="daily-interaction-catchball",
        task_queue="main-task-queue",
    )
    print("Started catchball workflow.")

    # Start a wisdom of the crowd workflow
    await client.start_workflow(
        DailyInteractionWorkflow.run,
        DailyInteractionRequest(
            mode='wisdom',
            users=users,
            prompt="What are the biggest challenges facing our industry in the next 5 years?"
        ),
        id="daily-interaction-wisdom",
        task_queue="main-task-queue",
    )
    print("Started wisdom of the crowd workflow.")

if __name__ == "__main__":
    asyncio.run(main())
