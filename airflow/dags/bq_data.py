from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
#from airflow.contrib.hooks.bigquery_hook import BigQueryHook

dag_args = {
    'owner': 'rebecca.vickery',
    'depends_on_past': False,
    'start_date': datetime(2020, 5, 31),
    'email': ['rebeccavickeryds@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=3)}

dag = DAG(
    dag_id='bq_data',
    start_date=datetime(2020, 5, 31),
    default_args=dag_args,
    end_date=None,
    schedule_interval='0 9 * * *')

t1 = BigQueryOperator(
    task_id='bq_write_to_test',
    use_legacy_sql=False,
    create_disposition='CREATE_IF_NEEDED',
    write_disposition='WRITE_TRUNCATE',
    allow_large_results=True,
    bigquery_conn_id='bigquery_default',
    time_partitioning={
        "type": 'DAY'
        },
    bql='''
    #standardSQL
            select date, 
    sum(total_confirmed_cases) as total_confirmed_cases
    from sandbox-278915:test.covid_italy_daily
    group by date
    ''',
    destination_dataset_table='sandbox-278915:test.covid_test',
    dag=dag)

#t1