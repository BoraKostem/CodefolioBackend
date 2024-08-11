from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_community.embeddings import BedrockEmbeddings
import os
import environ
import langchain
import pickle
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# Environment setup
env = environ.Env()
langchain.verbose = False
langchain.debug = False
langchain.llm_cache = False
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = env('LANGCHAIN_API_KEY')
os.environ["LANGCHAIN_PROJECT"] = "chatbot"

# Reading .env file
environ.Env.read_env()
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
    model_id="cohere.embed-multilingual-v3",
    region_name="eu-central-1"
)
llm = ChatBedrockConverse(
    model="meta.llama3-1-405b-instruct-v1:0",
    temperature=0,
    max_tokens=None,
    region_name="us-west-2"
)

vectorstore = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)

prompt = '''
You are a chatbot designed to role-play as a person with the given name and context. 
Respond to prompts professionally, keeping in mind that the person you're chatting with could be a recruiter.
Your responses should be relevant, coherent, and fluent. If unsure, state that you dont know.
Keep answers concise, using no more than five sentences. Avoid unrelated information, do not ask questions.

Name: {person_name}

Context: {context}
'''

# Functions to handle chat history with pickle
def get_chat(chat_uuid):
    try:
        with open(f"{chat_uuid}.pkl", 'rb') as chatfile:
            return pickle.load(chatfile)
    except IOError:
        return []

def store_chat(chat_uuid, chat_data):
    with open(f"{chat_uuid}.pkl", 'wb') as chatfile:
        pickle.dump(chat_data, chatfile)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

def chat(chat_uuid=None, person_name=None, user_id =None, input_message=None):
    history = get_chat(chat_uuid)
    context = vectorstore.similarity_search(query=input_message, k=4, filter={"user_id":{"$eq" : [int(user_id)]}})
    formatted_prompt = qa_prompt.invoke({
        "person_name": person_name,
        "context": context,
        "chat_history": history,
        "input": input_message
    })
    response = llm.invoke(formatted_prompt)
    history.append(HumanMessage(input_message))
    history.append(AIMessage(response.content))
    store_chat(chat_uuid, history) 
    return response.content