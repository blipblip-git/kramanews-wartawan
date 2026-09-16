🐝 STATUS KRAMANEWS
TERAKHIR DIUPDATE: 16 SEPTEMBER 2026 (V2.1)

Portal berita AI otomatis: kramanews.my.idDijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status repo.Untuk konteks lengkap: lihat Dokumen Serah Terima V3 di laptop pemilik.

⚡ SISTEM AKTIF
Komponen	Lokasi	Status
AI Wartawan (skrip-wartawan.py)	GitHub Actions	✅ V6.3.4 — Scheduled LIVE (menit 7/37 WITA)
Sosmed FB (skrip-sosmed.py)	GitHub Actions	✅ V1.7 — Scheduled LIVE (kalibrasi WITA)
Web (index.html, app.js, style.css)	Cloudflare Pages	✅ index v=610 / app.js V5.6 / css v=74
Telegram Command Center	Cloudflare Worker	✅ V1.0 LIVE (bot @kramanews_bot)
Database	Supabase	✅ articles + Storage gambar + admin-ops
🤖 AI WARTAWAN — V6.3.4 (TERBARU)
V6.3.4 (terbaru)
NAMA PUBLIK INSTANSI RESMI: nama yang diumumkan KPK/Kejaksaan/Polri/Pengadilan = informasi publik → WAJIB disebut LENGKAP & BERANI semua (dilarang kabur ke "orang kepercayaan"/"bos properti" jika nama ada di sumber)
FILTER GAMBAR SAMPAH: URL gambar logo/ikon/banner/iklan/thumbnail kecil (<400px) dibuang → otomatis jatuh ke Wikimedia via deskripsi_gambar AI
PERLUASAN GOOGLE NEWS +10 PROVINSI: Kalbar, Kalsel, Kalteng, Bali, NTB, NTT, Papua, Maluku, Gorontalo, Batam (kandidat daerah naik 4x lipat)
Statistik scraping dicetak di akhir run (sukses/gagal)
V6.3.3
SINDROM PENYANGKALAN DIHABISI: dilarang kalimat "identitas narasumber tidak disebutkan dalam laporan" dst (6+ pola) — cukup laporkan fakta langsung
Pola_larang diperkuat (11+ pola) — pelanggaran = berita diblokir sistem
V6.3.2
RESOLVER GOOGLE NEWS: link perantara news.google.com → artikel asli
JINA READER (r.jina.ai): tenaga kedua saat fetch diblokir WAF portal
SPESIFISITAS LOKASI: wilayah terdampak wajib menyebut nama daerah (dilarang "sejumlah daerah" jika sumber menyebut namanya)
NARASUMBER LEMBAGA: kutipan DPRD/BMKG/dll wajib nama orang jika ada
V6.3.1
SCRAPING ARTIKEL ASLI: AI membaca isi penuh artikel (bukan ringkasan RSS 2-3 kalimat) → jadwal laga, kutipan, angka lengkap terangkat
Fallback aman: scraping gagal → ringkasan RSS (sistem tidak pernah mati)
V6.3
Tanggal publikasi RSS disuntik ke prompt → tanggal konkret wajib; frasa "belum dikonfirmasi waktu pasti kejadian" DILARANG + dipolisikan
Narasumber: nama ada = wajib dikutip; panjang mengikuti materi
V6.2
Fix AI menolak breaking valid ("tidak ada tanggal") — umur sumber sudah diverifikasi sistem
Zona waktu
WITA (UTC+8) — seluruh skrip + cron + app.js (V6.4)
Sistem lama yang tetap
Anti-dobel 2 lapis • Anti berita lama 3 lapis • Breaking 3 slot (domestik/dunia/fleksibel) • Anti dominasi gempa (M≥5.5 dom / M≥6.5 dunia) • Kuota kategori per jam • Wikimedia fallback gambar

🖥️ KURSI HERO — APP.JS V5.6
BREAKING segar (≤30 mnt) = VIP: duduk slot 1/2/3 dengan badge merah
Setelah 30 mnt: jatuh jadi RAKYAT BIASA → masuk EKOR antrean (tanpa blokir berbasis waktu yang kadaluarsa — pelajaran V5.5)
TEMBOK UMUR 8 JAM: hanya berita ≤8 jam boleh masuk hero (kasus nyata: Musik Daul Pamekasan umur 24 jam)
ROUND-ROBIN 8 kategori: N→D→I→E→O→T→H→K bergantian duduk
Crowd-cleaner: browser pengunjung mencabut flag breaking >35 mnt langsung ke DB (terbukti: 🧹 #958 dicabut umur 55 mnt)
Auto-refresh 3 menit; SBANON kebal dua nama kunci
ATURAN EMAS pemilik: "siapapun yang duduk, 30 menit harus turun"

📘 SOSMED FB — V1.7 (KALIBRASI WITA)
PRIORITAS KALTARA/TARAKAN: selalu depan antrean (terbukti berkali-kali)
Maks 3 post per run; anti-dobel posted_fb; retry 504; caption optimal
Jadwal baru WITA: tiap 20 mnt jam 09:00-22:00; tiap 30 mnt malam
Token FB: masih hidup (terverifikasi 16 Sep)
📱 TELEGRAM COMMAND CENTER — V1.0 (LIVE & TERUJI)
Lapor teks+foto → AI rapikan → draft + tombol [🚨Breaking][📰Biasa][✏️Revisi][❌Batal]
Terbukti: lapor → tayang < 1 menit di slot breaking
Foto → Supabase Storage "gambar"; token bot SUDAH DIREVOKE & diganti
Worker: kramanews-telegram.denytriono-btm.workers.dev | KV: DRAFTS
🎨 TAMPILAN WEB
Header: logo 38px + KramaNews 24px KIRI, menu TENGAH, 3 ikon KANAN
Bar Breaking: Playfair merah tepi putih + lampu cincin putih; HP: Breaking tengah baris 1, tanggal tengah baris 2
Footer CNN ramping: logo 44px + 30px; TELUSURI center (4x2); IKUTI KAMI kanan (Facebook); Perusahaan & Legal DIHAPUS
"Masuk Admin" HANYA localhost (deteksi hostname otomatis)
Kursi hero: breaking & reguler SAMA 30 menit lalu berganti
Tombol KN melayang HP bottom 160px; Back bottom 36px
Share popup 6 pilihan di header
⏰ JADWAL (SEMUA WITA)
Komponen	Jadwal
Wartawan kategori	06:00-20:00 sesuai JADWAL_JAM (±50-60 berita/hari)
Wartawan breaking	Patroli 24 jam tiap 30 mnt (run menit 7/37)
Sosmed FB	Tiap 20 mnt (09-22) / 30 mnt (malam)
Kaltara	Min 2 berita per sesi daerah
Breaking hidup	30-35 mnt di hero lalu turun jadi rakyat
Hero	Selalu berita umur ≤8 jam, berganti tiap 30 mnt
🐛 DIAGNOSA CEPAT
Gejala	Cek
Breaking stuck	Run Scheduled ada? Manual run? (hero web sudah mandiri — yang gagal biasanya produksi)
Web polos tanpa warna	CSS gagal dimuat — cek versi style.css?v= di index & isi file online
Semua klik mati	F12 Console; historis: SUPABASE_ANON not defined (fix: SBANON V5.3)
Bot Telegram diam	getWebhookInfo; log Worker; 401 = token salah
Dobel/penyangkalan/frasa buruk	Pastikan V6.3.3 (KRAMAV633MARKER)
Nasi basi di hero	Pastikan app.js V5.6 (TEMBOK_UMUR_JAM)
FB tidak posting	Run merah? token kedaluwarsa? antrean kosong (normal)?
Scraping 0%	Link Google News perlu resolver + Jina (V6.3.2)
📋 ANTREAN TUGAS
Evaluasi V6.3.4: nama KPK dkk disebut berani? gambar lebih bersih?
Gambar Level 2 (opsional): verifikasi AI Vision skor relevansi gambar
Pantau Scheduled tetap rutin tiap menit 7/37
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
🗺️ CATATAN CAKUPAN SUMBER
RSS langsung: CNN, Kompas, Antara, CNBC, Tribun (9 wilayah), Bola.net, Yahoo, TechCrunch, Verge, BBC (world/tech/health), Al Jazeera, Guardian, Detik, Kompas Health/Hype

Google News: ±40 query (nasional, 20+ kota/provinsi, 14 negara internasional)

Catatan: Tribun = WAF tebal (scraping sering fallback RSS — normal)