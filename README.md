🐝 STATUS KRAMANEWSTERAKHIR DIUPDATE: 19 SEPTEMBER 2026 (V6)

Portal berita AI otomatis: kramanews.my.idDijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status repo.Untuk konteks lengkap: lihat Dokumen Serah Terima V4 di laptop pemilik.

⚡ SISTEM AKTIF

🤖 AI Wartawan — skrip-wartawan.py — GitHub Actions✅ V6.4.0 — Scheduled LIVE (cron KAWAL GANDA menit 7/22/37/52 WITA)

📘 Sosmed — skrip-sosmed.py — GitHub Actions✅ V1.8.1 — FB + INSTAGRAM — Scheduled LIVE

🌐 Web — index.html + app.js + style.css — Cloudflare Pages✅ index v=628 (GA4 G-D8ZGH4Q3E8) / app.js V5.8.4 / css V10 FINAL (dirapikan)

📱 Telegram Command Center — Cloudflare Worker✅ V1.0 LIVE — bot @kramanews_bot

🗄️ Database — Supabase✅ articles (+ posted_ig) + Storage "gambar" (dibuat 18 Sep!) + admin-ops

📊 Analytics & SEO✅ GA4 aktif • Search Console terverifikasi + sitemap submitted⚠️ Indeks Google baru 1 halaman (beranda) — program request indexing 10 URL/hari berjalan (18 Sep kuota habis = tanda bekerja)

🤖 AI WARTAWAN — V6.4.0 (TERBARU 18 SEP)

✨ V6.4.0 (terbaru)AI VISION BLUR-GATE: setiap gambar dinilai DeepSeek (1-10, kualitas & relevansi). Skor < 7 → DIBUANG → Wikimedia via deskripsi_gambar. Log penanda: "👁️ Vision skor: X/10 → LOLOS/DIBUANG".UEFA/CHAMPIONS RENTANG TANGGAL: scoreboard ESPN diminta rentang ±4 hari (dates=YYYYMMDD-YYYYMMDD) — laga malam Kamis WITA tidak terlewat lagi di run Jumat pagi.KLASMEN ENDPOINT FIX: site-standings ESPN ternyata mengembalikan {} kosong (terbukti tes browser 18 Sep) → diganti endpoint CORE (sports.core.api.espn.com). Jika core juga kosong → klasemen menyusul, skor tetap jalan.⚠️ VISION: model dipakai "deepseek-vision" — run pertama GAGAL menilai ("Vision gagal menilai — dipertahankan"). PERLU DICEK: ganti model ke "deepseek-chat" (dengan format image_url) atau cek nama model vision yang tersedia di akun. Sampai diperbaiki: gambar selalu dipertahankan (aman, hanya blur-gate belum aktif).

✨ V6.3.8RANGKUMAN LIGA EROPA 06:00 WITA (breaking) • NBA 13:00 •IDX/KURS 11/14/17 (Yahoo Finance — TERBUKTI 2x: 6.462,43 & 6.453,21) •MBG/KDMP/KEGIATAN MENTERI prioritas bergilir • OKEZONE masuk •TOPIK WAJIB dengan parsing aman (token ≤4 huruf pakai batas kata).

✨ V6.3.7ANTI-DOBEL 36 JAM (fix bocor tengah malam — Kebakaran Bambel 2x).✨ V6.3.6 PROMISE-CHECK judul • ✨ V6.3.5 BREAKING ANTI-OPINI •✨ V6.3.4 NAMA PUBLIK RESMI WAJIB + FILTER GAMBAR SAMPAH + +10 PROVINSI •✨ V6.3.1-V6.3.3 SCRAPING 4 LAPIS + POLISI FRASA.

🛡️ CRON KAWAL GANDA (17 SEP)Run Scheduled GitHub BISA DIBUANG DIAM-DIAM ±5 jam saat antrean global padat (kasus 17 Sep: 12:44 lompat ke 17:10).Solusi: setiap slot 2 menit — 7/37 + KAWAL 22/52. Run yang lolos dobel AMAN (anti-dobel menolak, biaya nol). Cron: '7,22,37,52 21-22' • '7,22,37,52 23' • '7,22,37,52 0-13' • '7,52 14-20' (semua UTC).⚠️ 18 Sep pagi: run 06:07/06:22 TETAP tidak muncul (hanya 05:48). GitHub masih belum stabil membaca jadwal baru — PANTAU; jika berulang → TINGKAT 2: pemicu eksternal (cron-job.org gratis) mengetuk Worker tiap slot.

🖥️ WEB — V10 FINAL (18 SEP: CSS DIRAPIKAN 1600→1200 BARIS)Mode Terang: header BIRU ES TIPIS #EAF1FB • menu 8 kategori 8 WARNA (Nasional merah, Daerah biru Krama, Internasional biru laut, Ekonomi hijau, Olahraga oranye, Teknologi ungu, Hiburan pink, Kesehatan teal) • ikon cari/share/mode TRANSPARAN biru Krama (hover biru tua) • KramaNews 26px Krama biru + News merah + kilau biru (brandGlowHeader) • footer HITAM + Instagram + email center + KramaNews kilau putih (brandGlowFooter) • kapsul filter 8 warna • Jelajahi 8 warna • Paling(biru)Buzz(merah) • lokasi merah News.SEMUA: tanggal di SEMUA tempat (kartu "17 Sep 2026", halaman baca "Kamis, 17 September 2026 • 17:50 WITA") • tabel klasmen • roket 🚀 • sticky header • header tanpa logo KN.DIRAPIKAN: netlify/nav-date/duplikat V6.x DIBUANG. Hasil tes pemilik: tampilan identik sebelum-sesudah ✅.

📘 SOSMED — V1.8.1 (FB + INSTAGRAM)FB: prioritas KALTARA, maks 3/run, anti-dobel posted_fb ✅ LIVE.IG @krama.news: TERBUKTI posting otomatis 18 Sep ✅ (foto+caption+hashtag, maks 2/run, 6/hari, posted_ig). Token IG_PAGE_TOKEN ±60 hari (expired → log memberi instruksi).THREADS: cross-post MANUAL dari IG (API menyusul).

📱 TELEGRAM COMMAND CENTER⚠️ V1.2.4 siap (terima PNG/File + foto-terpisah-diingat-KV-1-jam + WITA + prompt tanpa frasa terlarang) — BELUM DIDEPLOY (masalah foto tunda). V1.0 masih live. Marker V1.2.4: KRAMATELEGRAMV12MARKER. MASALAH AKAR 18 Sep: bucket "gambar" TIDAK PERNAH ADA sejak dulu → dibuat 18 Sep (public) → upload masih 403 "Invalid Compact JWS" (kunci service: sudah diganti 2x, tetap 400) → LANJUT: cek policy bucket "gambar" (Storage → Policies) — kemungkinan policy INSERT untuk service/anon hilang saat bucket dibuat ulang!

🗄️ SUPABASEarticles: kolom LENGKAP terverifikasi SQL 18 Sep (id, title, content, category, image_url ⚠️ NAMA BEDA: skrip/app.js memanggil "img"!, author, published_at, created_at ✅ ADA, status, breaking, posted_fb, posted_ig, views, views_count, dll).⚠️ PENTING: tabel pakai image_url (bukan img), views (bukan views_count sendiri), published_at (+ created_at ada). Kolom posted_ig ditambah 17 Sep (baris lama NULL — skrip V1.8.1 kebal NULL ✅).Storage: bucket "gambar" public DIBUAT 18 Sep (sebelumnya TIDAK ADA — akar masalah foto wartawan gagal 400/403).

🚨🚨 MASALAH BESAR TERBUKA 18/09 — WEB BEKU SEJAM 9:15 🚨🚨GEJALA: Web kramanews.my.id TIDAK menampilkan berita baru sejak ±09:15 (berita Telegram 11:15 + IHSG 2x + kategori jam 10-11 tidak muncul), TAPI: (a) datanya ADA di Supabase (SQL membuktikan id 1113-1117 published ✅), (b) FB MENAMPILKAN semuanya (termasuk Tes Manual), (c) F12 Console web live BERSIH (hanya img-cache yang belum dibuat).SUDAH DICoba: RLS policy dibuat 18 Sep (public_read_published + public_update_views) → Success → TETAP tidak berubah (menunggu verifikasi pemilik).DUGAAN TERSISA (urutan):

LOCALSTORAGE browser terjebak data 9:15 → TES: buka web dimode INCOGNITO / HP lain → jika muncul = localStorage → obat:hapus kramanews-news-override / perbaiki refreshNews (V6.4.1:Supabase sumber utama, localStorage hanya cadangan).
Cek console web live: F12 di kramanews.my.id (BUKAN dashboardSupabase!) → screenshot semua error MERAH.
Query app.js: order=created_at.desc — verifikasi created_atterisi semua (SQL: SELECT id, created_at IS NULL FROM articles).DIAGNOSA YANG SUDAH GUGUR (jangan diulang): error isCloud (sudah fix, app.js live = V5.8.4 ✅), bucket tidak ada (sudah dibuat ✅), kunci service (sudah diganti 2x ✅ — namun tetap 403 JWS saat upload foto → cek policy bucket!), RLS (sudah dibuat policy ✅).PELAJARAN: FB menampilkan tapi WEB tidak = data aman, masalah 100% di sisi tampilan web. JANGAN menebak — buktikan per lapisan: Supabase (SQL) → fetch manual → console web → localStorage.
📱 TELEGRAM COMMAND CENTERV1.0 LIVE: lapor → tayang < 1 mnt ✅ TERBUKTI (18 Sep: #10xx BREAKING dengan foto wartawan!).⚠️ MASALAH FOTO: PNG via File/Dokumen DITOLAK V1.0 (hanya gallery). V1.2.4 sudah dibuat (terima File + foto-terpisah-diingat 1 jam) — BELUM DIDEPLOY. Deploy saat diperlukan (kode ada di chat 18 Sep).Upload foto → Supabase Storage masih 403 (lihat masalah besar di atas).

🎨 TAMPILAN WEB — Lihat seksi WEB di atas (V10 FINAL).

⏰ JADWAL (WITA) — KAWAL GANDA06:00 Rangkuman Liga Eropa • 06-20 kuota • 11/14/17 IDX • 13:00 NBA •breaking patroli 24 jam • FB+IG tiap 20/30 mnt • breaking hidup 30-35 mnt.DeepSeek ±$0.04-0.07/hari + vision ±1 panggilan ekstra/berita.

🐛 DIAGNOSA CEPATWEB BEKU, FB JALAN → lihat 🚨 MASALAH BESAR di atas (localStorage → console → RLS — urutan ceknya).IG/FB ganda → anti-dobel posted_ig/posted_fb; cek kolom NULL.Run hilang → cek Actions: ada/hilang/merah; kawalan 22/52 sudah menangani — kalau berulang → Tingkat 2 (pemicu eksternal).Rangkuman Eropa "skip aman" di hari laga → cek ESPN scoreboard URL di browser (tes 18 Sep: hidup ✅); UEFA butuh rentang tanggal (sudah di V6.4.0).Vision gagal menilai → cek nama model deepseek di akun.

📋 ANTREAN TUGAS (URUT PRIORITAS)

🚨 WEB BEKU — selesaikan (lihat 🚨 MASALAH BESAR): incognito tes →localStorage → console → RLS verify. (18 Sep malam: berhenti,pemilik lelah — lanjut pagi dengan kepala dingin.)
Fix Vision model (1 baris: deepseek-vision → deepseek-chat /cek nama model yang tersedia).
ROTASI KUNCI SERVICE Supabase (ter-ekspose di chat 18 Sep!) —Settings → API Keys → rotate → update Cloudflare secretSUPABASE_SERVICE (copy-paste!).
Deploy Worker Telegram V1.2.4 (kode siap di chat 18 Sep) —terima PNG/File + foto-terpisah.
Cek policy bucket "gambar" (Storage → Policies): INSERT untukservice role — akar 403 upload foto.
Peredam lonjakan: Worker img-cache (error kuning img-cache hilang).
Berita dobel 13:42 — tunggu bukti pemilik (judul+link) → V6.3.xlapisan tambahan.
README/Dokumen V5: masukkan Aturan 8-14 + pelajaran 18 Sep.
favicon (masih lama) • Threads manual • V1.3 klasemen menyusuldata core • arsip Worker ke laptop.
⚠️ PELAJARAN BERHARGA (AKUMULASI — JANGAN DIULANGI!)FILE UTUH SELALU — tanpa part tanpa selipan (isCloud hilang, syntax error 195) — pemilik: "jangan suruh selip 1 huruf!"TANYA DULU SEBELUM KODE — pemilik bertanya ≠ izin gas (3x pelanggaran 18 Sep: "kau ini ribuan kali aku katakan...")SATU LANGKAH PER PESAN — jangan tumpuk instruksi klik-klik Meta dsb.FULL-PATH RULE: GitHub → repo → Actions → workflow → Run (jangan cuma "buka Actions"). Pemilik BARU di tiap layanan.LOCALHOST ≠ WEB LIVE — tes di live dulu (hard refresh) sebelum menyalahkan kode; sinkronkan folder VS Code dengan live.FB = DETEKTOR: FB tampil + web tidak = data aman, masalah di tampilan web (jangan tuduh produksi/database).Menambah kolom/tabel Supabase bisa mengubah perilaku RLS/policy → cek policy setelah struktur berubah.Kolom bool baru = baris lama NULL → skrip WAJIB kebal NULL.Token = copy-paste via tombol, verifikasi panjang di notepad.Run Scheduled bisa dibuang GitHub ±5 jam → cron kawal 22/52.CSS animasi jangan ditempel ke elemen ber-animasi lain (bentrok).GitHub = mesin waktu: commit lama tersimpan, bisa dipulihkan.DeepSeek Vision: cek dulu nama model tersedia di akun SEBELUM dipakai di produksi (tes 1 panggilan).

🆕 PELAJARAN 18 SEPTEMBER (hari penuh tragedi-komedi 😅):

Kunci service ter-paste ke CHAT → WAJIB rotasi besok (sudahdiantrekan). Aturan: verifikasi dulu LAYAR sebelum paste apa pun.
"Success" insert ≠ data ada → selalu verifikasi via SQL SELECT.
Bucket Supabase bisa TIDAK ADA walau dokumen bilang ada →verifikasi Storage langsung, jangan percaya catatan lama.
Edit struktur tabel (add column) bisa mengubah RLS → cek policysetelahnya (dugaan kuat penyebab web beku — BELUM terbukti).
Pemilik lelah = STOP. Ringkas posisi, tawarkan jeda, besoklanjut satu langkah. (Kesehatan sesi = kualitas jawaban.)
🗺️ SUMBERRSS: CNN • Kompas • Antara • CNBC • Okezone • Tribun (9) • Bola.net •Yahoo • TechCrunch • Verge • BBC (3) • Al Jazeera • Guardian • Detik •Kompas Health/Hype • Google News ±55 query • API: Yahoo Finance • ESPN(scoreboard ✅ / standings site-API kosong / core-standings V6.4.0)

📍 CARA COMMIT (dari awal — full-path sesuai aturan barumu):
Buka github.com/blipblip-git/kramanews-wartawan
Klik README.md → ikon pensil ✏️
Ctrl+A → Ctrl+V (paste ganti total) → Commit changes → konfirmasi
