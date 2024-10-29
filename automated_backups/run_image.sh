export $(cat secrets-aws.env | xargs)


docker build --platform linux/amd64 -t automated-backups:test .
docker run --rm \
    --platform linux/amd64 \
    --name automated-backups-test \
    -p 9000:8080 \
    -e AWS_REGION=$AWS_REGION \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_SECRET_NAME=$AWS_SECRET_NAME \
    -e TESTING=true \
    -e TEST_EMAIL=$TEST_EMAIL \
    automated-backups:test
