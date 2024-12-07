from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from data_load.process_github_repo.repo_clone import clone_repo
from data_load.process_github_repo.extract_code import extract_structures_from_repo
from data_load.process_github_repo.process_py_file import process_python_files
from data_load.process_github_repo.load_py_details_to_snowflake import load_python_data_to_snowflake
from data_load.process_github_repo.process_ipynb_file import process_ipynb_files
from data_load.process_github_repo.load_ipynb_details_to_snowflake import load_ipynnb_data_to_snowflake
from data_load.process_github_repo.process_md_file import process_md_files
from data_load.process_github_repo.load_md_details_to_snowflake import load_markdown_data_to_snowflake

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'start_date': datetime(2023, 11, 27),
}

# Define the DAG
with DAG(
    'github_repo_processing_dag',
    default_args=default_args,
    description='Clone a GitHub repo, process files by type, and load into Snowflake',
    schedule_interval=None,
    catchup=False
) as dag:

    # Task 1: Clone GitHub repository

    clone_task = PythonOperator(
    task_id='clone_repo',
    python_callable=clone_repo,
    op_kwargs={
        'repo_url': "https://github.com/langchain-ai/langgraph",
        'repo_dir': "/tmp/langgraph_repo",
    },
    )



    # Task 2 : List files from the repo
   
    list_files = PythonOperator(
        task_id='list_files',
        python_callable=extract_structures_from_repo,
        op_kwargs={'code_root': "/tmp/langgraph_repo"},
         provide_context=True,
    )


    


    # Task 3: Process Python files
    process_py_task = PythonOperator(
        task_id='process_py_files',
        python_callable=process_python_files,
        provide_context=True,
    )




    # Task 4 : Load Python Files into Snowflake
    load_py_task = PythonOperator(
        task_id='load_py_to_snowflake',
        python_callable=load_python_data_to_snowflake,
        provide_context=True,
    )


    # Task 5: Process IPYNB files
    process_ipynb_task = PythonOperator(
        task_id='process_ipynb_files',
        python_callable=process_ipynb_files,
        provide_context=True,
    )




    # Task 6: Load Ipynb Files into Snowflake
    load_ipynb_task = PythonOperator(
        task_id='load_ipynb_to_snowflake',
        python_callable=load_ipynnb_data_to_snowflake,
        provide_context=True,
    )

    # Task 7: Process MD files
    process_md_task = PythonOperator(
        task_id='process_md_files',
        python_callable=process_md_files,
        provide_context=True,
    )




    # Task 4 : Load MD Files into Snowflake
    load_md_task = PythonOperator(
        task_id='load_md_to_snowflake',
        python_callable=load_markdown_data_to_snowflake,
        provide_context=True,
    )

    clone_task >> list_files >> [ process_py_task, process_ipynb_task , process_md_task]
    process_py_task >> load_py_task
    process_ipynb_task >> load_ipynb_task
    process_md_task >> load_md_task