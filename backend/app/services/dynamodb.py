import boto3
from typing import List, Optional, Dict, Any
from app.core.config import settings

class DynamoDBService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.GROUPS_TABLE)

    def create_group(self, group_id: str, name: str, admin_email: str, admin_passcode: str, created_at: str) -> Dict[str, Any]:
        item = {
            "PK": f"GROUP#{group_id}",
            "SK": "METADATA",
            "group_id": group_id,
            "name": name,
            "admin_email": admin_email,
            "admin_passcode": admin_passcode,
            "status": "OPEN",
            "created_at": created_at
        }
        self.table.put_item(Item=item)
        return item

    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        response = self.table.get_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": "METADATA"
            }
        )
        return response.get("Item")

    def add_participant(self, group_id: str, participant_id: str, name: str, email: str, excluded_participant_ids: List[str], created_at: str) -> Dict[str, Any]:
        item = {
            "PK": f"GROUP#{group_id}",
            "SK": f"PARTICIPANT#{participant_id}",
            "participant_id": participant_id,
            "group_id": group_id,
            "name": name,
            "email": email,
            "excluded_participant_ids": excluded_participant_ids,
            "created_at": created_at
        }
        self.table.put_item(Item=item)
        return item

    def get_participants(self, group_id: str) -> List[Dict[str, Any]]:
        response = self.table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
            ExpressionAttributeValues={
                ":pk": f"GROUP#{group_id}",
                ":sk_prefix": "PARTICIPANT#"
            }
        )
        return response.get("Items", [])

    def delete_participant(self, group_id: str, participant_id: str):
        self.table.delete_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": f"PARTICIPANT#{participant_id}"
            }
        )

    def close_group(self, group_id: str):
        self.table.update_item(
            Key={
                "PK": f"GROUP#{group_id}",
                "SK": "METADATA"
            },
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": "CLOSED"}
        )

db_service = DynamoDBService()
