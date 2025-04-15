def template():
    with open("tests/test_data/test_cloudformation.yml", "r") as f:
        return f.read()


def parameters():
    return [
        {
            "ParameterKey": "TestParameter1",
            "ParameterValue": "test-parameter-1-value",
        },
        {
            "ParameterKey": "TestParameter2",
            "ParameterValue": "test-parameter-2-value",
        },
    ]


def outputs():
    return [
        {
            "Description": "ID of the test resource 1",
            "OutputKey": "TestResource1Id",
            "OutputValue": "test-parameter-1-value",
        },
        {
            "Description": "ID of the test resource 2",
            "OutputKey": "TestResource2Id",
            "OutputValue": "test-parameter-2-value",
        },
    ]
