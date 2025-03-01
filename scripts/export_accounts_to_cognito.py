import csv
import os
import re


def format_phone_number(phone):
    """
    Format phone numbers according to AWS Cognito requirements.
    Phone numbers must start with + followed by country code and only contain digits.
    """
    if not phone:
        return ""

    # Remove all non-digit characters except the plus sign
    formatted = re.sub(r'[^\d+]', '', phone)

    # Ensure the phone number starts with a plus sign
    if not formatted.startswith('+'):
        # Assume US number if no country code is provided
        formatted = '+1' + formatted

    return formatted


def export_accounts_to_csv(accounts, template_path, output_path="cognito_users_import.csv"):
    """
    Export accounts to a CSV file compatible with AWS Cognito import.

    Args:
        accounts: List of Account objects to export
        template_path: Path to the CSV template file
        output_path: Output CSV filename

    Returns:
        int: Number of accounts exported
    """
    # Read the template file headers
    with open(template_path, 'r') as template_file:
        headers = next(csv.reader(template_file))

    # Create the output file
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for account in accounts:
            # Create a row with default empty values for all columns
            row = {header: "" for header in headers}

            # Map account fields to Cognito fields
            row["given_name"] = account.first_name
            row["family_name"] = account.last_name
            row["email"] = account.email
            row["cognito:username"] = account.email
            row["phone_number"] = format_phone_number(account.phone_number)

            # Set required constant fields
            row["email_verified"] = "TRUE"
            row["cognito:mfa_enabled"] = "FALSE"

            writer.writerow(row)

    return len(accounts)
