import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations
from datetime import timedelta

# Page Setup
st.set_page_config(page_title="Pattern Backtest AI", layout="wide")

st.title("🧪 Pattern Accuracy & Backtest Dashboard")
st.write("पुरानी तारीखें चुनकर चेक करें कि आपका पैटर्न कितना सटीक (Setik) बैठ रहा है।")

# 1. Master Patterns & Config
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# 2. Sidebar - File Upload
uploaded_file = st.sidebar.file_uploader("Data File Upload (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.date
    
    for col in shifts:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- FEATURE 1: MANUAL DATE SELECTION (तारीख बदलने वाला बटन) ---
    st.sidebar.header("📅 विश्लेषण की तारीख चुनें")
    available_dates = df['DATE'].dropna().unique()
    selected_base_date = st.sidebar.selectbox("Base Date चुनें (जिसके आधार पर नंबर निकालने हैं)", options=reversed(available_dates))

    # Get index of selected date
    base_idx = df[df['DATE'] == selected_base_date].index[0]
    
    # --- CALCULATION LOGIC ---
    # Success patterns up to selected date for trend analysis
    success_history = []
    for i in range(1, base_idx + 1):
        today_vals = set(df.loc[i-1, shifts].dropna().values)
        tmrw_vals = set(df.loc[i, shifts].dropna().values)
        found = [p for v in today_vals for p in master_patterns if (v + p) % 100 in tmrw_vals]
        success_history.append(list(set(found)))

    # Get Top Patterns for this specific window
    flat_recent = [p for sub in success_history[-30:] for p in sub]
    top_patterns = [p for p, c in Counter(flat_recent).most_common(10)]

    # --- RESULTS SECTION ---
    st.header(f"📍 {selected_base_date} के आधार पर विश्लेषण")
    
    base_nums = df.loc[base_idx, shifts].dropna().to_dict()
    predicted_nums = set()
    for v in base_nums.values():
        for p in top_patterns:
            predicted_nums.add(int((v + p) % 100))

    # Check if next day data exists for verification
    if base_idx + 1 < len(df):
        next_date = df.loc[base_idx + 1, 'DATE']
        actual_nums = set(df.loc[base_idx + 1, shifts].dropna().values)
        hits = predicted_nums.intersection(actual_nums)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Base Date Numbers", f"{list(base_nums.values())}")
        c2.metric(f"Actual Result ({next_date})", f"{list(actual_nums)}")
        c3.metric("Total Hits (सटीक नंबर)", len(hits))
        
        if hits:
            st.success(f"✅ पास हुए नंबर: {sorted(list(hits))}")
        else:
            st.error("❌ इस दिन कोई नंबर मैच नहीं हुआ।")
    else:
        st.warning(f"{selected_base_date} के बाद का डेटा उपलब्ध नहीं है। यह भविष्य की प्रेडिक्शन है।")
        st.write(f"कल के संभावित नंबर: {sorted(list(predicted_nums))}")

    # --- FEATURE 2: 10-DAY BACKTEST SCOREBOARD ---
    st.divider()
    st.header("📊 पिछले 10 दिनों का रिपोर्ट कार्ड (Accuracy Check)")
    
    backtest_data = []
    # Loop for last 10 days
    start_test = max(1, len(df) - 11)
    end_test = len(df) - 1
    
    hits_count = 0
    for i in range(start_test, end_test):
        b_date = df.loc[i, 'DATE']
        b_nums = df.loc[i, shifts].dropna().values
        next_actual = set(df.loc[i+1, shifts].dropna().values)
        
        # Simple prediction with top 10 patterns
        d_preds = set()
        for v in b_nums:
            for p in top_patterns:
                d_preds.add(int((v + p) % 100))
        
        d_hits = d_preds.intersection(next_actual)
        status = "✅ Pass" if d_hits else "❌ Fail"
        if d_hits: hits_count += 1
        
        backtest_data.append({
            "तारीख": b_date,
            "रिजल्ट": status,
            "मैच हुए नंबर": sorted(list(d_hits)) if d_hits else "-"
        })

    st.table(backtest_data)
    st.write(f"🎯 **कुल स्कोर:** 10 में से **{hits_count}** दिन प्रेडिक्शन सटीक रही।")

else:
    st.info("Sidebar में अपनी फाइल अपलोड करें।")
        
