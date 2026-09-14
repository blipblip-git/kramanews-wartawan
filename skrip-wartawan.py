# ══════════════════════════════════════════════════════
#  AI WARTAWAN KRAMANEWS — V5.2 (BUG FIX `waktu` + NARASUMBER + ANGKA + GAMBAR)
#  Baru V5.2:
#   • FIX BUG: insert_news() sekarang MENERIMA parameter `waktu`
#   • Tetap: narasumber bernama wajib, angka utuh, gambar cerdas
#   • Tetap: breaking diperluas, gempa ≥5 SR saja
#  Mode 1 (shift 24 jam)  : python3 skrip-wartawan.py
#  Mode 2 (sekali jalan)  : python3 skrip-wartawan.py --sekali
# ══════════════════════════════════════════════════════

import requests
import json
import time
import re
import os
import sys
import random
import feedparser
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

DEEPSEEK_KEY         = os.environ.get('DEEPSEEK_KEY', '')
SUPABASE_PUBLISHABLE = os.environ.get('SUPABASE_PUBLISHABLE', '')

SUPABASE_URL = 'https://imcvijgytdjjpotlaltv.supabase.co'
REST_URL     = SUPABASE_URL + '/rest/v1/articles'
EDGE_URL     = SUPABASE_URL + '/functions/v1/admin-ops'
AUTHOR_NAME  = 'DT'

WIB = timezone(timedelta(hours=7))
SCHEDULE_JAM = list(range(24))

# ═══ JADWAL 24 JAM — KUOTA PER JAM (dari V5.1) ═══
JADWAL_JAM = {
    0:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
    1:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 2},
    2:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
    3:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
    4:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
    5:  {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 2, 'kesehatan': 2},
    6:  {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 3, 'kesehatan': 2},
    7:  {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'teknologi': 3, 'kesehatan': 1},
    8:  {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 3, 'kesehatan': 3},
    9:  {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'kesehatan': 3},
    10: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 2, 'kesehatan': 1},
    11: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'teknologi': 3, 'kesehatan': 2},
    12: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 2, 'teknologi': 1},
    13: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'kesehatan': 3},
    14: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 1, 'kesehatan': 2},
    15: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 3, 'kesehatan': 2},
    16: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'teknologi': 3, 'kesehatan': 2},
    17: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 3, 'kesehatan': 2},
    18: {'nasional': 3, 'daerah': 5, 'internasional': 3, 'ekonomi': 3, 'olahraga': 3, 'teknologi': 2},
    19: {'nasional': 3, 'daerah': 3, 'internasional': 3, 'ekonomi': 3, 'kesehatan': 3, 'olahraga': 2},
    20: {'nasional': 3, 'daerah': 3, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3, 'kesehatan': 2},
    21: {'nasional': 3, 'daerah': 3, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3, 'teknologi': 2},
    22: {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
    23: {'nasional': 3, 'daerah': 2, 'internasional': 5, 'ekonomi': 3, 'olahraga': 3},
}

# ═══ BREAKING CERDAS (V5.1) — SEMUA SELEVEL, TIDAK PRIORITAS GEMPA SAJA ═══
BREAKING_KEYWORDS = [
    'gempa', 'earthquake',
    'kapal tenggelam', 'feri tenggelam', 'kapal karam', 'perahu tenggelam',
    'pesawat jatuh', 'pesawat hilang', 'kecelakaan pesawat', 'pesawat tergelincir',
    'ferry sinks', 'boat sinking', 'plane crash', 'plane missing',
    'tsunami', 'banjir besar', 'banjir bandang', 'longsor', 'tanah longsor',
    'erupsi', 'gunung meletus', 'kebakaran hutan', 'karhutla',
    'kebakaran hebat', 'keracunan massal', 'keracunan', 'angin puting beliung',
    'tsunami warning', 'flood', 'volcano eruption', 'wildfire',
    'hurricane', 'typhoon', 'landslide', 'mass poisoning',
    'ott kpk', 'ditangkap kpk', 'tersangka korupsi', 'tertangkap tangan',
    'pembunuhan', 'dibunuh', 'pejabat dibunuh', 'pejabat ditemukan mati',
    'perampokan besar', 'rampok bank', 'perampokan bersenjata',
    'assassination', 'murder', 'bank robbery', 'armed robbery',
    'killed', 'explosion', 'attack', 'bomb', 'missile', 'airstrike',
    'corruption arrest', 'major robbery', 'arrested',
    'demo besar', 'unjuk rasa besar', 'demonstrasi besar',
    'massive protest', 'huge demonstration',
    'presiden meresmikan', 'wapres meresmikan', 'peresmian proyek besar',
    'proyek strategis nasional', 'groundbreaking',
    'president inaugurates', 'president opens',
]

# Gempa harus ≥5 SR untuk masuk breaking
GEMPA_MIN_MAGNITUDE = 5.0

KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata', 'amal', 'kayu putih']

def GN(q, lang='id', label=None):
    if lang == 'en':
        url = 'https://news.google.com/rss/search?q=' + quote_plus(q) + '&hl=en-US&gl=US&ceid=US:EN'
    else:
        url = 'https://news.google.com/rss/search?q=' + quote_plus(q) + '&hl=id&gl=ID&ceid=ID:id'
    return {'url': url, 'source': label or ('Google News: ' + q), 'gn': True}

def RSSF(url, source):
    return {'url': url, 'source': source, 'gn': False}

HUNT = {
    'nasional': [
        RSSF('https://www.cnnindonesia.com/nasional/rss', 'CNN Indonesia'),
        RSSF('https://nasional.kompas.com/rss', 'Kompas Nasional'),
        RSSF('https://www.antaranews.com/rss/nasional', 'Antara'),
        GN('pemerintah indonesia', 'id', 'Google News Nasional'),
        GN('dpr indonesia', 'id', 'Google News Nasional'),
        GN('Prabowo Subianto', 'id', 'Google News Presiden Prabowo'),
        GN('Gibran Rakabuming', 'id', 'Google News Wapres Gibran'),
    ],
    'daerah': [
        RSSF('https://kaltara.tribunnews.com/rss', 'Tribun Kaltara'),
        RSSF('https://kaltim.tribunnews.com/rss', 'Tribun Kaltim'),
        RSSF('https://jatim.tribunnews.com/rss', 'Tribun Jatim'),
        RSSF('https://jateng.tribunnews.com/rss', 'Tribun Jateng'),
        RSSF('https://jabar.tribunnews.com/rss', 'Tribun Jabar'),
        RSSF('https://dki.tribunnews.com/rss', 'Tribun DKI Jakarta'),
        RSSF('https://sumut.tribunnews.com/rss', 'Tribun Sumut'),
        RSSF('https://sumsel.tribunnews.com/rss', 'Tribun Sumsel'),
        RSSF('https://sulsel.tribunnews.com/rss', 'Tribun Sulsel'),
        GN('Tarakan', 'id', 'Google News Tarakan'),
        GN('Kaltara', 'id', 'Google News Kaltara'),
        GN('Surabaya', 'id', 'Google News Surabaya'),
        GN('Semarang', 'id', 'Google News Semarang'),
        GN('Bandung', 'id', 'Google News Bandung'),
        GN('Medan', 'id', 'Google News Medan'),
        GN('Makassar', 'id', 'Google News Makassar'),
    ],
    'internasional': [
        RSSF('https://feeds.bbci.co.uk/news/world/rss.xml', 'BBC World'),
        RSSF('https://www.aljazeera.com/xml/rss/all.xml', 'Al Jazeera'),
        RSSF('https://www.theguardian.com/world/rss', 'The Guardian'),
        RSSF('https://www.cnnindonesia.com/internasional/rss', 'CNN Indonesia'),
        GN('china politics', 'en', 'Google News China'),
        GN('malaysia politics', 'en', 'Google News Malaysia'),
        GN('uk politics', 'en', 'Google News UK'),
        GN('france politics', 'en', 'Google News France'),
        GN('germany politics', 'en', 'Google News Germany'),
        GN('us politics', 'en', 'Google News USA'),
        GN('australia politics', 'en', 'Google News Australia'),
        GN('timor-leste', 'en', 'Google News Timor Leste'),
        GN('thailand politics', 'en', 'Google News Thailand'),
        GN('japan politics', 'en', 'Google News Japan'),
        GN('north korea', 'en', 'Google News Korea Utara'),
        GN('south korea politics', 'en', 'Google News Korea Selatan'),
        GN('taiwan politics', 'en', 'Google News Taiwan'),
        GN('russia politics', 'en', 'Google News Russia'),
        GN('latin america politics', 'en', 'Google News Amerika Latin'),
    ],
    'ekonomi': [
        RSSF('https://www.cnnindonesia.com/ekonomi/rss', 'CNN Indonesia'),
        RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia'),
        RSSF('https://www.antaranews.com/rss/ekonomi', 'Antara'),
        GN('china economy', 'en', 'Google News Ekonomi China'),
        GN('japan economy', 'en', 'Google News Ekonomi Jepang'),
        GN('south korea economy', 'en', 'Google News Ekonomi Korea Selatan'),
        GN('malaysia economy', 'en', 'Google News Ekonomi Malaysia'),
        GN('european union economy', 'en', 'Google News Ekonomi Eropa'),
        GN('russia economy', 'en', 'Google News Ekonomi Rusia'),
        GN('us economy', 'en', 'Google News Ekonomi USA'),
        GN('latin america economy', 'en', 'Google News Ekonomi Amerika Latin'),
    ],
    'olahraga': [
        RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Indonesia'),
        RSSF('https://www.bola.net/feed', 'Bola.net'),
        RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        GN('timnas indonesia', 'id', 'Google News Timnas'),
        GN('premier league', 'en', 'Google News Premier League'),
        GN('bundesliga', 'en', 'Google News Bundesliga'),
        GN('la liga', 'en', 'Google News La Liga'),
        GN('ligue 1', 'en', 'Google News Ligue 1'),
        GN('nba basketball', 'en', 'Google News NBA'),
        GN('mls soccer', 'en', 'Google News MLS'),
    ],
    'teknologi': [
        RSSF('https://www.cnnindonesia.com/teknologi/rss', 'CNN Indonesia'),
        RSSF('https://techcrunch.com/feed/', 'TechCrunch'),
        RSSF('https://www.theverge.com/rss/index.xml', 'The Verge'),
        RSSF('https://feeds.bbci.co.uk/news/technology/rss.xml', 'BBC Tech'),
        GN('smartphone launch', 'en', 'Google News Smartphone'),
        GN('artificial intelligence', 'en', 'Google News AI'),
        GN('robot technology', 'en', 'Google News Robot'),
        GN('new laptop release', 'en', 'Google News Laptop'),
        GN('tablet launch', 'en', 'Google News Tablet'),
    ],
    'hiburan': [
        RSSF('https://www.cnnindonesia.com/hiburan/rss', 'CNN Indonesia'),
        RSSF('https://hot.detik.com/rss', 'DetikHot'),
        RSSF('https://www.kompas.com/hype/feed', 'Kompas Hype'),
        GN('musik indonesia', 'id', 'Google News Musik'),
        GN('film indonesia', 'id', 'Google News Film'),
    ],
    'kesehatan': [
        RSSF('https://health.kompas.com/rss', 'Kompas Health'),
        RSSF('https://health.detik.com/feed', 'Detik Health'),
        RSSF('https://feeds.bbci.co.uk/news/health/rss.xml', 'BBC Health'),
        RSSF('https://www.antaranews.com/rss/kesehatan', 'Antara Kesehatan'),
        GN('kesehatan', 'id', 'Google News Kesehatan'),
    ],
}

URGENT_FEEDS = [
    RSSF('https://www.cnnindonesia.com/nasional/rss', 'CNN Indonesia'),
    RSSF('https://nasional.kompas.com/rss', 'Kompas Nasional'),
    RSSF('https://www.liputan6.com/rss', 'Liputan6'),
    RSSF('https://www.detik.com/feed', 'Detik'),
    GN('earthquake today', 'en', 'Google News Gempa'),
    GN('tsunami warning', 'en', 'Google News Tsunami'),
    GN('volcanic eruption', 'en', 'Google News Erupsi'),
    GN('war conflict breaking', 'en', 'Google News Perang'),
    GN('missile attack', 'en', 'Google News Serangan'),
    GN('ferry sinks', 'en', 'Google News Kapal Tenggelam'),
    GN('plane crash', 'en', 'Google News Pesawat Jatuh'),
    GN('bank robbery', 'en', 'Google News Perampokan'),
    GN('massive protest', 'en', 'Google News Demo Besar'),
    GN('mass poisoning', 'en', 'Google News Keracunan'),
    GN('corruption arrest', 'en', 'Google News Penangkapan KPK'),
]

LUAR_NEGERI_WORDS = ['jepang', 'china', 'amerika', 'eropa', 'luar negeri', 'inggris',
                     'india', 'korea', 'australia', 'turki', 'israel', 'gaza',
                     'ukraina', 'rusia', 'malaysia', 'thailand', 'taiwan', 'timor leste']

SYSTEM_PROMPT = """Kamu adalah AI Wartawan profesional portal berita KramaNews Indonesia.

TUGAS: Tulis ulang materi sumber menjadi berita orisinal KramaNews.

ATURAN GAYA PENULISAN (WAJIB):
- Tulis seperti wartawan portal besar Indonesia. LAPOR BERITA LANGSUNG.
- DILARANG KERAS menyebut nama portal, media, situs, atau sumber berita mana pun
  di dalam isi berita ("Berdasarkan laporan...", "Dilansir dari...", dll DILARANG).
- JANGAN menjelaskan dari mana informasi didapat. Ceritakan langsung.

ATURAN NARASUMBER & TOKOH (WAJIB - PALING PENTING):
- Jika materi sumber menyebut NAMA ORANG yang menjadi sumber berita, tokoh
  utama, atau pejabat yang berbicara → WAJIB SEBUTKAN NAMA LENGKAPNYA
  dalam isi berita, bersama jabatannya.
- FORMAT KUTIPAN YANG WAJIB:
  ✅ "Ketua Komisi III DPRD Kaltara, Aminuddin, mengatakan bahwa..."
  ✅ "Rektor Universitas Siber Nusantara, Dr. Budi Santoso, menyatakan..."
  ✅ "Presiden Prabowo Subianto menyampaikan bahwa..."
  ✅ "Kepala BMKG, Dwikorita Karnawati, menjelaskan..."
- FORMAT SALAH (DILARANG KERAS):
  ❌ "anggota DPRD mengatakan..." (tanpa nama)
  ❌ "rektor universitas menyatakan..." (tanpa nama)
  ❌ "Presiden RI mengatakan..." (tanpa nama Prabowo)
- Kumpulkan SEMUA nama tokoh yang ada di materi sumber dan sebutkan mereka
  dengan nama lengkap di posisi kalimat kutipan/keterangan.
- Jika ada KUTIPAN LANGSUNG dari tokoh di materi, salin kutipannya dan
  tandai dengan nama yang mengatakannya.
- HANYA jika materi sumber SAMA SEKALI tidak menyebut nama orang mana pun
  (misal hanya fakta kejadian murni), barulah berita ditulis tanpa kutipan
  tokoh — jelaskan lewat fakta kejadian.
- DILARANG MENGARANG nama tokoh yang tidak ada di materi sumber.

ATURAN WAKTU KEJADIAN (WAJIB - BARU V5.1):
- Dalam isi berita WAJIB CANTUMKAN HARI, TANGGAL, dan JAM kejadian secara
  eksplisit, seperti contoh:
  ✅ "...kejadian terjadi pada Minggu (15 September 2026) sekitar pukul 03.00 WIB..."
  ✅ "...berdasarkan data BMKG, gempa terjadi Sabtu (14 September 2026) pukul 21.45 WIB..."
  ✅ "...peristiwa itu terjadi Jumat (13 September 2026) di kawasan..."
- Jika materi sumber tidak menyebut hari/tanggal/jam secara eksplisit,
  gunakan tanggal "today" dari konteks, ATAU tulis keterangan umum seperti
  "belum dikonfirmasi waktu pasti kejadian". JANGAN mengarang tanggal.
- Format penulisan tanggal di Indonesia: Hari (Tanggal Bulan Tahun) pukul Jam:Menit WIB

ATURAN DATELINE (WAJIB):
- Baris pertama isi berita diawali DATELINE: "KOTA, PROVINSI/NEGARA - ".
- Contoh: "TARAKAN, KALTARA - ...", "STOCKHOLM, SWEDIA - ...".
- Huruf kapital + "-". Jika lokasi tidak ada: "INDONESIA - ".

ATURAN NAMA ASING (WAJIB - JANGAN MENERJEMAHKAN):
- Nama PARTAI, ORGANISASI, LEMBAGA, PERUSAHAAN asing TIDAK BOLEH diterjemahkan.
  Tulis nama ASLI + jenis di depannya:
  BENAR: "Partai Sweden Democrats (Swedia)", "Partai AfD (Jerman)",
         "Partai Rassemblement National (Prancis)", "Partai Brothers of Italy".
  SALAH: "Gelombang Kanan Jauh" (itu Sweden Democrats!).
- Partai besar dunia: Sweden Democrats, AfD, Rassemblement National,
  Brothers of Italy, PVV, FPÖ, Vox, Labour, Conservative, Reform UK,
  Republican, Democratic. Gunakan NAMA ASLI.
- Nama tokoh asing: ejaan asli/lazim di media Indonesia.

ATURAN DATA & ANGKA (WAJIB):
- Angka dari materi sumber WAJIB SALIN UTUH & PERSIS.
  Jangan dibulatkan, diubah, atau dipangkas.
  Contoh: "tumbuh 5,02 persen" → wajib "5,02 persen".
- Berita ekonomi/statistik: minimal 1-3 angka kunci dari sumber muncul.
- DILARANG menambah angka yang tidak ada di materi sumber.
- Jika sumber tanpa angka: tulis ringkas padat, JANGAN karang angka.

ATURAN PANJANG & ISI (WAJIB):
- 350-500 kata (5-7 paragraf). KEBUTUHAN MINIMAL.
- Paragraf 1: inti berita. Paragraf 2-4: detail, angka, kronologi, kutipan tokoh.
- Paragraf 5-6: konteks. Terakhir: penutup netral.
- Kalimat pendek, jelas.

ATURAN JUDUL (WAJIB):
- Judul ORISINAL maksimal 10 kata. Nama tokoh/partai asing memakai nama asli.

ATURAN ETIKA FAKTA (WAJIB):
- HANYA fakta dari materi sumber. DILARANG mengarang fakta, nama, atau angka.

ATURAN GAMBAR (WAJIB - deskripsi_gambar):
- Isi field "deskripsi_gambar" dengan 3-6 kata kunci bahasa Inggris yang
  MENGGAMBARKAN TOPIK berita ini secara VISUAL.
- Contoh BENAR:
  Gempa: "earthquake rubble rescue"
  Kesehatan/RS: "hospital patients medical staff"
  Keagamaan: "prayer crowd mosque"
  Pemerintah: "city hall government building"
  Olahraga: "football stadium match"
  Kebakaran: "fire smoke burning building"
- Contoh SALAH: hutan rimbun untuk berita gempa, nelayan di laut untuk berita
  kebakaran, pemandangan kota untuk berita posko kesehatan.
- HANYA kata kunci visual, TANPA nama orang.

FORMAT JAWABAN:
Jawab HANYA dengan JSON valid tanpa teks lain:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2", "ringkasan": "...",
 "deskripsi_gambar": "visual keywords",
 "waktu_kejadian": "Hari (Tanggal Bulan Tahun) pukul Jam:Menit WIB atau UTC"}"""

# ═════════ FUNGSI BANTU ═════════

def edge_call(payload_json):
    r = requests.post(EDGE_URL,
        headers={'apikey': SUPABASE_PUBLISHABLE,
                 'Authorization': 'Bearer ' + SUPABASE_PUBLISHABLE,
                 'Content-Type': 'application/json'},
        json=payload_json, timeout=30)
    try:
        data = r.json()
    except Exception:
        raise Exception('HTTP ' + str(r.status_code) + ': ' + r.text[:120])
    if not r.ok or data.get('error'):
        raise Exception(str(data.get('error') or ('HTTP ' + str(r.status_code))))
    return data.get('data')

def rest_get(query):
    r = requests.get(REST_URL + query,
        headers={'apikey': SUPABASE_PUBLISHABLE,
                 'Authorization': 'Bearer ' + SUPABASE_PUBLISHABLE},
        timeout=30)
    if not r.ok:
        raise Exception('Supabase REST ' + str(r.status_code) + ': ' + r.text[:120])
    return r.json() or []

def get_today_state():
    rows = rest_get('?select=source_url,created_at&order=created_at.desc&limit=300')
    today = datetime.now(WIB).date()
    urls = set()
    for row in rows:
        try:
            d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WIB).date()
            if d == today and row.get('source_url'):
                urls.add(row['source_url'])
        except Exception:
            pass
    return urls

def get_breaking_list():
    try:
        return rest_get('?select=id,created_at&breaking=eq.true&status=eq.published&order=created_at.asc')
    except Exception:
        return []

def get_image(entry):
    mc = entry.get('media_content')
    if mc and mc[0].get('url'):
        return mc[0]['url']
    mt = entry.get('media_thumbnail')
    if mt and mt[0].get('url'):
        return mt[0]['url']
    if entry.get('enclosures'):
        return entry['enclosures'][0].get('href', '')
    return ''

def clean(text, limit=2000):
    t = re.sub(r'<[^>]+>', '', text or '')
    t = t.replace('&nbsp;', ' ').replace('&amp;', '&')
    return re.sub(r'\s+', ' ', t).strip()[:limit]

def get_material(entry):
    s = clean(entry.get('summary', ''))
    try:
        c = entry.get('content')
        if c and isinstance(c, list):
            for part in c:
                if isinstance(part, dict):
                    v = clean(part.get('value', ''), 2500)
                    if len(v) > len(s):
                        s = v
    except Exception:
        pass
    return s

def gn_split(title):
    if ' - ' in title:
        parts = title.rsplit(' - ', 1)
        if len(parts[1]) < 40:
            return parts[0].strip(), parts[1].strip()
    return title.strip(), 'Google News'

def collect_candidates(sources, today_urls, seen):
    out = []
    for src in sources:
        try:
            feed = feedparser.parse(src['url'])
        except Exception:
            continue
        for entry in feed.entries[:25]:
            link = entry.get('link', '')
            if not link or link in seen or link in today_urls:
                continue
            title = entry.get('title', '')
            summary = get_material(entry)
            if not title or not summary:
                continue
            seen.add(link)
            sname = src['source']
            if src.get('gn'):
                t2, portal = gn_split(title)
                title = t2
                if portal and portal != 'Google News':
                    sname = portal
            out.append({'title': title, 'summary': summary, 'link': link,
                        'source': sname, 'entry': entry})
    return out

def match_articles(candidates):
    STOP = set('di ke dari yang dan atau dengan untuk pada dalam akan telah '
               'sudah karena jika agar itu ini para kami mereka ada tidak bisa '
               'dapat juga lebih masih hanya setelah sebelum sekitar oleh '
               'sebagai kata bilang katakan ujar menurut the and for with from '
               'that this have will been are was were their they about after'.split())
    def kw(s):
        return set(re.findall(r'[a-z0-9]{4,}', s.lower())) - STOP
    groups = []
    for c in candidates:
        k = kw(c['title'])
        placed = False
        for g in groups:
            if len(k & g['kw']) >= 2:
                g['items'].append(c)
                g['kw'] |= k
                placed = True
                break
        if not placed:
            groups.append({'kw': k, 'items': [c]})
    return groups

def parse_ai_json(text):
    t = text.strip()
    if t.startswith('```'):
        t = re.sub(r'^```[a-zA-Z]*\s*', '', t)
        t = re.sub(r'\s*```$', '', t)
    return json.loads(t)

def ai_write(user_content, timeout=150):
    r = requests.post('https://api.deepseek.com/chat/completions',
        headers={'Authorization': 'Bearer ' + DEEPSEEK_KEY,
                 'Content-Type': 'application/json'},
        json={'model': 'deepseek-chat',
              'messages': [{'role': 'system', 'content': SYSTEM_PROMPT},
                           {'role': 'user', 'content': user_content}],
              'temperature': 0.8},
        timeout=timeout)
    r.raise_for_status()
    obj = parse_ai_json(r.json()['choices'][0]['message']['content'])
    judul = obj.get('judul', '').strip()
    isi = obj.get('isi', '').strip()
    ringkasan = obj.get('ringkasan', '').strip()
    gambar = (obj.get('deskripsi_gambar') or '').strip()
    waktu = (obj.get('waktu_kejadian') or '').strip()
    return judul, isi, ringkasan, gambar, waktu

def ai_rewrite_single(c):
    user = ('MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Ringkasan: ' + c['summary'] + '\n\n'
            'Tulis ulang sesuai SEMUA aturan: sebutkan NAMA LENGKAP tokoh/narasumber '
            '(jangan hanya jabatan tanpa nama), jangan sebut portal/media sumber, '
            'awali isi berita dengan dateline lokasi '
            '(format: "KOTA, PROVINSI/NEGARA - ..."), salin utuh semua angka, '
            'cantumkan HARI + TANGGAL + JAM kejadian di dalam isi berita, '
            'dan isi field deskripsi_gambar dengan kata kunci visual yang sesuai topik.')
    return ai_write(user)

def ai_rewrite_multi(items):
    parts = []
    for i, it in enumerate(items[:4], 1):
        parts.append('[MATERI ' + str(i) + ']\n'
                     'Judul: ' + it['title'] + '\nIsi: ' + it['summary'][:1500])
    user = ('Berikut beberapa materi tentang topik yang SAMA:\n\n'
            + '\n\n'.join(parts) +
            '\n\nGabungkan menjadi SATU berita KramaNews lengkap (350-500 kata) sesuai SEMUA aturan: '
            'sebutkan NAMA LENGKAP tokoh/narasumber, jangan sebut portal/media sumber, '
            'awali dengan dateline lokasi (format: "KOTA, PROVINSI/NEGARA - ..."), '
            'salin utuh semua angka, cantumkan HARI + TANGGAL + JAM kejadian, '
            'dan isi field deskripsi_gambar dengan kata kunci visual yang sesuai topik berita.')
    return ai_write(user, timeout=180)

def is_urgent(title, summary):
    t = (title + ' ' + summary).lower()
    return any(k in t for k in BREAKING_KEYWORDS)

# Cek gempa ≥5 SR (jangan semua gempa masuk breaking)
def cek_gempa_besar(title, summary):
    """Cek apakah ada mention gempa dengan magnitude ≥5. Kalau tidak, skip gempa kecil."""
    t = (title + ' ' + summary).lower()
    if 'gempa' not in t and 'earthquake' not in t:
        return False
    # cari magnitude
    m = re.search(r'm\s?(\d{1,2}[.,]\d{1,2})', t)
    if m:
        try:
            mag = float(m.group(1).replace(',', '.'))
            return mag >= GEMPA_MIN_MAGNITUDE
        except Exception:
            pass
    # kalau tidak bisa dibaca magnitude, asumsikan besar (breaking)
    return True

def cari_gambar_wikimedia(deskripsi):
    """Cari gambar bebas hak cipta di Wikimedia sesuai deskripsi gambar dari AI."""
    if not deskripsi:
        return ''
    try:
        q = quote_plus(deskripsi)
        url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
               '&gsrsearch=' + q + '&gsrnamespace=6&gsrlimit=5&prop=imageinfo'
               '&iiprop=url&iiurlwidth=800&format=json&origin=*')
        r = requests.get(url, timeout=20)
        if not r.ok:
            return ''
        pages = r.json().get('query', {}).get('pages', {})
        for p in pages.values():
            info = p.get('imageinfo', [{}])[0]
            u = info.get('thumburl') or info.get('url') or ''
            if u and u.lower().endswith(('.jpg', '.jpeg', '.png')):
                return u
    except Exception:
        pass
    return ''

def insert_news(judul, isi, ringkasan, cat, img, link, source_name, status,
                breaking=False, deskripsi_gambar='', waktu=''):
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+(.*)$', isi, re.DOTALL)
    dateline = m.group(1).strip() if m else ''
    isi_bersih = m.group(2).strip() if m else isi
    payload = {
        'title': judul, 'excerpt': ringkasan, 'content': isi_bersih,
        'category': cat, 'author': AUTHOR_NAME,
        'img': img or '',
        'dateline': dateline,
        'source_name': source_name, 'source_url': link,
        'written_by': 'ai', 'status': status,
    }
    if breaking:
        payload['breaking'] = True
    edge_call({'action': 'insert', 'payload': payload})

def cabut_breaking_terlama():
    brk = get_breaking_list()
    if brk:
        terlama = brk[0]
        edge_call({'action': 'update', 'id': terlama['id'],
                   'payload': {'breaking': False, 'updated_at': datetime.now(timezone.utc).isoformat()}})
        print('   🔄 Breaking terlama dicabut otomatis (ID ' + str(terlama['id']) + ')')
        return True
    return False

# ═════════ SESI BERBURU ═════════

def sesi_siaga(today_urls, seen):
    made = 0
    slots = 3 - len(get_breaking_list())
    print('\n🚨 SIAGA — slot breaking tersedia: ' + str(slots) + '...')
    cands = collect_candidates(URGENT_FEEDS, today_urls, seen)
    for c in cands:
        if made >= 3:
            break
        if not is_urgent(c['title'], c['summary']):
            continue
        try:
            judul, isi, ringkasan, waktu = ai_rewrite_single(c)
        except Exception as e:
            print('   ⚠️ AI gagal 1 siaga:', str(e)[:60])
            continue
        blob = (judul + ' ' + isi).lower()
        cat = 'internasional' if any(w in blob for w in LUAR_NEGERI_WORDS) else 'nasional'
        img = get_image(c['entry'])
        try:
            if slots > 0:
                insert_news(judul, isi, ringkasan, cat, img, c['link'],
                            c['source'], status='published', breaking=True,
                            deskripsi_gambar='', waktu=waktu)
                slots -= 1
                print('   🚨 BREAKING TAYANG: ' + judul)
            elif cabut_breaking_terlama():
                slots += 1
                insert_news(judul, isi, ringkasan, cat, img, c['link'],
                            c['source'], status='published', breaking=True,
                            deskripsi_gambar='', waktu=waktu)
                slots -= 1
                print('   🔄 BREAKING DIGANTI (terlama dicabut): ' + judul)
            else:
                insert_news(judul, isi, ringkasan, cat, img, c['link'],
                            c['source'], status='published',
                            deskripsi_gambar='', waktu=waktu)
                print('   📰 TAYANG (tanpa breaking): ' + judul)
            made += 1
            today_urls.add(c['link'])
        except Exception as e:
            print('   ⚠️ Gagal simpan siaga:', str(e)[:60])
        time.sleep(2)
    print('   → Siaga: ' + str(made))
    return made

def sesi_kategori(cat, need, today_urls, seen, kaltara_min=0):
    print('\n📰 ' + cat.upper() + ' — target ' + str(need))
    sources = list(HUNT.get(cat, []))
    if cat in ('internasional', 'ekonomi', 'olahraga', 'teknologi'):
        random.shuffle(sources)
    cands = collect_candidates(sources, today_urls, seen)
    print('   Kandidat: ' + str(len(cands)))
    if not cands:
        print('   ⚠️ Tidak ada kandidat.')
        return 0

    groups = match_articles(cands)
    groups.sort(key=lambda g: len(g['items']), reverse=True)

    made = 0
    kaltara_made = 0

    if kaltara_min > 0:
        kc = [c for c in cands
              if any(w in (c['title'] + ' ' + c['summary']).lower() for w in KALTARA_WORDS)]
        for c in kc:
            if kaltara_made >= kaltara_min or made >= need:
                break
            try:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(c)
                insert_news(judul, isi, ringkasan, cat, get_image(c['entry']),
                            c['link'], c['source'], status='published',
                            deskripsi_gambar=desc_gambar, waktu=waktu)
                made += 1
                kaltara_made += 1
                today_urls.add(c['link'])
                print('   🏝️ KALTARA [' + str(kaltara_made) + '/' + str(kaltara_min) + ']: ' + judul)
            except Exception as e:
                print('   ⚠️ Gagal 1 kaltara:', str(e)[:60])
            time.sleep(2)
        print('   → Kaltara: ' + str(kaltara_made) + '/' + str(kaltara_min))

    for g in groups:
        if made >= need:
            break
        items = g['items']
        top = items[0]
        try:
            if len(items) > 1:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_multi(items)
                print('       🔗 topik dari ' + str(len(items)) + ' portal')
            else:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(top)
            insert_news(judul, isi, ringkasan, cat, get_image(top['entry']),
                        top['link'], top['source'], status='published',
                        deskripsi_gambar=desc_gambar, waktu=waktu)
            made += 1
            for it in items:
                today_urls.add(it['link'])
            print('   ✅ [' + str(made) + '/' + str(need) + '] TAYANG: ' + judul)
        except Exception as e:
            print('   ⚠️ Gagal proses 1 kelompok:', str(e)[:80])
            continue
        time.sleep(2)

    print('   → Hasil: ' + str(made) + ' TAYANG')
    return made

def run_session(hour):
    today_urls = get_today_state()
    seen = set()
    total = 0
    total += sesi_siaga(today_urls, seen)

    quota = JADWAL_JAM.get(hour, {'nasional': 3})
    print('\n📊 Kuota jam ' + str(hour).zfill(2) + ':00 WIB')
    for cat, need in quota.items():
        try:
            if cat == 'daerah':
                total += sesi_kategori(cat, need, today_urls, seen, kaltara_min=2)
            else:
                total += sesi_kategori(cat, need, today_urls, seen)
        except Exception as e:
            print('   ❌ Kategori ' + cat + ' error: ' + str(e)[:80])
    return total

# ═════════ PROGRAM UTAMA ═════════

def main_sekali():
    print('🐝 AI WARTAWAN — MODE SEKALI JALAN (' + datetime.now(WIB).strftime('%H:%M WIB') + ')')
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ Kunci belum diisi!')
        return
    try:
        hour = datetime.now(WIB).hour
        total = run_session(hour)
        print(' 🏁 Selesai — total ' + str(total) + ' berita TAYANG.')
    except Exception as e:
        print(' ❌ Gagal: ' + str(e)[:100])

def main():
    print('=' * 60)
    print(' 🐝 AI WARTAWAN KRAMANEWS V5.2 — MODE 24 JAM PER JAM')
    print(' ⏰ Jadwal: setiap jam (24x/hari)')
    print(' ✍️  Penulis: ' + AUTHOR_NAME)
    print(' 💡 Biarkan terminal ini terbuka. Stop: Ctrl+C')
    print('=' * 60)

    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ DEEPSEEK_KEY / SUPABASE_PUBLISHABLE belum diisi!')
        return

    while True:
        try:
            now = datetime.now(WIB)
            hour = now.hour
            print('\n' + '=' * 60)
            print(' ⏰ SESI JAM ' + str(hour).zfill(2) + ':00 WIB — mulai berburu...')
            print('=' * 60)
            try:
                total = run_session(hour)
                print('\n 🏁 Sesi selesai — total ' + str(total) + ' berita TAYANG.')
            except Exception as e:
                print(' ❌ Sesi gagal: ' + str(e)[:100])
            next_run = now.replace(hour=(hour + 1) % 24, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run = next_run + timedelta(days=1)
            wait_sec = max(0, (next_run - datetime.now(WIB)).total_seconds())
            print(' ⏳ Menunggu jam berikutnya... (' + str(int(wait_sec)) + ' detik)')
            time.sleep(wait_sec)
        except KeyboardInterrupt:
            print('\n👋 Wartawan AI berhenti. Sampai jumpa!')
            break
        except Exception as e:
            print(' ⚠️ Loop error: ' + str(e)[:80])
            time.sleep(120)

if __name__ == '__main__':
    if '--sekali' in sys.argv:
        main_sekali()
    else:
        main()
