if [ -f secret-production.env ]; then
    export $(cat secret-production.env | xargs)
else
    echo "secret-production.env not found."
    exit 1
fi

if [ -f secret-aws.env ]; then
    export $(cat secret-aws.env | xargs)
else
    echo "secret-aws.env not found."
    exit 1
fi

cd aws_portal/frontend
npm run build
if [ $? -ne 0 ]; then
    exit 1
fi

aws s3 cp build/ s3://${AWS_BUCKET} --recursive
echo "Creating CloudFront invalidation..."
aws cloudfront create-invalidation --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} --paths "/*"
echo "Waiting for CloudFront invalidation to complete (this can take up to 5 minutes)..."
until [ $(aws cloudfront list-invalidations --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} | jq -r ".InvalidationList.Items[0].Status") != "InProgress" ]
do
  sleep 1s
done
aws cloudfront list-invalidations --distribution-id ${AWS_CLOUDFRONT_DISTRIBUTION_ID} | jq -r ".InvalidationList.Items[0]"
