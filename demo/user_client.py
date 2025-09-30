
import asyncio
import argparse
from temporalio.client import Client
from workflow.daily_interaction_workflow import DailyInteractionWorkflow

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    args = parser.parse_args()

    client = await Client.connect("localhost:7233")

    # In a real application, you would have a way to get the workflow id for the user.
    # For this demo, we'll assume a convention.
    workflow_id = f"daily-interaction-{args.user}"

    while True:
        print(f"User: {args.user}")
        print("Actions: [approve, reject, feedback, handoff]")
        action = input("Enter action: ")

        if action == "approve":
            await client.get_workflow_handle(workflow_id).signal(DailyInteractionWorkflow.approve_step, args.user)
            print("Approved step.")
        elif action == "reject":
            await client.get_workflow_handle(workflow_id).signal(DailyInteractionWorkflow.reject_step, args.user)
            print("Rejected step.")
        elif action == "feedback":
            feedback = input("Enter feedback: ")
            await client.get_workflow_handle(workflow_id).signal(DailyInteractionWorkflow.provide_feedback, args.user, feedback)
            print("Feedback provided.")
        elif action == "handoff":
            manager = input("Enter manager user id: ")
            await client.get_workflow_handle(workflow_id).signal(DailyInteractionWorkflow.handoff_to_manager, manager)
            print(f"Handoff to {manager} requested.")
        else:
            print("Invalid action.")

if __name__ == "__main__":
    asyncio.run(main())
