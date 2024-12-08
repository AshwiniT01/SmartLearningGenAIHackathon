import os

def get_prompt_template(activity, file_path=None, **parameters):
    """
    Generates a prompt based on the activity type and parameters.
    Optionally reads textbook content from a file.

    Args:
        activity (str): The activity type (e.g., "summarization", "teaching_instructions", "evaluation").
        file_path (str): Path to the file containing the textbook content (optional).
        **parameters: Other dynamic parameters like age, subject, topic, and learning_type.

    Returns:
        str: The generated prompt.
    """
    if activity not in PROMPT_TEMPLATES:
        raise ValueError(f"Invalid activity type: {activity}. Choose from {list(PROMPT_TEMPLATES.keys())}")

    # Read textbook content from the file if provided
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at path '{file_path}' does not exist.")
        try:
            with open(file_path, 'r') as file:
                parameters['textbook_content'] = file.read()
        except Exception as e:
            raise RuntimeError(f"Error reading the file: {e}")

    # Ensure textbook_content is present
    if 'textbook_content' not in parameters or not parameters['textbook_content']:
        raise ValueError("Textbook content is missing. Provide it directly or via a valid file path.")

    # Create a prompt template instance
    prompt_template = PromptTemplate(
        template=PROMPT_TEMPLATES[activity], 
        input_variables=parameters.keys()
    )

    # Generate the prompt
    return prompt_template.format(**parameters)

def get_prompt(activity, file_path, age, subject, topic, learning_type):
    # Read textbook content from the file if provided
    if file_path:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file at path '{file_path}' does not exist.")
        try:
            with open(file_path, 'r') as file:
                textbook_content = file.read()
        except Exception as e:
            raise RuntimeError(f"Error reading the file: {e}")
    
    if activity == "Summarization":
        return f"""
            Summarize the following textbook content for students of grade {age}.
            Focus on making it concise and easy to understand. Include key points related to the subject "{subject}" and topic "{topic}".
            
            Textbook Content:
            {textbook_content}
            
            Provide the summarized text:
        """
    elif activity == "Teaching":
        return f"""
            Generate teaching instructions tailored for a "{learning_type}" learner.
            The student is of grade {age}. The instructions should be relevant to the subject "{subject}" and topic "{topic}".
            
            Textbook Content:
            {textbook_content}
            
            Provide detailed teaching instructions:
        """
    elif activity == "Evaluation":
        return f"""
            Create an evaluation plan for a student of grade {age}, covering the subject "{subject}" and topic "{topic}".
            Provide:
            1. Three key questions to test understanding.
            2. Suggested evaluation criteria.
            3. Feedback strategies for a "{learning_type}" learner.
            
            Textbook Content:
            {textbook_content}
            
            Provide the evaluation plan:
        """
    else:
        raise ValueError(f"Unsupported activity type: {activity}")

