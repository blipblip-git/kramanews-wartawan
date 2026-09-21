# ══════════════════════════════════════════════════════
#  PART 1
#  KONFIGURASI, JADWAL & SUMBER
#  (versi file resmi = baca PART TERAKHIR/4B — bagian ini
#   sengaja TANPA klaim versi agar tidak menyesatkan pembaca)
#  Isi: import, konstanta, ESPN_LIGA, JADWAL_JAM,
#  DOMAIN_KESEHATAN, DOMAIN_TEKNOLOGI, HUNT
# ══════════════════════════════════════════════════════

import requests
import json
import time
import re
import os
import sys
import random
import base64
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

WITA = timezone(timedelta(hours=8))

BREAKING_MAX_SLOT   = 3
BREAKING_UMUR_MENIT = 30
MAX_UMUR_BERITA_JAM = 30
JENDELA_DOBEL_JAM   = 36
GEMPA_DOM_MIN       = 5.5
GEMPA_DUNIA_MIN     = 6.5
SKOR_BREAKING_MIN   = 30
AMBANG_MIRIP        = 0.50
SCRAPER_TIMEOUT     = 12
SCRAPE_MIN_KARAKTER = 600
JINA_READER         = 'https://r.jina.ai/'
GAMBAR_MIN_LEBAR    = 400

BLUR_SKOR_MINIMUM  = 7
VISION_TIMEOUT     = 30

MATCH_MIN_KATA     = 3
MATCH_MIN_RASIO    = 0.60

BARAT_MAX_HARI     = 1
KATA_BARAT_USA     = ['amerika', 'u.s', 'washington', 'trump', 'biden', 'new york', 'california', 'texas']
KATA_BARAT_RUSIA   = ['rusia', 'russia', 'moskow', 'moscow', 'putin', 'ukraina', 'ukraine']
KATA_BARAT_EROPA   = ['eropa', 'europe', 'jerman', 'germany', 'perancis', 'france', 'inggris',
                      'britain', 'italia', 'italy', 'spanyol', 'spain', 'paris', 'berlin', 'london']
KATA_TT            = ['timur tengah', 'middle east', 'gaza', 'israel', 'palestina', 'iran',
                      'iraq', 'suriah', 'syria', 'saudi', 'yaman', 'yemen', 'uni emirat',
                      'emirates', 'qatar', 'kuwait', 'libanon', 'jordan', 'turki']
KATA_ASEAN         = ['asean', 'malaysia', 'thailand', 'vietnam', 'filipina', 'philippines',
                      'singapura', 'singapore', 'indonesia', 'myanmar', 'kamboja', 'cambodia',
                      'laos', 'brunei', 'timor leste', 'jakarta', 'bangkok', 'manila',
                      'kuala lumpur', 'hanoi']

HARI_ID  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN_ID = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']

IDX_JAM = [11, 14, 17]
IDX_Sumber = 'Yahoo Finance'
IDX_EMITEN = [
    ('BBCA.JK', 'BCA'), ('BBRI.JK', 'BRI'), ('BMRI.JK', 'Mandiri'),
    ('BBNI.JK', 'BNI'), ('TLKM.JK', 'Telkom'), ('ASII.JK', 'Astra International'),
    ('GOTO.JK', 'GoTo Gojek Tokopedia'), ('ANTM.JK', 'Aneka Tambang'),
    ('ICBP.JK', 'Indofood CBP'), ('UNVR.JK', 'Unilever Indonesia'),
]

ESPN_LIGA = [
    ('eng.1',        'Premier League (Inggris)'),
    ('esp.1',        'La Liga (Spanyol)'),
    ('ita.1',        'Serie A (Italia)'),
    ('ger.1',        'Bundesliga (Jerman)'),
    ('fra.1',        'Ligue 1 (Prancis)'),
    ('ned.1',        'Eredivisie (Belanda)'),
    ('uefa.champions', 'Liga Champions'),
    ('uefa.europa',  'Liga Europa'),
    ('uefa.europa.conf', 'Liga Conference'),
    ('idn.1',        'Liga 1 (Indonesia)'),
]
ESPN_NBA = ('basketball/nba', 'NBA')
ESPN_SITE = 'https://site.api.espn.com/apis/site/v2/sports/'
ESPN_CORE = 'https://sports.core.api.espn.com/v2/sports/soccer/leagues/'

# OLAHRAGA: 07, 11 (Rangkuman Umum — V6.5.2), 13, 17, 20
# KESEHATAN: 10/15/20 perputaran domain — TEKNOLOGI: 08/13/18
JADWAL_JAM = {
    6:  {'nasional': 1, 'daerah': 2, 'ekonomi': 1},
    7:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'olahraga': 1},
    8:  {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'teknologi': 1},
    9:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'hiburan': 1},
    10: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'kesehatan': 1},
    11: {'nasional': 1, 'daerah': 2, 'ekonomi': 1, 'olahraga': 1},
    12: {'nasional': 1, 'daerah': 2},
    13: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'teknologi': 1, 'olahraga': 1},
    14: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1},
    15: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'kesehatan': 1},
    16: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'hiburan': 1},
    17: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'olahraga': 1},
    18: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'teknologi': 1},
    19: {'nasional': 1},
    20: {'hiburan': 1, 'olahraga': 1, 'kesehatan': 1},
}

TOPIK_NASIONAL_WAJIB = [
    ['makan bergizi gratis', 'mbg'],
    ['koperasi desa merah putih', 'kdmp'],
    ['menteri meresmikan', 'kunjungan kerja menteri',
     'menteri mengunjungi', 'menteri meninjau',
     'program menteri', 'kementerian meresmikan'],
]

KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata', 'amal', 'kayu putih']

UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

GAMBAR_SAMPAH_POLA = [
    'logo', 'icon', 'icon_', 'banner', 'ads', 'advert', 'sponsor',
    'placeholder', 'default', 'no-image', 'noimage', 'avatar',
    'thumb_100', 'thumb_150', 'thumb_200', '/100x', '/150x', '/200x',
    '100x100', '150x150', '200x200', '100-', '150-', '200-',
    'profile', 'favicon', 'sprite', 'watermark', 'blank', 'pixel',
]

GAMBAR_LARANG_KATA = [
    # hewan
    'animal', 'dog', 'cat', 'bird', 'monkey', 'elephant', 'tiger', 'lion',
    'snake', 'crocodile', 'lizard', 'frog', 'fish', 'shark', 'whale',
    'insect', 'butterfly', 'bee', 'spider', 'rat', 'mouse', 'horse',
    'cow', 'goat', 'sheep', 'pig', 'chicken', 'rooster', 'duck', 'goose',
    'rabbit', 'deer', 'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl',
    'kucing', 'anjing', 'burung', 'ular', 'kuda', 'sapi', 'ayam', 'bebek',
    'kambing', 'harimau', 'singa', 'gajah', 'monyet', 'buaya', 'ikan',
    'pet', 'wildlife', 'fauna', 'orangutan', 'komodo',
    # tempat ibadah
    'mosque', 'masjid', 'church', 'gereja', 'cathedral', 'temple',
    'pura', 'vihara', 'pagoda', 'synagogue', 'shrine', 'monastery',
    'worship', 'ibadah',
    # manusia
    'human', 'people', 'person', 'crowd', 'portrait', 'woman', 'women',
    'girl', 'child', 'children', 'soldier', 'manusia', 'warga',
    'kerumunan', 'wajah',
]

KATA_ANALISIS = ['analisis', 'soroti', 'opini', 'tinjauan',
                 'analysis', 'opinion', 'editorial']

JANJI_JADWAL  = ['jadwal', 'schedule']
JANJI_TABEL   = ['klasemen', 'standing', 'ranking', 'peringkat']
JANJI_ANGKA   = ['hasil', 'skor', 'result']

# KESEHATAN — 8 domain perputaran (slot 10=+0, 15=+1, 20=+2)
DOMAIN_KESEHATAN = [
    {'nama': 'Nutrisi & Makanan Sehat', 'query': [
        ('makanan sehat nutrisi pakar gizi', 'id'),
        ('makanan tidak sehat bahaya', 'id'),
        ('manfaat buah sayur', 'id'),
    ]},
    {'nama': 'Tidur & Kesehatan Mental', 'query': [
        ('pola tidur sehat bahaya begadang', 'id'),
        ('kelola stres kecemasan psikolog', 'id'),
        ('sleep health expert tips', 'en'),
    ]},
    {'nama': 'Gerak Tubuh & Kebugaran', 'query': [
        ('manfaat jalan kaki olahraga ringan', 'id'),
        ('olahraga kebugaran tips ahli', 'id'),
    ]},
    {'nama': 'Anak & Keluarga', 'query': [
        ('kesehatan anak imunisasi dokter', 'id'),
        ('kesehatan gigi anak', 'id'),
        ('gizi anak MPASI', 'id'),
    ]},
    {'nama': 'Pencegahan Penyakit', 'query': [
        ('cegah diabetes hipertensi gaya hidup', 'id'),
        ('tanda awal stroke serangan jantung', 'id'),
    ]},
    {'nama': 'Bahaya Kebiasaan', 'query': [
        ('bahaya rokok vape tubuh', 'id'),
        ('mitos fakta suplemen', 'id'),
    ]},
    {'nama': 'Kesehatan Musiman Tropis', 'query': [
        ('mencegah demam berdarah DBD', 'id'),
        ('penyakit musim hujan', 'id'),
    ]},
    {'nama': 'Kesehatan Lansia', 'query': [
        ('jaga kesehatan lansia', 'id'),
        ('senior health tips doctor', 'en'),
    ]},
]

# TEKNOLOGI — 6 domain perputaran (slot 08=+0, 13=+1, 18=+2)
DOMAIN_TEKNOLOGI = [
    {'nama': 'Gadget & Smartphone', 'aturan':
        ('Berita HARUS BANYAK, boleh hingga 2 halaman. WAJIB memuat '
         'SEBANYAK mungkin gadget/baru yang ada di materi sekaligus. '
         'SPESIFIKASI setiap gadget WAJIB lengkap (layar, chipset, '
         'RAM, kamera, baterai, sistem operasi — sesuai yang tertulis '
         'di materi). Estimasi harga WAJIB disebut jika ada di materi.'),
     'query': [
        ('smartphone launch spesifikasi harga', 'id'),
        ('gadget baru rilis Indonesia', 'id'),
        ('new smartphone launch specs price', 'en'),
    ]},
    {'nama': 'AI & Kecerdasan Buatan', 'aturan':
        ('Berita HARUS PANJANG dan LENGKAP, hingga 2 halaman. '
         'WAJIB membahas perkembangan AI TERKINI SELURUH DUNIA yang '
         'ada di materi: pemain barunya, kapabilitasnya, dampaknya, '
         'angka & tanggal persis dari materi.'),
     'query': [
        ('artificial intelligence development', 'en'),
        ('AI Indonesia terkini', 'id'),
        ('kecerdasan buatan terbaru', 'id'),
    ]},
    {'nama': 'Aplikasi & Internet', 'aturan':
        ('Berita HARUS LENGKAP dan BANYAK — gabungkan semua materi '
         'aplikasi/internet yang tersedia menjadi satu berita kaya.'),
     'query': [
        ('aplikasi baru populer', 'id'),
        ('fitur media sosial terbaru', 'id'),
        ('internet Indonesia kecepatan', 'id'),
    ]},
    {'nama': 'Startup & Ekonomi Digital', 'aturan':
        ('Berita HARUS LENGKAP dan BANYAK — pendanaan, valuasi, '
         'ekspansi, e-commerce, fintech: semua angka WAJIB persis '
         'dari materi.'),
     'query': [
        ('startup Indonesia pendanaan', 'id'),
        ('e-commerce fintech Indonesia', 'id'),
        ('startup funding tech asia', 'en'),
    ]},
    {'nama': 'Keamanan Digital', 'aturan':
        ('Jika materi keamanan digital KURANG, BOLEH menambahkan '
         'berita teknologi lainnya yang ada di materi sumber agar '
         'berita tetap kaya (isi silang khusus domain ini).'),
     'query': [
        ('kebocoran data keamanan', 'id'),
        ('scam online modus', 'id'),
        ('cyber security breach', 'en'),
    ]},
    {'nama': 'Inovasi & Sains Teknologi', 'aturan':
        ('Berita HARUS LENGKAP dan BANYAK — inovasi, riset, luar '
         'angkasa, kendaraan listrik: semua yang ada di materi '
         'dibahas menyeluruh.'),
     'query': [
        ('kendaraan listrik teknologi', 'id'),
        ('space technology innovation', 'en'),
        ('inovasi teknologi riset', 'id'),
    ]},
]

def GN(q, lang='id', label=None):
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
        RSSF('https://news.okezone.com/rss', 'Okezone'),
        GN('pemerintah indonesia', 'id', 'Google News Nasional'),
        GN('dpr indonesia', 'id', 'Google News Nasional'),
        GN('Prabowo Subianto', 'id', 'Google News Presiden Prabowo'),
        GN('Gibran Rakabuming', 'id', 'Google News Wapres Gibran'),
        GN('Makan Bergizi Gratis MBG', 'id', 'Google News MBG'),
        GN('Koperasi Desa Merah Putih', 'id', 'Google News KDMP'),
        GN('menteri meresmikan', 'id', 'Google News Menteri Resmikan'),
        GN('kunjungan kerja menteri indonesia', 'id', 'Google News Menteri Kunjungan'),
        GN('menteri indonesia program kementerian', 'id', 'Google News Program Kementerian'),
    ],
    'daerah': [
        RSSF('https://kaltara.tribunnews.com/rss', 'Tribun Kaltara'),
        RSSF('https://kaltim.tribunnews.com/rss', 'Tribun Kaltim'),
        GN('Tarakan', 'id', 'Google News Tarakan'),
        GN('Kaltara', 'id', 'Google News Kaltara'),
        RSSF('https://jatim.tribunnews.com/rss', 'Tribun Jatim'),
        RSSF('https://jateng.tribunnews.com/rss', 'Tribun Jateng'),
        RSSF('https://jabar.tribunnews.com/rss', 'Tribun Jabar'),
        RSSF('https://dki.tribunnews.com/rss', 'Tribun DKI Jakarta'),
        GN('Surabaya', 'id', 'Google News Surabaya'),
        GN('Semarang', 'id', 'Google News Semarang'),
        GN('Bandung', 'id', 'Google News Bandung'),
        RSSF('https://sumut.tribunnews.com/rss', 'Tribun Sumut'),
        RSSF('https://sumsel.tribunnews.com/rss', 'Tribun Sumsel'),
        GN('Medan', 'id', 'Google News Medan'),
        GN('Palembang', 'id', 'Google News Palembang'),
        GN('Pekanbaru', 'id', 'Google News Pekanbaru'),
        GN('Padang', 'id', 'Google News Padang'),
        RSSF('https://sulsel.tribunnews.com/rss', 'Tribun Sulsel'),
        GN('Makassar', 'id', 'Google News Makassar'),
        GN('Manado', 'id', 'Google News Manado'),
        GN('Kalimantan Barat', 'id', 'Google News Kalbar'),
        GN('Pontianak', 'id', 'Google News Pontianak'),
        GN('Kalimantan Selatan', 'id', 'Google News Kalsel'),
        GN('Banjarmasin', 'id', 'Google News Banjarmasin'),
        GN('Kalimantan Tengah', 'id', 'Google News Kalteng'),
        GN('Palangka Raya', 'id', 'Google News Palangka Raya'),
        GN('Bali', 'id', 'Google News Bali'),
        GN('Denpasar', 'id', 'Google News Denpasar'),
        GN('Nusa Tenggara Barat', 'id', 'Google News NTB'),
        GN('Mataram', 'id', 'Google News Mataram'),
        GN('Nusa Tenggara Timur', 'id', 'Google News NTT'),
        GN('Kupang', 'id', 'Google News Kupang'),
        GN('Papua', 'id', 'Google News Papua'),
        GN('Jayapura', 'id', 'Google News Jayapura'),
        GN('Maluku', 'id', 'Google News Maluku'),
        GN('Ambon', 'id', 'Google News Ambon'),
        GN('Gorontalo', 'id', 'Google News Gorontalo'),
        GN('Batam', 'id', 'Google News Batam'),
    ],
    'internasional_asean': [
        RSSF('https://www.thestar.com.my/rss/latest', 'The Star Malaysia'),
        RSSF('https://www.bangkokpost.com/rss/data/xml/rss.xml', 'Bangkok Post'),
        RSSF('https://vietnamnews.vn/rss.html', 'Vietnam News'),
        RSSF('https://www.straitstimes.com/rss-feed/latest', 'Straits Times'),
        GN('asean', 'en', 'Google News ASEAN'),
        GN('malaysia indonesia', 'en', 'Google News Malaysia-Indonesia'),
        GN('thailand southeast asia', 'en', 'Google News Thailand'),
        GN('vietnam southeast asia', 'en', 'Google News Vietnam'),
        GN('philippines southeast asia', 'en', 'Google News Filipina'),
        GN('singapore southeast asia', 'en', 'Google News Singapura'),
        GN('myanmar southeast asia', 'en', 'Google News Myanmar'),
        GN('cambodia laos brunei', 'en', 'Google News Kamboja-Laos-Brunei'),
        GN('borneo malaysia', 'en', 'Google News Borneo'),
    ],
    'internasional_tt': [
        RSSF('https://www.aljazeera.com/xml/rss/all.xml', 'Al Jazeera'),
        GN('middle east news', 'en', 'Google News Timur Tengah'),
        GN('gaza palestine', 'en', 'Google News Gaza-Palestina'),
        GN('saudi arabia uae', 'en', 'Google News Saudi-UEA'),
        GN('iran middle east', 'en', 'Google News Iran'),
        GN('turkey middle east', 'en', 'Google News Turki'),
        GN('west asia conflict', 'en', 'Google News Asia Barat'),
    ],
    'internasional': [
        RSSF('https://feeds.bbci.co.uk/news/world/rss.xml', 'BBC World'),
        RSSF('https://www.theguardian.com/world/rss', 'The Guardian'),
        RSSF('https://www.cnnindonesia.com/internasional/rss', 'CNN Indonesia'),
        GN('us politics', 'en', 'Google News USA'),
        GN('russia politics', 'en', 'Google News Rusia'),
        GN('europe politics', 'en', 'Google News Eropa'),
    ],
    'ekonomi': [
        RSSF('https://www.cnnindonesia.com/ekonomi/rss', 'CNN Indonesia'),
        RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia'),
        RSSF('https://www.antaranews.com/rss/ekonomi', 'Antara'),
        RSSF('https://economy.okezone.com/rss', 'Okezone Economy'),
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
        GN('badminton indonesia turnamen', 'id', 'Google News Badminton'),
        GN('badminton tournament', 'en', 'Google News Badminton Dunia'),
        GN('voli nasional timnas', 'id', 'Google News Voli'),
        GN('volleyball nations league', 'en', 'Google News Voli Dunia'),
        GN('IBL basket indonesia', 'id', 'Google News Basket IBL'),
        GN('tenis turnamen grand slam', 'id', 'Google News Tenis'),
    ],
    'hiburan': [
        RSSF('https://www.cnnindonesia.com/hiburan/rss', 'CNN Indonesia'),
        RSSF('https://hot.detik.com/rss', 'DetikHot'),
        RSSF('https://www.kompas.com/hype/feed', 'Kompas Hype'),
        RSSF('https://www.suara.com/entertainment/rss', 'Suara Entertainment'),
        GN('musik indonesia terbaru', 'id', 'Google News Musik Indonesia'),
        GN('film indonesia box office', 'id', 'Google News Film Indonesia'),
        GN('konser indonesia', 'id', 'Google News Konser Indonesia'),
        GN('drama korea serial', 'id', 'Google News Drama Korea'),
        GN('festival film indonesia', 'id', 'Google News Festival Film'),
        GN('asian pop music', 'en', 'Google News Musik Asia'),
    ],
}
# AKHIR PART 1

# ══════════════════════════════════════════════════════
#  PART 2
#  (feeds breaking [DUNIA +4 SUMBER ASIA — V6.5.2], kata-kunci,
#   anti-dobel 36jam & 6jam, scraper, build_system_prompt —
#   DENGAN ATURAN TEKNOLOGI per domain, ATURAN KESEHATAN,
#   ATURAN RANGKUMAN OLAHRAGA, ATURAN GAMBAR anti-hewan)
# ══════════════════════════════════════════════════════

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

BREAKING_DUNIA_FEEDS = [
    RSSF('https://feeds.bbci.co.uk/news/world/rss.xml', 'BBC World'),
    RSSF('https://www.theguardian.com/world/rss', 'The Guardian'),
    RSSF('http://rss.cnn.com/rss/edition_world.rss', 'CNN World'),
    RSSF('https://www.thestar.com.my/rss/latest', 'The Star Malaysia'),
    RSSF('https://www.bangkokpost.com/rss/data/xml/rss.xml', 'Bangkok Post'),
    RSSF('https://www.straitstimes.com/rss-feed/latest', 'Straits Times'),
    RSSF('https://vietnamnews.vn/rss.html', 'Vietnam News'),
    GN('breaking world news', 'en', 'GN Breaking Dunia'),
    GN('major earthquake', 'en', 'GN Gempa Besar Dunia'),
    GN('war conflict missile', 'en', 'GN Perang'),
    GN('breaking asia news', 'en', 'GN Breaking Asia'),
]

LUAR_NEGERI_WORDS = ['jepang', 'china', 'amerika', 'eropa', 'luar negeri', 'inggris',
                     'india', 'korea', 'australia', 'turki', 'israel', 'gaza',
                     'ukraina', 'rusia', 'malaysia', 'thailand', 'taiwan', 'timor leste']

INDO_GEO = ['indonesia', 'bmkg', 'aceh', 'sumatera', 'sumatra', 'jawa', 'kalimantan',
            'sulawesi', 'papua', 'bali', 'nusa tenggara', 'lombok', 'ntb', 'ntt',
            'maluku', 'ambon', 'manado', 'makassar', 'medan', 'padang', 'jakarta',
            'bandung', 'surabaya', 'yogyakarta', 'jayapura', 'bengkulu', 'lampung',
            'palu', 'mamuju', 'cilacap', 'garut', 'cianjur', 'tasikmalaya',
            'jember', 'lumajang', 'semarang', 'banggai', 'tarakan', 'kaltara',
            'nunukan', 'bulungan', 'malinau', 'pontianak', 'kalbar', 'banjarmasin',
            'kalsel', 'kalteng', 'palangka raya', 'denpasar', 'mataram', 'kupang',
            'gorontalo', 'batam', 'pekanbaru', 'palembang']

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

STAT_SCRAPE = {'ok': 0, 'gagal': 0}

JUDUL_TERPAKAI = []
JUDUL_6JAM = []
DOBEL_6JAM_MIN_KATA = 2
_GAMBAR_TERPAKAI_CACHE = None

def resolusi_link_google(url):
    try:
        if 'news.google.com' not in url:
            return url
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT, allow_redirects=True)
        if not r.ok:
            return url
        html = r.text or ''
        m = re.search(r'href="(https?://(?!news\.google|www\.google)[^"]+)"', html)
        if m:
            kandidat = m.group(1)
            if 'google' not in kandidat:
                return kandidat
        m = re.search(r'https?://(?!news\.google|www\.google)[A-Za-z0-9\.\-]+(?:/[^\s"\'<>\\]+)+', html)
        if m:
            kandidat = m.group(0)
            if 'google' not in kandidat and any(d in kandidat for d in ('.com', '.id', '.net', '.co', '.org')):
                return kandidat
        return url
    except Exception:
        return url

def scrape_via_jina(url):
    try:
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(JINA_READER + url, headers=headers,
                         timeout=SCRAPER_TIMEOUT + 8, allow_redirects=True)
        if not r.ok:
            return ''
        teks = r.text or ''
        teks = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', teks)
        teks = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', teks)
        teks = re.sub(r'[#*_`>]{1,3}', ' ', teks)
        teks = re.sub(r'\s+', ' ', teks).strip()
        return teks if len(teks) >= SCRAPE_MIN_KARAKTER else ''
    except Exception:
        return ''

def _bersihkan_html_artikel(html):
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
    if not url:
        return ''
    url_asli = resolusi_link_google(url)
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
    hasil = scrape_via_jina(url_asli)
    if hasil:
        return hasil
    if url_asli != url:
        hasil = scrape_via_jina(url)
        if hasil:
            return hasil
    return ''

def ambil_materi_kaya(c):
    scraped = scrape_artikel(c.get('link', ''))
    if scraped and len(scraped) >= SCRAPE_MIN_KARAKTER:
        STAT_SCRAPE['ok'] += 1
        print('       📥 Scraping artikel asli: ' + str(len(scraped)) + ' karakter')
        return scraped, True
    STAT_SCRAPE['gagal'] += 1
    print('       ↩️ Scraping gagal/pendek — pakai ringkasan RSS')
    return c.get('summary', ''), False

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
    # V6.4.3 — KRAMAV643MARKER: aturan longgar 6 jam
    for t in JUDUL_6JAM:
        if not t:
            continue
        kt = kata_inti(t)
        if ki and kt and len(ki & kt) >= DOBEL_6JAM_MIN_KATA:
            return True
    return False

def _dalam_jendela(row, jam):
    try:
        d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00'))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - d).total_seconds() <= jam * 3600
    except Exception:
        return False

def muat_judul_hari_ini():
    global JUDUL_6JAM
    out = []
    j6 = []
    try:
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=300')
        for row in rows:
            if row.get('title') and _dalam_jendela(row, JENDELA_DOBEL_JAM):
                out.append(normalisasi_judul(row['title']))
                if _dalam_jendela(row, 6):
                    j6.append(normalisasi_judul(row['title']))
    except Exception as e:
        print('   ⚠️ Gagal memuat judul 36 jam:', str(e)[:60])
    JUDUL_6JAM = j6
    return out

def masih_barusan_terbit(judul):
    try:
        q = ('?select=id&title=ilike.' + quote_plus('%' + judul[:40] + '%')
             + '&created_at=gte.'
             + (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat())
        rows = rest_get(q)
        return len(rows) > 0
    except Exception:
        return False

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
KRAMAV642MARKER — V6.5.2: fokus ASEAN & Timur Tengah; gambar tema alam/kota
TANPA manusia & TANPA hewan; satu topik per berita; angka mesin disalin
persis; dateline wajib dari materi sumber; kesehatan = edukasi pakar;
teknologi = kedalaman per domain harian.

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
- Jika berita menyebut ACARA/LAGA/KEJADIAN LAINNYA:
  ✅ Tanggal TERTULIS di materi → WAJIB salin lengkap.
  ✅ Sumber hanya frasa relatif ("pekan ini", "akhir pekan") → salin
     APA ADUNA — dilarang mengarang tanggal dari frasa relatif.
- DILARANG menyisakan kejadian penting tanpa keterangan waktu sama sekali.

ATURAN SPESIFISITAS LOKASI (WAJIB):
- Peristiwa dengan WILAYAH TERDAMPAK WAJIB menyebut daerah SPESIFIK
  sesuai materi. Frasa kabur "sejumlah daerah" DILARANG jika sumber
  menyebut nama daerahnya. Jika sumber memang tidak menyebut → boleh
  frasa umum, jangan mengarang.

ATURAN DATELINE DARI SUMBER (WAJIB — V6.4.3):
- Dateline HANYA boleh diambil dari nama tempat yang TERTULIS di materi.
- DILARANG KERAS mengarang nama kota/wilayah yang tidak ada di materi.
- Sistem MEMVERIFIKASI: kota yang tidak ada di materi = berita
  DIBLOKIR otomatis. Lebih baik "INDONESIA - " daripada mengarang.
- Wilayah Kalimantan Utara (Kaltara) hanya untuk: Tarakan, Nunukan,
  Bulungan, Malinau, Tana Tidung, Sebatik, Tanjung Selor.

ATURAN NAMA PUBLIK INSTANSI RESMI (WAJIB — PALING PENTING):
- Nama orang yang DIUMUMKAN RESMI oleh instansi (KPK, Kejaksaan, Polri,
  Pengadilan, BMKG, BNPB, kementerian, pemda) = INFORMASI PUBLIK HUKUM.
- Jika materi menyebut nama-nama tersebut → WAJIB SEBUTKAN SEMUA
  LENGKAP dan BERANI dengan jabatannya.
- Tetap DILARANG MENGARANG nama yang TIDAK ada di materi sumber.

ATURAN NARASUMBER (WAJIB — V6.4.3.2 KRAMAV6432MARKER — TANPA PENGECEKAN):
- Deskripsi kabur pengganti nama orang SELALU DILARANG, TANPA SYARAT,
  APA PUN kondisi materinya. DILARANG KERAS menulis:
  ❌ "seorang pejabat", "seorang pengusaha", "seorang pengamat",
     "seorang tokoh", "seorang pejabat tinggi", "seorang bos",
     "sumber yang tidak disebutkan namanya", atau varian lainnya.
  Pemeriksa sistem MEMBLOKIR otomatis — berita GAGAL total.
- Jika materi menyebut NAMA ORANG → WAJIB kutip dengan jabatan lengkap.
- Jika materi TIDAK menyebut nama orang → atribusi HANYA boleh ke
  INSTITUSI/LEMBAGA yang tertulis di materi, contoh benar:
  ✅ "Kementerian Kesehatan Gaza mengatakan..."
  ✅ "Polisi dalam keterangan resminya menyatakan..."
  ATAU cukup LAPORKAN FAKTA LANGSUNG tanpa atribusi siapa pun.
- DILARANG KERAS menulis kalimat tentang KETIADAAN narasumber.
- DILARANG KERAS frasa atribusi kosong: "dilaporkan bahwa...",
  "kabarnya...", "diduga kuat...", "menurut informasi yang diterima...".

ATURAN KESEHATAN (WAJIB — V6.4.4): ═══════════════════════════
- Berita kategori kesehatan WAJIB mengutamakan EDUKASI untuk pembaca:
  saran, panduan, penjelasan PAKAR (dokter, ahli gizi, psikolog,
  peneliti) yang tertulis di materi sumber.
- WAJIB menonjolkan PESAN PRAKTIS untuk pembaca: apa yang harus
  dilakukan/dihindari, berapa batas aman, kapan harus waspada.
- Materi "kegiatan/seremoni dinas" = PILIHAN TERAKHIR. Jika terpaksa
  menulisnya, WAJIB menonjolkan SARAN PAKAR di dalamnya, bukan
  protokol acaranya.
- DILARANG menulis nasihat medis yang tidak ada di materi sumber.

ATURAN TEKNOLOGI (WAJIB — V6.5): ═══════════════════════════════
- Pesan user akan menyertakan blok "DOMAIN TEKNOLOGI HARI INI" berisi
  nama domain + aturan kedalamannya — WAJIB DIKUTUH persis.
- Kedalaman per domain:
  ▸ GADGET & SMARTPHONE: berita BANYAK, boleh hingga 2 halaman;
    muat SEBANYAK mungkin gadget yang ada di materi; SPESIFIKASI tiap
    gadget WAJIB lengkap sesuai materi (layar, chipset, RAM, kamera,
    baterai, OS); ESTIMASI HARGA disebut jika ada di materi.
  ▸ AI & KECERDASAN BUATAN: PANJANG & LENGKAP hingga 2 halaman;
    perkembangan AI terkini SELURUH DUNIA yang ada di materi dibahas
    menyeluruh (pemain, kapabilitas, dampak, angka, tanggal).
  ▸ APLIKASI & INTERNET: LENGKAP & BANYAK.
  ▸ STARTUP & EKONOMI DIGITAL: LENGKAP & BANYAK (angka persis materi).
  ▸ KEAMANAN DIGITAL: jika materi kurang, BOLEH menambahkan berita
    teknologi lain dari materi sumber (isi silang khusus domain ini).
  ▸ INOVASI & SAINS TEKNOLOGI: LENGKAP & BANYAK.
- DILARANG menambah spesifikasi/harga/angka yang TIDAK ada di materi
  — "lengkap" berarti menggali seluruh materi, BUKAN mengarang.
- Jika pesan user menyertakan ATURAN KEDALAMAN domain, kutip
  persis sebagai panduan utama penulisan.

ATURAN RANGKUMAN OLAHRAGA (WAJIB — V6.4.4): ═══════════════════
- BERITA OLAHRAGA BOLEH dan DIANJURKAN berbentuk RANGKUMAN:
  SATU judul berisi BANYAK laporan (hasil banyak laga, klasemen
  banyak liga, beberapa cabang olahraga sekaligus).
- IKUTI struktur data yang diberikan: jika pesan user berisi banyak
  liga/cabang, WAJIB membahas SEMUA yang diberikan, tidak memilih satu.
- Tetap dilarang mengarang angka/laga di luar data mesin.

ATURAN ANTI-PLAGIAT (WAJIB — MATERI KAYA):
- Tulis ulang dengan kalimatmu sendiri. DILARANG verbatim >5 kata berurutan.
- Boleh disalin persis: nama, jabatan, angka, kutipan dalam tanda kutip.

ATURAN PANJANG (WAJIB):
- Target jumlah kata DIBERIKAN di pesan user — IKUTI target itu.
- Untuk domain teknologi yang mensyaratkan "2 halaman", target kata
  di pesan user bisa lebih besar dari biasanya — IKUTI target itu.
- DILARANG menggembung dengan kalimat kosong/penyangkalan/pengulangan.
- Setiap kalimat WAJIB membawa informasi baru dari sumber.
- Judul tidak boleh menjanjikan data yang tidak ditulis di isi.

ATURAN GAYA PENULISAN (WAJIB):
- Tulis seperti wartawan portal besar Indonesia. LAPOR BERITA LANGSUNG.
- DILARANG KERAS menyebut nama portal/media/sumber berita mana pun.
- Kalimat pendek, jelas, padat.

ATURAN DATELINE (WAJIB):
- Baris pertama isi berita diawali: "KOTA, PROVINSI/NEGARA - ".
- Jika lokasi tidak ada: "INDONESIA - ".

ATURAN NAMA ASING (WAJIB — JANGAN MENERJEMAHKAN):
- "Partai AfD (Jerman)", "Bayern Munich" — ejaan asli/lazim.

ATURAN DATA & ANGKA (WAJIB):
- Angka dari materi sumber WAJIB SALIN UTUH & PERSIS (contoh: "5,02 persen").
- DILARANG menambah angka yang tidak ada di materi sumber.

ATURAN DATA OLAH RAGA DARI MESIN (WAJIB):
- Bagian "DATA ESPN" di pesan user = angka resmi dari mesin (skor,
  klasemen, jadwal). SALIN PERSIS, DILARANG mengubah/membulatkan/menambah.
- WAJIB: setiap tim yang kamu sebut, sebutkan POSISI KLASEMENNYA
  berdasarkan data yang diberikan.
- Jika data menyertakan blok klasemen siap-render, WAJIB sisipkan blok itu
  APA ADUNA di akhir isi berita ([KLASMEN] ... [/KLASMEN]) — JANGAN mengubah
  isi blok, JANGAN mengarang blok sendiri jika tidak diberikan.
- Jika data menyertakan jadwal laga berikutnya, sebutkan di paragraf akhir.
- DILARANG menebak penyebab hasil laga atau menyebut statistik di luar data.

ATURAN JUDUL (WAJIB):
- Judul ORISINAL maksimal 10 kata, mencerminkan isi berita.
- ═══ PROMISE-CHECK ═══
  Judul DILARANG menjanjikan JADWAL/KLASEMEN/RANKING/HASIL/SKOR jika
  isi tidak memuat datanya. Sistem MEMBLOKIR berita demikian.
- ═══ SATU TOPIK (V6.4.1) ═══
  Jika materi yang diberikan berisi DUA peristiwa yang tidak berkaitan
  langsung, DILARANG mencampurnya dalam satu judul/berita — pilih
  peristiwa yang paling utama dan tulis ITU saja.
- PENGECUALIAN RANGKUMAN OLAHRAGA: banyak laga/liga dalam satu rangkuman
  = SATU topik (bukan pelanggaran aturan satu-topik).
- PENGECUALIAN TEKNOLOGI GADGET: banyak gadget dalam satu berita
  (rasa "2 halaman") = SATU topik domain (bukan pelanggaran).

ATURAN ETIKA FAKTA (WAJIB):
- HANYA fakta dari materi sumber & data mesin. DILARANG mengarang.
- KECUALI: nama publik instansi resmi WAJIB ditulis lengkap.

ATURAN GAMBAR (WAJIB — V6.5.1 ANTI-HEWAN): ═════════════════════
- "deskripsi_gambar" = 3-6 kata kunci visual BAHASA INGGRIS, tanpa nama orang.
- WAJIB memilih tema dari daftar ini saja (atau persis serupa):
  ✅ mountain landscape / rainforest / ocean sea view / grass field /
     flower garden / high speed train / old vintage train /
     city skyline skyscrapers / desert dunes / fresh fruits /
     starry night sky / galaxy space
- ❌ DILARANG KERAS: hewan apa pun (animal, dog, cat, bird, wolf,
  wildlife, animals in forest, zoo, pet, insect, fish, dll) —
  termasuk hewan sebagai LATAR belakang pemandangan. Sistem vision
  MEMBLOKIR otomatis skor maksimal untuk gambar ber-hewan.
- ❌ DILARANG KERAS: tempat ibadah apa pun (mosque, church, temple, pura, dll).
- ❌ DILARANG KERAS: MANUSIA apa pun — orang, wajah, kerumunan, potret,
  tangan, siluet (human, person, people, crowd, portrait).
- ❌ DILARANG: foto suasana insiden (kebakaran, kecelakaan, korban, polisi).
- Contoh benar: "mountain landscape morning fog", "city skyline sunset",
  "fresh fruits market", "starry night sky galaxy".
- Contoh salah: "crowd of people", "firefighters at scene", "portrait",
  "wildlife photography", "wolf in forest", "birds on beach".

FORMAT JAWABAN — HANYA JSON valid tanpa teks lain:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2", "ringkasan": "...",
 "deskripsi_gambar": "visual keywords",
 "waktu_kejadian": "Hari (Tanggal Bulan """ + k['tahun'] + """)"}
INGAT: nama publik resmi WAJIB lengkap. Frasa "seorang pejabat/pengusaha/dll"
SELALU DILARANG — atribusi hanya ke institusi atau lapor fakta langsung.
Blok [KLASMEN] disalin apa aduna bila diberikan. Tanpa bukti tertulis
peristiwa lama = TULIS BERITA."""
# AKHIR PART 2

# ══════════════════════════════════════════════════════
#  PART 3A
#  (edge_call s.d. ai_rewrite_multi — utuh identik V6.5.1,
#   termasuk sumber kesehatan/teknologi, koreksi mandiri,
#   materi_asli, cek_dateline. Perubahan V6.5.2 ada di 3B)
# ══════════════════════════════════════════════════════

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
    urls = set()
    for row in rows:
        if row.get('source_url') and _dalam_jendela(row, JENDELA_DOBEL_JAM):
            urls.add(row['source_url'])
    return urls

def get_breaking_list():
    try:
        return rest_get('?select=id,created_at&breaking=eq.true&status=eq.published&order=created_at.asc')
    except Exception:
        return []

def expire_breaking(menit):
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

def gambar_sampah(url):
    if not url:
        return True
    low = url.lower()
    if any(p in low for p in GAMBAR_SAMPAH_POLA):
        return True
    if any(k in low for k in GAMBAR_LARANG_KATA):
        return True
    m = re.search(r'(\d{2,4})x(\d{2,4})', low)
    if m:
        try:
            if int(m.group(1)) < GAMBAR_MIN_LEBAR:
                return True
        except Exception:
            pass
    return False

def get_image(entry):
    kandidat = []
    mc = entry.get('media_content')
    if mc and mc[0].get('url'):
        kandidat.append(mc[0]['url'])
    mt = entry.get('media_thumbnail')
    if mt and mt[0].get('url'):
        kandidat.append(mt[0]['url'])
    if entry.get('enclosures'):
        kandidat.append(entry['enclosures'][0].get('href', ''))
    for u in kandidat:
        u = (u or '').strip()
        if u and not gambar_sampah(u):
            return u
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
            if len(g['items']) >= 4:
                continue
            sama = k & g['kw']
            kecil = min(len(k), len(g['kw']))
            if kecil == 0:
                continue
            rasio = len(sama) / kecil
            if len(sama) >= MATCH_MIN_KATA and rasio >= MATCH_MIN_RASIO:
                g['items'].append(c)
                g['kw'] |= k
                placed = True
                break
        if not placed:
            groups.append({'kw': k, 'items': [c]})
    return groups

def kategori_barat(title, summary):
    t = ((title or '') + ' ' + (summary or '')).lower()
    if any(k in t for k in KATA_BARAT_USA):
        return 'usa'
    if any(k in t for k in KATA_BARAT_RUSIA):
        return 'rusia'
    if any(k in t for k in KATA_BARAT_EROPA):
        return 'eropa'
    return None

def barat_sudah_terbit(kelompok):
    try:
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=300')
        today = datetime.now(WITA).date()
        for row in rows:
            try:
                d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
                if d != today:
                    continue
                teks = (row.get('title') or '').lower()
                if kelompok == 'usa' and any(k in teks for k in KATA_BARAT_USA):
                    return True
                if kelompok == 'rusia' and any(k in teks for k in KATA_BARAT_RUSIA):
                    return True
                if kelompok == 'eropa' and any(k in teks for k in KATA_BARAT_EROPA):
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False

def deteksi_dua_topik(judul, isi):
    try:
        lokasi = set(re.findall(r'(?:^|\n)([A-Z][A-Z\s\.,\'\-]{2,40}?)\s+[-–—]\s+', isi or ''))
        if len(lokasi) >= 2:
            return 'isi memuat lebih dari satu dateline kota: ' + '; '.join(list(lokasi)[:3])
    except Exception:
        pass
    return None

# ═══ V6.4.3.1 — KRAMAV6431MARKER: PEMERIKSA DATELINE ═══
def cek_dateline(isi, user_content):
    m = re.match(r'^([A-Z][^\n\-–—]{1,60}?)\s+[-–—]\s+', (isi or '').strip())
    if not m:
        return None
    dp = m.group(1).strip().lower()
    if dp == 'indonesia':
        return None
    bag = [x.strip() for x in dp.split(',') if x.strip()]
    kota = bag[0] if bag else ''
    wilayah = bag[1] if len(bag) > 1 else ''
    sumber = re.sub(r'\s+', ' ', (user_content or '')).lower()
    if kota and kota not in sumber:
        return 'kota dateline "' + kota + '" tidak ada di materi sumber'
    if 'kalimantan utara' in wilayah:
        daftar = KALTARA_WORDS + ['sebatik', 'tanjung selor', 'tana tidung']
        if kota and not any(k in kota for k in daftar):
            return 'klaim KALTARA tapi kota "' + kota + '" bukan wilayah Kaltara'
    return None

def parse_ai_json(text):
    t = text.strip()
    if t.startswith('```'):
        t = re.sub(r'^```[a-zA-Z]*\s*', '', t)
        t = re.sub(r'\s*```$', '', t)
    return json.loads(t)

def cek_janji_judul(judul, isi):
    j = (judul or '').lower()
    b = (isi or '').lower()
    if not j or not b:
        return None
    hari_kecil = [h.lower() for h in HARI_ID]
    bulan_kecil = [x.lower() for x in BULAN_ID[1:]]
    if any(w in j for w in JANJI_JADWAL):
        ada = any(w in b for w in ('vs', 'dijadwalkan', 'menghadapi',
                                   'kick off', 'kick-off', 'tanding', 'laga'))
        ada = ada or any(h in b for h in hari_kecil)
        ada = ada or any(re.search(r'\b\d{1,2}\s+' + re.escape(bn), b) for bn in bulan_kecil)
        if not ada:
            return 'judul menjanjikan JADWAL tapi isi tidak memuat jadwal'
    if any(w in j for w in JANJI_TABEL):
        ada_angka = bool(re.search(r'\d', b))
        ada_konteks = any(w in b for w in ('peringkat', 'posisi', 'poin',
                                           'klasemen', 'puncak', 'memimpin'))
        if not (ada_angka and ada_konteks):
            return 'judul menjanjikan KLASEMEN/RANKING tapi isi tidak memuatnya'
    if any(w in j for w in JANJI_ANGKA):
        if not re.search(r'\d', b):
            return 'judul menjanjikan HASIL/SKOR tapi isi tidak memuat angka'
    return None

def cek_deskripsi_gambar(deskripsi):
    d = (deskripsi or '').lower()
    for k in GAMBAR_LARANG_KATA:
        if k in d:
            return 'deskripsi gambar memuat kata terlarang: ' + k
    return None
# AKHIR PART 3A

# ══════════════════════════════════════════════════════
#  PART 3B
#  (JAM_KESEHATAN [KRAMAV644], JAM_TEKNOLOGI [KRAMAV65],
#   POLA_LARANG, ai_write koreksi mandiri [6433] + materi_asli
#   [6434], rewrite single/multi, gempa, gambar terpakai,
#   wikimedia anti-hewan, pexels [KRAMAV652], cari_gambar_otomatis,
#   vision anti-manusia+anti-hewan+relevansi, insert_news,
#   REVISI KRAMAV652B: FUNGSI TEKNOLOGI DIPULIHKAN
#   (_target_teknologi, ai_rewrite_teknologi_single/multi —
#   hilang saat restrukturisasi 4A), espn 4 fungsi)
# ══════════════════════════════════════════════════════

# ═══ V6.4.4 — KRAMAV644MARKER: KESEHATAN PERPUTARAN DOMAIN ═══
JAM_KESEHATAN = {10: 0, 15: 1, 20: 2}

def sumber_kesehatan_hari_ini(jam):
    if jam not in JAM_KESEHATAN:
        return None, None
    try:
        dasar = datetime(2026, 1, 1).date()
        indeks = (datetime.now(WITA).date() - dasar).days % len(DOMAIN_KESEHATAN)
    except Exception:
        indeks = 0
    idx_domain = (indeks + JAM_KESEHATAN[jam]) % len(DOMAIN_KESEHATAN)
    dom = DOMAIN_KESEHATAN[idx_domain]
    sumber = []
    for q, lang in dom['query']:
        sumber.append(GN(q, lang, 'GN Kesehatan: ' + dom['nama']))
    sumber.append(RSSF('https://health.kompas.com/rss', 'Kompas Health'))
    sumber.append(RSSF('https://feeds.bbci.co.uk/news/health/rss.xml', 'BBC Health'))
    print('   🏥 KESEHATAN hari ini (jam ' + str(jam) + '): ' + dom['nama'])
    return dom, sumber

# ═══ V6.5 — KRAMAV65MARKER: TEKNOLOGI PERPUTARAN DOMAIN ═══
JAM_TEKNOLOGI = {8: 0, 13: 1, 18: 2}

def sumber_teknologi_hari_ini(jam):
    if jam not in JAM_TEKNOLOGI:
        return None, None
    try:
        dasar = datetime(2026, 1, 1).date()
        indeks = (datetime.now(WITA).date() - dasar).days % len(DOMAIN_TEKNOLOGI)
    except Exception:
        indeks = 0
    idx_domain = (indeks + JAM_TEKNOLOGI[jam]) % len(DOMAIN_TEKNOLOGI)
    dom = DOMAIN_TEKNOLOGI[idx_domain]
    sumber = []
    for q, lang in dom['query']:
        sumber.append(GN(q, lang, 'GN Teknologi: ' + dom['nama']))
    sumber.append(RSSF('https://www.cnnindonesia.com/teknologi/rss', 'CNN Teknologi'))
    sumber.append(RSSF('https://feeds.bbci.co.uk/news/technology/rss.xml', 'BBC Tech'))
    print('   💻 TEKNOLOGI hari ini (jam ' + str(jam) + '): ' + dom['nama'])
    return dom, sumber

POLA_LARANG = [
    'belum dikonfirmasi waktu', 'waktu kejadian belum',
    'belum dikonfirmasi kapan',
    'menurut informasi yang diterima', 'diduga kuat',
    'kabarnya', 'dikabarkan',
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
    'seorang pengusaha', 'seorang pengamat', 'seorang pejabat tinggi',
    'seorang tokoh', 'seorang bos', 'seorang pejabat',
]

def _frasa_tertangkap(isi):
    isi_lower = (isi or '').lower()
    for p in POLA_LARANG:
        if p in isi_lower:
            return p
    return None

def _panggil_deepseek(user_content, temperature):
    r = requests.post('https://api.deepseek.com/chat/completions',
        headers={'Authorization': 'Bearer ' + DEEPSEEK_KEY,
                 'Content-Type': 'application/json'},
        json={'model': 'deepseek-chat',
              'messages': [{'role': 'system', 'content': build_system_prompt()},
                           {'role': 'user', 'content': user_content}],
              'temperature': temperature},
        timeout=150)
    r.raise_for_status()
    return parse_ai_json(r.json()['choices'][0]['message']['content'])

def ai_write(user_content, timeout=150):
    # V6.4.3.3 — KRAMAV6433MARKER: KOREKSI MANDIRI (retry 1x, temp 0.3)
    # V6.4.3.4 — KRAMAV6434MARKER: materi_asli utk cek_dateline
    obj = None
    materi_asli = user_content
    for percobaan in (1, 2):
        try:
            obj = _panggil_deepseek(user_content, 0.8 if percobaan == 1 else 0.3)
        except BeritaLama:
            raise
        except Exception as e:
            if percobaan == 2:
                raise
            print('       ⚠️ Panggilan AI gagal (' + str(e)[:60] + ') — coba sekali lagi.')
            continue
        if str(obj.get('tolak', '')).strip():
            raise BeritaLama(str(obj.get('tolak'))[:100])
        isi_c = obj.get('isi', '').strip()
        frasa = _frasa_tertangkap(isi_c)
        if frasa and percobaan == 1:
            print('       🔁 Koreksi mandiri: frasa "' + frasa + '" — minta AI tulis ulang...')
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena memuat frasa '
                'terlarang: "' + frasa + '".\n\n'
                'TULIS ULANG berita yang sama dengan ATURAN KETAT:\n'
                '- HAPUS total frasa itu dan semua variannya.\n'
                '- DILARANG deskripsi kabur pengganti nama orang ("seorang '
                'pejabat", "seorang pengusaha", dst) — APA PUN kondisinya.\n'
                '- Atribusi HANYA ke institusi/lembaga yang tertulis di materi '
                '(contoh: "Kementerian Kesehatan setempat mengatakan...") ATAU '
                'laporkan fakta langsung TANPA atribusi siapa pun.\n'
                '- Jangan mengubah fakta, angka, tanggal, dan struktur lain.\n'
                '- Jangan menambah topik/wilayah baru yang tidak ada di materi.\n'
                '- Jawab HANYA JSON valid dengan format yang sama.')
            continue
        break
    judul = obj.get('judul', '').strip()
    isi = obj.get('isi', '').strip()
    ringkasan = obj.get('ringkasan', '').strip()
    waktu = (obj.get('waktu_kejadian') or '').strip()
    gambar = (obj.get('deskripsi_gambar') or '').strip()
    frasa_akhir = _frasa_tertangkap(isi)
    if frasa_akhir:
        raise Exception('diblokir pemeriksa V6.3.4: ' + str(frasa_akhir)[:50])
    alasan_janji = cek_janji_judul(judul, isi)
    if alasan_janji:
        raise Exception('diblokir promise-check V6.3.6: ' + alasan_janji)
    dua_topik = deteksi_dua_topik(judul, isi)
    if dua_topik:
        raise Exception('diblokir tembok anti-2-topik V6.4.2: ' + dua_topik[:60])
    cek_dl = cek_dateline(isi, materi_asli)
    if cek_dl:
        raise Exception('diblokir pemeriksa dateline V6.4.3: ' + cek_dl[:70])
    for t in JUDUL_6JAM:
        if len(kata_inti(judul) & kata_inti(t)) >= DOBEL_6JAM_MIN_KATA:
            raise Exception('diblokir anti-dobel-6jam V6.4.3: mirip "' + t[:40] + '"')
    gambar_terlarang = cek_deskripsi_gambar(gambar)
    if gambar_terlarang:
        raise Exception('diblokir filter gambar V6.4.2: ' + gambar_terlarang[:60])
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
            '- TANGGAL KONKRET di isi berita.\n'
            '- NAMA PUBLIK INSTANSI RESMI: sebut SEMUA namanya lengkap dan BERANI.\n'
            '- SPESIFIK: wilayah terdampak wajib menyebut nama daerah yang tertulis '
            'di materi (dilarang "sejumlah daerah" jika nama daerah ada).\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi — ejaan PERSIS '
            'materi, DILARANG menerjemahkan nama kota (KRAMAV651B).\n'
            '- NARASUMBER: "seorang pejabat/pengusaha/dll" SELALU DILARANG — '
            'atribusi hanya ke institusi tertulis di materi atau lapor fakta '
            'langsung (pemeriksa sistem memblokir).\n'
            '- ACARA/LAGA: tanggal jika tertulis; frasa relatif salin apa adanya.\n'
            '- JUDUL: dilarang menjanjikan jadwal/klasemen/hasil/skor/ranking jika '
            'isi tidak memuat datanya (sistem memblokir).\n'
            '- deskripsi_gambar: WAJIB 3-6 kata kunci DARI ELEMEN UTAMA BERITA '
            '(lokasi/objek/cuaca/aktivitas) — bukan tema generik; DILARANG '
            'manusia, hewan, insiden-korban (sistem memblokir).\n'
            '- Tulis ulang dengan kalimatmu sendiri — dilarang menjiplak kalimat sumber.\n'
            '- Jangan sebut portal/media sumber, awali dateline, salin utuh angka.')
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
            'Berikut beberapa materi tentang SATU peristiwa yang sama '
            '(dilaporkan banyak media — BUKAN peristiwa berbeda):\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita KramaNews tentang SATU peristiwa '
            'tersebut sesuai SEMUA aturan:\n'
            '- Jika ternyata materinya berisi DUA peristiwa berbeda, tulis HANYA '
            'peristiwa yang paling utama — dilarang mencampur dua topik.\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- NAMA PUBLIK INSTANSI RESMI: sebut semua namanya lengkap dan berani.\n'
            '- SPESIFIK: wilayah terdampak wajib menyebut nama daerah dari materi.\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi — ejaan PERSIS '
            'materi (KRAMAV651B).\n'
            '- NARASUMBER: "seorang pejabat/pengusaha/dll" SELALU DILARANG — '
            'atribusi hanya ke institusi tertulis di materi atau lapor fakta langsung.\n'
            '- ACARA/LAGA: tanggal jika tertulis; frasa relatif salin apa adanya.\n'
            '- JUDUL: dilarang menjanjikan data yang tidak ada di isi.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA — DILARANG '
            'manusia, hewan, insiden-korban.\n'
            '- Tulis ulang dengan kalimatmu sendiri — dilarang menjiplak kalimat sumber.\n'
            '- Jangan sebut media sumber, awali dateline, salin utuh angka.')
    return ai_write(user, timeout=180)

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
    if any(w in t for w in KATA_ANALISIS):
        return 0
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
    if any(w in t for w in KATA_ANALISIS):
        return 0
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

_GAMBAR_TERPAKAI_CACHE = None

def muat_gambar_terpakai():
    global _GAMBAR_TERPAKAI_CACHE
    if _GAMBAR_TERPAKAI_CACHE is not None:
        return _GAMBAR_TERPAKAI_CACHE
    out = set()
    try:
        rows = rest_get('?select=image_url,img,created_at&order=created_at.desc&limit=300')
        for row in rows:
            if not _dalam_jendela(row, JENDELA_DOBEL_JAM):
                continue
            u = (row.get('image_url') or row.get('img') or '').strip()
            if u:
                out.add(u)
    except Exception as e:
        print('   ⚠️ Gagal muat gambar terpakai:', str(e)[:60])
    _GAMBAR_TERPAKAI_CACHE = out
    return out

def gambar_sudah_dipakai(url):
    if not url:
        return False
    return url in muat_gambar_terpakai()

def catat_gambar_terpakai(url):
    if url:
        muat_gambar_terpakai().add(url)

# ═══ V6.5.1 — KRAMAV651MARKER: WIKIMEDIA ANTI-HEWAN ═══
KATA_HEWAN_FILE = [
    'wolf', 'serigala', 'dog', 'anjing', 'cat_', '-cat-', 'kucing',
    'bird', 'burung', 'egret', 'heron', 'eagle', 'hawk', 'owl',
    'monkey', 'monyet', 'orangutan', 'komodo', 'tiger', 'harimau',
    'lion', 'singa', 'elephant', 'gajah', 'bear', 'beruang', 'deer',
    'rusa', 'fox', 'rubah', 'snake', 'ular', 'crocodile', 'buaya',
    'lizard', 'kadal', 'frog', 'katak', 'fish', 'ikan', 'shark',
    'hiu', 'whale', 'paus', 'dolphin', 'lumba', 'insect', 'serangga',
    'butterfly', 'kupu', 'spider', 'labah', 'rat', 'tikus', 'mouse-',
    'horse', 'kuda', 'cow', 'sapi', 'goat', 'kambing', 'sheep',
    'chicken', 'ayam', 'duck', 'bebek', 'goose', 'rabbit', 'kelinci',
    'zoo', 'safari', 'wildlife', 'fauna',
]

def _url_berbau_hewan(url):
    low = (url or '').lower()
    return any(k in low for k in KATA_HEWAN_FILE)

def cari_gambar_wikimedia(deskripsi):
    if not deskripsi:
        return ''
    try:
        if cek_deskripsi_gambar(deskripsi):
            print('       🚫 Deskripsi berbau hewan/terlarang — Wikimedia dilewati.')
            return ''
        q = quote_plus(deskripsi)
        url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
               '&gsrsearch=' + q + '&gsrnamespace=6&gsrlimit=10&prop=imageinfo'
               '&iiprop=url&iiurlwidth=800&format=json&origin=*')
        r = requests.get(url, timeout=20)
        if not r.ok:
            return ''
        pages = r.json().get('query', {}).get('pages', {})
        kandidat = []
        for p in pages.values():
            info = p.get('imageinfo', [{}])[0]
            u = info.get('thumburl') or info.get('url') or ''
            if u and u.lower().endswith(('.jpg', '.jpeg', '.png')):
                kandidat.append(u)
        for u in kandidat:
            if not gambar_sampah(u) and not gambar_sudah_dipakai(u) \
               and not _url_berbau_hewan(u):
                return u
        if kandidat:
            print('       ⚠️ Kandidat Wikimedia tak layak (terpakai/terlarang/hewan) — tanpa gambar.')
    except Exception:
        pass
    return ''

# ═══ V6.5.2 — KRAMAV652MARKER: PEXELS UTAMA ═══
PEXELS_API = 'https://api.pexels.com/v1/search'

def cari_gambar_pexels(deskripsi):
    kunci = os.environ.get('PEXELS_API_KEY', '')
    if not kunci:
        print('       ⚠️ PEXELS_API_KEY belum ada di Secrets — lewati Pexels.')
        return ''
    if not deskripsi:
        return ''
    try:
        r = requests.get(PEXELS_API,
            headers={'Authorization': kunci},
            params={'query': deskripsi, 'per_page': 6, 'orientation': 'landscape'},
            timeout=20)
        if not r.ok:
            print('       ⚠️ Pexels HTTP ' + str(r.status_code) + ' — lewati.')
            return ''
        kandidat = []
        for foto in r.json().get('photos', []):
            u = (foto.get('src', {}) or {}).get('large2x') or (foto.get('src', {}) or {}).get('large') or ''
            if u:
                kandidat.append(u)
        for u in kandidat:
            if not gambar_sampah(u) and not gambar_sudah_dipakai(u):
                return u
        if kandidat:
            print('       ⚠️ Semua kandidat Pexels terpakai/sampah — fallback Wikimedia.')
    except Exception as e:
        print('       ⚠️ Pexels gagal: ' + str(e)[:60])
    return ''

def cari_gambar_otomatis(deskripsi, judul_berita):
    """V6.5.2 — urutan resmi: Pexels → Wikimedia → kosong.
    Vision gate (dengan cek relevansi) = pengaman terakhir."""
    img = cari_gambar_pexels(deskripsi)
    if img:
        return img
    print('       🔄 Pexels kosong — fallback Wikimedia...')
    return cari_gambar_wikimedia(deskripsi)

def insert_news(judul, isi, ringkasan, cat, img, link, source_name, status,
                breaking=False, deskripsi_gambar=''):
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+(.*)$', isi, re.DOTALL)
    dateline = m.group(1).strip() if m else ''
    isi_bersih = m.group(2).strip() if m else isi
    if masih_barusan_terbit(judul):
        raise Exception('diblokir anti-dobel insert-momen V6.4.2: judul sama baru terbit <10 mnt')
    if not img and deskripsi_gambar:
        img = cari_gambar_otomatis(deskripsi_gambar, judul)
        if img:
            print('   🖼️ Gambar ditemukan — cek vision...')
            if not gambar_lolos_blur_gate(img, judul):
                img = ''
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
    catat_gambar_terpakai(img or '')
    JUDUL_TERPAKAI.append(normalisasi_judul(judul))

def vision_nilai_gambar(img_url, judul_berita):
    try:
        img_r = requests.get(img_url, headers={'User-Agent': random.choice(UA_LIST)},
                             timeout=20)
        if not img_r.ok or len(img_r.content) < 1000:
            return None
        b64 = base64.b64encode(img_r.content).decode('ascii')
        r = requests.post('https://api.deepseek.com/chat/completions',
            headers={'Authorization': 'Bearer ' + DEEPSEEK_KEY,
                     'Content-Type': 'application/json'},
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': [
                        {'type': 'text',
                         'text': ('Nilai gambar ini untuk berita berjudul: "'
                                  + judul_berita[:120] + '". '
                                  'ATURAN PENILAIAN: '
                                  '(1) MANUSIA sebagai subjek utama (wajah, '
                                  'orang, kerumunan, potret, siluet) = skor '
                                  'MAKSIMAL 3 — portal melarang foto manusia. '
                                  '(2) KRAMAV652MARKER: HEWAN APAPUN (serigala, '
                                  'anjing, kucing, burung, monyet, ikan, '
                                  'serangga, hewan liar/peliharaan — BAHKAN '
                                  'sebagai latar) = skor MAKSIMAL 3. '
                                  '(3) TIDAK NYAMBUNG dengan judul berita '
                                  '(subjek berbeda total dari topik judul) = '
                                  'skor 1-4. '
                                  '(4) Blur, rusak, iklan, placeholder, logo, '
                                  'watermark = skor 1-4. '
                                  '(5) Gambar yang SUBJEKNYA SESUAI tema judul, '
                                  'tajam, dan bebas manusia/hewan = skor 8-10. '
                                  'Jawab HANYA JSON: {"skor": <angka>} '
                                  'KRAMAV643MARKER')},
                        {'type': 'image_url',
                         'image_url': {'url': 'data:image/jpeg;base64,' + b64}}
                    ]}
                ],
                'temperature': 0.1
            },
            timeout=VISION_TIMEOUT)
        if not r.ok:
            return None
        txt = (r.json()['choices'][0]['message']['content'] or '').strip()
        m = re.search(r'\d+', txt)
        if m:
            return min(10, max(1, int(m.group(0))))
        return None
    except Exception:
        return None

def gambar_lolos_blur_gate(img_url, judul_berita):
    if not img_url:
        return False
    skor = vision_nilai_gambar(img_url, judul_berita)
    if skor is None:
        print('       👁️ Vision gagal menilai — gambar dipertahankan.')
        return True
    print('       👁️ Vision skor: ' + str(skor) + '/10 → ' +
          ('LOLOS' if skor >= BLUR_SKOR_MINIMUM else 'DIBUANG (blur/manusia/hewan/tak relevan)'))
    return skor >= BLUR_SKOR_MINIMUM

# ═══ V6.5.2 — KRAMAV652B: FUNGSI TEKNOLOGI DIPULIHKAN ═══
# Hilang saat restrukturisasi 4A — dipulihkan (kasus "is not defined")
def _target_teknologi(dom):
    if dom['nama'].startswith(('Gadget', 'AI')):
        return ('600-900 kata (8-12 paragraf) — WAJIB panjang & menyeluruh '
                'sesuai aturan kedalaman domain "2 halaman".')
    return '400-600 kata (6-9 paragraf) — LENGKAP & BANYAK.'

def ai_rewrite_teknologi_single(c, dom):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' — sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia — sistem memverifikasi '
                     'umur sumber maksimal 30 jam. Tulis kejadian TERKINI ('
                     + k['hari_ini'] + ' / ' + k['kemarin'] + ') dengan tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTUH):\n' + dom['aturan'] + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi + '\n\n'
            'Tulis berita teknologi sesuai SEMUA aturan sistem + ATURAN '
            'KEDALAMAN DOMAIN di atas:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi — ejaan PERSIS '
            'materi, DILARANG menerjemahkan nama kota.\n'
            '- NARASUMBER: "seorang pejabat/dll" SELALU DILARANG — atribusi '
            'ke institusi tertulis atau lapor fakta langsung.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi — '
            '"lengkap" berarti menggali seluruh materi, BUKAN mengarang.\n'
            '- JUDUL maks 10 kata; banyak gadget dalam satu berita = SATU topik.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA — DILARANG '
            'manusia, hewan, insiden-korban.\n'
            '- Tulis ulang kalimatmu sendiri; jangan sebut media sumber; '
            'salin utuh angka.')
    return ai_write(user)

def ai_rewrite_teknologi_multi(items, dom):
    k = konteks_waktu()
    bagian = []
    tgl = None
    for i, it in enumerate(items[:4], 1):
        materi, kaya = ambil_materi_kaya(it)
        if it.get('tgl_pub') and not tgl:
            tgl = it['tgl_pub']
        bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + it['title'] + '\nIsi: ' + materi[:2000])
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' — sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia — sistem memverifikasi '
                     'umur maksimal 30 jam. Tulis kejadian TERKINI ('
                     + k['hari_ini'] + ' / ' + k['kemarin'] + ') tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTUH):\n' + dom['aturan'] + '\n\n'
            'Berikut beberapa materi teknologi domain ini:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita teknologi kaya sesuai SEMUA '
            'aturan sistem + ATURAN KEDALAMAN DOMAIN di atas:\n'
            '- TANGGAL KONKRET; DATELINE dari materi (ejaan PERSIS, KRAMAV651B).\n'
            '- NARASUMBER: atribusi institusi saja — dilarang kabur.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi.\n'
            '- deskripsi_gambar tanpa manusia/hewan/ibadah; jangan sebut media.\n')
    return ai_write(user, timeout=180)

# ═════════ V6.4.2: ESPN — FIX NBA ROUTING ═════════

def _espn_get(path):
    try:
        r = requests.get(ESPN_SITE + path, headers={'User-Agent': random.choice(UA_LIST)},
                         timeout=15)
        if not r.ok:
            return None
        return r.json()
    except Exception:
        return None

def espn_klasemen(liga_code, nama_liga):
    try:
        if liga_code.startswith('basketball'):
            r = requests.get(ESPN_SITE + 'basketball/nba/standings',
                             headers={'User-Agent': random.choice(UA_LIST)}, timeout=15)
        else:
            r = requests.get(ESPN_CORE + liga_code +
                             '/standings?season=2026',
                             headers={'User-Agent': random.choice(UA_LIST)}, timeout=15)
        if not r.ok:
            return '', ''
        data = r.json()
        entries = []
        try:
            anak = data.get('children', [])
            for ch in anak:
                st = ch.get('standings', {})
                for e in st.get('entries', []):
                    entries.append(e)
        except Exception:
            entries = []
        if not entries and data.get('standings'):
            for e in data.get('standings', {}).get('entries', []):
                entries.append(e)
        baris = []
        for st in entries:
            pos = None
            poin = None
            for stat in st.get('stats', []):
                tipe = stat.get('type') or stat.get('name') or ''
                val = stat.get('value')
                if tipe in ('rank', 'playoffSeed', 'position') and pos is None:
                    pos = val
                if (tipe == 'points' or tipe.lower() == 'points') and poin is None:
                    poin = val
                if tipe in ('wins',) and pos is None and poin is None:
                    poin = val
            tim = st.get('team', {}).get('displayName', '?')
            if pos is None:
                continue
            baris.append((int(pos), tim, int(poin) if poin is not None else 0))
        if not baris:
            return '', ''
        baris.sort()
        teks = nama_liga + ': '
        teks += '; '.join(str(p) + '. ' + t + ' (' + str(pt) + ' poin)'
                          for p, t, pt in baris[:10])
        blok = '[KLASMEN]\n' + nama_liga + '\n'
        for p, t, pt in baris:
            blok += str(p) + '|' + t + '|' + str(pt) + '\n'
        blok += '[/KLASMEN]'
        return blok, teks
    except Exception:
        return '', ''

def espn_skor_semalam(liga_code, nama_liga):
    data = _espn_get('soccer/scoreboard/_/league/' + liga_code) \
        if not liga_code.startswith('basketball') else _espn_get('basketball/nba/scoreboard')
    out = []
    if not data:
        return out
    try:
        for ev in data.get('events', []):
            komp = ev.get('competitions', [{}])[0]
            st = komp.get('status', {}).get('type', {})
            if st.get('state') != 'post':
                continue
            peserta = komp.get('competitors', [])
            if len(peserta) < 2:
                continue
            away = peserta[0] if peserta[0].get('homeAway') == 'away' else peserta[1]
            home = peserta[1] if peserta[0].get('homeAway') == 'away' else peserta[0]
            ha = away.get('team', {}).get('displayName', '?')
            sa = away.get('score')
            hh = home.get('team', {}).get('displayName', '?')
            sh = home.get('score')
            if sa is None or sh is None:
                continue
            out.append(ha + ' ' + str(int(float(sa))) + ' - ' + str(int(float(sh))) + ' ' + hh)
    except Exception:
        pass
    return out

def espn_jadwal_berikutnya(liga_code, nama_liga, maks=3):
    data = _espn_get('soccer/scoreboard/_/league/' + liga_code) \
        if not liga_code.startswith('basketball') else _espn_get('basketball/nba/scoreboard')
    out = []
    if not data:
        return out
    try:
        for ev in data.get('events', []):
            komp = ev.get('competitions', [{}])[0]
            st = komp.get('status', {}).get('type', {})
            if st.get('state') == 'post':
                continue
            peserta = komp.get('competitors', [])
            if len(peserta) < 2:
                continue
            away = peserta[0] if peserta[0].get('homeAway') == 'away' else peserta[1]
            home = peserta[1] if peserta[0].get('homeAway') == 'away' else peserta[0]
            d = ev.get('date', '')
            tgl = ''
            try:
                tgl = tanggal_panjang(datetime.fromisoformat(d.replace('Z', '+00:00'))
                                      .astimezone(WITA).date())
            except Exception:
                pass
            out.append(away.get('team', {}).get('displayName', '?') + ' vs '
                       + home.get('team', {}).get('displayName', '?')
                       + (' (' + tgl + ')' if tgl else ''))
            if len(out) >= maks:
                break
    except Exception:
        pass
    return out

def espn_skor_rentang(liga_code, hari_mundur=4):
    out = []
    try:
        t0 = datetime.now(timezone.utc) - timedelta(days=hari_mundur)
        t1 = datetime.now(timezone.utc) + timedelta(days=1)
        fmt = '%Y%m%d'
        if liga_code.startswith('basketball'):
            base = ('basketball/nba/scoreboard?dates='
                    + t0.strftime(fmt) + '-' + t1.strftime(fmt))
        else:
            base = ('soccer/scoreboard/_/league/' + liga_code +
                    '?dates=' + t0.strftime(fmt) + '-' + t1.strftime(fmt))
        r = requests.get(ESPN_SITE + base,
                         headers={'User-Agent': random.choice(UA_LIST)}, timeout=15)
        if not r.ok:
            return out
        data = r.json()
        for ev in data.get('events', []):
            komp = ev.get('competitions', [{}])[0]
            st = komp.get('status', {}).get('type', {})
            if st.get('state') != 'post':
                continue
            peserta = komp.get('competitors', [])
            if len(peserta) < 2:
                continue
            away = peserta[0] if peserta[0].get('homeAway') == 'away' else peserta[1]
            home = peserta[1] if peserta[0].get('homeAway') == 'away' else peserta[0]
            sa, sh = away.get('score'), home.get('score')
            if sa is None or sh is None:
                continue
            out.append(away.get('team', {}).get('displayName', '?') + ' '
                       + str(int(float(sa))) + ' - ' + str(int(float(sh))) + ' '
                       + home.get('team', {}).get('displayName', '?'))
    except Exception:
        pass
    return out
# AKHIR PART 3B


# ══════════════════════════════════════════════════════
#  PART 4A
#  (buat_materi_rangkuman_eropa [tetap, jendela 4 hari aman],
#   sesi_olahraga_api SIMPEL: hanya 'eropa' jam 07 — NBA ESPN
#   & Rangkuman Malam 00:00 DIHAPUS [keputusan pemilik 21 Sep],
#   V6.5.2 BARU: KATA_REGIONAL_OLAHRAGA + SUMBER_RANGKUMAN_UMUM
#   [A+B: portal besar + query event] + sesi_rangkuman_umum
#   jam 11:00 + ai_rewrite_rangkuman_umum — KRAMAV652MARKER)
# ══════════════════════════════════════════════════════

def buat_materi_rangkuman_eropa():
    skor_semua = []
    klasemen_blok = []
    klasemen_teks = []
    jadwal_teks = []
    for code, nama in ESPN_LIGA:
        for s in espn_skor_rentang(code):
            skor_semua.append(nama.split(' (')[0] + ': ' + s)
        blok, teks = espn_klasemen(code, nama)
        if blok:
            klasemen_blok.append(blok)
            klasemen_teks.append(teks)
        j = espn_jadwal_berikutnya(code, nama, maks=2)
        if j:
            jadwal_teks.append(nama.split(' (')[0] + ': ' + '; '.join(j))
    if not skor_semua and not klasemen_blok:
        return None
    bagian = []
    if skor_semua:
        bagian.append('HASIL LAGA TERAKHIR (ANGKA RESMI MESIN — SALIN PERSIS):\n'
                      + '\n'.join(skor_semua))
    if klasemen_teks:
        bagian.append('KLASMEN (ANGKA RESMI MESIN — WAJIB disebut posisi tiap tim '
                      'yang dibahas):\n' + '\n'.join(klasemen_teks[:4]))
    if jadwal_teks:
        bagian.append('LAGA BERIKUTNYA (WAJIB sebut di paragraf akhir):\n'
                      + '\n'.join(jadwal_teks[:4]))
    if klasemen_blok:
        bagian.append('BLOK KLASMEN SIAP-RENDER (WAJIB disalin APA ADUNA di akhir '
                      'isi berita, jangan diubah, jangan digandakan):\n'
                      + '\n\n'.join(klasemen_blok[:4]))
    return '\n\n'.join(bagian)

def olahraga_sudah_terbit_dengan_data(sumber='ESPN Data'):
    try:
        batas = (datetime.now(timezone.utc) - timedelta(hours=20)).isoformat()
        rows = rest_get('?select=id&source_name=eq.' + quote_plus(sumber)
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

def sesi_olahraga_api(jenis):
    # V6.5.2 — hanya 'eropa' (jam 07). NBA & Malam DIHAPUS:
    # NBA bukan lagi fokus utama; slot 13/17/20 produksi RSS
    # berfilter regional (PART 4B); slot 11 = Rangkuman Umum.
    jam = datetime.now(WITA).hour
    if jenis != 'eropa' or jam != 7:
        return 0
    print('\n⚽ RANGKUMAN LIGA EROPA TERJADWAL — jam 7:00 WITA')
    if olahraga_sudah_terbit_dengan_data():
        print('   ⏭️ Berita data-olahraga sudah terbit 20 jam terakhir — skip.')
        return 0
    materi = buat_materi_rangkuman_eropa()
    if not materi:
        print('   🏖️ Tidak ada laga selesai/klasemen dari ESPN — skip aman.')
        return 0
    k = konteks_waktu()
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            'TUGAS KHUSUS: BERITA RANGKUMAN HASIL LIGA EROPA (SATU judul, '
            'BANYAK laporan — sederhana: hasil akhir + klasmen terbaru).\n\n'
            + materi + '\n\n'
            'ATURAN TAMBAHAN:\n'
            '- Dateline: "JAKARTA, DKI JAKARTA - ".\n'
            '- Panjang: 300-500 kata.\n'
            '- WAJIB membahas SEMUA liga yang diberikan.\n'
            '- WAJIB menyebut POSISI + POIN setiap tim yang kamu sebut.\n'
            '- Jika ada blok [KLASMEN], WAJIB menyalinnya APA ADUNA di paragraf '
            'terakhir isi (setelah paragraf terakhir, baris baru).\n'
            '- DILARANG menebak penyebab hasil laga; DILARANG menambah angka/laga.\n'
            '- Judul maks 10 kata: sebut kompetisi + kata kunci hasil.\n'
            '- deskripsi_gambar: tema stadion/bola/liga 3-6 kata — TANPA hewan, '
            'tanpa manusia (sistem memblokir).\n'
            '- Jangan sebut sumber data. Tulis berita.')
    print('   ✍️ AI menulis berita dari data ESPN...')
    try:
        judul, isi, ringkasan, waktu, gambar = ai_write(user)
    except BeritaLama as bl:
        print('   ⏳ Ditolak AI: ' + str(bl)[:60])
        return 0
    except Exception as e:
        print('   ⛔ ' + str(e)[:90])
        return 0
    try:
        insert_news(judul, isi, ringkasan, 'olahraga', '',
                    'https://www.espn.com/soccer/ (data mesin eropa)',
                    'ESPN Data', 'published', breaking=True, deskripsi_gambar=gambar)
        print('   ✅ Rangkuman Liga Eropa BREAKING TERBIT: ' + judul[:60])
        return 1
    except Exception as e:
        print('   ⚠️ Insert gagal: ' + str(e)[:80])
        return 0

# ═══ V6.5.2 — KRAMAV652MARKER: RANGKUMAN OLAHRAGA UMUM JAM 11 ═══
# Sumber A+B: portal olahraga besar + query event besar berlangsung.
# WAJIB lolos FILTER REGIONAL (kandidat tanpa penanda Indonesia/
# ASEAN/Asia/event besar dunia = dibuang — adieu Purdy Washington).
KATA_REGIONAL_OLAHRAGA = [
    'indonesia', 'timnas', 'pssi', 'liga 1', 'tarakan', 'kaltara',
    'asean', 'aff', 'sea games', 'asian games', 'olimpiade', 'olympic',
    'badminton', 'bulu tangkis', 'voli', 'volly', 'volleyball', 'bola voli',
    'basket', 'ibl', 'tenis', 'motogp', 'mandalika', 'f1', 'formula 1',
    'jepang', 'korea', 'thailand', 'malaysia', 'vietnam', 'singapura',
    'filipina', 'china', 'india', 'asia', 'piala dunia', 'fifa',
    'liga champions', 'uefa', 'eropa',
]

SUMBER_RANGKUMAN_UMUM = [
    # [A] Portal olahraga besar
    RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
    RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
    RSSF('https://www.bola.net/feed', 'Bola.net'),
    # [B] Query event besar (berlangsung/hasil)
    GN('badminton turnamen hasil hari ini', 'id', 'GN Event Badminton'),
    GN('voli nations league hasil', 'id', 'GN Event Voli'),
    GN('timnas indonesia laga hasil', 'id', 'GN Event Timnas'),
    GN('liga 1 indonesia hasil', 'id', 'GN Event Liga 1'),
    GN('motogp hasil balapan', 'id', 'GN Event MotoGP'),
    GN('tenis atp hasil turnamen', 'id', 'GN Event Tenis'),
    GN('basket ibl hasil', 'id', 'GN Event IBL'),
]

def sesi_rangkuman_umum(today_urls, seen):
    # V6.5.2 — KRAMAV652MARKER: jam 11:00 WITA.
    # Kumpulkan kandidat A+B → filter regional → pilih kelompok
    # kaya event (banyak item diprioritaskan) → 1 berita rangkuman.
    jam = datetime.now(WITA).hour
    if jam != 11:
        return 0
    print('\n🏆 RANGKUMAN OLAHRAGA UMUM TERJADWAL — jam 11:00 WITA')
    if olahraga_sudah_terbit_dengan_data('Rangkuman Olahraga'):
        print('   ⏭️ Rangkuman umum sudah terbit 20 jam terakhir — skip.')
        return 0
    cand = collect_candidates(SUMBER_RANGKUMAN_UMUM, today_urls, seen)
    if not cand:
        print('   🏖️ Tidak ada kandidat olahraga segar — skip aman.')
        return 0
    regional = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'],
                                   KATA_REGIONAL_OLAHRAGA)]
    if not regional:
        print('   🏖️ Tidak ada kandidat yang lolos filter regional — skip.')
        return 0
    groups = match_articles(regional)
    groups.sort(key=lambda g: -len(g['items']))  # kelompok paling kaya duluan
    dibuat = 0
    for g in groups:
        if dibuat >= 1:
            break
        items = g['items']
        top = items[0]
        if sudah_serupa(top['title']):
            continue
        print('\n   ✍️ [rangkuman umum] menulis: ' + top['title'][:70]
              + ' (+' + str(len(items) - 1) + ' materi lain)')
        try:
            k = konteks_waktu()
            bagian = []
            for i, it in enumerate(items[:6], 1):
                materi, kaya = ambil_materi_kaya(it)
                bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + it['title']
                              + '\nIsi: ' + materi[:1500])
            user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: '
                    + k['kemarin'] + ')\n'
                    'TUGAS KHUSUS: RANGKUMAN OLAHRAGA (SATU judul, BANYAK '
                    'event/hasil/laporan sekaligus — event besar berlangsung '
                    'atau hasil akhir).\n\n'
                    + '\n\n'.join(bagian) + '\n\n'
                    'Gabungkan menjadi SATU berita rangkuman olahraga:\n'
                    '- Judul maks 10 kata mencerminkan rangkuman (bukan satu event).\n'
                    '- WAJIB membahas SEMUA materi di atas (satu paragraf per event).\n'
                    '- TANGGAL KONKRET; dateline dari materi atau "INDONESIA - ".\n'
                    '- Angka/skor WAJIB persis dari materi; dilarang mengarang.\n'
                    '- Panjang: 350-550 kata.\n'
                    '- deskripsi_gambar: 3-6 kata kunci dari elemen utama (bola, '
                    'bulu tangkis, lapangan, stadion, dsb) — TANPA manusia/hewan.\n'
                    '- Jangan sebut media sumber; gaya wartawan profesional.')
            judul, isi, ringkasan, waktu, gambar = ai_write(user)
        except BeritaLama as bl:
            print('   ⏳ Ditolak AI: ' + str(bl)[:60])
            continue
        except Exception as e:
            print('   ⛔ ' + str(e)[:90])
            continue
        if sudah_serupa(judul):
            print('   ⏭️ Hasil AI dobel — skip.')
            continue
        try:
            img_url = get_image(top.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            if img_url and not gambar_lolos_blur_gate(img_url, judul):
                img_url = ''
            insert_news(judul, isi, ringkasan, 'olahraga', img_url,
                        top.get('link', ''), top.get('source', 'Rangkuman Olahraga'),
                        'published', breaking=True, deskripsi_gambar=gambar)
            dibuat += 1
            print('   ✅ RANGKUMAN OLAHRAGA TERBIT: ' + judul[:60])
        except Exception as e:
            print('   ⚠️ Insert gagal: ' + str(e)[:80])
    return dibuat
# AKHIR PART 4A

# ══════════════════════════════════════════════════════
#  PART 4B — PENUTUP
#  ═══ SEMENTARA BAGIAN INI PENUH VERSI FILE ══
#  File VERSI & PART TERAKHIR dibaca otomatis oleh cek_versi.py
#  (Sentinel di baris paling bawah file — WAJIB tetap di ujung!)
#  Daftar marker verifikasi seluruh file (pindahan dari PART 1):
#   KRAMAV642MARKER(2x P2) • KRAMAV643MARKER(5x P1/P2/P3B)
#   KRAMAV6431MARKER(2x P1/P3A) • KRAMAV6432MARKER(2x P1/P2)
#   KRAMAV6433MARKER(2x P1/P3B) • KRAMAV6434MARKER(2x P1/P3B)
#   KRAMAV644MARKER(3x P1/P3B/P4B) • KRAMAV65MARKER(3x P1/P3B/P4B)
#   KRAMAV651MARKER(3x P2/P3B) • KRAMAV651B(2x P2/P3B)
#   KRAMAV652MARKER(5x P3B/P4A/P4B)
# ══════════════════════════════════════════════════════

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

    for label, c, tip in pilihan:
        if made >= slots:
            break
        if sudah_serupa(c['title']):
            print('   ⏭️ Skip (dobel dengan judul hari ini): ' + c['title'][:50])
            continue
        print('\n   🚨 ' + label + ': ' + c['title'][:70])
        try:
            judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(c)
        except BeritaLama as bl:
            print('   ⏳ Ditolak AI: ' + str(bl)[:60])
            continue
        except Exception as e:
            print('   ⛔ ' + str(e)[:90])
            continue
        if sudah_serupa(judul):
            print('   ⏭️ Hasil AI mirip judul yang sudah ada — skip.')
            continue
        try:
            img_url = get_image(c.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            if img_url and not gambar_lolos_blur_gate(img_url, judul):
                img_url = ''
            insert_news(judul, isi, ringkasan, kategori_breaking(c, tip),
                        img_url, c.get('link', ''), c.get('source', 'Breaking'),
                        'published', breaking=True, deskripsi_gambar=gambar)
            made += 1
            print('   ✅ BREAKING TERBIT: ' + judul[:60])
        except Exception as e:
            print('   ⚠️ Insert gagal: ' + str(e)[:80])
    return made

def kategori_breaking(c, tip):
    if tip == 'dun':
        return 'internasional'
    t = (c.get('title', '') + ' ' + c.get('summary', '')).lower()
    if any(w in t for w in LUAR_NEGERI_WORDS):
        return 'internasional'
    return 'nasional'

# ═════════ IDX TERJADWAL (11/14/17 WITA) ═════════

def angka_id(n):
    s = '{:,.2f}'.format(float(n))
    s = s.replace(',', '@').replace('.', ',').replace('@', '.')
    if s.endswith(',00'):
        s = s[:-3]
    return s

def persen_id(p):
    tanda = '+' if p >= 0 else '-'
    return tanda + angka_id(abs(p)) + '%'

def yahoo_quote(symbol):
    try:
        headers = {'User-Agent': random.choice(UA_LIST)}
        url = ('https://query1.finance.yahoo.com/v8/finance/chart/' + symbol
               + '?interval=1d&range=7d')
        r = requests.get(url, headers=headers, timeout=12)
        if not r.ok:
            return None
        res = r.json().get('chart', {}).get('result')
        if not res:
            return None
        ts = res[0].get('timestamp') or []
        quote = res[0].get('indicators', {}).get('quote', [{}])[0]
        closes = quote.get('close') or []
        hari_ini = datetime.now(WITA).date()
        pasangan = []
        for t, c in zip(ts, closes):
            if c is None:
                continue
            d = datetime.fromtimestamp(t, tz=timezone.utc).astimezone(WITA).date()
            pasangan.append((d, c))
        if len(pasangan) < 2:
            return None
        if pasangan[-1][0] != hari_ini:
            return None
        harga = pasangan[-1][1]
        prev = pasangan[-2][1]
        if not prev:
            return None
        return {'harga': harga, 'prev': prev,
                'pct': (harga - prev) / prev * 100.0}
    except Exception:
        return None

def buat_data_idx():
    ihsg = yahoo_quote('^JKSE')
    if ihsg is None:
        return None
    baris = ['IHSG: ' + angka_id(ihsg['harga'])
             + ' (perubahan ' + persen_id(ihsg['pct']) + ' dari penutupan sebelumnya)']
    kurs = yahoo_quote('IDR=X')
    if kurs:
        baris.append('Kurs USD/IDR: Rp' + angka_id(kurs['harga'])
                     + ' (perubahan ' + persen_id(kurs['pct']) + ')')
    emiten = []
    for sym, nama in IDX_EMITEN:
        q = yahoo_quote(sym)
        if q:
            emiten.append((nama, sym, q['pct']))
    naik = sorted([e for e in emiten if e[2] > 0], key=lambda x: -x[2])[:3]
    turun = sorted([e for e in emiten if e[2] < 0], key=lambda x: x[2])[:3]
    if naik:
        baris.append('Saham penguat teratas: '
                     + '; '.join(n + ' (' + s + ') ' + persen_id(p) for n, s, p in naik))
    if turun:
        baris.append('Saham pelemah teratas: '
                     + '; '.join(n + ' (' + s + ') ' + persen_id(p) for n, s, p in turun))
    return '\n'.join(baris)

def idx_sudah_terbit(jam=3):
    try:
        batas = (datetime.now(timezone.utc) - timedelta(hours=jam)).isoformat()
        rows = rest_get('?select=id&source_name=eq.' + quote_plus(IDX_Sumber)
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

def sesi_idx(today_urls, seen):
    jam = datetime.now(WITA).hour
    if jam not in IDX_JAM:
        return 0
    print('\n📈 IDX TERJADWAL — jam ' + str(jam) + ':00 WITA')
    if idx_sudah_terbit():
        print('   ⏭️ Berita IDX sudah terbit dalam 3 jam terakhir — skip.')
        return 0
    data = buat_data_idx()
    if not data:
        print('   🏖️ Pasar libur / data tidak tersedia — skip aman.')
        return 0
    k = konteks_waktu()
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            'TUGAS KHUSUS: BERITA PASAR MODAL INDONESIA TERJADWAL.\n\n'
            'DATA RESMI DARI SISTEM PASAR (SALIN ANGKA UTUH & PERSIS —\n'
            'DILARANG mengubah, membulatkan, atau menambah angka lain):\n'
            + data + '\n\n'
            'ATURAN TAMBAHAN:\n'
            '- Dateline: "JAKARTA, DKI JAKARTA - ".\n'
            '- Panjang: 150-250 kata (4-6 paragraf).\n'
            '- Sebut pergerakan dengan tanggal hari ini (konteks di atas).\n'
            '- DILARANG menebak atau menuliskan PENYEBAB/faktor pergerakan\n'
            '  pasar — data penyebab tidak tersedia. Cukup laporkan angka,\n'
            '  arah pergerakan, dan saham yang penguat/pelemah.\n'
            '- DILARANG menambah saham, kurs, atau angka di luar data.\n'
            '- Judul maksimal 10 kata, sebut IHSG dan arah pergerakannya.\n'
            '- deskripsi_gambar: tema city skyline/kantor — tanpa hewan, ibadah, '
            'manusia.\n'
            '- Jangan sebut sumber data. Tulis berita.')
    print('   ✍️ AI menulis berita IDX dari data pasar...')
    try:
        judul, isi, ringkasan, waktu, gambar = ai_write(user)
    except BeritaLama as bl:
        print('   ⏳ Ditolak AI: ' + str(bl)[:60])
        return 0
    except Exception as e:
        print('   ⛔ ' + str(e)[:90])
        return 0
    try:
        link_unik = ('https://finance.yahoo.com/quote/%5EJKSE?sesi='
                     + str(int(time.time())))
        insert_news(judul, isi, ringkasan, 'ekonomi', '',
                    link_unik, IDX_Sumber, 'published',
                    breaking=True, deskripsi_gambar=gambar)
        print('   ✅ IDX BREAKING TERBIT: ' + judul[:60])
        return 1
    except Exception as e:
        print('   ⚠️ Insert IDX gagal: ' + str(e)[:80])
        return 0

# ═════════ SESI KATEGORI — V6.5.2 ═════════

KATEGORI_DB = {
    'nasional': 'nasional', 'daerah': 'daerah',
    'internasional_asean': 'internasional', 'internasional_tt': 'internasional',
    'internasional': 'internasional',
    'ekonomi': 'ekonomi', 'olahraga': 'olahraga', 'teknologi': 'teknologi',
    'hiburan': 'hiburan', 'kesehatan': 'kesehatan',
}

def teks_mengandung(teks, kata_list):
    t = (teks or '').lower()
    for k in kata_list:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', t):
                return True
        elif k in t:
            return True
    return False

def hitung_kaltara_hari_ini():
    n = 0
    try:
        rows = rest_get('?select=title,dateline,created_at&order=created_at.desc&limit=300')
        today = datetime.now(WITA).date()
        for row in rows:
            try:
                d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
                if d != today:
                    continue
                teks = ((row.get('title') or '') + ' ' + (row.get('dateline') or '')).lower()
                if any(w in teks for w in KALTARA_WORDS):
                    n += 1
            except Exception:
                pass
    except Exception as e:
        print('   ⚠️ Gagal hitung Kaltara: ' + str(e)[:60])
    return n

def hitung_topik_hari_ini(kata_list):
    n = 0
    try:
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=300')
        today = datetime.now(WITA).date()
        for row in rows:
            try:
                d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
                if d != today:
                    continue
                if teks_mengandung(row.get('title') or '', kata_list):
                    n += 1
            except Exception:
                pass
    except Exception as e:
        print('   ⚠️ Gagal hitung topik wajib: ' + str(e)[:60])
    return n

def kelompok_kaltara(items):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return any(w in teks for w in KALTARA_WORDS)

def kelompok_topik(items, kata_list):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return teks_mengandung(teks, kata_list)

def kelompok_regional(items):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return teks_mengandung(teks, KATA_REGIONAL_OLAHRAGA)

def produksi_satu(cat, today_urls, seen, utamakan_kaltara, utamakan_topik=None,
                  sumber_custom=None, domain_tek=None, wajib_regional=False):
    cand = collect_candidates(sumber_custom if sumber_custom else HUNT.get(cat, []),
                              today_urls, seen)
    if not cand:
        print('   (' + cat + ') Tidak ada kandidat segar.')
        return False

    if cat == 'internasional_tt':
        cand = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'], KATA_TT)]
        if not cand:
            print('   (tt) Tidak ada kandidat Timur Tengah segar.')
            return False

    # ═══ V6.5.2 — KRAMAV652MARKER: WAJIB REGIONAL (olahraga RSS) ═══
    if wajib_regional:
        sebelum = len(cand)
        cand = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'],
                                   KATA_REGIONAL_OLAHRAGA)]
        print('   (' + cat + ') Filter regional: ' + str(sebelum) + ' → '
              + str(len(cand)) + ' kandidat lolos.')
        if not cand:
            print('   (' + cat + ') Tidak ada kandidat regional segar — skip.')
            return False

    groups = match_articles(cand)
    if utamakan_kaltara:
        groups.sort(key=lambda g: 0 if kelompok_kaltara(g['items']) else 1)
    if utamakan_topik:
        def topik_prio(g):
            for kl in utamakan_topik:
                if kelompok_topik(g['items'], kl):
                    return 0
            return 1
        groups.sort(key=topik_prio)
    if cat == 'internasional_asean':
        def asean_prio(g):
            if kelompok_topik(g['items'], KATA_ASEAN):
                return 0
            b = kategori_barat(g['items'][0]['title'], g['items'][0].get('summary', ''))
            if b:
                return 2 if barat_sudah_terbit(b) else 1
            return 1
        groups.sort(key=asean_prio)

    percobaan = 0
    for g in groups:
        if percobaan >= 3:
            break
        items = g['items']
        top = items[0]
        if cat in ('internasional_asean', 'internasional_tt', 'internasional'):
            b = kategori_barat(top['title'], top.get('summary', ''))
            if b and barat_sudah_terbit(b):
                continue
        if sudah_serupa(top['title']):
            continue
        percobaan += 1
        print('\n   ✍️ [' + cat + '] menulis: ' + top['title'][:70])
        try:
            if domain_tek:
                if len(items) > 1:
                    judul, isi, ringkasan, waktu, gambar = ai_rewrite_teknologi_multi(items, domain_tek)
                else:
                    judul, isi, ringkasan, waktu, gambar = ai_rewrite_teknologi_single(top, domain_tek)
            elif len(items) > 1:
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_multi(items)
            else:
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(top)
        except BeritaLama as bl:
            print('   ⏳ Ditolak AI: ' + str(bl)[:60])
            continue
        except Exception as e:
            print('   ⛔ ' + str(e)[:90])
            continue
        if sudah_serupa(judul):
            print('   ⏭️ Hasil AI dobel dengan judul yang sudah ada — skip.')
            continue
        try:
            img_url = get_image(top.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            if img_url and not gambar_lolos_blur_gate(img_url, judul):
                img_url = ''
            insert_news(judul, isi, ringkasan, KATEGORI_DB.get(cat, cat), img_url,
                        top.get('link', ''), top.get('source', ''),
                        'published', deskripsi_gambar=gambar)
            print('   ✅ Terbit: ' + judul[:60])
            return True
        except Exception as e:
            print('   ⚠️ Insert gagal: ' + str(e)[:80])
            continue
    return False

def sesi_kategori(today_urls, seen):
    jam = datetime.now(WITA).hour
    kuota = JADWAL_JAM.get(jam)
    if not kuota:
        print('\n📰 KATEGORI — jam ' + str(jam) + ':00 WITA di luar jadwal produksi. Lewat.')
        return 0
    print('\n📰 KATEGORI — jam ' + str(jam) + ':00 WITA — kuota: ' +
          ', '.join(k + '=' + str(v) for k, v in kuota.items()))
    utamakan_kaltara = False
    if kuota.get('daerah'):
        utamakan_kaltara = hitung_kaltara_hari_ini() < 2
        if utamakan_kaltara:
            print('   🏝️ Kuota Kaltara hari ini belum capai 2 — kandidat Kaltara didahulukan.')
    utamakan_topik = None
    if kuota.get('nasional'):
        utamakan_topik = []
        for kl in TOPIK_NASIONAL_WAJIB:
            if hitung_topik_hari_ini(kl) == 0:
                utamakan_topik.append(kl)
        if utamakan_topik:
            nama = []
            for kl in utamakan_topik:
                if 'mbg' in kl:
                    nama.append('MBG')
                elif 'kdmp' in kl:
                    nama.append('KDMP')
                else:
                    nama.append('Kegiatan Menteri')
            print('   🎯 Topik wajib nasional belum terpenuhi: ' + ' & '.join(nama)
                  + ' — kandidatnya didahulukan.')
    # ═══ V6.4.4 — KRAMAV644MARKER: kesehatan = DOMAIN HARI INI ═══
    sumber_kesehatan = None
    if kuota.get('kesehatan'):
        dom_kes, sumber_kesehatan = sumber_kesehatan_hari_ini(jam)
        if not dom_kes:
            sumber_kesehatan = None
    # ═══ V6.5 — KRAMAV65MARKER: teknologi = DOMAIN HARI INI ═══
    sumber_teknologi = None
    dom_tek = None
    if kuota.get('teknologi'):
        dom_tek, sumber_teknologi = sumber_teknologi_hari_ini(jam)
        if not dom_tek:
            sumber_teknologi = None
    total = 0
    for cat, n in kuota.items():
        prio = utamakan_topik if cat == 'nasional' else None
        sumber = None
        domain_tek = None
        wajib_regional = False
        if cat == 'kesehatan':
            sumber = sumber_kesehatan
        elif cat == 'teknologi':
            sumber = sumber_teknologi
            domain_tek = dom_tek
        elif cat == 'olahraga':
            # ═══ V6.5.2 — KRAMAV652MARKER: RSS olahraga WAJIB regional ═══
            wajib_regional = True
        for _ in range(n):
            if produksi_satu(cat, today_urls, seen,
                             utamakan_kaltara and cat == 'daerah',
                             prio, sumber, domain_tek, wajib_regional):
                total += 1
    return total

# ═══ STATISTIK + SATU SESI PENUH ═══

def run_session():
    now = datetime.now(WITA)
    print('\n══════════════════════════════════════════')
    print('🤖 SESI BERBURU — ' + now.strftime('%d/%m/%Y %H:%M') + ' WITA (V6.5.2)')
    print('══════════════════════════════════════════')
    dicabut = expire_breaking(BREAKING_UMUR_MENIT)
    if dicabut:
        print('   (' + str(dicabut) + ' breaking tua dicabut otomatis)')
    today_urls = get_today_state()
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   🧠 ' + str(len(JUDUL_TERPAKAI)) + ' judul 36 jam terakhir dimuat (anti-dobel).')
    print('   🕐 ' + str(len(JUDUL_6JAM)) + ' judul 6 jam terakhir dimuat (anti-dobel-6jam).')
    print('   🖼️ ' + str(len(muat_gambar_terpakai())) + ' gambar 36 jam terakhir terdaftar (anti-dobel gambar).')
    seen = set()
    n_brk = sesi_breaking(today_urls, seen)
    n_kat = sesi_kategori(today_urls, seen)
    n_idx = sesi_idx(today_urls, seen)
    n_liga = sesi_olahraga_api('eropa')
    n_umum = sesi_rangkuman_umum(today_urls, seen)
    total_scrape = STAT_SCRAPE['ok'] + STAT_SCRAPE['gagal']
    if total_scrape:
        persen = int(STAT_SCRAPE['ok'] * 100 / total_scrape)
        print('\n📊 Statistik scraping: ' + str(STAT_SCRAPE['ok']) + ' sukses / '
              + str(total_scrape) + ' artikel (' + str(persen) + '%) — gagal '
              + str(STAT_SCRAPE['gagal']))
    else:
        print('\n📊 Statistik scraping: tidak ada percobaan scraping sesi ini.')
    print('🏁 Sesi selesai — breaking: ' + str(n_brk) + ' • kategori: ' + str(n_kat)
          + ' • IDX: ' + str(n_idx) + ' • LigaEropa: ' + str(n_liga)
          + ' • RangkumanUmum: ' + str(n_umum))
    return n_brk + n_kat + n_idx + n_liga + n_umum

def main_sekali():
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ Kunci belum lengkap! Cek Secrets GitHub: DEEPSEEK_KEY, SUPABASE_PUBLISHABLE')
        return
    run_session()

def main():
    print('🤖 AI WARTAWAN KRAMANEWS V6.5.2 — mode loop 30 menit (Ctrl+C untuk berhenti)')
    while True:
        try:
            main_sekali()
        except Exception as e:
            print('⚠️ Sesi gagal total: ' + str(e)[:100])
        time.sleep(1800)

if __name__ == '__main__':
    if '--sekali' in sys.argv:
        main_sekali()
    else:
        main()

# ══════════════════════════════════════════════════════
#  SENTINEL VERSI — WAJIB SELALU DI BARIS PALING BAWAH FILE
#  (jangan pindah, jangan hapus, jangan dobel!)
#  Kelak kalau ada PART 4C/PART 5: pindahkan SENTINEL ini ke
#  ujung part baru itu + update nilai di bawah.
#  Dibaca otomatis oleh cek_versi.py tiap run (GitHub Actions).
# ══════════════════════════════════════════════════════
FILE_VERSI      = 'V6.5.2'
FILE_PART_AKHIR = 'PART 4B'
# AKHIR PART 4B — FILE V6.5.2 SELESAI