import pandas as pd
from datetime import datetime, time, timedelta
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import os
import joblib
import sys

# --- Helper for PyInstaller bundled data ---
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename

# ---------- Load Pre-trained Models ----------
holiday_model = joblib.load(resource_path("holiday_model.pkl"))
onpeak_model = joblib.load(resource_path("onpeak_model.pkl"))
offpeak_model = joblib.load(resource_path("offpeak_model.pkl"))
holiday_kwh_model = joblib.load(resource_path("holiday_kwh_model.pkl"))

# ---------- Prediction Logic ----------
def predict_and_export(start_kwh, end_kwh, date_from, date_to):
    # ลบไฟล์ predicted_power_data.csv ถ้ามีอยู่แล้ว
    if os.path.exists("predicted_power_data.csv"):
        os.remove("predicted_power_data.csv")
    total_kwh = end_kwh - start_kwh
    missing_dates = pd.date_range(start=date_from, end=date_to, freq="D")
    future = pd.DataFrame({'transaction_date': missing_dates})
    future['day'] = future['transaction_date'].dt.day
    future['month'] = future['transaction_date'].dt.month
    future['year'] = future['transaction_date'].dt.year
    future['weekday'] = future['transaction_date'].dt.weekday
    future['is_weekend'] = future['weekday'].isin([5,6]).astype(int)
    # Predict holiday
    future['is_holiday_pred'] = holiday_model.predict(future[['day', 'month', 'year', 'weekday', 'is_weekend']]).round().astype(int)
    # Predict kwh
    future['onpeak_kwh'] = 0.0
    future['offpeak_kwh'] = 0.0
    future['holiday_kwh'] = 0.0
    not_holiday_idx = future['is_holiday_pred'] == 0
    future.loc[not_holiday_idx, 'onpeak_kwh'] = onpeak_model.predict(future.loc[not_holiday_idx, ['day', 'month', 'year', 'weekday', 'is_weekend']])
    future.loc[not_holiday_idx, 'offpeak_kwh'] = offpeak_model.predict(future.loc[not_holiday_idx, ['day', 'month', 'year', 'weekday', 'is_weekend']])
    holiday_idx = future['is_holiday_pred'] == 1
    if holiday_idx.any():
        future.loc[holiday_idx, 'holiday_kwh'] = holiday_kwh_model.predict(future.loc[holiday_idx, ['day', 'month', 'year', 'weekday', 'is_weekend']])
    future['kwh'] = future['onpeak_kwh'] + future['offpeak_kwh'] + future['holiday_kwh']
    # Scale ให้ผลรวม kwh ตรงกับที่ user กรอก
    scale_factor = total_kwh / future['kwh'].sum()
    for col in ['kwh', 'onpeak_kwh', 'offpeak_kwh', 'holiday_kwh']:
        future[col] *= scale_factor
    # คำนวณ start_kwh, end_kwh
    future['start_kwh'] = 0.0
    future.at[0, 'start_kwh'] = start_kwh
    for i in range(1, len(future)):
        future.at[i, 'start_kwh'] = future.at[i-1, 'start_kwh'] + future.at[i-1, 'kwh']
    future['end_kwh'] = future['start_kwh'] + future['kwh']
    # Export
    future['transaction_date'] = future['transaction_date'].dt.strftime('%Y-%m-%d')
    result = future[['transaction_date', 'start_kwh', 'end_kwh', 'kwh', 'onpeak_kwh', 'offpeak_kwh', 'holiday_kwh']]
    for col in ['onpeak_kwh', 'offpeak_kwh', 'holiday_kwh', 'kwh']:
        result[col] = result[col].round(3)
    result['kwh'] = result['onpeak_kwh'] + result['offpeak_kwh'] + result['holiday_kwh']
    # เรียงวันที่จากล่าสุดไปอดีต
    result = result.sort_values('transaction_date', ascending=False).reset_index(drop=True)
    result.to_csv("predicted_power_data.csv", index=False, float_format='%.3f')
    return result

# ---------- GUI ----------
def run_gui():
    def on_predict():
        try:
            # Validate number input (allow paste from any keyboard layout)
            try:
                start_kwh = float(entry_start.get().replace(",", "").strip())
                end_kwh = float(entry_end.get().replace(",", "").strip())
            except Exception:
                messagebox.showerror("Error", "กรุณากรอกตัวเลข start_kwh และ end_kwh ให้ถูกต้อง")
                return
            date_from = entry_date_from.get()
            date_to = entry_date_to.get()
            # Validate date
            try:
                date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
                date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")
            except Exception:
                messagebox.showerror("Error", "กรุณากรอกวันที่ในรูปแบบ YYYY-MM-DD")
                return
            if end_kwh <= start_kwh:
                messagebox.showerror("Error", "end_kwh ต้องมากกว่า start_kwh")
                return
            if date_to_dt < date_from_dt:
                messagebox.showerror("Error", "วันที่สิ้นสุดต้องมากกว่าหรือเท่ากับวันที่เริ่มต้น")
                return
            predict_and_export(start_kwh, end_kwh, date_from, date_to)
            messagebox.showinfo("Success", "สร้างไฟล์ predicted_power_data.csv เรียบร้อยแล้ว!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("AI Power Data Predictor")
    root.geometry("430x420")
    root.configure(bg="#f4f6fa")
    font_label = ("Segoe UI", 12)
    font_entry = ("Segoe UI", 12)
    font_btn = ("Segoe UI", 13, "bold")
    # Header
    header = tk.Label(root, text="AI Power Data Predictor", font=("Segoe UI", 16, "bold"), fg="#1a237e", bg="#f4f6fa")
    header.pack(pady=(18, 10))
    # Start kWh
    frame1 = tk.Frame(root, bg="#f4f6fa")
    frame1.pack(pady=5, fill="x", padx=30)
    tk.Label(frame1, text="หน่วยที่เก็บก่อนหาย (start_kwh):", font=font_label, bg="#f4f6fa").pack(side="left")
    entry_start = tk.Entry(frame1, font=font_entry, width=15, justify="right")
    entry_start.pack(side="right")
    # End kWh
    frame2 = tk.Frame(root, bg="#f4f6fa")
    frame2.pack(pady=5, fill="x", padx=30)
    tk.Label(frame2, text="หน่วยที่แสดงหลังจากหาย (end_kwh):", font=font_label, bg="#f4f6fa").pack(side="left")
    entry_end = tk.Entry(frame2, font=font_entry, width=15, justify="right")
    entry_end.pack(side="right")
    # Custom validation: allow any paste, check only on Predict
    # Date from
    frame3 = tk.Frame(root, bg="#f4f6fa")
    frame3.pack(pady=5, fill="x", padx=30)
    tk.Label(frame3, text="วันที่เริ่มต้น:", font=font_label, bg="#f4f6fa").pack(side="left")
    entry_date_from = DateEntry(frame3, date_pattern='yyyy-mm-dd', font=font_entry, width=12, background="#e3eafc", foreground="#1a237e", borderwidth=2)
    entry_date_from.pack(side="right")
    # Date to
    frame4 = tk.Frame(root, bg="#f4f6fa")
    frame4.pack(pady=5, fill="x", padx=30)
    tk.Label(frame4, text="วันที่สิ้นสุด:", font=font_label, bg="#f4f6fa").pack(side="left")
    entry_date_to = DateEntry(frame4, date_pattern='yyyy-mm-dd', font=font_entry, width=12, background="#e3eafc", foreground="#1a237e", borderwidth=2)
    entry_date_to.pack(side="right")
    # Spacer
    tk.Label(root, text="", bg="#f4f6fa").pack(pady=8)
    # Predict Button
    btn = tk.Button(root, text="Predict", command=on_predict, font=font_btn, bg="#1976d2", fg="white", activebackground="#1565c0", activeforeground="white", height=2, width=20, bd=0, relief="ridge", cursor="hand2")
    btn.pack(pady=10)
    # Footer
    tk.Label(root, text="© 2025 Power AI | github copilot", font=("Segoe UI", 9), fg="#888", bg="#f4f6fa").pack(side="bottom", pady=8)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
