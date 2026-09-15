# ══════════════════════════════════════════════════════
#  AI WARTAWAN KRAMANEWS — V6.1
#  Baru V6.1:
#   • ANTI BERITA DOBEL: cek kemiripan judul sebelum tayang
#     (kasus: "80 Hektare Tarakan Terbakar" tayang 2x dari portal beda)
#   • Semua fitur V6.0 tetap: tanggal dinamis, breaking 3 slot,
#     expire 30 menit, anti dominasi gempa, kuota per jam
#   • Marker verifikasi: cari kata "KRAMAV610MARKER"
#  Mode 1 (loop 30 menit) : python3 skrip-wartawan.py
#  Mode 2 (GitHub Actions): python3 skrip-wartawan.py --sekali
# ══════════════════════════════════════════════════════

import requests
import json
import time
import re
import os
import sys
import random
import feedparser
from time import mktime
from difflib import SequenceMatcher
from datetime import datetime, timezone, timedelta
from urllib.parse import quote_plus

DEEPSEEK_KEY         = os.environ.get('DEEPSEEK_KEY', '')
SUPABASE_PUBLISHABLE = os.environ.get('SUPABASE_PUBLISHABLE', '')

SUPABASE_URL = 'https://imcvijgytdjjpotlaltv.supabase.co'
REST_URL     = SUPABASE_URL + '/rest/v1/articles'
EDGE_URL     = SUPABASE_URL + '/functions/v1/admin-ops'
AUTHOR_NAME  = 'DT'

WIB = timezone(timedelta(hours=7))

# ═══ PENGATURAN V6.1 ═══
BREAKING_MAX_SLOT   = 3      # slot breaking di hero
BREAKING_UMUR_MENIT = 30     # breaking dicabut otomatis setelah 30 menit
MAX_UMUR_BERITA_JAM = 30     # tolak materi RSS lebih tua dari 30 jam
GEMPA_DOM_MIN       = 5.5    # gempa Indonesia: breaking jika M >= ini (tertulis jelas)
GEMPA_DUNIA_MIN     = 6.5    # gempa luar negeri: breaking jika M >= ini (tertulis jelas)
SKOR_BREAKING_MIN   = 30     # skor minimal kandidat breaking
AMBANG_MIRIP        = 0.50   # judul dianggap DOBEL jika kemiripan >= ini (0-1)

HARI_ID  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN_ID = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']

# ═══ JADWAL KUOTA PER JAM (WIB) ═══
JADWAL_JAM = {
    6:  {'nasional': 1, 'daerah': 2, 'internasional': 1, 'ekonomi': 1},
    7:  {'nasional': 1, 'daerah': 2, 'internasional': 1, 'olahraga': 1},
    8:  {'nasional': 1, 'daerah': 3, 'internasional': 1, 'teknologi': 1},
    9:  {'nasional': 1, 'daerah': 2, 'internasional': 1, 'hiburan': 1},
    10: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'kesehatan': 1},
    11: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'ekonomi': 1},
    12: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'olahraga': 1},
    13: {'nasional': 1, 'daerah': 3, 'internasional': 1, 'teknologi': 1},
    14: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'hiburan': 1},
    15: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'kesehatan': 1},
    16: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'ekonomi': 1},
    17: {'nasional': 1, 'daerah': 2, 'internasional': 1, 'olahraga': 1},
    18: {'nasional': 1, 'daerah': 3, 'internasional': 1, 'teknologi': 1},
    19: {'nasional': 1},
    20: {'internasional': 1},
}

KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata', 'amal', 'kayu putih']

def GN(q, lang='id', label=None):
    # when:1d → HANYA berita 1 hari terakhir (anti berita lama)
    if lang == 'en':
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:1d')
               + '&hl=en-US&gl=US&ceid=US:EN')
    else:
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:1d')
               + '&hl=id&gl=ID&ceid=ID:id')
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

# ═══ FEED BREAKING — SLOT 1: DOMESTIK (portal besar Indonesia) ═══
BREAKING_DOMESTIK_FEEDS = [
    RSSF('https://www.cnnindonesia.com/nasional/rss', 'CNN Indonesia'),
    RSSF('https://www.detik.com/feed', 'Detik'),
    RSSF('https://nasional.kompas.com/rss', 'Kompas Nasional'),
    RSSF('https://www.liputan6.com/rss', 'Liputan6'),
    RSSF('https://www.antaranews.com/rss/nasional', 'Antara'),
    RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia'),
    RSSF('https://nasional.tribunnews.com/rss', 'Tribun Nasional'),
    GN('breaking news indonesia', 'id', 'GN Breaking Indonesia'),
]

# ═══ FEED BREAKING — SLOT 2: DUNIA (portal besar dunia) ═══
BREAKING_DUNIA_FEEDS = [
    RSSF('https://feeds.bbci.co.uk/news/world/rss.xml', 'BBC World'),
    RSSF('https://www.aljazeera.com/xml/rss/all.xml', 'Al Jazeera'),
    RSSF('https://www.theguardian.com/world/rss', 'The Guardian'),
    RSSF('http://rss.cnn.com/rss/edition_world.rss', 'CNN World'),
    GN('breaking world news', 'en', 'GN Breaking Dunia'),
    GN('major earthquake', 'en', 'GN Gempa Besar Dunia'),
    GN('war conflict missile', 'en', 'GN Perang'),
]

LUAR_NEGERI_WORDS = ['jepang', 'china', 'amerika', 'eropa', 'luar negeri', 'inggris',
                     'india', 'korea', 'australia', 'turki', 'israel', 'gaza',
                     'ukraina', 'rusia', 'malaysia', 'thailand', 'taiwan', 'timor leste']

# ═══ SKOR BREAKING ═══
INDO_GEO = ['indonesia', 'bmkg', 'aceh', 'sumatera', 'sumatra', 'jawa', 'kalimantan',
            'sulawesi', 'papua', 'bali', 'nusa tenggara', 'lombok', 'ntb', 'ntt',
            'maluku', 'ambon', 'manado', 'makassar', 'medan', 'padang', 'jakarta',
            'bandung', 'surabaya', 'yogyakarta', 'jayapura', 'bengkulu', 'lampung',
            'palu', 'mamuju', 'cilacap', 'garut', 'cianjur', 'tasikmalaya',
            'jember', 'lumajang', 'semarang', 'banggai', 'tarakan', 'kaltara',
            'nunukan', 'bulungan', 'malinau']

DOM_KRITIS = [
    'tsunami', 'erupsi', 'gunung meletus', 'banjir bandang', 'banjir besar',
    'tanah longsor', 'longsor', 'karhutla', 'kebakaran hutan', 'kebakaran hebat',
    'kebakaran massal', 'keracunan massal', 'angin puting beliung', 'korban jiwa',
    'mengungsi', 'kapal tenggelam', 'feri tenggelam', 'kapal karam', 'perahu tenggelam',
    'pesawat jatuh', 'pesawat hilang', 'kecelakaan pesawat', 'pesawat tergelincir',
    'pembunuhan', 'dibunuh', 'ditemukan mati', 'penembakan', 'ledakan', 'bom meledak',
    'perampokan bersenjata', 'rampok bank', 'ott kpk', 'ditangkap kpk',
    'tersangka korupsi', 'tertangkap tangan',
    'reshuffle', 'pergantian menteri', 'menteri diganti', 'menteri meninggal',
    'menteri wafat', 'menteri ditangkap', 'menteri tersangka',
    'presiden meninggal', 'wapres meninggal',
    'kerusuhan', 'ricuh', 'bentrok massa', 'demo besar', 'demonstrasi besar',
    'massa membakar', 'membakar massal', 'tawuran besar',
]

DUNIA_KRITIS = [
    'missile', 'airstrike', 'air strike', 'invasion', 'nuclear', 'nuklir',
    'assassination', 'coup', 'uprising', 'civil war', 'terror attack',
    'suicide bombing', 'explosion', 'explodes', 'mass shooting', 'stabbing attack',
    'hurricane', 'typhoon', 'cyclone', 'wildfire', 'flood', 'landslide',
    'volcano', 'eruption', 'tsunami warning', 'volcanic eruption',
    'plane crash', 'ferry sinks', 'train derailment', 'derailed',
    'resignation', 'overthrown', 'state of emergency', 'killed',
]
class BeritaLama(Exception):
    pass

# ═══ ANTI BERITA DOBEL (V6.1) ═══

KATA_STOP_DOBEL = set('yang dan di ke dari untuk pada dengan dalam ini itu akan telah '
                      'sudah oleh sebagai ada adalah kata ujar bilang menurut the and '
                      'for with from that this have will been are was were their they '
                      'about after'.split())

def normalisasi_judul(s):
    s = (s or '').lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def kata_inti(judul):
    return set(k for k in normalisasi_judul(judul).split()
               if len(k) > 3 and k not in KATA_STOP_DOBEL)

JUDUL_TERPAKAI = []  # judul berita hari ini (dari DB + sesi berjalan), sudah dinormalisasi

def sudah_serupa(judul):
    """True jika judul mirip dengan berita yang sudah tayang hari ini (anti dobel)."""
    j = normalisasi_judul(judul)
    if not j:
        return False
    ki = kata_inti(judul)
    for t in JUDUL_TERPAKAI:
        if not t:
            continue
        # Cek 1: kemiripan urutan huruf
        if SequenceMatcher(None, j, t).ratio() >= AMBANG_MIRIP:
            return True
        # Cek 2: tumpang tindih kata inti (>=3 kata sama & >=70% dari set kecil)
        kt = kata_inti(t)
        if ki and kt:
            sama = ki & kt
            if len(sama) >= 3 and len(sama) / min(len(ki), len(kt)) >= 0.7:
                return True
    return False

def muat_judul_hari_ini():
    """Ambil semua judul berita yang tayang hari ini (WIB) dari database."""
    out = []
    try:
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=300')
        today = datetime.now(WIB).date()
        for row in rows:
            try:
                d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WIB).date()
                if d == today and row.get('title'):
                    out.append(normalisasi_judul(row['title']))
            except Exception:
                pass
    except Exception as e:
        print('   ⚠️ Gagal memuat judul hari ini:', str(e)[:60])
    return out

# ═══ KONTEKS WAKTU DINAMIS (AI SELALU TAHU TANGGAL) ═══
def tanggal_panjang(d):
    return HARI_ID[d.weekday()] + ' (' + str(d.day) + ' ' + BULAN_ID[d.month] + ' ' + str(d.year) + ')'

def konteks_waktu():
    now = datetime.now(WIB)
    kemarin = (now - timedelta(days=1)).date()
    return {'hari_ini': tanggal_panjang(now.date()),
            'kemarin': tanggal_panjang(kemarin),
            'tahun': str(now.year)}

def build_system_prompt():
    k = konteks_waktu()
    return """Kamu adalah AI Wartawan profesional portal berita KramaNews Indonesia.
KRAMAV610MARKER — V6.1: berita HANYA hari ini/kemarin, breaking cerdas, narasumber bernama.

TUGAS: Tulis ulang materi sumber menjadi berita orisinal KramaNews.

═══ ATURAN KEMUTAKHIRAN (PALING PENTING — ANTI BERITA LAMA) ═══
- HARI INI adalah """ + k['hari_ini'] + """.
- KEMARIN adalah """ + k['kemarin'] + """.
- Tahun berjalan: """ + k['tahun'] + """.
- HANYA tulis peristiwa yang terjadi HARI INI atau KEMARIN.
- PERIKSA tanggal di materi sumber! Jika peristiwa lebih lama dari kemarin
  (contoh: berita tahun 2025, atau bulan Mei/Juni/Juli yang sudah lewat),
  TOLAK dengan jawaban: {"tolak": "berita lama: <sebutkan tanggal sumber>"}
- DILARANG KERAS menulis tanggal dari tahun sebelum """ + k['tahun'] + """ di dalam berita.

ATURAN GAYA PENULISAN (WAJIB):
- Tulis seperti wartawan portal besar Indonesia. LAPOR BERITA LANGSUNG.
- DILARANG KERAS menyebut nama portal, media, situs, atau sumber berita mana pun
  di dalam isi berita ("Berdasarkan laporan...", "Dilansir dari...", dll DILARANG).
- JANGAN menjelaskan dari mana informasi didapat. Ceritakan langsung.

ATURAN NARASUMBER & TOKOH (WAJIB):
- Jika materi sumber menyebut NAMA ORANG (sumber, tokoh utama, pejabat yang
  berbicara) → WAJIB SEBUTKAN NAMA LENGKAPNYA bersama jabatannya.
  ✅ "Ketua Komisi III DPRD Kaltara, Aminuddin, mengatakan bahwa..."
  ❌ "anggota DPRD mengatakan..." (tanpa nama — DILARANG)
- Jika ada KUTIPAN LANGSUNG, salin dan tandai dengan nama yang mengatakannya.
- HANYA jika materi SAMA SEKALI tidak menyebut nama orang, tulis tanpa kutipan tokoh.
- DILARANG MENGARANG nama tokoh yang tidak ada di materi sumber.

ATURAN WAKTU KEJADIAN (WAJIB):
- Cantumkan HARI, TANGGAL, JAM kejadian dalam isi berita:
  ✅ "...terjadi pada """ + k['hari_ini'] + """ sekitar pukul 03.00 WIB..."
- Jika sumber tidak menyebut waktu, tulis "belum dikonfirmasi waktu pasti kejadian".
- JANGAN mengarang tanggal. Format: Hari (Tanggal Bulan """ + k['tahun'] + """) pukul Jam:Menit WIB

ATURAN DATELINE (WAJIB):
- Baris pertama isi berita diawali: "KOTA, PROVINSI/NEGARA - ".
  Contoh: "TARAKAN, KALTARA - ...", "STOCKHOLM, SWEDIA - ...".
- Jika lokasi tidak ada: "INDONESIA - ".

ATURAN NAMA ASING (WAJIB — JANGAN MENERJEMAHKAN):
- Nama partai/organisasi/lembaga/perusahaan asing ditulis APA ADUNA + negaranya.
  BENAR: "Partai Sweden Democrats (Swedia)", "Partai AfD (Jerman)".
  SALAH: "Gelombang Kanan Jauh".
- Nama tokoh asing: ejaan asli/lazim di media Indonesia.

ATURAN DATA & ANGKA (WAJIB):
- Angka dari materi sumber WAJIB SALIN UTUH & PERSIS (contoh: "5,02 persen").
- DILARANG menambah angka yang tidak ada di materi sumber.

ATURAN PANJANG & ISI (WAJIB):
- 350-500 kata (5-7 paragraf). Paragraf 1: inti. 2-4: detail, angka, kutipan.
- 5-6: konteks. Terakhir: penutup netral. Kalimat pendek, jelas.

ATURAN JUDUL (WAJIB):
- Judul ORISINAL maksimal 10 kata.

ATURAN ETIKA FAKTA (WAJIB):
- HANYA fakta dari materi sumber. DILARANG mengarang fakta, nama, atau angka.

ATURAN GAMBAR (WAJIB - deskripsi_gambar):
- Isi "deskripsi_gambar" dengan 3-6 kata kunci bahasa Inggris yang menggambarkan
  TOPIK berita secara VISUAL. Contoh: gempa → "earthquake rubble rescue",
  kebakaran → "fire smoke burning building", olahraga → "football stadium match".
- HANYA kata kunci visual, TANPA nama orang.

FORMAT JAWABAN — HANYA JSON valid tanpa teks lain:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2", "ringkasan": "...",
 "deskripsi_gambar": "visual keywords",
 "waktu_kejadian": "Hari (Tanggal Bulan """ + k['tahun'] + """) pukul Jam:Menit WIB"}
atau jika materi terlalu lama:
{"tolak": "berita lama: <tanggal sumber>"}"""

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

def expire_breaking(menit):
    """Cabut otomatis breaking yang berumur lebih dari `menit` menit."""
    brk = get_breaking_list()
    if not brk:
        return 0
    now = datetime.now(timezone.utc)
    n = 0
    for row in brk:
        try:
            c = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00'))
            if c.tzinfo is None:
                c = c.replace(tzinfo=timezone.utc)
            umur = (now - c).total_seconds() / 60
            if umur > menit:
                edge_call({'action': 'update', 'id': row['id'],
                           'payload': {'breaking': False,
                                       'updated_at': datetime.now(timezone.utc).isoformat()}})
                n += 1
                print('   ⏰ Breaking #' + str(row['id']) + ' dicabut (umur '
                      + str(int(umur)) + ' mnt > ' + str(menit) + ' mnt)')
        except Exception as e:
            print('   ⚠️ expire:', str(e)[:60])
    return n

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

def umur_jam(entry):
    """Umur berita dalam jam. None jika feed tidak menyediakan tanggal."""
    t = entry.get('published_parsed') or entry.get('updated_parsed')
    if not t:
        return None
    try:
        pub = datetime.fromtimestamp(mktime(t), tz=timezone.utc)
        return (datetime.now(timezone.utc) - pub).total_seconds() / 3600.0
    except Exception:
        return None

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
            # ═══ ANTI BERITA LAMA: buang entri lebih tua dari batas ═══
            u = umur_jam(entry)
            if u is not None and u > MAX_UMUR_BERITA_JAM:
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
              'messages': [{'role': 'system', 'content': build_system_prompt()},
                           {'role': 'user', 'content': user_content}],
              'temperature': 0.8},
        timeout=timeout)
    r.raise_for_status()
    obj = parse_ai_json(r.json()['choices'][0]['message']['content'])
    if str(obj.get('tolak', '')).strip():
        raise BeritaLama(str(obj.get('tolak'))[:100])
    judul = obj.get('judul', '').strip()
    isi = obj.get('isi', '').strip()
    ringkasan = obj.get('ringkasan', '').strip()
    waktu = (obj.get('waktu_kejadian') or '').strip()
    gambar = (obj.get('deskripsi_gambar') or '').strip()
    # URUTAN KONSISTEN: judul, isi, ringkasan, WAKTU, GAMBAR
    return judul, isi, ringkasan, waktu, gambar

def ai_rewrite_single(c):
    k = konteks_waktu()
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Ringkasan: ' + c['summary'] + '\n\n'
            'Tulis ulang sesuai SEMUA aturan. PERIKSA DULU: jika peristiwa lebih lama '
            'dari kemarin, TOLAK. Jika masih segar: sebutkan NAMA LENGKAP tokoh/narasumber, '
            'jangan sebut portal/media sumber, awali isi berita dengan dateline lokasi, '
            'salin utuh semua angka, cantumkan HARI + TANGGAL + JAM kejadian di isi berita, '
            'dan isi deskripsi_gambar dengan kata kunci visual sesuai topik.')
    return ai_write(user)

def ai_rewrite_multi(items):
    k = konteks_waktu()
    parts = []
    for i, it in enumerate(items[:4], 1):
        parts.append('[MATERI ' + str(i) + ']\n'
                     'Judul: ' + it['title'] + '\nIsi: ' + it['summary'][:1500])
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n\n'
            'Berikut beberapa materi tentang topik yang SAMA:\n\n'
            + '\n\n'.join(parts) +
            '\n\nGabungkan menjadi SATU berita KramaNews (350-500 kata) sesuai SEMUA aturan. '
            'PERIKSA DULU: jika peristiwanya lebih lama dari kemarin, TOLAK. '
            'Jika segar: sebutkan NAMA LENGKAP tokoh, jangan sebut media sumber, '
            'awali dengan dateline, salin utuh angka, cantumkan waktu kejadian, '
            'isi deskripsi_gambar dengan kata kunci visual.')
    return ai_write(user, timeout=180)

# ═══ SKOR BREAKING (anti dominasi gempa) ═══

def ambil_magnitude(teks):
    """Ambil angka magnitude dari teks. None jika tidak tertulis jelas."""
    m = re.search(r'(?:magnitudo|magnitude)\s*(?:m)?\s*[:=]?\s*(\d{1,2}[.,]\d{1,2})', teks)
    if not m:
        m = re.search(r'\bm\s*[:=]?\s*(\d{1,2}[.,]\d{1,2})\b', teks)
    if not m:
        m = re.search(r'(\d{1,2}[.,]\d{1,2})\s*(?:magnitude|magnitudo|sr)\b', teks)
    if m:
        try:
            return float(m.group(1).replace(',', '.'))
        except Exception:
            return None
    return None

def skor_domestik(title, summary):
    """Skor breaking SLOT 1. Gempa luar negeri & gempa mikro = 0."""
    t = (title + ' ' + summary).lower()
    skor = 0
    if 'gempa' in t:
        # Gempa hanya breaking jika di Indonesia + magnitude jelas & cukup besar
        if not any(w in t for w in INDO_GEO):
            return 0
        mag = ambil_magnitude(t)
        if mag is None or mag < GEMPA_DOM_MIN:
            return 0
        skor = 60 + min(int(mag), 8)
    hit = sum(1 for k in DOM_KRITIS if k in t)
    if hit:
        skor += 30 + (hit - 1) * 8
    return skor

def skor_dunia(title, summary):
    """Skor breaking SLOT 2. Gempa luar negeri harus M >= GEMPA_DUNIA_MIN jelas."""
    t = (title + ' ' + summary).lower()
    skor = 0
    if 'earthquake' in t or 'gempa' in t:
        mag = ambil_magnitude(t)
        if mag is None or mag < GEMPA_DUNIA_MIN:
            return 0
        skor = 60 + min(int(mag), 9)
    hit = sum(1 for k in DUNIA_KRITIS if k in t)
    if hit:
        skor += 30 + (hit - 1) * 8
    return skor

def cari_gambar_wikimedia(deskripsi):
    """Cari gambar bebas hak cipta di Wikimedia sesuai deskripsi dari AI."""
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
                breaking=False, deskripsi_gambar=''):
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+(.*)$', isi, re.DOTALL)
    dateline = m.group(1).strip() if m else ''
    isi_bersih = m.group(2).strip() if m else isi
    # ═══ FALLBACK GAMBAR WIKIMEDIA ═══
    if not img and deskripsi_gambar:
        img = cari_gambar_wikimedia(deskripsi_gambar)
        if img:
            print('   🖼️ Gambar Wikimedia ditemukan untuk berita ini.')
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
    # Daftarkan judul ke daftar anti-dobel
    JUDUL_TERPAKAI.append(normalisasi_judul(judul))

# ═════════ SESI BREAKING — 3 SLOT ═════════

def sesi_breaking(today_urls, seen):
    made = 0
    slots = BREAKING_MAX_SLOT - len(get_breaking_list())
    print('\n🚨 BREAKING — slot tersedia: ' + str(slots) + '/' + str(BREAKING_MAX_SLOT))
    if slots <= 0:
        return 0

    # Kumpulkan kandidat domestik & dunia sekaligus, beri skor
    cand_dom = collect_candidates(BREAKING_DOMESTIK_FEEDS, today_urls, seen)
    skor_dom = sorted([(c, skor_domestik(c['title'], c['summary'])) for c in cand_dom],
                      key=lambda x: -x[1])
    skor_dom = [x for x in skor_dom if x[1] >= SKOR_BREAKING_MIN]
    print('   🇮🇩 Kandidat breaking domestik layak: ' + str(len(skor_dom)))

    cand_dun = collect_candidates(BREAKING_DUNIA_FEEDS, today_urls, seen)
    skor_dun = sorted([(c, skor_dunia(c['title'], c['summary'])) for c in cand_dun],
                      key=lambda x: -x[1])
    skor_dun = [x for x in skor_dun if x[1] >= SKOR_BREAKING_MIN]
    print('   🌍 Kandidat breaking dunia layak: ' + str(len(skor_dun)))

    # Susun prioritas: slot1 = domestik terkuat, slot2 = dunia terkuat,
    # slot3 = fleksibel (sisa terkuat)
    sisa = ([(c, s, 'dom') for c, s in skor_dom[1:]]
            + [(c, s, 'dun') for c, s in skor_dun[1:]])
    pilihan = []
    if skor_dom:
        pilihan.append(('SLOT 1 (DOMESTIK)', skor_dom[0][0], 'dom'))
    if skor_dun:
        pilihan.append(('SLOT 2 (DUNIA)', skor_dun[0][0], 'dun'))
    if sisa:
        pilihan.append(('SLOT 3 (FLEKSIBEL)', sisa[0][0], sisa[0][2]))

    for label, c, asal in pilihan:
        if slots <= 0:
            break
        # ANTI DOBEL: cek judul sumber sebelum panggil AI (hemat biaya)
        if sudah_serupa(c['title']):
            print('   🗑️ ' + label + ' — sumber dobel dengan berita yang sudah tayang, dilewati')
            continue
        try:
            judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(c)
            # ANTI DOBEL: cek judul hasil AI
            if sudah_serupa(judul):
                print('   🗑️ ' + label + ' — hasil AI dobel, dilewati: ' + judul[:50])
                continue
            blob = (judul + ' ' + isi).lower()
            if asal == 'dun':
                cat = 'internasional'
            elif any(w in blob for w in KALTARA_WORDS):
                cat = 'daerah'
            elif any(w in blob for w in LUAR_NEGERI_WORDS) and 'indonesia' not in blob:
                cat = 'internasional'
            else:
                cat = 'nasional'
            insert_news(judul, isi, ringkasan, cat, get_image(c['entry']),
                        c['link'], c['source'], status='published', breaking=True,
                        deskripsi_gambar=desc_gambar)
            slots -= 1
            made += 1
            today_urls.add(c['link'])
            print('   🚨 ' + label + ': ' + judul)
        except BeritaLama as e:
            print('   🗑️ ' + label + ' — materi lama, ditolak AI: ' + str(e)[:60])
        except Exception as e:
            print('   ⚠️ ' + label + ' gagal:', str(e)[:70])
        time.sleep(2)

    print('   → Breaking tayang: ' + str(made))
    return made

# ═════════ SESI KATEGORI ═════════

def sesi_kategori(cat, need, today_urls, seen, kaltara_min=0):
    print('\n📰 ' + cat.upper() + ' — target ' + str(need))
    sources = list(HUNT.get(cat, []))
    if cat in ('internasional', 'ekonomi', 'olahraga', 'teknologi'):
        random.shuffle(sources)
    cands = collect_candidates(sources, today_urls, seen)
    print('   Kandidat segar (≤' + str(MAX_UMUR_BERITA_JAM) + ' jam): ' + str(len(cands)))
    if not cands:
        print('   ⚠️ Tidak ada kandidat segar — tidak menulis apa-apa (anti berita lama).')
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
            if sudah_serupa(c['title']):
                print('   🗑️ Kaltara sumber dobel, dilewati: ' + c['title'][:50])
                continue
            try:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(c)
                if sudah_serupa(judul):
                    print('   🗑️ Kaltara hasil AI dobel, dilewati: ' + judul[:50])
                    continue
                insert_news(judul, isi, ringkasan, cat, get_image(c['entry']),
                            c['link'], c['source'], status='published',
                            deskripsi_gambar=desc_gambar)
                made += 1
                kaltara_made += 1
                today_urls.add(c['link'])
                print('   🏝️ KALTARA [' + str(kaltara_made) + '/' + str(kaltara_min) + ']: ' + judul)
            except BeritaLama as e:
                print('   🗑️ Kaltara materi lama, ditolak: ' + str(e)[:50])
            except Exception as e:
                print('   ⚠️ Gagal 1 kaltara:', str(e)[:60])
            time.sleep(2)
        print('   → Kaltara: ' + str(kaltara_made) + '/' + str(kaltara_min))

    for g in groups:
        if made >= need:
            break
        items = g['items']
        # ANTI DOBEL: jika topik ini sudah ditulis lewat jalur lain (mis. kaltara), skip
        if any(it['link'] in today_urls for it in items):
            continue
        top = items[0]
        # ANTI DOBEL: cek judul sumber sebelum panggil AI (hemat biaya)
        if sudah_serupa(top['title']):
            print('   🗑️ Sumber dobel dengan berita yang sudah tayang, dilewati: ' + top['title'][:50])
            continue
        try:
            if len(items) > 1:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_multi(items)
                print('       🔗 topik dari ' + str(len(items)) + ' portal')
            else:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(top)
            # ANTI DOBEL: cek judul hasil AI
            if sudah_serupa(judul):
                print('   🗑️ Hasil AI dobel, dilewati: ' + judul[:50])
                continue
            insert_news(judul, isi, ringkasan, cat, get_image(top['entry']),
                        top['link'], top['source'], status='published',
                        deskripsi_gambar=desc_gambar)
            made += 1
            for it in items:
                today_urls.add(it['link'])
            print('   ✅ [' + str(made) + '/' + str(need) + '] TAYANG: ' + judul)
        except BeritaLama as e:
            print('   🗑️ Materi lama, ditolak AI: ' + str(e)[:60])
            continue
        except Exception as e:
            print('   ⚠️ Gagal proses 1 kelompok:', str(e)[:80])
            continue
        time.sleep(2)

    print('   → Hasil: ' + str(made) + ' TAYANG')
    return made

# ═════════ SESI UTAMA ═════════

def run_session():
    now = datetime.now(WIB)
    print('\n' + '=' * 60)
    print(' ⏰ SESI ' + now.strftime('%H:%M') + ' WIB — ' + tanggal_panjang(now.date()))
    print('=' * 60)

    # 1) Cabut breaking yang sudah > 30 menit
    tercabut = expire_breaking(BREAKING_UMUR_MENIT)
    if tercabut:
        print('   (Slot breaking yang kosong otomatis diisi berita biasa N/I/D oleh web)')

    # 2) Muat judul hari ini untuk mesin anti-dobel
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   🧹 Anti-dobel: memuat ' + str(len(JUDUL_TERPAKAI)) + ' judul hari ini dari DB')

    today_urls = get_today_state()
    seen = set()

    # 3) Patroli breaking — SELALU, 24 jam
    total = sesi_breaking(today_urls, seen)

    # 4) Kuota kategori — HANYA jika jam ini ada di jadwal
    quota = JADWAL_JAM.get(now.hour)
    if quota:
        print('\n📊 Kuota jam ' + str(now.hour).zfill(2) + ':00 WIB → '
              + ', '.join(k.upper() + '=' + str(v) for k, v in quota.items()))
        for cat, need in quota.items():
            try:
                if cat == 'daerah':
                    total += sesi_kategori(cat, need, today_urls, seen, kaltara_min=2)
                else:
                    total += sesi_kategori(cat, need, today_urls, seen)
            except Exception as e:
                print('   ❌ Kategori ' + cat + ' error: ' + str(e)[:80])
    else:
        print('\n   (Di luar jadwal kategori 06–20 WIB — hanya patroli breaking)')
    return total

def main_sekali():
    print('🐝 AI WARTAWAN V6.1 — MODE SEKALI JALAN (' + datetime.now(WIB).strftime('%H:%M WIB') + ')')
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ Kunci belum diisi!')
        return
    try:
        total = run_session()
        print(' 🏁 Selesai — total ' + str(total) + ' berita TAYANG.')
    except Exception as e:
        print(' ❌ Gagal: ' + str(e)[:100])

def main():
    print('=' * 60)
    print(' 🐝 AI WARTAWAN KRAMANEWS V6.1 — LOOP TIAP 30 MENIT')
    print(' ⏰ Breaking: patroli 24 jam | Kategori: sesuai JADWAL_JAM (06–20 WIB)')
    print(' ✍️  Penulis: ' + AUTHOR_NAME)
    print(' 💡 Stop: Ctrl+C')
    print('=' * 60)

    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ DEEPSEEK_KEY / SUPABASE_PUBLISHABLE belum diisi!')
        return

    while True:
        try:
            total = run_session()
            print('\n 🏁 Sesi selesai — total ' + str(total) + ' berita TAYANG.')
            print(' ⏳ Menunggu 30 menit...')
            time.sleep(1800)
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