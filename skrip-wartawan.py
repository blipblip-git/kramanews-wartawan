# ══════════════════════════════════════════════════════
#  AI WARTAWAN KRAMANEWS — V6.3.3 (SINDROM PENYANGKALAN DIHABISI)
#  Baru V6.3.3 (audit pemilik: 3 berita berbeda = 3 kalimat
#  penyangkalan narasumber yang sama — tidak profesional):
#   • HAPUS aturan "tulis eksplisit identitas tidak disebutkan"
#     (V6.3.2) — ternyata menciptakan kebiasaan baru: AI menggembung
#     penyangkalan jadi 2 kalimat pengisi di tengah berita.
#   • ATURAN BARU: jika sumber tidak menyebut nama narasumber →
#     cukup laporkan fakta langsung, TANPA kalimat APA PUN tentang
#     ketiadaan narasumber/identitas/laporan — berita profesional
#     tidak pernah membahas ketiadaan narasumbernya.
#   • POLA_LARANG DIPERKUAT (polisi otomatis ai_write): frasa baru
#     diblokir — "identitas narasumber", "tidak disebutkan dalam
#     laporan", "tanpa menyebut nama", "dalam laporan yang beredar",
#     "dalam laporan yang dihimpun", "materi yang tersedia".
#   • Larangan mengarang nama TETAP MUTLAK.
#   • Semua fitur V6.3.2 tetap: scraping 3 lapis (Direct → Resolver
#     Google News → Jina Reader → RSS), aturan spesifisitas lokasi,
#     jadwal & acara, anti-plagiat, anti dobel, anti lama, fix V6.2,
#     breaking 3 slot, expire 30 menit, kuota per jam WITA, Kaltara.
#   • Marker verifikasi: cari kata "KRAMAV633MARKER"
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

# ═══ ZONA WAKTU WITA (UTC+8) — WAKTU TARAKAN/KALTARA ═══
WITA = timezone(timedelta(hours=8))

# ═══ PENGATURAN ═══
BREAKING_MAX_SLOT   = 3      # slot breaking di hero
BREAKING_UMUR_MENIT = 30     # breaking dicabut otomatis setelah 30 menit
MAX_UMUR_BERITA_JAM = 30     # tolak materi RSS lebih tua dari 30 jam
GEMPA_DOM_MIN       = 5.5    # gempa Indonesia: breaking jika M >= ini (tertulis jelas)
GEMPA_DUNIA_MIN     = 6.5    # gempa luar negeri: breaking jika M >= ini (tertulis jelas)
SKOR_BREAKING_MIN   = 30     # skor minimal kandidat breaking
AMBANG_MIRIP        = 0.50   # judul dianggap DOBEL jika kemiripan >= ini (0-1)
SCRAPER_TIMEOUT     = 12     # detik maksimal scraping 1 halaman
SCRAPE_MIN_KARAKTER = 600    # hasil scraping dianggap "kaya" jika >= ini
JINA_READER         = 'https://r.jina.ai/'  # tenaga kedua anti-blokir (gratis)

HARI_ID  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN_ID = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']

# ═══ JADWAL KUOTA PER JAM (WITA — waktu Tarakan) ═══
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

# ═══ USER-AGENTS UNTUK SCRAPING (biar tidak diblokir portal) ═══
UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

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

# ═══ V6.3.2: RESOLVER GOOGLE NEWS ═══

def resolusi_link_google(url):
    """Link news.google.com = halaman perantara. Buka halaman itu,
    ekstrak URL artikel ASLI dari dalam HTML-nya. Return url asli
    (atau url semula jika bukan link Google / gagal resolve)."""
    try:
        if 'news.google.com' not in url:
            return url
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT, allow_redirects=True)
        if not r.ok:
            return url
        html = r.text or ''
        # Pola 1: link asli tertanam sebagai href
        m = re.search(r'href="(https?://(?!news\.google|www\.google)[^"]+)"', html)
        if m:
            kandidat = m.group(1)
            if 'google' not in kandidat:
                return kandidat
        # Pola 2: URL asli di dalam data (encoded articles)
        m = re.search(r'https?://(?!news\.google|www\.google)[A-Za-z0-9\.\-]+(?:/[^\s"\'<>\\]+)+', html)
        if m:
            kandidat = m.group(0)
            if 'google' not in kandidat and any(d in kandidat for d in ('.com', '.id', '.net', '.co', '.org')):
                return kandidat
        return url
    except Exception:
        return url

def scrape_via_jina(url):
    """Tenaga kedua: minta Jina Reader merender halaman (lolos anti-bot).
    Return teks bersih atau ''."""
    try:
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(JINA_READER + url, headers=headers,
                         timeout=SCRAPER_TIMEOUT + 8, allow_redirects=True)
        if not r.ok:
            return ''
        teks = r.text or ''
        # Jina mengembalikan markdown — bersihkan sintaks markdown ringan
        teks = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', teks)   # gambar
        teks = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', teks)  # link → teks
        teks = re.sub(r'[#*_`>]{1,3}', ' ', teks)
        teks = re.sub(r'\s+', ' ', teks).strip()
        return teks if len(teks) >= SCRAPE_MIN_KARAKTER else ''
    except Exception:
        return ''

def _bersihkan_html_artikel(html):
    """Buang bagian non-artikel dari HTML mentah → teks bersih."""
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<nav[^>]*>.*?</nav>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<footer[^>]*>.*?</footer>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<header[^>]*>.*?</header>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<aside[^>]*>.*?</aside>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<form[^>]*>.*?</form>', ' ', html, flags=re.S | re.I)
    html = re.sub(r'<!--.*?-->', ' ', html, flags=re.S)
    html = re.sub(r'</(p|div|h[1-6]|li|tr)>', '\n', html, flags=re.I)
    html = re.sub(r'<br[^>]*>', '\n', html, flags=re.I)
    teks = re.sub(r'<[^>]+>', ' ', html)
    teks = (teks.replace('&nbsp;', ' ').replace('&amp;', '&')
                .replace('&quot;', '"').replace('&#39;', "'")
                .replace('&ldquo;', '"').replace('&rdquo;', '"')
                .replace('&lsquo;', "'").replace('&rsquo;', "'")
                .replace('&mdash;', '—').replace('&ndash;', '–'))
    baris_ok = []
    for b in teks.split('\n'):
        b = re.sub(r'\s+', ' ', b).strip()
        if len(b) < 60:
            continue
        low = b.lower()
        if any(x in low for x in ('baca juga', 'simak juga', 'ikuti kami',
                                  'copyright', 'hak cipta', 'cookie',
                                  'subscribe', 'newsletter', 'berlangganan',
                                  'dapatkan update', 'baca selengkapnya')):
            continue
        baris_ok.append(b)
    if not baris_ok:
        return ''
    return re.sub(r'\s+', ' ', ' '.join(baris_ok)).strip()[:6000]

def scrape_artikel(url):
    """RANTAI 3 LAPIS (V6.3.2):
    1. Direct fetch artikel asli (dengan resolver Google News)
    2. Jina Reader (lolos WAF/anti-bot)
    3. Gagal semua → '' (caller fallback ke ringkasan RSS)
    """
    if not url:
        return ''
    # ── Lapis 0: resolve link Google News ke artikel asli ──
    url_asli = resolusi_link_google(url)
    # ── Lapis 1: direct fetch ──
    try:
        headers = {
            'User-Agent': random.choice(UA_LIST),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.8',
        }
        r = requests.get(url_asli, headers=headers, timeout=SCRAPER_TIMEOUT, allow_redirects=True)
        if r.ok:
            hasil = _bersihkan_html_artikel(r.text or '')
            if len(hasil) >= SCRAPE_MIN_KARAKTER:
                return hasil
    except Exception:
        pass
    # ── Lapis 2: Jina Reader (anti anti-bot) ──
    hasil = scrape_via_jina(url_asli)
    if hasil:
        return hasil
    # ── Lapis 3: coba Jina pada url semula (kalau resolusi gagal tadi) ──
    if url_asli != url:
        hasil = scrape_via_jina(url)
        if hasil:
            return hasil
    return ''

def ambil_materi_kaya(c):
    """Scraping artikel asli; gagal → fallback ringkasan RSS. Return (materi, kaya_bool)."""
    scraped = scrape_artikel(c.get('link', ''))
    if scraped and len(scraped) >= SCRAPE_MIN_KARAKTER:
        print('       📥 Scraping artikel asli: ' + str(len(scraped)) + ' karakter')
        return scraped, True
    print('       ↩️ Scraping gagal/pendek — pakai ringkasan RSS')
    return c.get('summary', ''), False

# ═══ ANTI BERITA DOBEL ═══

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

JUDUL_TERPAKAI = []

def sudah_serupa(judul):
    j = normalisasi_judul(judul)
    if not j:
        return False
    ki = kata_inti(judul)
    for t in JUDUL_TERPAKAI:
        if not t:
            continue
        if SequenceMatcher(None, j, t).ratio() >= AMBANG_MIRIP:
            return True
        kt = kata_inti(t)
        if ki and kt:
            sama = ki & kt
            if len(sama) >= 3 and len(sama) / min(len(ki), len(kt)) >= 0.7:
                return True
    return False

def muat_judul_hari_ini():
    out = []
    try:
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=300')
        today = datetime.now(WITA).date()
        for row in rows:
            try:
                d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
                if d == today and row.get('title'):
                    out.append(normalisasi_judul(row['title']))
            except Exception:
                pass
    except Exception as e:
        print('   ⚠️ Gagal memuat judul hari ini:', str(e)[:60])
    return out

# ═══ KONTEKS WAKTU DINAMIS (WITA) ═══
def tanggal_panjang(d):
    return HARI_ID[d.weekday()] + ' (' + str(d.day) + ' ' + BULAN_ID[d.month] + ' ' + str(d.year) + ')'

def konteks_waktu():
    now = datetime.now(WITA)
    kemarin = (now - timedelta(days=1)).date()
    return {'hari_ini': tanggal_panjang(now.date()),
            'kemarin': tanggal_panjang(kemarin),
            'tahun': str(now.year)}

def tanggal_publikasi_str(entry):
    t = entry.get('published_parsed') or entry.get('updated_parsed')
    if not t:
        return None
    try:
        pub = datetime.fromtimestamp(mktime(t), tz=timezone.utc).astimezone(WITA)
        return tanggal_panjang(pub.date())
    except Exception:
        return None

def build_system_prompt():
    k = konteks_waktu()
    return """Kamu adalah AI Wartawan profesional portal berita KramaNews Indonesia.
KRAMAV633MARKER — V6.3.3: berita bersih, spesifik, tanpa kalimat penyangkalan.

TUGAS: Tulis ulang materi sumber menjadi berita orisinal KramaNews.

═══ ATURAN WAKTU (WAJIB) ═══
- HARI INI adalah """ + k['hari_ini'] + """.
- KEMARIN adalah """ + k['kemarin'] + """.
- Tahun berjalan: """ + k['tahun'] + """.
- Materi sumber SUDAH DIVERIFIKASI SISTEM: segar, maksimal 30 jam.
- WAJIB: kejadian dalam berita diberi waktu KONKRET sesuai tanggal
  publikasi sumber yang diberikan di pesan user.
- DILARANG KERAS menulis frasa (atau variannya):
  ❌ "belum dikonfirmasi waktu pasti kejadian"
  ❌ "waktu kejadian belum dikonfirmasi"
- DILARANG mengarang JAM spesifik jika tidak tertulis di materi.
- DILARANG KERAS menulis tanggal dari tahun sebelum """ + k['tahun'] + """.
- TOLAK ({"tolak": ...}) HANYA jika ada tanggal peristiwa TERTULIS
  EKSPLISIT di materi yang jelas lebih lama dari kemarin.

ATURAN JADWAL & ACARA (WAJIB):
- Jika berita menyebut ACARA/LAGA/KEJADIAN LAINNYA (jadwal pertandingan,
  peresmian, kunjungan, agenda berikutnya):
  ✅ Tanggal TERTULIS di materi → WAJIB salin lengkap:
     "...dijadwalkan menghadapi Union Berlin pada Sabtu (20 September 2026)..."
  ✅ Sumber hanya frasa relatif ("pekan ini", "akhir pekan") → salin
     APA ADUNA — dilarang mengarang tanggal dari frasa relatif.
- DILARANG menyisakan kejadian penting tanpa keterangan waktu sama sekali.

ATURAN SPESIFISITAS LOKASI (WAJIB):
- Peristiwa dengan WILAYAH TERDAMPAK (karhutla/asap, banjir, gempa,
  kekeringan, krisis, erupsi, dsb) WAJIB menyebut daerah SPESIFIK:
  ✅ "asap menyelimuti Palangka Raya, Pontianak, dan Pangkalan Bun..."
  ❌ "menyelimuti sejumlah daerah di Indonesia..." (KABUR — DILARANG
     jika sumber menyebut nama daerahnya)
- Jika sumber menyebut nama provinsi/kota yang terdampak → WAJIB
  dituliskan semua (atau minimal 3 yang terpenting) di dalam berita.
- Frasa kabur seperti "sejumlah daerah", "beberapa wilayah", "berbagai
  tempat" DILARANG digunakan sebagai pengganti nama daerah yang ada
  di materi sumber.
- Jika sumber MEMANG tidak menyebut daerah spesifik → boleh gunakan
  frasa umum, jangan mengarang nama daerah.

ATURAN NARASUMBER (WAJIB — DIREVISI TOTAL V6.3.3):
- Jika materi menyebut NAMA ORANG → WAJIB kutip dengan jabatan lengkap:
  ✅ "Ketua DPRD Kaltara, [Nama], menyatakan..."
  ❌ "DPRD Kaltara menyatakan..." (tanpa nama, padahal nama ada — DILARANG)
- Jika materi TIDAK menyebut nama orang → CUKUP LAPORKAN FAKTA
  LANGSUNG: apa, di mana, kapan, bagaimana. SELESAI.
- ═══ ATURAN EMAS V6.3.3 ═══
  DILARANG KERAS menulis KALIMAT APA PUN yang membahas KETIADAAN
  narasumber/identitas/sumber — berita profesional TIDAK PERNAH
  mengumumkan kekurangan narasumbernya di tengah berita:
  ❌ "identitas narasumber tidak disebutkan dalam laporan"
  ❌ "identitas narasumber tidak disebutkan secara eksplisit"
  ❌ "tidak disebutkan nama pejabat maupun petugas yang berwenang"
  ❌ "rincian tidak dapat dipastikan dari materi yang tersedia"
  ❌ "keterangan disampaikan tanpa menyebut nama pejabat"
  Kalimat-kalimat semacam itu = KALIMAT SAMPAH pengisi, dan akan
  MENYEBABKAN BERITA DITOLAK SISTEM.
- DILARANG KERAS frasa atribusi kosong: "dilaporkan bahwa...",
  "menurut informasi yang diterima...", "diduga kuat...", "kabarnya...",
  "dikabarkan...".
- DILARANG MENGARANG nama tokoh yang tidak ada di materi sumber.

ATURAN ANTI-PLAGIAT (WAJIB — MATERI KAYA):
- Materi sumber hanyalah FAKTA mentah — tulis ulang dengan kalimatmu sendiri.
- DILARANG menyalin kalimat sumber secara verbatim lebih dari 5 kata berurutan.
- Yang boleh disalin persis: nama, jabatan, angka, dan kutipan langsung
  di dalam tanda kutip.
- Hasil akhir harus terasa KRAMANEWS, bukan salinan portal sumber.

ATURAN PANJANG (WAJIB):
- Target jumlah kata DIBERIKAN di pesan user — IKUTI target itu.
- DILARANG menggembung berita dengan kalimat kosong, penyangkalan,
  atau pengulangan demi mencapai target kata.
- Setiap kalimat WAJIB membawa informasi baru dari sumber.
- Jika isi berita menjanjikan data (jadwal, daftar, angka) yang TIDAK
  ada di materi sumber → UBAH JUDUL agar tidak menjanjikan data itu.

ATURAN GAYA PENULISAN (WAJIB):
- Tulis seperti wartawan portal besar Indonesia. LAPOR BERITA LANGSUNG.
- DILARANG KERAS menyebut nama portal, media, situs, atau sumber berita mana pun.
- JANGAN menjelaskan dari mana informasi didapat. Ceritakan langsung.
- Kalimat pendek, jelas, padat.

ATURAN DATELINE (WAJIB):
- Baris pertama isi berita diawali: "KOTA, PROVINSI/NEGARA - ".
  Contoh: "TARAKAN, KALTARA - ...", "MUNICH, JERMAN - ...".
- Jika lokasi tidak ada: "INDONESIA - ".

ATURAN NAMA ASING (WAJIB — JANGAN MENERJEMAHKAN):
- Nama partai/organisasi/lembaga/perusahaan asing ditulis APA ADUNA + negaranya.
  BENAR: "Partai AfD (Jerman)", "Bayern Munich".
- Nama tokoh asing: ejaan asli/lazim di media Indonesia.

ATURAN DATA & ANGKA (WAJIB):
- Angka dari materi sumber WAJIB SALIN UTUH & PERSIS (contoh: "5,02 persen").
- DILARANG menambah angka yang tidak ada di materi sumber.

ATURAN JUDUL (WAJIB):
- Judul ORISINAL maksimal 10 kata.
- Judul HARUS mencerminkan isi berita — tidak menjanjikan data yang tidak ditulis.

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
 "waktu_kejadian": "Hari (Tanggal Bulan """ + k['tahun'] + """)"}
INGAT: frasa tentang ketiadaan narasumber DILARANG — cukup laporkan
fakta langsung. Tanpa bukti tertulis peristiwa lama = TULIS BERITA."""

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
    today = datetime.now(WITA).date()
    urls = set()
    for row in rows:
        try:
            d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
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
                        'source': sname, 'entry': entry,
                        'tgl_pub': tanggal_publikasi_str(entry)})
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
    # ═══ PEMERIKSA KUALITAS V6.3.3 — DIPERKUAT ═══
    pola_larang = [
        # frasa waktu yang dilarang (warisan V6.3)
        'belum dikonfirmasi waktu', 'waktu kejadian belum',
        'belum dikonfirmasi kapan',
        # frasa atribusi kosong
        'menurut informasi yang diterima', 'diduga kuat',
        'kabarnya', 'dikabarkan',
        # ═══ V6.3.3: sindrom penyangkalan narasumber ═══
        'identitas narasumber',
        'tidak disebutkan dalam laporan',
        'tidak disebutkan secara eksplisit',
        'tanpa menyebut nama',
        'tanpa menyebut nama pejabat',
        'dalam laporan yang beredar',
        'dalam laporan yang dihimpun',
        'materi yang tersedia',
        'tidak dapat dipastikan',
        'keterangan disampaikan tanpa',
    ]
    isi_lower = isi.lower()
    tertangkap = [p for p in pola_larang if p in isi_lower]
    if tertangkap:
        raise Exception('diblokir pemeriksa V6.3.3: ' + str(tertangkap[0])[:50])
    # URUTAN KONSISTEN: judul, isi, ringkasan, WAKTU, GAMBAR
    return judul, isi, ringkasan, waktu, gambar

def target_kata(materi_len):
    if materi_len < 500:
        return ('200-300 kata (3-5 paragraf) — sumber ringkas, tulis PADAT, '
                'dilarang menggembung dengan kalimat pengisi.')
    return '350-500 kata (5-7 paragraf).'

def ai_rewrite_single(c):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' — sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita, contoh: '
                     '"pada ' + tgl + '" (ini hari ini atau kemarin).\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia — namun sistem sudah '
                     'memverifikasi umur sumber maksimal 30 jam.\n'
                     'WAJIB: tulis kejadian sebagai peristiwa TERKINI (hari ini atau '
                     'kemarin: ' + k['hari_ini'] + ' / ' + k['kemarin'] + ') dengan tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + target_kata(len(materi)) + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi + '\n\n'
            'Tulis ulang sesuai SEMUA aturan:\n'
            '- TANGGAL KONKRET di isi berita — dilarang frasa "belum dikonfirmasi '
            'waktu pasti kejadian".\n'
            '- SPESIFIK: peristiwa wilayah terdampak WAJIB menyebut nama daerah yang '
            'tertulis di materi (dilarang "sejumlah daerah" jika nama daerah ada).\n'
            '- Kutipan lembaga (DPRD/BMKG/dll): sebut NAMA orangnya jika ada di materi. '
            'Jika tidak ada nama: cukup laporkan fakta langsung — DILARANG menulis '
            'kalimat apa pun tentang ketiadaan narasumber/identitas (berita akan '
            'DITOLAK sistem).\n'
            '- ACARA/LAGA lain: tulis tanggalnya jika tertulis; frasa relatif salin apa adanya.\n'
            '- Nama tokoh wajib dikutip dengan jabatan; tanpa nama = fakta langsung.\n'
            '- Tulis ulang dengan kalimatmu sendiri — dilarang menjiplak kalimat sumber.\n'
            '- Jangan sebut portal/media sumber, awali dengan dateline lokasi, '
            'salin utuh semua angka, isi deskripsi_gambar dengan kata kunci visual.')
    return ai_write(user)

def ai_rewrite_multi(items):
    k = konteks_waktu()
    bagian = []
    total_len = 0
    tgl = None
    for i, it in enumerate(items[:4], 1):
        materi, kaya = ambil_materi_kaya(it)
        if kaya:
            total_len += len(materi)
        else:
            total_len += len(it.get('summary', ''))
        if it.get('tgl_pub') and not tgl:
            tgl = it['tgl_pub']
        bagian.append('[MATERI ' + str(i) + ']\n'
                      'Judul: ' + it['title'] + '\nIsi: ' + materi[:2000])
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' — sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia — sistem sudah memverifikasi '
                     'umur sumber maksimal 30 jam. Tulis kejadian sebagai peristiwa TERKINI '
                     '(' + k['hari_ini'] + ' / ' + k['kemarin'] + ') dengan tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + target_kata(total_len) + '\n\n'
            'Berikut beberapa materi tentang topik yang SAMA:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita KramaNews sesuai SEMUA aturan:\n'
            '- TANGGAL KONKRET di isi berita — dilarang frasa "belum dikonfirmasi '
            'waktu pasti kejadian".\n'
            '- SPESIFIK: wilayah terdampak wajib menyebut nama daerah dari materi.\n'
            '- Kutipan lembaga: sebut nama orangnya jika ada; jika tidak, cukup '
            'laporkan fakta langsung — DILARANG menulis kalimat tentang ketiadaan '
            'narasumber/identitas (berita akan DITOLAK sistem).\n'
            '- ACARA/LAGA: tanggal jika tertulis; frasa relatif salin apa adanya.\n'
            '- Tulis ulang dengan kalimatmu sendiri — dilarang menjiplak kalimat sumber.\n'
            '- Jangan sebut media sumber, awali dengan dateline, salin utuh angka, '
            'isi deskripsi_gambar dengan kata kunci visual.')
    return ai_write(user, timeout=180)

# ═══ SKOR BREAKING (anti dominasi gempa) ═══

def ambil_magnitude(teks):
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
    t = (title + ' ' + summary).lower()
    skor = 0
    if 'gempa' in t:
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
    JUDUL_TERPAKAI.append(normalisasi_judul(judul))

# ═════════ SESI BREAKING — 3 SLOT ═════════

def sesi_breaking(today_urls, seen):
    made = 0
    slots = BREAKING_MAX_SLOT - len(get_breaking_list())
    print('\n🚨 BREAKING — slot tersedia: ' + str(slots) + '/' + str(BREAKING_MAX_SLOT))
    if slots <= 0:
        return 0

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
        if sudah_serupa(c['title']):
            print('   🗑️ ' + label + ' — sumber dobel dengan berita yang sudah tayang, dilewati')
            continue
        try:
            judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(c)
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
            print('   🗑️ ' + label + ' — materi TERTULIS jelas lama, ditolak AI: ' + str(e)[:60])
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
                print('   🗑️ Kaltara materi TERTULIS jelas lama, ditolak: ' + str(e)[:50])
            except Exception as e:
                print('   ⚠️ Gagal 1 kaltara:', str(e)[:60])
            time.sleep(2)
        print('   → Kaltara: ' + str(kaltara_made) + '/' + str(kaltara_min))

    for g in groups:
        if made >= need:
            break
        items = g['items']
        if any(it['link'] in today_urls for it in items):
            continue
        top = items[0]
        if sudah_serupa(top['title']):
            print('   🗑️ Sumber dobel dengan berita yang sudah tayang, dilewati: ' + top['title'][:50])
            continue
        try:
            if len(items) > 1:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_multi(items)
                print('       🔗 topik dari ' + str(len(items)) + ' portal')
            else:
                judul, isi, ringkasan, waktu, desc_gambar = ai_rewrite_single(top)
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
            print('   🗑️ Materi TERTULIS jelas lama, ditolak AI: ' + str(e)[:60])
            continue
        except Exception as e:
            print('   ⚠️ Gagal proses 1 kelompok:', str(e)[:80])
            continue
        time.sleep(2)

    print('   → Hasil: ' + str(made) + ' TAYANG')
    return made

# ═════════ SESI UTAMA ═════════

def run_session():
    now = datetime.now(WITA)
    print('\n' + '=' * 60)
    print(' ⏰ SESI ' + now.strftime('%H:%M') + ' WITA — ' + tanggal_panjang(now.date()))
    print('=' * 60)

    tercabut = expire_breaking(BREAKING_UMUR_MENIT)
    if tercabut:
        print('   (Slot breaking yang kosong otomatis diisi berita biasa N/I/D oleh web)')

    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   🧹 Anti-dobel: memuat ' + str(len(JUDUL_TERPAKAI)) + ' judul hari ini dari DB')

    today_urls = get_today_state()
    seen = set()

    total = sesi_breaking(today_urls, seen)

    quota = JADWAL_JAM.get(now.hour)
    if quota:
        print('\n📊 Kuota jam ' + str(now.hour).zfill(2) + ':00 WITA → '
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
        print('\n   (Di luar jadwal kategori 06–20 WITA — hanya patroli breaking)')
    return total

def main_sekali():
    print('🐝 AI WARTAWAN V6.3.3 — MODE SEKALI JALAN (' + datetime.now(WITA).strftime('%H:%M WITA') + ')')
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
    print(' 🐝 AI WARTAWAN KRAMANEWS V6.3.3 — LOOP TIAP 30 MENIT (WITA)')
    print(' 📥 Scraping: Direct → Google News Resolver → Jina Reader → RSS')
    print(' ✂️  Polisi frasa: waktu + penyangkalan narasumber (DIPERKUAT)')
    print(' ⏰ Breaking: patroli 24 jam | Kategori: sesuai JADWAL_JAM (06–20 WITA)')
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