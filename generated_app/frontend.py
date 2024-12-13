import streamlit as st
from backend import CodeGenerationGraph

def main():
    st.set_page_config(page_title="LangGraph Code Generation Assistant", layout="wide")
    
    # Sidebar for API key
    with st.sidebar:
        st.title("Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if not openai_api_key:
            st.warning("Please enter your OpenAI API key to continue.")
            return

    st.title("LangGraph Code Generation Assistant")
    st.write("Get help with code generation, documentation, and implementation explanations.")

    # User input section
    user_requirement = st.text_area(
        "Enter your programming requirements:",
        height=150,
        placeholder="Describe the functionality you need..."
    )

    if st.button("Generate Code") and user_requirement:
        try:
            with st.spinner("Generating code and documentation..."):
                # Initialize the graph with the API key
                code_graph = CodeGenerationGraph(openai_api_key)
                
                # Process the requirement through the graph
                result = code_graph.process_requirement(user_requirement)
                
                # Display results in tabs
                tab1, tab2, tab3 = st.tabs(["Generated Code", "Documentation", "Implementation Details"])
                
                with tab1:
                    st.code(result["code"], language="python")
                
                with tab2:
                    st.markdown(result["documentation"])
                
                with tab3:
                    st.markdown(result["implementation_details"])
                    
                # Display edge cases
                st.subheader("Edge Cases to Consider")
                for idx, edge_case in enumerate(result["edge_cases"], 1):
                    st.write(f"{idx}. {edge_case}")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Add usage instructions
    with st.expander("How to use"):
        st.markdown("""
        1. Enter your OpenAI API key in the sidebar
        2. Describe your programming requirements in detail
        3. Click 'Generate Code' to receive:
           - Fully documented code
           - Implementation explanation
           - Edge case considerations
        """)

if __name__ == "__main__":
    main()