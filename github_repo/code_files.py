from repo_clone import process_github_repo

repo_url = "https://github.com/langchain-ai/langgraph"
repo_dir = "./langgraph"

functions_df = process_github_repo(repo_url, repo_dir)

if functions_df is not None:
    print("Results created successfully.")