from app.core.santa_draw import generate_secret_santa_draw

def test_draw_simple():
    participants = [
        {"participant_id": "p1", "name": "Ana", "excluded_participant_ids": []},
        {"participant_id": "p2", "name": "Bruno", "excluded_participant_ids": []},
        {"participant_id": "p3", "name": "Carla", "excluded_participant_ids": []},
    ]
    draw = generate_secret_santa_draw(participants)
    assert draw is not None
    assert len(draw) == 3
    # Asegurar que nadie se regala a sí mismo
    for giver, receiver in draw.items():
        assert giver != receiver

def test_draw_with_exclusions():
    participants = [
        {"participant_id": "p1", "name": "Ana", "excluded_participant_ids": ["p2"]}, # Ana ya le regaló a Bruno
        {"participant_id": "p2", "name": "Bruno", "excluded_participant_ids": ["p3"]}, # Bruno ya le regaló a Carla
        {"participant_id": "p3", "name": "Carla", "excluded_participant_ids": ["p1"]}, # Carla ya le regaló a Ana
    ]
    draw = generate_secret_santa_draw(participants)
    assert draw is not None
    # Ana debe regalarle a Carla (única opción ya que no puede dar a sí misma ni a p2)
    assert draw["p1"] == "p3"
    assert draw["p2"] == "p1"
    assert draw["p3"] == "p2"

def test_draw_impossible():
    participants = [
        {"participant_id": "p1", "name": "Ana", "excluded_participant_ids": ["p2", "p3"]},
        {"participant_id": "p2", "name": "Bruno", "excluded_participant_ids": []},
        {"participant_id": "p3", "name": "Carla", "excluded_participant_ids": []},
    ]
    draw = generate_secret_santa_draw(participants)
    # Ana no tiene a quién regalarle (excluyó a p2 y p3, y no puede regalarse a sí misma p1)
    assert draw is None

if __name__ == "__main__":
    test_draw_simple()
    test_draw_with_exclusions()
    test_draw_impossible()
    print("¡Todas las pruebas unitarias pasaron con éxito!")
