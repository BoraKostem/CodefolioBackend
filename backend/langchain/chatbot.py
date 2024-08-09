import boto3
import json

# Initialize the Bedrock client
client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Function to send a message to the Bedrock model
def send_message_to_bedrock(context):
    body = json.dumps({
        'messages': context,
        'max_tokens': 1000,
        'anthropic_version': "bedrock-2023-05-31"
    }).encode('utf-8')
    
    response = client.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=body,
        contentType='application/json',
        accept='application/json',
    )
    return json.loads(response['body'].read().decode('utf-8'))['content'][0]['text']

# Main chatbot function
def chatbot():
    context = []
    print("Chatbot: Hello! How can I assist you today?\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Chatbot: Goodbye!")
            break
        # Add user input to context
        context.append({'role': 'user', 'content': user_input})
        # Generate response from Bedrock
        response = send_message_to_bedrock(context) 
        # Add chatbot response to context
        context.append({'role': 'assistant', 'content': response})
        print(f"Chatbot: {response}\n")

if __name__ == "__main__":
    chatbot()