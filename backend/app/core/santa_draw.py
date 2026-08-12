import random
from typing import Dict, List, Optional

def generate_secret_santa_draw(participants: List[dict]) -> Optional[Dict[str, str]]:
    """
    Secret Santa Matching Algorithm with Historical Exclusion Constraints.
    
    :param participants: List of dicts with 'participant_id', 'name', 'excluded_participant_ids'
    :return: Dictionary mapping giver_id -> receiver_id or None if graph cannot be solved.
    """
    if len(participants) < 3:
        return None

    p_ids = [p['participant_id'] for p in participants]
    random.shuffle(p_ids)

    valid_targets: Dict[str, List[str]] = {}
    for p in participants:
        p_id = p['participant_id']
        exclusions = set(p.get('excluded_participant_ids', []))
        exclusions.add(p_id)  # Rule 1: Cannot give to oneself
        
        # Valid candidates = All participants minus exclusions
        candidates = [target_id for target_id in p_ids if target_id not in exclusions]
        random.shuffle(candidates)
        valid_targets[p_id] = candidates

    assignment: Dict[str, str] = {}
    assigned_receivers = set()

    def backtrack(idx: int) -> bool:
        if idx == len(p_ids):
            return True

        giver = p_ids[idx]
        candidates = valid_targets[giver]

        for receiver in candidates:
            if receiver not in assigned_receivers:
                assignment[giver] = receiver
                assigned_receivers.add(receiver)

                if backtrack(idx + 1):
                    return True

                # Undo backtrack step
                assigned_receivers.remove(receiver)
                del assignment[giver]

        return False

    if backtrack(0):
        return assignment
    return None
