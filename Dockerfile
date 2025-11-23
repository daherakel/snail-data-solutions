FROM quay.io/astronomer/astro-runtime:12.5.0

# Install dbt-postgres after Astro dependencies to avoid conflicts
RUN pip install --no-cache-dir "dbt-postgres>=1.9.0,<2.0.0"
