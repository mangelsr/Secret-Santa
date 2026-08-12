from app.core.santa_draw import generate_secret_santa_draw

def test_draw_simple():
    participants = [
        {"participant_id": "p1", "name": "Alice", "excluded_participant_ids": []},
        {"participant_id": "p2", "name": "Bob", "excluded_participant_ids": []},
        {"participant_id": "p3", "name": "Charlie", "excluded_participant_ids": []},
    ]
    draw = generate_secret_santa_draw(participants)
    assert draw is not None
    assert len(draw) == 3
    # Ensure nobody gives a gift to themselves
    for giver, receiver in draw.items():
        assert giver != receiver

def test_draw_with_exclusions():
    participants = [
        {"participant_id": "p1", "name": "Alice", "excluded_participant_ids": ["p2"]}, # Alice gifted Bob past year
        {"participant_id": "p2", "name": "Bob", "excluded_participant_ids": ["p3"]},   # Bob gifted Charlie past year
        {"participant_id": "p3", "name": "Charlie", "excluded_participant_ids": ["p1"]},# Charlie gifted Alice past year
    ]
    draw = generate_secret_santa_draw(participants)
    assert draw is not None
    # Alice must give to Charlie (only valid option since she excluded p2 and cannot give to herself)
    assert draw["p1"] == "p3"
    assert draw["p2"] == "p1"
    assert draw["p3"] == "p2"

def test_draw_impossible():
    participants = [
        {"participant_id": "p1", "name": "Alice", "excluded_participant_ids": ["p2", "p3"]},
        {"participant_id": "p2", "name": "Bob", "excluded_participant_ids": []},
        {"participant_id": "p3", "name": "Charlie", "excluded_participant_ids": []},
    ]
    draw = generate_secret_santa_draw(participants)
    # Alice has no valid targets left
    assert draw is None

if __name__ == "__main__":
    test_draw_simple()
    test_draw_with_exclusions()
    test_draw_impossible()
    print("All unit tests passed successfully!")
