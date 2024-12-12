from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from data_load.process_documentation_pages.scrape_url import load_recursive_url
from data_load.process_documentation_pages.process_docs import process_content
from data_load.process_documentation_pages.load_into_pinecone import store_to_pinecone


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),  
    'start_date': datetime(2023, 11, 27),
}


with DAG(
    'documentation_extraction_dag',
    default_args=default_args,
    description='A DAG for extracting documentation pages, parsing files, storing them in AWS, and loading vector embeddings into Pinecone',
    schedule_interval=None,  
    catchup=False
) as dag:
    # Task 1: Load Recursive URL
    load_task = PythonOperator(
        task_id='load_recursive_url_task',
        python_callable=load_recursive_url,
        op_kwargs={
            'start_url': Variable.get('start_url', default_var=''),
            'base_url': Variable.get('base_url', default_var=''),
        },
        provide_context=True,
    )


    # Task 2: Process and Store Code
    process_task = PythonOperator(
        task_id='process_and_store_task',
        python_callable=process_content,
        op_kwargs={
            'file_dir': Variable.get('file_dir', default_var=''),
        },
        provide_context=True,  
    )

    # Task 3: Store Documents in Pinecone
    store_task = PythonOperator(
        task_id='store_to_pinecone_task',
        python_callable=store_to_pinecone,
        op_kwargs={
            'index_name': Variable.get('file_dir', default_var=''),
        },
        provide_context=True,
    )

 
    load_task >> process_task >> store_task