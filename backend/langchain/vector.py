from flask import Flask, request, jsonify
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.embeddings import OllamaEmbeddings
import os

app = Flask(__name__)

# Environment setup
os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["AWS_DEFAULT_REGION"] = "eu-central-1"

# Database connection setup
connection = "postgresql+psycopg://langchain:12345678@codefolio-1.c5uiksm6gkn7.eu-central-1.rds.amazonaws.com:5432/vector_test"
collection_name = "ollama_embeddings"

# Initialize embeddings and vector store
embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

def add_documents(projects):
    try:
        documents = []
        for project in projects:
            languages = ', '.join([lang['language'] for lang in project['github_project_languages']])
            page_content = f"{project['project_name']} {project['description']} {languages}"
            metadata = {
                "id": project['id'],
                "languages": [
                    {"language": lang['language'], "percentage": lang['percentage']}
                    for lang in project['github_project_languages']
                ],
                "project_name": project['project_name'],
                "description": project['description']
            }
            doc = Document(page_content=page_content, metadata=metadata)
            documents.append(doc)

        vectorstore.add_documents(documents)
        return {"message": "Documents added successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def add_cv_documents(cv_data):
    try:
        page_content = cv_data['about']
        for project in cv_data['cv_projects']:
            languages = ', '.join([lang['language'] for lang in project['cv_project_languages']])
            project_content = f"{project['project_name']} {project['description']} {languages}"
            page_content += f" {project_content}"

        metadata = {
            "about": cv_data['about'],
            "cv_languages": cv_data['cv_languages'],
            "cv_experiences": cv_data['cv_experiences'],
            "cv_educations": cv_data['cv_educations'],
            "cv_skills": cv_data['cv_skills'],
            "cv_certifications": cv_data['cv_certifications'],
            "cv_projects": cv_data['cv_projects']
        }
        doc = Document(page_content=page_content, metadata=metadata)
        vectorstore.add_documents([doc])

        return {"message": "CV documents added successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def update_cv_about_and_projects(cv_id, new_about=None, new_projects=None):
    try:
        document = vectorstore.get_document_by_id(cv_id)
        if not document:
            return {"error": "Document not found"}, 404

        if new_about:
            document.metadata['about'] = new_about
            parts = document.page_content.split(' ', 1)
            if len(parts) > 1:
                document.page_content = f"{new_about} {parts[1]}"
            else:
                document.page_content = new_about

        if new_projects:
            document.metadata['cv_projects'] = new_projects
            project_descriptions = []
            for project in new_projects:
                project_name = project.get('project_name', '')
                description = project.get('description', '')
                languages = ', '.join([lang['language'] for lang in project.get('cv_project_languages', [])])
                project_descriptions.append(f"{project_name} {description} {languages}")

            updated_page_content = ' '.join(project_descriptions)

            if new_about:
                parts = document.page_content.split(' ', 1)
                if len(parts) > 1:
                    document.page_content = f"{new_about} {updated_page_content}"
                else:
                    document.page_content = f"{new_about} {updated_page_content}"
            else:
                document.page_content = updated_page_content

        vectorstore.update_document(document)
        return {"message": "About and projects updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def update_github_project_description(project_id, new_description):
    try:
        document = vectorstore.get_document_by_id(project_id)
        if not document:
            return {"error": "Document not found"}, 404

        document.metadata['description'] = new_description

        parts = document.page_content.split(' ', 1)
        if len(parts) > 1:
            project_name_and_languages = parts[0]
            document.page_content = f"{project_name_and_languages} {new_description}"
        else:
            document.page_content = f"{parts[0]} {new_description}"

        vectorstore.update_document(document)
        return {"message": "Project description updated successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

def delete_document(document_id):
    try:
        vectorstore.delete_document(document_id)
        return {"message": "Document deleted successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('/add_documents', methods=['POST'])
def add_documents_route():
    data = request.get_json()
    projects = data['content']
    return add_documents(projects)

@app.route('/add_cv_documents', methods=['POST'])
def add_cv_documents_route():
    data = request.get_json()
    cv_data = data['content']
    return add_cv_documents(cv_data)

@app.route('/update_cv', methods=['POST'])
def update_cv_route():
    data = request.get_json()
    cv_id = data['cv_id']
    new_about = data.get('new_about')
    new_projects = data.get('new_projects')
    return update_cv_about_and_projects(cv_id, new_about, new_projects)

@app.route('/update_github_project_description', methods=['POST'])
def update_github_project_description_route():
    data = request.get_json()
    project_id = data['project_id']
    new_description = data['new_description']
    return update_github_project_description(project_id, new_description)

@app.route('/delete_document', methods=['DELETE'])
def delete_document_route():
    data = request.get_json()
    document_id = data['document_id']
    return delete_document(document_id)

if __name__ == '__main__':
    app.run(debug=True)
