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

# export deployment env variables
if [ -f secret-deploy.env ]; then
    export $(cat secret-deploy.env | xargs)
else
    echo "secret-deploy.env not found."
    exit 1
fi

# build the react app
cd frontend
npm run build
if [ $? -ne 0 ]; then
    exit 1
fi

# upload the built app to the AWS bucket
echo "Uploading to s3://${AWS_BUCKET}..."
aws s3 cp dist s3://${AWS_BUCKET} --recursive
if [ $? -ne 0 ]; then
    exit 1
fi

echo "Creating CloudFront invalidation..."

# create a CloudFront invalidation to update the app's frontend
aws cloudfront create-invalidation --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} --paths "/*"
echo "Waiting for CloudFront invalidation to complete (this can take up to 5 minutes)..."

# check each second until the status of the invalidation changes
until [ $(aws cloudfront list-invalidations --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} | jq -r ".InvalidationList.Items[0].Status") != "InProgress" ]
do
  sleep 1
done
aws cloudfront list-invalidations --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} | jq -r ".InvalidationList.Items[0]"
