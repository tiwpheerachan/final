from database import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT NOW();")
print("เวลาปัจจุบันจาก Supabase:", cur.fetchone())

cur.close()
conn.close()
