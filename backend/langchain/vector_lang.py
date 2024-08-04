from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.embeddings import BedrockEmbeddings
import os
import json
# Environment setup
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"

# Database connection setup
connection = "postgresql+psycopg://langchain:12345678@codefolio-1.c5uiksm6gkn7.eu-central-1.rds.amazonaws.com:5432/vector_test"
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

def add_documents(content):
    try:
        for item in content:
            languages = ', '.join([lang['language'] for lang in item['github_project_languages']])
            page_content = f"{item['project_name']} {item['description']} {languages}"
            metadata = {
                "user_id": item['user'],
                "languages": [
                    {"language": lang['language'], "percentage": lang['percentage']}
                    for lang in item['github_project_languages']
                ],
                "project_name": item['project_name'],
                "description": item['description']
            }
            doc = Document(page_content=page_content, metadata=metadata)
            vectorstore.add_documents(doc)

        return f"{len(content)} documents added successfully"
    except Exception as e:
        return str(e)


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
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(language_data),metadata={"user_id":user_id, "type":"cv_languages","language":language_data})
    vectorstore.add_documents([doc])
    
#experience_id ekle metadataya
def create_cv_experience(experience_data, user_id):
    print(json.dumps(experience_data))
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(experience_data),metadata={"user_id":user_id, "type":"cv_experiences","experience_id":experience_data['id']})
    vectorstore.add_documents([doc])

#education_id ekle
def create_cv_education(education_data, user_id):
    # Implement logic to create or store CV language data
    doc = Document(page_content=json.dumps(education_data),metadata={"user_id":user_id, "type":"cv_educations","education_id":education_data['id']})
    vectorstore.add_documents([doc])

#user_id + cv_skill unique
def create_cv_skill(skill_data, user_id):
    # Implement logic to create or store CV skill data
    doc = Document(page_content=json.dumps(skill_data),metadata={"user_id":user_id, "type":"cv_skills","skill":skill_data["skill"]})
    vectorstore.add_documents([doc])

#certification_id ekle 
def create_cv_certification(certification_data, user_id):
    # Implement logic to create or store CV certification data
    doc = Document(page_content=json.dumps(certification_data),metadata={"user_id":user_id, "type":"cv_certifications","certification_id":certification_data['id']})
    vectorstore.add_documents([doc])

#project_id ekle
def create_cv_project(project_data, user_id):
    # Implement logic to create or store CV project data
    doc = Document(page_content=json.dumps(project_data),metadata={"user_id":user_id, "type":"cv_projects","project_id":project_data['id']})
    vectorstore.add_documents([doc])

# spesifik vektörü silme
def delete_vector(user_id):
    try:
        # Fetch the document IDs to delete
        documents_to_delete = vectorstore.get_by_ids({"user_id": user_id})
        if not documents_to_delete:
            return f"No documents found for user_id: {user_id}"

        # Extract the IDs
        ids_to_delete = [doc.metadata['id'] for doc in documents_to_delete]

        # Delete the documents from the vector store
        vectorstore.delete_documents(ids_to_delete)
        return f"Deleted {len(ids_to_delete)} documents for user_id: {user_id}"
    except Exception as e:
        return str(e)

# CV language ekleme-çıkarma
def add_cv_language(user_id, cv_language):
    try:
        # Create a new document for the cv_language
        metadata = {
            "user_id": user_id,
            "type": "cv_languages",
            "language": cv_language["language"],
            "id": cv_language["id"]
        }
        doc = Document(page_content=cv_language["language"], metadata=metadata)

        # Add the new document to the vector store
        vectorstore.add_documents([doc])
        return f"Language '{cv_language['language']}' added successfully for user_id: {user_id}"
    except Exception as e:
        return str(e)

def delete_cv_language(user_id, language_id):
    try:
        # Fetch the documents to delete
        documents_to_delete = vectorstore.get_documents_by_metadata({
            "user_id": user_id,
            "type": "cv_languages",
            "id": language_id
        })
        if not documents_to_delete:
            return f"No CV language found for user_id: {user_id} with language_id: {language_id}"

        # Delete the documents
        document_ids = [doc.metadata['id'] for doc in documents_to_delete]
        vectorstore.delete(document_ids)
        return f"Language with id: {language_id} deleted successfully for user_id: {user_id}"
    except Exception as e:
        return str(e)
 

# about editleme
def edit_about(user_id, new_about):
    try:
        # Fetch the document to update
        documents_to_update = vectorstore.get_documents_by_metadata({
            "user_id": user_id,
            "type": "about"
        })
        if not documents_to_update:
            return f"No document found for user_id: {user_id} with type 'about'"

        # Delete the old document
        old_document_id = documents_to_update[0].metadata['id']
        vectorstore._delete_collection([old_document_id])

        # Create the new document
        metadata = {
            "user_id": user_id,
            "type": "about"
        }
        doc = Document(page_content=new_about, metadata=metadata)

        # Add the new document to the vector store
        vectorstore.add_documents(doc)
        return f"Document for user_id: {user_id} with type 'about' updated successfully"
    except Exception as e:
        return str(e)

# Deleting the user cv project's by receiving the user id and the project id  
def user_cv_project_delete(user_id: int, project_id: str) -> None:
    try:
        # Fetch all documents associated with the user_id
        user_documents = vectorstore.get_by_ids([user_id])  # Adjust method if needed
        
        # Find the document with the matching project_id
        document_to_delete = None
        for doc in user_documents:
            # Load the page_content to access metadata
            metadata = json.loads(doc.page_content)
            if metadata.get('project_id') == project_id:
                document_to_delete = doc.metadata.get('id')  # Adjust if your document ID is stored differently
                break
        
        if document_to_delete:
            # Using the 'delete' method to delete the document based on its ID
            vectorstore.delete(ids=[document_to_delete])
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
    try:
        # Fetch documents with the specific user_id and experience_id from vectorstore
        documents = vectorstore.get_by_ids([experience_id])
        
        # Filter documents to match both user_id and experience_id
        ids_to_delete = [doc.id for doc in documents if doc.metadata.get("user_id") == user_id and doc.metadata.get("experience_id") == experience_id]
        
        if ids_to_delete:
            # Use the built-in delete function to remove the documents
            vectorstore.delete(ids=ids_to_delete)
            print(f"Deleted vectors with experience_id {experience_id} for user {user_id}.")
        else:
            print(f"No vectors found for experience_id {experience_id} for user {user_id}.")
            
    except Exception as e:
        print(f"An error occurred while deleting vectors for experience_id {experience_id} for user {user_id}: {e}")


def delete_cv_skill(user_id, skill):
    # Fetch all documents for the user
    documents = vectorstore.get_by_ids([user_id])

    # Filter documents to find those matching the skill
    ids_to_delete = [doc.id for doc in documents if doc.metadata.get("user_id") == user_id and doc.metadata.get("skill") == skill]

    # Delete the documents
    vectorstore.delete(ids=ids_to_delete)


def delete_cv_certification(user_id: int, certification_id: int) -> None:
    # Step 1: Fetch documents by user_id and certification_id
    # You need to know the IDs of the documents you want to delete.
    # Assuming `get_by_ids` method can be used to get documents.
    
    # Example method to fetch document IDs based on metadata
    all_docs = vectorstore.get_by_ids([str(user_id)])  # Fetch all docs for a specific user_id
    ids_to_delete = []
    
    for doc in all_docs:
        # Check if this document matches the certification_id
        if doc.metadata.get('type') == 'cv_certifications' and doc.metadata.get('certification_id') == certification_id:
            ids_to_delete.append(doc.id)  # Collect IDs of documents to be deleted

    # Step 2: Delete documents by their IDs
    if ids_to_delete:
        vectorstore.delete(ids=ids_to_delete)







    






'''
Document(
        page_content=cv_data,
        metadata={"user_id": 2, "type": , "topic": "animals"},
    ),
'''