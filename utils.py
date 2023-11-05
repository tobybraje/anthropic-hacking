from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from settings import settings
from pdf_to_html import EMBEDDINGS
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatAnthropic
from langchain.vectorstores import Chroma
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.globals import set_debug


def generate_response(messages):
    set_debug(True)
    user_prompt = ""
    for message in messages:
        if message["role"] == "assistant":
            user_prompt += f"{AI_PROMPT}{message['content']}"
        else:
            user_prompt += f"{HUMAN_PROMPT}{message['content']}"

    vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=EMBEDDINGS)
    retriever = vectorstore.as_retriever()
    template = """
    <instructions>
    You are a mental health diagnostics assistant. Mental health
    professionals will use you to help talk through their patients and evaluate
    potential diagnoses. Answer the question based only on the DSM-5 excerpt
    which has been provided to you as context. Bear in mind, this has been extracted
    from an unstructured PDF. Therefore, if you see anything that does not look like
    correct English, ignore it (it was probably a table). If an answer to the question is provided, it must be annotated with a citation from the context.
    Use the following format to cite relevant passages: 'quote' - source. Answer only if you know the answer, otherwise feel free to say that you don't know.
    Think step by step.
    </instructions>
    <context>
    {context}
    </context>
    <question
    {question}
    </question>
    """
    model = ChatAnthropic()
    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )

    return chain.invoke(user_prompt)
