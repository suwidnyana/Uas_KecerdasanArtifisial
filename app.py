from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzzy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Folder grafik
if not os.path.exists('static/img'):
    os.makedirs('static/img')

# =============================
# 1. Universe Variables
# =============================
rating_x  = np.arange(0, 5.01, 0.01)
crash_x   = np.arange(0, 51, 5)
keluhan_x = np.arange(0, 301, 1)
quality_x = np.arange(0, 101, 1)

# =============================
# 2. Membership Function (NEW)
# =============================

# --- Rating ---
rating_buruk  = fuzzy.trapmf(rating_x, [0, 0, 1, 2])
rating_normal = fuzzy.trapmf(rating_x, [1, 2, 3, 4])
rating_baik   = fuzzy.trapmf(rating_x, [3, 4, 5, 5])

# --- Crash ---
crash_rendah = fuzzy.trapmf(crash_x, [0, 0, 10, 20])
crash_sedang = fuzzy.trapmf(crash_x, [10, 20, 30, 40])
crash_tinggi = fuzzy.trapmf(crash_x, [30, 40, 50, 50])


# --- Keluhan (Smooth & Clean Version) ---

# Sedikit: tinggi 0–60, turun halus hingga 120
keluhan_sedikit = fuzzy.trapmf(keluhan_x, [0, 0, 60, 120])

# Sedang: overlap 60–120, puncak 150, turun halus ke 240
keluhan_sedang = fuzzy.trapmf(keluhan_x, [60, 120, 150, 240])

# Banyak: naik halus dari 200, plateau 260–300
keluhan_banyak = fuzzy.trapmf(keluhan_x, [200, 260, 300, 300])

# # --- Keluhan ---
# keluhan_sedikit = fuzzy.trapmf(keluhan_x, [0, 0, 40, 80])
# keluhan_sedang = fuzzy.trapmf(keluhan_x, [60, 120, 160, 220])
# keluhan_banyak = fuzzy.trapmf(keluhan_x, [200, 240, 300, 300])

# --- Quality ---
quality_buruk = fuzzy.trapmf(quality_x, [0, 0, 20, 40])
quality_cukup = fuzzy.trapmf(quality_x, [30, 45, 60, 75])
quality_baik = fuzzy.trapmf(quality_x, [60, 75, 100, 100])


# =============================
# 3. Generate GRAPH (New Style)
# =============================
def generate_graph():
    plt.figure(figsize=(10, 16))

    # Rating
    plt.subplot(4, 1, 1)
    plt.plot(rating_x, rating_buruk, label="Buruk")
    plt.plot(rating_x, rating_normal, label="Normal")
    plt.plot(rating_x, rating_baik, label="Baik")
    plt.title("Rating Pengguna")
    plt.legend(); plt.grid(True)

    # Crash
    plt.subplot(4, 1, 2)
    plt.plot(crash_x, crash_rendah, label="Rendah")
    plt.plot(crash_x, crash_sedang, label="Sedang")
    plt.plot(crash_x, crash_tinggi, label="Tinggi")
    plt.title("Jumlah Crash")
    plt.legend(); plt.grid(True)

    # Keluhan
    plt.subplot(4, 1, 3)
    plt.plot(keluhan_x, keluhan_sedikit, label="Sedikit")
    plt.plot(keluhan_x, keluhan_sedang, label="Sedang")
    plt.plot(keluhan_x, keluhan_banyak, label="Banyak")
    plt.title("Jumlah Keluhan")
    plt.legend(); plt.grid(True)

    # Quality
    plt.subplot(4, 1, 4)
    plt.plot(quality_x, quality_buruk, label="Buruk")
    plt.plot(quality_x, quality_cukup, label="Cukup")
    plt.plot(quality_x, quality_baik, label="Baik")
    plt.title("Output Kualitas Layanan")
    plt.legend(); plt.grid(True)

    plt.tight_layout()
    plt.savefig("static/img/fuzzy_graph_new.png")
    plt.close()

generate_graph()

# =============================
# 4. Fuzzy Inference RULE BASE
# =============================
def fuzzy_inference(rating, crash, keluhan):

    # ==========================
    # 1. DEGREE OF MEMBERSHIP
    # ==========================

    # Rating
    Rb = fuzzy.interp_membership(rating_x, rating_buruk, rating)
    Rn = fuzzy.interp_membership(rating_x, rating_normal, rating)
    Rk = fuzzy.interp_membership(rating_x, rating_baik, rating)

    # Crash
    C_low  = fuzzy.interp_membership(crash_x, crash_rendah, crash)
    C_mid  = fuzzy.interp_membership(crash_x, crash_sedang, crash)
    C_high = fuzzy.interp_membership(crash_x, crash_tinggi, crash)

    # Keluhan
    K_low  = fuzzy.interp_membership(keluhan_x, keluhan_sedikit, keluhan)
    K_mid  = fuzzy.interp_membership(keluhan_x, keluhan_sedang, keluhan)
    K_high = fuzzy.interp_membership(keluhan_x, keluhan_banyak, keluhan)

    # ==========================
    # 2. RULES
    # ==========================

    # --- BURUK ---
    rules_buruk = [
        min(Rb, max(C_high, K_high)),   # rating buruk + crash/keluhan tinggi
        min(Rb, K_mid),                 # rating buruk + keluhan sedang
        min(Rn, C_high),                # rating normal + crash tinggi
        # fallback: jika crash atau keluhan tinggi tanpa peduli rating -> buruk
        max(C_high, K_high)
    ]

    # --- CUKUP ---
    rules_cukup = [
        min(Rn, C_mid),    # rating normal + crash sedang
        min(Rn, K_mid),    # rating normal + keluhan sedang
        
         # RULE BARU!!!
        min(Rn, C_low, K_low) # rating normal + crash rendah + keluhan rendah
    ]

    # --- BAIK ---
    rules_baik = [
        min(Rk, C_low, K_low),   # rating baik, crash rendah, keluhan rendah
        min(Rk, C_low),          # rating baik + crash rendah
        min(Rk, K_low),          # rating baik + keluhan rendah
    ]

    # ==========================
    # 3. FALLBACK RULE (PENTING)
    # ==========================
    # Jika crash tinggi ATAU keluhan tinggi → otomatis kualitas buruk.
    fallback_buruk = max(C_high, K_high)
    rules_buruk.append(fallback_buruk)

    # Gabungkan semua rules
    rules = rules_buruk + rules_cukup + rules_baik

    # ==========================
    # 4. DEFUZZIFICATION
    # ==========================

    # Mapping tiap rule ke output-nya
    outputs = []

    # 3 rule pertama + fallback = buruk
    for r in rules_buruk:
        if r > 0:
            outputs.append(fuzzy.defuzz(quality_x, np.fmin(r, quality_buruk), 'centroid'))
        else:
            outputs.append(0)

    # Cukup
    for r in rules_cukup:
        if r > 0:
            outputs.append(fuzzy.defuzz(quality_x, np.fmin(r, quality_cukup), 'centroid'))
        else:
            outputs.append(0)

    # Baik
    for r in rules_baik:
        if r > 0:
            outputs.append(fuzzy.defuzz(quality_x, np.fmin(r, quality_baik), 'centroid'))
        else:
            outputs.append(0)

    # ==========================
    # 5. WEIGHTED AVERAGE
    # ==========================

    score = np.sum(np.array(rules) * np.array(outputs)) / (np.sum(rules) + 1e-9)
    return score

# =============================
# 5. Flask Routes
# =============================
@app.route('/', methods=['GET', 'POST'])



def index():
    result = None
    rating = crash = keluhan = None

    if request.method == 'POST':
        rating = float(request.form['rating'])
        crash = float(request.form['crash'])
        keluhan = float(request.form['keluhan'])

        score = fuzzy_inference(rating, crash, keluhan)
        result = int(round(score))

    return render_template(
        "index.html",
        hasil=result,
        
        
        input_rating=format_value(rating),
        input_crash=format_value(crash),
        input_keluhan=format_value(keluhan)
    )


def format_value(x):
    if x is None:
        return None
    return int(x) if float(x).is_integer() else x


@app.route('/grafik')
def grafik():
    return render_template("grafik.html")


@app.route('/about')
def about():
    return render_template("about.html")


# ----------------------------------------------------
# LOCAL RUN ONLY
# ----------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)