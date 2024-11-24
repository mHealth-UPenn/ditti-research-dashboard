NOCACHE=0

# parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NOCACHE=1
            shift
            ;;
        -*|--*)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

cp -r ../../shared shared
if [ $NOCACHE -eq 1 ]; then
    docker build --platform linux/amd64 --no-cache -t wearable-data-retrieval:test .
else
    docker build --platform linux/amd64 -t wearable-data-retrieval:test .
fi
if [ $? -ne 0 ]; then
    rm -rf shared
    exit 1
fi
rm -rf shared

export $(cat .env | xargs)

docker run --rm \
    --platform linux/amd64 \
    --name wearable-data-retrieval-test \
    --network aws-network \
    -p 9000:8080 \
    -e DB_URI=$DB_URI \
    -e TESTING=true \
    wearable-data-retrieval:test
