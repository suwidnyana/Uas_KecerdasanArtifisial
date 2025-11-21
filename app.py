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
crash_x   = np.arange(0, 51, 1)
keluhan_x = np.arange(0, 301, 1)
quality_x = np.arange(0, 101, 1)

# =============================
# 2. Membership Function (NEW)
# =============================

# --- Rating ---
rating_buruk = fuzzy.gaussmf(rating_x, 0.8, 0.6)
rating_normal = fuzzy.gbellmf(rating_x, 1.2, 3, 2.5)
rating_baik = fuzzy.gaussmf(rating_x, 4.3, 0.5)

# --- Crash ---
crash_rendah = fuzzy.sigmf(crash_x, 8, -0.3)
crash_sedang = fuzzy.gaussmf(crash_x, 20, 6)
crash_tinggi = fuzzy.sigmf(crash_x, 30, 0.3)

# --- Keluhan ---
keluhan_sedikit = fuzzy.trapmf(keluhan_x, [0, 0, 40, 80])
keluhan_sedang = fuzzy.trapmf(keluhan_x, [60, 120, 160, 220])
keluhan_banyak = fuzzy.trapmf(keluhan_x, [200, 240, 300, 300])

# --- Quality ---
quality_buruk = fuzzy.sigmf(quality_x, 30, -0.2)
quality_cukup = fuzzy.gaussmf(quality_x, 55, 10)
quality_baik = fuzzy.sigmf(quality_x, 70, 0.2)

# =============================
# 3. Generate GRAPH (New Style)
# =============================
def generate_graph():
    plt.figure(figsize=(10, 12))

    # Rating
    plt.subplot(3, 1, 1)
    plt.plot(rating_x, rating_buruk, label="Buruk")
    plt.plot(rating_x, rating_normal, label="Normal")
    plt.plot(rating_x, rating_baik, label="Baik")
    plt.title("Rating Pengguna (Baru)")
    plt.legend(); plt.grid(True)

    # Crash
    plt.subplot(3, 1, 2)
    plt.plot(crash_x, crash_rendah, label="Rendah")
    plt.plot(crash_x, crash_sedang, label="Sedang")
    plt.plot(crash_x, crash_tinggi, label="Tinggi")
    plt.title("Jumlah Crash (Baru)")
    plt.legend(); plt.grid(True)

    # Keluhan
    plt.subplot(3, 1, 3)
    plt.plot(keluhan_x, keluhan_sedikit, label="Sedikit")
    plt.plot(keluhan_x, keluhan_sedang, label="Sedang")
    plt.plot(keluhan_x, keluhan_banyak, label="Banyak")
    plt.title("Jumlah Keluhan (Baru)")
    plt.legend(); plt.grid(True)

    plt.tight_layout()
    plt.savefig("static/img/fuzzy_graph_new.png")
    plt.close()

generate_graph()

# =============================
# 4. Fuzzy Inference RULE BASE
# =============================
def fuzzy_inference(rating, crash, keluhan):

    # Degree of membership
    Rb = fuzzy.interp_membership(rating_x, rating_buruk, rating)
    Rn = fuzzy.interp_membership(rating_x, rating_normal, rating)
    Rk = fuzzy.interp_membership(rating_x, rating_baik, rating)

    C_low = fuzzy.interp_membership(crash_x, crash_rendah, crash)
    C_mid = fuzzy.interp_membership(crash_x, crash_sedang, crash)
    C_high = fuzzy.interp_membership(crash_x, crash_tinggi, crash)

    K_low = fuzzy.interp_membership(keluhan_x, keluhan_sedikit, keluhan)
    K_mid = fuzzy.interp_membership(keluhan_x, keluhan_sedang, keluhan)
    K_high = fuzzy.interp_membership(keluhan_x, keluhan_banyak, keluhan)

    rules = []

    # RULES (Baru)
    rules.append( min(Rb, max(C_high, K_high)) )   # buruk
    rules.append( min(Rb, K_mid) )                 # buruk
    rules.append( min(Rn, C_high) )                # buruk

    rules.append( min(Rn, C_mid) )                 # cukup
    rules.append( min(Rn, K_mid) )                 # cukup

    rules.append( min(Rk, C_low, K_low) )          # baik
    rules.append( min(Rk, C_low) )                 # baik
    rules.append( min(Rk, K_low) )                 # baik

    # Mapping ke output
    outputs = [
        fuzzy.defuzz(quality_x, np.fmin(r, quality_buruk), 'centroid') if r>0 else 0 for r in rules[:3]
    ] + [
        fuzzy.defuzz(quality_x, np.fmin(r, quality_cukup), 'centroid') if r>0 else 0 for r in rules[3:5]
    ] + [
        fuzzy.defuzz(quality_x, np.fmin(r, quality_baik), 'centroid') if r>0 else 0 for r in rules[5:]
    ]

    # Weighted average
    score = np.sum(np.array(rules) * np.array(outputs)) / (np.sum(rules) + 1e-9)
    return score


# =============================
# 5. Flask Routes
# =============================
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None

    if request.method == 'POST':
        rating = float(request.form['rating'])
        crash = float(request.form['crash'])
        keluhan = float(request.form['keluhan'])

        score = fuzzy_inference(rating, crash, keluhan)
        result = int(round(score))

    return render_template("index.html", hasil=result)


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