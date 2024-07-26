"""Test the app module."""

from app import Person


def test_person():
    """Test the Person class."""
    person = Person(1, "John Doe", "M", "")
    assert person.id == 1
    assert person.name == "John Doe"


def test_add_parent():
    """Test the add_parent method of the Person class."""
    parent = Person(1, "John Doe", "M", "")
    child1 = Person(2, "Jane Doe", "F", "")
    child2 = Person(3, "Jack Doe", "M", "")
    child1.add_parent(parent)
    child2.add_parent(parent)
    assert child1.parent == 1
    assert child2.parent == 1
    assert parent.children == [2, 3]


def test_add_spouse():
    """Test the add_spouse method of the Person class."""
    person1 = Person(1, "John Doe", "M", "")
    person2 = Person(2, "Jane Doe", "F", "")
    person1.add_spouse(person2)
    assert person1.spouse == 2
    assert person2.spouse == 1


def test_add_child():
    """Test the add_child method of the Person class."""
    parent = Person(1, "John Doe", "M", "")
    child1 = Person(2, "Jane Doe", "F", "")
    child2 = Person(3, "Jack Doe", "M", "")
    parent.add_child(child1)
    parent.add_child(child2)
    assert parent.children == [2, 3]
    assert child1.parent == 1
    assert child2.parent == 1


def test_get_parent():
    """Test the get_parent method of the Person class."""
    parent = Person(1, "John Doe", "M", "")
    child = Person(2, "Jane Doe", "F", "")
    child.add_parent(parent)
    assert child.get_parent() == 1


def test_get_parents():
    """Test the get_parents method of the Person class."""
    parent = Person(1, "John Doe", "M", "")
    spouse = Person(2, "Jane Doe", "F", "")
    child = Person(3, "Jack Doe", "F", "")
    parent.add_spouse(spouse)
    child.add_parent(parent)
    Person.members = {1: parent, 2: spouse, 3: child}
    assert child.get_parents() == [(1, "John Doe"), (2, "Jane Doe")]


def test_get_spouse():
    """Test the get_spouse method of the Person class."""
    person1 = Person(1, "John Doe", "M", "")
    person2 = Person(2, "Jane Doe", "F", "")
    person1.add_spouse(person2)
    assert person1.get_spouse() == (2, "Jane Doe")


def test_get_children():
    """Test the get_children method of the Person class."""
    parent = Person(1, "John Doe", "M", "")
    spouse = Person(2, "Jane Doe", "F", "")
    child1 = Person(3, "Jack Doe", "M", "")
    child2 = Person(4, "Jill Doe", "F", "")
    parent.add_spouse(spouse)
    parent.add_child(child1)
    parent.add_child(child2)
    Person.members = {1: parent, 2: spouse, 3: child1, 4: child2}
    assert parent.get_children() == [(3, "Jack Doe"), (4, "Jill Doe")]
    assert spouse.get_children() == [(3, "Jack Doe"), (4, "Jill Doe")]


def test_get_member_count():
    """Test the get_member_count method of the Person class."""
    Person.members = [{1: Person(1, "John Doe", "M", "")}]
    assert Person.get_member_count() == 1
    Person.members = []
    assert Person.get_member_count() == 0
