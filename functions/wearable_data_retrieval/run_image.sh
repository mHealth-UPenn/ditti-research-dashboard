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
rm -rf shared

docker run --rm \
    --platform linux/amd64 \
    --name wearable-data-retrieval-test \
    -p 9000:8080 \
    -e TESTING=true \
    wearable-data-retrieval:test
