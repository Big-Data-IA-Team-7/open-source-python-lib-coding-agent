from repo_clone import process_github_repo
from snowflake_data_loader import load_github_data_to_snowflake

repo_url = "https://github.com/langchain-ai/langgraph"
repo_dir = "./langgraph"

results = process_github_repo(repo_url, repo_dir)

if results is not None:
    try:
        # Load the data into Snowflake
        load_github_data_to_snowflake(results)
        print("Data successfully loaded into Snowflake")
    except Exception as e:
        print(f"Error loading data to Snowflake: {e}")