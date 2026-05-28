"""Build hierarchical tree data for D3.js visualization."""

from __future__ import annotations

import json
from models import Person


def load_family() -> dict[int, Person]:
    """Load family members from family_members.json."""
    data = json.load(open("family_members.json"))

    # Handle both old format (raw list) and new format (dict with "rows" key)
    if isinstance(data, list):
        rows: list[dict[str, str]] = data
    else:
        rows = data.get("rows", [])

    family = [
        Person(int(row["Sl"]), row["Name"], row["Gender"], row.get("VitalStatus", ""))
        for row in rows
    ]
    Person.members = {member.id: member for member in family}

    # Add parent and spouse relationships
    for row in rows:
        if row.get("Parent"):
            child = Person.members[int(row["Sl"])]
            parent = Person.members[int(row["Parent"])]
            child.add_parent(parent)
        if row.get("Spouse"):
            person = Person.members[int(row["Sl"])]
            spouse = Person.members[int(row["Spouse"])]
            person.add_spouse(spouse)

    return Person.members


def build_tree_node(person: Person) -> dict[str, object]:
    """Recursively build a tree node for D3.

    Spouses (people who married into the family) are shown as labels
    on their partner's node, never as separate child nodes.
    """
    spouse_info = person.get_spouse()
    node: dict[str, object] = {
        "id": person.id,
        "name": person.name,
        "gender": person.gender,
        "vital_stats": person.vital_stats,
        "spouse_name": spouse_info[1] if spouse_info else None,
    }

    # Collect children: the person's own children plus the spouse's children.
    # A spouse "married into" the family, so their children belong to this node.
    children_ids = set(person.children)
    if person.spouse is not None and person.spouse in Person.members:
        children_ids.update(Person.members[person.spouse].children)

    # Remove the spouse from children (spouse is shown as a label, not a node)
    if person.spouse is not None:
        children_ids.discard(person.spouse)

    if children_ids:
        children: list[dict[str, object]] = []
        for cid in sorted(children_ids):
            if cid != person.parent:  # don't recurse back up to the parent
                child = Person.members[cid]
                children.append(build_tree_node(child))
        if children:
            node["children"] = children
        else:
            node["children"] = []
    else:
        node["children"] = []

    return node


def build_tree() -> dict[str, object]:
    """Build the full family tree hierarchy for D3.

    Sl #1 (id=1) is always the origin/root of the family.
    """
    members = load_family()

    root = members.get(1)
    if root is None:
        return {"name": "No family data", "children": []}

    return build_tree_node(root)


def get_all_members() -> list[dict[str, object]]:
    """Return all family members as a flat list of dicts."""
    members = load_family()
    return [m.to_dict() for m in members.values()]
