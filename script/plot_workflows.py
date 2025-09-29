#!/usr/bin/env python3
"""
Plot workflows and actors from the migrated data
Shows organizational structure, workflows, and message flows
"""

from pathlib import Path
import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from neo4j_service import Neo4jService
from postgres_models import PostgresInboxService


def get_organizational_data():
    """Get organizational structure from Neo4j"""
    neo4j_service = Neo4jService()

    try:
        with neo4j_service.driver.session() as session:
            # Get all people with their roles and departments
            result = session.run("""
                MATCH (p:Person)
                OPTIONAL MATCH (p)-[:HAS_ROLE]->(r:Role)
                OPTIONAL MATCH (p)-[:BELONGS_TO]->(d:Department)
                OPTIONAL MATCH (p)-[:REPORTS_TO]->(manager:Person)
                RETURN p, r, d, manager
            """)

            people = []
            for record in result:
                person_data = dict(record["p"])
                role_data = dict(record["r"]) if record["r"] else None
                dept_data = dict(record["d"]) if record["d"] else None
                manager_data = dict(record["manager"]) if record["manager"] else None

                people.append(
                    {
                        "person": person_data,
                        "role": role_data,
                        "department": dept_data,
                        "manager": manager_data,
                    }
                )

            # Get workflows
            workflow_result = session.run("""
                MATCH (w:Workflow)
                OPTIONAL MATCH (initiator:Person)-[:INITIATED]->(w)
                RETURN w, initiator
            """)

            workflows = []
            for record in workflow_result:
                workflow_data = dict(record["w"])
                initiator_data = dict(record["initiator"]) if record["initiator"] else None

                workflows.append({"workflow": workflow_data, "initiator": initiator_data})

        return people, workflows

    finally:
        neo4j_service.close()


def get_message_flows():
    """Get message flows from PostgreSQL"""
    postgres_service = PostgresInboxService()

    with postgres_service.get_session() as session:
        # Get all messages with workflow info
        from sqlalchemy import text

        result = session.execute(
            text("""
            SELECT m.*, w.workflow_type, w.status as workflow_status
            FROM inbox_messages m
            LEFT JOIN workflows w ON m.workflow_id = w.id
            ORDER BY m.created_at
        """)
        )

        messages = []
        for row in result:
            # Convert row to dict manually
            row_dict = {}
            for i, col in enumerate(result.keys()):
                row_dict[col] = row[i]
            messages.append(row_dict)

    return messages


def create_organizational_plot(people, workflows, messages):
    """Create a comprehensive plot of the organizational structure and workflows"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle(
        "Organizational Twin: Workflows and Actor Analysis", fontsize=16, fontweight="bold"
    )

    # Plot 1: Organizational Hierarchy
    G_org = nx.DiGraph()

    # Add nodes for people
    pos_org = {}
    dept_positions = {
        "Executive": (0, 2),
        "Sales": (-2, 1),
        "Engineering": (0, 1),
        "Legal": (2, 1),
        "IT": (0, 0),
    }

    for person_data in people:
        person = person_data["person"]
        dept = person_data["department"]
        role = person_data["role"]

        dept_name = dept["name"] if dept else "Unknown"
        role_title = role["title"] if role else "Unknown"

        # Create node ID and label
        node_id = person["id"]
        label = f"{person['name']}\n{role_title}"

        G_org.add_node(node_id, label=label, department=dept_name)

        # Position based on department
        if dept_name in dept_positions:
            base_x, base_y = dept_positions[dept_name]
            # Add some randomness to avoid overlap
            import random

            pos_org[node_id] = (
                base_x + random.uniform(-0.3, 0.3),
                base_y + random.uniform(-0.2, 0.2),
            )
        else:
            pos_org[node_id] = (random.uniform(-3, 3), random.uniform(-1, 3))

    # Add reporting relationships
    for person_data in people:
        person = person_data["person"]
        manager = person_data["manager"]

        if manager:
            G_org.add_edge(manager["id"], person["id"], relationship="reports_to")

    # Draw organizational chart
    ax1.set_title("Organizational Hierarchy", fontweight="bold")

    # Color nodes by department
    dept_colors = {
        "Executive": "red",
        "Sales": "blue",
        "Engineering": "green",
        "Legal": "orange",
        "IT": "purple",
    }
    node_colors = [
        dept_colors.get(G_org.nodes[node].get("department", "Unknown"), "gray")
        for node in G_org.nodes()
    ]

    nx.draw(
        G_org,
        pos_org,
        ax=ax1,
        with_labels=False,
        node_color=node_colors,
        node_size=2000,
        font_size=8,
        arrows=True,
        edge_color="gray",
    )

    # Add labels
    labels = {node: G_org.nodes[node]["label"] for node in G_org.nodes()}
    nx.draw_networkx_labels(G_org, pos_org, labels, ax=ax1, font_size=8)

    # Create legend for departments
    legend_elements = [
        mpatches.Patch(color=color, label=dept) for dept, color in dept_colors.items()
    ]
    ax1.legend(handles=legend_elements, loc="upper right")

    # Plot 2: Workflow Flow
    ax2.set_title("Workflow Execution Flow", fontweight="bold")

    if workflows:
        workflow_data = workflows[0]["workflow"]  # Focus on the main workflow
        initiator = workflows[0]["initiator"]

        # Create workflow flow diagram
        G_workflow = nx.DiGraph()

        # Add workflow node
        G_workflow.add_node("workflow", label=f"Workflow\n{workflow_data['type']}", type="workflow")

        if initiator:
            G_workflow.add_node(initiator["id"], label=initiator["name"], type="person")
            G_workflow.add_edge(initiator["id"], "workflow", relationship="initiated")

        # Add message recipients
        recipients = set()
        for msg in messages:
            if msg["workflow_id"] == workflow_data["id"]:
                recipients.add(msg["to_user_id"])
                G_workflow.add_node(msg["to_user_id"], type="person")
                G_workflow.add_edge("workflow", msg["to_user_id"], relationship="message")

        # Layout
        pos_workflow = nx.spring_layout(G_workflow, k=2, iterations=50)

        # Color by type
        node_colors_wf = [
            "lightblue" if G_workflow.nodes[node].get("type") == "workflow" else "lightgreen"
            for node in G_workflow.nodes()
        ]

        nx.draw(
            G_workflow,
            pos_workflow,
            ax=ax2,
            with_labels=True,
            node_color=node_colors_wf,
            node_size=1500,
            font_size=10,
            arrows=True,
        )
    else:
        ax2.text(0.5, 0.5, "No workflows found", ha="center", va="center", transform=ax2.transAxes)

    # Plot 3: Message Flow Network
    ax3.set_title("Message Communication Network", fontweight="bold")

    G_messages = nx.DiGraph()

    # Add all people as nodes
    for person_data in people:
        person = person_data["person"]
        G_messages.add_node(person["id"], label=person["name"])

    # Add message edges
    message_counts = {}
    for msg in messages:
        from_user = msg["from_user_id"]
        to_user = msg["to_user_id"]
        edge_key = (from_user, to_user)

        if edge_key in message_counts:
            message_counts[edge_key] += 1
        else:
            message_counts[edge_key] = 1
            G_messages.add_edge(from_user, to_user)

    # Layout for message network
    pos_messages = nx.spring_layout(G_messages, k=1.5, iterations=50)

    # Draw with edge thickness based on message count
    edge_widths = [message_counts.get((u, v), 1) * 2 for u, v in G_messages.edges()]

    nx.draw(
        G_messages,
        pos_messages,
        ax=ax3,
        with_labels=True,
        node_color="lightcoral",
        node_size=1200,
        font_size=9,
        arrows=True,
        width=edge_widths,
    )

    # Plot 4: Message Statistics
    ax4.set_title("Message and Workflow Statistics", fontweight="bold")

    # Create statistics
    stats_data = {
        "Total People": len(people),
        "Total Workflows": len(workflows),
        "Total Messages": len(messages),
        "Departments": len(set(p["department"]["name"] for p in people if p["department"])),
        "Active Communications": len(set((m["from_user_id"], m["to_user_id"]) for m in messages)),
    }

    # Message types distribution
    message_types = {}
    for msg in messages:
        msg_type = msg["message_type"]
        message_types[msg_type] = message_types.get(msg_type, 0) + 1

    # Create bar chart
    y_pos = range(len(stats_data))
    ax4.barh(y_pos, list(stats_data.values()), color="skyblue")
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(list(stats_data.keys()))
    ax4.set_xlabel("Count")

    # Add values on bars
    for i, v in enumerate(stats_data.values()):
        ax4.text(v + 0.1, i, str(v), va="center")

    plt.tight_layout()
    plt.savefig("organizational_workflows.png", dpi=300, bbox_inches="tight")
    plt.show()

    return stats_data, message_types


def print_detailed_analysis(people, workflows, messages, stats_data, message_types):
    """Print detailed text analysis"""
    print("\n" + "=" * 80)
    print("🏢 ORGANIZATIONAL TWIN - DETAILED ANALYSIS")
    print("=" * 80)

    print("\n📊 OVERVIEW:")
    for key, value in stats_data.items():
        print(f"  • {key}: {value}")

    print("\n👥 ORGANIZATIONAL STRUCTURE:")
    departments = {}
    for person_data in people:
        person = person_data["person"]
        dept = person_data["department"]
        role = person_data["role"]

        dept_name = dept["name"] if dept else "Unknown"
        if dept_name not in departments:
            departments[dept_name] = []

        departments[dept_name].append(
            {
                "name": person["name"],
                "role": role["title"] if role else "Unknown",
                "id": person["id"],
            }
        )

    for dept, members in departments.items():
        print(f"\n  🏬 {dept} Department:")
        for member in members:
            print(f"    • {member['name']} - {member['role']} ({member['id']})")

    print("\n🔄 WORKFLOWS:")
    for i, workflow_data in enumerate(workflows, 1):
        workflow = workflow_data["workflow"]
        initiator = workflow_data["initiator"]

        print(f"\n  {i}. Workflow: {workflow['id']}")
        print(f"     Type: {workflow['type']}")
        print(f"     Status: {workflow['status']}")
        if initiator:
            print(f"     Initiated by: {initiator['name']} ({initiator['id']})")

    print("\n💬 MESSAGE FLOWS:")
    if messages:
        print(f"  Total Messages: {len(messages)}")
        print("\n  Message Types:")
        for msg_type, count in message_types.items():
            print(f"    • {msg_type}: {count}")

        print("\n  Recent Messages:")
        for i, msg in enumerate(messages[-5:], 1):  # Show last 5 messages
            print(f"    {i}. {msg['from_user_id']} → {msg['to_user_id']}")
            print(f"       Type: {msg['message_type']} | Priority: {msg['priority']}")
            print(f"       Message: {msg['original_message'][:60]}...")
            if msg["workflow_id"]:
                print(f"       Workflow: {msg['workflow_id']}")

    print("\n🎯 KEY INSIGHTS:")

    # Find the most active communicator
    from_counts = {}
    to_counts = {}
    for msg in messages:
        from_counts[msg["from_user_id"]] = from_counts.get(msg["from_user_id"], 0) + 1
        to_counts[msg["to_user_id"]] = to_counts.get(msg["to_user_id"], 0) + 1

    if from_counts:
        most_active_sender = max(from_counts, key=from_counts.get)
        most_active_receiver = max(to_counts, key=to_counts.get)

        print(
            f"  • Most Active Sender: {most_active_sender} ({from_counts[most_active_sender]} messages)"
        )
        print(
            f"  • Most Active Receiver: {most_active_receiver} ({to_counts[most_active_receiver]} messages)"
        )

    # Analyze hierarchy
    ceo = next((p for p in people if p["role"] and "CEO" in p["role"]["title"]), None)
    if ceo:
        print(f"  • CEO: {ceo['person']['name']} ({ceo['person']['id']})")

        # Count direct reports
        direct_reports = [
            p for p in people if p["manager"] and p["manager"]["id"] == ceo["person"]["id"]
        ]
        print(f"  • Direct Reports to CEO: {len(direct_reports)}")

    print("\n🔗 COMMUNICATION PATTERNS:")
    if workflows and messages:
        workflow_messages = [m for m in messages if m["workflow_id"]]
        print(f"  • Workflow-driven messages: {len(workflow_messages)}/{len(messages)}")

        # Check if all VPs received messages in the main workflow
        vp_roles = [p for p in people if p["role"] and "VP" in p["role"]["title"]]
        if vp_roles:
            vp_ids = {vp["person"]["id"] for vp in vp_roles}
            messaged_vps = {m["to_user_id"] for m in workflow_messages if m["to_user_id"] in vp_ids}
            print(f"  • VPs engaged in workflow: {len(messaged_vps)}/{len(vp_ids)}")


def main():
    """Main function to generate workflow visualization"""
    print("🔄 Analyzing organizational workflows and actors...")

    try:
        # Get data from both databases
        people, workflows = get_organizational_data()
        messages = get_message_flows()

        print(
            f"✅ Loaded {len(people)} people, {len(workflows)} workflows, {len(messages)} messages"
        )

        # Create visualizations
        stats_data, message_types = create_organizational_plot(people, workflows, messages)

        # Print detailed analysis
        print_detailed_analysis(people, workflows, messages, stats_data, message_types)

        print("\n📈 Visualization saved as 'organizational_workflows.png'")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
