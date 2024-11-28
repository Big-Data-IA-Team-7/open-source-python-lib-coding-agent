from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from data_load.docs_scrape_page import load_recursive_url
from data_load.process_docs import process_content
from data_load.load_into_pinecone import store_to_pinecone

def create_dag():
    with DAG(
        'langgraph_extraction_dag',
        default_args={
            'owner': 'airflow',
            'start_date': datetime(2023, 11, 27),
            'retries': 1,
        },
        description='A DAG for extracting the documentation pages, parse the py files separately, store them into AWS and load the processed format as vector embeddings into Pinecone',
        schedule_interval=None,
        catchup=False
    ) as dag:

        # Task 1: Load Recursive URL Loader
        load_task = PythonOperator(
            task_id='load_recursive_url_task',
            python_callable=load_recursive_url
        )

        # Task 2: Process and Store Code
        process_task = PythonOperator(
            task_id='process_and_store_task',
            python_callable=process_content,
            provide_context=True,
            op_kwargs={'output_dir': 'langgraph_code_extracts'}
        )

        # Task 3: Store Documents in Pinecone
        store_task = PythonOperator(
            task_id='store_to_pinecone_task',
            python_callable=store_to_pinecone,
            provide_context=True
        )

        # Task dependencies
        load_task >> process_task >> store_task

    return dag

dag = create_dag()
