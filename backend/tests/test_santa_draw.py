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

def test_draw_mrv_large_constrained_and_impossible():
    # 30 participants where everyone excludes 27 others (only 2 valid targets each -> forced cycle)
    n = 30
    ids = [f"p{i}" for i in range(n)]
    constrained_participants = []
    for i in range(n):
        allowed = {ids[(i + 1) % n], ids[(i + 2) % n]}
        excluded = [pid for pid in ids if pid != ids[i] and pid not in allowed]
        constrained_participants.append(
            {"participant_id": ids[i], "name": f"User {i}", "excluded_participant_ids": excluded}
        )

    draw = generate_secret_santa_draw(constrained_participants)
    assert draw is not None
    assert len(draw) == n
    assert len(set(draw.values())) == n
    for p in constrained_participants:
        pid = p["participant_id"]
        assert draw[pid] != pid
        assert draw[pid] not in p["excluded_participant_ids"]

    # Impossible 30-participant graph: two participants can only gift the same single target
    impossible = [dict(p, excluded_participant_ids=list(p["excluded_participant_ids"])) for p in constrained_participants]
    impossible[0]["excluded_participant_ids"] = [pid for pid in ids if pid not in {ids[0], ids[5]}]
    impossible[1]["excluded_participant_ids"] = [pid for pid in ids if pid not in {ids[1], ids[5]}]
    assert generate_secret_santa_draw(impossible) is None

if __name__ == "__main__":
    test_draw_simple()
    test_draw_with_exclusions()
    test_draw_impossible()
    print("All unit tests passed successfully!")
