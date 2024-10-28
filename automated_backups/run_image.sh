docker build --platform linux/amd64 -t automated-backups:test .
docker run --rm \
    --platform linux/amd64 \
    --name automated-backups-test \
    -p 9000:8080 \
    -e AWS_REGION=us-east-1 \
    automated-backups:test
