# Copyright 2025 The Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may]
# not use this file except in compliance with the License. You may obtain a
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

# Script to manage IP whitelisting for NAT instance and bastion host security group
# Usage: ./whitelist-bastion-ip.sh [security-group-id] <action> <ip> [description]
# Actions: add, remove, list
# Examples: 
#   ./whitelist-bastion-ip.sh sg-01234567890abcdef0 add 203.0.113.1/32 "Office IP"

set -e

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed"
    exit 1
fi

# Function to validate IP address format
validate_ip() {
    local ip="$1"
    if [[ ! $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]]; then
        echo "Error: Invalid IP format. Use CIDR notation (e.g., 203.0.113.1/32)"
        exit 1
    fi
}

# Function to validate security group ID format
validate_sg_id() {
    local sg_id="$1"
    if [[ ! $sg_id =~ ^sg-[a-f0-9]{17}$ ]]; then
        echo "Error: Invalid security group ID format. Use format: sg-01234567890abcdef0"
        exit 1
    fi
}

# Function to add an IP
add_ip() {
    local ip="$1"
    local description="$2"
    local sg_id="$3"

    echo "Adding IP $ip to security group $sg_id..."
    aws ec2 authorize-security-group-ingress \
        --group-id "$sg_id" \
        --ip-permissions "[{\"IpProtocol\":\"tcp\",\"FromPort\":22,\"ToPort\":22,\"IpRanges\":[{\"CidrIp\":\"$ip\",\"Description\":\"$description\"}]}]"
    echo "IP $ip added successfully"
}

# Function to remove an IP
remove_ip() {
    local ip="$1"
    local sg_id="$2"

    echo "Removing IP $ip from security group $sg_id..."
    aws ec2 revoke-security-group-ingress \
        --group-id "$sg_id" \
        --protocol tcp \
        --port 22 \
        --cidr "$ip"
    echo "IP $ip removed successfully"
}

# Function to list all whitelisted IPs
list_ips() {
    local sg_id="$1"

    echo "Current whitelisted IPs:"
    aws ec2 describe-security-groups \
        --group-ids "$sg_id" \
        --query 'SecurityGroups[0].IpPermissions[?FromPort==`22`].IpRanges[].[CidrIp,Description]' \
        --output table
}

# Main script logic
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 [security-group-id] <action> <ip> [description]"
    echo "Actions: add, remove, list"
    echo ""
    echo "Examples:"
    echo "  $0 sg-01234567890abcdef0 add 203.0.113.1/32 \"Office IP\""
    exit 1
fi

SG_ID="$1"
ACTION="$2"
IP="$3"
DESCRIPTION="${4:-Manual addition}"

# Validate security group ID
validate_sg_id "$SG_ID"

echo "Using provided security group: $SG_ID"

case "$ACTION" in
    "add")
        validate_ip "$IP"
        add_ip "$IP" "$DESCRIPTION" "$SG_ID"
        ;;
    "remove")
        validate_ip "$IP"
        remove_ip "$IP" "$SG_ID"
        ;;
    "list")
        list_ips "$SG_ID"
        ;;
    *)
        echo "Error: Invalid action. Use 'add', 'remove', or 'list'"
        exit 1
        ;;
esac
