import random
from typing import Dict, List, Optional, Set


def generate_secret_santa_draw(participants: List[dict]) -> Optional[Dict[str, str]]:
    """
    Secret Santa Matching Algorithm with Historical Exclusion Constraints.

    Uses randomized candidate ordering combined with Minimum Remaining Values (MRV)
    and forward-checking pruning to solve constrained graphs efficiently.

    :param participants: List of dicts with 'participant_id', 'name', 'excluded_participant_ids'
    :return: Dictionary mapping giver_id -> receiver_id or None if graph cannot be solved.
    """
    if len(participants) < 3:
        return None

    p_ids = [p["participant_id"] for p in participants]
    random.shuffle(p_ids)

    valid_targets: Dict[str, List[str]] = {}
    for p in participants:
        p_id = p["participant_id"]
        exclusions = set(p.get("excluded_participant_ids", []))
        exclusions.add(p_id)  # Rule 1: Cannot give to oneself

        candidates = [target_id for target_id in p_ids if target_id not in exclusions]
        if not candidates:
            return None
        random.shuffle(candidates)
        valid_targets[p_id] = candidates

    assignment: Dict[str, str] = {}
    assigned_receivers: Set[str] = set()
    unassigned: List[str] = list(p_ids)

    def backtrack() -> bool:
        if not unassigned:
            return True

        # MRV heuristic: select the unassigned giver with the fewest remaining valid receivers
        best_giver = None
        best_candidates: Optional[List[str]] = None
        best_count = len(p_ids) + 1

        for giver in unassigned:
            remaining = [r for r in valid_targets[giver] if r not in assigned_receivers]
            count = len(remaining)
            if count == 0:
                return False  # Forward-checking prune: dead end
            if count < best_count:
                best_count = count
                best_giver = giver
                best_candidates = remaining
                if count == 1:
                    break

        assert best_giver is not None and best_candidates is not None
        unassigned.remove(best_giver)

        for receiver in best_candidates:
            assignment[best_giver] = receiver
            assigned_receivers.add(receiver)

            if backtrack():
                return True

            assigned_receivers.remove(receiver)
            del assignment[best_giver]

        unassigned.append(best_giver)
        return False

    if backtrack():
        return assignment
    return None
