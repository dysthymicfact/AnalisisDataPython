import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi load data dengan caching menggunakan st.cache_data
@st.cache_data
def load_day_data():
    url_day = "https://raw.githubusercontent.com/dysthymicfact/AnalisisDataPython/refs/heads/main/dashboard/day_data.csv"
    return pd.read_csv(url_day)

@st.cache_data
def load_hour_data():
    url_hour = "https://raw.githubusercontent.com/dysthymicfact/AnalisisDataPython/refs/heads/main/dashboard/hour_data.csv"
    return pd.read_csv(url_hour)

# Memuat data
day_df = load_day_data()
hour_df = load_hour_data()

# Sidebar untuk navigasi
st.sidebar.title("Navigasi Bike Sharing Dashboard")
page = st.sidebar.radio("Pilih halaman:",
                        ("Halaman Utama", 
                         "Analisis Cuaca", 
                         "Analisis Per Jam", 
                         "Hari Kerja vs Weekend"))

# 1. Halaman Utama
if page == "Halaman Utama":
    st.header("Halaman Utama Bike Sharing Dashboard :bike:")
    
    # Menampilkan metrik utama
    total_rentals = day_df['cnt'].sum()
    avg_rentals_day = day_df['cnt'].mean()
    st.metric("Total Penyewaan Sepeda", total_rentals)
    st.metric("Rata-Rata Penyewaan Sepeda per Hari", f"{avg_rentals_day:.0f}")

# 2. Analisis Cuaca
elif page == "Analisis Cuaca":
    st.header("Analisis Berdasarkan Kondisi Cuaca (Data Harian)")
    st.write("Visualisasi ini menunjukkan bagaimana kondisi cuaca memengaruhi penyewaan sepeda.")
    
    # Menghitung rata-rata penyewaan per kondisi cuaca dari data harian
    avg_weather = day_df.groupby('weathersit')['cnt'].mean().reset_index()
    
    fig_weather, ax_weather = plt.subplots(figsize=(8, 6))
    ax_weather.bar(avg_weather['weathersit'], avg_weather['cnt'], color="skyblue")
    ax_weather.set_title("Rata-rata Penyewaan Sepeda per Kondisi Cuaca")
    ax_weather.set_xlabel("Kondisi Cuaca")
    ax_weather.set_ylabel("Rata-Rata Penyewaan")
    # Tambahkan anotasi nilai di atas bar sebagai bilangan bulat
    for i, row in avg_weather.iterrows():
        ax_weather.annotate(f"{int(row['cnt'])}", 
                            (row['weathersit'], row['cnt']),
                            textcoords="offset points", xytext=(0, 5), ha="center")
    st.pyplot(fig_weather)

# 3. Analisis per Jam
elif page == "Analisis per Jam":
    st.header("Analisis Penyewaan Sepeda Per Jam (Data Per Jam)")
    st.write("Grafik di bawah memperlihatkan tren penyewaan sepeda tiap jam untuk setiap kondisi cuaca.")

    # Tampilkan beberapa baris pertama data untuk memastikan data dimuat dengan benar
    st.write("DataFrame Hourly Data - Preview:")
    st.write(hour_df.head(50))

    # Periksa kolom yang diperlukan
    st.write("Kolom DataFrame:")
    st.write(hour_df.columns)

    # Buat pivot table dari data per jam: baris = jam, kolom = kondisi cuaca
    weather_by_hour = hour_df.pivot_table(values="cnt", index="hr", columns="weathersit", aggfunc="mean")

    # Tampilkan pivot table di bawah grafik
    st.write("Pivot Table - Rata-rata Penyewaan Sepeda per Jam Berdasarkan Kondisi Cuaca:")
    st.write(weather_by_hour.head(24))

    # Membuat grafik menggunakan Streamlit
    fig, ax = plt.subplots(figsize=(10, 6))
    for column in weather_by_hour.columns:
        ax.plot(weather_by_hour.index, weather_by_hour[column], marker="o", linestyle="-", label=f'Kondisi {column}')

    ax.set_title("Rata-rata jumlah penyewa sepeda per jam berdasarkan kondisi cuaca (Data Per Jam)")
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata Jumlah Penyewa Sepeda (cnt)")
    ax.legend(title="Kondisi Cuaca")
    ax.grid(True)

    st.pyplot(fig)

# 4. Hari Kerja vs Weekend
elif page == "Hari Kerja vs Weekend":
    st.header("Perbandingan Penyewaan Sepeda: Hari Kerja vs Weekend")
    st.write("Berikut perbandingan penyewaan sepeda antara hari kerja dan weekend menggunakan data harian.")
    
    # Bar chart perbedaan rata-rata penyewaan sepeda
    avg_work = day_df.groupby("workingday")["cnt"].mean().reset_index()
    labels = {0: "Weekend", 1: "Hari Kerja"}
    
    fig_work, ax_work = plt.subplots(figsize=(8, 6))
    ax_work.bar([labels[x] for x in avg_work['workingday']], avg_work['cnt'], color=["salmon", "skyblue"])
    ax_work.set_title("Rata-Rata Penyewaan Sepeda: Hari Kerja vs Weekend")
    ax_work.set_xlabel("Jenis Hari")
    ax_work.set_ylabel("Rata-Rata Penyewaan")
    for i, row in avg_work.iterrows():
        ax_work.annotate(f"{int(row['cnt'])}", (i, row['cnt']),
                         textcoords="offset points", xytext=(0, 5), ha="center")
    st.pyplot(fig_work)
    
    # Box plot untuk distribusi penyewaan sepeda
    st.subheader("Distribusi Penyewaan Sepeda")
    day_df['TipeHari'] = day_df['workingday'].apply(lambda x: "Hari Kerja" if x == 1 else "Weekend")
    fig_box, ax_box = plt.subplots(figsize=(8, 6))
    sns.boxplot(x="TipeHari", y="cnt", data=day_df, ax=ax_box, palette="Pastel1")
    ax_box.set_title("Distribusi Penyewaan Sepeda: Hari Kerja vs Weekend")
    st.pyplot(fig_box)
