import json
import boto3
import logging
import base64
import uuid
import PyPDF2
from bedrock_model_invoker import BedrockModelInvoker
from prompt_template_helper import get_prompt
from pdf_loader import S3PDFLoader
# Configure logging
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS clients
bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')
polly_client = boto3.client('polly')

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    try:
        # Parse the JSON body
        body = json.loads(event['body'])
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON: %s", str(e))
        return {
            'statusCode': 400,
            'body': json.dumps(f"Invalid JSON: {str(e)}")
        }

    # Extract fields from the body
    subject = body.get('subject')
    topic = body.get('topic')
    age = body.get('age')
    learner_type = body.get('learner-type')
    activity = body.get('activity')
    audio_book_required = body.get('audio-book-required')

    # Check if required fields are present
    if not subject or not activity:
        logger.error("Missing required fields: subject and activity")
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required fields: subject and activity')
        }
    
    # Initialize the helper class
    model_invoker = BedrockModelInvoker(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        max_tokens=4096,
        temperature=0.7,
        top_k=200,
        top_p=0.9
    )

    file_path = "textbook_content.txt"  # Assume this file contains the textbook content
    # # Initialize the loader
    # bucket_name = "sciencex"
    # pdf_key = "jesc101.pdf"
    # # Load the text content from the S3 PDF file
    # pdf_loader = S3PDFLoader(bucket_name, pdf_key)
    # textbook_content = pdf_loader.get_text_from_pdf()

    prompt = get_prompt(activity, file_path, age, subject, topic, learner_type)
    print(prompt)


    # Invoke the Bedrock agent based on subject and activity
    try:
        response = model_invoker.invoke(prompt)
        logger.info(f"Generated response: {response}")

        if audio_book_required:
            try:
                audio_content = generate_audio(response)
                if audio_content:
                    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                    logger.info("Generated audio content")
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'audio/mpeg',
                            'Content-Disposition': 'attachment; filename="output_audio.mp3"'
                        },
                        'body': audio_base64,
                        'isBase64Encoded': True
                    }
                else:
                    raise Exception("Audio content is empty")
            except Exception as audio_error:
                logger.error(f"Error generating audio: {audio_error}")
                return {
                    'statusCode': 500,
                    'body': json.dumps(f"Error generating audio: {str(audio_error)}")
                }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({"response": response})
            }
    except Exception as e:
        logger.error(f"Error invoking Bedrock agent: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error invoking Bedrock agent: {str(e)}")
        }

def read_prompt_file(activity):
    try:
        # Define a mapping of activity types to file names
        activity_file_mapping = {
            "summarization": "summarize_prompt.txt",
            "teaching": "teaching_prompt.txt",
            "evaluation": "evaluation_prompt.txt"
        }

        # Get the file name based on the activity type
        file_name = activity_file_mapping.get(activity)
        
        if not file_name:
            raise FileNotFoundError(f"No file mapping found for activity: {activity}")
        
        # Open the corresponding file and read the content
        with open(file_name, "r") as file:
            prompt = file.read()

        # Return the prompt content
        return prompt
    except Exception as e:
        # Handle exceptions gracefully
        return {
            "statusCode": 500,
            "body": f"Error reading file: {str(e)}"
        }

def generate_audio(text):
    try:
        # Call Amazon Polly to synthesize speech
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'  # You can change this to other voices like 'Matthew', 'Ivy', etc.
        )

        # Read the audio stream returned by Amazon Polly
        audio_stream = response['AudioStream'].read()
        if not audio_stream:
            raise Exception("Empty audio stream returned by Polly")
        return audio_stream

    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise
