import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

sns.set(style="dark")

st.set_page_config(page_title="Bike Sharing Dashboard", layout="centered")

# fungsi load data (menggunakan st.cache_data)
@st.cache_data
def load_day_data():
    url = "https://raw.githubusercontent.com/dysthymicfact/AnalisisDataPython/refs/heads/main/data/day.csv"
    df = pd.read_csv(url, parse_dates=["dteday"])
    return df

@st.cache_data
def load_hour_data():
    url = "https://raw.githubusercontent.com/dysthymicfact/AnalisisDataPython/refs/heads/main/data/hour.csv"
    df = pd.read_csv(url, parse_dates=["dteday"])
    return df

# mengakses data
day_df = load_day_data()
hour_df = load_hour_data()

# navigasi sidebar pilihan rentang waktu
st.sidebar.header("Rentang Waktu")
min_date = day_df["dteday"].min().date()
max_date = day_df["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Pilih rentang tanggal:",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) != 2:
    st.error("Silakan pilih rentang tanggal yang valid!")
else:
    start_date, end_date = date_range
    # Filter data berdasarkan rentang waktu yang dipilih
    filtered_day_df = day_df[(day_df["dteday"] >= pd.to_datetime(start_date)) &
                             (day_df["dteday"] <= pd.to_datetime(end_date))]
    filtered_hour_df = hour_df[(hour_df["dteday"] >= pd.to_datetime(start_date)) &
                               (hour_df["dteday"] <= pd.to_datetime(end_date))]
    
    st.title("Bike Sharing Dashboard :bike:")
    st.write(f"Menampilkan data dari {start_date} hingga {end_date}")
    
    # 1. Overview 
    st.header("Overview")
    total_rentals = filtered_day_df["cnt"].sum()
    avg_daily = filtered_day_df["cnt"].mean()
    st.metric("Total Penyewaan Sepeda", total_rentals)
    st.metric("Rata-Rata Penyewaan Sepeda per Hari", f"{avg_daily:.0f}")
    
    st.subheader("Tren Penyewaan Sepeda Harian")
    fig_trend, ax_trend = plt.subplots(figsize=(10, 5))
    ax_trend.plot(filtered_day_df['dteday'], filtered_day_df['cnt'], 
                  marker='o', linestyle='-', color='blue')
    ax_trend.set_xlabel("Tanggal")
    ax_trend.set_ylabel("Jumlah Penyewaan")
    ax_trend.set_title("Tren Penyewaan Harian")
    ax_trend.grid(True)
    fig_trend.autofmt_xdate()
    st.pyplot(fig_trend)
    
    # 2. Analisis Cuaca
    st.header("Analisis Cuaca")
    st.write("Rata-rata penyewaan sepeda per kondisi cuaca (dari data day).")
    avg_weather = filtered_day_df.groupby("weathersit")["cnt"].mean().reset_index()
    fig_weather, ax_weather = plt.subplots(figsize=(8, 5))
    ax_weather.plot(avg_weather["weathersit"], avg_weather["cnt"], marker='o', linestyle='-', color='green')
    ax_weather.set_title("Penyewaan Sepeda per Kondisi Cuaca")
    ax_weather.set_xlabel("Kondisi Cuaca")
    ax_weather.set_ylabel("Rata-Rata Penyewaan")
    for i, row in avg_weather.iterrows():
        ax_weather.annotate(f"{int(row['cnt'])}", 
                        (row["weathersit"], row["cnt"]),
                        textcoords="offset points", xytext=(0, 5), ha='center')
    st.pyplot(fig_weather)

    
    # 3. Analisis Penyewaan Sepeda Berdasarkan Waktu (Jam) 
    st.header("Analisis Penyewaan Sepeda per Jam")
    st.write("Tren penyewaan sepeda per jam berdasarkan kondisi cuaca (dari data hour).")
    pivot_table = filtered_hour_df.pivot_table(values="cnt", index="hr", 
                                               columns="weathersit", aggfunc="mean")
    st.write("Pivot Table - Rata-rata Penyewaan Sepeda per Jam:")
    st.write(pivot_table.head(100))
    
    fig_hour, ax_hour = plt.subplots(figsize=(10, 5))
    for cond in pivot_table.columns:
        ax_hour.plot(pivot_table.index, pivot_table[cond], 
                     marker='o', linestyle='-', label=f"Kondisi {cond}")
    ax_hour.set_title("Tren Penyewaan Sepeda per Jam")
    ax_hour.set_xlabel("Jam (0 - 23)")
    ax_hour.set_ylabel("Rata-Rata Penyewaan")
    ax_hour.legend(title="Kondisi Cuaca")
    ax_hour.grid(True)
    st.pyplot(fig_hour)
    
    # 4. Hari Kerja vs Weekend
    st.header("Perbandingan Hari Kerja vs Weekend")
    st.write("Analisis perbandingan penyewaan sepeda antara hari kerja dan weekend (dari data day).")
    avg_work = filtered_day_df.groupby("workingday")["cnt"].mean().reset_index()
    labels = {0: "Weekend", 1: "Hari Kerja"}
    
    fig_work, ax_work = plt.subplots(figsize=(8, 5))
    ax_work.bar([labels[x] for x in avg_work["workingday"]], avg_work["cnt"],
                color=["salmon", "skyblue"])
    ax_work.set_title("Rata-Rata Penyewaan Sepeda: Hari Kerja vs Weekend")
    ax_work.set_xlabel("Tipe Hari")
    ax_work.set_ylabel("Rata-Rata Penyewaan")
    for i, row in avg_work.iterrows():
        ax_work.annotate(f"{int(row['cnt'])}", (i, row['cnt']),
                         textcoords="offset points", xytext=(0, 5), ha="center")
    st.pyplot(fig_work)
    
    st.subheader("Distribusi Penyewaan Sepeda: Hari Kerja vs Weekend")
    filtered_day_df["Tipe Hari"] = filtered_day_df["workingday"].apply(lambda x: "Hari Kerja" if x==1 else "Weekend")
    fig_box, ax_box = plt.subplots(figsize=(8, 5))
    sns.boxplot(x="Tipe Hari", y="cnt", data=filtered_day_df, palette="Pastel1", ax=ax_box)
    ax_box.set_title("Distribusi Penyewaan Sepeda: Hari Kerja vs Weekend")
    st.pyplot(fig_box)
