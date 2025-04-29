import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa Ayarları
st.set_page_config(page_title="Kafe Dashboard", layout="wide")

# Stil ve Fontlar
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    html, body, .stApp {
        background-color: #392315;
        color: #f5d9c7;
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffe8d6;
    }
    .card {
        background: rgba(74, 44, 23, 0.7);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        backdrop-filter: blur(4px);
        transition: transform 0.3s, box-shadow 0.3s;
        margin-bottom: 20px;
    }
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
    }
    .card-title {
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 14px;
        color: #d4a373;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("☕ Menü")
    selected_date = st.date_input("Tarih Seçiniz", datetime.today())
    refresh = st.button("🔄 Verileri Yenile")

# Kahve çeşitleri ve fiyatlar
np.random.seed(42)
coffee_list = [
    "Espresso", "Americano", "Cappuccino", "Latte", "Mocha",
    "Flat White", "Macchiato", "Cortado", "Turkish Coffee", "Irish Coffee"
]
coffee_prices = {coffee: round(np.random.randint(100, 201, 1)[0] / 10) * 10 for coffee in coffee_list}

# Rastgele veri üret (2 ay - 60 gün) + hafta sonu etkisi + dinamik ortalama satışlar
@st.cache_data
def generate_random_data():
    dates = pd.date_range(end=datetime.today(), periods=60).to_pydatetime().tolist()
    data = []
    
    coffee_mean_sales = {
        coffee: np.random.randint(0, 31)
        for coffee in coffee_list
    }
    
    for date in dates:
        daily_sales = {
            'date': date.strftime('%Y-%m-%d'),
            'sales': []
        }
        for coffee in coffee_list:
            base_quantity = np.random.normal(coffee_mean_sales[coffee], 5)
            if date.weekday() in [5, 6]:
                base_quantity *= np.random.uniform(1.1, 1.3)
            quantity = max(0, int(base_quantity))
            daily_sales['sales'].append({
                'coffee': coffee,
                'quantity': quantity,
                'price': coffee_prices[coffee]
            })
        data.append(daily_sales)
    return data

if 'data' not in st.session_state or refresh:
    st.session_state.data = generate_random_data()

# Veri işleme
selected_date_str = selected_date.strftime('%Y-%m-%d')
yesterday_date = selected_date - timedelta(days=1)
yesterday_date_str = yesterday_date.strftime('%Y-%m-%d')

def get_day_data(date_str):
    for day in st.session_state.data:
        if day['date'] == date_str:
            return day
    return None

def calculate_total(day_data):
    if not day_data:
        return 0, {}
    total = 0
    product_counter = {}
    for item in day_data['sales']:
        total += item['quantity'] * item['price']
        product_counter[item['coffee']] = item['quantity']
    return total, product_counter

today_data = get_day_data(selected_date_str)
yesterday_data = get_day_data(yesterday_date_str)

today_total, today_products = calculate_total(today_data)
yesterday_total, _ = calculate_total(yesterday_data)

# Değişim Yüzdesi
if yesterday_total > 0:
    growth_percentage = ((today_total - yesterday_total) / yesterday_total) * 100
else:
    growth_percentage = 0

# En Çok Satan Ürün
if today_products:
    best_seller = max(today_products.items(), key=lambda x: x[1])
    best_product_name, best_product_quantity = best_seller
else:
    best_product_name, best_product_quantity = "-", 0

# Ana Başlık
st.title("☕ Kafe Satış Dashboard")
st.markdown("---")

# Premium Kartlar
col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(f'<div class="card"><div class="card-title">📈 Günlük Ciro</div><p style="text-align:center;">{today_total:.2f} ₺</p></div>', unsafe_allow_html=True)

with col2:
    change_icon = "📈" if growth_percentage >= 0 else "📉"
    st.markdown(f'<div class="card"><div class="card-title">{change_icon} Değişim %</div><p style="text-align:center;">{growth_percentage:.2f}%</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown(f'<div class="card"><div class="card-title">🛒 En Çok Satan</div><p style="text-align:center;">{best_product_name} ({best_product_quantity} adet)</p></div>', unsafe_allow_html=True)

with col4:
    total_items = sum(today_products.values()) if today_products else 0
    st.markdown(f'<div class="card"><div class="card-title">📦 Toplam Satış</div><p style="text-align:center;">{total_items} Adet</p></div>', unsafe_allow_html=True)

# Grafikler
if today_products:
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6 = st.columns(2, gap="large")

    with col5:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="text-align:center;">📊 Ürün Satış Dağılımı</h3>', unsafe_allow_html=True)
            df_bar = pd.DataFrame({
                'Kahve': list(today_products.keys()),
                'Adet': list(today_products.values())
            })
            fig_bar = px.bar(df_bar, x='Kahve', y='Adet',
                             color_discrete_sequence=['#d4a373'],
                             template="plotly_dark")
            fig_bar.update_layout(
                plot_bgcolor='rgba(74,44,23,0.7)',
                paper_bgcolor='rgba(74,44,23,0.7)',
                font_color='#f5d9c7',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="text-align:center;">📈 Son 30 Gün Ciro Trend</h3>', unsafe_allow_html=True)
            trends = []
            for day in st.session_state.data:
                total, _ = calculate_total(day)
                trends.append({'Tarih': day['date'], 'Ciro': total})
            df_line = pd.DataFrame(trends)
            fig_line = px.line(df_line, x='Tarih', y='Ciro',
                               markers=True,
                               color_discrete_sequence=['#7f5539'],
                               template="plotly_dark")
            fig_line.update_layout(
                plot_bgcolor='rgba(74,44,23,0.7)',
                paper_bgcolor='rgba(74,44,23,0.7)',
                font_color='#f5d9c7',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False),
                margin=dict(l=20, r=20, t=20, b=20),
            )
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Bugün için satış verisi bulunamadı.")

# Haftalık Satış Performansı
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="metric-card">', unsafe_allow_html=True)
st.markdown('<h3 style="text-align:center;">🔮 Haftalık Satış Performansı</h3>', unsafe_allow_html=True)

today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())
dates_of_week = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

real_sales = []
for date_str in dates_of_week:
    day_data = get_day_data(date_str)
    if day_data:
        day_total, _ = calculate_total(day_data)
    else:
        day_total = 0
    real_sales.append(day_total)

# 60 günlük veriden gün gün ortalamalar
weekday_totals = {i: [] for i in range(7)}
for day in st.session_state.data:
    date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
    weekday = date_obj.weekday()
    day_total, _ = calculate_total(day)
    weekday_totals[weekday].append(day_total)

weekday_averages = {i: np.mean(weekday_totals[i]) if weekday_totals[i] else 0 for i in range(7)}

# Şu haftanın beklenen satışları
expected_sales = []
for date_str in dates_of_week:
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    weekday = date_obj.weekday()
    expected_sales.append(weekday_averages[weekday])

# Grafik
df_week = pd.DataFrame({
    'Tarih': dates_of_week * 2,
    'Ciro': real_sales + expected_sales,
    'Tür': ['Gerçekleşen'] * 7 + ['Beklenen'] * 7
})

fig_week = px.line(df_week, x='Tarih', y='Ciro', color='Tür',
                   markers=True,
                   color_discrete_map={
                       'Gerçekleşen': '#d4a373',
                       'Beklenen': '#9c6644'
                   },
                   template="plotly_dark")
fig_week.update_layout(
    plot_bgcolor='rgba(74,44,23,0.7)',
    paper_bgcolor='rgba(74,44,23,0.7)',
    font_color='#f5d9c7',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False),
    margin=dict(l=20, r=20, t=20, b=20),
    legend_title_text='Veri Türü'
)

st.plotly_chart(fig_week, use_container_width=True)

# Bugün için performans
today_str = today.strftime('%Y-%m-%d')
if today_str in dates_of_week:
    index_today = dates_of_week.index(today_str)
    today_real = real_sales[index_today]
    today_expected = expected_sales[index_today]

    if today_expected > 0:
        difference_percentage = ((today_real - today_expected) / today_expected) * 100
    else:
        difference_percentage = 0

    if difference_percentage >= 0:
        st.success(f"🎯 Bugün beklenenden %{difference_percentage:.1f} fazla satış yapıldı!")
    else:
        st.error(f"⚠️ Bugün beklenenden %{abs(difference_percentage):.1f} daha az satış yapıldı.")
else:
    st.info("Bugün haftalık dönem dışında.")

st.markdown('</div>', unsafe_allow_html=True)

# Son 30 gün ve önceki 30 gün için verileri ayır
today = datetime.today()
last_30_days = today - timedelta(days=30)
prev_30_days = today - timedelta(days=60)

# Son 30 gün ve önceki 30 gün verilerini topla
recent_sales = {coffee: 0 for coffee in coffee_list}
previous_sales = {coffee: 0 for coffee in coffee_list}

for day in st.session_state.data:
    date_obj = datetime.strptime(day['date'], '%Y-%m-%d')
    for sale in day['sales']:
        if last_30_days <= date_obj <= today:
            recent_sales[sale['coffee']] += sale['quantity']
        elif prev_30_days <= date_obj < last_30_days:
            previous_sales[sale['coffee']] += sale['quantity']

# Yüzde değişimleri hesapla
declines = {}
for coffee in coffee_list:
    previous = previous_sales[coffee]
    recent = recent_sales[coffee]
    if previous > 0:
        change = ((recent - previous) / previous) * 100
        declines[coffee] = change

# En çok düşen ürünü bul
if declines:
    most_declined_product = min(declines.items(), key=lambda x: x[1])  # en negatif değişimi bul
    product_name, decline_percentage = most_declined_product

    if decline_percentage < 0:
        st.error(f"⚠️ Son 30 gün içerisinde **{product_name}** satışları %{abs(decline_percentage):.1f} azaldı!!!")
    else:
        st.success(f"🎉 Son 30 gün içerisinde **{product_name}** satışları %{decline_percentage:.1f} arttı!!!")
else:
    st.info("Yeterli veri bulunamadı.")
    
st.markdown('</div>', unsafe_allow_html=True)

