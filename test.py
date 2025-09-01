import pandas as pd
import pyodbc

CSV_FILE = r"C:\Users\Chinnawat\Downloads\EDMI_log_2025-07-30.csv"

# อ่านโดยให้ pandas จับ space/tab ทั้งหมดเป็นตัวคั่น
df = pd.read_csv(CSV_FILE, header=None, delim_whitespace=True, engine="python")

print("Shape of DataFrame:", df.shape)
print(df.head(3))   # ดูว่าได้กี่ column จริง
