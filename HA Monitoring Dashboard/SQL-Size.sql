SELECT table_schema AS 'db_name', ROUND(SUM(data_length + index_length)/1024/1024, 2) AS 'size_mb' FROM information_schema.TABLES WHERE table_schema='homeassistant’
