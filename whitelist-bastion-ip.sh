#!/bin/bash

# Script to manage IP whitelisting for bastion host security group
# Usage: ./whitelist-bastion-ip.sh <action> <ip> [description]
# Actions: add, remove, list
# Example: ./whitelist-bastion-ip.sh add 203.0.113.1/32 "Office IP"

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

# Function to get the security group ID
get_security_group_id() {
    local app_name="$1"
    local environment="$2"
    local sg_name="${app_name}-${environment}-bastion-sg"

    aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=$sg_name" \
        --query 'SecurityGroups[0].GroupId' \
        --output text
}

# Function to validate IP address format
validate_ip() {
    local ip="$1"
    if [[ ! $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$ ]]; then
        echo "Error: Invalid IP format. Use CIDR notation (e.g., 203.0.113.1/32)"
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
        --protocol tcp \
        --port 22 \
        --cidr "$ip" \
        --tag-specifications "ResourceType=security-group-rule,Tags=[{Key=Description,Value=$description}]"
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
    echo "Usage: $0 <action> <ip> [description]"
    echo "Actions: add, remove, list"
    echo "Example: $0 add 203.0.113.1/32 \"Office IP\""
    exit 1
fi

ACTION="$1"
IP="$2"
DESCRIPTION="${3:-Manual addition}"

# Get security group ID
SG_ID=$(get_security_group_id "ditti-dashboard" "staging")

if [ -z "$SG_ID" ]; then
    echo "Error: Could not find security group"
    exit 1
fi

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
