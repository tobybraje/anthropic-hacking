# DSM Chatbot

A simple chatbot using retrieval-augmented generation (RAG) to provide context-awareness of the Diagnostic and Statistical Manual of Mental Disorders, Fifth edition (DSM-5). AI applied in this way could provide a huge help to mental health professionals, which will become increasingly important in the current age of mental health crises. This is more of a proof of concept than anything else, but even a project this simple demonstrates the potential of LLMs applied to healthcare.

## Running the app locally

The app uses FastAPI for the backend and React for the frontend. After installing the requirements and setting the necessary environment variables, the backend can be started with the following command:

`uvicorn main.py:app --reload`

This will include hot reloading so the local server will automatically update when the code is changed.

The frontend can then be started by cd'ing into the frontend/ folder and running the following command:

`npm start`

## Next steps

Dockerize and include a docker-compose for easier local development.

Add the ability to provide one's own notes as context in addition to the DSM.

Add more productivity and quality-of-life features - saving chats, exporting in different formats, integrations with other services.
