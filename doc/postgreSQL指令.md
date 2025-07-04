### 匯入 CSV 到 postgreSQL :

COPY code FROM 'C:/ytdb/database/code.csv'
WITH (
FORMAT csv,
HEADER true,
DELIMITER ',',
NULL '',
ENCODING 'UTF8'
);
