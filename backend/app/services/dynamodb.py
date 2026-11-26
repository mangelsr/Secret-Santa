from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError

from app.core.config import settings

_serializer = TypeSerializer()


def _serialize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize a Python dict into DynamoDB low-level AttributeValue format."""
    return {k: _serializer.serialize(v) for k, v in data.items()}


class GroupNotFoundError(Exception):
    """Raised when the target group does not exist."""


class GroupClosedError(Exception):
    """Raised when an operation requires an OPEN group."""


class DuplicateEmailError(Exception):
    """Raised when an email is already registered in the group."""


class ParticipantNotFoundError(Exception):
    """Raised when the target participant does not exist."""


class DrawAlreadyInProgressError(Exception):
    """Raised when a draw cannot be started due to concurrent or invalid state."""


class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.GROUPS_TABLE)

    @property
    def client(self):
        return self.table.meta.client

    def create_group(
        self,
        group_id: str,
        name: str,
        admin_email: str,
        admin_passcode_hash: str,
        created_at: str,
    ) -> Dict[str, Any]:
        item = {
            "PK": f"GROUP#{group_id}",
            "SK": "METADATA",
            "group_id": group_id,
            "name": name,
            "admin_email": admin_email,
            "admin_passcode": admin_passcode_hash,
            "status": "OPEN",
            "failed_passcode_attempts": 0,
            "passcode_locked_until": 0,
            "created_at": created_at,
            "updated_at": created_at,
        }
        self.table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(PK)",
        )
        return item

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": "METADATA",
            }
        )
        return response.get("Item")

    def record_failed_passcode_attempt(
        self,
        group_id: str,
        max_attempts: int,
        lockout_seconds: int,
        now_ts: int,
    ) -> int:
        response = self.table.update_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": "METADATA",
            },
            UpdateExpression=(
                "SET failed_passcode_attempts = "
                "if_not_exists(failed_passcode_attempts, :zero) + :one"
            ),
            ExpressionAttributeValues={":zero": 0, ":one": 1},
            ReturnValues="ALL_NEW",
        )
        attempts = int(response.get("Attributes", {}).get("failed_passcode_attempts", 1))
        if attempts >= max_attempts:
            self.table.update_item(
                Key={
                    "PK": f"GROUP#{group_id}",
                    "SK": "METADATA",
                },
                UpdateExpression="SET passcode_locked_until = :until",
                ExpressionAttributeValues={":until": now_ts + lockout_seconds},
            )
        return attempts

    def reset_passcode_attempts(self, group_id: str) -> None:
        self.table.update_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": "METADATA",
            },
            UpdateExpression="SET failed_passcode_attempts = :zero, passcode_locked_until = :zero",
            ExpressionAttributeValues={":zero": 0},
        )

    def add_participant(
        self,
        group_id: str,
        participant_id: str,
        name: str,
        email: str,
        excluded_participant_ids: List[str],
        created_at: str,
        edit_passcode_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        email_lower = email.strip().lower()
        participant_item: Dict[str, Any] = {
            "PK": f"GROUP#{group_id}",
            "SK": f"PARTICIPANT#{participant_id}",
            "participant_id": participant_id,
            "group_id": group_id,
            "name": name,
            "email": email,
            "excluded_participant_ids": excluded_participant_ids,
            "created_at": created_at,
        }
        if edit_passcode_hash:
            participant_item["edit_passcode_hash"] = edit_passcode_hash

        email_lock_item = {
            "PK": f"GROUP#{group_id}",
            "SK": f"EMAIL#{email_lower}",
            "participant_id": participant_id,
            "email": email_lower,
        }

        try:
            self.client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": _serialize_dict(
                                {"PK": f"GROUP#{group_id}", "SK": "METADATA"}
                            ),
                            "UpdateExpression": "SET updated_at = :now",
                            "ConditionExpression": "attribute_exists(PK) AND #s = :open",
                            "ExpressionAttributeNames": {"#s": "status"},
                            "ExpressionAttributeValues": _serialize_dict(
                                {":now": created_at, ":open": "OPEN"}
                            ),
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.table.name,
                            "Item": _serialize_dict(email_lock_item),
                            "ConditionExpression": "attribute_not_exists(PK)",
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.table.name,
                            "Item": _serialize_dict(participant_item),
                            "ConditionExpression": "attribute_not_exists(PK)",
                        }
                    },
                ]
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                reasons = exc.response.get("CancellationReasons", [])
                if len(reasons) > 0 and reasons[0].get("Code") == "ConditionalCheckFailed":
                    raise GroupClosedError("Group is closed or does not exist") from exc
                if len(reasons) > 1 and reasons[1].get("Code") == "ConditionalCheckFailed":
                    raise DuplicateEmailError("Email already registered in group") from exc
            raise

        return participant_item

    def _query_by_sk_prefix(self, group_id: str, sk_prefix: str) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        query_kwargs: Dict[str, Any] = {
            "KeyConditionExpression": "PK = :pk AND begins_with(SK, :sk_prefix)",
            "ExpressionAttributeValues": {
                ":pk": f"GROUP#{group_id}",
                ":sk_prefix": sk_prefix,
            },
        }
        while True:
            response = self.table.query(**query_kwargs)
            items.extend(response.get("Items", []))
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            query_kwargs["ExclusiveStartKey"] = last_key
        return items

    def get_participants(self, group_id: str) -> List[Dict[str, Any]]:
        return self._query_by_sk_prefix(group_id, "PARTICIPANT#")

    def get_participant(self, group_id: str, participant_id: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": f"PARTICIPANT#{participant_id}",
            }
        )
        return response.get("Item")

    def update_participant(
        self,
        group_id: str,
        participant_id: str,
        name: str,
        email: str,
        excluded_participant_ids: List[str],
        old_email: str,
        updated_at: str,
    ) -> Dict[str, Any]:
        old_email_lower = old_email.strip().lower()
        new_email_lower = email.strip().lower()

        transact_items: List[Dict[str, Any]] = [
            {
                "Update": {
                    "TableName": self.table.name,
                    "Key": _serialize_dict({"PK": f"GROUP#{group_id}", "SK": "METADATA"}),
                    "UpdateExpression": "SET updated_at = :now",
                    "ConditionExpression": "attribute_exists(PK) AND #s = :open",
                    "ExpressionAttributeNames": {"#s": "status"},
                    "ExpressionAttributeValues": _serialize_dict(
                        {":now": updated_at, ":open": "OPEN"}
                    ),
                }
            },
            {
                "Update": {
                    "TableName": self.table.name,
                    "Key": _serialize_dict(
                        {"PK": f"GROUP#{group_id}", "SK": f"PARTICIPANT#{participant_id}"}
                    ),
                    "UpdateExpression": "SET #n = :name, #e = :email, #ex = :ex, updated_at = :now",
                    "ConditionExpression": "attribute_exists(PK)",
                    "ExpressionAttributeNames": {
                        "#n": "name",
                        "#e": "email",
                        "#ex": "excluded_participant_ids",
                    },
                    "ExpressionAttributeValues": _serialize_dict(
                        {
                            ":name": name,
                            ":email": email,
                            ":ex": excluded_participant_ids,
                            ":now": updated_at,
                        }
                    ),
                }
            },
        ]

        email_changed = new_email_lower != old_email_lower
        if email_changed:
            transact_items.append(
                {
                    "Put": {
                        "TableName": self.table.name,
                        "Item": _serialize_dict(
                            {
                                "PK": f"GROUP#{group_id}",
                                "SK": f"EMAIL#{new_email_lower}",
                                "participant_id": participant_id,
                                "email": new_email_lower,
                            }
                        ),
                        "ConditionExpression": "attribute_not_exists(PK)",
                    }
                }
            )
            transact_items.append(
                {
                    "Delete": {
                        "TableName": self.table.name,
                        "Key": _serialize_dict(
                            {"PK": f"GROUP#{group_id}", "SK": f"EMAIL#{old_email_lower}"}
                        ),
                    }
                }
            )

        try:
            self.client.transact_write_items(TransactItems=transact_items)
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                reasons = exc.response.get("CancellationReasons", [])
                if len(reasons) > 0 and reasons[0].get("Code") == "ConditionalCheckFailed":
                    raise GroupClosedError("Group is closed or does not exist") from exc
                if len(reasons) > 1 and reasons[1].get("Code") == "ConditionalCheckFailed":
                    raise ParticipantNotFoundError("Participant not found") from exc
                if email_changed and len(reasons) > 2 and reasons[2].get("Code") == "ConditionalCheckFailed":
                    raise DuplicateEmailError("Email already registered in group") from exc
            raise

        return {
            "participant_id": participant_id,
            "group_id": group_id,
            "name": name,
            "email": email,
            "excluded_participant_ids": excluded_participant_ids,
        }

    def delete_participant(
        self,
        group_id: str,
        participant_id: str,
        email: str,
        updated_at: str,
    ) -> None:
        email_lower = email.strip().lower()
        try:
            self.client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": _serialize_dict(
                                {"PK": f"GROUP#{group_id}", "SK": "METADATA"}
                            ),
                            "UpdateExpression": "SET updated_at = :now",
                            "ConditionExpression": "attribute_exists(PK) AND #s = :open",
                            "ExpressionAttributeNames": {"#s": "status"},
                            "ExpressionAttributeValues": _serialize_dict(
                                {":now": updated_at, ":open": "OPEN"}
                            ),
                        }
                    },
                    {
                        "Delete": {
                            "TableName": self.table.name,
                            "Key": _serialize_dict(
                                {"PK": f"GROUP#{group_id}", "SK": f"PARTICIPANT#{participant_id}"}
                            ),
                            "ConditionExpression": "attribute_exists(PK)",
                        }
                    },
                    {
                        "Delete": {
                            "TableName": self.table.name,
                            "Key": _serialize_dict(
                                {"PK": f"GROUP#{group_id}", "SK": f"EMAIL#{email_lower}"}
                            ),
                        }
                    },
                ]
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                reasons = exc.response.get("CancellationReasons", [])
                if len(reasons) > 0 and reasons[0].get("Code") == "ConditionalCheckFailed":
                    raise GroupClosedError("Group is closed or does not exist") from exc
                if len(reasons) > 1 and reasons[1].get("Code") == "ConditionalCheckFailed":
                    raise ParticipantNotFoundError("Participant not found") from exc
            raise

    def begin_draw(self, group_id: str, assignments: Dict[str, str], now_iso: str) -> None:
        """Atomically lock the group from OPEN to DRAWING and persist all draw assignments."""
        assignment_items = [
            {
                "PK": f"GROUP#{group_id}",
                "SK": f"ASSIGNMENT#{giver_id}",
                "giver_id": giver_id,
                "receiver_id": receiver_id,
                "delivery_status": "PENDING",
                "updated_at": now_iso,
            }
            for giver_id, receiver_id in assignments.items()
        ]

        if len(assignment_items) <= 99:
            transact_items: List[Dict[str, Any]] = [
                {
                    "Update": {
                        "TableName": self.table.name,
                        "Key": _serialize_dict({"PK": f"GROUP#{group_id}", "SK": "METADATA"}),
                        "UpdateExpression": "SET #s = :drawing, updated_at = :now",
                        "ConditionExpression": "attribute_exists(PK) AND #s = :open",
                        "ExpressionAttributeNames": {"#s": "status"},
                        "ExpressionAttributeValues": _serialize_dict(
                            {":drawing": "DRAWING", ":open": "OPEN", ":now": now_iso}
                        ),
                    }
                }
            ]
            for item in assignment_items:
                transact_items.append(
                    {
                        "Put": {
                            "TableName": self.table.name,
                            "Item": _serialize_dict(item),
                            "ConditionExpression": "attribute_not_exists(PK)",
                        }
                    }
                )
            try:
                self.client.transact_write_items(TransactItems=transact_items)
            except ClientError as exc:
                if exc.response.get("Error", {}).get("Code") == "TransactionCanceledException":
                    raise DrawAlreadyInProgressError(
                        "Group is no longer OPEN for drawing"
                    ) from exc
                raise
            return

        # Fallback for >99 participants: lock METADATA conditionally, then batch-write assignments
        try:
            self.table.update_item(
                Key={"PK": f"GROUP#{group_id}", "SK": "METADATA"},
                UpdateExpression="SET #s = :drawing, updated_at = :now",
                ConditionExpression="attribute_exists(PK) AND #s = :open",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":drawing": "DRAWING", ":open": "OPEN", ":now": now_iso},
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise DrawAlreadyInProgressError("Group is no longer OPEN for drawing") from exc
            raise

        with self.table.batch_writer() as batch:
            for item in assignment_items:
                batch.put_item(Item=item)

    def acquire_retry_draw(self, group_id: str, now_iso: str) -> None:
        """Atomically transition DRAW_PARTIAL -> DRAWING so retries cannot overlap."""
        try:
            self.table.update_item(
                Key={"PK": f"GROUP#{group_id}", "SK": "METADATA"},
                UpdateExpression="SET #s = :drawing, updated_at = :now",
                ConditionExpression="attribute_exists(PK) AND #s = :partial",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":drawing": "DRAWING",
                    ":partial": "DRAW_PARTIAL",
                    ":now": now_iso,
                },
            )
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise DrawAlreadyInProgressError(
                    "Draw retry already in progress or group is closed"
                ) from exc
            raise

    def get_assignments(self, group_id: str) -> List[Dict[str, Any]]:
        return self._query_by_sk_prefix(group_id, "ASSIGNMENT#")

    def update_assignment_status(
        self, group_id: str, giver_id: str, delivery_status: str, now_iso: str
    ) -> None:
        self.table.update_item(
            Key={"PK": f"GROUP#{group_id}", "SK": f"ASSIGNMENT#{giver_id}"},
            UpdateExpression="SET delivery_status = :ds, updated_at = :now",
            ExpressionAttributeValues={":ds": delivery_status, ":now": now_iso},
        )

    def finalize_draw_status(self, group_id: str, new_status: str, now_iso: str) -> None:
        self.table.update_item(
            Key={"PK": f"GROUP#{group_id}", "SK": "METADATA"},
            UpdateExpression="SET #s = :status, updated_at = :now",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": new_status, ":now": now_iso},
        )

    def close_group(self, group_id: str, now_iso: str = "") -> None:
        self.finalize_draw_status(group_id, "CLOSED", now_iso)


db_service = DynamoDBService()
