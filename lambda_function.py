import base64
import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

# Configure TABLE_NAME in Lambda > Configuration > Environment variables.
TABLE_NAME = os.environ.get("TABLE_NAME", "Students")
table = boto3.resource("dynamodb").Table(TABLE_NAME)

PBKDF2_ROUNDS = 200_000


def response(status_code, body):
    """Return an API Gateway HTTP API compatible response."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def hash_password(password, salt_hex):
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        PBKDF2_ROUNDS,
    )
    return digest.hex()


def parse_body(event):
    raw_body = event.get("body") or "{}"

    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    try:
        parsed = json.loads(raw_body)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
        return {}


def signup(data):
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return response(400, {"message": "Name, email and password are required."})

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return response(400, {"message": "Enter a valid email address."})

    if len(password) < 6:
        return response(400, {"message": "Password must be at least 6 characters."})

    salt_hex = secrets.token_hex(16)
    item = {
        "email": email,
        "name": name,
        "salt": salt_hex,
        "password_hash": hash_password(password, salt_hex),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(email)",
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")
        if error_code == "ConditionalCheckFailedException":
            return response(409, {"message": "This email is already registered."})

        print("DynamoDB signup error:", error_code)
        return response(500, {"message": "Could not create the account."})

    return response(201, {"message": "Account created successfully."})


def signin(data):
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return response(400, {"message": "Email and password are required."})

    try:
        result = table.get_item(Key={"email": email})
    except ClientError as exc:
        print("DynamoDB signin error:", exc.response.get("Error", {}).get("Code"))
        return response(500, {"message": "Could not read the account."})

    item = result.get("Item")
    if not item:
        return response(401, {"message": "Invalid email or password."})

    expected_hash = item.get("password_hash", "")
    salt_hex = item.get("salt", "")

    try:
        actual_hash = hash_password(password, salt_hex)
    except (ValueError, TypeError):
        print("Stored password hash data is invalid.")
        return response(500, {"message": "Could not verify the account."})

    if not hmac.compare_digest(expected_hash, actual_hash):
        return response(401, {"message": "Invalid email or password."})

    # Demo response only: this project does not issue an authentication token.
    return response(
        200,
        {
            "message": "Sign in successful.",
            "student": {"name": item.get("name", ""), "email": item.get("email", "")},
        },
    )


def lambda_handler(event, context):
    path = event.get("rawPath") or event.get("path") or ""
    data = parse_body(event)

    print("Request path:", path)

    if path.endswith("/signup"):
        return signup(data)

    if path.endswith("/signin"):
        return signin(data)

    return response(404, {"message": "Route not found."})
