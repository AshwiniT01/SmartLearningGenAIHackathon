import json
import boto3
import logging

# Configure logging
logging.basicConfig(format='[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AWS Translate client
translate_client = boto3.client('translate')

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
    query_text = body.get('translate-query')
    target_language = body.get('target-language')

    if not query_text or not target_language:
        logger.error("Missing required fields: translate-query and target-language")
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required fields: translate-query and target-language')
        }

    # Perform the translation
    try:
        translated_text = translate_text(query_text, target_language)
        logger.info(f"Translated Text: {translated_text}")
        return {
            'statusCode': 200,
            'body': json.dumps({"translated_text": translated_text})
        }
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error translating text: {str(e)}")
        }

def translate_text(text, target_language):
    try:
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode="en",
            TargetLanguageCode=target_language
        )
        return response['TranslatedText']
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise