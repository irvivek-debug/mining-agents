"""Fetch INC-5059 date and fatigue_logs_node log_id values from BigQuery."""
import sys
sys.path.insert(0, '/Users/amritharajendran/VivekWork/src/mining-agents/data/generator')

from google.cloud import bigquery

client = bigquery.Client(project="genial-union-475913-i7")

# Get INC-5059 date
q1 = """
SELECT incident_id, timestamp
FROM `genial-union-475913-i7.mining_data.safety_incidents`
WHERE incident_id = @inc_id
"""
job1 = client.query(
    q1,
    job_config=bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("inc_id", "STRING", "INC-5059")]
    )
)
rows1 = list(job1)
print("INC-5059 rows:")
for r in rows1:
    print(f"  incident_id={r['incident_id']}  timestamp={r['timestamp']}")

# Get fatigue_logs_node log_id values (ordered by timestamp, operator_id)
q2 = """
SELECT log_id, timestamp, operator_id
FROM `genial-union-475913-i7.mining_data.fatigue_logs_node`
ORDER BY timestamp, operator_id
LIMIT 10
"""
job2 = client.query(q2)
rows2 = list(job2)
print("\nfatigue_logs_node sample (first 10 rows):")
for r in rows2:
    print(f"  log_id={r['log_id']}  ts={r['timestamp']}  op={r['operator_id']}")

# Count total
q3 = "SELECT COUNT(*) as n FROM `genial-union-475913-i7.mining_data.fatigue_logs_node`"
rows3 = list(client.query(q3))
print(f"\nTotal fatigue_logs_node rows: {rows3[0]['n']}")

# Get log_id format to understand pattern
q4 = """
SELECT log_id FROM `genial-union-475913-i7.mining_data.fatigue_logs_node`
WHERE operator_id = 'OP-113'
ORDER BY timestamp
LIMIT 5
"""
rows4 = list(client.query(q4))
print("\nOP-113 log_ids:")
for r in rows4:
    print(f"  {r['log_id']}")
