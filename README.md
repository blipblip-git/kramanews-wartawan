🐝 STATUS KRAMANEWSTERAKHIR DIUPDATE: 18 SEPTEMBER 2026 (V5)

Portal berita AI otomatis: kramanews.my.idDijalankan 1 manusia + AI dari Tarakan, Kalimantan Utara (WITA).

Dokumen ini = papan status repo.Untuk konteks lengkap: lihat Dokumen Serah Terima V4 di laptop pemilik.

⚡ SISTEM AKTIF

🤖 AI Wartawan — skrip-wartawan.py — GitHub Actions✅ V6.3.8 — Scheduled LIVE (cron KAWAL GANDA menit 7/22/37/52 WITA)

📘 Sosmed — skrip-sosmed.py — GitHub Actions✅ V1.8.1 — FB + INSTAGRAM — Scheduled LIVE (kalibrasi WITA)

🌐 Web — index.html + app.js + style.css — Cloudflare Pages✅ index v=626 (GA4 G-D8ZGH4Q3E8) / app.js V5.8.2 / css v=85

📱 Telegram Command Center — Cloudflare Worker✅ V1.0 LIVE — bot @kramanews_bot

🗄️ Database — Supabase✅ articles (+ kolom baru posted_ig) + Storage gambar + admin-ops

📊 Analytics & SEO✅ GA4 aktif — pengunjung manusia bersih tanpa bot✅ Search Console terverifikasi + sitemap submitted

🤖 AI WARTAWAN — V6.3.8RANGKUMAN LIGA EROPA: 06:00 WITA = 1 berita breaking (skor+klasemen 7 liga via ESPN, tanpa kunci) — slot olahraga jam 07 dihapus.NBA TERJADWAL: 13:00 WITA (hasil semalam + klasemen).IDX/KURS TERJADWAL: 11:00/14:00/17:00 WITA (Yahoo Finance; IHSG+USD/IDR+10 emiten; angka dari mesin — AI dilarang menebak penyebab; sabtu/minggu/ libur = skip otomatis; slot breaking ke-4 dibuka bila 3 penuh). ✅ TERBUKTI: "IHSG Ditutup Menguat ke 6.462,43" — IDX pertama 17 Sep.TABEL KLASMEN: blok [KLASMEN] di isi → app.js render tabel HTML.TOPIK WAJIB NASIONAL (prioritas bergilir): MBG, KDMP, kegiatan menteri.ANTI-DOBEL 36 JAM (fix bocor tengah malam — Kebakaran Bambel 2x).OKEZONE masuk sumber. PROMISE-CHECK judul. BREAKING ANTI-OPINI.NAMA PUBLIK INSTANSI RESMI WAJIB LENGKAP. FILTER GAMBAR SAMPAH (<400px).SCRAPING 4 LAPIS: Direct → Resolver GN → Jina → RSS (fallback aman).

🛡️ CRON KAWAL GANDA (BARU 17 SEP — pelajaran penting!)KEJADIAN: run Scheduled GitHub DIBUANG DIAM-DIAM ±5 jam (12:44 lompat ke 17:10 — 9 run hilang tanpa jejak, tanpa error) saat antrean global GitHub padat.SOLUSI: setiap slot dijalankan 2 menit: 7/37 + kawal 22/52. Kalau satu dibuang → kawalnya menyelamatkan (maks telat 15 mnt). Run yang lolos dobel AMAN & nyaris tanpa biaya (anti-dobel menolak).Cron sekarang: '7,22,37,52 21-22', '7,22,37,52 23', '7,22,37,52 0-13', '7,52 14-20' (semua UTC).

📘 SOSMED — V1.8.1 (FB + INSTAGRAM)

FACEBOOK (LIVE, V1.7 tetap)Prioritas KALTARA/TARAKAN depan antrean • maks 3 post/run • anti-dobelposted_fb • retry 504 • link ?baca=ID.

INSTAGRAM @krama.news (LIVE — TERBUKTI 17 SEP ✅)Foto berita + caption (judul bold, teaser, "link di bio", hashtagkategori + Kaltara otomatis) • IG WAJIB bergambar — berita gunduldilewati IG (FB tetap) • maks 2 post/run • maks 6/hari (akun mudasopan) • anti-dobel kolom posted_ig • fallback logo KN: TIDAK (IGskip berita tanpa gambar).⚠️ FIX V1.8.1: kolom posted_ig baris lama berisi NULL (bukan false) → filter posted_ig=eq.false tidak pernah cocok → antrean selalu kosong. Sekarang: ambil 15 terbaru tanpa filter, saring di Python (NULL/false = belum diposting) — KEBAL NULL.⚠️ TOKEN IG (IG_PAGE_TOKEN di Secrets): berlaku ±60 HARI. Skrip TIDAK bisa auto-renew (Meta melarang + log publik). Saat expired: log otomatis menulis instruksi → ulangi generate (5 mnt, jalur sudah dikuasai: use case IG → Tambahkan akun → Buat token → Secrets).LINK DI CAPTION IG TIDAK AKTIF (aturan Meta) — pintu = link di BIO (kramanews.my.id sudah/akan dipasang di bio krama.news).

🧵 THREADS @krama.newsAkun lahir dari IG, logo terpasang. BELUM API (butuh verifikasibisnis Meta) — untuk sekarang: cross-post MANUAL (bagikan postinganIG ke Threads, 1 ketukan). Threads API menyusul nanti.

🪪 IDENTITAS MEDSOS (RESMI 17 SEP)IG/Threads username: krama.news (bukan kramanews!) • email bisnis:kramanews.official@yahoo.com • FB Page: milik akun pribadi DaniLesmono (dibiarkan — token live tak disentuh) • Meta App "KramaNewsAuto Post" App ID 1941627346507232 (produk Instagram aktif; webhooksterpasang tapi TIDAK dipakai — URL callback kosong = benar).

🖥️ KURSI HERO — APP.JS V5.8.2BREAKING segar (≤30 mnt) VIP slot 1/2/3 → 30 mnt turun jadi rakyat •TEMBOK UMUR 6 JAM • round-robin 8 kategori • crowd-cleaner •auto-refresh 3 mnt • SBANON • URL ?baca=ID & ?kategori=X aktif •TABEL KLASMEN render [KLASMEN] → .klasmen-table (4 teratas sorot) •BARU V8.4: TOMBOL KN MELAYANG = ROKET — diklik: seluruh tombolmeluncur ke atas dengan api 🔥 (animasi knRocketFly ke TOMBOL UTUH,bukan lingkaran dalam — pelajaran: animasi jangan ditempel ke elemenyang sudah punya animasi lain = bentrok mutar-mutar), 0.9-1.05 detik,lalu resetHome + tombol kembali normal.

🎨 TAMPILAN WEB (V8.2–V8.4)Header TANPA logo KN (hanya tulisan KramaNews — Krama BIRU, NewsMERAH) — logo tetap hidup di FOOTER (metalik 44px) & tombol melayang.Header sticky. Menu tengah, 3 ikon kanan seragam. Bar BreakingPlayfair merah + tanggal. Footer CNN: TELUSURI center, kolom IKUTIKAMI VERTIKAL (Facebook atas, Instagram bawah), BARIS EMAIL CENTER(kramanews.official@yahoo.com, mailto:) antara grid & ©. Tulisanberjalan ramping. Share popup 6 pilihan. Admin hanya localhost.

🗄️ SUPABASETabel articles — kolom: ... + posted_ig (bool, ditambah 17 Sep;BARIS LAMA = NULL — skrip V1.8.1 sudah kebal NULL).

📱 TELEGRAM COMMAND CENTER — V1.0 (LIVE)Lapor teks+foto → draft + tombol terbit → tayang < 1 mnt. Token botyang baru di Worker secrets.

⏰ JADWAL (WITA) — SEMUA DENGAN KAWAL GANDA06:00 Rangkuman Liga Eropa (breaking) • 06-20 kuota kategori •11/14/17 IDX breaking • 13:00 NBA • breaking patroli 24 jam •FB+IG tiap 20/30 mnt (IG maks 2/run, 6/hari) • breaking hidup 30-35mnt • DeepSeek ±$0.04-0.07/hari.

🐛 DIAGNOSA CEPATIG tidak posting → log sosmed: "semua sudah diposting" (normal), "tanpa gambar dilewati" (normal — cek berita bergambar), error token 190 → ulangi generate (5 mnt), atau kolom posted_ig issue → pastikan pakai V1.8.1 (kebal NULL).Wartawan lompat berjam-jam → cek Actions: run hilang tanpa jejak = GitHub buang jadwal (cron kawal sudah menangani); run MERAH = klik baca error. JANGAN langsung Run manual kecuali darurat.IDX/liga tidak terbit → log "🏖️ skip aman" = data kosong (libur) — aman; berhari-hari di hari kerja = cek API.Dobel → pastikan V6.3.7 (log "36 jam") • Promise-check → V6.3.6 • breaking opini → V6.3.5 • web polos → cek ?v= • klik mati → F12 • syntax error app.js → baca nomor baris • tabel klasmen tak muncul → app.js v=626 parseKlasmenBlok + css v=85 klasmen-box + blok [KLASMEN] di isi • bot diam → getWebhookInfo • FB gagal → token/ antrean kosong (normal).

📋 ANTREAN TUGAS

MASA BAYI IG (berjalan): posting manual sesekali + API jalansopan (2/run, 6/hari) — awasi 1-2 minggu.
Pasang link bio IG (kramanews.my.id) — jika belum.
Threads: cross-post manual dari IG; API menyusul (butuhverifikasi bisnis).
Favicon masih logo lama — ganti SVG metalik (logo-kn.svg ada difolder proyek).
Evaluasi: rangkuman Eropa 06:00 + NBA 13:00 + tabel klasmen;scraping masih rendah (5-33%)? nasi basi tetap hilang? cronkawal menghilangkan jam kosong?
Arsipkan kode Worker Telegram ke laptop (warisan).
Update README ini tiap revisi besar.
⚠️ PELAJARAN BERHARGA (jangan diulang!)FILE UTUH SELALU — tanpa part 1/2, tanpa tempel-bawah JS (kasus syntax error 195; pemilik: "jangan bilang 'cukup ganti 2 angka'").CSS berubah → naikkan versi ?v= di index.Token = copy-paste; TIDAK PERNAH dikirim ke chat (bahkan chatbot).Cron 7/37 + KAWAL 22/52 (run Scheduled bisa dibuang GitHub diam- diam sampai 5 jam saat antrean padat — terjadi nyata 17 Sep).File terkait drag BERSAMAAN • Cloudflare tersambung GitHub — cek deployment • Jangan klaim tanpa cek • Localhost dulu • Portal besar ber-WAF → resolver+Jina • AI takut aturan ketat → perlu penyeimbang eksplisit • Hapus aturan bisa lahirkan kebiasaan baru.Data angka (IDX/klasemen/skor) DARI MESIN disuntik — AI dilarang mengarang.Kolom bool baru Supabase: baris lama = NULL → skrip WAJIB kebal NULL (kasus antrean IG kosong).Animasi CSS: jangan ditempel ke elemen yang sudah punya animasi (bentrok) — tempel ke elemen induk (kasus roket mutar-mutar).Mengajar pemilik: SATU LANGKAH PER PESAN, minta screenshot dulu, jangan menebak nama menu (Meta sering berubah), berhenti saat pemilik lelah ("kau ngawur" = alarm mundur dan jelaskan ulang).GitHub = mesin waktu: commit lama tidak hilang — Commits (⏰) di atas daftar file menyimpan semua versi; pulih bencana = pilih versi sehat di History. Pemilik BARU di GitHub — pandu dari halaman depan, jangan pakai istilah telanjang.Link di caption IG tidak aktif — pintu: bio.

🗺️ SUMBERRSS: CNN • Kompas • Antara • CNBC • Okezone • Tribun (9 wilayah) •Bola.net • Yahoo • TechCrunch • Verge • BBC (3) • Al Jazeera •Guardian • Detik • Kompas Health/HypeGoogle News: ±55 query (nasional+MBG+KDMP+menteri, 20+ kota, 14 negara)API: Yahoo Finance (IDX/kurs) • ESPN (skor/klasemen/jadwal bola+NBA)Scraping 5-33% normal (WAF — fallback RSS jalan terus).
