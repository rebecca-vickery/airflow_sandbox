from datetime import timedelta, datetime
from airflow import DAG
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
from airflow.contrib.operators.bigquery_check_operator import BigQueryCheckOperator

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
    dag_id='covid_italy_daily',
    start_date=datetime(2020, 5, 31),
    default_args=dag_args,
    end_date=None,
    schedule_interval='0 9 * * *')

t1 = BigQueryCheckOperator(task_id='check_public_data_exists',
                           sql="""
                            select count(*) > 0
                            from bigquery-public-data.covid19_italy.data_by_region
                            where DATE(date) = '{{ ds }}'
                        """,
                           use_legacy_sql=False)

t2 = BigQueryOperator(
    task_id='load_public_data',
    use_legacy_sql=False,
    create_disposition='CREATE_IF_NEEDED',
    write_disposition='WRITE_TRUNCATE',
    allow_large_results=True,
    bigquery_conn_id='bigquery_default',
    time_partitioning={
        "type": 'DAY'
        },
    sql='''
    #standardSQL
            select date, 
    sum(total_confirmed_cases) as total_confirmed_cases
    from bigquery-public-data.covid19_italy.data_by_region
    where DATE(date) = '{{ ds }}'
    group by date
    ''',
    destination_dataset_table='sandbox-278915:airflow.covid_italy_daily_cases',
    dag=dag)

t1 >> t2