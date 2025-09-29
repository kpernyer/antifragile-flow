import asyncio
import inspect
import os

from activities import Activities
from temporalio.client import Client
from temporalio.worker import Worker

import shared
from workflows import CompetitorAnalysisWorkflow, HelloWorldWorkflow, StrategicDecisionWorkflow


async def main():
    # Connect to local Temporal server
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    # Register the activities with dependency injection
    # Import OrganizationalTwin here to avoid Temporal sandbox issues
    from organizational_twin import organizational_twin

    activities = Activities(org_twin=organizational_twin)

    worker = Worker(
        client,
        task_queue=shared.TASK_QUEUE_NAME,
        workflows=[HelloWorldWorkflow, StrategicDecisionWorkflow, CompetitorAnalysisWorkflow],
        activities=find_activities(activities),
    )

    print("Worker started.")
    await worker.run()


# ---- auto-discovery helper ----
_ACTIVITY_ATTR = "__temporal_activity_definition"  # set by @activity.defn


def find_activities(obj):
    """Return a list of bound methods on `obj` that are Temporal activities."""
    acts = []
    for _, member in inspect.getmembers(obj):
        if callable(member) and is_activity_callable(member):
            acts.append(member)  # bound method carries injected deps
    return acts


def is_activity_callable(attr) -> bool:
    # Works for functions and bound methods
    func = attr.__func__ if inspect.ismethod(attr) else attr
    return hasattr(func, _ACTIVITY_ATTR)


if __name__ == "__main__":
    asyncio.run(main())
