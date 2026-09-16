🐝 STATUS KRAMANEWS
TERAKHIR DIUPDATE: 16 SEPTEMBER 2026 (V3)

Portal berita AI otomatis: kramanews.my.idDijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status repo.Untuk konteks lengkap: lihat Dokumen Serah Terima V3 di laptop pemilik.

⚡ SISTEM AKTIF
🤖 AI Wartawan — skrip-wartawan.py — GitHub Actions✅ V6.3.4 — Scheduled LIVE (menit 7/37 WITA)

📘 Sosmed FB — skrip-sosmed.py — GitHub Actions✅ V1.7 — Scheduled LIVE (kalibrasi WITA)

🌐 Web — index.html + app.js + style.css — Cloudflare Pages✅ index v=620 (GA4 terpasang) / app.js V5.7 / css v=74

📱 Telegram Command Center — Cloudflare Worker✅ V1.0 LIVE — bot @kramanews_bot

🗄️ Database — Supabase✅ articles + Storage gambar + admin-ops

📊 Analytics & SEO✅ GA4 aktif (G-D8ZGH4Q3E8) — pengunjung manusia bersih tanpa bot✅ Search Console terverifikasi + sitemap submitted✅ Cloudflare Analytics (355 Indonesia / bot USA diabaikan)

🤖 AI WARTAWAN — V6.3.4 (TERBARU)
✨ V6.3.4 (terbaru)
NAMA PUBLIK INSTANSI RESMI: nama yang diumumkan KPK/Kejaksaan/Polri/Pengadilan = informasi publik → WAJIB disebut LENGKAP & BERANI semua (dilarang kabur ke "orang kepercayaan"/"bos properti" jika nama ada di sumber)
FILTER GAMBAR SAMPAH: URL gambar logo/ikon/banner/iklan/thumbnail kecil (<400px) dibuang → otomatis jatuh ke Wikimedia via deskripsi_gambar AI
PERLUASAN GOOGLE NEWS +10 PROVINSI: Kalbar, Kalsel, Kalteng, Bali, NTB, NTT, Papua, Maluku, Gorontalo, Batam — kandidat daerah naik 4x lipat
Statistik scraping dicetak di akhir run (sukses/gagal)
✨ V6.3.3
SINDROM PENYANGKALAN DIHABISI: dilarang kalimat "identitas narasumber tidak disebutkan dalam laporan" dst — cukup laporkan fakta langsung
Pola_larang diperkuat (11+ pola) — pelanggaran = berita diblokir sistem
✨ V6.3.2
RESOLVER GOOGLE NEWS: link perantara news.google.com → artikel asli
JINA READER (r.jina.ai): tenaga kedua saat fetch diblokir WAF portal
SPESIFISITAS LOKASI: wilayah terdampak wajib menyebut nama daerah (dilarang "sejumlah daerah" jika sumber menyebut namanya)
NARASUMBER LEMBAGA: kutipan DPRD/BMKG/dll wajib nama orang jika ada
✨ V6.3.1
SCRAPING ARTIKEL ASLI: AI membaca isi penuh artikel (bukan ringkasan RSS 2-3 kalimat) → jadwal laga, kutipan, angka lengkap terangkat
Fallback aman: scraping gagal → ringkasan RSS (sistem tidak pernah mati)
✨ V6.3
Tanggal publikasi RSS disuntik ke prompt → tanggal konkret wajib
Frasa "belum dikonfirmasi waktu pasti kejadian" DILARANG + dipolisikan
Narasumber: nama ada = wajib dikutip; panjang mengikuti materi
✨ V6.2
Fix AI menolak breaking valid ("tidak ada tanggal") — umur sumber sudah diverifikasi sistem
🕐 Zona waktu
WITA (UTC+8) — seluruh skrip + cron + app.js + GA4
🧰 Sistem lama yang tetap
Anti-dobel 2 lapis
Anti berita lama 3 lapis
Breaking 3 slot (domestik / dunia / fleksibel)
Anti dominasi gempa (M≥5.5 dom / M≥6.5 dunia)
Kuota kategori per jam
Wikimedia fallback gambar
Scraping rantai 4 lapis: Direct → Resolver GN → Jina → RSS
🖥️ KURSI HERO — APP.JS V5.7
BREAKING segar (≤30 mnt) = VIP: duduk slot 1/2/3 dengan badge merah
Setelah 30 mnt: jatuh jadi RAKYAT BIASA → masuk EKOR antrean — TANPA blokir waktu khusus (blokir 3 jam V5.5/V5.5.1 DIBUANG: sukur-sukur kebagian nomor antrean)
TEMBOK UMUR 6 JAM: hanya berita ≤6 jam boleh masuk hero — umur >6 jam GUGUR permanen dari panggung utama (masih tampil di daftar bawah sebagai arsip)
ROUND-ROBIN 8 kategori digali dalam: semua level antrean ditempuh sebelum kembali ke yang sudah duduk
DARURAT: jika tak ada berita lolos tembok, hero tetap hidup menampilkan terbaru tersedia (tanpa keistimewaan)
Crowd-cleaner: browser pengunjung mencabut flag breaking >35 mnt langsung ke DB (terbukti: 🧹 #958)
Auto-refresh 3 menit; SBANON kebal dua nama kunci
ATURAN EMAS pemilik: "siapapun yang duduk, 30 menit harus turun — jadi rakyat, ikut antrean panjang"Data pembanding: produksi ±48 berita/hari (D=17, I=15, N=8) vs konsumsi hero 6 slot/jam → antrean selalu beralih ke berita segar

📘 SOSMED FB — V1.7 (KALIBRASI WITA)
PRIORITAS KALTARA/TARAKAN: selalu depan antrean (terbukti 2x: KSOP+PMK+Bantuan Pangan, lalu Ruko+Bapas+Samsat)
Maks 3 post per run; anti-dobel posted_fb; retry 504; caption optimal
Jadwal WITA: tiap 20 mnt jam 09:00-22:00; tiap 30 mnt malam
Token FB: hidup (terverifikasi 16 Sep — posting sukses)
📱 TELEGRAM COMMAND CENTER — V1.0 (LIVE & TERUJI)
Lapor teks+foto → AI rapikan → draft + tombol [🚨Breaking][📰Biasa][✏️Revisi][❌Batal]
Terbukti: lapor → tayang < 1 menit di slot breaking
Foto → Supabase Storage "gambar"; token bot SUDAH DIREVOKE & diganti
Worker: kramanews-telegram.denytriono-btm.workers.dev | KV: DRAFTS
🎨 TAMPILAN WEB
Header: logo 38px + KramaNews 24px KIRI, menu TENGAH, 3 ikon KANAN
Bar Breaking: Playfair merah tepi putih + lampu cincin putih
HP: Breaking tengah baris 1, tanggal tengah baris 2
Footer CNN ramping: logo 44px + 30px; TELUSURI center (4x2); IKUTI KAMI kanan (Facebook); Perusahaan & Legal DIHAPUS
Masuk Admin: HANYA localhost (deteksi hostname otomatis → body.is-publik)
Tombol KN melayang HP bottom 160px; Back bottom 36px
Share popup 6 pilihan di header
GA4 script terpasang di head (G-D8ZGH4Q3E8)
⏰ JADWAL (SEMUA WITA)
Komponen	Jadwal
Wartawan kategori	06:00-20:00 sesuai JADWAL_JAM (±48-60 berita/hari)
Wartawan breaking	Patroli 24 jam tiap 30 mnt (run menit 7/37)
Sosmed FB	Tiap 20 mnt (09-22) / 30 mnt (malam)
Kaltara	Min 2 berita per sesi daerah
Breaking hidup	30-35 mnt di hero lalu turun jadi rakyat
Hero	Selalu berita umur ≤6 jam, berganti tiap 30 mnt
Biaya DeepSeek	Terbukti ±$0.04-0.07/hari (±79 request, rasio 1.7 req/berita) — saldo $2 cukup ±1 bulan
🐛 DIAGNOSA CEPAT
Breaking stuck → run Scheduled ada? Manual run? (hero web sudah mandiri — yang gagal biasanya produksi)
Web polos tanpa warna → CSS gagal dimuat — cek versi style.css?v= di index & isi file online
Semua klik mati → F12 Console; historis: SUPABASE_ANON not defined (fix: SBANON V5.3)
Bot Telegram diam → getWebhookInfo; log Worker; 401 = token salah
Dobel/penyangkalan/frasa buruk → pastikan V6.3.3 (KRAMAV633MARKER)
Nasi basi di hero → pastikan app.js V5.7 (TEMBOK_UMUR_JAM=6)
FB tidak posting → run merah? token kedaluwarsa? antrean kosong (normal)?
Scraping 0% → link Google News perlu resolver + Jina (V6.3.2)
Hero pakai berita lama → normal HANYA saat darurat (tak ada berita ≤6 jam sama sekali)
📋 ANTREAN TUGAS
Evaluasi V6.3.4 — nama KPK dkk disebut berani? gambar lebih bersih? statistik scraping naik?
Akun bisnis IG/Threads — tunggu email Yahoo dibuat (di cafe, perangkat+IP baru) → lanjut IG profesional → Threads → Meta App → Threads API → skrip-sosmed V1.8
Gambar Level 2 (opsional) — verifikasi AI Vision skor relevansi gambar
Update README ini setiap revisi besar
⚠️ PELAJARAN BERHARGA (jangan diulang!)
Revisi = FILE UTUH selalu (kasus v=511 crash)
CSS berubah → naikkan versi style.css?v= di index (kasus HP tidak berubah)
Token = copy-paste, jangan ketik (kasus 401)
Cron jangan menit 0/30 (padat global — pakai 7/37)
File terkait drag BERSAMAAN (index+app.js)
Cloudflare Pages tersambung GitHub — cek deployment benar-benar masuk (kasus drag tidak tayang)
Jangan klaim tanpa cek kode (kasus blokir 3 jam ternyata bolong)
Localhost dulu → verifikasi → drag online
Scraping: portal besar Indonesia ber-WAF → butuh resolver + Jina
AI "takut" aturan ketat → perlu aturan penyeimbang eksplisit (kasus: menolak semua breaking, lalu menyembunyikan nama KPK)
Hapus aturan lama bisa menciptakan kebiasaan baru — pantau hasilnya (kasus: penghapusan atribusi kosong → muncul sindrom penyangkalan)
🗺️ CATATAN CAKUPAN SUMBER
RSS langsung:CNN • Kompas • Antara • CNBC • Tribun (9 wilayah) • Bola.net • Yahoo • TechCrunch • Verge • BBC (world/tech/health) • Al Jazeera • Guardian • Detik • Kompas Health/Hype

Google News:±50 query — nasional, 20+ kota/provinsi (termasuk 10 baru: Kalbar, Kalsel, Kalteng, Bali, NTB, NTT, Papua, Maluku, Gorontalo, Batam), 14 negara internasional

Catatan: Tribun = WAF tebal (scraping sering fallback RSS — normal)Catatan: Biaya DeepSeek terbukti ±$0.04-0.07/hari