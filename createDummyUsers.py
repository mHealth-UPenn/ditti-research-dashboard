import json

x = {  
    "tapPermission": True,
    "information": "string",
    "userPermissionId": "",
    "expTime": "2025-01-01T00:00:00.000Z",
    "teamEmail": "msii@fakeemail.com",
    "createdAt": "",
}

users = [x.copy() for _ in range(8)]

for i in range(0, 8):
    users[i]["userPermissionId"] = f"msii00{i + 1}"

with open("dummyUsers.json", "w") as f:
    json.dump(users, f, indent=4)
