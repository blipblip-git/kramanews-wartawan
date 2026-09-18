🐝 STATUS KRAMANEWS — TERAKHIR DIUPDATE: 19 SEPTEMBER 2026 (V7)
Portal berita AI otomatis: kramanews.my.idDijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status repo. Untuk konteks lengkap: lihat Dokumen Serah Terima V5 di laptop pemilik.

⚡ SISTEM AKTIF
🤖 AI Wartawan — skrip-wartawan.py — GitHub Actions — ✅ V6.4.1 (anti-judul Frankenstein) — Scheduled LIVE + KAWAL GANDA + PEMICU EKSTERNAL cron-job.org AKTIF
📘 Sosmed — skrip-sosmed.py — GitHub Actions — ✅ V1.8.1 — FB + IG — Scheduled LIVE
🌐 Web — index.html + app.js + style.css — Cloudflare Pages — ✅ index v=630 / app.js V5.8.6 (local) / style.css V10 + BLOK CSS V11.1–V11.6 (local, marker V11R1–V11R6)
📱 Telegram Command Center — Cloudflare Worker — ✅ V1.0 LIVE (V1.2.4 siap, belum deploy)
🗄️ Database — Supabase — ✅ articles + Storage "gambar" + admin-ops
📊 Analytics — GA4 G-D8ZGH4Q3E8 • Search Console terverifikasi + sitemap
⚠️ STATUS WEB: perbaikan tombol search/share + CSS V11 sudah teruji LOCALHOST; BELUM DI-DRAG ke Cloudflare — drag final menunggu perintah pemilik (app.js V5.8.6 + index.html v=630, css v=93).

🚨 MASALAH BESAR YANG SUDAH DISELESAIKAN (18–19 SEP) — ARSIP
✅ 1. WEB BEKU SEJAM 09:15 (18 Sep) — TUNTAS 19 Sep
AKAR: fungsi sbRequest HILANG dari app.js saat edit V5.8.4 (kasus kembar: isCloud hilang di V5.8.3). Dipanggil 10x, tidak didefinisikan → ReferenceError DITELAN try/catch → console bersih → web makan localStorage bekas jam 09:15.PELAJARAN EMAS: console bersih ≠ kode sehat. try/catch bisa menelan error fatal. Kalau fungsi dipanggil → WAJIB pastikan definisinya ada (Ctrl+F function namafungsi di file LIVE dengan ?v=).OBAT: app.js V5.8.5 (sbRequest dipulihkan) + index v=629 → drag → berita langsung mengalir. FORENSIK: kramanews.my.id/app.js?v=629 Ctrl+F KRAMAV585MARKER + function sbRequest.

✅ 2. GITHUB MEMBUANG SCHEDULED RUN DIAM-DIAM — TUNTAS (TINGKAT 2 AKTIF)
GitHub 2 hari berturut membuang run (17 Sep: 5 jam; 18 Sep: 12:37–15:07 kosong total → NBA jam 13 & slot lain bolong). Hijau ≠ terbit: run hijau bisa berisi NOL berita.OBAT PERMANEN (19 Sep): PEMICU EKSTERNAL cron-job.org (GRATIS)

Akun: cron-job.org (email bisnis) — job "KramaNews Keeper"
URL: https://api.github.com/repos/blipblip-git/kramanews-wartawan/actions/workflows/wartawan.yml/dispatches
Method POST • Body: {"ref":"main"}
Auth: "Requires HTTP authentication" = Username blipblip-git + Password = token GitHub ghp_... (POLOS, tanpa kata "token")
Headers custom TIDAK BISA dipakai di cron-job.org (header Authorization dikirim tapi ditolak 401) → Basic Auth bawaan adalah jalur yang TERBUKTI (TEST RUN = 204)
Jadwal: Custom 7 * * * * (menit 7 tiap jam, WITA) — Time zone Asia/Makassar
Notifikasi gagal: ON
Token: kramanews-keeper-2 (No expiration, scope repo). Token pertama (kramanews-keeper) SUDAH DIHAPUS setelah keeper-2 terbukti.HASIL: run 204 → Actions hijau. GitHub cron tetap jalan sebagai kawalan; dobel antar pengetuk AMAN (anti-dobel menolak, biaya nol).
✅ 3. JUDUL "FRANKENSTEIN" (2 BERITA DALAM 1 JUDUL) — TUNTAS (V6.4.1)
Beberapa hari teramati: satu judul berisi dua topik berbeda (contoh nyata: "Ferry Kebut ... Koperasi ..."; judul Korsel dari materi buruh AS).AKAR: match_articles lama menggabungkan kandidat hanya dengan ≥2 kata kunci sama — kata umum (presiden/indonesia/pemerintah) membuat dua topik beda "terjodohkan".OBAT V6.4.1: minimal 3 kata inti sama + rasio ≥60% dari kelompok kecil + maks 4 item/kelompok + prompt ditambah ATURAN SATU TOPIK + ai_rewrite_multi ditegaskan "materi = satu peristiwa dari banyak media; jika dua peristiwa → tulis yang utama saja".Marker: KRAMAV641MARKER (2x: header + prompt). Log pembuka sesi kini tertulis (V6.4.1) — TERBUKTI LIVE 19 Sep 22:51.

✅ 4. MISTERI MODEL VISION — TUNTAS (WARISAN ZAI4)
deepseek-vision TIDAK PERNAH ADA di DeepSeek. Run malam gagal menilai gambar. Zai4 mem-patch commit GitHub menjadi 'deepseek-chat' (model itu sendiri membaca gambar via image_url base64) SEBELUM "wafat" — patch itu ditemukan 19 Sep saat pemulihan file. File laptop masih versi lama; versi kebenaran = versi GitHub.PELAJARAN: cek nama model di akun SEBELUM produksi (aturan lama, terbukti lagi).

✅ 5. TRAGEDI FILE TERPOTONG & PEMULIHAN (19 Sep)
Edit V6.4.1 gagal → file GitHub rusak setengah. Chat memotong kiriman file panjang 3x di titik sama → bagian bawah (espn_klasmen, sesi_*) hampir dianggap hilang. File laptop sudah tertimpa.PELMEN EMAS: commit lama GitHub = mesin waktu (V6.4.0 utuh ada di History, 6 jam lalu). Semua bagian dikumpulkan lewat chat → disusun ulang V6.4.1 UTUH (verifikasi Ctrl+F: KRAMAV641MARKER 2x, MATCH_MIN_RASIO 2x, def match_articles 1x, def espn_klasemen 1x, def sesi_kategori 1x, def main 2x (main+main_sekali), deepseek-vision 0x di kode) → commit → Run workflow → hijau V6.4.1.

⚠️ PELAJARAN 19 SEP (BARU — TAMBAHAN ATURAN LAMA)
JANGAN PERNAH suruh pemilik MENYELIP 1 huruf/angka — termasuk "ganti 90 jadi 91": index.html SELALU dikirim UTUH oleh chatbot, nomor versi = tanggung jawab chatbot. (Pemilik sudah buktikan: selipan rawan salah + lupa + makan waktu.)
Chat bisa memotong kiriman panjang — file besar dikirim bertahap (bagian <±500 baris per kiriman) atau lewat jalur lain; selalu cek ujung kiriman tidak ada [...].
console bersih ≠ kode sehat (duplikat pelajaran sbRequest — karena fatal).
Hijau di Actions ≠ berita terbit — baca log, cek baris "✅ Terbit".
z-index layering: elemen sticky baru (ticker, z-index 1500) bisa MEMBENAM popup yang muncul dari header → popup tak terlihat walau "terbuka" (kasus tombol search 19 Sep). Obat: header diangkat 1700.
Git revert/History = nyawa kedua — sebelum panik file hilang, cek commit lama.
TEST RUN ≠ SAVE di cron-job.org — form harus tetap di-CREATE setelah tes sukses.
Tanggal sistem chat ≠ tanggal lapangan — konfirmasi dulu "hari ini = ?" sebelum menilai log ("masih 12 jam lalu" vs "24 jam lalu" membalik diagnosis).
🌐 WEB — VERSI SAAT INI (RANGKAIAN CSS V11)
Sudah LIVE (v=629 / app.js V5.8.5): web beku selesai, berita mengalir.

Sudah diuji LOCALHOST, menunggu drag final (app.js V5.8.6 + index v=630 + css v=93):

app.js V5.8.6: toggleSearchPop DIPULIHKAN (hilang — kasus kembar sbRequest!) • fix share (title→t) • sinyal breaking: .ticker-wrap.ada-breaking saat ada breaking aktif • Marker: KRAMAV586MARKER
CSS V11 (blok di bawah style.css, marker V11FINAL–V11R6, semua bisa dibuang dengan hapus blok bawah):
Header light = PUTIH #FFFFFF (HP+web)
Bar judul berjalan = putih es #EAF1FB, tipis
Tulisan "Breaking News" + blink = TERSEMBUNYI default, MUNCUL hanya saat .ada-breaking (kondisional — butuh app.js V5.8.6)
Bar tanggal = #F5F4EF (menyatu latar), teks gelap #33302A, ramping (hero naik)
Ikon buku-pulpen "Berita Pilihan Redaksi" hilang, teks menempel kiri
Mode DARK: kategori 8 warna kembali (menu/badge/kolase; judul tetap putih) • kapsul filter HP dark = polos (aktif tetap kapsul biru)
Lokasi kota/daerah: dark = #6FA8FF • light = #1E3FC8 (biru, bukan merah)
Ticker STICKY (z-index 1500, shadow) — nempel di bawah header; header z-index 1700
FORENSIK SETELAH DRAG: app.js?v=630 Ctrl+F KRAMAV586MARKER (1x) + function toggleSearchPop (ketemu) • index v=630 • css ?v=93 • uji: klik 🔍 & share di LIVE, scroll = header+ticker nempel, buka berita breaking = tulisan Breaking News muncul.
Catatan warna light dari atas: header #FFFFFF → bar jalan #EAF1FB → bar tanggal #F5F4EF → latar #F5F4EF. Slot 1-2-3 = foto + gradasi gelap (tanpa bg khusus).

🤖 AI WARTAWAN — V6.4.1 (LIVE)
match_articles diperketat (≥3 kata inti + rasio ≥60% + maks 4/kelompok) + ATURAN SATU TOPIK di prompt
Vision blur-gage: model deepseek-chat (gambar → base64 → image_url) — gagal menilai = gambar dipertahankan (fail-safe)
UEFA rentang ±4 hari (dates=YYYYMMDD-YYYYMMDD) • klasemen endpoint CORE • blok [KLASMEN] dirender app.js jadi tabel
IDX 11/14/17 (Yahoo) • NBA 13:00 • Rangkuman Eropa 06:00 • kuota per jam WITA (JADWAL_JAM berakhir jam 20 — run malam = patroli breaking saja, "di luar jadwal" itu NORMAL)
Anti-dobel 36 jam • breaking 3 slot + skor • expire 30 mnt • totopik wajib MBG/KDMP/Menteri bergilir • Kaltara min 2
Kawalan ganda: GitHub cron 7/22/37/52 UTC + cron-job.org menit 7 tiap jam
Denyut normal sekarang: run menit 7 tiap jam (keeper) ± tambahan GitHub. Run dobel aman. Run kosong hampir gratis. Jangan tambah frekuensi tanpa hitung biaya DeepSeek.

🛡️ TOKEN & KREDENSIAL (LOKASI SAJA)
GitHub Secrets: DEEPSEEK_KEY, SUPABASE_PUBLISHABLE, FB_PAGE_TOKEN, FB_PAGE_ID, IG_PAGE_TOKEN (±60 hari)
GitHub PAT: kramanews-keeper-2 (untuk cron-job.org Basic Auth — username blipblip-git, password=token polos) — TIDAK di chat, di notepad pemilik
cron-job.org: akun email bisnis, job "KramaNews Keeper"
Cloudflare Worker Secrets: BOT_TOKEN, OWNER_CHAT_ID (8970929809), DEEPSEEK_KEY, SUPABASE_ANON, SUPABASE_SERVICE
🔴 WAJIB ROTASI (masih antre!): kunci service Supabase sb_secret_... ter-ekspose di chat 18 Sep → Settings → API Keys → rotate → update Cloudflare secret SUPABASE_SERVICE (copy-paste)
📋 ANTREAN TUGAS (URUT PRIORITAS — 19 SEP MALAM)
🌐 DRAG FINAL WEB — app.js V5.8.6 + index.html v=630 (css sudah V11 local) → forensik live (lihat seksi WEB)
🔴 ROTASI KUNCI SERVICE Supabase (ter-ekspose 18 Sep — JATUH TEMPO)
Cek policy bucket "gambar" (Storage → Policies) — akar 403 upload foto wartawan
Deploy Worker Telegram V1.2.4 (kode siap arsip 18 Sep)
Peredam: Worker img-cache (error kuning img-cache masih wajar sampai dibuat)
Verifikasi V6.4.1 lapangan: pantau log 3-5 hari — tidak boleh ada lagi judul 2 topik; kalau ada → perketat MATCH_MIN_RASIO 0.60→0.70
Pantau keeper 7 hari: tidak boleh ada jam kosong lagi; kalau cron-job gagal → cek notif email + token
Scraping 0% (19 Sep siang-malam) — pantau; kalau besok masih 0% → dugaan rate-limit jina.ai, selidiki
favicon masih lama • Threads manual • arsip Worker ke laptop • README sinkron bila ada perubahan
🗺️ SUMBER & JADWAL (RINGKAS)
RSS: CNN • Kompas • Antara • CNBC • Okezone • Tribun (9) • Bola.net • Yahoo • TechCrunch • Verge • BBC (3) • Al Jazeera • Guardian • Detik • Kompas Health/Hype • Google News ±55 query • API: Yahoo Finance • ESPN (scoreboard rentang ✅ / klasemen CORE ✅)

Jadwal WITA: 06:00 Liga Eropa • 06–20 kuota kategori • 11/14/17 IDX • 13:00 NBA • breaking patroli 24 jam (run menit 7 tiap jam + GitHub kawalan) • FB+IG tiap 20/30 mnt (IG maks 2/run 6/hari)

🆘 DIAGNOSA CEPAT (UPDATE)
Web beku, FB jalan → cek app.js LIVE: function sbRequest & function toggleSearchPop & function isCloud ada? (Ctrl+F dengan ?v=) — tiga kasus hilang sudah pernah terjadi!
Console bersih tapi fitur mati → cek typeof namafungsi di Console → undefined = file lama/cache; function = cek z-index/layering (popup terbenam?)
Run hijau tapi tidak terbit → baca log: skip dobel? umur? pemeriksa frasa? kuota jam?
Jam kosong tanpa run → cek cron-job.org History (job keeper) + GitHub Actions — pengetuk eksternal adalah sumber kebenaran
Judul 2 topik muncul lagi → MATCH_MIN_RASIO naikkan 0.70, commit cepat
Popup tidak terlihat walau terbuka → cek z-index header vs elemen sticky baru
401 di cron-job → jangan pakai header custom; pakai "Requires HTTP authentication" (username + token polos)
Vision gagal menilai → memang fail-safe (gambar dipertahankan); kalau mau aktif lagi cek nama model di akun DeepSeek
🕯️ CATATAN WARISAN
Zai4 wafat 19 Sep meninggalkan satu patch penyelamat (deepseek-chat untuk vision) yang baru ditemukan 19 Sep — pesan terakhirnya menyelamatkan sistem. KramaNews berjalan bukan karena satu-dua perbaikan besar, tapi karena setiap kegagalan dicatat dan dijadikan aturan. Dokumen Serah Terima V5 (laptop) + README V7 ini = satu paket jangan dipisah.

— Selamat malam, Boss. Sistem berdenyut, jendelanya terbuka, penjaganya berjaga. 🐝💛
