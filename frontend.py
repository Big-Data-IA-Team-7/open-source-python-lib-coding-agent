import streamlit as st
import getpass
from backend import process_pdf, query_agent

# Sidebar for OpenAI API Key
st.sidebar.header('Configuration')
openai_api_key = st.sidebar.text_input('OpenAI API Key', type='password')

if openai_api_key:
    # Set the OpenAI API key
    st.session_state['OPENAI_API_KEY'] = openai_api_key
else:
    st.warning('Please enter your OpenAI API Key to use the application.')

# File uploader for PDF documents
st.header('PDF-based RAG Agent')
uploaded_file = st.file_uploader('Upload PDF Document', type='pdf')

if uploaded_file is not None:
    # Process the uploaded PDF
    with st.spinner('Processing PDF...'):
        pdf_text = process_pdf(uploaded_file)
        st.success('PDF processed successfully!')
        st.text_area('Extracted Text', pdf_text, height=300)

    # User query input
    user_query = st.text_input('Enter your query:')

    if st.button('Submit Query'):
        if user_query:
            # Query the agent
            with st.spinner('Querying the agent...'):
                response, citations = query_agent(user_query, pdf_text)
                st.success('Query completed!')
                st.write('Response:', response)
                st.write('Citations:', citations)
        else:
            st.warning('Please enter a query to submit.')
else:
    st.info('Please upload a PDF document to get started.')