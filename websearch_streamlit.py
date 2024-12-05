import streamlit as st
import os
from serpapi import GoogleSearch
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
# import openai
from dotenv import load_dotenv

load_dotenv()
api_key=os.getenv('OPENAI_API_KEY')

SERPAPI_KEY=os.getenv('SERPAPI_KEY')

SERPAPI_PARAMS = {
    "engine": "google",
    "api_key": SERPAPI_KEY,
}

def web_search(query: str):
    """Finds general knowledge information using Google search."""
    search = GoogleSearch({
        **SERPAPI_PARAMS,
        "q": query,
        "num": 5
    })
    results = search.get_dict().get("organic_results", [])  # Ensure we extract "organic_results"
    return results

def extract_domain(url: str) -> str:
    """Extracts the second-level domain name from a given URL."""
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split('.')  # Split the domain into parts
        if len(domain_parts) > 1:
            return domain_parts[-2]  # Returns 'justanswer' from 'www.justanswer.com'
        else:
            return parsed_url.netloc  # If no subdomains exist, just return the netloc
    except Exception as e:
        print(f"Error extracting domain: {e}")
        return ""
    
# Function to scrape content from URLs
def scrape_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""
        
#     return corrected_code
def code_correction_agent(current_code: str, error_message: str):
    query = f"Correct this code: {current_code}. Error: {error_message}."
    
    # Perform the search using SerpAPI
    search_results = web_search(query)
    print("Search Result URLs:")
    urls = [result['link'] for result in search_results]  # Get URLs from the results
    for url in urls:
        print(url)
    
    # Scrape content from the URLs
    scraped_contents = []
    for url in urls:
        scraped_content = scrape_url(url)
        scraped_contents.append(scraped_content)
    search_content = "\n\n".join(scraped_contents)
    
    # Initialize the LLM for code correction
    llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", openai_api_key=api_key)
    llm_input = [
        {"role": "system", "content": "You are a code correction agent. Your task is to analyze the provided code, identify the reasons for any errors, and suggest a corrected version of the code. Provide a clear explanation of why the original code failed and how the corrected code resolves the issue."},
    {
    "role": "user",
    "content": f"""
    ### Current Code (User's Code):
    {current_code}
    
    ### Error Message:
    {error_message}
    
    ### Relevant Search Result:
    {search_content}
    
    ## Analysis:
    Please provide a detailed analysis addressing the following:
    
    1. **Root Cause of the Error**:
       - Why did this error occur based on the current code?
       - What specifically in the code or environment leads to this error?
       
    2. **Explanation of the Error**:
       - What is the precise issue causing the error message (e.g., wrong import, missing module)?
       - Are there any particular details in the error message that help pinpoint the cause?
       
    3. **Suggested Fix**:
       - What changes need to be made to resolve the error?
       - Why does this change fix the error (be specific about how the modification addresses the root cause)?

    ## Additional Instructions:
    - **Include the original code** as part of the explanation and the corrected code so the user can compare.
    - Provide a clear and concise explanation of the modifications.
    - Avoid any unnecessary details. Focus only on the necessary changes and the rationale behind them.
    - Ensure that the corrected code works as expected, based on the error analysis.
    """
    }
    ]
    
    # Get the corrected code from the LLM
    corrected_code = llm.invoke(llm_input)
    
    # Extract the content from the AIMessage object directly
    corrected_code_output = corrected_code.content  # Access the content directly

    return corrected_code_output

# Function to split the full input into code and error parts
def split_input(input_text):
    # Initialize empty variables for code and error parts
    code_part = ""
    error_part = ""

    try:
        # Look for common error message keywords (e.g., "cannot import", "TypeError", etc.)
        error_keywords = ['cannot import', 'TypeError', 'ImportError', 'AttributeError', 'Exception', 'Error','ModuleNotFoundError','error']
        
        # Find the first occurrence of any error keyword
        error_index = len(input_text)  # Default to no error found
        for keyword in error_keywords:
            index = input_text.find(keyword)
            if index != -1 and index < error_index:
                error_index = index
        
        # Split the input at the found error part
        if error_index < len(input_text):
            code_part = input_text[:error_index].strip()  # Code part is everything before the error
            error_part = input_text[error_index:].strip()  # Error part is from the error keyword onward
        else:
            code_part = input_text.strip()  # If no error found, treat entire input as code
            error_part = ""  # No error found
        
        return code_part, error_part
    except Exception as e:
        return "Invalid format. Could not extract code and error properly.", str(e)

# Streamlit app
st.title("Web Search App")
st.write("Enter a query below to search the web and view the favicon of results:")

# Text input for the query
query = st.text_input("Search Query", placeholder="Type your query here")
current_code=st.text_input("Current Code", placeholder="Type your code here")
# full_text=st.text_area("Search Query", placeholder="Type your query here")
# query, current_code = split_input(full_text)

if st.button("Search"):
    if query.strip():
        try:
            # Perform web search
            with st.spinner("Searching... Please wait."):
                time.sleep(3)
                results = web_search(query)
            # Display search results
            if results:  # Checking if results is not empty
                st.write("### Sources:")
                # Create columns based on the number of results
                cols = st.columns(len(results))
                for col, result in zip(cols, results):
                    with col:
                        title = result.get("title", "No Title")
                        link = result.get("link", "#")
                        favicon = result.get("favicon", None)  # Extract the favicon URL
                        domain = extract_domain(link)
                        
                        # Display the title and link
                        st.markdown(f"**[{title}]({link})**")
                        
                        # Ensure the image and text are aligned within one consistent column
                        if favicon:
                            st.image(favicon, use_container_width=True)  # Updated to use_container_width
                            st.write(f"**{domain}**")
                        else:
                            st.write("No favicon available.")
            else:
                st.write("No results found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a query to search.")
    with st.spinner("Query Response..."):
        corrected_code = code_correction_agent(current_code, query)
        print(corrected_code)
        st.write("### Corrected Code:")
        st.write(corrected_code)