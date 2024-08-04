from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.embeddings import BedrockEmbeddings
import os
import environ
import uuid
import json
# Environment setup
env = environ.Env()
# Reading .env file
environ.Env.read_env()
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"
POSTGRE_USER = env("POSTGRE_USER")
POSTGRE_PASSWORD = env("POSTGRE_PASSWORD")
POSTGRE_HOST = env("POSTGRE_HOST")
POSTGRE_PORT = env("POSTGRE_PORT")
DATABASE_NAME = "codefolio"
# Database connection setup
connection = f"postgresql+psycopg://{POSTGRE_USER}:{POSTGRE_PASSWORD}@{POSTGRE_HOST}:{POSTGRE_PORT}/{DATABASE_NAME}"
collection_name = "aws_bedrock"

# Initialize embeddings and vector store
embeddings = BedrockEmbeddings(
    model_id="cohere.embed-multilingual-v3"
)

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

documents = []

def create_uuid_from_string(string):
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    return uuid.uuid5(namespace, string).hex

def add_documents(item):
    try:
        languages = ', '.join([lang['language'] for lang in item['github_project_languages']])
        page_content = f"{item['project_name']} {item['description']} {languages}"
        name = f"{item['user']}_{item['project_name']}"  # Unique name for the document
        id = create_uuid_from_string(name)
        metadata = {
            "id": id,
            "user_id": item['user'],
            "type": "github_projects",
            "languages": [
                {"language": lang['language'], "percentage": lang['percentage']}
                for lang in item['github_project_languages']
            ],
            "project_name": item['project_name'],
            "description": item['description']
        }
        doc = Document(page_content=page_content, metadata=metadata)
        vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

        return f"Github documents added successfully"
    except Exception as e:
        return str(e)

def delete_github_project(user_id):
    document_to_delete = []
    try:
        user_documents = vectorstore.similarity_search(query="", k=1000, filter={"user_id":{"$eq" : [int(user_id)]}, "type": {"$eq" : ["github_projects"]}})
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            vectorstore.delete(document_to_delete)
            print(f"Deleted Github projects for user {user_id}.")
        else:
            print(f"No Github projects found for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting Github projects for user {user_id}: {e}")

def create_cv_data(cv_json, user_id):
    cv_languages = cv_json.get('cv_language', [])
    cv_experiences = cv_json.get('cv_experience', [])
    cv_educations = cv_json.get('cv_education', [])
    cv_skills = cv_json.get('cv_skills', [])
    cv_certifications = cv_json.get('cv_certifications', [])
    cv_projects = cv_json.get('cv_projects', [])

    # Process cv_languages
    for language_data in cv_languages:
        create_cv_language(language_data, user_id)

    # Process cv_experiences
    for experience_data in cv_experiences:
        create_cv_experience(experience_data, user_id)

    # Process cv_educations
    for education_data in cv_educations:
        create_cv_education(education_data, user_id)

    # Process cv_skills
    for skill_data in cv_skills:
        create_cv_skill(skill_data, user_id)

    # Process cv_certifications
    for certification_data in cv_certifications:
        create_cv_certification(certification_data, user_id)

    # Process cv_projects
    for project_data in cv_projects:
        create_cv_project(project_data, user_id)

#delete için user_id ve language unique
# Sample functions (placeholders for actual implementation)
def create_cv_language(language_data, user_id):
    name = f"{user_id}_{language_data['language']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(language_data),metadata={"id": id, "user_id":user_id, "type":"cv_languages","language":language_data})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])
    
#experience_id ekle metadataya
def create_cv_experience(experience_data, user_id):
    name = f"{user_id}_{experience_data['id']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(experience_data),metadata={"id": id, "user_id":user_id, "type":"cv_experiences","experience_id":experience_data['id']})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

#education_id ekle
def create_cv_education(education_data, user_id):
    name = f"{user_id}_{education_data['id']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(education_data),metadata={"id":id, "user_id":user_id, "type":"cv_educations","education_id":education_data['id']})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

#user_id + cv_skill unique
def create_cv_skill(skill_data, user_id):
    name = f"{user_id}_{skill_data['skill']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV skill data
    doc = Document(page_content=json.dumps(skill_data),metadata={"id":id, "user_id":user_id, "type":"cv_skills","skill":skill_data["skill"]})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

#certification_id ekle 
def create_cv_certification(certification_data, user_id):
    name = f"{user_id}_{certification_data['id']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV certification data
    doc = Document(page_content=json.dumps(certification_data),metadata={"id":id, "user_id":user_id, "type":"cv_certifications","certification_id":certification_data['id']})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

#project_id ekle
def create_cv_project(project_data, user_id):
    name = f"{user_id}_{project_data['id']}"  # Unique name for the document
    id = create_uuid_from_string(name)
    # Implement logic to create or store CV project data
    doc = Document(page_content=json.dumps(project_data),metadata={"id":id, "user_id":user_id, "type":"cv_projects","project_id":project_data['id']})
    vectorstore.add_documents([doc], ids=[doc.metadata["id"]])

# CV language ekleme-çıkarma
def add_cv_language(user_id, cv_language):
    try:
        name = f"{user_id}_{cv_language['language']}"  # Unique name for the document
        id = create_uuid_from_string(name)
        # Create a new document for the cv_language
        metadata = {
            "user_id": user_id,
            "type": "cv_languages",
            "language": cv_language["language"],
            "id": id
        }
        doc = Document(page_content=cv_language["language"], metadata=metadata)

        # Add the new document to the vector store
        vectorstore.add_documents([doc], ids=[doc.metadata["id"]])
        return f"Language '{cv_language['language']}' added successfully for user_id: {user_id}"
    except Exception as e:
        return str(e)

# Deleting the user cv project's by receiving the user id and the project id  
def user_cv_project_delete(user_id: int, project_id: int):
    document_to_delete = []
    try:
        # Fetch all documents associated with the user_id
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "project_id":{"$eq" : [int(project_id)]}})
        # Find the document with the matching project_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Using the 'delete' method to delete the document based on its ID
            vectorstore.delete(document_to_delete)
            print(f"Project with ID {project_id} for user {user_id} deleted successfully.")
        else:
            print(f"No project found with ID {project_id} for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting the project {project_id} for user {user_id}: {e}")

def user_cv_project_update(user_id: int, project_id: str, project_data: dict) -> None:
    try:
        # Create a new document with the updated project data
        doc = Document(page_content=json.dumps(project_data), metadata={"user_id": user_id, "type": "cv_projects", "project_id": project_id})
        
        # Using the 'add_documents' method to update the vector store with the new document
        vectorstore.add_documents([doc])
        print(f"Project with ID {project_id} for user {user_id} updated successfully in vector store.")
    except Exception as e:
        print(f"An error occurred while updating the project {project_id} for user {user_id} in vector store: {e}")


def delete_pgvector_experience(experience_id: str, user_id: int) -> None:
    document_to_delete = []
    try:
        # Fetch documents with the specific user_id and experience_id from vectorstore
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "experience_id":{"$eq" : [int(experience_id)]}})
        # Filter documents to match both user_id and experience_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(document_to_delete)
            print(f"Deleted vectors with experience_id {experience_id} for user {user_id}.")
        else:
            print(f"No vectors found for experience_id {experience_id} for user {user_id}.")
            
    except Exception as e:
        print(f"An error occurred while deleting vectors for experience_id {experience_id} for user {user_id}: {e}")


def delete_cv_skill(user_id, skill):
    document_to_delete = []
    try:
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "skill":{"$eq" : [skill]}})
        # Filter documents to match both user_id and experience_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(document_to_delete)
            print(f"Deleted vectors with skill {skill} for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting the skill '{skill}' for user {user_id}: {e}")


def delete_cv_certification(user_id: int, certification_id: int) -> None:
    document_to_delete = []
    try:
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "certification_id":{"$eq" : [int(certification_id)]}})
        # Filter documents to match both user_id and experience_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(document_to_delete)
            print(f"Deleted vectors with certification_id {certification_id} for user {user_id}.")
        else:
            print(f"No vectors found for certification_id {certification_id} for user {user_id}.")
    except Exception as e:
        print(f"An error occurred while deleting the certification {certification_id} for user {user_id}: {e}")

def delete_cv_education(education_id: str, user_id: int) -> None:
    document_to_delete = []
    try:
        # Fetch documents with the specific user_id and education_id from vectorstore
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "education_id":{"$eq" : [int(education_id)]}})
        # Filter documents to match both user_id and education_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(document_to_delete)
            print(f"Deleted vectors with education_id {education_id} for user {user_id}.")
        else:
            print(f"No vectors found for education_id {education_id} for user {user_id}.")
            
    except Exception as e:
        print(f"An error occurred while deleting vectors for education_id {education_id} for user {user_id}: {e}")

def delete_cv_language(user_id, language):
    document_to_delete = []
    try:
        user_documents = vectorstore.similarity_search(query="", k=1, filter={"user_id":{"$eq" : [int(user_id)]}, "language":{"$eq" : [language]}})
        # Filter documents to match both user_id and experience_id
        for doc in user_documents:
            id = doc.metadata['id']
            document_to_delete.append(str(id))
        if document_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(document_to_delete)
            print(f"Deleted vectors with language {language} for user {user_id}.")
        else:
            print(f"No vectors found for language {language} for user {user_id}.")
    except:
        print(f"An error occurred while deleting the language '{language}' for user {user_id}.")

def search_ml(search, page=1, offset=10):
    # Perform the search
    all_results = vectorstore.similarity_search(search, k=1000)  # Fetch more results than needed

    # Filter for unique metadata.user_id
    seen_user_ids = set()
    unique_results = []
    for result in all_results:
        user_id = result.metadata['user_id']
        if user_id not in seen_user_ids:
            seen_user_ids.add(user_id)
            unique_results.append(result)

    # Calculate start and end indices for pagination on the filtered results
    start_index = (page - 1) * offset
    end_index = start_index + offset

    # Apply pagination to the unique results
    paginated_unique_results = unique_results[start_index:end_index]

    return paginated_unique_results
