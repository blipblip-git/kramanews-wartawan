STATUS KRAMANEWS — TERAKHIR DIUPDATE: 16 SEPTEMBER 2026
══════════════════════════════════════════════════════
AI WARTAWAN KRAMANEWS — V6.3.1 (SCRAPING ARTIKEL ASLI)
Baru V6.3.1 (UPGRADE TERBESAR — permintaan pemilik):
• SCRAPING ARTIKEL ASLI: sebelum AI menulis, sistem membuka
halaman artikel sumber (link RSS), mengambil ISI PENUH artikel
(bukan cuma ringkasan RSS 2-3 kalimat).
• AI kini membaca MATERI KAYA: jadwal laga/acara, kutipan
narasumber, angka lengkap — semua terangkat ke berita.
• ATURAN JADWAL & ACARA: tanggal event di dalam berita (laga,
acara mendatang) wajib konkret jika tertulis di sumber;
frasa relatif sumber ("pekan ini") disalin apa adanya.
• ATURAN ANTI-PLAGIAT: tulis ulang dengan kalimat sendiri,
dilarang menyalin verbatim lebih dari 5 kata berurutan.
• FALLBACK AMAN: scraping gagal (portal blokir/lambat) →
otomatis kembali ke ringkasan RSS — sistem tidak pernah mati.
V6.3 (sebelumnya): TANGGAL PUBLIKASI RSS disuntik ke prompt;
frasa "belum dikonfirmasi waktu pasti kejadian" DILARANG +
dipolisikan ai_write (berita diblokir jika lolos); narasumber:
nama ada = wajib dikutip, tidak ada = fakta langsung tanpa
atribusi kosong; PANJANG MENGIKUTI MATERI (target_kata).
V6.2: fix AI menolak breaking valid ("tidak ada tanggal").
Marker verifikasi: cari kata "KRAMAV631MARKER"
Mode 1 (loop 30 menit) : python3 skrip-wartawan.py
Mode 2 (GitHub Actions): python3 skrip-wartawan.py --sekali
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
ZONA WAKTU: WITA (UTC+8) — KALIBRASI V6.4
• Seluruh sistem berjalan dalam waktu TARAKAN (WITA)
• skrip-wartawan.py: WITA = timezone(timedelta(hours=8))
• JADWAL_JAM: kuota kategori jatuh tepat jam WITA
• wartawan.yml: cron dikalibrasi WITA (menit 7 & 37)
• app.js: tanggal header + jam berita label WITA
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
WEB — APP.JS V5.6 (KURSI HERO SETARA + TEMBOK UMUR)
Baru V5.6 (perbaikan nasi basi):
• TEMBOK UMUR 8 JAM: hanya berita umur <=8 jam boleh masuk
slot 1/2/3 hero. Berita lebih tua (termasuk eks-breaking,
kasus nyata: Musik Daul Pamekasan umur 24 jam) GUGUR permanen
dari panggung utama — anti nasi basi.
• EKS-BREAKING = RAKYAT BIASA: setelah 30 menit di tahta,
breaking jatuh jadi rakyat, masuk EKOR antrean (paling
belakang) — praktis tak pernah kebagian lagi. Sistem blokir
3 jam versi V5.5 DIBUANG (malah menciptakan izin kembali).
• ROUND-ROBIN 8 kategori: pengisi slot = terbaru tiap kategori
bergantian (N→D→I→E→O→T→H→K) — semua kategori kebagian.
• DARURAT rapi: jika tak ada berita <=8 jam, hero menampilkan
terbaru tersedia urut terbaru, tanpa keistimewaan.
V5.5: breaking VIP 30 menit; V5.4: crowd-cleaner (browser
pengunjung mencabut flag breaking >35 mnt langsung ke DB —
terbukti jalan: 🧹 flag #958 dicabut umur 55 mnt);
V5.3: SBANON kebal dua nama kunci (fix crash SUPABASE_ANON).
Falsafah pemilik: "manusia kebanyakan hanya melihat ke
permukaan" — hero adalah etalase, harus selalu segar.
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
WEB — INDEX.HTML V6.2 (style.css?v=74, app.js?v=610)
• TANGGAL pindah dari header ke bar hitam Breaking News
(struktur: tl-top = lampu + teks; tl-date = tanggal)
• HP: Breaking News tengah baris 1, tanggal tengah baris 2
• Desktop: Breaking News + tanggal sejajar tengah
• BREAKING NEWS: font Playfair Display 16px, merah #E11D2E
tepi putih 8 arah, lampu kedip cincin PUTIH
• Header: logo KN 38px + KramaNews 24px KIRI, menu kategori
TENGAH (grid auto|1fr|auto), 3 ikon KANAN
• Footer gaya CNN: logo circle gaya header 44px + KramaNews
30px; TELUSURI center (8 kategori, 4x2); IKUTI KAMI kanan
(tombol Facebook teks); kolom Perusahaan & Legal DIHAPUS
• Footer dirampingkan; Masuk Admin HANYA di localhost
(script deteksi hostname → body.is-publik → CSS sembunyikan)
• Tombol KN melayang HP bottom 160px; Back bottom 36px
• Popup share 6 pilihan (WA/FB/IG/Threads/X/Copy Link)
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
TELEGRAM COMMAND CENTER — V1.0 (LIVE & TERUJI)
Flow: Laporan + Foto → AI rapikan → Draft + Tombol
[🚨 Terbit BREAKING] [📰 Terbit Biasa] [✏️ Revisi] [❌ Batal]
• Keamanan: hanya OWNER_CHAT_ID yang dilayani
• Foto → Supabase Storage bucket "gambar" (public)
• Revisi: instruksi chat berikutnya diproses AI
• Slot breaking penuh → bot tawarkan ganti terlama
• Terbukti: lapor → tayang < 1 menit di slot breaking
• Token bot: SUDah DIREVOKE & diganti (keamanan)
• Webhook: kramanews-telegram.denytriono-btm.workers.dev
• KV: KRAMANEWS_DRAFTS (binding DRAFTS)
══════════════════════════════════════════════════════
✅ FB AUTO-POST: AKTIF & TERVERIFIKASI (15/08/2026)!
══════════════════════════════════════════════════════
KRAMANEWS — SKRIP SOSMED V1.7 (PRIORITAS KALTARA/TARAKAN)
• Berita KALIMANTAN UTARA (Tarakan, Nunukan, Bulungan, Malinau)
selalu DIPRIORITASKAN paling depan antrean FB
→ berita daerah terdepan update-nya di Facebook Page
• Tetap: maks 3 post per run (anti spam FB), anti-dobel posted_fb,
retry 504, link ?baca=ID, caption optimal
• Cron: tiap 20 mnt jam sibuk / tiap 30 mnt jam tenang (UTC)
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
JADWAL & INFRASTRUKTUR
• GitHub Actions: repo blipblip-git/kramanews-wartawan (PUBLIC)
• Wartawan: cron menit 7 & 37 (BUKAN 0/30 — menit padat global,
run sering dibuang GitHub); ramai tiap 30 mnt, malam tiap 60 mnt
• Sosmed: tiap 20 mnt jam sibuk / 30 mnt jam tenang
• Hosting: Cloudflare Pages kramanews.my.id (Rumahweb domain)
• Database: Supabase articles (Edge Function admin-ops)
• DeepSeek: saldo ~$2 — hemat, scraper menambah pemakaian sedikit
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
ANTRIAN / TUGAS BELUM SELESAI
1. PERBAIKAN GAMBAR (Level 1): filter URL gambar sampah
(logo/icon/banner/ads/ukuran kecil) di get_image/insert_news
→ langsung pakai Wikimedia via deskripsi_gambar AI.
Level 2 (opsional): verifikasi AI Vision skor relevansi.
2. Pantau run Scheduled menit 7/37 tetap rutin
3. Evaluasi 1-2 hari: jadwal laga/tanggal event sudah konkret?
4. Update dokumen serah terima (V3 sudah ada di tangan pemilik)
══════════════════════════════════════════════════════
══════════════════════════════════════════════════════
PELAJARAN BERHARGA (jangan diulang!)
1. File revisi = SELALU FILE UTUH (kasus v=511 web crash)
2. CSS berubah → WAJIB naikkan versi di index.html
(kasus: HP tidak berubah sama sekali)
3. Token = copy-paste, jangan ketik (kasus 401 Unauthorized)
4. Cron jangan menit 0/30 (padat global — run dibuang)
5. Drag file terkait BERSAMAAN (index+app.js)
6. Cloudflare Pages tersambung GitHub — deploy bisa menimpa drag
7. Jangan klaim "tidak berpengaruh" tanpa cek kode
(kasus: blokir 3 jam ternyata menciptakan izin kembali)
8. Kerjakan di localhost → verifikasi → sekali drag online
