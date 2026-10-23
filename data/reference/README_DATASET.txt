CALIFORNIA WATER LOSS - DATASET UNTUK EKSPLORASI PORTOFOLIO
Diunduh dan diperiksa: 21 Oktober 2026.

ISI
1. ca-retailer-waterlossdata.csv: CSV asli, byte sumber dipertahankan.
2. data_dictionary.csv: kamus data resmi, 142 baris definisi.
3. source_manifest.json: sumber, checksum SHA-256, dan cakupan data.

PEMERIKSAAN AWAL
4.936 baris, 190 kolom, 441 ID organisasi unik.
609 nilai PWS_ID_OR_OTHER_ID unik; belum dinormalisasi sebagai identitas sistem kanonis.
Satu baris merupakan laporan audit sistem air untuk suatu periode. Satu organisasi dapat memiliki beberapa sistem.
Tanggal mulai minimum 2015-07-01; maksimum 2025-01-01.
Tanggal akhir minimum 2016-06-30; maksimum 2025-12-31.
Tidak ada duplikat kunci gabungan organisasi + ID sistem + tanggal mulai + tanggal akhir.
Seluruh nilai volume air tersuplai, real losses, apparent losses, non-revenue water (kolom _AF), jumlah sambungan, dan panjang jaringan dapat dibaca sebagai angka.

TEMUAN YANG HARUS DITANGANI SEBELUM ANALISIS
- REPORTING_YEAR kosong seluruhnya. Kamus resmi menyarankan tanggal mulai/akhir untuk mengidentifikasi periode audit.
- Campuran tahun kalender dan fiskal. Jangan membandingkan periode berbeda tanpa penjelasan.
- Unit asal: Acre-feet (3.097 baris) dan Million gallons (US) (1.839 baris). Gunakan kolom _AF yang sudah dikonversi oleh penyedia untuk perbandingan volume.
- 64 baris real losses _AF bernilai negatif; apparent losses negatif pada 3 baris; non-revenue water negatif pada 25 baris. Tandai dan periksa, jangan otomatis diubah menjadi nol.
- Status laporan: Requirements Addressed 2.369; Preliminarily Approved 2.114; Requirements Not Addressed 310; Under Review 140; Not Required 3. Status tidak sama dengan jaminan semua nilai akurat.
- Tahun akhir pelaporan 2025 hanya 152 baris, dibanding 549 untuk 2024. Tidak boleh langsung dianggap penurunan aktivitas/kehilangan air secara agregat.
- Versi formulir V5, V6.0, V6.1 bercampur. Kamus data hanya mencakup 142 dari 190 kolom; cek definisi kolom baru sebelum dipakai.
- Beberapa kolom tambahan kosong seluruhnya atau sangat jarang terisi.
- Kolom kontak administratif tidak diperlukan untuk analisis kinerja; keluarkan dari tabel analisis/dashboard publik.

PENILAIAN
Layak untuk EDA, SQL, dan dashboard portofolio setelah cleaning, pemeriksaan satuan, periode, status, dan nilai anomali. Dataset asli belum merupakan dataset bersih siap modeling.
Fokus awal yang masuk akal: tren pada kelompok sistem yang konsisten, perbandingan kehilangan air dengan ukuran sistem, konsentrasi volume kehilangan air, dan kualitas pelaporan.
Kelayakan ML belum ditetapkan. Jangan memprediksi label yang dibentuk langsung dari fitur yang sama atau memakai kolom hasil perhitungan target sebagai input.
Sumber resmi meningkatkan ketertelusuran, bukan jaminan bebas kesalahan. Semua hasil harus disertai cakupan dan batasan.
