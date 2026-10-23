# Ringkasan modeling
- Kandidat ML terpilih berdasarkan validation: ridge_alpha_10.
- MAE validation: baseline 163.18 AF; kandidat ML 157.12 AF.
- Evaluasi test 2024: 307 pasangan sistem-tahun.
- MAE test: baseline 142.56 AF; kandidat ML 149.04 AF.
- Perubahan MAE relatif terhadap baseline: -4.54% (positif = MAE lebih kecil).
- MAE kandidat ML pada test lebih tinggi daripada baseline.
- Kandidat dipilih sebelum test; hasil test tidak digunakan untuk memilih ulang model.

Batas interpretasi:
- Hasil berasal dari satu tahun test pada sampel audit yang lolos cleaning.
- Waktu publikasi dan revisi audit historis belum diverifikasi; ini bukan backtest operasional.
- Sistem yang sama dapat muncul antartahun; hasil bukan bukti generalisasi ke seluruh sistem baru.
- MAE global perlu dibaca bersama kesalahan menurut ukuran sistem dan RMSE.
- Perbedaan numerik belum merupakan bukti signifikansi statistik atau manfaat operasional.

Hubungan dengan proyek data analis:
- SQL dan EDA menjelaskan cakupan dan pola historis; ML menambah evaluasi prediksi terhadap baseline.
- Dashboard harus menampilkan periode, ukuran sampel, baseline, dan keterbatasan ini.
- Analisis SQL saat ini memakai SQLite lokal, bukan BigQuery.

Catatan hasil: keunggulan ML belum konsisten pada validation dan test. Baseline tetap perlu ditonjolkan; jangan menyebut ML terbukti lebih unggul secara umum.