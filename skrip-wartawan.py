# PART 1 - KONFIGURASI, JADWAL & SUMBER - V6.16.0

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
ADMIN_SECRET         = os.environ.get('ADMIN_OPS_SECRET', '')
FOOTBALL_API_KEY     = os.environ.get('FOOTBALL_API_KEY', '')

SUPABASE_URL = 'https://imcvijgytdjjpotlaltv.supabase.co'
REST_URL     = SUPABASE_URL + '/rest/v1/articles'
EDGE_URL     = SUPABASE_URL + '/functions/v1/admin-ops'
AUTHOR_NAME  = 'DT'

WITA = timezone(timedelta(hours=8))

# ═══ API FOOTBALL (api-sports.io) ═══
FOOTBALL_API_URL   = 'https://v3.football.api-sports.io'
BASKETBALL_API_URL = 'https://v1.basketball.api-sports.io'
NBA_API_URL        = 'https://v1.nba.api-sports.io'
VOLLEYBALL_API_URL = 'https://v1.volleyball.api-sports.io'
F1_API_URL         = 'https://v1.formula-1.api-sports.io'

BREAKING_MAX_SLOT   = 3
BREAKING_UMUR_MENIT = 30
MAX_UMUR_BERITA_JAM = 30
JENDELA_DOBEL_JAM   = 36
GEMPA_DOM_MIN       = 5.5
GEMPA_DUNIA_MIN     = 6.5
SKOR_BREAKING_MIN   = 20
AMBANG_MIRIP        = 0.65
SCRAPER_TIMEOUT     = 12
SCRAPE_MIN_KARAKTER = 600
JINA_READER         = 'https://r.jina.ai/'
GAMBAR_MIN_LEBAR    = 400

BLUR_SKOR_MINIMUM  = 5
VISION_TIMEOUT     = 30

MATCH_MIN_KATA     = 2
MATCH_MIN_RASIO    = 0.50

DOMAIN_SKIP_SCRAPE = ['berita.tarakankota.go.id']

# ═══ V6.16.0: Filter umur per kategori (jam) ═══
UMUR_BERITA_PER_KATEGORI = {
    'nasional': 30,
    'daerah': 30,
    'internasional_asean': 30,
    'internasional_tt': 30,
    'internasional': 30,
    'olahraga': 30,
    'ekonomi': 48,
    'teknologi': 72,
    'kesehatan': 180 * 24,   # 180 hari (6 bulan)
    'otomotif': 180 * 24,    # 180 hari (6 bulan)
}

# Kategori evergreen — tanggal disembunyikan di web
KATEGORI_EVERGREEN = ['kesehatan', 'otomotif']

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

def GN(q, lang='id', label=None, when='1d'):
    """V6.16.0: parameter `when` untuk arsip Google News.
    - '1d' = 1 hari (default)
    - '180d' = 180 hari (untuk kategori evergreen)"""
    if lang == 'en':
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:' + when)
               + '&hl=en-US&gl=US&ceid=US:EN')
    else:
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:' + when)
               + '&hl=id&gl=ID&ceid=ID:id')
    return {'url': url, 'source': label or ('Google News: ' + q), 'gn': True}

def RSSF(url, source):
    return {'url': url, 'source': source, 'gn': False}

# ═══ ESPN (untuk klasmen liga top Eropa & NBA — fallback kalau API Football gagal) ═══
ESPN_LIGA_TOP = [
    ('eng.1',        'Premier League (Inggris)'),
    ('esp.1',        'La Liga (Spanyol)'),
    ('ita.1',        'Serie A (Italia)'),
    ('ger.1',        'Bundesliga (Jerman)'),
    ('fra.1',        'Ligue 1 (Prancis)'),
    ('uefa.champions', 'Liga Champions'),
    ('uefa.europa',  'Liga Europa'),
]
ESPN_LIGA_LAIN = [
    ('ned.1',        'Eredivisie (Belanda)'),
    ('uefa.europa.conf', 'Liga Conference'),
    ('idn.1',        'Liga 1 (Indonesia)'),
]
ESPN_NBA = ('basketball/nba', 'NBA')
ESPN_SITE = 'https://site.api.espn.com/apis/site/v2/sports/'
ESPN_CORE = 'https://sports.core.api.espn.com/v2/sports/soccer/leagues/'

# ═══ JADWAL JAM — V6.16.0: hiburan -> otomotif ═══
JADWAL_JAM = {
    6:  {'nasional': 1, 'daerah': 2, 'ekonomi': 1},
    7:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'olahraga': 1},
    8:  {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'teknologi': 1},
    9:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'otomotif': 1},
    10: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'kesehatan': 1},
    11: {'nasional': 1, 'daerah': 2, 'ekonomi': 1, 'olahraga': 1},
    12: {'nasional': 1, 'daerah': 2},
    13: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'teknologi': 1, 'olahraga': 1},
    14: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1},
    15: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'kesehatan': 1},
    16: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'otomotif': 1},
    17: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'olahraga': 1},
    18: {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'teknologi': 1},
    19: {'nasional': 1, 'olahraga': 1, 'ekonomi': 1},
    20: {'otomotif': 1, 'olahraga': 1, 'kesehatan': 1},
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

GAMBAR_SAMPAH_KATA = [
    'logo', 'icon', 'banner', 'ads', 'advert', 'sponsor',
    'placeholder', 'default', 'noimage', 'avatar',
    'profile', 'favicon', 'sprite', 'watermark', 'blank', 'pixel',
]
GAMBAR_SAMPAH_POLA = [
    'icon_', 'no-image',
    'thumb_100', 'thumb_150', 'thumb_200',
    '/100x', '/150x', '/200x',
    '100x100', '150x150', '200x200',
    '100-', '150-', '200-',
]

GAMBAR_LARANG_KATA = [
    'animal', 'dog', 'cat', 'bird', 'monkey', 'elephant', 'tiger', 'lion',
    'snake', 'crocodile', 'lizard', 'frog', 'fish', 'shark', 'whale',
    'insect', 'butterfly', 'bee', 'spider', 'rat', 'mouse', 'horse',
    'cow', 'goat', 'sheep', 'pig', 'chicken', 'rooster', 'duck', 'goose',
    'rabbit', 'deer', 'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl',
    'kucing', 'anjing', 'burung', 'ular', 'kuda', 'sapi', 'ayam', 'bebek',
    'kambing', 'harimau', 'singa', 'gajah', 'monyet', 'buaya', 'ikan',
    'pet', 'wildlife', 'fauna', 'orangutan', 'komodo',
    'leopard', 'jaguar', 'cheetah', 'puma', 'lynx', 'panther',
    'puppy', 'kitten', 'hound', 'terrier', 'retriever', 'shepherd',
    'falcon', 'hawk', 'sparrow', 'pigeon', 'parakeet', 'peacock',
    'hamster', 'guinea', 'ferret', 'hedgehog', 'squirrel',
    'stag', 'boar', 'bison', 'yak', 'llama', 'alpaca', 'otter',
    'badger', 'beaver', 'raccoon', 'skunk', 'koala', 'kangaroo',
    'panda', 'penguin', 'dolphin', 'seal_', 'walrus', 'octopus',
    'crab', 'lobster', 'shrimp', 'jellyfish', 'starfish',
    'dinosaur', 'dragon', 'unicorn',
    'mosque', 'masjid', 'church', 'gereja', 'cathedral', 'temple',
    'pura', 'vihara', 'pagoda', 'synagogue', 'shrine', 'monastery',
    'worship', 'ibadah',
    'human', 'people', 'person', 'crowd', 'portrait', 'woman', 'women',
    'girl', 'child', 'children', 'soldier', 'manusia', 'warga',
    'kerumunan', 'wajah',
    'shoes', 'shoe', 'sneaker', 'sneakers', 'sandal', 'sandals',
    'slipper', 'slippers', 'footwear', 'high heels', 'stiletto',
    'sendal', 'sepatu',
]

KATA_ANALISIS = ['analisis', 'soroti', 'opini', 'tinjauan',
                 'analysis', 'opinion', 'editorial']

JANJI_JADWAL  = ['jadwal', 'schedule']
JANJI_TABEL   = ['klasemen', 'standing', 'ranking', 'peringkat']
JANJI_ANGKA   = ['hasil', 'skor', 'result']
JANJI_HARGA = ['harga', 'tarif', 'biaya', 'berapa', 'sewa', 'gaji']

KATA_HARGA_LONGGAR = ['naik', 'turun', 'melonjak', 'anjlok', 'drastis',
                      'meroket', 'terjun', 'menguat', 'melemah']

KATA_HEWAN_SLUG = [
    'dog', 'puppy', 'cat', 'kitten', 'bird', 'monkey', 'elephant',
    'tiger', 'lion', 'leopard', 'jaguar', 'cheetah', 'puma', 'lynx',
    'panther', 'snake', 'crocodile', 'lizard', 'frog', 'fish',
    'shark', 'whale', 'insect', 'butterfly', 'bee', 'spider',
    'rat', 'mouse', 'horse', 'cow', 'goat', 'sheep', 'pig',
    'chicken', 'rooster', 'duck', 'goose', 'rabbit', 'deer',
    'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl', 'hamster',
    'ferret', 'hedgehog', 'squirrel', 'stag', 'boar', 'bison',
    'otter', 'badger', 'beaver', 'raccoon', 'koala', 'kangaroo',
    'panda', 'penguin', 'dolphin', 'walrus', 'octopus', 'crab',
    'lobster', 'shrimp', 'jellyfish', 'dinosaur', 'zoo', 'safari',
    'wildlife', 'fauna', 'anjing', 'kucing', 'burung', 'ular',
    'kuda', 'sapi', 'ayam', 'bebek', 'kambing', 'harimau',
    'singa', 'gajah', 'monyet', 'buaya', 'ikan', 'serigala',
]

# ═══ V6.16.0: Nama lembaga yang TIDAK boleh diterjemahkan ═══
KATA_LEMBAGA_ASING = [
    'party', 'association', 'union', 'federation', 'league',
    'club', 'fc', 'ac', 'united', 'city', 'company', 'corp',
    'corporation', 'bank', 'group', 'holdings', 'institute',
    'foundation', 'agency', 'organization',
]

# ═══ DOMAIN KESEHATAN — V6.16.0: pakai when=180d (arsip 6 bulan) ═══
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

JAM_KESEHATAN = {10: 0, 15: 1, 20: 2}

# ═══ V6.16.0: DOMAIN OTOMOTIF (6 domain, muter 2 hari) ═══
DOMAIN_OTOMOTIF = [
    {'nama': 'Mobil Baru & Rilis', 'query': [
        ('mobil baru rilis Indonesia', 'id'),
        ('mobil facelift terbaru', 'id'),
        ('new car launch', 'en'),
    ]},
    {'nama': 'Motor & Skutik', 'query': [
        ('motor baru rilis Indonesia', 'id'),
        ('motor matic terbaru', 'id'),
        ('motorcycle launch', 'en'),
    ]},
    {'nama': 'Kendaraan Listrik', 'query': [
        ('mobil listrik terbaru', 'id'),
        ('motor listrik rilis', 'id'),
        ('electric vehicle launch', 'en'),
    ]},
    {'nama': 'Industri & Penjualan', 'query': [
        ('penjualan mobil Indonesia', 'id'),
        ('industri otomotif nasional', 'id'),
        ('car sales data', 'en'),
    ]},
    {'nama': 'Review & Test Drive', 'query': [
        ('review mobil terbaru', 'id'),
        ('review motor terbaru', 'id'),
        ('test drive mobil', 'id'),
    ]},
    {'nama': 'Aksesori & Modifikasi', 'query': [
        ('modifikasi mobil terbaru', 'id'),
        ('modifikasi motor terbaru', 'id'),
        ('aksesori mobil baru', 'id'),
    ]},
]

JAM_OTOMOTIF = {9: 0, 16: 1, 20: 2}

# ═══ DOMAIN TEKNOLOGI (tetap) ═══
DOMAIN_TEKNOLOGI = [
    {'nama': 'Gadget & Smartphone', 'aturan':
        ('Berita HARUS BANYAK, boleh hingga 2 halaman. WAJIB memuat '
         'SEBANYAK mungkin gadget/baru yang ada di materi sekaligus. '
         'SPESIFIKASI setiap gadget WAJIB lengkap (layar, chipset, '
         'RAM, kamera, baterai, sistem operasi - sesuai yang tertulis '
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
        ('Berita HARUS LENGKAP dan BANYAK - gabungkan semua materi '
         'aplikasi/internet yang tersedia menjadi satu berita kaya.'),
     'query': [
        ('aplikasi baru populer', 'id'),
        ('fitur media sosial terbaru', 'id'),
        ('internet Indonesia kecepatan', 'id'),
    ]},
    {'nama': 'Startup & Ekonomi Digital', 'aturan':
        ('Berita HARUS LENGKAP dan BANYAK - pendanaan, valuasi, '
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
        ('Berita HARUS LENGKAP dan BANYAK - inovasi, riset, luar '
         'angkasa, kendaraan listrik: semua yang ada di materi '
         'dibahas menyeluruh.'),
     'query': [
        ('kendaraan listrik teknologi', 'id'),
        ('space technology innovation', 'en'),
        ('inovasi teknologi riset', 'id'),
    ]},
]

JAM_TEKNOLOGI = {8: 0, 13: 1, 18: 2}

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
        RSSF('https://berita.tarakankota.go.id/rss.xml', 'Humas Pemkot Tarakan'),
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
        RSSF('https://market.bisnis.com/feed', 'Bisnis Market'),
        RSSF('https://www.antaranews.com/rss/pasar-modal', 'Antara Pasar Modal'),
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
        GN('eredivisie hasil', 'id', 'Google News Eredivisie'),
        GN('liga conference hasil', 'id', 'Google News Liga Conference'),
        GN('liga 1 indonesia hasil', 'id', 'Google News Liga 1'),
    ],
    # ═══ V6.16.0: OTOMOTIF (pengganti hiburan) ═══
    'otomotif': [
        RSSF('https://www.otomotifnet.com/rss', 'Otomotifnet'),
        RSSF('https://www.gridoto.com/rss', 'GridOto'),
        RSSF('https://autonetmagz.com/feed/', 'Autonetmagz'),
        RSSF('https://oto.detik.com/rss', 'Detik Oto'),
        GN('mobil baru rilis Indonesia', 'id', 'GN Mobil Baru'),
        GN('motor baru rilis Indonesia', 'id', 'GN Motor Baru'),
        GN('kendaraan listrik Indonesia', 'id', 'GN Kendaraan Listrik'),
        GN('mobil listrik terbaru', 'id', 'GN Mobil Listrik'),
        GN('penjualan mobil Indonesia', 'id', 'GN Penjualan Mobil'),
        GN('review mobil terbaru', 'id', 'GN Review Mobil'),
        GN('modifikasi mobil motor', 'id', 'GN Modifikasi'),
        GN('new car launch', 'en', 'GN Car Launch'),
        GN('electric vehicle launch', 'en', 'GN EV Launch'),
        GN('car review', 'en', 'GN Car Review'),
    ],
}
# AKHIR PART 1

# PART 2 - FEEDS BREAKING, KATA-KUNCI, ANTI-DOBEL, SCRAPER, SYSTEM PROMPT - V6.16.4

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
    RSSF('https://www.aljazeera.com/xml/rss/all.xml', 'Al Jazeera'),
    RSSF('https://apnews.com/index.rss', 'AP News'),
    RSSF('https://www.france24.com/en/rss', 'France24'),
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

TOPIK_BESAR_GATE = [
    'tsunami', 'gempa', 'erupsi', 'gunung meletus', 'banjir bandang',
    'tanah longsor', 'kebakaran hutan', 'karhutla',
    'hurricane', 'typhoon', 'cyclone', 'wildfire', 'earthquake',
    'perang', 'war', 'invasi', 'missile', 'nuclear',
    'asian games', 'sea games', 'piala dunia', 'world cup',
    'olimpiade', 'olympic', 'piala asia', 'asian cup',
    'piala eropa', 'euro 202', 'copa america',
    'nba finals', 'liga champions final',
    'pemilu', 'pilpres', 'pilkada',
]

def judul_topik_besar(judul):
    j = (judul or '').lower()
    return any(k in j for k in TOPIK_BESAR_GATE)

KATA_TURNAMEN_OLAHRAGA = [
    'fifa', 'aff', 'uefa', 'afc', 'piala dunia', 'world cup',
    'sea games', 'asian games', 'olimpiade', 'olympic',
    'piala asia', 'asian cup', 'piala aff', 'aff cup',
    'fifa asean cup', 'piala eropa', 'euro 202', 'copa america',
    'liga champions', 'champions league', 'europa league',
    'premier league', 'la liga', 'serie a', 'bundesliga', 'ligue 1',
    'eredivisie', 'nba', 'wnba', 'ibl',
    'badminton', 'bulu tangkis', 'bwf',
    'voli', 'volleyball', 'fivb',
    'motogp', 'formula 1', 'f1',
]

def adalah_turnamen_olahraga(teks):
    t = (teks or '').lower()
    return any(k in t for k in KATA_TURNAMEN_OLAHRAGA)

# V6.16.4: kata wajib olahraga - hapus 'cc ' dan 'cc)' yang rawan false positive
KATA_WAJIB_OLAHRAGA = [
    'bola', 'sepak bola', 'sepakbola', 'football', 'soccer',
    'basket', 'nba', 'wnba', 'ibl',
    'badminton', 'bulu tangkis', 'bwf',
    'voli', 'volleyball', 'fivb',
    'tenis', 'tennis', 'atp', 'wta',
    'motogp', 'formula 1', 'f1', 'balap',
    'liga', 'piala', 'turnamen', 'kejuaraan', 'kompetisi',
    'timnas', 'atlet', 'pemain', 'klub', 'klub sepak',
    'pertandingan', 'laga', 'skor', 'klasemen', 'gol',
    'olimpiade', 'olympic', 'sea games', 'asian games',
    'stadion', 'kick-off', 'kick off',
]

def adalah_konten_olahraga(teks):
    t = (teks or '').lower()
    return any(k in t for k in KATA_WAJIB_OLAHRAGA)

KATA_KUNCI_OTOMOTIF = [
    'mobil', 'motor', 'skutik', 'matic', 'bebek', 'sport touring',
    'kendaraan listrik', 'mobil listrik', 'motor listrik',
    'tesla', 'byd', 'geely', 'nissan', 'toyota', 'honda', 'yamaha',
    'suzuki', 'mitsubishi', 'hyundai', 'kia', 'wuling', 'chery',
    'bmw', 'mercedes', 'audi', 'volkswagen', 'ford', 'chevrolet',
    'facelift', 'sedan', 'suv', 'mpv', 'pickup', 'hatchback',
    'spesifikasi mobil', 'spesifikasi motor', 'harga mobil', 'harga motor',
    'test drive', 'review mobil', 'review motor', 'modifikasi',
    'mesin mobil', 'mesin motor',
]

def adalah_konten_otomotif(teks):
    t = (teks or '').lower()
    return any(k in t for k in KATA_KUNCI_OTOMOTIF)

class BeritaLama(Exception):
    pass

STAT_SCRAPE = {'ok': 0, 'gagal': 0, 'skip': 0}

JUDUL_TERPAKAI = []
JUDUL_6JAM = []
DOBEL_6JAM_MIN_KATA = 2
_GAMBAR_TERPAKAI_CACHE = None

DOMAIN_NON_BERITA = [
    'www.w3.org', 'w3.org',
    'schema.org', 'ogp.me', 'purl.org',
    'gstatic.com', 'googleapis.com', 'googleusercontent.com',
    'fonts.googleapis.com', 'fonts.gstatic.com',
    'cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'unpkg.com',
    'facebook.com', 'twitter.com', 'instagram.com',
    'youtube.com', 'tiktok.com',
    'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
    'googletagmanager.com', 'google-analytics.com',
    'accounts.google.com', 'consent.google.com', 'policies.google.com',
    'support.google.com', 'myaccount.google.com',
]

def _url_valid_berita(u):
    if not u:
        return False
    low = u.lower().strip()
    if not low.startswith(('http://', 'https://')):
        return False
    for blok in DOMAIN_NON_BERITA:
        if blok in low:
            return False
    m = re.match(r'^https?://[^/]+(/.*)?$', low)
    if not m or not m.group(1):
        return False
    if not re.search(r'\.(com|id|net|co|org|tv|info|news|co\.id|or\.id|go\.id|ac\.id|my\.id|sch\.id)\b', low):
        return False
    if low.endswith(('.svg', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico',
                     '.css', '.js', '.woff', '.woff2', '.ttf', '.eot')):
        return False
    return True

def resolusi_link_google(url):
    try:
        if 'news.google.com' not in url:
            return url
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(url, headers=headers, timeout=SCRAPER_TIMEOUT, allow_redirects=True)
        if not r.ok:
            return url
        html = r.text or ''
        for m in re.finditer(r'href="(https?://[^"]+)"', html):
            kandidat = m.group(1)
            if _url_valid_berita(kandidat):
                return kandidat
        for m in re.finditer(r'https?://[A-Za-z0-9\.\-]+(?:/[^\s"\'<>\\]*)?', html):
            kandidat = m.group(0)
            if _url_valid_berita(kandidat):
                return kandidat
        return url
    except Exception:
        return url

def domain_skip_scrape(url):
    low = (url or '').lower()
    return any(d in low for d in DOMAIN_SKIP_SCRAPE)

def scrape_via_jina(url):
    try:
        headers = {'User-Agent': random.choice(UA_LIST)}
        r = requests.get(JINA_READER + url, headers=headers,
                         timeout=SCRAPER_TIMEOUT + 8, allow_redirects=True)
        if not r.ok:
            print('       Jina HTTP ' + str(r.status_code) + ' - ' + url[:60])
            return ''
        teks = r.text or ''
        teks = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', teks)
        teks = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', teks)
        teks = re.sub(r'[#*_`>]{1,3}', ' ', teks)
        teks = re.sub(r'\s+', ' ', teks).strip()
        if len(teks) < SCRAPE_MIN_KARAKTER:
            print('       Jina hasil PENDEK: ' + str(len(teks)) + ' kar (butuh ' + str(SCRAPE_MIN_KARAKTER) + ') - ' + url[:60])
            return ''
        return teks
    except requests.exceptions.Timeout:
        print('       Jina TIMEOUT - ' + url[:60])
        return ''
    except Exception as e:
        print('       Jina EXCEPTION: ' + str(e)[:80] + ' - ' + url[:60])
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
                .replace('&mdash;', '-').replace('&ndash;', '-'))
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
    if domain_skip_scrape(url):
        STAT_SCRAPE['skip'] += 1
        print('       Skip scraping (domain 403 konsisten) - ' + url[:60])
        return ''
    url_asli = resolusi_link_google(url)
    if not _url_valid_berita(url_asli) and 'news.google.com' not in url_asli:
        print('       URL hasil resolusi tidak valid (non-berita) - skip: ' + url_asli[:60])
        STAT_SCRAPE['skip'] += 1
        return ''
    hasil = ''
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
        print('       Langsung scrape pendek: ' + str(len(hasil)) + ' kar - ' + url_asli[:60])
    except Exception as e:
        print('       Langsung scrape gagal: ' + str(e)[:60])
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
        print('       Scraping artikel asli: ' + str(len(scraped)) + ' karakter')
        return scraped, True
    STAT_SCRAPE['gagal'] += 1
    potongan = []
    t = (c.get('title') or '').strip()
    if t:
        potongan.append('Judul: ' + t)
    s = (c.get('summary') or '').strip()
    if s:
        potongan.append('Ringkasan: ' + s)
    try:
        entry = c.get('entry') or {}
        konten_rss = ''
        cc = entry.get('content')
        if cc and isinstance(cc, list):
            for part in cc:
                if isinstance(part, dict):
                    v = part.get('value') or ''
                    if len(v) > len(konten_rss):
                        konten_rss = v
        konten_rss = clean(konten_rss, 3000)
        if konten_rss and len(konten_rss) > len(s):
            potongan.append('Konten RSS: ' + konten_rss)
    except Exception:
        pass
    if not potongan:
        print('       Scraping gagal & RSS kosong - pakai summary minimal')
        return c.get('summary', ''), False
    gabung = '\n\n'.join(potongan)
    print('       Scraping gagal/pendek - pakai gabungan title+RSS ('
          + str(len(gabung)) + ' kar)')
    return gabung, False

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
        print('   Gagal memuat judul 36 jam:', str(e)[:60])
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
    return """Kamu AI Wartawan profesional KramaNews Indonesia.
KRAMAV6164MARKER - V6.16.4

GAYA BAHASA (ANTI-JIPLAK):
- Tulis dengan kalimatmu sendiri, struktur beda dari materi.
- Kalimat pembuka wajib struktur baru, jangan salin pembuka materi.
- Pakai sinonim ("mengatakan" -> "menuturkan/menyatakan/mengungkapkan").
- Acak urutan fakta, jangan ikuti urutan materi.
- DILARANG frasa khas media: "dalam keterangan resminya", "seperti
  dikutip dari", "dalam siaran pers yang diterima redaksi".
- DILARANG 15+ kata berurutan sama dengan materi (diblokir otomatis).
- Materi pendek (<500 kata) toleransi 25 kata.
- Istilah resmi (nama lembaga/jabatan) boleh disalin persis.

DILARANG MENAMBAH FAKTA DI LUAR MATERI (SANGAT KERAS):
Semua NAMA ORANG, NAMA LEMBAGA spesifik, NAMA TEMPAT spesifik, ANGKA,
dan PERNYATAAN WAJIB ada di materi sumber. DILARANG menambah entitas baru.

Contoh SALAH:
- Materi: "13 personel Taliban tewas di perbatasan"
- Tulisan AI: "Pakistan Klaim 13 Personel Taliban Tewas, KABUL BANTAH"
- SALAH karena "Kabul Bantah" tidak ada di materi.

CATATAN PENTING: Kata sifat, kata kerja, kata umum BUKAN "fakta baru".
Kata seperti "Dukung", "Pertama", "Siber", "Burden", "Penting" itu boleh
muncul di judul walau tidak ada di materi — itu bagian gaya bahasa.

WAJIB: Judul dan isi HANYA boleh bicara topik yang ada di materi.
Kalau materi tidak sebut nama orang spesifik, jangan tambah.

ATURAN NAMA ORANG (SANGAT KERAS):
Setiap pejabat/tokoh yang disebut WAJIB ada NAMANYA. Ini berlaku untuk
semua berita DALAM NEGERI. Kalau materi hanya sebut jabatan/institusi
TANPA nama pejabat, AI WAJIB pakai nama pejabat yang menjabat
sekarang (dari pengetahuan umum). Kalau TIDAK YAKIN nama, maka
berita itu HARUS DITOLAK: {"tolak":"narasumber tanpa nama"}.

Contoh SALAH vs BENAR:
- SALAH: "Kementerian Pendidikan memperkuat literasi digital..."
- BENAR: "Menteri Pendidikan Dasar dan Menengah, Abdul Mu'ti,
  memperkuat literasi digital..."
- SALAH: "Bawaslu Tarakan menyatakan penyediaan fasilitas..."
- BENAR: "Ketua Bawaslu Tarakan, [nama lengkap], menyatakan..."
- SALAH: "Kodam VI/Mulawarman menegaskan..."
- BENAR: "Panglima Kodam VI/Mulawarman, Mayjen TNI [nama lengkap],
  menegaskan..."

ATURAN KHUSUS TNI/POLRI:
- Narasumber TNI/Polri WAJIB tulis NAMA + PANGKAT + JABATAN.
- Contoh BENAR: "Kapolres Tarakan, AKBP [nama lengkap], menyatakan..."
- DILARANG tulis pangkat saja tanpa nama.

ATURAN GELAR AKADEMIK:
- Kalau materi sebut gelar (S.E., M.Si., Dr., Ir., dr., dll), WAJIB ikut.

DILARANG:
- "seorang pejabat", "seorang pengusaha", "seorang pengamat", "seorang
  tokoh".
- Atribusi ke institusi SAJA tanpa nama pejabat (berita dalam negeri).

VARIASI FRASA KUTIPAN:
"kata [jabatan + nama]", "ujar [jabatan + nama]", "menurut
[jabatan + nama]", "sebagaimana disampaikan [jabatan + nama]".

ATURAN NAMA LEMBAGA (JANGAN DITERJEMAHKAN):
Nama partai politik, perusahaan, organisasi, tim olahraga, dan
institusi TIDAK BOLEH DITERJEMAHKAN.

DILARANG:
- "Cockroach Janta Party" -> "Partai Kecoak India"
- "Manchester United" -> "Persatuan Manchester"
- "Bank of America" -> "Bank Amerika"

WAJIB: Tulis nama lembaga dalam bahasa aslinya.
PENGECUALIAN: Nama tempat (kota/negara) tetap diterjemahkan sesuai
ejaan Indonesia. Nama orang asing ditulis sesuai ejaan asli.

WAKTU:
- HARI INI: """ + k['hari_ini'] + """ | KEMARIN: """ + k['kemarin'] + """ | TAHUN: """ + k['tahun'] + """
- Sumber terverifikasi segar.
- DILARANG "belum dikonfirmasi waktu". DILARANG mengarang jam.
- DILARANG tanggal tahun sebelum """ + k['tahun'] + """.

DATELINE:
- HANYA dari tempat yang TERTULIS di materi, ejaan PERSIS.
- Tidak ada tempat -> dateline = "INDONESIA - ".
- DILARANG mengarang nama kota.

PERSEN: selalu simbol % ("95%", "3,5%"). Dilarang "95 persen".

KATEGORI (WAJIB TEPAT - BACA TOPIK INTI):
- nasional: pemerintah pusat, DPR, presiden, wapres, menteri.
- daerah: peristiwa/pejabat lokal kota/kabupaten Indonesia.
- internasional: peristiwa luar negeri, pejabat asing, PBB, ASEAN.
- ekonomi: IHSG, kurs, saham, BI, OJK, keuangan, bisnis, UMKM.
- olahraga: sepak bola, basket, badminton, voli, tenis, MotoGP, F1,
  liga, timnas, atlet, pertandingan, klasemen, TURNAMEN.
- teknologi: gadget, AI, aplikasi, internet, startup (teknologinya),
  keamanan digital, sains, inovasi.
- otomotif: mobil, motor, kendaraan listrik, spare part, modifikasi,
  industri otomotif, review kendaraan.
- kesehatan: penyakit, gizi, obat, dokter, rumah sakit, mental
  health, pandemi, vaksin.

PERHATIAN KHUSUS KATEGORI:
- "FIFA ASEAN Cup", "Piala AFF", "Piala Dunia", "Asian Games",
  "SEA Games", "UEFA Nations League" => WAJIB masuk olahraga.
- "Kemendikbud", "literasi digital sekolah" => nasional.
- "Geely", "BYD", "Tesla", "Nissan", "Toyota", dll tentang MOBIL/
  MOTOR/LISTRIK => OTOMOTIF (bukan teknologi).
- "Hilirisasi nikel" => ekonomi.
- Review mobil/motor => otomotif.

GAMBAR (deskripsi_gambar):
- 3-6 kata kunci visual bahasa Inggris.
- Prioritas tema: mountain/rainforest/ocean/city skyline/space/galaxy/
  fruits/grass field/flower garden/car engine/motorcycle.
- DILARANG: hewan, tempat ibadah, alas kaki, insiden-korban.
- Manusia boleh SILUET/objek (tangan, punggung tanpa wajah).

PANJANG: target kata diberikan di pesan user. Dilarang menggembung.

JUDUL: maks 10 kata. Dilarang janjikan jadwal/klasemen/hasil/harga
bila isi tidak memuat datanya.

KHUSUS KESEHATAN: utamakan edukasi pakar. Bila tidak ada nama pakar
di materi, PAKAI nama pakar terkenal yang kamu YAKIN, ATAU tolak.

KHUSUS OTOMOTIF: fokus ke kendaraan/produk (spesifikasi, harga,
review). Jangan bahas teknologi AI/baterai secara mendalam.

FORMAT JAWABAN - HANYA JSON valid:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2", "ringkasan": "...",
 "kategori": "nasional|daerah|internasional|ekonomi|olahraga|teknologi|otomotif|kesehatan",
 "deskripsi_gambar": "visual keywords",
 "waktu_kejadian": "Hari (Tanggal Bulan """ + k['tahun'] + """)"}
"""

# AKHIR PART 2
    
# PART 3A - EDGE CALL, REST GET, STATE, GAMBAR, SKOR, DATELINE, PERSEN, VALIDATOR - V6.16.5

def edge_call(payload_json):
    if not ADMIN_SECRET:
        raise Exception('ADMIN_OPS_SECRET kosong - cek Secrets GitHub')
    r = requests.post(EDGE_URL,
        headers={'apikey': SUPABASE_PUBLISHABLE,
                 'Authorization': 'Bearer ' + SUPABASE_PUBLISHABLE,
                 'x-admin-secret': ADMIN_SECRET,
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
                print('   Breaking #' + str(row['id']) + ' dicabut (umur '
                      + str(int(umur)) + ' mnt > ' + str(menit) + ' mnt)')
        except Exception as e:
            print('   expire:', str(e)[:60])
    return n

def is_evergreen(cat):
    return cat in KATEGORI_EVERGREEN

def max_umur_kategori(cat):
    return UMUR_BERITA_PER_KATEGORI.get(cat, MAX_UMUR_BERITA_JAM)

def gambar_sampah(url):
    if not url:
        return True
    low = url.lower()
    if any(p in low for p in GAMBAR_SAMPAH_POLA):
        return True
    for k in GAMBAR_SAMPAH_KATA:
        if re.search(r'\b' + re.escape(k) + r'\b', low):
            return True
    for k in GAMBAR_LARANG_KATA:
        if k.endswith('_') or k.endswith('-'):
            if k in low:
                return True
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', low):
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

def collect_candidates(sources, today_urls, seen, max_umur_jam=None):
    if max_umur_jam is None:
        max_umur_jam = MAX_UMUR_BERITA_JAM
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
            if u is not None and u > max_umur_jam:
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

def barat_terbit_jumlah(kelompok):
    n = 0
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
                    n += 1
                elif kelompok == 'rusia' and any(k in teks for k in KATA_BARAT_RUSIA):
                    n += 1
                elif kelompok == 'eropa' and any(k in teks for k in KATA_BARAT_EROPA):
                    n += 1
            except Exception:
                pass
    except Exception:
        pass
    return n

def barat_sudah_terbit(kelompok, batas=2):
    return barat_terbit_jumlah(kelompok) >= batas

def deteksi_dua_topik(judul, isi):
    try:
        lokasi = set(re.findall(r'(?:^|\n)([A-Z][A-Z\s\.,\'\-]{2,40}?)\s+[-–—]\s+', isi or ''))
        if len(lokasi) >= 2:
            return 'isi memuat lebih dari satu dateline kota: ' + '; '.join(list(lokasi)[:3])
    except Exception:
        pass
    return None

VARIAN_KOTA_EN_ID = {
    'korea selatan': ['south korea', 'korea'],
    'korea': ['korea selatan', 'south korea', 'north korea'],
    'korea utara': ['north korea'],
    'inggris': ['england', 'uk', 'britain', 'united kingdom'],
    'jerman': ['germany'],
    'perancis': ['france'],
    'spanyol': ['spain'],
    'italia': ['italy'],
    'belanda': ['netherlands', 'holland'],
    'yunani': ['greece'],
    'turki': ['turkey', 'turkiye'],
    'mesir': ['egypt'],
    'jepang': ['japan'],
    'cina': ['china'],
    'india': ['india'],
    'rusia': ['russia'],
    'ukraina': ['ukraine'],
    'iran': ['iran'],
    'irak': ['iraq'],
    'suriah': ['syria'],
    'yaman': ['yemen'],
    'arab saudi': ['saudi arabia'],
    'uni emirat arab': ['united arab emirates', 'uae'],
    'qatar': ['qatar'],
    'filipina': ['philippines'],
    'vietnam': ['vietnam'],
    'thailand': ['thailand'],
    'malaysia': ['malaysia'],
    'singapura': ['singapore'],
    'myanmar': ['myanmar'],
    'kamboja': ['cambodia'],
    'laos': ['laos'],
    'australia': ['australia'],
    'amerika serikat': ['united states', 'us', 'usa', 'america'],
    'brasilia': ['brazil'],
    'argentina': ['argentina'],
    'seoul': ['seoul'],
    'beijing': ['beijing'],
    'tokyo': ['tokyo'],
    'london': ['london'],
    'paris': ['paris'],
    'moskow': ['moscow'],
    'washington': ['washington'],
    'new york': ['new york'],
}

def _varian_cocok(kota, sumber):
    if kota in sumber:
        return True
    varian = VARIAN_KOTA_EN_ID.get(kota, [])
    return any(v in sumber for v in varian)

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
    if kota and not _varian_cocok(kota, sumber):
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

POLA_PERSEN = re.compile(r'(\d[\d\.,]*)\s+persen\b', re.IGNORECASE)

def ada_persen_kata(teks):
    return bool(POLA_PERSEN.search(teks or ''))

def perbaiki_persen(teks):
    return POLA_PERSEN.sub(lambda m: m.group(1).rstrip('.,') + '%', teks or '')

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
    if any(w in j for w in JANJI_HARGA):
        ada_harga = (
            'rp' in b
            or re.search(r'\brp\.?\s*\d', b) is not None
            or re.search(r'\d[\d\.,]*\s*(?:rb|ribu|juta|miliar|triliun)\b', b) is not None
            or re.search(r'usd\s*\d', b) is not None
            or re.search(r'\$\s*\d', b) is not None
            or re.search(r'\b(?:dihargai|dibandrol|seharga|berharga)\b', b) is not None
        )
        if not ada_harga:
            tema_harga = any(k in b for k in (
                'harga', 'tengkulak', 'bulog', 'pasar', 'petani', 'pangan',
                'komoditas', 'inflasi', 'kurs', 'saham', 'ihsg', 'bursa',
                'parit', 'gabah', 'beras', 'jagung', 'cabai', 'beras'))
            ada_tren = any(w in j for w in KATA_HARGA_LONGGAR)
            if not tema_harga and not ada_tren:
                return ('judul menjanjikan HARGA/TARIF tapi isi tidak memuat '
                        'angka harga maupun tema harga')
    return None

def cek_deskripsi_gambar(deskripsi):
    d = (deskripsi or '').lower()
    for k in KATA_HEWAN_SLUG:
        if k.endswith('_') or k.endswith('-'):
            if k in d:
                return 'deskripsi gambar memuat kata hewan terlarang: ' + k
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', d):
                return 'deskripsi gambar memuat kata hewan terlarang: ' + k
    for k in GAMBAR_LARANG_KATA:
        if k.endswith('_') or k.endswith('-'):
            if k in d:
                return 'deskripsi gambar memuat kata terlarang: ' + k
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', d):
                return 'deskripsi gambar memuat kata terlarang: ' + k
    return None

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

POLA_JABATAN_TANPA_NAMA = [
    'menteri ', 'presiden ', 'wakil presiden ', 'gubernur ',
    'wakil gubernur ', 'walikota ', 'wakil walikota ', 'bupati ',
    'wakil bupati ', 'kepala dinas ', 'kepala cabang ', 'kepala badan ',
    'kepala kantor ', 'ketua ', 'wakil ketua ', 'direktur utama ',
    'dirut ', 'direktur ', 'komisaris ',
    'kasat ', 'kapolres ', 'kapolda ', 'kapolsek ', 'danramil ',
    'dandim ', 'panglima ', 'jenderal ', 'sekjen ', 'sekretaris jenderal ',
    'ketua umum ', 'presiden fifa', 'presiden pbb',
    'kepala perwakilan ', 'kepala daerah ',
]

def cek_jabatan_tanpa_nama(isi):
    if not isi:
        return None
    teks = isi
    KATA_KERJA = [
        'mengatakan', 'menyatakan', 'menjelaskan', 'menuturkan',
        'mengungkapkan', 'mengimbau', 'menghimbau', 'meminta',
        'menegaskan', 'menambahkan', 'mengatakan bahwa',
        'menyampaikan', 'menekankan', 'mengajak', 'memastikan',
        'berbicara', 'menegaskan bahwa',
    ]
    for jabatan in POLA_JABATAN_TANPA_NAMA:
        pola = re.compile(
            r'\b' + re.escape(jabatan).rstrip() + r'\s+(?:yang\s+)?('
            + '|'.join(re.escape(k) for k in KATA_KERJA) + r')\b',
            re.IGNORECASE
        )
        m = pola.search(teks)
        if m:
            awal = max(0, m.start() - 120)
            sebelum = teks[awal:m.start()]
            if re.search(r',\s*[A-Z][a-zA-Z\.\'\-]+', sebelum):
                continue
            return 'jabatan "' + jabatan.strip() + '" muncul tanpa nama orang'
    return None

PANGKAT_TNI_POLRI = [
    'jenderal', 'letnan jenderal', 'letjen', 'mayor jenderal', 'mayjen',
    'brigadir jenderal', 'brigjen', 'kolonel', 'letnan kolonel', 'letkol',
    'mayor', 'kapten', 'lettu', 'letda', 'letnan', 'pembantu letnan',
    'pelda', 'pelton', 'peltu', 'sersan', 'kopral', 'prajurit',
    'akbp', 'akp', 'iptu', 'ipda', 'bripka', 'brigpol', 'bripda',
    'komisaris besar', 'kombes', 'ajun komisaris besar',
    'komisaris', 'kompol', 'ajun komisaris',
    'inspektur', 'inspektur polisi satu', 'inspektur polisi dua',
    'ajun inspektur',
    'bharada', 'bharatu', 'bharaka', 'abrip',
]

INSTITUSI_BUTUH_NAMA = [
    'kementerian', 'kemenko', 'kemen',
    'dinas', 'badan', 'kantor', 'lembaga', 'komisi',
    'pemkot', 'pemkab', 'pemprov',
    'polres', 'polsek', 'polda', 'kodam', 'korem', 'kodim', 'koramil',
    'kejaksaan', 'kejari', 'kejati', 'pengadilan',
    'bawaslu', 'kpu', 'kppu', 'kppn', 'kpp', 'bpjs',
    'bank indonesia', 'ojk',
    'bulog', 'pertamina', 'pln', 'telkom',
    'perum', 'peruri', 'pelindo', 'angkasa pura',
    'kpk', 'bnpb', 'basarnas',
]

KATA_KERJA_NARASUMBER = [
    'mengatakan', 'menyatakan', 'menjelaskan', 'menuturkan',
    'mengungkapkan', 'mengimbau', 'menghimbau', 'meminta',
    'menegaskan', 'menambahkan', 'mengatakan bahwa',
    'menyampaikan', 'menekankan', 'mengajak', 'memastikan',
    'berbicara', 'menegaskan bahwa', 'menyebut', 'menyebutkan',
    'menjelaskan bahwa', 'menuturkan bahwa',
]

def _ada_nama_orang_sebelum(teks, posisi):
    awal = max(0, posisi - 150)
    sebelum = teks[awal:posisi]
    pola_nama = re.compile(r'[A-Z][a-z]+\s+(?:[A-Z]\.\s*)?[A-Z][a-z]+')
    if pola_nama.search(sebelum):
        return True
    return False

def cek_narasumber_tanpa_nama(isi, kategori=''):
    if not isi:
        return None
    if kategori in ('internasional', 'internasional_asean', 'internasional_tt'):
        return None
    teks = isi
    for pangkat in PANGKAT_TNI_POLRI:
        pola = re.compile(
            r'\b' + re.escape(pangkat) + r'\s+('
            + '|'.join(re.escape(k) for k in KATA_KERJA_NARASUMBER) + r')\b',
            re.IGNORECASE
        )
        m = pola.search(teks)
        if m:
            if not _ada_nama_orang_sebelum(teks, m.start()):
                return ('pangkat TNI/Polri "' + pangkat
                        + '" muncul tanpa nama orang')
        pola2 = re.compile(
            r'\b' + re.escape(pangkat) + r'\s*,\s*('
            + '|'.join(re.escape(k) for k in KATA_KERJA_NARASUMBER) + r')\b',
            re.IGNORECASE
        )
        if pola2.search(teks):
            return ('pangkat TNI/Polri "' + pangkat
                    + '" diikuti koma langsung kata kerja (tanpa nama)')
    for inst in INSTITUSI_BUTUH_NAMA:
        pola = re.compile(
            r'\b' + re.escape(inst) + r'\b[^\.]{0,60}?\s+('
            + '|'.join(re.escape(k) for k in KATA_KERJA_NARASUMBER) + r')\b',
            re.IGNORECASE
        )
        m = pola.search(teks)
        if m:
            if not _ada_nama_orang_sebelum(teks, m.start()):
                return ('institusi "' + inst
                        + '" muncul tanpa nama pejabat')
    for inst in INSTITUSI_BUTUH_NAMA:
        pola3 = re.compile(
            r'\bmenurut\s+' + re.escape(inst) + r'\b[^\.]{0,30}?[,\.]',
            re.IGNORECASE
        )
        if pola3.search(teks):
            return ('"menurut ' + inst + '" tanpa nama pejabat')
    return None

def cek_nama_lembaga_diterjemahkan(judul, isi):
    if not judul:
        return None
    kata_aneh_terjemahan = [
        'kecoak', 'kecoa', 'tikus', 'ular', 'kadal', 'cicak',
        'kucing', 'anjing', 'monyet', 'babi', 'kerbau',
        'gerakan kecoak', 'partai kecoak', 'partai tikus',
    ]
    j_low = (judul or '').lower()
    for k in kata_aneh_terjemahan:
        if k in j_low:
            return 'judul memuat terjemahan nama lembaga yang aneh: "' + k + '"'
    pola_aneh = re.compile(
        r'\b(partai|gerakan|organisasi|asosiasi|lembaga)\s+[a-z]+\s+'
        r'(india|china|jepang|korea|amerika|rusia|mesir|iran|irak)\b',
        re.IGNORECASE
    )
    m = pola_aneh.search(judul)
    if m:
        tengah = m.group(0).split()[1].lower()
        kata_wajar = ['buruh', 'tani', 'nelayan', 'islam', 'kristen',
                      'hindu', 'budha', 'nasional', 'demokrasi', 'rakyat',
                      'merdeka', 'keadilan', 'persatuan', 'kebangsaan']
        if tengah not in kata_wajar:
            return ('judul memuat kemungkinan terjemahan nama lembaga: "'
                    + m.group(0) + '"')
    return None

# ═══ V6.16.5: validator judul vs materi DIPERBAIKI LAGI ═══
# Blokir HANYA nama orang (2+ kata Kapital), bukan frasa kerja.
# DAN cek bahwa judul nyambung dengan materi (topik sama).
KATA_KERJA_JUDUL = [
    'kirim', 'kirimkan', 'uji', 'ujicoba', 'coba', 'luncurkan', 'rilis',
    'umumkan', 'buka', 'tutup', 'gelar', 'gelar', 'mulai', 'akhiri',
    'pimpin', 'pimpin', 'kunjungi', 'hadiri', 'sambut', 'terima',
    'tolak', 'dukung', 'desak', 'minta', 'harap', 'imbau', 'ajak',
    'tegaskan', 'nyatakan', 'jelaskan', 'sebut', 'tambah', 'tekan',
    'catat', 'raih', 'menang', 'kalah', 'unggul', 'susul',
    'naik', 'turun', 'melonjak', 'anjlok', 'menguat', 'melemah',
    'buka', 'tutup', 'siap', 'siapkan', 'susun', 'bahas', 'kaji',
    'lakukan', 'kerjakan', 'buat', 'ciptakan', 'temukan', 'ganti',
    'beri', 'kasih', 'terapkan', 'terapkan', 'pasang', 'lepas',
]

def cek_judul_vs_materi(judul, materi_sumber):
    """V6.16.5: blokir HANYA nama orang (2+ kata Kapital berurutan).
    Kata kerja/frasa kerja DIBOLEHKAN walau tidak ada di materi."""
    if not judul or not materi_sumber:
        return None
    materi_low = materi_sumber.lower()
    # Cek nama orang: 2+ kata Kapital berurutan (Title Case)
    pola_nama = re.compile(r'\b[A-Z][a-z]{2,}\s+(?:[A-Z]\.\s*)?[A-Z][a-z]{2,}\b')
    kandidat_nama = pola_nama.findall(judul)
    for nama in kandidat_nama:
        # Cek kata pertama apakah kata kerja umum → skip
        kata_pertama = nama.split()[0].lower()
        if kata_pertama in KATA_KERJA_JUDUL:
            continue
        # Cek apakah nama ada di materi (lowercase substring)
        if nama.lower() in materi_low:
            continue
        # Cek per kata
        bagian = nama.split()
        ada_di_materi = sum(1 for b in bagian if b.lower() in materi_low)
        if ada_di_materi >= len(bagian) - 1:
            continue
        # Kalau tidak ada di materi → blokir
        return ('judul memuat nama yang tidak ada di materi: ' + nama)
    return None

# ═══ V6.16.5: cek judul-isi nyambung topik ═══
def cek_judul_isi_nyambung(judul, isi):
    """V6.16.5: pastikan judul & isi satu topik.
    Ambil 3 kata kunci dari judul, cek ada di 5 kalimat pertama isi."""
    if not judul or not isi:
        return None
    # Kata kunci judul (buang stopword)
    STOP = set('yang dan di ke dari untuk pada dengan dalam ini itu akan telah '
               'sudah oleh sebagai ada adalah para kami mereka tidak bisa '
               'dapat juga lebih masih hanya setelah sebelum sekitar the and '
               'for with from that this have will been are was were they'.split())
    kata_judul = set(w.lower() for w in re.findall(r'[a-zA-Z]{4,}', judul)
                     if w.lower() not in STOP)
    if not kata_judul:
        return None
    # Ambil awal isi (500 karakter pertama, setelah dateline)
    isi_awal = re.sub(r'^[A-Z][^\n]{1,60}?\s*[-–—]\s*', '', isi)[:800].lower()
    # Hitung berapa kata judul yang muncul di awal isi
    match = sum(1 for w in kata_judul if w in isi_awal)
    # Minimal 30% kata judul muncul di awal isi
    rasio = match / len(kata_judul) if kata_judul else 0
    if rasio < 0.3:
        return ('judul & isi tidak nyambung (kemiripan '
                + str(int(rasio * 100)) + '%)')
    return None

KATA_BUKAN_BERITA = [
    'zodiak', 'horoskop', 'ramalan bintang', 'ramalan cinta',
    'ramalan nasib', 'ramalan zodiak', 'shio', 'primbon',
    'arti mimpi', 'artinya mimpi', 'pertanda baik', 'pertanda buruk',
    'keberuntungan hari ini', 'peruntungan',
]

def cek_bukan_berita(judul, isi):
    gab = ((judul or '') + ' ' + (isi or '')).lower()
    for k in KATA_BUKAN_BERITA:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', gab):
                return True
        else:
            if k in gab:
                return True
    return False

# AKHIR PART 3A

# PART 3B - BAGIAN 1 DARI 2 - V6.16.5

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
        sumber.append(GN(q, lang, 'GN Kesehatan: ' + dom['nama'], when='180d'))
    sumber.append(RSSF('https://health.kompas.com/rss', 'Kompas Health'))
    sumber.append(RSSF('https://feeds.bbci.co.uk/news/health/rss.xml', 'BBC Health'))
    print('   KESEHATAN hari ini (jam ' + str(jam) + '): ' + dom['nama'])
    return dom, sumber

def sumber_otomotif_hari_ini(jam):
    if jam not in JAM_OTOMOTIF:
        return None, None
    try:
        dasar = datetime(2026, 1, 1).date()
        indeks = (datetime.now(WITA).date() - dasar).days % len(DOMAIN_OTOMOTIF)
    except Exception:
        indeks = 0
    idx_domain = (indeks + JAM_OTOMOTIF[jam]) % len(DOMAIN_OTOMOTIF)
    dom = DOMAIN_OTOMOTIF[idx_domain]
    sumber = []
    for q, lang in dom['query']:
        sumber.append(GN(q, lang, 'GN Otomotif: ' + dom['nama'], when='180d'))
    sumber.append(RSSF('https://www.otomotifnet.com/rss', 'Otomotifnet'))
    sumber.append(RSSF('https://www.gridoto.com/rss', 'GridOto'))
    sumber.append(RSSF('https://autonetmagz.com/feed/', 'Autonetmagz'))
    print('   OTOMOTIF hari ini (jam ' + str(jam) + '): ' + dom['nama'])
    return dom, sumber

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
    print('   TEKNOLOGI hari ini (jam ' + str(jam) + '): ' + dom['nama'])
    return dom, sumber

POLA_LARANG = [
    'belum dikonfirmasi waktu', 'waktu kejadian belum',
    'belum dikonfirmasi kapan',
    'menurut informasi yang diterima', 'diduga kuat',
    'kabarnya',
    'identitas narasumber',
    'tidak disebutkan dalam laporan',
    'tidak disebutkan secara eksplisit',
    'tanpa menyebut nama',
    'tanpa menyebut nama pejabat',
    'dalam laporan yang beredar',
    'dalam laporan yang dihimpun',
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
        json={'model': 'deepseek-flash',
              'messages': [{'role': 'system', 'content': build_system_prompt()},
                           {'role': 'user', 'content': user_content}],
              'temperature': temperature},
        timeout=150)
    r.raise_for_status()
    return parse_ai_json(r.json()['choices'][0]['message']['content'])

def _kata_bersih(teks):
    return re.sub(r'[^a-z0-9\s]', ' ', (teks or '').lower()).split()

def _gram_list(teks, n):
    kata = _kata_bersih(teks)
    return [tuple(kata[i:i+n]) for i in range(len(kata) - n + 1)] if len(kata) >= n else []

def _gram_set(teks, n):
    kata = _kata_bersih(teks)
    return set(tuple(kata[i:i+n]) for i in range(len(kata) - n + 1)) if len(kata) >= n else set()

def cek_jiplak(materi_sumber, isi_ai):
    if not materi_sumber or not isi_ai:
        return None
    n_kata = 15
    if len(materi_sumber) < 500:
        n_kata = 25
    sumber_grams = _gram_set(materi_sumber, n_kata)
    if not sumber_grams:
        return None
    for gram in _gram_list(isi_ai, n_kata):
        if gram in sumber_grams:
            return ' '.join(gram)
    return None

def _paksa_dateline_indonesia(isi):
    m = re.match(r'^([^\n]{1,80}?)\s+[-–—]\s+', isi or '')
    if m:
        return 'INDONESIA - ' + isi[m.end():]
    return 'INDONESIA - ' + (isi or '')

LIGA_API_FOOTBALL = {
    'eng.1': 39, 'esp.1': 140, 'ita.1': 135, 'ger.1': 78,
    'fra.1': 61, 'ned.1': 88, 'uefa.champions': 2, 'uefa.europa': 3,
    'uefa.europa.conf': 848, 'idn.1': 274,
}

LIGA_API_NAMA = {
    39: 'Premier League (Inggris)', 140: 'La Liga (Spanyol)',
    135: 'Serie A (Italia)', 78: 'Bundesliga (Jerman)',
    61: 'Ligue 1 (Prancis)', 88: 'Eredivisie (Belanda)',
    2: 'Liga Champions', 3: 'Liga Europa', 848: 'Liga Conference',
    274: 'Liga 1 (Indonesia)',
}

def _musim_sekarang():
    now = datetime.now(WITA)
    if now.month >= 7:
        return now.year
    return now.year - 1

def football_api_get(endpoint, params=None, timeout=20):
    if not FOOTBALL_API_KEY:
        return None
    url = FOOTBALL_API_URL + endpoint
    try:
        r = requests.get(url,
            headers={'x-apisports-key': FOOTBALL_API_KEY},
            params=params or {},
            timeout=timeout)
        if not r.ok:
            print('       API Football HTTP ' + str(r.status_code) + ' - ' + endpoint)
            return None
        data = r.json()
        errors = data.get('errors') or {}
        if errors and isinstance(errors, dict) and len(errors) > 0:
            print('       API Football error: ' + str(errors)[:80])
            return None
        return data
    except Exception as e:
        print('       API Football gagal: ' + str(e)[:60])
        return None

def api_klasmen_football(liga_code):
    liga_id = LIGA_API_FOOTBALL.get(liga_code)
    if not liga_id:
        return '', ''
    data = football_api_get('/standings', {
        'league': liga_id, 'season': _musim_sekarang(),
    })
    if not data:
        return '', ''
    resp = data.get('response') or []
    if not resp:
        return '', ''
    semua_grup = []
    try:
        liga_data = resp[0].get('league', {}).get('standings', []) or []
        for grup in liga_data:
            semua_grup.append(grup)
    except Exception:
        return '', ''
    if not semua_grup:
        return '', ''
    nama_liga = LIGA_API_NAMA.get(liga_id, 'Klasmen')
    bagian = []
    teks_ringkas = []
    for idx_grup, grup in enumerate(semua_grup):
        label = nama_liga
        if len(semua_grup) > 1:
            label = nama_liga + ' - Grup ' + chr(65 + idx_grup)
        baris = []
        for entry in grup[:20]:
            try:
                rank = entry.get('rank')
                tim = (entry.get('team') or {}).get('name', '?')
                poin = entry.get('points', 0)
                main = entry.get('all', {}).get('played', 0)
                menang = entry.get('all', {}).get('win', 0)
                draw = entry.get('all', {}).get('draw', 0)
                kalah = entry.get('all', {}).get('lose', 0)
                if rank is None:
                    continue
                baris.append((int(rank), tim, int(main), int(menang),
                              int(draw), int(kalah), int(poin)))
            except Exception:
                continue
        if not baris:
            continue
        blok = '[KLASMEN]\n' + label + '\n'
        for rank, tim, main, mn, dr, kl, pt in baris:
            blok += str(rank) + '|' + tim + '|' + str(main) + '|' \
                    + str(mn) + '|' + str(dr) + '|' + str(kl) + '|' + str(pt) + '\n'
        blok += '[/KLASMEN]'
        bagian.append(blok)
        teks_ringkas.append(label + ': ' + ', '.join(
            str(r) + '. ' + t + ' (' + str(p) + ' poin)'
            for r, t, _, _, _, _, p in baris[:6]))
    return '\n\n'.join(bagian), ' | '.join(teks_ringkas)

def api_skor_football(liga_code, hari_mundur=2):
    liga_id = LIGA_API_FOOTBALL.get(liga_code)
    if not liga_id:
        return []
    t0 = (datetime.now(WITA) - timedelta(days=hari_mundur)).date()
    t1 = (datetime.now(WITA) + timedelta(days=1)).date()
    hasil = []
    for tanggal in (t0, t1):
        data = football_api_get('/fixtures', {
            'league': liga_id, 'season': _musim_sekarang(),
            'date': tanggal.strftime('%Y-%m-%d'),
        })
        if not data:
            continue
        resp = data.get('response') or []
        for ev in resp:
            try:
                status = (ev.get('fixture') or {}).get('status') or {}
                short = status.get('short', '')
                if short not in ('FT', 'AET', 'PEN'):
                    continue
                home = (ev.get('teams') or {}).get('home', {}).get('name', '?')
                away = (ev.get('teams') or {}).get('away', {}).get('name', '?')
                gh = (ev.get('goals') or {}).get('home')
                ga = (ev.get('goals') or {}).get('away')
                if gh is None or ga is None:
                    continue
                hasil.append(home + ' ' + str(int(gh)) + ' - ' + str(int(ga)) + ' ' + away)
            except Exception:
                continue
    return list(dict.fromkeys(hasil))

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
    for k in KATA_HEWAN_FILE:
        if k.endswith('_') or k.endswith('-'):
            if k in low:
                return True
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', low):
                return True
    return False

def cari_gambar_wikimedia(deskripsi):
    if not deskripsi:
        return ''
    try:
        if cek_deskripsi_gambar(deskripsi):
            print('       Deskripsi berbau hewan/terlarang - Wikimedia dilewati.')
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
            print('       Kandidat Wikimedia tak layak - tanpa gambar.')
    except Exception:
        pass
    return ''

PEXELS_API = 'https://api.pexels.com/v1/search'

def cari_gambar_pexels(deskripsi):
    kunci = os.environ.get('PEXELS_API_KEY', '')
    if not kunci:
        print('       PEXELS_API_KEY belum ada di Secrets - lewati Pexels.')
        return ''
    if not deskripsi:
        return ''
    try:
        r = requests.get(PEXELS_API,
            headers={'Authorization': kunci},
            params={'query': deskripsi, 'per_page': 6, 'orientation': 'landscape'},
            timeout=20)
        if not r.ok:
            print('       Pexels HTTP ' + str(r.status_code) + ' - lewati.')
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
            print('       Semua kandidat Pexels terpakai/sampah - fallback Wikimedia.')
    except Exception as e:
        print('       Pexels gagal: ' + str(e)[:60])
    return ''

WORKER_GAMBAR_URL = 'https://kramanews-generate-image.denytriono-btm.workers.dev'

def generate_gambar_ai(deskripsi):
    if not deskripsi:
        return ''
    try:
        r = requests.post(WORKER_GAMBAR_URL,
            headers={'Content-Type': 'application/json'},
            json={'prompt': deskripsi},
            timeout=30)
        if not r.ok:
            print('       AI gambar HTTP ' + str(r.status_code) + ' - lewati.')
            return ''
        data = r.json()
        url = (data.get('image') or '').strip()
        if not url:
            print('       AI gambar kosong - lewati.')
            return ''
        if url.startswith('data:'):
            print('       AI gambar gagal upload ke Supabase - lewati.')
            return ''
        return url
    except Exception as e:
        print('       AI gambar gagal: ' + str(e)[:60])
        return ''

def cari_gambar_otomatis(deskripsi, judul_berita):
    img = cari_gambar_pexels(deskripsi)
    if img:
        return img, 'pexels'
    print('       Pexels kosong - fallback Wikimedia...')
    img = cari_gambar_wikimedia(deskripsi)
    if img:
        return img, 'wikimedia'
    print('       Wikimedia kosong - fallback AI generate...')
    return generate_gambar_ai(deskripsi), 'ai'

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
        print('   Gagal muat gambar terpakai:', str(e)[:60])
    _GAMBAR_TERPAKAI_CACHE = out
    return out

def gambar_sudah_dipakai(url):
    if not url:
        return False
    return url in muat_gambar_terpakai()

def catat_gambar_terpakai(url):
    if url:
        muat_gambar_terpakai().add(url)

# V6.16.5: ai_write tambah validator judul-isi nyambung
def ai_write(user_content, timeout=150, materi_sumber='', kategori=''):
    obj = None
    materi_asli = user_content
    frasa_dikoreksi = 0
    dateline_dikoreksi = False
    nama_dikoreksi = 0
    lembaga_dikoreksi = False
    judul_materi_dikoreksi = False
    judul_isi_dikoreksi = False
    koneksi_retry = 0
    MAX_KONEKSI_RETRY = 2
    MAX_NAMA_KOREKSI = 1
    MAX_FRASA_KOREKSI = 1
    MAX_LOOP = 7
    FRASA_TOLAK_AI = [
        'materi tidak tersedia',
        'materi sumber tidak tersedia',
        'materi tidak relevan',
        'tidak dapat menulis',
        'tidak ada materi',
    ]
    percobaan = 0
    while percobaan < MAX_LOOP:
        percobaan += 1
        temp = 0.5 if percobaan == 1 else 0.3
        try:
            obj = _panggil_deepseek(user_content, temp)
        except BeritaLama:
            raise
        except Exception as e:
            if koneksi_retry >= MAX_KONEKSI_RETRY:
                raise
            koneksi_retry += 1
            print('       Panggilan AI gagal (' + str(e)[:60] + ') - retry koneksi '
                  + str(koneksi_retry) + '/' + str(MAX_KONEKSI_RETRY) + '...')
            continue
        tolak_msg = str(obj.get('tolak', '')).strip()
        if tolak_msg:
            tl = tolak_msg.lower()
            if any(f in tl for f in FRASA_TOLAK_AI) and percobaan < MAX_LOOP:
                print('       AI tolak bingung ("' + tolak_msg[:50] + '") - '
                      'minta tulis ulang (percobaan ' + str(percobaan) + ')')
                user_content = (
                    'CATATAN: MATERI SUMBER TERSEDIA di atas. '
                    'TULIS ULANG berita sesuai SEMUA aturan. '
                    'Jangan tolak. Materi sumber ada di pesan sebelumnya.\n\n'
                    'MATERI SUMBER:\n' + materi_sumber[:3000] + '\n\n'
                    'Tulis berita JSON valid.')
                continue
            raise BeritaLama(tolak_msg[:100])
        isi_c = obj.get('isi', '').strip()
        judul_c = obj.get('judul', '').strip()
        frasa = _frasa_tertangkap(isi_c)
        cek_dl = cek_dateline(isi_c, materi_asli)
        nama_masalah = None
        if nama_dikoreksi < MAX_NAMA_KOREKSI:
            nama_masalah = cek_narasumber_tanpa_nama(isi_c, kategori)
        lembaga_masalah = None
        if not lembaga_dikoreksi:
            lembaga_masalah = cek_nama_lembaga_diterjemahkan(judul_c, isi_c)
        judul_masalah = None
        if not judul_materi_dikoreksi and materi_sumber:
            judul_masalah = cek_judul_vs_materi(judul_c, materi_sumber)
        # V6.16.5: cek judul-isi nyambung
        judul_isi_masalah = None
        if not judul_isi_dikoreksi:
            judul_isi_masalah = cek_judul_isi_nyambung(judul_c, isi_c)
        if frasa and frasa_dikoreksi < MAX_FRASA_KOREKSI:
            frasa_dikoreksi += 1
            print('       Koreksi frasa #' + str(frasa_dikoreksi) + ': "'
                  + frasa + '"...')
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena memuat frasa '
                'terlarang: "' + frasa + '".\n\n'
                'TULIS ULANG berita yang sama dengan ATURAN KETAT:\n'
                '- HAPUS total frasa itu dan semua variannya.\n'
                '- DILARANG deskripsi kabur pengganti nama orang.\n'
                '- Atribusi HANYA ke institusi yang tertulis di materi.\n'
                '- Jangan mengubah fakta, angka, tanggal, struktur lain.\n'
                '- Jawab HANYA JSON valid dengan format yang sama.')
            continue
        if cek_dl and not dateline_dikoreksi:
            dateline_dikoreksi = True
            print('       Koreksi dateline: ' + cek_dl[:60] + '...')
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena DATELINE-nya '
                'bermasalah: ' + cek_dl + '.\n\n'
                'Berikut MATERI SUMBER ASLI:\n'
                '==========================================\n'
                + materi_asli + '\n'
                '==========================================\n\n'
                'PERBAIKI DATELINE:\n'
                '- Gunakan HANYA nama tempat yang TERTULIS di materi.\n'
                '- Jika tidak ada tempat sama sekali, dateline = "INDONESIA - ".\n'
                '- Isi berita JANGAN DIUBAH.\n'
                '- Jawab HANYA JSON valid dengan format yang sama.')
            continue
        # V6.16.5: koreksi judul-isi tidak nyambung (prioritas)
        if judul_isi_masalah and not judul_isi_dikoreksi:
            judul_isi_dikoreksi = True
            print('       Koreksi judul-isi: ' + judul_isi_masalah[:80])
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena: ' + judul_isi_masalah + '.\n\n'
                'ATURAN: Judul dan ISI HARUS satu topik yang sama.\n'
                'Judul harus mencerminkan isi berita.\n\n'
                'Berikut MATERI SUMBER ASLI:\n'
                '==========================================\n'
                + materi_asli + '\n'
                '==========================================\n\n'
                'TULIS ULANG berita dengan JUDUL dan ISI yang NYAMBUNG '
                '(satu topik).\n'
                'Jawab HANYA JSON valid dengan format yang sama.')
            continue
        if judul_masalah and not judul_materi_dikoreksi:
            judul_materi_dikoreksi = True
            print('       Koreksi judul vs materi: ' + judul_masalah[:80])
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena: ' + judul_masalah + '.\n\n'
                'ATURAN: Judul dan isi HANYA boleh bicara topik yang ADA '
                'di materi. DILARANG menambah nama orang/lembaga/tempat baru.\n\n'
                'CATATAN: Kata kerja/umum (Dukung, Pertama, Kirim, Uji) '
                'BOLEH muncul walau tidak ada di materi.\n\n'
                'Berikut MATERI SUMBER ASLI:\n'
                '==========================================\n'
                + materi_asli + '\n'
                '==========================================\n\n'
                'TULIS ULANG berita DENGAN JUDUL & ISI yang hanya bicara '
                'topik di materi.\n'
                'Jawab HANYA JSON valid dengan format yang sama.')
            continue
        if nama_masalah and nama_dikoreksi < MAX_NAMA_KOREKSI:
            nama_dikoreksi += 1
            print('       Koreksi nama #' + str(nama_dikoreksi) + ': '
                  + nama_masalah[:80])
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena: ' + nama_masalah + '.\n\n'
                'ATURAN WAJIB (ULANG): Setiap pejabat/tokoh yang disebut '
                'WAJIB ada NAMA LENGKAPNYA.\n\n'
                'Contoh SALAH vs BENAR:\n'
                '- SALAH: "Bawaslu Tarakan menyatakan penyediaan fasilitas..."\n'
                '- BENAR: "Ketua Bawaslu Tarakan, [nama lengkap], menyatakan..."\n'
                '- SALAH: "Kodam VI/Mulawarman menegaskan..."\n'
                '- BENAR: "Panglima Kodam VI/Mulawarman, Mayjen TNI [nama lengkap], '
                'menegaskan..."\n'
                '- SALAH: "AKBP mengatakan..."\n'
                '- BENAR: "Kapolres Tarakan, AKBP [nama lengkap], mengatakan..."\n\n'
                'WAJIB sertakan GELAR AKADEMIK kalau materi menyebutnya.\n\n'
                'Kalau kamu TIDAK YAKIN nama pejabat yang menjabat sekarang, '
                'jawab HANYA dengan: {"tolak":"narasumber tanpa nama"}.\n\n'
                'Isi berita JANGAN DIUBAH selain soal nama.\n'
                'Jawab HANYA JSON valid dengan format yang sama.')
            continue
        if lembaga_masalah and not lembaga_dikoreksi:
            lembaga_dikoreksi = True
            print('       Koreksi lembaga: ' + lembaga_masalah[:80])
            user_content = (
                'TULISANMU SEBELUMNYA DITOLAK SISTEM karena: ' + lembaga_masalah + '.\n\n'
                'ATURAN: Nama partai, perusahaan, organisasi, tim olahraga, '
                'dan institusi asing TIDAK BOLEH diterjemahkan.\n\n'
                'Contoh SALAH vs BENAR:\n'
                '- SALAH: "Partai Kecoak India"\n'
                '- BENAR: "Cockroach Janta Party (CJP)"\n'
                '- SALAH: "Persatuan Manchester"\n'
                '- BENAR: "Manchester United"\n\n'
                'Perbaiki: tulis nama lembaga dalam bahasa ASLINYA.\n'
                'Jawab HANYA JSON valid dengan format yang sama.')
            continue
        break

    if obj is None:
        raise Exception('AI tidak menghasilkan output valid')

    judul = perbaiki_persen(obj.get('judul', '').strip())
    isi = perbaiki_persen(obj.get('isi', '').strip())
    ringkasan = perbaiki_persen(obj.get('ringkasan', '').strip())
    if ada_persen_kata(judul + ' ' + isi + ' ' + ringkasan):
        print('       Persen auto-fix diterapkan.')
    waktu = (obj.get('waktu_kejadian') or '').strip()
    gambar = (obj.get('deskripsi_gambar') or '').strip()
    frasa_akhir = _frasa_tertangkap(isi)
    if frasa_akhir:
        raise Exception('diblokir pemeriksa: ' + str(frasa_akhir)[:50])
    alasan_janji = cek_janji_judul(judul, isi)
    if alasan_janji:
        raise Exception('diblokir promise-check: ' + alasan_janji)
    dua_topik = deteksi_dua_topik(judul, isi)
    if dua_topik:
        raise Exception('diblokir anti-2-topik: ' + dua_topik[:60])
    cek_dl = cek_dateline(isi, materi_asli)
    if cek_dl:
        print('       Dateline masih salah setelah koreksi - paksa INDONESIA -')
        isi = _paksa_dateline_indonesia(isi)
    if not judul_topik_besar(judul):
        for t in JUDUL_6JAM:
            if len(kata_inti(judul) & kata_inti(t)) >= DOBEL_6JAM_MIN_KATA:
                raise Exception('diblokir anti-dobel-6jam: mirip "' + t[:40] + '"')
    else:
        print('       Topik besar terdeteksi - gate 6jam dilewati.')
    # V6.16.5: cek judul-isi nyambung (final)
    ji_final = cek_judul_isi_nyambung(judul, isi)
    if ji_final:
        raise Exception('DITOLAK V6.16.5 - ' + ji_final[:80])
    # V6.16.5: cek judul vs materi (final)
    if materi_sumber:
        jm_final = cek_judul_vs_materi(judul, materi_sumber)
        if jm_final:
            raise Exception('DITOLAK V6.16.5 - ' + jm_final[:80])
    nama_final = cek_narasumber_tanpa_nama(isi, kategori)
    if nama_final:
        raise Exception('DITOLAK V6.16.5 - narasumber tanpa nama ('
                        + nama_final[:60] + ')')
    gambar_terlarang = cek_deskripsi_gambar(gambar)
    if gambar_terlarang:
        raise Exception('diblokir filter gambar: ' + gambar_terlarang[:60])
    jiplak = cek_jiplak(materi_sumber, judul + ' ' + isi)
    if jiplak:
        raise Exception('diblokir ANTI-JIPLAK V6.16.5: kalimat tersalin: "'
                        + jiplak[:70] + '"')
    return judul, isi, ringkasan, waktu, gambar

def target_kata(materi_len):
    if materi_len < 500:
        return ('200-300 kata (3-5 paragraf) - sumber ringkas, tulis PADAT, '
                'dilarang menggembung dengan kalimat pengisi.')
    return '350-500 kata (5-7 paragraf).'

def ai_rewrite_single(c, kategori_target=''):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian sebagai peristiwa TERKINI dengan tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + target_kata(len(materi)) + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi + '\n\n'
            'Tulis ulang sesuai SEMUA aturan:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- TNI/POLRI: WAJIB nama + pangkat + jabatan.\n'
            '- GELAR AKADEMIK: ikut kalau ada di materi.\n'
            '- NAMA LEMBAGA: JANGAN diterjemahkan.\n'
            '- JUDUL DAN ISI: HARUS satu topik yang sama.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang dengan kalimatmu sendiri.\n'
            '- Jangan sebut portal/media sumber.')
    return ai_write(user, materi_sumber=materi, kategori=kategori_target)

def ai_rewrite_multi(items, kategori_target=''):
    k = konteks_waktu()
    bagian = []
    total_len = 0
    tgl = None
    semua_materi = ''
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
        semua_materi += ' ' + materi
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian sebagai peristiwa TERKINI.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + target_kata(total_len) + '\n\n'
            'Berikut beberapa materi tentang SATU peristiwa yang sama:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita KramaNews:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- TNI/POLRI: WAJIB nama + pangkat + jabatan.\n'
            '- GELAR AKADEMIK: ikut kalau ada di materi.\n'
            '- NAMA LEMBAGA: JANGAN diterjemahkan.\n'
            '- JUDUL DAN ISI: HARUS satu topik yang sama.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang dengan kalimatmu sendiri.')
    return ai_write(user, timeout=180, materi_sumber=semua_materi, kategori=kategori_target)

# AKHIR PART 3B BAGIAN 1
# PART 3B - BAGIAN 2 DARI 2 - V6.16.3

def insert_news(judul, isi, ringkasan, cat, img, link, source_name, status,
                breaking=False, deskripsi_gambar=''):
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+(.*)$', isi, re.DOTALL)
    dateline = m.group(1).strip() if m else ''
    isi_bersih = m.group(2).strip() if m else isi
    if masih_barusan_terbit(judul):
        raise Exception('diblokir anti-dobel insert-momen')
    img_final = ''
    sumber_gambar = ''
    if deskripsi_gambar:
        img_final, sumber_gambar = cari_gambar_otomatis(deskripsi_gambar, judul)
        if img_final:
            # V6.16.3: skip vision untuk Wikimedia (sudah terkurasi)
            if sumber_gambar == 'wikimedia':
                print('   Gambar Wikimedia - skip vision (V6.16.3).')
            else:
                print('   Gambar baru ditemukan - cek vision...')
                if not gambar_lolos_blur_gate(img_final, judul):
                    img_final = ''
    if not img_final:
        img_final = 'https://picsum.photos/seed/kn' + str(int(datetime.now().timestamp())) + '/800/500'
        print('   Fallback Picsum dipakai (gambar AI kosong).')
    payload = {
        'title': judul, 'excerpt': ringkasan, 'content': isi_bersih,
        'category': cat, 'author': AUTHOR_NAME,
        'img': img_final,
        'dateline': dateline,
        'source_name': source_name, 'source_url': link,
        'written_by': 'ai', 'status': status,
    }
    if breaking:
        payload['breaking'] = True
    edge_call({'action': 'insert', 'payload': payload})
    catat_gambar_terpakai(img_final)
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
                'model': 'deepseek-flash',
                'messages': [
                    {'role': 'user', 'content': [
                        {'type': 'text',
                         'text': ('Nilai gambar ini untuk berita berjudul: "'
                                  + judul_berita[:120] + '". '
                                  'ATURAN PENILAIAN: '
                                  '(1) HEWAN APAPUN di dalam foto = skor MAKSIMAL 2. '
                                  '(2) MANUSIA sebagai subjek utama dengan WAJAH JELAS '
                                  'atau KERUMUNAN = skor MAKSIMAL 3. '
                                  '(2b) SILUET manusia atau tangan memegang objek = '
                                  'DIPERBOLEHKAN, skor 7-10. '
                                  '(3) ALAS KAKI = skor MAKSIMAL 3. '
                                  '(4) TIDAK NYAMBUNG dengan judul = skor 1-4. '
                                  '(5) Blur, rusak, iklan, placeholder, logo = skor 1-4. '
                                  '(6) Gambar sesuai tema, tajam, bebas hewan/alas kaki = skor 8-10. '
                                  'Jawab HANYA JSON: {"skor": <angka>} '
                                  'KRAMAV6163MARKER')},
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
        print('       Vision gagal menilai - gambar dipertahankan.')
        return True
    print('       Vision skor: ' + str(skor) + '/10 - ' +
          ('LOLOS' if skor >= BLUR_SKOR_MINIMUM else 'DIBUANG'))
    return skor >= BLUR_SKOR_MINIMUM

def _target_teknologi(dom):
    if dom['nama'].startswith(('Gadget', 'AI')):
        return ('500-600 kata (7-9 paragraf) - PADAT & LENGKAP, '
                'sesuai aturan kedalaman domain.')
    return '400-600 kata (6-9 paragraf) - LENGKAP & BANYAK.'

def ai_rewrite_teknologi_single(c, dom):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian TERKINI dengan tanggal konkret.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTIP):\n' + dom['aturan'] + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi + '\n\n'
            'Tulis berita teknologi sesuai SEMUA aturan sistem + ATURAN '
            'KEDALAMAN DOMAIN di atas:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: HANYA dari tempat yang tertulis di materi.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang kalimatmu sendiri.')
    return ai_write(user, materi_sumber=materi, kategori='teknologi')

def ai_rewrite_teknologi_multi(items, dom):
    k = konteks_waktu()
    bagian = []
    tgl = None
    semua_materi = ''
    for i, it in enumerate(items[:4], 1):
        materi, kaya = ambil_materi_kaya(it)
        if it.get('tgl_pub') and not tgl:
            tgl = it['tgl_pub']
        bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + it['title'] + '\nIsi: ' + materi[:2000])
        semua_materi += ' ' + materi
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian TERKINI.\n')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTIP):\n' + dom['aturan'] + '\n\n'
            'Berikut beberapa materi teknologi domain ini:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita teknologi kaya:\n'
            '- TANGGAL KONKRET; DATELINE dari materi.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar tanpa manusia/hewan/alas kaki/ibadah.\n'
            '- Jangan sebut media sumber.')
    return ai_write(user, timeout=180, materi_sumber=semua_materi, kategori='teknologi')

def _espn_get(path):
    try:
        r = requests.get(ESPN_SITE + path, headers={'User-Agent': random.choice(UA_LIST)},
                         timeout=15)
        if not r.ok:
            return None
        return r.json()
    except Exception:
        return None

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
            main = None
            mn = None
            dr = None
            kl = None
            for stat in st.get('stats', []):
                tipe = stat.get('type') or stat.get('name') or ''
                val = stat.get('value')
                if tipe in ('rank', 'playoffSeed', 'position') and pos is None:
                    pos = val
                if (tipe == 'points' or tipe.lower() == 'points') and poin is None:
                    poin = val
                if tipe in ('gamesPlayed',) and main is None:
                    main = val
                if tipe in ('wins',) and mn is None:
                    mn = val
                if tipe in ('ties', 'draws') and dr is None:
                    dr = val
                if tipe in ('losses',) and kl is None:
                    kl = val
            tim = st.get('team', {}).get('displayName', '?')
            if pos is None:
                continue
            baris.append((
                int(pos), tim,
                int(main) if main is not None else 0,
                int(mn) if mn is not None else 0,
                int(dr) if dr is not None else 0,
                int(kl) if kl is not None else 0,
                int(poin) if poin is not None else 0
            ))
        if not baris:
            return '', ''
        baris.sort()
        teks = nama_liga + ': '
        teks += '; '.join(str(p) + '. ' + t + ' (' + str(pt) + ' poin)'
                          for p, t, _, _, _, _, pt in baris[:10])
        blok = '[KLASMEN]\n' + nama_liga + '\n'
        for p, t, main, mn, dr, kl, pt in baris:
            blok += str(p) + '|' + t + '|' + str(main) + '|' + str(mn) + '|' \
                    + str(dr) + '|' + str(kl) + '|' + str(pt) + '\n'
        blok += '[/KLASMEN]'
        return blok, teks
    except Exception:
        return '', ''

# AKHIR PART 3B

# PART 4A - KALENDER EVENT, RANGKUMAN, SESI OLAHRAGA CERDAS - V6.16.5

KALENDER_EVENT = [
    {'nama': 'Asian Games Aichi-Nagoya 2026',
     'mulai': '2026-09-19', 'selesai': '2026-10-04',
     'query': [
        ('klasmen medali asian games 2026', 'id'),
        ('perolehan medali indonesia asian games', 'id'),
        ('asian games 2026 hasil hari ini', 'id'),
        ('asian games nagoya medal tally', 'en'),
     ]},
    {'nama': 'Asian Para Games 2026',
     'mulai': '2026-10-18', 'selesai': '2026-10-25',
     'query': [
        ('klasmen medali asian para games', 'id'),
        ('indonesia medali asian para games', 'id'),
     ]},
    {'nama': 'SEA Games Thailand 2026',
     'mulai': '2026-12-09', 'selesai': '2026-12-20',
     'query': [
        ('klasmen medali sea games 2026', 'id'),
        ('indonesia medali sea games thailand', 'id'),
        ('sea games 2026 hasil', 'id'),
     ]},
    {'nama': 'ASEAN Para Games 2027',
     'mulai': '2027-01-20', 'selesai': '2027-01-27',
     'query': [
        ('klasmen medali asean para games', 'id'),
     ]},
    {'nama': 'Winter Olympics Milano-Cortina 2026',
     'mulai': '2027-02-06', 'selesai': '2027-02-22',
     'query': [
        ('winter olympics 2026 medal tally', 'en'),
        ('winter olympics hasil', 'id'),
     ]},
]

def event_besara_aktif():
    hari = datetime.now(WITA).date()
    aktif = []
    for ev in KALENDER_EVENT:
        try:
            mulai = datetime.strptime(ev['mulai'], '%Y-%m-%d').date()
            selesai = datetime.strptime(ev['selesai'], '%Y-%m-%d').date()
            if mulai <= hari <= selesai:
                aktif.append(ev)
        except Exception:
            continue
    return aktif

def buat_sumber_event(aktif):
    sumber = []
    for ev in aktif:
        for q, lang in ev['query']:
            sumber.append(GN(q, lang, 'GN Event: ' + ev['nama']))
    return sumber

ATURAN_KOMPETISI_WAJIB = (
    '- SYARAT WAJIB LAPORAN KOMPETISI (SANGAT PENTING):\n'
    '- WAJIB tulis SKOR AKHIR setiap pertandingan dengan ANGKA PERSIS.\n'
    '  Format: "Tim A 2 - 1 Tim B" atau "MU 2-1 Chelsea".\n'
    '- DILARANG menulis "berbagi angka", "menang tipis", "kalah dramatis"\n'
    '  TANPA menyebut angka skor.\n'
    '- WAJIB salin APA ADUNA blok [KLASMEN]...[/KLASMEN] di akhir isi\n'
    '  berita (kalau materi menyediakannya). Jangan diubah.\n'
    '- PERSEN: selalu simbol % - dilarang kata "persen".\n')

def _tulis_dari_kandidat(c, source_nama, breaking=False, kategori_target='olahraga'):
    try:
        judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(
            c, kategori_target=kategori_target)
        insert_news(judul, isi, ringkasan, 'olahraga', '',
                    c.get('link', ''), source_nama, 'published',
                    breaking=breaking, deskripsi_gambar=gambar)
        print('   TERBIT: ' + judul[:60])
        return 1
    except BeritaLama as bl:
        print('   Ditolak AI: ' + str(bl)[:60]); return 0
    except Exception as e:
        print('   Insert gagal: ' + str(e)[:80]); return 0

def _tulis_event_besar(cand, aktif, breaking=True):
    bagian = []
    for i, c in enumerate(cand[:8], 1):
        bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + c['title']
                      + '\nIsi: ' + c['summary'][:1200])
    nama_event = ' & '.join(e['nama'] for e in aktif)
    k = konteks_waktu()
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: '
            + k['kemarin'] + ')\n'
            'TUGAS KHUSUS: SATU berita EVENT BESAR BERLANGSUNG: '
            + nama_event + '.\n\n'
            'MATERI TERKINI:\n\n' + '\n\n'.join(bagian) + '\n\n'
            'ATURAN WAJIB EVENT BESAR:\n'
            '- WAJIB menampilkan KLASMEN MEDALI sementara (peringkat, '
            'emas/perak/perunggu) bila materi memuatnya - minimal 5 '
            'negara teratas + POSISI INDONESIA (atau negara yang '
            'dibahas).\n'
            '- WAJIB menampilkan HASIL/medali yang diraih hari ini '
            'bila materi memuatnya.\n'
            '- Angka medali/tanggal WAJIB persis dari materi; DILARANG '
            'mengarang.\n'
            '- Jika materi TIDAK memuat klasmen medali sama sekali, '
            'laporkan pencapaian terbaru atlet/event yang disebut.\n'
            '- Dateline: dari materi atau "INDONESIA - ".\n'
            '- Panjang: 300-500 kata.\n'
            '- Judul maks 10 kata: sebut nama event + kata kunci.\n'
            '- PERSEN: simbol %.\n'
            '- NAMA + JABATAN narasumber wajib lengkap.\n'
            '- deskripsi_gambar: tema stadion/medali/atletik 3-6 kata - '
            'TANPA hewan, manusia, alas kaki.\n'
            '- Jangan sebut media sumber.')
    print('   AI menulis rekap event besar (' + str(len(cand[:8]))
          + ' materi)...')
    try:
        judul, isi, ringkasan, waktu, gambar = ai_write(
            user, kategori='olahraga')
    except BeritaLama as bl:
        print('   Ditolak AI: ' + str(bl)[:60]); return 0
    except Exception as e:
        print('   ' + str(e)[:90]); return 0
    if sudah_serupa(judul):
        print('   Hasil AI dobel - skip.'); return 0
    try:
        insert_news(judul, isi, ringkasan, 'olahraga', '',
                    cand[0].get('link', ''), 'Event Besar Dunia',
                    'published', breaking=breaking,
                    deskripsi_gambar=gambar)
        print('   EVENT BESAR TERBIT: ' + judul[:60])
        return 1
    except Exception as e:
        print('   Insert gagal: ' + str(e)[:80])
        return 0

def olahraga_sudah_terbit_dengan_data(sumber='ESPN Data', jam=6):
    try:
        batas = (datetime.now(timezone.utc) - timedelta(hours=jam)).isoformat()
        rows = rest_get('?select=id&source_name=eq.' + quote_plus(sumber)
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

KATA_REGIONAL_OLAHRAGA = [
    'indonesia', 'timnas', 'pssi', 'liga 1', 'tarakan', 'kaltara',
    'asean', 'aff', 'sea games', 'asian games', 'olimpiade', 'olympic',
    'badminton', 'bulu tangkis', 'voli', 'volly', 'volleyball', 'bola voli',
    'basket', 'ibl', 'tenis', 'motogp', 'mandalika', 'f1', 'formula 1',
    'jepang', 'korea', 'thailand', 'malaysia', 'vietnam', 'singapura',
    'filipina', 'china', 'india', 'asia', 'piala dunia', 'fifa',
    'liga champions', 'uefa', 'eropa',
    'premier league', 'champions league', 'europa league', 'la liga',
    'serie a', 'bundesliga', 'ligue 1', 'eredivisie', 'world cup',
    'europe', 'european', 'singapore', 'philippines', 'japan',
    'nba',
]

SUMBER_RANGKUMAN_UMUM = [
    RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
    RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
    RSSF('https://www.bola.net/feed', 'Bola.net'),
    GN('badminton turnamen hasil hari ini', 'id', 'GN Event Badminton'),
    GN('voli nations league hasil', 'id', 'GN Event Voli'),
    GN('timnas indonesia laga hasil', 'id', 'GN Event Timnas'),
    GN('liga 1 indonesia hasil', 'id', 'GN Event Liga 1'),
    GN('motogp hasil balapan', 'id', 'GN Event MotoGP'),
    GN('tenis atp hasil turnamen', 'id', 'GN Event Tenis'),
    GN('basket ibl hasil', 'id', 'GN Event IBL'),
    GN('hasil liga champion', 'id', 'GN Hasil Liga Champions'),
    GN('hasil premier league', 'id', 'GN Hasil Premier League'),
    GN('hasil la liga serie a bundesliga', 'id', 'GN Hasil Liga Eropa'),
    GN('NBA news results', 'en', 'GN NBA Berita'),
]

def rangkuman_umum_sudah_terbit_hari_ini():
    try:
        now_wita = datetime.now(WITA)
        awal_hari = datetime(now_wita.year, now_wita.month, now_wita.day,
                             0, 0, 0, tzinfo=WITA)
        batas = awal_hari.astimezone(timezone.utc).isoformat()
        rows = rest_get('?select=id&source_name=eq.'
                        + quote_plus('Rangkuman Olahraga')
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

def sesi_rangkuman_umum(today_urls, seen):
    jam = datetime.now(WITA).hour
    if not (10 <= jam < 13):
        return 0
    print('\nRANGKUMAN OLAHRAGA UMUM TERJADWAL - jam ' + str(jam) + ':00 WITA')
    if rangkuman_umum_sudah_terbit_hari_ini():
        print('   Rangkuman umum sudah terbit HARI INI - skip.')
        return 0
    cand = collect_candidates(SUMBER_RANGKUMAN_UMUM, today_urls, seen,
                              max_umur_jam=30)
    if not cand:
        print('   Tidak ada kandidat olahraga segar - skip aman.')
        return 0
    regional = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'],
                                   KATA_REGIONAL_OLAHRAGA)]
    sebelum_tolak = len(regional)
    regional = [c for c in regional
                if not tolak_amerika_lokal(c['title'] + ' ' + c['summary'])]
    if sebelum_tolak != len(regional):
        print('   ' + str(sebelum_tolak - len(regional))
              + ' kandidat Amerika-lokal dibuang.')
    if not regional:
        print('   Tidak ada kandidat yang lolos filter regional - skip.')
        return 0
    groups = match_articles(regional)
    groups.sort(key=lambda g: -len(g['items']))
    dibuat = 0
    for g in groups:
        if dibuat >= 1:
            break
        items = g['items']
        top = items[0]
        if not adalah_konten_olahraga(top['title'] + ' ' + top.get('summary', '')):
            print('   Bukan konten olahraga: ' + top['title'][:50] + ' - skip.')
            continue
        if sudah_serupa(top['title']):
            continue
        print('\n   [rangkuman umum] menulis: ' + top['title'][:70]
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
                    'event/hasil/laporan sekaligus).\n\n'
                    + '\n\n'.join(bagian) + '\n\n'
                    'Gabungkan menjadi SATU berita rangkuman olahraga:\n'
                    '- Judul maks 10 kata mencerminkan rangkuman.\n'
                    '- WAJIB membahas SEMUA materi di atas.\n'
                    '- TANGGAL KONKRET; dateline dari materi atau "INDONESIA - ".\n'
                    '- Angka/skor WAJIB persis dari materi; dilarang mengarang.\n'
                    '- Panjang: 350-550 kata.\n'
                    '- PERSEN: selalu simbol %.\n'
                    '- NAMA + JABATAN narasumber wajib lengkap.\n'
                    '- deskripsi_gambar: 3-6 kata kunci dari elemen utama.\n'
                    '- Jangan sebut media sumber.')
            judul, isi, ringkasan, waktu, gambar = ai_write(
                user, kategori='olahraga')
        except BeritaLama as bl:
            print('   Ditolak AI: ' + str(bl)[:60])
            continue
        except Exception as e:
            print('   ' + str(e)[:90])
            continue
        if sudah_serupa(judul):
            print('   Hasil AI dobel - skip.')
            continue
        try:
            img_url = get_image(top.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            insert_news(judul, isi, ringkasan, 'olahraga', img_url,
                        top.get('link', ''), 'Rangkuman Olahraga',
                        'published', breaking=True, deskripsi_gambar=gambar)
            dibuat += 1
            print('   RANGKUMAN OLAHRAGA TERBIT: ' + judul[:60])
        except Exception as e:
            print('   Insert gagal: ' + str(e)[:80])
    return dibuat

def buat_materi_rangkuman_eropa():
    skor_semua = []
    klasemen_blok = []
    klasemen_teks = []
    for code, nama in ESPN_LIGA_TOP:
        skor_api = api_skor_football(code, hari_mundur=2)
        if skor_api:
            for s in skor_api:
                skor_semua.append(nama.split(' (')[0] + ': ' + s)
        else:
            for s in espn_skor_rentang(code, hari_mundur=2):
                skor_semua.append(nama.split(' (')[0] + ': ' + s)
        blok_api, teks_api = api_klasmen_football(code)
        if blok_api:
            klasemen_blok.append(blok_api)
            klasemen_teks.append(teks_api)
        else:
            blok_esp, teks_esp = espn_klasemen(code, nama)
            if blok_esp:
                klasemen_blok.append(blok_esp)
                klasemen_teks.append(teks_esp)
    if not skor_semua:
        return None
    bagian = []
    bagian.append('HASIL LAGA TERAKHIR LIGA TOP EROPA (ANGKA RESMI MESIN - '
                  'SALIN PERSIS):\n' + '\n'.join(skor_semua))
    if klasemen_teks:
        bagian.append('KLASMEN (ANGKA RESMI MESIN - WAJIB disalin ke blok '
                      '[KLASMEN]):\n' + '\n'.join(klasemen_teks[:4]))
    if klasemen_blok:
        bagian.append('BLOK KLASMEN SIAP-RENDER (WAJIB disalin APA ADUNA di '
                      'akhir isi berita, jangan diubah, jangan digandakan):\n'
                      + '\n\n'.join(klasemen_blok[:6]))
    return '\n\n'.join(bagian)

def buat_materi_rangkuman_nba():
    skor_semua = []
    for s in espn_skor_rentang('basketball/nba', hari_mundur=2):
        skor_semua.append('NBA: ' + s)
    if not skor_semua:
        return None
    blok, teks = espn_klasemen('basketball/nba', 'NBA')
    bagian = []
    bagian.append('HASIL LAGA NBA TERAKHIR (ANGKA RESMI MESIN - SALIN PERSIS):\n'
                  + '\n'.join(skor_semua))
    if teks:
        bagian.append('KLASMEN NBA (ANGKA RESMI MESIN - WAJIB disalin ke blok '
                      '[KLASMEN]):\n' + teks)
    if blok:
        bagian.append('BLOK KLASMEN SIAP-RENDER (WAJIB disalin APA ADUNA di '
                      'akhir isi berita, jangan diubah, jangan digandakan):\n'
                      + blok)
    return '\n\n'.join(bagian)

def _tulis_event_besar_dari_cand(today_urls, seen, aktif):
    sumber = buat_sumber_event(aktif)
    cand = collect_candidates(sumber, today_urls, seen, max_umur_jam=72)
    if not cand:
        print('   Tidak ada materi event segar.')
        return 0
    return _tulis_event_besar(cand, aktif, breaking=True)

def sesi_olahraga_api(jenis):
    now = datetime.now(WITA)
    jam = now.hour

    if jenis == 'eropa' and 7 <= jam < 12:
        print('\nOLAHRAGA ' + str(jam) + ':00 - LIGA TOP EROPA / EVENT BESAR / OLAHRAGA UMUM')
        if olahraga_sudah_terbit_dengan_data('ESPN Data'):
            print('   ESPN sudah terbit 6 jam terakhir - skip.')
            return 1

        print('   TAHAP 1: API Football Liga Top Eropa...')
        materi = buat_materi_rangkuman_eropa()
        if materi:
            k = konteks_waktu()
            user = (
                'TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: '
                + k['kemarin'] + ')\n'
                'TUGAS: LAPORAN HASIL LIGA TOP EROPA + KLASMEN SEMENTARA.\n'
                'GAYA: MINIM KATA.\n\n'
                + materi + '\n\n'
                'FORMAT WAJIB:\n'
                '1. Buka 1 kalimat: "Inilah hasil Liga Eropa dan klasmen sementara:"\n'
                '2. Daftar SKOR pertandingan.\n'
                '3. SALIN APA ADUNA semua blok [KLASMEN]...[/KLASMEN].\n'
                '4. DILARANG narasi bertele-tele.\n'
                '5. Dateline: "INDONESIA - ".\n'
                '6. Judul maks 10 kata: sebut "Hasil Liga Eropa".\n'
                '7. deskripsi_gambar: tema stadion/bola.\n'
                '8. Jangan sebut sumber data.')
            print('   AI menulis dari data API Football...')
            try:
                judul, isi, ringkasan, waktu, gambar = ai_write(
                    user, kategori='olahraga')
            except BeritaLama as bl:
                print('   Ditolak AI: ' + str(bl)[:60])
                materi = None
            except Exception as e:
                print('   ' + str(e)[:90])
                materi = None
            if materi:
                try:
                    insert_news(judul, isi, ringkasan, 'olahraga', '',
                                'https://www.api-football.com/ (data mesin)',
                                'ESPN Data', 'published', breaking=True,
                                deskripsi_gambar=gambar)
                    print('   TERBIT (API Football): ' + judul[:60])
                    return 1
                except Exception as e:
                    print('   Insert gagal: ' + str(e)[:80])

        print('   TAHAP 2: event besar aktif...')
        aktif = event_besara_aktif()
        if aktif:
            today_urls = get_today_state()
            seen = set()
            if _tulis_event_besar_dari_cand(today_urls, seen, aktif) == 1:
                return 1
        else:
            print('   Tidak ada event besar aktif.')

        print('   TAHAP 3: berita bola apa saja...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_BOLA = [
            GN('hasil pertandingan bola semalam', 'id', 'GN Hasil Bola'),
            GN('hasil premier league', 'id', 'GN Hasil Premier League'),
            GN('hasil liga champions', 'id', 'GN Hasil Liga Champions'),
            GN('berita bola terkini', 'id', 'GN Berita Bola'),
            GN('hasil la liga serie a', 'id', 'GN Hasil Liga Eropa'),
            GN('hasil bundesliga ligue 1', 'id', 'GN Hasil Liga Eropa 2'),
            GN('premier league news', 'en', 'GN Premier League'),
            GN('champions league news', 'en', 'GN Champions League'),
            GN('soccer match results', 'en', 'GN Soccer'),
            RSSF('https://www.bola.net/feed', 'Bola.net'),
            RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
            RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        ]
        cand = collect_candidates(SUMBER_BOLA, today_urls, seen, max_umur_jam=30)
        bola = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'],
                                   ['bola', 'liga', 'sepak', 'football',
                                    'soccer', 'premier', 'champions',
                                    'bundesliga', 'serie a', 'la liga'])]
        if bola:
            hasil = _tulis_dari_kandidat(bola[0], 'Olahraga Pagi',
                                         breaking=False)
            if hasil == 1:
                return 1

        print('   TAHAP 4: olahraga umum (fallback terakhir)...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_OLGA_UMUM = [
            GN('berita olahraga terkini', 'id', 'GN Olahraga'),
            GN('hasil pertandingan hari ini', 'id', 'GN Hasil Hari Ini'),
            GN('timnas indonesia', 'id', 'GN Timnas'),
            GN('badminton hasil', 'id', 'GN Badminton'),
            GN('motogp hasil', 'id', 'GN MotoGP'),
            GN('voli hasil', 'id', 'GN Voli'),
            GN('tenis hasil', 'id', 'GN Tenis'),
            GN('basket hasil', 'id', 'GN Basket'),
            RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
            RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
            RSSF('https://www.bola.net/feed', 'Bola.net'),
        ]
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30)
        # V6.16.5: WAJIB konten olahraga (ketat, 2 lapis)
        cand = [c for c in cand
                if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand
                if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Pagi',
                                         breaking=False)
            if hasil == 1:
                return 1

        print('   Tidak ada berita olahraga apa pun - skip.')
        return 0

    if jenis == 'nba' and 13 <= jam < 17:
        print('\nOLAHRAGA ' + str(jam) + ':00 - NBA/WNBA')
        if olahraga_sudah_terbit_dengan_data('ESPN Data NBA'):
            print('   ESPN NBA sudah terbit 6 jam terakhir - skip.')
            return 1

        print('   TAHAP 1: NBA...')
        materi = buat_materi_rangkuman_nba()
        if materi:
            k = konteks_waktu()
            user = (
                'TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: '
                + k['kemarin'] + ')\n'
                'TUGAS: LAPORAN HASIL NBA + KLASMEN SEMENTARA.\n'
                'GAYA: MINIM KATA.\n\n'
                + materi + '\n\n' + ATURAN_KOMPETISI_WAJIB +
                'FORMAT WAJIB:\n'
                '1. Buka 1 kalimat: "Inilah hasil NBA dan klasmen sementara:"\n'
                '2. Daftar SKOR pertandingan.\n'
                '3. SALIN APA ADUNA blok [KLASMEN]...[/KLASMEN].\n'
                '4. Dateline: "INDONESIA - ".\n'
                '5. Judul maks 10 kata.\n'
                '6. deskripsi_gambar: tema bola basket.\n'
                '7. Jangan sebut sumber data.')
            print('   AI menulis dari data NBA...')
            try:
                judul, isi, ringkasan, waktu, gambar = ai_write(
                    user, kategori='olahraga')
            except BeritaLama as bl:
                print('   Ditolak AI: ' + str(bl)[:60])
                materi = None
            except Exception as e:
                print('   ' + str(e)[:90])
                materi = None
            if materi:
                try:
                    insert_news(judul, isi, ringkasan, 'olahraga', '',
                                'https://www.espn.com/nba/ (data mesin nba)',
                                'ESPN Data NBA', 'published', breaking=True,
                                deskripsi_gambar=gambar)
                    print('   TERBIT (NBA): ' + judul[:60])
                    return 1
                except Exception as e:
                    print('   Insert gagal: ' + str(e)[:80])

        print('   TAHAP 2: berita NBA/WNBA...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_NBA = [
            GN('NBA scores results', 'en', 'GN NBA Hasil'),
            GN('NBA standings', 'en', 'GN NBA Klasmen'),
            GN('WNBA scores results', 'en', 'GN WNBA Hasil'),
            GN('NBA news', 'en', 'GN NBA Berita'),
            GN('berita NBA', 'id', 'GN NBA Berita ID'),
        ]
        cand = collect_candidates(SUMBER_NBA, today_urls, seen, max_umur_jam=30)
        cand = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'],
                                   ['nba', 'wnba'])]
        # V6.16.5: WAJIB konten olahraga (ketat)
        cand = [c for c in cand
                if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Rangkuman NBA',
                                         breaking=False)
            if hasil == 1:
                return 1

        print('   TAHAP 3: olahraga umum (fallback)...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_OLGA_UMUM = [
            GN('berita olahraga terkini', 'id', 'GN Olahraga'),
            GN('hasil pertandingan hari ini', 'id', 'GN Hasil Hari Ini'),
            RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
            RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        ]
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30)
        # V6.16.5: WAJIB konten olahraga + TOLAK berita politik/hukum
        cand = [c for c in cand
                if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand
                if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Siang',
                                         breaking=False)
            if hasil == 1:
                return 1

        print('   Tidak ada berita olahraga - skip.')
        return 0

    return 0

# AKHIR PART 4A

# PART 4B - SESI BREAKING, PASAR MODAL, SESI KATEGORI, RUN SESSION - V6.16.5

def is_berita_politik_hukum(teks):
    """V6.16.5: cek apakah berita ini politik/hukum/korupsi (bukan olahraga).
    Dipakai untuk TOLAK fallback olahraga yang salah kategori."""
    t = (teks or '').lower()
    KATA_POLITIK_HUKUM = [
        'tersangka', 'korupsi', 'kpk', 'kejaksaan', 'pengadilan',
        'sidang', 'dakwaan', 'hukuman', 'pidana', 'penjara', 'ditahan',
        'dpr', 'presiden', 'menteri', 'gubernur', 'walikota', 'bupati',
        'pileg', 'pilpres', 'pilkada', 'partai', 'kampanye',
        'demonstrasi', 'unjuk rasa', 'kerusuhan',
    ]
    for k in KATA_POLITIK_HUKUM:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            return True
    return False

def sesi_breaking(today_urls, seen):
    made = 0
    slots = BREAKING_MAX_SLOT - len(get_breaking_list())
    print('\nBREAKING - slot tersedia: ' + str(slots) + '/' + str(BREAKING_MAX_SLOT))
    if slots <= 0:
        return 0
    cand_dom = collect_candidates(BREAKING_DOMESTIK_FEEDS, today_urls, seen,
                                  max_umur_jam=30)
    skor_dom = sorted([(c, skor_domestik(c['title'], c['summary'])) for c in cand_dom],
                      key=lambda x: -x[1])
    skor_dom = [x for x in skor_dom if x[1] >= SKOR_BREAKING_MIN]
    print('   Kandidat breaking domestik layak: ' + str(len(skor_dom)))
    cand_dun = collect_candidates(BREAKING_DUNIA_FEEDS, today_urls, seen,
                                  max_umur_jam=30)
    skor_dun = sorted([(c, skor_dunia(c['title'], c['summary'])) for c in cand_dun],
                      key=lambda x: -x[1])
    skor_dun = [x for x in skor_dun if x[1] >= SKOR_BREAKING_MIN]
    print('   Kandidat breaking dunia layak: ' + str(len(skor_dun)))
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
            print('   Skip (dobel): ' + c['title'][:50])
            continue
        print('\n   ' + label + ': ' + c['title'][:70])
        try:
            judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(
                c, kategori_target='nasional' if tip == 'dom' else 'internasional')
        except BeritaLama as bl:
            print('   Ditolak AI: ' + str(bl)[:60]); continue
        except Exception as e:
            print('   ' + str(e)[:90]); continue
        if sudah_serupa(judul):
            print('   Hasil AI mirip judul yang sudah ada - skip.')
            continue
        if len(get_breaking_list()) >= BREAKING_MAX_SLOT:
            print('   Slot breaking penuh - stop.')
            break
        try:
            img_url = get_image(c.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            insert_news(judul, isi, ringkasan, kategori_breaking(c, tip),
                        img_url, c.get('link', ''), c.get('source', 'Breaking'),
                        'published', breaking=True, deskripsi_gambar=gambar)
            made += 1
            print('   BREAKING TERBIT: ' + judul[:60])
        except Exception as e:
            print('   Insert gagal: ' + str(e)[:80])
    return made

def kategori_breaking(c, tip):
    if tip == 'dun':
        return 'internasional'
    t = (c.get('title', '') + ' ' + c.get('summary', '')).lower()
    if any(w in t for w in LUAR_NEGERI_WORDS):
        return 'internasional'
    return 'nasional'

def _pasar_modal_sesi():
    now = datetime.now(WITA)
    if now.weekday() >= 5:
        return None
    jam = now.hour
    if not (12 <= jam < 18):
        return None
    if jam < 16:
        return 'Tengah'
    return 'Penutupan'

def pasar_modal_sudah_terbit(sesi):
    try:
        now_wita = datetime.now(WITA)
        awal_hari_wita = datetime(now_wita.year, now_wita.month, now_wita.day,
                                  0, 0, 0, tzinfo=WITA)
        batas = awal_hari_wita.astimezone(timezone.utc).isoformat()
        sumber = 'Pasar Modal ' + str(sesi)
        rows = rest_get('?select=id&source_name=eq.' + quote_plus(sumber)
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

def _ambil_harga_yahoo(simbol):
    try:
        url = ('https://query1.finance.yahoo.com/v8/finance/chart/'
               + quote_plus(simbol) + '?interval=1d&range=1d')
        r = requests.get(url, headers={'User-Agent': random.choice(UA_LIST)}, timeout=15)
        if not r.ok:
            return None
        data = r.json()
        hasil = data.get('chart', {}).get('result', [])
        if not hasil:
            return None
        meta = hasil[0].get('meta', {})
        harga = meta.get('regularMarketPrice')
        sebelum = meta.get('chartPreviousClose') or meta.get('previousClose')
        if harga is None:
            return None
        perubahan = None
        if sebelum and sebelum != 0:
            perubahan = (harga - sebelum) / sebelum * 100
        return {'harga': harga, 'perubahan': perubahan}
    except Exception:
        return None

def _ambil_kurs_usdidr():
    d = _ambil_harga_yahoo('USDIDR=X')
    if d and d.get('harga'):
        return d
    d = _ambil_harga_yahoo('IDR=X')
    if d and d.get('harga'):
        return d
    try:
        r = requests.get('https://open.er-api.com/v6/latest/USD',
                         headers={'User-Agent': random.choice(UA_LIST)}, timeout=15)
        if r.ok:
            data = r.json()
            idr = (data.get('rates') or {}).get('IDR')
            if idr:
                return {'harga': float(idr), 'perubahan': None}
    except Exception:
        pass
    return None

def _format_harga_yahoo(simbol, nama, prefix='', suffix=''):
    d = _ambil_harga_yahoo(simbol)
    if not d:
        return None
    harga = d['harga']
    if harga is None:
        return None
    if harga >= 1000:
        s = prefix + format(int(round(harga)), ',').replace(',', '.') + suffix
    else:
        s = prefix + format(harga, '.2f').replace('.', ',') + suffix
    if d['perubahan'] is not None:
        tanda = '+' if d['perubahan'] >= 0 else ''
        s += ' (' + tanda + format(d['perubahan'], '.2f').replace('.', ',') + '%)'
    return s

def _format_kurs_usdidr():
    d = _ambil_kurs_usdidr()
    if not d or not d.get('harga'):
        return None
    s = 'Rp ' + format(int(round(d['harga'])), ',').replace(',', '.')
    if d.get('perubahan') is not None:
        tanda = '+' if d['perubahan'] >= 0 else ''
        s += ' (' + tanda + format(d['perubahan'], '.2f').replace('.', ',') + '%)'
    return s

def sesi_pasar_modal(today_urls, seen):
    sesi = _pasar_modal_sesi()
    if not sesi:
        return 0
    jam = datetime.now(WITA).hour
    print('\nPASAR MODAL TERJADWAL - sesi ' + sesi + ' (jam ' + str(jam) + ':00 WITA)')
    if pasar_modal_sudah_terbit(sesi):
        print('   Pasar modal sesi ' + sesi + ' sudah terbit hari ini - skip.')
        return 0

    baris = []
    s = _format_harga_yahoo('^JKSE', 'IHSG', '', '')
    if s:
        baris.append('- IHSG: ' + s)
    s = _format_kurs_usdidr()
    if s:
        baris.append('- Kurs USD/IDR: ' + s)
    s = _format_harga_yahoo('CL=F', 'Minyak WTI', '$', '/barel')
    if s:
        baris.append('- Minyak WTI: ' + s)
    s = _format_harga_yahoo('BZ=F', 'Minyak Brent', '$', '/barel')
    if s:
        baris.append('- Minyak Brent: ' + s)
    s = _format_harga_yahoo('TIO=F', 'Biji Besi (Iron Ore)', '$', '/ton')
    if s:
        baris.append('- Biji Besi (Iron Ore): ' + s)

    if not baris:
        print('   Semua data harga kosong - skip.')
        return 0

    tanggal = datetime.now(WITA).strftime('%d %B %Y')
    jam_str = datetime.now(WITA).strftime('%H:%M')
    k = konteks_waktu()
    kata_sesi = 'sesi tengah hari' if sesi == 'Tengah' else 'penutupan'
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            'TUGAS: Tulis SATU berita laporan pasar keuangan ' + kata_sesi + ' '
            'dari data berikut:\n\n'
            + '\n'.join(baris) + '\n\n'
            'Aturan:\n'
            '- Judul maks 10 kata: sebut IHSG + arah pergerakan atau ringkas pasar.\n'
            '- Dateline: "JAKARTA, DKI JAKARTA - ".\n'
            '- Panjang: 200-350 kata (4-6 paragraf).\n'
            '- Sajikan data dalam bentuk laporan naratif ringkas, bukan sekadar daftar.\n'
            '- DILARANG mengarang angka di luar data di atas.\n'
            '- DILARANG menebak sebab-akibat pergerakan (cukup laporkan angka).\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: tema city skyline/gedung bursa.\n'
            '- Akhiri dengan kalimat: "Data dihimpun KramaNews dari perdagangan '
            'terakhir ' + jam_str + ' WITA, ' + tanggal + '."')
    print('   AI menulis laporan pasar modal (' + sesi + ')...')
    try:
        judul, isi, ringkasan, waktu, gambar = ai_write(user, kategori='ekonomi')
    except BeritaLama as bl:
        print('   Ditolak AI: ' + str(bl)[:60]); return 0
    except Exception as e:
        print('   ' + str(e)[:90]); return 0
    if sudah_serupa(judul):
        print('   Hasil AI dobel - skip.')
        return 0
    try:
        insert_news(judul, isi, ringkasan, 'ekonomi', '',
                    'https://finance.yahoo.com/', 'Pasar Modal ' + sesi,
                    'published', breaking=True, deskripsi_gambar=gambar)
        print('   PASAR MODAL TERBIT (' + sesi + '): ' + judul[:60])
        return 1
    except Exception as e:
        print('   Insert pasar modal gagal: ' + str(e)[:80])
        return 0


KATEGORI_DB = {
    'nasional': 'nasional', 'daerah': 'daerah',
    'internasional_asean': 'internasional', 'internasional_tt': 'internasional',
    'internasional': 'internasional',
    'ekonomi': 'ekonomi', 'olahraga': 'olahraga', 'teknologi': 'teknologi',
    'otomotif': 'otomotif', 'kesehatan': 'kesehatan',
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
        print('   Gagal hitung Kaltara: ' + str(e)[:60])
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
        print('   Gagal hitung topik wajib: ' + str(e)[:60])
    return n

def kelompok_kaltara(items):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return any(w in teks for w in KALTARA_WORDS)

def kelompok_topik(items, kata_list):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return teks_mengandung(teks, kata_list)

def kelompok_regional_olahraga(items):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '')
                    for it in items).lower()
    return teks_mengandung(teks, KATA_REGIONAL_OLAHRAGA)

def tolak_amerika_lokal(teks):
    t = (teks or '').lower()
    KATA_OLAHRAGA_TOLAK = [
        'nfl', 'mlb', 'nhl', 'wnba', 'mls', 'ncaa', 'cfb', 'super bowl',
        'world series', 'stanley cup',
        'seahawks', 'patriots', 'cowboys', 'packers', 'chiefs', '49ers',
        'bills', 'dolphins', 'eagles', 'ravens', 'bengals',
        'yankees', 'dodgers', 'red sox', 'mets', 'cubs', 'astros',
        'bruins', 'maple leafs', 'penguins',
        'lakers', 'celtics', 'warriors', 'knicks', 'bulls nba',
        'heat nba', 'suns nba', 'mavericks', 'nuggets nba',
        'bucks nba', 'sixers', 'spurs nba', 'raptors nba',
        'college football', 'college basketball', 'march madness',
        'northwestern', 'indiana hoosiers', 'south dakota',
        'big ten', 'sec football', 'pac-12',
    ]
    for k in KATA_OLAHRAGA_TOLAK:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            return True
    return False

def produksi_satu(cat, today_urls, seen, utamakan_kaltara, utamakan_topik=None,
                  sumber_custom=None, domain_tek=None, wajib_regional=False,
                  sumber_fallback=None):
    max_umur = max_umur_kategori(cat)
    cand = collect_candidates(sumber_custom if sumber_custom else HUNT.get(cat, []),
                              today_urls, seen, max_umur_jam=max_umur)
    if not cand:
        print('   (' + cat + ') Tidak ada kandidat segar.')
        return False
    if cat == 'internasional_tt':
        cand = [c for c in cand
                if teks_mengandung(c['title'] + ' ' + c['summary'], KATA_TT)]
        if not cand:
            print('   (tt) Tidak ada kandidat Timur Tengah segar.')
            return False
    if cat in ('internasional', 'internasional_asean', 'internasional_tt'):
        sebelum = len(cand)
        cand = [c for c in cand
                if not adalah_turnamen_olahraga(c['title'] + ' ' + c['summary'])]
        if sebelum != len(cand):
            print('   (' + cat + ') ' + str(sebelum - len(cand))
                  + ' kandidat turnamen olahraga dibuang (ke olahraga).')
        sebelum2 = len(cand)
        cand = [c for c in cand
                if not adalah_konten_otomotif(c['title'] + ' ' + c['summary'])]
        if sebelum2 != len(cand):
            print('   (' + cat + ') ' + str(sebelum2 - len(cand))
                  + ' kandidat otomotif dibuang (ke otomotif).')
    if cat == 'teknologi':
        sebelum = len(cand)
        cand = [c for c in cand
                if not adalah_konten_otomotif(c['title'] + ' ' + c['summary'])]
        if sebelum != len(cand):
            print('   (' + cat + ') ' + str(sebelum - len(cand))
                  + ' kandidat otomotif dibuang (ke otomotif).')
    if wajib_regional and cat == 'olahraga':
        n_reg = sum(1 for c in cand
                    if teks_mengandung(c['title'] + ' ' + c['summary'],
                                       KATA_REGIONAL_OLAHRAGA))
        print('   (' + cat + ') Kandidat regional: ' + str(n_reg) + '/' + str(len(cand))
              + ' (diprioritaskan, tidak wajib).')
    if cat == 'olahraga':
        sebelum_tolak = len(cand)
        cand = [c for c in cand
                if not tolak_amerika_lokal(c['title'] + ' ' + c['summary'])]
        if sebelum_tolak != len(cand):
            print('   (' + cat + ') ' + str(sebelum_tolak - len(cand))
                  + ' kandidat Amerika-lokal dibuang.')
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
    if wajib_regional and cat == 'olahraga':
        groups.sort(key=lambda g: 0 if kelompok_regional_olahraga(g['items']) else 1)
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
        if percobaan >= 2:
            break
        items = g['items']
        top = items[0]
        if cek_bukan_berita(top['title'], top.get('summary', '')):
            print('   Bukan berita (zodiak/dsb): ' + top['title'][:50] + ' - skip.')
            continue
        if cat in ('internasional_asean', 'internasional_tt', 'internasional'):
            b = kategori_barat(top['title'], top.get('summary', ''))
            if b and barat_sudah_terbit(b):
                continue
        if sudah_serupa(top['title']):
            continue
        percobaan += 1
        print('\n   [' + cat + '] menulis: ' + top['title'][:70])
        try:
            if domain_tek:
                if len(items) > 1:
                    judul, isi, ringkasan, waktu, gambar = ai_rewrite_teknologi_multi(items, domain_tek)
                else:
                    judul, isi, ringkasan, waktu, gambar = ai_rewrite_teknologi_single(top, domain_tek)
            elif len(items) > 1:
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_multi(
                    items, kategori_target=cat)
            else:
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(
                    top, kategori_target=cat)
        except BeritaLama as bl:
            print('   Ditolak AI: ' + str(bl)[:60]); continue
        except Exception as e:
            print('   ' + str(e)[:90]); continue
        if sudah_serupa(judul):
            print('   Hasil AI dobel dengan judul yang sudah ada - skip.')
            continue
        try:
            img_url = get_image(top.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            src_nama = sumber_fallback if sumber_fallback else top.get('source', '')
            insert_news(judul, isi, ringkasan, KATEGORI_DB.get(cat, cat), img_url,
                        top.get('link', ''), src_nama,
                        'published', deskripsi_gambar=gambar)
            print('   Terbit: ' + judul[:60])
            return True
        except Exception as e:
            print('   Insert gagal: ' + str(e)[:80])
            continue
    return False

def sesi_otomotif(today_urls, seen):
    jam = datetime.now(WITA).hour
    if jam not in JAM_OTOMOTIF:
        return 0
    dom, sumber_oto = sumber_otomotif_hari_ini(jam)
    if not dom:
        return 0
    print('\nOTOMOTIF - jam ' + str(jam) + ':00 WITA - domain: ' + dom['nama'])
    if produksi_satu('otomotif', today_urls, seen, False, None,
                     sumber_custom=sumber_oto,
                     sumber_fallback='Otomotif: ' + dom['nama']):
        return 1
    return 0

def sesi_kategori(today_urls, seen):
    jam = datetime.now(WITA).hour
    kuota = JADWAL_JAM.get(jam)
    if not kuota:
        print('\nKATEGORI - jam ' + str(jam) + ':00 WITA di luar jadwal produksi. Lewat.')
        return 0
    print('\nKATEGORI - jam ' + str(jam) + ':00 WITA - kuota: ' +
          ', '.join(k + '=' + str(v) for k, v in kuota.items()))
    utamakan_kaltara = False
    if kuota.get('daerah'):
        utamakan_kaltara = hitung_kaltara_hari_ini() < 2
        if utamakan_kaltara:
            print('   Kuota Kaltara hari ini belum capai 2 - kandidat Kaltara didahulukan.')
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
            print('   Topik wajib nasional belum terpenuhi: ' + ' & '.join(nama)
                  + ' - kandidatnya didahulukan.')
    sumber_kesehatan = None
    if kuota.get('kesehatan'):
        dom_kes, sumber_kesehatan = sumber_kesehatan_hari_ini(jam)
        if not dom_kes:
            sumber_kesehatan = None
    sumber_teknologi = None
    dom_tek = None
    if kuota.get('teknologi'):
        dom_tek, sumber_teknologi = sumber_teknologi_hari_ini(jam)
        if not dom_tek:
            sumber_teknologi = None
    sumber_oto = None
    dom_oto = None
    if kuota.get('otomotif'):
        dom_oto, sumber_oto = sumber_otomotif_hari_ini(jam)
        if not dom_oto:
            sumber_oto = None
    pasar_modal_skip = False
    if kuota.get('ekonomi') and datetime.now(WITA).weekday() < 5:
        if pasar_modal_sudah_terbit('Tengah') or pasar_modal_sudah_terbit('Penutupan'):
            print('   Kategori ekonomi dilewati - pasar modal sudah terbit hari ini.')
            pasar_modal_skip = True
    total = 0
    for cat, n in kuota.items():
        if cat == 'ekonomi' and pasar_modal_skip:
            continue
        prio = utamakan_topik if cat == 'nasional' else None
        sumber = None
        domain_tek = None
        wajib_regional = False
        sumber_fallback = None
        if cat == 'kesehatan':
            sumber = sumber_kesehatan
        elif cat == 'teknologi':
            sumber = sumber_teknologi
            domain_tek = dom_tek
        elif cat == 'otomotif':
            sumber = sumber_oto
            if dom_oto:
                sumber_fallback = 'Otomotif: ' + dom_oto['nama']
        elif cat == 'olahraga':
            wajib_regional = True
            if olahraga_sudah_terbit_dengan_data('Event Besar Dunia') and jam in (11, 17):
                print('   Event Besar Dunia sudah terbit - slot dilewati.')
                continue
            if jam == 7 and olahraga_sudah_terbit_dengan_data('ESPN Data'):
                print('   ESPN sudah terbit - skip (anti-dobel).')
                continue
            if jam == 11 and olahraga_sudah_terbit_dengan_data('Rangkuman Olahraga'):
                print('   Rangkuman Umum sudah terbit - skip (anti-dobel).')
                continue
            if jam == 13 and olahraga_sudah_terbit_dengan_data('ESPN Data NBA'):
                print('   ESPN NBA sudah terbit - skip (anti-dobel).')
                continue
            if 7 <= jam < 12:
                if sesi_olahraga_api('eropa') == 1:
                    total += 1
                continue
            if 13 <= jam < 17:
                if sesi_olahraga_api('nba') == 1:
                    total += 1
                continue
            if jam in (11, 17):
                aktif = event_besara_aktif()
                if aktif:
                    print('   EVENT BESAR AKTIF: '
                          + ' & '.join(e['nama'] for e in aktif)
                          + ' - diprioritaskan.')
                    if _tulis_event_besar_dari_cand(
                            today_urls, seen, aktif) == 1:
                        total += 1
                        continue
                for _ in range(n):
                    if produksi_satu(cat, today_urls, seen,
                                     utamakan_kaltara and cat == 'daerah',
                                     prio, sumber, domain_tek, wajib_regional,
                                     sumber_fallback):
                        total += 1
                continue
        for _ in range(n):
            if produksi_satu(cat, today_urls, seen,
                             utamakan_kaltara and cat == 'daerah',
                             prio, sumber, domain_tek, wajib_regional,
                             sumber_fallback):
                total += 1
    return total

def run_session():
    now = datetime.now(WITA)
    print('\n==========================================')
    print('SESI BERBURU - ' + now.strftime('%d/%m/%Y %H:%M') + ' WITA (V6.16.5)')
    print('==========================================')
    dicabut = expire_breaking(BREAKING_UMUR_MENIT)
    if dicabut:
        print('   (' + str(dicabut) + ' breaking tua dicabut otomatis)')
    today_urls = get_today_state()
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   ' + str(len(JUDUL_TERPAKAI)) + ' judul 36 jam terakhir dimuat (anti-dobel).')
    print('   ' + str(len(JUDUL_6JAM)) + ' judul 6 jam terakhir dimuat (anti-dobel-6jam).')
    print('   ' + str(len(muat_gambar_terpakai())) + ' gambar 36 jam terakhir terdaftar.')
    seen = set()
    n_umum = sesi_rangkuman_umum(today_urls, seen)
    n_brk = sesi_breaking(today_urls, seen)
    n_kat = sesi_kategori(today_urls, seen)
    n_idx = sesi_pasar_modal(today_urls, seen)
    total_scrape = STAT_SCRAPE['ok'] + STAT_SCRAPE['gagal']
    if total_scrape:
        persen = int(STAT_SCRAPE['ok'] * 100 / total_scrape)
        print('\nStatistik scraping: ' + str(STAT_SCRAPE['ok']) + ' sukses / '
              + str(total_scrape) + ' artikel (' + str(persen) + '%) - gagal '
              + str(STAT_SCRAPE['gagal']) + ' - skip ' + str(STAT_SCRAPE['skip']))
    else:
        print('\nStatistik scraping: tidak ada percobaan scraping sesi ini.')
    print('Sesi selesai - breaking: ' + str(n_brk) + ' - kategori: ' + str(n_kat)
          + ' - PasarModal: ' + str(n_idx) + ' - RangkumanUmum: ' + str(n_umum))
    return n_brk + n_kat + n_idx + n_umum

def main_sekali():
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('Kunci belum lengkap! Cek Secrets GitHub: DEEPSEEK_KEY, SUPABASE_PUBLISHABLE')
        return
    if not ADMIN_SECRET:
        print('ADMIN_OPS_SECRET belum ada di Secrets GitHub!')
        return
    print('Kunci gerbang admin-ops: OK')
    print('API Football key: ' + ('OK' if FOOTBALL_API_KEY else 'KOSONG (fallback ke ESPN)'))
    run_session()

def main():
    print('AI WARTAWAN KRAMANEWS V6.16.5 - mode loop 30 menit (Ctrl+C untuk berhenti)')
    while True:
        try:
            main_sekali()
        except Exception as e:
            print('Sesi gagal total: ' + str(e)[:100])
        time.sleep(1800)

if __name__ == '__main__':
    if '--sekali' in sys.argv:
        main_sekali()
    else:
        main()

FILE_VERSI      = 'V6.16.5'
FILE_PART_AKHIR = 'PART 4B'

# AKHIR PART 4B