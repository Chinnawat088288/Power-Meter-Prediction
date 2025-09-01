import pandas as pd
import pyodbc

# ================== CONFIG ==================
CSV_FILE = r"D:\work\TCC\bill meter\Code\EDMI_log_2025-07-30.csv"   # ไฟล์ csv ของคุณ
SERVER = "100.84.39.62\TBE_DB_2022"             # ชื่อ SQL Server หรือ IP
DATABASE = "Energy_DB_P1_2"
USERNAME = "sa"                  # user SQL Server
PASSWORD = "TBE@w0rd"        # password
TABLE = "LOG_OICHT_CBI"

# ================== STEP 1: READ CSV ==================
col_names = [
    "CREATE_DATE","HW_DEVICE_ID","TRANSACTION_DATE","ENERGY_KWH",
    "ENERGY_L1","ENERGY_L2","ENERGY_L3",
    "ENERGY_KW1","ENERGY_KW2","ENERGY_KW3","ENERGY_HZ"
]

# อ่าน CSV โดยบังคับชื่อ column และ skip header row
df = pd.read_csv(
    CSV_FILE,
    header=None,
    skiprows=1,           # ข้าม header row
    usecols=range(11),    # ใช้เฉพาะ 11 คอลัมน์แรก
    names=col_names
)

# ลบแถวว่างทั้งหมด
df = df.dropna(how="all")

print("Columns in DataFrame:", df.columns.tolist())
print("Shape:", df.shape)
print(df.head())

# ================== STEP 2: CLEAN ==================
df = df.replace(["null", "NULL", "Null", " "], None)

# ================== STEP 3: CONNECT SQL SERVER ==================
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# ================== STEP 4: INSERT ==================
insert_query = f"""
INSERT INTO {TABLE} 
(HW_DEVICE_ID, CREATE_DATE, ENERGY_KWH, ENERGY_L1, ENERGY_L2, ENERGY_L3, ENERGY_KW1, ENERGY_KW2, ENERGY_KW3, ENERGY_HZ)
VALUES (?,?,?,?,?,?,?,?,?,?)
"""

for i, row in df.iterrows():
    try:
        values = [
            int(row["HW_DEVICE_ID"]),
            pd.to_datetime(row["CREATE_DATE"]),
            float(row["ENERGY_KWH"]),
            float(row["ENERGY_L1"]),
            float(row["ENERGY_L2"]),
            float(row["ENERGY_L3"]),
            float(row["ENERGY_KW1"]),
            float(row["ENERGY_KW2"]),
            float(row["ENERGY_KW3"]),
            float(row["ENERGY_HZ"])
        ]
        cursor.execute(insert_query, values)
    except Exception as e:
        print(f"❌ Error at row {i}: {e}")
        print(row)
        break

conn.commit()
cursor.close()
conn.close()

print("✅ Insert Completed")