# 🤖 Albani – Asisten Suara Berbasis AI (Windows)

Albani adalah **personal voice assistant berbasis Python** yang mendukung:
- Speech-to-Text (Whisper)
- Text-to-Speech (ID-VITS)
- Kontrol aplikasi Windows (buka aplikasi lewat suara)
- Deteksi aplikasi yang sedang berjalan

Project ini masih dicoba pada sistem operasi **Windows**.

## Kontribusi

Kontribusi sangat terbuka 🙌  

Langkah singkat:
1. Fork repository ini
2. Buat branch baru dari `main`
   ```bash
   git checkout -b feature/nama-fitur
   ```

---

# Prasyarat Sistem

- **OS**: Windows 10 / 11 (64-bit)
- **Python**: **3.10.x (WAJIB)**
- **CUDA (opsional)**: NVIDIA CUDA (direkomendasikan ≥ 12.x)
- **Microphone aktif**

⚠️ **Python 3.11+ tidak direkomendasikan** karena banyak library AI (Torch, TTS) belum stabil.

---

## Install Python 3.10.9 (WAJIB)

Gunakan **Python versi berikut**:

**Python 3.10.9 (64-bit)**  
https://www.python.org/downloads/release/python-3109/

Saat install:
- ✅ Centang **Add Python to PATH**
- ✅ Pilih **Install for all users** (opsional tapi disarankan)

Cek versi:
```bash
python --version
```

## Clone Repository
```bash
git clone https://github.com/NamriHolmes-indo/Asisten-Albany.git
cd Asisten-Albany
```

## Buat Virtual Environment (WAJIB)
```bash
py -3.10 -m venv env310
```
Lalu masuk ke env dengan cara
```bash
venv310\Scripts\activate
```
dan lakukan instalasi library dengan cara
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
---

# Generate Daftar Aplikasi Windows
Langkah ini wajib dilakukan sekali sebelum menjalankan asisten suara.
```bash
python ambil_program.py
```
Perintah ini akan menghasilkan file:
```
installed_apps.json
```
File ini digunakan untuk fitur membuka aplikasi melalui suara.

**Menjalankan Asisten Suara**
Setelah semua langkah di atas selesai:
```bash
python speech_to_text.py
```
Jika berhasil, Albani akan menyatakan bahwa asisten sudah aktif dan siap digunakan.

**Contoh Perintah Suara**
Sapaan:
- halo albani
- hai albani

Membuka aplikasi:
- buka chrome
- albani buka dbeaver
- tolong bukakan edge

Cek aplikasi:
- apakah chrome sedang terbuka
- berapa aplikasi yang terbuka

Waktu:
- jam berapa sekarang

# Menghentikan Program
Untuk keluar dan menghentikan program, maka gunakan
```
CTRL + C
```
