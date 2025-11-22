FROM quay.io/astronomer/astro-runtime:12.1.1

# Install dbt adapter (adjust based on your database)
# Uncomment the one you need:
# RUN pip install dbt-postgres
# RUN pip install dbt-snowflake
# RUN pip install dbt-bigquery
# RUN pip install dbt-redshift
