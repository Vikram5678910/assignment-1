import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import altair as alt

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.set_page_config(page_title="👮 SecureCheck: Police Check", layout="wide")

st.title("👮 SecureCheck: Police Check")
st.write("Welcome! This is your Streamlit SecureCheck: Police Check.")

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
try:
    # Encode password properly (important if it has special characters)
    password = urllib.parse.quote_plus("Vikram123")

    # Create engine for MySQL (root user, database = securecheck)
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost/securecheck")

    # Test query
    query = "SELECT * FROM traffic_stops LIMIT 10;"
    df = pd.read_sql(query, engine)

  
    st.write("Here is a preview of your data:")
    st.dataframe(df)

    # Example chart
    if "violation" in df.columns:
        st.subheader("📊 Violations Count")
        # Make sure this is **outside** the if
        
     # Prepare data
    violation_counts = df["violation"].value_counts().reset_index()
    violation_counts.columns = ["violation", "count"]

    # Assign colors based on count
    def assign_color(count):
        if count == 3:
            return "skyblue"
        elif count == 2:
            return "lightgreen"
        elif count == 1:
            return "darkred"
        else:
            return "gray"  # default for other counts

    violation_counts["color"] = violation_counts["count"].apply(assign_color)

    bar = alt.Chart(violation_counts).mark_bar().encode(
    x='count',
    y=alt.Y('violation', sort='-x'),  # horizontal bars
    color=alt.Color('color', scale=None)
)
    text = bar.mark_text(
    align='left',        # align text to the left of label
    baseline='middle',   # vertical center
    dx=5                 # 5 pixels to the right of bar
).encode(
    text='violation'
)
    chart = (bar + text).properties(
    width=600,
    height=400
)
    st.altair_chart(chart)
    
    st.header("📈 Advanced Insights")

    # Dropdown for queries
    query_option = st.selectbox(
        "Select a Query to Run",
        [
            "Top 10 Vehicle Numbers in Drug-Related Stops",
            "Vehicles Most Frequently Searched",
            "Driver Age Group with Highest Arrest Rate",
            "Gender Distribution of Drivers Stopped in Each Country",
            "Race & Gender with Highest Search Rate",
            "Time of Day with Most Traffic Stops",
            "Average Stop Duration by Violation",
            "Are Night Stops More Likely to Lead to Arrests?",
            "Violations Associated with Searches/Arrests",
            "Violations Common Among Younger Drivers (<25)",
            "Violations Rarely Resulting in Search/Arrest",
            "Arrest Rate by Country & Violation",
            "Country with Most Stops Involving Searches",
            "Yearly Breakdown of Stops & Arrests by Country",
            "Top 5 Violations with Highest Arrest Rates"
        ]
    )

    
    queries = {
       "Top 10 Vehicle Numbers in Drug-Related Stops": """
         SELECT vehicle_number, COUNT(*) AS stop_count
         FROM traffic_stops
         WHERE drugs_related_stop = 1
         GROUP BY vehicle_number
         ORDER BY stop_count DESC
         LIMIT 10;
      """,
        "Vehicles Most Frequently Searched": """
            SELECT vehicle_number, COUNT(*) AS search_count
            FROM traffic_stops
            WHERE search_conducted = 1
            GROUP BY vehicle_number
            ORDER BY search_count DESC
            LIMIT 10;
        """,
        "Driver Age Group with Highest Arrest Rate": """
            SELECT driver_age, 
                   SUM(is_arrested)/COUNT(*)*100 AS arrest_rate
            FROM traffic_stops
            GROUP BY driver_age
            ORDER BY arrest_rate DESC
            LIMIT 10;
        """,
        "Gender Distribution of Drivers Stopped in Each Country": """
            SELECT country_name, driver_gender, COUNT(*) AS stop_count
            FROM traffic_stops
            GROUP BY country_name, driver_gender;
        """,
        "Race & Gender with Highest Search Rate": """
            SELECT driver_race, driver_gender,
                   SUM(search_conducted)/COUNT(*)*100 AS search_rate
            FROM traffic_stops
            GROUP BY driver_race, driver_gender
            ORDER BY search_rate DESC
            LIMIT 10;
        """,
        "Time of Day with Most Traffic Stops": """
            SELECT HOUR(stop_time) AS hour_of_day, COUNT(*) AS stop_count
            FROM traffic_stops
            GROUP BY hour_of_day
            ORDER BY stop_count DESC;
        """,
        "Average Stop Duration by Violation": """
            SELECT violation, AVG(stop_duration) AS avg_duration
            FROM traffic_stops
            GROUP BY violation;
        """,
        "Are Night Stops More Likely to Lead to Arrests?": """
            SELECT CASE WHEN HOUR(stop_time) BETWEEN 20 AND 23 
                        OR HOUR(stop_time) BETWEEN 0 AND 5 
                        THEN 'Night' ELSE 'Day' END AS time_period,
                   SUM(is_arrested)/COUNT(*)*100 AS arrest_rate
            FROM traffic_stops
            GROUP BY time_period;
        """,
        "Violations Associated with Searches/Arrests": """
            SELECT violation,
                   SUM(search_conducted) AS total_searches,
                   SUM(is_arrested) AS total_arrests
            FROM traffic_stops
            GROUP BY violation
            ORDER BY total_searches DESC, total_arrests DESC;
        """,
        "Violations Common Among Younger Drivers (<25)": """
            SELECT 
               COALESCE(violation, 'Unknown') AS violation,
               COUNT(*) AS stop_count
           FROM traffic_stops
           WHERE driver_age < 25
           GROUP BY violation
           ORDER BY stop_count DESC;
        """,
        "Violations Rarely Resulting in Search/Arrest": """
        SELECT COALESCE(violation, 'Unknown') AS violation,
                SUM(search_conducted) AS total_searches,
                SUM(is_arrested) AS total_arrests
        FROM traffic_stops
        GROUP BY violation
        ORDER BY total_searches ASC, total_arrests ASC
        LIMIT 10;
        """,
        "Countries with Highest Drug-Related Stops": """
            SELECT country_name, COUNT(*) AS drug_stops
            FROM traffic_stops
            WHERE violation LIKE '%drug%'
            GROUP BY country_name
            ORDER BY drug_stops DESC;
        """,
        "Arrest Rate by Country & Violation": """
            SELECT country_name, violation,
                   SUM(is_arrested)/COUNT(*)*100 AS arrest_rate
            FROM traffic_stops
            GROUP BY country_name, violation
            ORDER BY arrest_rate DESC
            LIMIT 20;
        """,
        "Country with Most Stops Involving Searches": """
            SELECT country_name, SUM(search_conducted) AS total_searches
            FROM traffic_stops
            GROUP BY country_name
            ORDER BY total_searches DESC;
        """,
        "Yearly Breakdown of Stops & Arrests by Country": """
            SELECT country_name, YEAR(stop_date) AS year,
                   COUNT(*) AS total_stops,
                   SUM(is_arrested) AS total_arrests
            FROM traffic_stops
            GROUP BY country_name, YEAR(stop_date)
            ORDER BY year, country_name;
        """,
        "Top 5 Violations with Highest Arrest Rates": """
            SELECT violation, 
               ROUND(SUM(is_arrested)/COUNT(*)*100, 2) AS arrest_rate
            FROM traffic_stops
            GROUP BY violation
            ORDER BY arrest_rate DESC
            LIMIT 5;
        """

    }

   
    if query_option in queries:
        
       result_df = pd.read_sql(queries[query_option], engine)


       result_df = result_df.astype(str)


       st.write(f"**Results for: {query_option}**")
       st.dataframe(result_df)


except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.info("But Streamlit is working fine . Check your MySQL setup or table.")
except Exception as e:
    st.error(f" Database connection failed: {e}")
    st.info("But Streamlit is working fine . Check your MySQL setup or table.")

# ---------------------------
# 🚔 Add New Police Log & Predict Outcome and Violation
# ---------------------------
import random  

st.markdown("---")
st.title("🚔 Add New Police Log & Predict Outcome and Violation")


stop_date = st.date_input("Stop Date")
stop_time = st.time_input("Stop Time")
county_name = st.text_input("County Name")
driver_gender = st.selectbox("Driver Gender", ["male", "female"])
driver_age = st.number_input("Driver Age", min_value=16, max_value=100, step=1)
driver_race = st.text_input("Driver Race")
search_conducted = st.selectbox("Was a Search Conducted?", ["Yes", "No"])
search_type = st.text_input("Search Type (if any)")
drug_related = st.selectbox("Was it Drug Related?", ["Yes", "No"])
stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
vehicle_number = st.text_input("Vehicle Number")


if st.button("Predict Stop Outcome & Violation"):

    
    predicted_violation = random.choice(["speeding", "signal violation", "DUI", "equipment violation"])
    predicted_outcome = random.choice(["warning", "citation", "arrest"])

    
    st.subheader("📝 Prediction Summary")
    st.markdown(f"- **Predicted Violation:** {predicted_violation}")
    st.markdown(f"- **Predicted Stop Outcome:** {predicted_outcome}")

    
    if search_conducted == "No":
        search_text = "No search was conducted"
    else:
        search_text = f"A search was conducted ({search_type})"

    summary = (
        f"🚗 A {driver_age}-year-old {driver_gender} driver was stopped for "
        f"**{predicted_violation.capitalize()}** at {stop_time.strftime('%I:%M %p')}. "
        f"{search_text}, and he received a **{predicted_outcome}**. "
        f"The stop lasted {stop_duration} and was "
        f"{'drug-related' if drug_related == 'Yes' else 'not drug-related'}."
    )

    st.write(summary)









