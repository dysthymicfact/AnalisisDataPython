import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from pandas.api.types import CategoricalDtype
import plotly.graph_objects as go
from babel.numbers import format_currency

sns.set(style='dark')

# Page configuration
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴🏻‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load cleaned datasets
load_day_data = pd.read_csv('./dashboard/day_data.csv', sep=","')
load_hour_data = pd.read_csv('./dashboard/hour_data.csv', sep=",")

# Helper function untuk menyiapkan dataframe 
def create_daily_bikesharing(df):
    df['dteday'] = pd.to_datetime(df['dteday'])  # Konversi ke datetime
    daily_bikesharing_df = df.groupby('dteday').agg({
        'cnt': 'sum',
        'registered': 'sum',
        'casual': 'sum',
    }).reset_index()  
    
    # Menambahkan kolom 'weekday'
    daily_bikesharing_df['weekday'] = daily_bikesharing_df['dteday'].dt.day_name()
    return daily_bikesharing_df

# Helper function untuk menghitung RFM Analysis
def create_rfm_df(load_hour_data, group_by_column='registered', add_scores=True):
   
    # Salin DataFrame asli
    df_copy = load_hour_data.copy()
    df_copy['dteday'] = pd.to_datetime(df_copy['dteday'])  # Konversi ke datetime
    
    # Hitung current_date (tanggal terkini berdasarkan dataset)
    current_date = df_copy['dteday'].max()
    
    # RFM Analysis: Hitung Recency, Frequency, dan Monetary
    rfm_df = (
        df_copy.groupby(group_by_column, as_index=False)
        .agg(
            Recency=('dteday', lambda x: (current_date - x.max()).days),
            Frequency=('instant', 'count'),  # Asumsi setiap baris = 1 transaksi
            Monetary=('cnt', 'sum')          # Total peminjaman
        )
    )
    
    # Tambahkan Skor R, F, M jika diperlukan
    if add_scores:
        rfm_df['R_Score'] = pd.qcut(rfm_df['Recency'], q=5, labels=[5, 4, 3, 2, 1])
        rfm_df['F_Score'] = pd.qcut(rfm_df['Frequency'], q=5, labels=[1, 2, 3, 4, 5])
        rfm_df['M_Score'] = pd.qcut(rfm_df['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
        # Gabungkan skor RFM
        rfm_df['RFM_Score'] = (
            rfm_df['R_Score'].astype(str) +
            rfm_df['F_Score'].astype(str) +
            rfm_df['M_Score'].astype(str)
        )
    
    return rfm_df

# Filter tanggal
load_day_data['dteday'] = pd.to_datetime(load_day_data['dteday'])  # Format ke datetime
load_day_data.sort_values(by='dteday', inplace=True)  # Perbaiki sort_values
load_day_data.reset_index(drop=True, inplace=True)  # Reset index

# Tentukan min dan max date dari kolom dteday
min_date = load_day_data['dteday'].min()
max_date = load_day_data['dteday'].max()

# Sidebar
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/dysthymicfact/AnalisisDataPython/refs/heads/main/dashboard/bikesaring-logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Date Range', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Konversi start_date dan end_date menjadi datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter data berdasarkan input rentang waktu
main_df = load_day_data[(load_day_data['dteday'] >= start_date) & 
                        (load_day_data['dteday'] <= end_date)]

st.caption('Copyright (c) dysthymicfact')

# Menyiapkan dataframe
daily_bikesharing_df = create_daily_bikesharing(main_df)
rfm_df = create_rfm_df(load_hour_data, group_by_column='registered', add_scores=True)

# Melengkapi dashboard dengan visualisasi data
st.header('Bikesharing Dashboard 🚴🏻‍♀️')

# Overview
st.subheader('Daily Rides Trend')
col = st.columns(3)
with col[0]:
    total_reg = daily_bikesharing_df['registered'].sum()
    st.metric('🪪 Registered Users', value=total_reg)

with col[1]:
    total_cnt = daily_bikesharing_df['cnt'].sum()
    st.metric('👥 Total Users', value=total_cnt)

with col[2]:
    total_cas = daily_bikesharing_df['casual'].sum()
    st.metric('🎟️ Casual Users', value=total_cas)


# Visualisasi 1: Tren penyewaan sepeda harian (registered vs casual)
# Menemukan tanggal dengan jumlah penyewaan total tertinggi
max_total = daily_bikesharing_df['cnt'].max()
max_date = daily_bikesharing_df.loc[daily_bikesharing_df['cnt'] == max_total, 'dteday'].values[0]

# Format tanggal menjadi 'YYYY-MM-DD'
formatted_date = pd.to_datetime(max_date).strftime('%Y-%m-%d')

# Membuat grafik
grafik = go.Figure()

# Menambahkan garis untuk total penyewaan
grafik.add_trace(go.Scatter(
    x=daily_bikesharing_df['dteday'],
    y=daily_bikesharing_df['cnt'],
    mode='lines',
    name='Total Bike Sharing',
    line=dict(color='blue', width=2)
))

# Menambahkan garis untuk pengguna kasual
grafik.add_trace(go.Scatter(
    x=daily_bikesharing_df['dteday'],
    y=daily_bikesharing_df['casual'],
    mode='lines',
    name='Casual Users',
    line=dict(color='teal', width=2)
))

# Menambahkan garis untuk pengguna terdaftar
grafik.add_trace(go.Scatter(
    x=daily_bikesharing_df['dteday'],
    y=daily_bikesharing_df['registered'],
    mode='lines',
    name='Registered Users',
    line=dict(color='orange', width=2)
))

# Menyoroti titik dengan jumlah penyewaan tertinggi
grafik.add_trace(go.Scatter(
    x=[max_date],
    y=[max_total],
    mode='markers',
    marker=dict(color='red', size=12, symbol='star'),
    name=f'Maksimum: {max_total}'
))

# Menyesuaikan tata letak
grafik.update_layout(
    title='Tren Penyewaan Sepeda Harian (Registered vs Casual)',
    xaxis_title='Tanggal',
    yaxis_title='Jumlah Penyewaan',
    template='plotly_white',
    xaxis=dict(tickangle=45)
)

# Menampilkan grafik di Streamlit
st.plotly_chart(grafik)

# Output data tertinggi
st.write(f"📅 Tanggal dengan penyewaan sepeda terbanyak: **{formatted_date}** dengan total **{max_total}** penyewaan.")


# Visualisasi 2: Tren penyewaan sepeda per bulan (registered vs casual)
# Buat kolom baru dengan format "YYYY-MM" untuk pengelompokan
daily_bikesharing_df['year_month'] = daily_bikesharing_df['dteday'].dt.to_period('M')

# Grouping berdasarkan year_month untuk registered dan casual users
monthly_trend = daily_bikesharing_df.groupby('year_month', as_index=False)[['registered', 'casual']].sum()

# Konversi year_month ke datetime agar bisa diurutkan
monthly_trend['year_month'] = pd.to_datetime(monthly_trend['year_month'].astype(str))

# Mengubah format data menjadi long format agar bisa divisualisasikan dalam satu plot
monthly_trend_melted = monthly_trend.melt(id_vars=['year_month'],
                                          value_vars=['registered', 'casual'],
                                          var_name='user_type', value_name='total_count')

# Mengganti nama user_type agar lebih mudah dibaca di legenda
user_type_mapping = {
    'registered': 'Registered Users',
    'casual': 'Casual Users'
}
monthly_trend_melted['user_type'] = monthly_trend_melted['user_type'].map(user_type_mapping)

fig = px.line(monthly_trend_melted, x='year_month', y='total_count', color='user_type',
              title='Tren Peminjaman Sepeda per Bulan (Registered vs Casual)',
              labels={'year_month': 'Bulan', 'total_count': 'Total Peminjaman', 'user_type': 'Tipe Pengguna'},
              markers=True)

# Menyesuaikan tampilan sumbu x agar tidak bertabrakan
fig.update_layout(xaxis=dict(tickangle=-45))

# Menampilkan plot
st.plotly_chart(fig)

# Visualisasi 3: Rata-rata Penyewaan Sepeda per Hari Berdasarkan Cuaca 
# Pastikan kolom 'dteday' dan 'weekday' ada di load_day_data
load_day_data['dteday'] = pd.to_datetime(load_day_data['dteday'])  # Konversi ke tipe datetime
load_day_data['weekday'] = load_day_data['dteday'].dt.day_name()  # Tambahkan kolom nama hari

# Periksa keberadaan kolom 'weathersit' sebelum melanjutkan analisis
if 'weathersit' in load_day_data.columns:
    # Buat pivot table untuk rata-rata penyewaan berdasarkan hari dan cuaca
    pivot_table = load_day_data.pivot_table(
        index='weekday',         # Kelompokkan berdasarkan nama hari
        columns='weathersit',    # Kondisi cuaca sebagai kategori
        values='cnt',            # Total penyewaan
        aggfunc='mean'           # Hitung rata-rata
    ).reset_index()

    # Ubah pivot table ke format long agar mudah divisualisasikan
    pivot_long = pivot_table.melt(
        id_vars='weekday',       # Kolom yang dipertahankan
        var_name='weathersit',   # Nama kondisi cuaca
        value_name='average_count'  # Nama rata-rata penyewaan
    )

    # Pastikan urutan hari dari Minggu hingga Sabtu
    ordered_days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    pivot_long['weekday'] = pd.Categorical(
        pivot_long['weekday'],        # Kolom nama hari
        categories=ordered_days,      # Urutan yang diinginkan
        ordered=True                  # Tetapkan sebagai urutan
    )

# Pastikan data disortir sesuai urutan hari
    pivot_long = pivot_long.sort_values(by='weekday')

    # Visualisasikan menggunakan Plotly
    fig = px.line(
        pivot_long,
        x='weekday',                  # Sumbu X sebagai nama hari
        y='average_count',            # Sumbu Y sebagai rata-rata penyewaan
        color='weathersit',           # Warna berdasarkan cuaca
        title='Rata-rata Penyewaan Sepeda per Hari Berdasarkan Cuaca',
        labels={'weekday': 'Hari', 'average_count': 'Rata-rata Penyewaan', 'weathersit': 'Kondisi Cuaca'},
        markers=True                  # Tambahkan marker untuk garis
    )

    # Menampilkan plot di Streamlit
    st.plotly_chart(fig)

else:
    st.error("Kolom 'weathersit' tidak ditemukan pada dataset day_data.csv. Silakan periksa kembali dataset.")

# Visualisasi 4: Rata-rata Jumlah Penyewaan Sepeda per Jam Berdasarkan Kondisi Cuaca
# Menghitung rata-rata penyewaan sepeda berdasarkan jam (0-23) dan kondisi cuaca
weather_by_hour = load_hour_data.pivot_table(values="cnt", index="hr", columns="weathersit", aggfunc="mean").reset_index()

# Mapping nama kondisi cuaca jika belum deskriptif
weather_mapping = {
    1: 'Clear',
    2: 'Mist + Cloudy',
    3: 'Light Snow',
    4: 'Heavy Rain'
}

# Ubah nama kolom cuaca (opsional, tergantung dataset)
weather_by_hour.rename(columns=weather_mapping, inplace=True)

# Transformasi ke long format untuk visualisasi Plotly
weather_long = weather_by_hour.melt(
    id_vars='hr',
    var_name='weathersit',
    value_name='average_count'
)

# Membuat grafik line dengan Plotly
fig = px.line(
    weather_long,
    x='hr',
    y='average_count',
    color='weathersit',
    title="Rata-rata Jumlah Penyewaan Sepeda per Jam Berdasarkan Kondisi Cuaca",
    labels={
        'hr': 'Jam',
        'average_count': 'Rata-rata Penyewaan',
        'weathersit': 'Kondisi Cuaca'
    },
    markers=True
)

# Menyesuaikan tampilan sumbu dan layout
fig.update_layout(
    xaxis=dict(tickmode='linear', tick0=0, dtick=2),  # Interval tiap 2 jam
    template='plotly_white',  # Tampilan minimalis
    legend_title=dict(text='Kondisi Cuaca'),
    xaxis_title='Jam',
    yaxis_title='Rata-rata Jumlah Penyewaan Sepeda'
)

# Tampilkan plot di Streamlit
st.plotly_chart(fig)

# Visualisasi 5, 6, dan 7 = Barplot 1, 2, dan 3
# Pastikan kolom 'workingday' memiliki nilai valid (hanya dilakukan sekali)
if load_day_data['workingday'].dtype == 'object':
    workingday_mapping_reverse = {'Weekend': 0, 'Weekday': 1}
    load_day_data['workingday'] = load_day_data['workingday'].map(workingday_mapping_reverse)

# Konversi kolom 'workingday' ke integer jika diperlukan
load_day_data['workingday'] = load_day_data['workingday'].astype(int)

# Atur urutan hari agar visualisasi terurut
day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
load_day_data['weekday'] = load_day_data['weekday'].astype(CategoricalDtype(categories=day_order, ordered=True))

# Peta warna konsisten untuk kategori Weekday dan Weekend
workingday_color_map = {'Weekend': '#fc8d62', 'Weekday': '#66c2a5'}

### Barplot 1: Rata-rata total penyewaan sepeda Weekday vs Weekend ###
avg_rent_by_workingday = load_day_data.groupby('workingday')['cnt'].mean().reset_index()
workingday_mapping = {0: 'Weekend', 1: 'Weekday'}
avg_rent_by_workingday['workingday'] = avg_rent_by_workingday['workingday'].map(workingday_mapping)

fig1 = px.bar(
    avg_rent_by_workingday,
    x='workingday',
    y='cnt',
    color='workingday',
    text='cnt',
    title="Perbandingan Rata-rata Total Penyewaan Sepeda Weekday vs Weekend",
    labels={'workingday': 'Jenis Hari', 'cnt': 'Rata-rata Penyewaan Sepeda (cnt)'},
    color_discrete_map=workingday_color_map
)

fig1.update_traces(
    texttemplate='%{text:.1f}',
    textposition='outside'
)
fig1.update_layout(
    xaxis_title='Jenis Hari',
    yaxis_title='Rata-rata Penyewa Sepeda',
    legend_title_text='Jenis Hari',
    template='plotly_white',
    title_x=0.0
)

### Barplot 2: Rata-rata penyewaan sepeda Weekday vs Weekend dalam 1 Minggu ###
valid_df = load_day_data[
    ((load_day_data['weekday'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])) & (load_day_data['workingday'] == 1)) |
    ((load_day_data['weekday'].isin(['Saturday', 'Sunday'])) & (load_day_data['workingday'] == 0))
]

avg_by_day_type = valid_df.groupby(['weekday', 'workingday'], observed=True)['cnt'].mean().reset_index()
avg_by_day_type['workingday'] = avg_by_day_type['workingday'].map(workingday_mapping)

fig2 = px.bar(
    avg_by_day_type,
    x='weekday',
    y='cnt',
    color='workingday',
    text='cnt',
    title="Perbandingan Rata-rata Penyewaan Sepeda Weekday vs Weekend dalam 1 Minggu",
    labels={'weekday': 'Hari', 'cnt': 'Rata-rata Penyewaan Sepeda', 'workingday': 'Tipe Hari'},
    color_discrete_map=workingday_color_map
)

fig2.update_traces(
    texttemplate='%{text:.0f}',
    textposition='outside'
)
fig2.update_layout(
    xaxis_title='Hari',
    yaxis_title='Rata-rata Penyewa Sepeda',
    legend_title_text='Tipe Hari',
    xaxis=dict(categoryorder='array', categoryarray=day_order),
    template='plotly_white',
    title_x=0.0
)

### Barplot 3: Rata-rata penyewaan sepeda Weekday vs Weekend per Musim ###

# Salin data agar tidak mengubah dataframe asli
df = load_day_data.copy()

# Konversi dan validasi kolom 'season' jika bertipe object
if df['season'].dtype == 'object':
    season_order = ['Springer', 'Summer', 'Fall', 'Winter']
    df['season'] = pd.Categorical(df['season'], categories=season_order, ordered=True)

# Hitung rata-rata jumlah penyewa berdasarkan kombinasi season dan workingday
grouped = df.groupby(['season', 'workingday'], observed=True)['cnt'].mean().reset_index()

# Mapping kategori tipe hari untuk visualisasi
workingday_mapping = {0: 'Weekend', 1: 'Weekday'}
grouped['workingday'] = grouped['workingday'].map(workingday_mapping)

# Peta warna konsisten untuk kedua kategori (Weekday dan Weekend)
workingday_color_map = {'Weekend': '#fc8d62', 'Weekday': '#66c2a5'}

#grouped = load_day_data.groupby(['season', 'workingday'], observed=True)['cnt'].mean().reset_index()
#grouped['season'] = grouped['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
#grouped['workingday'] = grouped['workingday'].map(workingday_mapping)

fig3 = px.bar(
    grouped,
    x='season',
    y='cnt',
    color='workingday',
    text='cnt',
    title="Perbandingan Rata-rata Penyewaan Sepeda Weekday vs Weekend per Musim",
    labels={'season': 'Musim', 'cnt': 'Rata-rata Penyewaan Sepeda', 'workingday': 'Tipe Hari'},
    color_discrete_map=workingday_color_map
)

fig3.update_traces(
    texttemplate='%{text:.0f}',
    textposition='outside'
)
fig3.update_layout(
    xaxis_title='Musim',
    yaxis_title='Rata-rata Penyewa Sepeda',
    legend_title_text='Tipe Hari',
    template='plotly_white',
    title_x=0.0
)

# Tampilkan ketiga grafik di Streamlit
st.plotly_chart(fig1)
st.plotly_chart(fig2)
st.plotly_chart(fig3)


# Konversi current_date menjadi datetime
current_date = pd.to_datetime(load_hour_data['dteday'].max())  # Mendapatkan tanggal terkini dari kolom 'dteday'

# Pastikan kolom 'dteday' sudah dalam format datetime
load_hour_data['dteday'] = pd.to_datetime(load_hour_data['dteday'])

# RFM Analysis per Jam
rfm_by_hour = (load_hour_data.groupby('hr', as_index=False).agg(
    Recency=('dteday', lambda x: (current_date - x.max()).days),  # Hitung selisih hari
    Frequency=('instant', 'count'),  # Aktivitas per jam
    Monetary=('cnt', 'sum')          # Total peminjaman per jam
).sort_values('Monetary', ascending=False))


# Visualisasi 8: Distribusi Monetary per Jam
st.subheader('Analisis RFM')
fig_hour = px.bar(rfm_by_hour, x='hr', y='Monetary', color='Monetary',
                  title='Distribusi Monetary Berdasarkan Jam',
                  labels={'hr': 'Jam', 'Monetary': 'Total Peminjaman'})
fig_hour.update_layout(xaxis_title='Jam', yaxis_title='Total Peminjaman')
st.plotly_chart(fig_hour)

# Visualisasi 9: Distribusi Skor RFM untuk Registered User
fig_rfm_score = px.histogram(rfm_df, x='RFM_Score', color='RFM_Score',
                             title='Distribusi Skor RFM untuk Registered User',
                             labels={'RFM_Score': 'Skor RFM', 'count': 'Jumlah Pengguna'})
fig_rfm_score.update_layout(xaxis_title='Skor RFM', yaxis_title='Jumlah Pengguna', showlegend=False)
st.plotly_chart(fig_rfm_score)


st.caption('Copyright (c) dysthymicfact')
