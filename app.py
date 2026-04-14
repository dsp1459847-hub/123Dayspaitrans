import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations
from datetime import timedelta

# Page Setup
st.set_page_config(page_title="Master Pattern AI", layout="wide")

st.title("🎯 Ultimate Pattern Prediction & Backtest Tool")
st.write("आज के नंबरों से पैटर्न निकालें और अगले 24-48 घंटों के सटीक नंबर पाएं।")

# 1. Master Patterns Config
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# 2. Sidebar - File Upload
uploaded_file = st.sidebar.file_uploader("Data File (CSV/Excel)", type=['csv', 'xlsx'])
window = st.sidebar.select_slider("Trend Window (Days)", options=[1, 3, 7, 10, 15, 30], value=30)

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE']).dt.date
    
    for col in shifts:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

    # --- DATE SELECTION ---
    st.sidebar.header("📅 तारीख चुनें")
    available_dates = df['DATE'].dropna().unique()
    selected_base_date = st.sidebar.selectbox("Base Date (प्रेडिक्शन के लिए):", options=reversed(available_dates))
    base_idx = df[df['DATE'] == selected_base_date].index[0]

    # --- STEP 1: PATTERN EXTRACTION (पैटर्न निकालना) ---
    st.header(f"🔍 स्टेप 1: {selected_base_date} के पैटर्न का विश्लेषण")
    
    # Yesterday for sequence logic
    yesterday_vals = df.loc[base_idx-1, shifts].dropna().values if base_idx > 0 else []
    today_vals = df.loc[base_idx, shifts].dropna().to_dict()
    
    # Finding what patterns worked today
    today_worked_ps = []
    if len(yesterday_vals) > 0:
        for v_y in yesterday_vals:
            for v_t in today_vals.values():
                p = int((v_t - v_y) % 100)
                for mp in master_patterns:
                    if mp % 100 == p:
                        today_worked_ps.append(mp)
    
    st.write(f"आज के सक्रिय पैटर्न (Active Patterns): `{list(set(today_worked_ps))}`")

    # --- STEP 2: NUMBER GENERATION (नंबर प्रेडिक्शन) ---
    st.header(f"🔮 स्टेप 2: {selected_base_date} के आधार पर अगले दिन के नंबर")
    
    # Application of All 22 Patterns
    all_gen_nums = []
    for s_val in today_vals.values():
        for p in master_patterns:
            all_gen_nums.append(int((s_val + p) % 100))
    
    num_counts = Counter(all_gen_nums)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("🔥 Super Strong (4+ Bar)")
        super_list = sorted([n for n, c in num_counts.items() if c >= 4])
        st.write(super_list if super_list else "None")
        
    with c2:
        st.subheader("⭐ Strong (2-3 Bar)")
        st.write(sorted([n for n, c in num_counts.items() if 2 <= c <= 3]))
        
    with c3:
        st.subheader("📍 Normal (1 Bar)")
        st.write(sorted([n for n, c in num_counts.items() if c == 1]))

    # --- STEP 3: BACKTESTING (नतीजा चेक करना) ---
    st.divider()
    st.header("🧪 स्टेप 3: बैक-टेस्ट (क्या प्रेडिक्शन सही थी?)")
    
    if base_idx + 1 < len(df):
        next_date = df.loc[base_idx + 1, 'DATE']
        actual_nums = set(df.loc[base_idx + 1, shifts].dropna().values)
        predicted_set = set(all_gen_nums)
        hits = predicted_set.intersection(actual_nums)
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(f"असल रिजल्ट ({next_date})", f"{list(actual_nums)}")
        with col_res2:
            st.metric("टोटल मैच (Hits)", len(hits))
        
        if hits:
            st.success(f"✅ पास हुए नंबर: {sorted(list(hits))}")
        else:
            st.error("❌ इस दिन कोई नंबर मैच नहीं हुआ।")
    else:
        st.info("यह सबसे ताज़ा तारीख है, इसका रिजल्ट कल आएगा।")

    # --- STEP 4: 10-DAY ACCURACY SCORE ---
    st.divider()
    st.header("📊 पिछले 10 दिनों का सटीकता स्कोर")
    
    accuracy_data = []
    pass_days = 0
    start_point = max(1, len(df) - 11)
    
    for i in range(start_point, len(df) - 1):
        b_date = df.loc[i, 'DATE']
        b_nums = df.loc[i, shifts].dropna().values
        next_res = set(df.loc[i+1, shifts].dropna().values)
        
        d_preds = set()
        for v in b_nums:
            for p in master_patterns:
                d_preds.add(int((v + p) % 100))
        
        d_hits = d_preds.intersection(next_res)
        if d_hits: pass_days += 1
        accuracy_data.append({
            "तारीख": b_date,
            "रिजल्ट": "✅ Pass" if d_hits else "❌ Fail",
            "मैच": sorted(list(d_hits)) if d_hits else "-"
        })
    
    st.table(accuracy_data)
    st.write(f"🎯 **10 में से {pass_days} दिन सटीक रहे।**")

else:
    st.info("शुरू करने के लिए Sidebar में अपनी एक्सेल फाइल अपलोड करें।")
    
