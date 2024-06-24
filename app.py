import os
import chainlit as cl
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

# Azure AI Search configuration
search_endpoint = ""
search_key = ""
index_name = ""

# Azure OpenAI configuration
openai_endpoint = ""
openai_key = ""
deployment_name = ""

# Initialize Azure AI Search client
search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_key)
)

# Initialize Azure OpenAI client
openai_client = AzureOpenAI(
    api_key=openai_key,
    api_version="2023-05-15",
    azure_endpoint=openai_endpoint
)

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome to the Onelake - AISearch RAG chat application! How can I assist you?").send()

@cl.on_message
async def main(message: cl.Message):
    # Search for relevant documents
    search_results = search_client.search(message.content, top=3)
    
    context = ""
    for result in search_results:
        context += f"{result['chunk']}\n\n"

    # Prepare the prompt for OpenAI
    prompt = f"""
    Context information is below.
    ---------------------
    {context}
    ---------------------
    Given the context information, answer the user question: {message.content}
    """

    # Generate response using Azure OpenAI
    response = openai_client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    answer = response.choices[0].message.content

    await cl.Message(content=answer).send()

if __name__ == "__main__":
    cl.run()