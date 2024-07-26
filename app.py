"""Create a family tree from google sheets.

Classes:
    Person: Represent a person in the family tree.

Functions:
    main: Create a family class list from JSON.
"""

import json
from typing import Union


class Person:
    """Represent a person in the family tree."""

    members: list = list()

    def __init__(self, id: int, name: str, gender: str, vital_stats: str):
        """Initialize the person object."""
        self.id = id
        self.name = name
        self.gender = gender
        self.vital_stats = vital_stats
        self.parent: Union[None, int] = None
        self.spouse: Union[None, int] = None
        self.children: list[int] = []

    def add_parent(self, parent: "Person"):
        """Add a parent to the person."""
        self.parent = parent.id
        parent.children.append(self.id)

    def add_spouse(self, spouse: "Person"):
        """Add a spouse to the person."""
        self.spouse = spouse.id
        spouse.spouse = self.id

    def add_child(self, child: "Person"):
        """Add a child to the person."""
        self.children.append(child.id)
        child.parent = self.id

    def get_parent(self):
        """Return the parent of the person."""
        return self.parent

    def get_parents(self):
        """Return the parents of the person.

        Return the parents of the person including the spouse of the parent.
        """
        parents = []
        if self.parent:
            parents.append((self.parent, Person.members[self.parent].name))
            ps = Person.members[self.parent].get_spouse()
            if ps:
                parents.append(ps)
        return parents

    def get_spouse(self):
        """Return the spouse of the person."""
        if self.spouse:
            return (self.spouse, Person.members[self.spouse].name)
        return None

    def get_children(self):
        """Return the children of the person."""
        chidren = []
        chidren.extend([(child, Person.members[child].name) for child in self.children])
        spouse = self.get_spouse()
        if spouse:
            chidren.extend(
                [
                    (child, Person.members[child].name)
                    for child in Person.members[spouse[0]].children
                ]
            )
        return chidren

    @classmethod
    def get_member_count(cls):
        """Return the count of family members."""
        return len(cls.members)

    def __repr__(self):
        """Return the string representation of the person."""
        return self.name


def create_family():
    """Create a family tree from JSON."""
    print("Creating a family tree from JSON")
    family_members = json.load(open("family_members.json"))
    family = [Person(int(row[0]), row[1], row[2], row[4]) for row in family_members]
    Person.members = {member.id: member for member in family}
    print(f"Total family members: {Person.get_member_count()}")

    # Add parent, spouse, and children
    for row in family_members:
        if row[11]:
            # print(row)
            # print(
            #     f"Adding parent: {Person.members[int(row[11])]} to child: {Person.members[int(row[0])]}"
            # )
            child = Person.members[int(row[0])]
            parent = Person.members[int(row[11])]
            child.add_parent(parent)
        if row[12]:
            # print(row)
            # print(
            #     f"Adding spouse: {Person.members[int(row[12])]} to member: {Person.members[int(row[0])]}"
            # )
            person = Person.members[int(row[0])]
            spouse = Person.members[int(row[12])]
            person.add_spouse(spouse)

    return Person.members


def main():
    """Create a family tree from JSON."""
    create_family()
    # Print the family tree
    for i in Person.members:
        print(
            f"""
            {i}
            Name: {Person.members[i]}
            Parents: {Person.members[i].get_parents()}
            Spouse: {Person.members[i].get_spouse()}
            Children: {Person.members[i].get_children()}"""
        )


if __name__ == "__main__":
    main()
