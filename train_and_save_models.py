import pandas as pd
import xgboost as xgb
import joblib

def train_and_save_models():
    df = pd.read_csv("database_oichi_sri.csv", parse_dates=["transaction_date"])
    df['day'] = df['transaction_date'].dt.day
    df['month'] = df['transaction_date'].dt.month
    df['year'] = df['transaction_date'].dt.year
    df['weekday'] = df['transaction_date'].dt.weekday
    df['is_weekend'] = df['weekday'].isin([5, 6]).astype(int)
    df['is_holiday'] = (df['holiday_kwh'] > 0).astype(int)
    features = ['day', 'month', 'year', 'weekday', 'is_weekend']
    # Holiday classifier
    holiday_model = xgb.XGBClassifier(n_estimators=200, random_state=42, use_label_encoder=False, eval_metric='logloss')
    holiday_model.fit(df[features], df['is_holiday'])
    # Onpeak/offpeak regressors (non-holiday)
    not_holiday = df['is_holiday'] == 0
    onpeak_train = df.loc[not_holiday & df['onpeak_kwh'].notna()]
    offpeak_train = df.loc[not_holiday & df['offpeak_kwh'].notna()]
    onpeak_model = xgb.XGBRegressor(n_estimators=200, random_state=42)
    onpeak_model.fit(onpeak_train[features], onpeak_train['onpeak_kwh'])
    offpeak_model = xgb.XGBRegressor(n_estimators=200, random_state=42)
    offpeak_model.fit(offpeak_train[features], offpeak_train['offpeak_kwh'])
    # Holiday kwh regressor
    holiday_kwh_train = df[(df['is_holiday'] == 1) & (df['holiday_kwh'].notna())]
    holiday_kwh_model = xgb.XGBRegressor(n_estimators=200, random_state=42)
    if len(holiday_kwh_train) > 0:
        holiday_kwh_model.fit(holiday_kwh_train[features], holiday_kwh_train['holiday_kwh'])
    # Save models
    joblib.dump(holiday_model, 'holiday_model.pkl')
    joblib.dump(onpeak_model, 'onpeak_model.pkl')
    joblib.dump(offpeak_model, 'offpeak_model.pkl')
    joblib.dump(holiday_kwh_model, 'holiday_kwh_model.pkl')
    print('✅ บันทึกโมเดล XGBoost เป็นไฟล์ .pkl เรียบร้อย')

if __name__ == "__main__":
    train_and_save_models()
