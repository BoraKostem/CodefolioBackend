from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrock
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from pdfminer.high_level import extract_text
import tempfile
import json
import os
from pathlib import Path
import environ
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialize environment variables
env = environ.Env()
# Assuming your .env file is in the same directory as settings.py
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

token = env('LANGSMITH_TOKEN')

os.environ["LANGSMITH_API_KEY"] = token
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"

llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs=dict(temperature=0,max_tokens=8192),
    # other params...
)

system_prompt = '''
Parse the following CV and extract the following information in json format:
- Name
- Email
- Phone
- About
- Address
- Education
- Experience
- Skills (Programming languages, Frameworks, Libraries, etc.)
- Certifications
- Languages (English, Turkish, etc.)
- Projects

the output should be like this: (do not change the layout of the output, just fill the fields with the extracted information (also do not shorten the descriptions))
(In the skills section if a skill is added as a language and framework/library side by side add them as separate skill fields.)
(Do not write anything that is not in the provided CV!, If there is no information about a field, just leave it empty.)
    "name": "String",
    "location": "String",
    "email": "String",
    "phone": "String",
    "about": "String",
    "cv_language": [
        
          "language": "String",
        
      ],
    "cv_experience": [
        
          "company_name": "String",
          "description": "String", (job title, responsibilities, etc.)
          "position": "String",
          "location": "String",
          "start_date": "String",
          "end_date": "String",
        
      ],
    "cv_education": [
        
          "degree": "String",
          "school": "String",
          "location": "String",
          "start_date": "String",
          "end_date": "String",
        
      ],
    "cv_skills": [
        
          "skill": "String",
        
      ],
    "cv_certifications": [
        
          "certification": "String",
          "date": "String",
          "certification_url": "String"
        
      ],
    "cv_projects": [
        
          "project_name": "String",
          "description": "String",
          "cv_projects_language": [

              "language": "String" (java, python, etc),
            
          ]
        
      ],

'''

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt,
        ),
        ("human", "{input}"),
    ]
)
chain = prompt | llm

def cv_parser(cv):
    try:
        # Attempt to extract text directly using the file-like object.
        cv_text = extract_text(cv)
    except TypeError:
        # If the direct approach fails, use a temporary file.
        with tempfile.NamedTemporaryFile(delete=True) as temp_cv:
            for chunk in cv.chunks():
                temp_cv.write(chunk)
            temp_cv.seek(0)
            cv_text = extract_text(temp_cv.name) 
    out = chain.invoke({"input":cv_text})
    json_data = json.loads(out.content)
    return json_data