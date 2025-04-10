# export deployment env variables
if [ -f secret-staging.env ]; then
    export $(cat secret-staging.env | xargs)
else
    echo "secret-staging.env not found."
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
aws s3 cp build s3://${AWS_BUCKET} --recursive
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
