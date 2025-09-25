import boto3

bedrock = boto3.client('bedrock', region_name='us-east-1')
models = bedrock.list_foundation_models()

claude_models = [m for m in models['modelSummaries'] if 'claude' in m['modelId'].lower()]
for model in claude_models:
    print(f"Model: {model['modelId']}")
    print(f"Supports streaming: {model.get('responseStreamingSupported', False)}")
    print("---")