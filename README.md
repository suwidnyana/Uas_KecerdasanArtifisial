# Fuzzy Persediaan - Sistem Logika Fuzzy untuk Produksi

Proyek ini adalah implementasi sistem logika fuzzy menggunakan metode Tsukamoto untuk menentukan jumlah produksi berdasarkan permintaan dan persediaan. Dibangun dengan Python dan Flask, serta visualisasi menggunakan Matplotlib.

---

## 🛠️ Persiapan Sebelum Menjalankan

Sebelum menjalankan proyek ini, pastikan kamu telah menginstal:

- **Python 3.x**  
  Unduh dari [python.org](https://www.python.org/downloads/) dan pastikan sudah ditambahkan ke PATH.
- **pip** (Python package installer)  
  Biasanya sudah terinstal bersama Python. Untuk memastikan, jalankan:



---

## 📦 Instalasi dan Setup

1. Clone repository:
```
git clone https://github.com/suwidnyana/Uas_-KecerdasanArtifisial
```

2. Buat dan aktifkan virtual environment:
- **Windows:**
  ```
  python -m venv env_fuzzy_flask
  .\env_fuzzy_flask\Scripts\activate
  ```
- **macOS/Linux:**
  ```
  python3 -m venv env_fuzzy_flask
  source env_fuzzy_flask/bin/activate
  ```

3. Install dependencies:
 ```
pip install -r requirements.txt
 ```
  ```
pip install flask numpy matplotlib scikit-fuzzy

 ```
---

## 🚀 Menjalankan Aplikasi

1. Set environment variable untuk Flask app:
- **Windows:**
  ```
  set FLASK_APP=app.py
  ```
- **macOS/Linux:**
  ```
  export FLASK_APP=app.py
  ```

2. Jalankan server Flask:
```
flask run
```


---

## 📂 Struktur Folder


```text
Uas-KecerdasanArtifisial/
├── app.py
├── static/
│   └── img/
│       └── fuzzy_graph.png
├── templates/
│   ├── index.html
│   ├── base.html
│   ├── grafik.html
│   └── about.html
└── README.md
```

---

## ⚙️ Catatan Penting

- Proyek ini menggunakan python versi 3.10
- 
- 

---

Jika ada bagian yang ingin ditambahkan atau disesuaikan, silakan beri tahu.
