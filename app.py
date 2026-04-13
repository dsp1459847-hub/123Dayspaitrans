import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations

# Page Configuration
st.set_page_config(page_title="Advanced Pattern Sequence AI", layout="wide")

st.title("📊 Advanced Pattern Sequence & Time-Window Analysis")
st.write("1 दिन से लेकर 30 दिन तक के डेटा का गहन विश्लेषण और पैटर्न प्रेडिक्शन।")

# 1. Master Patterns List
master_patterns = [0, -18, -16, -26, -32, -1, -4, -11, -15, -10, -51, -50, 15, 5, -5, -55, 1, 10, 11, 51, 55, -40]
shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG']

# 2. File Upload
uploaded_file = st.sidebar.file_uploader("अपनी एक्सेल/CSV फाइल अपलोड करें", type=['csv', 'xlsx'])

if uploaded_file:
    # Load Data
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Clean Data
    for col in shifts:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Sidebar - Time Window Selection
    window = st.sidebar.selectbox(
        "विश्लेषण के लिए दिन चुनें (Lookback Window)",
        options=[1, 3, 5, 7, 10, 15, 30],
        format_func=lambda x: f"पिछले {x} दिन" if x > 1 else "सिर्फ आज (1 दिन)"
    )

    # Filter data based on window
    recent_df = df.tail(window + 2).reset_index(drop=True) # Extra days for transition calculation
    
    # 4. Success Pattern Extraction
    # Har din kaun-kaun se pattern pass hue, uski list banate hain
    success_sets = []
    for i in range(len(df) - 1):
        today = set(df.loc[i, shifts].dropna().values)
        tomorrow = set(df.loc[i+1, shifts].dropna().values)
        
        if not today or not tomorrow: continue
        
        found_patterns = []
        for val in today:
            for p in master_patterns:
                if (val + p) % 100 in tomorrow:
                    found_patterns.append(p)
        success_sets.append(list(set(found_patterns)))

    # Only look at the selected window
    recent_success = success_sets[-window:] if window < len(success_sets) else success_sets

    # --- FREQUENCY ANALYSIS ---
    st.header(f"📈 पिछले {window} दिन की फ्रीक्वेंसी")
    all_flat_patterns = [p for s in recent_success for p in s]
    freq_counts = Counter(all_flat_patterns)
    
    freq_df = pd.DataFrame(freq_counts.items(), columns=['Pattern', 'Matches']).sort_values(by='Matches', ascending=False)
    st.bar_chart(freq_df.set_index('Pattern'))

    # --- SEQUENCE ANALYSIS (Transitions) ---
    st.header(f"🔗 पैटर्न सीक्वेंस विश्लेषण (1 से 5 पैटर्न)")
    
    tabs = st.tabs(["1 पैटर्न के बाद", "2 के बाद", "3 के बाद", "4 के बाद", "5 के बाद"])

    for size in range(1, 6):
        with tabs[size-1]:
            st.subheader(f"{size} पैटर्न के बाद कौन सा अगला आएगा?")
            
            combos = Counter()
            for i in range(len(recent_success) - 1):
                current_day_patterns = recent_success[i]
                next_day_patterns = recent_success[i+1]
                
                if len(current_day_patterns) >= size:
                    for combo in combinations(sorted(current_day_patterns), size):
                        for next_p in next_day_patterns:
                            combos[(combo, next_p)] += 1
            
            if combos:
                combo_results = []
                for (prev, nxt), count in combos.most_common(15):
                    combo_results.append({
                        "Current Group": str(prev),
                        "Next Pattern": nxt,
                        "Times Seen": count
                    })
                st.table(pd.DataFrame(combo_results))
            else:
                st.write("इस विंडो में कोई मजबूत सीक्वेंस नहीं मिला।")

    # --- PREDICTION FOR TOMORROW ---
    st.divider()
    st.header("🔮 कल के लिए प्रेडिक्शन (Based on Window)")
    
    last_day_patterns = success_sets[-1] if success_sets else []
    st.write(f"आज के सफल पैटर्न: `{last_day_patterns}`")
    
    # Suggest numbers based on the last observed sequence in this window
    suggested_next = []
    for (prev, nxt), count in combos.most_common(5):
        if set(prev).issubset(set(last_day_patterns)):
            suggested_next.append(nxt)
    
    if suggested_next:
        st.success(f"सीक्वेंस के आधार पर कल के टॉप पैटर्न: `{list(set(suggested_next))}`")
    else:
        st.info("आज के पैटर्न से कोई पुराना सीक्वेंस मैच नहीं हुआ। टॉप फ्रीक्वेंसी पैटर्न का उपयोग करें।")

else:
    st.warning("कृपया विश्लेषण शुरू करने के लिए डेटा फाइल अपलोड करें।")
  
