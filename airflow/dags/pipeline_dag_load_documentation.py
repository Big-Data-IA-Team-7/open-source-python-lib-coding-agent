from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from data_load.process_documentation_pages.scrape_url import load_recursive_url
from data_load.process_documentation_pages.process_docs import process_content
from data_load.process_documentation_pages.load_into_pinecone import store_to_pinecone

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),  # Delay between retries
    'start_date': datetime(2023, 11, 27),
}

# Define the DAG
with DAG(
    'langgraph_extraction_dag',
    default_args=default_args,
    description='A DAG for extracting documentation pages, parsing files, storing them in AWS, and loading vector embeddings into Pinecone',
    schedule_interval=None,  # Trigger manually
    catchup=False
) as dag:
    # Task 1: Load Recursive URL
    load_task = PythonOperator(
        task_id='load_recursive_url_task',
        python_callable=load_recursive_url,
        op_kwargs={
            'start_url': 'https://docs.llamaindex.ai/en/stable/#introduction',
            'base_url': 'https://docs.llamaindex.ai/en/stable/',
        },
        provide_context=True,
    )


    # Task 2: Process and Store Code
    process_task = PythonOperator(
        task_id='process_and_store_task',
        python_callable=process_content,
        op_kwargs={
            'file_dir': 'llamaindex'
        },
        provide_context=True,  # Important for XCom
    )

    # Task 3: Store Documents in Pinecone
    store_task = PythonOperator(
        task_id='store_to_pinecone_task',
        python_callable=store_to_pinecone,
        op_kwargs={
            'index_name': 'llamaindex'  # Pass the index name dynamically here
        },
        provide_context=True,  # Important for XCom
    )

    # Define task dependencies
    load_task >> process_task >> store_task