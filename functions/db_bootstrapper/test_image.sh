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

RequestType="Create"

while [[ $# -gt 0 ]]; do
    case $1 in
        --request-type)
            RequestType=$2
            shift
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# RequestType must be one of: Create, Update, Delete
if [[ ! "$RequestType" =~ ^(Create|Update|Delete)$ ]]; then
    echo "Invalid request type: $RequestType. Must be one of: Create, Update, Delete."
    exit 1
fi

curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{
  "RequestType": "'${RequestType}'",
  "ResponseURL": "http://pre-signed-S3-url-for-response",
  "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/MyStack/guid",
  "RequestId": "unique id for this create request",
  "ResourceType": "Custom::TestResource",
  "LogicalResourceId": "MyTestResource"
}'
