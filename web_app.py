"""Flask web application for EV House family tree."""

from __future__ import annotations

from typing import Any
from flask import Flask, render_template, jsonify, request, Response
from tree_builder import build_tree, get_all_members, load_family
from models import Person

app = Flask(__name__)


def _get_members() -> dict[int, Person]:
    """Return Person.members dict from family_members.json."""
    return load_family()


@app.route("/")
def index() -> str:
    """Main page with the interactive family tree."""
    return render_template("index.html")


@app.route("/api/tree")
def api_tree() -> Response:
    """Return the full family tree as hierarchical JSON for D3."""
    tree = build_tree()
    return jsonify(tree)


@app.route("/api/members")
def api_members() -> Response:
    """Return all family members as a flat list."""
    members = get_all_members()
    return jsonify(members)


@app.route("/api/member/<int:member_id>")
def api_member(member_id: int) -> tuple[Response, int] | Response:
    """Return details for a single family member."""
    members = _get_members()
    if member_id in members:
        member = members[member_id]
        data = member.to_dict()

        if member.parent is not None and member.parent in members:
            data["parent_name"] = members[member.parent].name
        else:
            data["parent_name"] = None

        data["children_names"] = [
            members[cid].name for cid in member.children if cid in members
        ]

        parents = member.get_parents()
        data["parents"] = [{"id": p[0], "name": p[1]} for p in parents]

        return jsonify(data)
    return jsonify({"error": "Member not found"}), 404


@app.route("/api/search")
def api_search() -> Response:
    """Search family members by name."""
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])

    members = _get_members()
    results: list[dict[str, object]] = []
    for member in members.values():
        if query in member.name.lower():
            results.append(
                {
                    "id": member.id,
                    "name": member.name,
                    "gender": member.gender,
                    "vital_stats": member.vital_stats,
                }
            )
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)
