AI Power Data Predictor
-----------------------

📦 โปรแกรมนี้ช่วยคาดการณ์การใช้พลังงานไฟฟ้ารายวัน โดยแยก On-peak, Off-peak และวันหยุด
ใช้งานง่ายผ่านหน้าต่าง GUI ไม่ต้องใช้ Excel

🛠️ ความต้องการ
---------------
1. ติดตั้ง Python 3.8 ขึ้นไป  
   ดาวน์โหลดได้จาก https://www.python.org/downloads/windows/

2. ติดตั้งไลบรารีด้วยคำสั่ง:

   pip install -r requirements.txt


📁 รายชื่อไฟล์ที่ต้องมีในโฟลเดอร์
---------------------------------
- `predict_gui.py`              ← โปรแกรมหลัก
- `train_and_save_models.py`    ← สคริปต์สำหรับเทรนโมเดล
- `database_oichi_sri.csv`      ← ไฟล์ข้อมูลสำหรับเทรนโมเดล
- `requirements.txt`            ← รายการไลบรารีที่ต้องติดตั้ง


⚙️ วิธีเตรียมโมเดล (ต้องทำก่อนใช้งาน)
--------------------------------------
1. เปิด Command Prompt หรือ Terminal
2. เปลี่ยน directory มาที่โฟลเดอร์โปรเจกต์ เช่น:

   cd D:\Users\YourName\Documents\power_predictor

3. รันคำสั่งนี้เพื่อเทรนและบันทึกโมเดล `.pkl`:

   python train_and_save_models.py

4. หลังจากรันเสร็จ จะได้ไฟล์:
   - `holiday_model.pkl`
   - `onpeak_model.pkl`
   - `offpeak_model.pkl`
   - `holiday_kwh_model.pkl`

   ซึ่งใช้สำหรับโปรแกรมหลักในการพยากรณ์


🚀 วิธีใช้งานโปรแกรม
---------------------
1. รันโปรแกรมโดยพิมพ์:

   python predict_gui.py

2. กรอกข้อมูลในหน้าต่าง GUI แล้วคลิก “Predict”
3. ระบบจะสร้างไฟล์ `predicted_power_data.csv` ให้อัตโนมัติในโฟลเดอร์นี้


ℹ️ หมายเหตุ
-----------
- รองรับเฉพาะ Windows
- หากเจอปัญหาเกี่ยวกับ `xgboost.dll` ให้ลองติดตั้งใหม่โดยพิมพ์:
  
  pip install --force-reinstall xgboost


