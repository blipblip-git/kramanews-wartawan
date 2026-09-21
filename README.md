# ══════════════════════════════════════════════════════
#  PART 1 — README V8
# ══════════════════════════════════════════════════════

🐝 STATUS KRAMANEWS — TERAKHIR DIUPDATE: 21 SEPTEMBER 2026 (V8)
Portal berita AI otomatis: kramanews.my.id
Dijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status teknis repo. Untuk filosofi & cara kerja
dengan pemilik: baca WARISAN.md (laptop pemilik). Satu paket.

════════════════════════════════════════════
⚡ SISTEM AKTIF (VERSI SAAT INI)
════════════════════════════════════════════

🤖 AI WARTAWAN — skrip-wartawan.py — V6.5.2 — GitHub Actions LIVE
   Struktur file: PART 1 / 2 / 3A / 3B / 4A / 4B berpembatas
   (# PART X ... # AKHIR PART X — marker tertanam di file)
   SENTINEL VERSI di baris paling bawah file:
   FILE_VERSI + FILE_PART_AKHIR — dibaca cek_versi.py tiap run
   (step "Cek versi & struktur file" di wartawan.yml, hasil di
   baris awal log: "✅ Struktur OK — versi ... di PART ...")
   Naik versi = cukup kirim ulang PART TERAKHIR dengan string baru.
   Marker forensik (Ctrl+F):
   KRAMAV642(2x) 643(5x) 6431(2x) 6432(2x) 6433(2x) 6434(2x)
   644(3x) 65(3x) 651(3x) 651B(2x) 652(5x) 652B(1x) 652C-REV(1x)
   652D(1x PART2 log detail Jina) 652E(1x retry koneksi terpisah)
   652B(1x PART3B fungsi teknologi dipulihkan)

📘 SOSMED — skrip-sosmed.py — V1.8.1 — FB+IG LIVE
🌐 WEB — index.html v=103 + app.js V5.9.1 (v=633) + style.css
   V16.9 (v=104) — Cloudflare Pages
   Fitur: dark navy serata (V16.8), sumber berita tercantum di
   halaman baca (KRAMASOURCEV591), back pojok bawah kanan HP
   (bottom:60 right:15), logo footer = KN Home (teks 20px),
   Paling Buzz maks 2/kategori (KRAMAV59), mesin cari multi-kata
   server-side (KRAMASEARCHV171, di index.html)
📱 TELEGRAM — Cloudflare Worker V1.1 LIVE
   V1.2.4 = cadangan (foto-menunggu + dual-header upload +
   diagnostik error). Deploy HANYA kalau V1.1 bermasalah. File
   di arsip laptop. Jangan deploy buta.
🗄️ DATABASE — Supabase articles + Storage "gambar" + admin-ops
📊 GA4 G-D8ZGH4Q3E8 • Search Console TERINDEKS (email "mulai
   mengumpulkan tayangan" 17 Sep 2026 = tahap 2 SEO tercapai!)

════════════════════════════════════════════
✅ SELESAI 19-21 SEP (ARSIP — JANGAN DIBONGKAR)
════════════════════════════════════════════

✅ WEB BEKU (sbRequest hilang) → pelajaran: console bersih ≠
   kode sehat; cek fungsi di file live dengan ?v=
✅ GITHUB BUANG RUN → keeper cron-job.org (Basic Auth, token
   kramanews-keeper-2 di notepad pemilik)
✅ JUDUL FRANKENSTEIN → match ≥3 kata inti + rasio 60% + maks 4
✅ VISION MODEL → deepseek-chat (deepseek-vision tak pernah ada)
✅ FILTER GAMBAR ANTI-HUMAN+HEWAN V6.5.1 3 LAPIS:
   (1) prompt contoh salah + wildlife/wolf eksplisit,
   (2) wikimedia: nama-file hewan diblokir (KATA_HEWAN_FILE),
   (3) vision: hewan APAPUN = skor maks 3, manusia maks 3,
       + CEK RELEVANSI JUDUL (tak nyambung = 1-4)
   Bukti lapangan: vision 1/10 & 2/10 & 3/10 DIBUANG berulang
✅ PEMERIKSA DATELINE V6.4.3.1: kota wajib ada di materi (blok
   "Benuanta" karangan); wilayah generik bebas; penjaga Kaltara
✅ ANTI-DOBEL-6JAM: 2 kata inti sama dlm 6 jam = tolak
✅ KOREKSI MANDIRI V6.5.3 (KRAMAV652C-REV/652E):
   frasa terlarang → retry 1x temp 0.3;
   DATELINE salah → retry 1x DENGAN MATERI ASLI DISERTAKAN
   (kasus "gaza" halusinasi karena koreksi buta — fixed);
   retry koneksi TIDAK makan slot koreksi (counter terpisah
   maks 2). Bukti: KLU & Korea Utara & frasa dikabarkan lolos
✅ KESEHATAN PERPUTARAN DOMAIN V6.4.4: 8 domain, slot 10/15/20
   = +0/+1/+2, geser 3/hari. Log: "🏥 KESEHATAN hari ini..."
✅ TEKNOLOGI PERPUTARAN DOMAIN V6.5: 6 domain (Gadget/AI/
   Aplikasi/Startup/Keamanan/Inovasi), slot 08/13/18 = +0/+1/+2,
   geser 2/hari, weekend libur jalan terus. ATURAN KEDALAMAN
   per domain (gadget spesifikasi+harga 2 halaman, AI dunia 2
   halaman, dsb). Log: "💻 TEKNOLOGI hari ini..."
   V6.5.2: fungsi teknologi dipulihkan (KRAMAV652B — hilang
   saat restrukturisasi 4A; pelajaran: restrukturisasi part =
   audit fungsi yang direferensikan!)
✅ OLAHRAGA V6.5.2 RESTRUKTURISASI:
   - Rangkuman Malam 00:00 DIHAPUS (bug zona waktu UTC vs WITA)
   - Rangkuman Liga Eropa 07:00 tetap (data ESPN)
   - RANGKUMAN OLAHRAGA UMUM BARU jam 11:00 (KRAMAV652):
     sumber A+B (portal besar + query event besar), WAJIB lolos
     FILTER REGIONAL (KATA_REGIONAL_OLAHRAGA: indonesia/timnas/
     badminton/voli/IBL/asean/dll) — adieu "Purdy Washington"
   - Olahraga: 07, 11, 13, 17, 20 (5x) — slot 15 diberikan ke
     teknologi+kesehatan (keputusan pemilik)
✅ PALING BUZZ BERAGAM V5.9: maks 2/kategori (KRAMAV59)
✅ MESIN CARI V17.1: multi-kata server-side seluruh artikel
   (KRAMASEARCHV171, di index.html)
✅ SUMBER BERITA TERcantum V5.9.1: "📰 Sumber asli: [media]"
   di halaman baca (KRAMASOURCEV591) — TANPA baris utk:
   ESPN Data/Malam, Pelaporan Wartawan, IDX/Yahoo, kosong.
   Berlaku surut ke seluruh arsip (source_name sudah ada dari awal)
✅ BREAKING DUNIA 11 SUMBER: +Al Jazeera +AP News +France24
   +4 portal Asia (The Star/Bangkok Post/Straits Times/Vietnam
   News) — Guardian bukan lagi satu-satunya raksasa breaking
✅ EKONOMI 14 SUMBER: +CNBC World +Investing.com
✅ TAMPILAN HP V16.9: header 4 baris, header krem #F5F4EF,
   dark NAVY serata #1E3A5C (V16.8 — bukan hitam lagi),
   ticker biru-es light #D9E6F6 / navy gelap dark, ikon 25x25,
   tanggal 13px HP / 14px desktop, back pojok bawah kanan
   (bottom:60 right:15 — hasil tuning pemilik), logo footer
   KN 20px = KN Home
✅ DOMAIN GRETONG: Pexels API terdaftar (kunci di GitHub
   Secrets: PEXELS_API_KEY) — belum terpasang di kode (tunggu
   fitur foto topikal, lihat ANTREAN)

# AKHIR PART 1 — README V8

════════════════════════════════════════════
🚨 ANTREAN TUGAS (URUT PRIORITAS — 21 SEP MALAM)
════════════════════════════════════════════

1. PANTAUAN PAGI 22 SEP:
   • Run 11:07 — RANGKUMAN OLAHRAGA UMUM PERTAMA! (baris
     "🏆 RANGKUMAN OLAHRAGA UMUM TERJADWAL" + "Filter regional:
     X → Y kandidat lolos" + terbit?)
   • Run 13:07 — TEKNOLOGI domain "AI & Kecerdasan Buatan"
     (perputaran geser: 21 Sep = Inovasi+Sains, 22 Sep =
     Gadget 08 / AI 13 / Aplikasi 18)
   • Run 20:07 — kandidat olahraga RSS harus lolos FILTER
     REGIONAL (tak ada lagi "Purdy Washington")
2. SCRAPING 0-10% — DIAGNOSA TUNTAS 21 Sep:
   AKAR: link Google News format baru (CBMi...) TIDAK BISA
   diurai resolusi_link_google → Jina diminta scrape link
   redirect → HTTP 403 (diblokir Google). YANG SUKSES =
   feed RSS langsung portal (Tribun/Antara/Detik).
   JINA TIDAK BERMASALAH — dia cuma korban.
   SOLUSI KANDIDAT (pilih saat sesi baru, jangan buru-buru):
   a) Kurangi ketergantungan GN query → perbanyak RSS
      langsung portal di HUNT (sebagian besar daerah/nasional
      sudah RSS langsung — hitung ulang mana GN yang bisa
      diganti RSS portal)
   b) Parser link CBMi baru (proyek besar, rapuh — Google
      bisa ubah lagi)
   c) Terima: berita via GN query cukup ringkasan RSS
      (kualitas turun dikit tapi tetap terbit)
3. FIX KECIL DITUNDA (siap dieksekusi sesi baru):
   a) Koreksi dateline = menyertakan materi asli di pesan
      koreksi (kasus "philippines" gagal 2x karena koreksi
      buta — AI tak lihat materi) — PART 3B
   b) Retry koneksi (ConnectionReset 104) TIDAK memakan slot
      koreksi — counter terpisah — PART 3B
   c) Log detail Jina (HTTP/pendek/timeout per URL) — PART 2
   d) Bukti perlu: koreksi dateline buta di log 09:01 & 09:18
4. Views (👁) di beranda: feed+hero+buzz, angka ringkas,
   desktop+HP (data views_count SUDAH ADA di Supabase, tinggal
   render app.js) — menunggu konfirmasi final pemilik
5. FILTER KATEGORI di panel admin + PANEL RESPONSIF HP
   (tombol 44px, form 1 kolom, daftar kartu) — panel admin
   HP sudah bisa dibuka (footer → Masuk Admin), tinggal
   nyaman-kan
6. Foto tokoh (Prabowo dll): bank foto lokal sendiri di
   Supabase Storage folder tokoh/ (isi manual sekali, sistem
   tinggal match nama di judul) — otomatis legal 100%
7. Token IG ±60 hari — cek expiry berkala
8. Threads manual • favicon baru (KN logo) • arsip Worker ke laptop
9. String versi PART 4B masih benar V6.5.2 — kalau ada revisi
   berikutnya yang menyentuh PART 4B, naikkan sekalian
10. README sinkron tiap perubahan — revisi cukup 1 PART

════════════════════════════════════════════
📜 ATURAN KERJA (WAJIB — PELAJARAN MAHAL)
════════════════════════════════════════════

1. FILE BERSERI = PART BERPEMBATAS: "# PART X" (py) /
   "// PART X" (js) / "<!-- PART X -->" (html) WAJIB TERTANAM
   DI DALAM blok kode + "# AKHIR PART X" di ujung tiap part.
   Marker di luar blok = TIDAK SAH (tidak ikut ter-copas).
2. **PEMETAAN METODE REVISI PER FILE** (bukti 21 Sep):
   skrip-wartawan.py (~2600 baris) = PART berpembatas WAJIB;
   app.js (~374 baris) = UTUH; index.html = UTUH; style.css =
   TEMPEL blok bermarker di paling bawah (cascade aman) +
   HAPUS blok lama yang digantikan; WARISAN/README = utuh
   atau 1-2 part.
3. IZIN DULU sebelum membuat file apa pun.
4. PEMILIK TIDAK MENYELIP ANGKA/HURUF — chatbot kirim utuh/
   part. KECUALI: edit 1 kata/angka di lokasi yang PEMILIK
   SUDAH temukan sendiri via Ctrl+F (kasus jam 11 olahraga
   21 Sep) — kecuali chatbot menawarkan kirim utuh.
5. "OK/GAS/LANJUT" = jalan. Jangan tunggu format khusus.
6. Revisi CSS: ubah blok → review dulu di laptop (F12 →
   Ctrl+Shift+M mode HP) → baru naik versi + drag SEKALI.
   Jangan naik versi per iterasi.
7. Fix konflik CSS di SUMBERNYA, jangan tumpuk override.
8. Naikkan ?v= setiap css/js berubah (cache HP = musuh berulang).
9. Drag index+css+js BARENG (versi saling kunci).
10. Git History = mesin waktu. Hijau ≠ terbit (baca log).
    Console bersih ≠ kode sehat.
11. **EVALUASI KESEIMBANGAN SUMBER SEBELUM commit** (kasus:
    breaking dunia Guardian-dominan baru disadarakan SETELAH
    run — seharusnya ditawarkan kandidat sumber setara
    SEBELUM). Saat menyusun daftar sumber: tawarkan kandidat
    setara (Al Jazeera/AP/France24/dst) sejak awal.
12. **Minta screenshot saat gejala visual ambigu** (kasus
    tombol Back: salah diagnosa 2x karena tidak minta gambar).

════════════════════════════════════════════
🔑 KREDENSIAL & INVENTARIS BIAYA (LOKASI SAJA)
════════════════════════════════════════════

GitHub Secrets: DEEPSEEK_KEY, SUPABASE_PUBLISHABLE,
FB_PAGE_TOKEN, FB_PAGE_ID, IG_PAGE_TOKEN, **PEXELS_API_KEY (baru!)**
Cloudflare Worker Secrets: BOT_TOKEN, OWNER_CHAT_ID (8970929809),
DEEPSEEK_KEY, SUPABASE_ANON, SUPABASE_SERVICE
GitHub PAT: kramanews-keeper-2 (cron-job.org Basic Auth)
cron-job.org: job "KramaNews Keeper" (email bisnis)

BIAYA NYATA (filosofi gretong — lihat WARISAN.md poin 12):
1. 🔴 DOMAIN kramanews.my.id — Rp23rb/TAHUN — Registrar:
   RUMAHWEB — EXPIRED: 12 SEPTEMBER 2027
   ⚠️ ZAI WAJIB MENGINGATKAN PEMILIK MULAI 12 AGUSTUS 2027
   (1 bulan sebelum jatuh tempo). Kalau domain hangat =
   situs mati total meski semua sistem jalan!
2. 🟡 DeepSeek API — per panggilan AI (satu-satunya biaya
   operasional harian)
SISANYA SEMUA Rp0: GitHub Actions, Cloudflare, Supabase,
RSS, ESPN/Yahoo, Wikimedia, Pexels, Search Console/GA4.

════════════════════════════════════════════
🆘 DIAGNOSA CEPAT (UPDATE)
════════════════════════════════════════════

• Cek versi live: buka skrip-wartawan.py di GitHub → scroll
  paling bawah → SENTINEL (FILE_VERSI). Jangan pakai log
  Actions (bisa tertinggal 1 revisi)
• Log run diawali "✅ Struktur OK" = sentinel sehat
• Log "⚠️ PERINGATAN: file TIDAK diakhiri..." = part terakhir
  melenceng / sentinel pindah — cek ujung file SEBELUM run
  berikutnya
• "⛔ dateline tidak ada di materi" berulang di kandidat yang
  sama → AI bandel menerjemahkan nama kota → koreksi mandiri
  dateline akan menolong (sudah ada sejak V6.5.2C-REV)
• "🔁 Koreksi mandiri..." di log = sistem mengoreksi AI (bukan
  kegagalan — itu fitur)
• Run kosong "di luar jadwal produksi" = NORMAL (run malam =
  patroli breaking saja)
• Anti-dobel menolak kandidat yang sama berulang = slot bolong
  hari itu NORMAL — besok kandidat baru, jangan panik
• Fitur tidak muncul padahal kode sudah commit → cek log run
  PERTAMA setelah commit: apakah ada error import/function
  not defined (kasus ai_rewrite_teknologi hilang saat
  restrukturisasi 4A — pelajaran: audit fungsi yang
  direferensikan saat memecah/menggabung part)

# AKHIR PART 2 — README V8 SELESAI
