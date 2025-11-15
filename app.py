from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzzy
import matplotlib
matplotlib.use('Agg')  # Backend non-GUI untuk menghindari error di macOS
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# Buat folder static jika belum ada
if not os.path.exists('static'):
    os.makedirs('static')


# Menyatakan universe dari variable
permintaan_x = np.arange(0, 5001, 1)
persediaan_x = np.arange(0, 601, 1)
produksi_x  = np.arange(0, 7001, 1)

# Generate fungsi keanggotaan fuzzy
permintaan_turun = fuzzy.trapmf(permintaan_x, [0, 0, 1000, 5000])
permintaan_naik = fuzzy.trapmf(permintaan_x, [1000, 5000, 5000, 5000])

persediaan_sedikit = fuzzy.trapmf(persediaan_x, [0, 0, 100, 600])
persediaan_banyak = fuzzy.trapmf(persediaan_x, [100, 600, 600, 600])

produksi_berkurang  = fuzzy.trapmf(produksi_x, [0, 0, 2000, 7000])
produksi_bertambah  = fuzzy.trapmf(produksi_x, [2000, 7000, 7000, 7000])


# Membuat 3 grafik sekaligus
fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))

# Grafik 1: Permintaan
ax0.plot(permintaan_x, permintaan_turun, 'b', linewidth=1.5, label='Turun')
ax0.plot(permintaan_x, permintaan_naik, 'g', linewidth=1.5, label='Naik')
ax0.set_title('Permintaan')
ax0.legend()

# Grafik 2: Persediaan
ax1.plot(persediaan_x, persediaan_sedikit, 'b', linewidth=1.5, label='Sedikit')
ax1.plot(persediaan_x, persediaan_banyak, 'g', linewidth=1.5, label='Banyak')
ax1.set_title('Persediaan')
ax1.legend()

# Grafik 3: Produksi
ax2.plot(produksi_x, produksi_berkurang, 'b', linewidth=1.5, label='Berkurang')
ax2.plot(produksi_x, produksi_bertambah, 'g', linewidth=1.5, label='Bertambah')
ax2.set_title('Produksi')
ax2.legend()

# Menghilangkan garis atas dan kanan dari ketiga grafik
for ax in (ax0, ax1, ax2):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()

# Simpan gambar di folder static/img
graph_path = 'static/img/fuzzy_graph.png'
plt.savefig(graph_path)
plt.close()

    

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil_produksi = None

    if request.method == 'POST':
        try:
            # Ambil input dari form
            permintaan = int(request.form['permintaan'])
            persediaan = int(request.form['persediaan'])

            print(f"\nPermintaan: {permintaan}, Persediaan: {persediaan}")

            # Menghitung derajat keanggotaan (miu) permintaan
            miu_permintaan = [
                fuzzy.interp_membership(permintaan_x, permintaan_turun, permintaan),
                fuzzy.interp_membership(permintaan_x, permintaan_naik, permintaan)
            ]

            print(f"Derajat Keanggotaan Permintaan:")
            print(f"  Turun: {miu_permintaan[0]}")
            print(f"  Naik : {miu_permintaan[1]}")

            # Menghitung derajat keanggotaan (miu) persediaan
            miu_persediaan = [
                fuzzy.interp_membership(persediaan_x, persediaan_sedikit, persediaan),
                fuzzy.interp_membership(persediaan_x, persediaan_banyak, persediaan)
            ]

            print(f"Derajat Keanggotaan Persediaan:")
            print(f"  Sedikit: {miu_persediaan[0]}")
            print(f"  Banyak : {miu_persediaan[1]}")

            # Proses inferensi menggunakan metode Tsukamoto
            alpha1 = np.fmin(miu_permintaan[0], miu_persediaan[1])
            z1 = fuzzy.interp_universe(produksi_x, produksi_berkurang, alpha1)
            #z1 = np.interp(alpha1, produksi_berkurang, produksi_x)

            alpha2 = np.fmin(miu_permintaan[0], miu_persediaan[0])
            z2 = fuzzy.interp_universe(produksi_x, produksi_berkurang, alpha2)
            #z2 = np.interp(alpha2, produksi_berkurang, produksi_x)

            alpha3 = np.fmin(miu_permintaan[1], miu_persediaan[1])
            z3 = fuzzy.interp_universe(produksi_x, produksi_bertambah, alpha3)
            #z3 = np.interp(alpha3, produksi_bertambah, produksi_x)

            alpha4 = np.fmin(miu_permintaan[1], miu_persediaan[0])
            z4 = fuzzy.interp_universe(produksi_x, produksi_bertambah, alpha4)
            #z4 = np.interp(alpha4, produksi_bertambah, produksi_x)

            print(f"\nNilai Alpha dan Z:")
            print(f"  Alpha1: {alpha1}, Z1: {z1}")
            print(f"  Alpha2: {alpha2}, Z2: {z2}")
            print(f"  Alpha3: {alpha3}, Z3: {z3}")
            print(f"  Alpha4: {alpha4}, Z4: {z4}")

            # Defuzzifikasi dengan rata-rata tertimbang
            penyebut = alpha1 + alpha2 + alpha3 + alpha4
            if penyebut == 0:
                      hasil_produksi = 0  # atau nilai default, misalnya rata-rata
            else:
                      hasil_produksi = (alpha1 * z1[0] + alpha2 * z2[0] + alpha3 * z3[0] + alpha4 * z4[0]) / (alpha1 + alpha2 + alpha3 + alpha4)

            hasil_produksi = int(hasil_produksi)  # Konversi ke integer

            return render_template('index.html', hasil=hasil_produksi)

        except ValueError:
            return "Input harus berupa angka!"

    return render_template('index.html', hasil=hasil_produksi)

@app.route('/grafik')
def grafik():
    return render_template('grafik.html')

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)

