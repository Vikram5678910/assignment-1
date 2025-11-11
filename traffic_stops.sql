CREATE DATABASE IF NOT EXISTS securecheck;
USE securecheck;
SHOW TABLES;
  
DROP TABLE IF EXISTS traffic_stops;
CREATE TABLE traffic_stops (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  stop_date DATE,
  stop_time TIME,
  country_name VARCHAR(100),
  driver_gender VARCHAR(20),
  driver_age SMALLINT,
  driver_race VARCHAR(50),
  violation_raw VARCHAR(120),
  violation VARCHAR(120),
  search_conducted TINYINT(1),
  search_type VARCHAR(120),
  stop_outcome VARCHAR(50),
  is_arrested TINYINT(1),
  stop_duration VARCHAR(30),
  drugs_related_stop TINYINT(1),
  vehicle_number VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SHOW TABLES;
DESCRIBE traffic_stops;
INSERT INTO traffic_stops (
    stop_date, stop_time, country_name, driver_gender, driver_age, driver_race, 
    violation_raw, violation, search_conducted, search_type, stop_outcome, 
    is_arrested, stop_duration, drugs_related_stop, vehicle_number
)
VALUES
('2025-08-26','14:25:00','India','Male',28,'Asian','speeding - 25 km/h over','speeding',0,NULL,'Warning',0,'0-15 Min',0,'TN10AB1234'),
('2025-08-26','10:15:00','India','Male',28,'Asian','Speeding over 60','Speeding',0,NULL,'Warning',0,'0-15 Min',0,'TN10AB1234'),
('2025-08-26','11:45:00','India','Female',34,'Asian','Red light violation','Signal Violation',1,'Vehicle search','Ticket',0,'16-30 Min',0,'TN22XY5678'),
('2025-08-25','20:05:00','India','Male',42,'Asian','Driving under influence','DUI',1,'Full search','Arrest',1,'30+ Min',1,'KA09GH4321');

-- 6️⃣ Select all
SELECT * FROM traffic_stops
ORDER BY stop_date DESC, stop_time DESC;

-- 7️⃣ Filtered selects
SELECT stop_date, driver_gender, violation, stop_outcome
FROM traffic_stops
WHERE driver_gender = 'Male';

SELECT stop_date, driver_gender, violation, stop_outcome
FROM traffic_stops
WHERE driver_age > 30;

-- 8️⃣ Aggregate queries
SELECT driver_gender, COUNT(*) AS total_stops
FROM traffic_stops
GROUP BY driver_gender;

SELECT violation, COUNT(*) AS total
FROM traffic_stops
GROUP BY violation
ORDER BY total DESC;

SELECT ROUND(AVG(driver_age), 2) AS avg_age
FROM traffic_stops;

SELECT COUNT(*) AS total_stops,
       SUM(search_conducted) AS searched,
       ROUND(100.0 * SUM(search_conducted) / COUNT(*), 2) AS pct_searched
FROM traffic_stops;

SELECT violation, COUNT(*) AS cnt
FROM traffic_stops
WHERE stop_date >= CURDATE() - INTERVAL 7 DAY
GROUP BY violation
ORDER BY cnt DESC;

SELECT violation, COUNT(*) AS cnt
FROM traffic_stops
GROUP BY violation
ORDER BY cnt DESC
LIMIT 5;

SELECT stop_date, COUNT(*) AS arrests
FROM traffic_stops
WHERE is_arrested = 1
GROUP BY stop_date
ORDER BY stop_date;

SELECT violation, COUNT(*) AS searched_count
FROM traffic_stops
WHERE search_conducted = 1
GROUP BY violation
ORDER BY searched_count DESC;

-- 9️⃣ Arrest statistics
SELECT SUM(is_arrested) AS total_arrests,
       COUNT(*) - SUM(is_arrested) AS non_arrests,
       ROUND(100.0 * SUM(is_arrested) / COUNT(*), 2) AS pct_arrests,
       ROUND(100.0 * (COUNT(*) - SUM(is_arrested)) / COUNT(*), 2) AS pct_non_arrests
FROM traffic_stops;

-- 10️⃣ Driver age statistics
SELECT driver_gender,
       AVG(driver_age) AS avg_age,
       MIN(driver_age) AS min_age,
       MAX(driver_age) AS max_age
FROM traffic_stops
GROUP BY driver_gender;

-- 11️⃣ Gender vs Violation count
SELECT driver_gender, violation, COUNT(*) AS total
FROM traffic_stops
GROUP BY driver_gender, violation
ORDER BY driver_gender, total DESC;

-- 12️⃣ Stops per day
SELECT stop_date, COUNT(*) AS total_stops
FROM traffic_stops
GROUP BY stop_date
ORDER BY stop_date DESC;

-- 13️⃣ Top violations
SELECT violation, COUNT(*) AS total
FROM traffic_stops
GROUP BY violation
ORDER BY total DESC;
-- 14 Arrest rate by country and violation
SELECT 
    country,
    violation,
    ROUND(SUM(arrest_made) * 100.0 / COUNT(*), 2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY country, violation
ORDER BY arrest_rate_percent DESC;

-- 15 Country with the most stops where a search was conducted
SELECT 
    country,
    COUNT(*) AS total_searches
FROM traffic_stops
WHERE search_conducted = 1
GROUP BY country
ORDER BY total_searches DESC
LIMIT 1;

-- 16 Yearly Breakdown of Stops and Arrests by Country (Subquery + Window Function)
SELECT 
    country,
    YEAR(date) AS year,
    COUNT(*) AS total_stops,
    SUM(arrest_made) AS total_arrests,
    ROUND(SUM(arrest_made) * 100.0 / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (PARTITION BY country ORDER BY COUNT(*) DESC) AS rank_by_stops
FROM traffic_stops
GROUP BY country, YEAR(date)
ORDER BY country, year;

-- 17 Driver Violation Trends Based on Age and Race (Join with Subquery)
-- Subquery: average age per violation by race
SELECT 
    v.violation,
    d.driver_race,
    ROUND(AVG(d.driver_age), 2) AS avg_age,
    COUNT(*) AS total_drivers
FROM traffic_stops d
JOIN (
    SELECT violation, driver_race
    FROM traffic_stops
    GROUP BY violation, driver_race
) v ON d.violation = v.violation AND d.driver_race = v.driver_race
GROUP BY v.violation, d.driver_race
ORDER BY total_drivers DESC;

-- 18 Time Period Analysis of Stops (Year, Month, Hour)
SELECT 
    YEAR(date) AS year,
    MONTHNAME(date) AS month,
    HOUR(time) AS hour_of_day,
    COUNT(*) AS total_stops
FROM traffic_stops
GROUP BY YEAR(date), MONTHNAME(date), HOUR(time)
ORDER BY year, month, hour_of_day;

-- 19 Violations with High Search and Arrest Rates 
SELECT 
    violation,
    ROUND(SUM(search_conducted) * 100.0 / COUNT(*), 2) AS search_rate,
    ROUND(SUM(arrest_made) * 100.0 / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (ORDER BY SUM(arrest_made) DESC) AS rank_by_arrest
FROM traffic_stops
GROUP BY violation
ORDER BY arrest_rate DESC;

-- 20 Driver Demographics by Country (Age, Gender, and Race)
SELECT 
    country,
    driver_gender,
    driver_race,
    ROUND(AVG(driver_age), 2) AS avg_age,
    COUNT(*) AS total_drivers
FROM traffic_stops
GROUP BY country, driver_gender, driver_race
ORDER BY country, total_drivers DESC;

-- 21 Top 5 Violations with Highest Arrest Rates
SELECT 
    violation,
    ROUND(SUM(arrest_made) * 100.0 / COUNT(*), 2) AS arrest_rate_percent
FROM traffic_stops
GROUP BY violation
ORDER BY arrest_rate_percent DESC
LIMIT 5;

ALTER USER 'root'@'localhost' IDENTIFIED BY 'Vikram123';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS securecheck;
USE securecheck;
SHOW TABLES;
SELECT 1;
CREATE DATABASE securecheck;