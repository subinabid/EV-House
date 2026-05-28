"""Person model for the EV House family tree."""

from __future__ import annotations


class Person:
    """Represent a person in the family tree."""

    members: dict[int, Person] = {}

    def __init__(self, id: int, name: str, gender: str, vital_stats: str) -> None:
        """Initialize the person object."""
        self.id = id
        self.name = name
        self.gender = gender
        self.vital_stats = vital_stats
        self.parent: int | None = None
        self.spouse: int | None = None
        self.children: list[int] = []

    def add_parent(self, parent: Person) -> None:
        """Add a parent to the person."""
        self.parent = parent.id
        parent.children.append(self.id)

    def add_spouse(self, spouse: Person) -> None:
        """Add a spouse to the person (bidirectional)."""
        self.spouse = spouse.id
        spouse.spouse = self.id

    def add_child(self, child: Person) -> None:
        """Add a child to the person."""
        self.children.append(child.id)
        child.parent = self.id

    def get_parent(self) -> int | None:
        """Return the parent of the person."""
        return self.parent

    def get_parents(self) -> list[tuple[int, str]]:
        """Return the parents including the spouse of the parent."""
        parents: list[tuple[int, str]] = []
        if self.parent:
            parents.append((self.parent, Person.members[self.parent].name))
            ps = Person.members[self.parent].get_spouse()
            if ps:
                parents.append(ps)
        return parents

    def get_spouse(self) -> tuple[int, str] | None:
        """Return the spouse of the person."""
        if self.spouse:
            return (self.spouse, Person.members[self.spouse].name)
        return None

    def get_children(self) -> list[tuple[int, str]]:
        """Return the children of the person."""
        children: list[tuple[int, str]] = []
        children.extend(
            [(child, Person.members[child].name) for child in self.children]
        )
        spouse = self.get_spouse()
        if spouse:
            children.extend(
                [
                    (child, Person.members[child].name)
                    for child in Person.members[spouse[0]].children
                ]
            )
        return children

    def to_dict(self) -> dict[str, object]:
        """Return the person as a dictionary."""
        spouse_info = self.get_spouse()
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "vital_stats": self.vital_stats,
            "parent": self.parent,
            "spouse": self.spouse,
            "spouse_name": spouse_info[1] if spouse_info else None,
            "children": self.children,
        }

    @classmethod
    def get_member_count(cls) -> int:
        """Return the count of family members."""
        return len(cls.members)

    def __repr__(self) -> str:
        """Return the string representation of the person."""
        return f"{self.id} - {self.name}"
