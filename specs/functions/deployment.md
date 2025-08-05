# Deployment

Lambda functions are deployed using CloudFormation templates with separate stacks for IAM resources and function configurations. The deployment process supports both staging and production environments.

## CloudFormation Stack Structure

**IAM Stack (`iam-template.yml`):**

- Creates Lambda execution roles for each function
- Defines basic role permissions and trust policies
- Exports role ARNs and names for use in function stacks

**Functions Stack (`functions-template.yml`):**

- Creates Lambda functions with proper configuration
- Defines function-specific IAM policies
- Sets up triggers, permissions, and environment variables
- Imports IAM roles from the IAM stack

## IAM Stack Pattern

- Define execution roles in the dedicated IAM CloudFormation template:

    ```yaml
    {FunctionName}LambdaRole:
      Type: AWS::IAM::Role
      Properties:
        RoleName: !Sub "${App}-${Environment}-{function-name}-lambda-role"
        AssumeRolePolicyDocument:
          Version: "2012-10-17"
          Statement:
            - Effect: Allow
            Principal:
              Service: "lambda.amazonaws.com"
            Action:
              - sts:AssumeRole
          Path: "/"
        ManagedPolicyArns:
          - "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
    ```

    **Note**: `arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole` should be included to enable deployment in an VPC.

- Export the execution role ARN and name:

    ```yaml
    Outputs:
      {FunctionName}LambdaRoleArn:
        Value: !GetAtt {FunctionName}LambdaRole.Arn
        Export:
          Name: !Sub "${AWS::StackName}-{FunctionName}LambdaRoleArn"
      {FunctionName}LambdaRoleName:
        Value: !Ref {FunctionName}LambdaRole
        Export:
          Name: !Sub "${AWS::StackName}-{FunctionName}LambdaRoleName"
    ```

## Functions Stack Pattern

- Define role policies in the functions template using the principle of least privilege. For example:

    ```yaml
    {FunctionName}SecretAccessPolicy:
      Type: AWS::IAM::RolePolicy
      Properties:
        PolicyName: "{function-name}-lambda-role-secret-access"
        PolicyDocument:
          Version: "2012-10-17"
          Statement:
            - Effect: "Allow"
              Action: "secretsmanager:GetSecretValue"
              Resource: !Sub "arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:${SecretName}*"
        RoleName:
          Fn::ImportValue: !Sub ${IAMStackName}-{FunctionName}LambdaRoleName
    ```

- Lambda function definitions generally follow this pattern:

    ```yaml
    {FunctionName}LambdaFunction:
      Type: AWS::Lambda::Function
      Properties:
        FunctionName: !Sub "${App}-{function-name}-${Environment}"
        Architectures:
          - x86_64
        Code:
          ImageUri: !Ref {FunctionName}ImageURI
        MemorySize: # Set memory size
        PackageType: Image
        Role:
          Fn::ImportValue: !Sub ${IAMStackName}-{FunctionName}LambdaRoleArn
        Timeout: # Set timeout
        VpcConfig:
          SecurityGroupIds:
            - Fn::ImportValue: !Sub ${VpcStackName}-LambdaSecurityGroupId
          SubnetIds:
            - Fn::ImportValue: !Sub ${VpcStackName}-PrivateSubnet1
            - Fn::ImportValue: !Sub ${VpcStackName}-PrivateSubnet2
        Environment:
          Variables:
            # Function-specific environment variables
        Tags:
          - Key: App
            Value: !Ref App
          - Key: Environment
            Value: !Ref Environment
    ```

- Add any required triggers, permissions, etc. For example:

    ```yaml
    # For scheduled functions
    {FunctionName}DailyTrigger:
      Type: AWS::Events::Rule
      Properties:
        Name: !Sub "${App}-{function-name}-schedule-${Environment}"
        Description: "Triggers the {function-name} function"
        ScheduleExpression: !Ref {FunctionName}TriggerSchedule
        State: ENABLED
        Targets:
          - Arn: !GetAtt {FunctionName}LambdaFunction.Arn
            Id: "{FunctionName}Target"
    
    {FunctionName}LambdaPermission:
      Type: AWS::Lambda::Permission
      Properties:
        FunctionName: !Ref {FunctionName}LambdaFunction
        Action: "lambda:InvokeFunction"
        Principal: "events.amazonaws.com"
        SourceArn: !GetAtt {FunctionName}DailyTrigger.Arn
    ```
