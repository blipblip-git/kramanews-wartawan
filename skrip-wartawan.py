# PART 1 - KONFIGURASI, JADWAL & SUMBER

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

SUPABASE_URL = 'https://imcvijgytdjjpotlaltv.supabase.co'
REST_URL     = SUPABASE_URL + '/rest/v1/articles'
EDGE_URL     = SUPABASE_URL + '/functions/v1/admin-ops'
AUTHOR_NAME  = 'DT'

WITA = timezone(timedelta(hours=8))

BREAKING_MAX_SLOT       = 2
BREAKING_UMUR_MENIT     = 30
MAX_UMUR_BERITA_JAM     = 30
JENDELA_DOBEL_JAM       = 72
GEMPA_DOM_MIN           = 5.5
GEMPA_DUNIA_MIN         = 6.5
SKOR_BREAKING_MIN       = 15
SKOR_BREAKING_MIN_DOM   = 15
AMBANG_MIRIP            = 0.55
SCRAPER_TIMEOUT         = 12
SCRAPE_MIN_KARAKTER     = 600
MATERI_MIN_KARAKTER     = 700
JINA_READER             = 'https://r.jina.ai/'
GAMBAR_MIN_LEBAR        = 400
BLUR_SKOR_MINIMUM       = 5
VISION_TIMEOUT          = 30
MATCH_MIN_KATA          = 2
MATCH_MIN_RASIO         = 0.50
DOMAIN_SKIP_SCRAPE      = ['berita.tarakankota.go.id', 'vnexpress.net']

DOBEL_6JAM_MIN_KATA     = 3
DOBEL_6JAM_BUTUH_NAMA   = True

GOOGLE_NEWS_HOST        = 'news.google.com'
GOOGLE_NEWS_DECODE_MIN  = 5
GOOGLE_NEWS_BATCH_MAX   = 10
GN_DECODE_TIMEOUT       = 15

KAMUS_PROVINSI_IBUKOTA = {
    'aceh': 'banda aceh',
    'sumatera utara': 'medan', 'sumut': 'medan',
    'sumatera barat': 'padang', 'sumbar': 'padang',
    'riau': 'pekanbaru',
    'kepulauan riau': 'tanjung pinang', 'kepri': 'tanjung pinang',
    'jambi': 'jambi',
    'bengkulu': 'bengkulu',
    'sumatera selatan': 'palembang', 'sumsel': 'palembang',
    'bangka belitung': 'pangkal pinang', 'babel': 'pangkal pinang',
    'lampung': 'bandar lampung',
    'dki jakarta': 'jakarta', 'jakarta': 'jakarta',
    'jawa barat': 'bandung', 'jabar': 'bandung',
    'jawa tengah': 'semarang', 'jateng': 'semarang',
    'di yogyakarta': 'yogyakarta', 'yogyakarta': 'yogyakarta', 'diy': 'yogyakarta',
    'jawa timur': 'surabaya', 'jatim': 'surabaya',
    'banten': 'serang',
    'bali': 'denpasar',
    'nusa tenggara barat': 'mataram', 'ntb': 'mataram',
    'nusa tenggara timur': 'kupang', 'ntt': 'kupang',
    'kalimantan barat': 'pontianak', 'kalbar': 'pontianak',
    'kalimantan tengah': 'palangka raya', 'kalteng': 'palangka raya',
    'kalimantan selatan': 'banjarmasin', 'kalsel': 'banjarmasin',
    'kalimantan timur': 'samarinda', 'kaltim': 'samarinda',
    'kalimantan utara': 'tarakan', 'kaltara': 'tarakan',
    'sulawesi utara': 'manado', 'sulut': 'manado',
    'sulawesi tengah': 'palu', 'sulteng': 'palu',
    'sulawesi selatan': 'makassar', 'sulsel': 'makassar',
    'sulawesi tenggara': 'kendari', 'sultra': 'kendari',
    'gorontalo': 'gorontalo',
    'sulawesi barat': 'mamuju', 'sulbar': 'mamuju',
    'maluku': 'ambon',
    'maluku utara': 'sofifi', 'malut': 'sofifi',
    'papua': 'jayapura',
    'papua barat': 'manokwari',
    'papua barat daya': 'sorong',
    'papua selatan': 'merauke',
    'papua tengah': 'nabire',
    'papua pegunungan': 'jayawijaya',
}

UMUR_BERITA_PER_KATEGORI = {
    'nasional': 30, 'daerah': 30, 'internasional_asean': 30,
    'internasional_tt': 30, 'internasional': 30, 'olahraga': 30,
    'ekonomi': 48, 'teknologi': 72,
    'kesehatan': 180 * 24, 'otomotif': 180 * 24,
}

KATEGORI_EVERGREEN = ['kesehatan', 'otomotif']

KATA_BARAT_USA   = ['amerika', 'u.s', 'washington', 'trump', 'biden', 'new york', 'california', 'texas']
KATA_BARAT_RUSIA = ['rusia', 'russia', 'moskow', 'moscow', 'putin', 'ukraina', 'ukraine']
KATA_BARAT_EROPA = ['eropa', 'europe', 'jerman', 'germany', 'perancis', 'france', 'inggris',
                    'britain', 'italia', 'italy', 'spanyol', 'spain', 'paris', 'berlin', 'london']
KATA_TT          = ['timur tengah', 'middle east', 'gaza', 'israel', 'palestina', 'iran',
                    'iraq', 'suriah', 'syria', 'saudi', 'yaman', 'yemen', 'uni emirat',
                    'emirates', 'qatar', 'kuwait', 'libanon', 'jordan', 'turki']
KATA_ASEAN       = ['asean', 'malaysia', 'thailand', 'vietnam', 'filipina', 'philippines',
                    'singapura', 'singapore', 'indonesia', 'myanmar', 'kamboja', 'cambodia',
                    'laos', 'brunei', 'timor leste', 'jakarta', 'bangkok', 'manila',
                    'kuala lumpur', 'hanoi']

NEGARA_ASING = [
    'kamboja', 'cambodia', 'thailand', 'vietnam', 'filipina', 'philippines',
    'singapura', 'singapore', 'malaysia', 'myanmar', 'laos', 'brunei',
    'timor leste', 'jepang', 'japan', 'china', 'tiongkok', 'korea',
    'korea selatan', 'south korea', 'korea utara', 'north korea',
    'india', 'pakistan', 'bangladesh', 'srilanka', 'sri lanka', 'nepal',
    'amerika', 'united states', 'usa', 'kanada', 'canada', 'meksiko', 'mexico',
    'brasil', 'brazil', 'argentina', 'chile', 'peru', 'kolombia', 'colombia',
    'inggris', 'england', 'britain', 'united kingdom', 'uk',
    'jerman', 'germany', 'perancis', 'france', 'italia', 'italy',
    'spanyol', 'spain', 'belanda', 'netherlands', 'belgia', 'belgium',
    'swiss', 'switzerland', 'austria', 'portugal', 'yunani', 'greece',
    'rusia', 'russia', 'ukraina', 'ukraine', 'polandia', 'poland',
    'irlandia', 'ireland', 'skotlandia', 'scotland',
    'australia', 'selandia baru', 'new zealand',
    'mesir', 'egypt', 'maroko', 'morocco', 'aljazair', 'algeria',
    'tunisia', 'libya', 'sudan', 'ethiopia', 'kenya', 'nigeria',
    'afrika selatan', 'south africa',
    'saudi', 'saudi arabia', 'uni emirat arab', 'uae', 'qatar', 'kuwait',
    'yaman', 'yemen', 'oman', 'bahrain', 'jordan', 'libanon', 'lebanon',
    'suriah', 'syria', 'irak', 'iraq', 'iran', 'turki', 'turkey', 'turkiye',
    'israel', 'palestina', 'palestine', 'gaza',
    'kazakhstan', 'uzbekistan', 'turkmenistan', 'afghanistan',
]

KAMUS_TIM_LIGA_NEGARA = {
    'newcastle': 'inggris', 'aston villa': 'inggris', 'manchester city': 'inggris',
    'manchester united': 'inggris', 'liverpool': 'inggris', 'chelsea': 'inggris',
    'arsenal': 'inggris', 'tottenham': 'inggris', 'everton': 'inggris',
    'west ham': 'inggris', 'brighton': 'inggris', 'crystal palace': 'inggris',
    'premier league': 'inggris', 'liga inggris': 'inggris', 'fa cup': 'inggris',
    'barcelona': 'spanyol', 'real madrid': 'spanyol', 'atletico madrid': 'spanyol',
    'sevilla': 'spanyol', 'valencia': 'spanyol', 'la liga': 'spanyol',
    'liga spanyol': 'spanyol', 'el clasico': 'spanyol',
    'juventus': 'italia', 'inter milan': 'italia', 'ac milan': 'italia',
    'napoli': 'italia', 'roma': 'italia', 'lazio': 'italia',
    'serie a': 'italia', 'liga italia': 'italia',
    'bayern munich': 'jerman', 'bayern munchen': 'jerman', 'dortmund': 'jerman',
    'borussia dortmund': 'jerman', 'bundesliga': 'jerman', 'liga jerman': 'jerman',
    'psg': 'perancis', 'paris saint germain': 'perancis', 'marseille': 'perancis',
    'ligue 1': 'perancis', 'liga perancis': 'perancis',
    'ajax': 'belanda', 'psv': 'belanda', 'eredivisie': 'belanda',
    'benfica': 'portugal', 'porto': 'portugal', 'sporting lisbon': 'portugal',
    'nba': 'amerika', 'los angeles lakers': 'amerika', 'boston celtics': 'amerika',
    'golden state warriors': 'amerika', 'chicago bulls': 'amerika',
    'miami heat': 'amerika', 'brooklyn nets': 'amerika', 'new york knicks': 'amerika',
    'timberwolves': 'amerika', 'minnesota timberwolves': 'amerika',
    'rudy gobert': 'amerika',
    'boca juniors': 'argentina', 'river plate': 'argentina',
}

EVENT_BESAR_KOTA = {
    'asian games': ('Aichi-Nagoya', 'Jepang'),
    'asian games 2026': ('Aichi-Nagoya', 'Jepang'),
    'sea games': ('Bangkok', 'Thailand'),
    'sea games 2026': ('Bangkok', 'Thailand'),
    'piala dunia': ('New York', 'Amerika Serikat'),
    'world cup': ('New York', 'Amerika Serikat'),
    'olimpiade': ('Paris', 'Prancis'),
    'olympic': ('Paris', 'Prancis'),
    'winter olympics': ('Milano-Cortina', 'Italia'),
    'copa america': ('Buenos Aires', 'Argentina'),
    'piala eropa': ('Berlin', 'Jerman'),
    'euro 2026': ('Berlin', 'Jerman'),
    'piala asia': ('Doha', 'Qatar'),
    'asian cup': ('Doha', 'Qatar'),
    'aff cup': ('Bangkok', 'Thailand'),
    'piala aff': ('Bangkok', 'Thailand'),
    'liga champions': ('London', 'Inggris'),
    'champions league': ('London', 'Inggris'),
}

# V6.17.87: tambah selebriti/lifestyle/gosip/infotainment
KATA_BUKAN_NASIONAL = [
    'miss youth', 'miss indonesia', 'putri indonesia', 'kontes', 'beauty pageant',
    'pageant', 'ratu', 'finalis', 'grand final', 'pemilihan putri',
    # V6.17.87: selebriti/lifestyle/gosip
    'selebriti', 'artis', 'aktris', 'aktor', 'lifestyle', 'gosip',
    'infotainment', 'sinetron', 'drama korea', 'drakor', 'kpop', 'k-pop',
    'idol', 'band', 'penyanyi', 'vokalis', 'celebgram', 'selebgram',
    'influencer', 'youtuber', 'tiktoker', 'seleb tiktok',
    'nikah', 'menikah', 'pernikahan', 'cerai', 'perceraian',
    'pacaran', 'putus', 'selingkuh', 'perselingkuhan',
    'kabur', 'nikah siri', 'istri', 'suami',
]
KATA_BUKAN_DAERAH = [
    'jadwal kapal', 'jadwal ferry', 'jadwal pesawat', 'jadwal kereta',
    'jadwal bus', 'jadwal keberangkatan', 'jam berangkat', 'jam berlayar',
]

HARI_ID  = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN_ID = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
            'Agustus', 'September', 'Oktober', 'November', 'Desember']

LIBUR_BURSA_2026 = {
    '2026-01-01', '2026-01-16', '2026-02-16', '2026-02-17',
    '2026-03-18', '2026-03-19', '2026-03-20', '2026-03-23', '2026-03-24',
    '2026-04-03', '2026-05-01', '2026-05-14', '2026-05-15', '2026-05-27',
    '2026-05-28', '2026-06-01', '2026-06-16', '2026-08-17', '2026-08-25',
    '2026-12-24', '2026-12-25', '2026-12-31',
}

def pasar_modal_libur_hari_ini():
    now = datetime.now(WITA)
    if now.weekday() >= 5:
        return True
    tgl = now.date().strftime('%Y-%m-%d')
    return tgl in LIBUR_BURSA_2026

def GN(q, lang='id', label=None, when='1d'):
    if lang == 'en':
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:' + when)
               + '&hl=en-US&gl=US&ceid=US:EN')
    else:
        url = ('https://news.google.com/rss/search?q=' + quote_plus(q + ' when:' + when)
               + '&hl=id&gl=ID&ceid=ID:id')
    return {'url': url, 'source': label or ('Google News: ' + q), 'gn': True}

def RSSF(url, source):
    return {'url': url, 'source': source, 'gn': False}

# V6.17.82: slot 06:07 nasional +1, slot 12:07 daerah +1
JADWAL_JAM = {
    6:  {'nasional': 2, 'daerah': 2, 'ekonomi': 1},
    7:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'olahraga': 1, 'ekonomi': 1},
    8:  {'nasional': 1, 'daerah': 2, 'internasional_asean': 1, 'teknologi': 1, 'kesehatan': 1},
    9:  {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'otomotif': 1, 'olahraga': 1, 'ekonomi': 1},
    10: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'kesehatan': 1},
    11: {'nasional': 1, 'daerah': 2, 'ekonomi': 1, 'olahraga': 1, 'otomotif': 1},
    12: {'nasional': 1, 'daerah': 2, 'ekonomi': 1, 'olahraga': 1},
    13: {'nasional': 1, 'daerah': 1, 'ekonomi': 1, 'teknologi': 1, 'otomotif': 1},
    14: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'olahraga': 1, 'ekonomi': 1},
    15: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'kesehatan': 1},
    16: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'otomotif': 1, 'kesehatan': 1, 'olahraga': 1},
    17: {'nasional': 1, 'daerah': 1, 'internasional_tt': 1, 'olahraga': 1, 'ekonomi': 1},
    18: {'nasional': 1, 'daerah': 1, 'internasional_asean': 1, 'teknologi': 1, 'olahraga': 1},
}

EKONOMI_JAM_DOMESTIK = [6, 9, 11, 12, 13, 17]
EKONOMI_JAM_ASING    = [7, 14]

TOPIK_NASIONAL_WAJIB = [
    ['makan bergizi gratis', 'mbg'],
    ['koperasi desa merah putih', 'kdmp'],
    ['menteri meresmikan', 'kunjungan kerja menteri', 'menteri mengunjungi',
     'menteri meninjau', 'program menteri', 'kementerian meresmikan'],
]

KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata', 'amal', 'kayu putih']

UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
]

GAMBAR_SAMPAH_KATA = ['logo', 'icon', 'banner', 'ads', 'advert', 'sponsor',
                      'placeholder', 'default', 'noimage', 'avatar', 'profile',
                      'favicon', 'sprite', 'watermark', 'blank', 'pixel']
GAMBAR_SAMPAH_POLA = ['icon_', 'no-image', 'thumb_100', 'thumb_150', 'thumb_200',
                      '/100x', '/150x', '/200x', '100x100', '150x150', '200x200',
                      '100-', '150-', '200-']

GAMBAR_LARANG_KATA = [
    'animal', 'dog', 'cat', 'bird', 'monkey', 'elephant', 'tiger', 'lion',
    'snake', 'crocodile', 'lizard', 'frog', 'fish', 'shark', 'whale',
    'insect', 'butterfly', 'bee', 'spider', 'rat', 'mouse', 'horse',
    'cow', 'goat', 'sheep', 'pig', 'chicken', 'rooster', 'duck', 'goose',
    'rabbit', 'deer', 'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl',
    'kucing', 'anjing', 'burung', 'ular', 'kuda', 'sapi', 'ayam', 'bebek',
    'kambing', 'harimau', 'singa', 'gajah', 'monyet', 'buaya', 'ikan',
    'pet', 'wildlife', 'fauna', 'orangutan', 'komodo', 'leopard', 'jaguar',
    'cheetah', 'puma', 'lynx', 'panther', 'puppy', 'kitten', 'hound',
    'terrier', 'retriever', 'shepherd', 'falcon', 'hawk', 'sparrow',
    'pigeon', 'parakeet', 'peacock', 'hamster', 'guinea', 'ferret',
    'hedgehog', 'squirrel', 'stag', 'boar', 'bison', 'yak', 'llama',
    'alpaca', 'otter', 'badger', 'beaver', 'raccoon', 'skunk', 'koala',
    'kangaroo', 'panda', 'penguin', 'dolphin', 'seal_', 'walrus',
    'octopus', 'crab', 'lobster', 'shrimp', 'jellyfish', 'starfish',
    'dinosaur', 'dragon', 'unicorn', 'mosque', 'masjid', 'church', 'gereja',
    'cathedral', 'temple', 'pura', 'vihara', 'pagoda', 'synagogue',
    'shrine', 'monastery', 'worship', 'ibadah', 'human', 'people', 'person',
    'crowd', 'portrait', 'woman', 'women', 'girl', 'child', 'children',
    'soldier', 'manusia', 'warga', 'kerumunan', 'wajah', 'shoes', 'shoe',
    'sneaker', 'sneakers', 'sandal', 'sandals', 'slipper', 'slippers',
    'footwear', 'high heels', 'stiletto', 'sendal', 'sepatu',
]

KATA_ANALISIS = ['analisis', 'soroti', 'opini', 'tinjauan', 'analysis', 'opinion', 'editorial']
JANJI_JADWAL  = ['jadwal', 'schedule']
JANJI_TABEL   = ['klasemen', 'standing', 'ranking', 'peringkat']
JANJI_ANGKA   = ['hasil', 'skor', 'result']
JANJI_HARGA   = ['harga', 'tarif', 'biaya', 'berapa', 'sewa', 'gaji']
KATA_HARGA_LONGGAR = ['naik', 'turun', 'melonjak', 'anjlok', 'drastis', 'meroket',
                      'terjun', 'menguat', 'melemah']

KATA_HEWAN_SLUG = [
    'dog', 'puppy', 'cat', 'kitten', 'bird', 'monkey', 'elephant', 'tiger',
    'lion', 'leopard', 'jaguar', 'cheetah', 'puma', 'lynx', 'panther',
    'snake', 'crocodile', 'lizard', 'frog', 'fish', 'shark', 'whale',
    'insect', 'butterfly', 'bee', 'spider', 'rat', 'mouse', 'horse', 'cow',
    'goat', 'sheep', 'pig', 'chicken', 'rooster', 'duck', 'goose', 'rabbit',
    'deer', 'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl', 'hamster',
    'ferret', 'hedgehog', 'squirrel', 'stag', 'boar', 'bison', 'otter',
    'badger', 'beaver', 'raccoon', 'koala', 'kangaroo', 'panda', 'penguin',
    'dolphin', 'walrus', 'octopus', 'crab', 'lobster', 'shrimp', 'jellyfish',
    'dinosaur', 'zoo', 'safari', 'wildlife', 'fauna', 'anjing', 'kucing',
    'burung', 'ular', 'kuda', 'sapi', 'ayam', 'bebek', 'kambing', 'harimau',
    'singa', 'gajah', 'monyet', 'buaya', 'ikan', 'serigala',
]

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
JAM_KESEHATAN = {8: 0, 10: 1, 15: 2, 16: 3}

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
JAM_OTOMOTIF = {9: 0, 11: 1, 13: 2, 16: 3}

DOMAIN_TEKNOLOGI = [
    {'nama': 'Gadget & Smartphone', 'aturan': 'Berita HARUS BANYAK, boleh hingga 2 halaman. WAJIB memuat SEBANYAK mungkin gadget/baru yang ada di materi sekaligus. SPESIFIKASI setiap gadget WAJIB lengkap (layar, chipset, RAM, kamera, baterai, sistem operasi - sesuai yang tertulis di materi). Estimasi harga WAJIB disebut jika ada di materi.', 'query': [
        ('smartphone launch spesifikasi harga', 'id'),
        ('gadget baru rilis Indonesia', 'id'),
        ('new smartphone launch specs price', 'en'),
    ]},
    {'nama': 'AI & Kecerdasan Buatan', 'aturan': 'Berita HARUS PANJANG dan LENGKAP, hingga 2 halaman. WAJIB membahas perkembangan AI TERKINI SELURUH DUNIA yang ada di materi: pemain barunya, kapabilitasnya, dampaknya, angka & tanggal persis dari materi.', 'query': [
        ('artificial intelligence development', 'en'),
        ('AI Indonesia terkini', 'id'),
        ('kecerdasan buatan terbaru', 'id'),
    ]},
    {'nama': 'Aplikasi & Internet', 'aturan': 'Berita HARUS LENGKAP dan BANYAK - gabungkan semua materi aplikasi/internet yang tersedia menjadi satu berita kaya.', 'query': [
        ('aplikasi baru populer', 'id'),
        ('fitur media sosial terbaru', 'id'),
        ('internet Indonesia kecepatan', 'id'),
    ]},
    {'nama': 'Startup & Ekonomi Digital', 'aturan': 'Berita HARUS LENGKAP dan BANYAK - pendanaan, valuasi, ekspansi, e-commerce, fintech: semua angka WAJIB persis dari materi.', 'query': [
        ('startup Indonesia pendanaan', 'id'),
        ('e-commerce fintech Indonesia', 'id'),
        ('startup funding tech asia', 'en'),
    ]},
    {'nama': 'Keamanan Digital', 'aturan': 'Jika materi keamanan digital KURANG, BOLEH menambahkan berita teknologi lainnya yang ada di materi sumber agar berita tetap kaya (isi silang khusus domain ini).', 'query': [
        ('kebocoran data keamanan', 'id'),
        ('scam online modus', 'id'),
        ('cyber security breach', 'en'),
    ]},
    {'nama': 'Inovasi & Sains Teknologi', 'aturan': 'Berita HARUS LENGKAP dan BANYAK - inovasi, riset, luar angkasa, kendaraan listrik: semua yang ada di materi dibahas menyeluruh.', 'query': [
        ('kendaraan listrik teknologi', 'id'),
        ('space technology innovation', 'en'),
        ('inovasi teknologi riset', 'id'),
    ]},
]
JAM_TEKNOLOGI = {8: 0, 13: 1, 18: 2}

EKONOMI_DOMESTIK_FEEDS = [
    RSSF('https://market.bisnis.com/feed', 'Bisnis Market'),
    RSSF('https://www.antaranews.com/rss/pasar-modal', 'Antara Pasar Modal'),
    RSSF('https://www.antaranews.com/rss/ekonomi', 'Antara Ekonomi'),
    RSSF('https://www.cnnindonesia.com/ekonomi/rss', 'CNN Ekonomi'),
    RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia Market'),
    RSSF('https://www.cnbcindonesia.com/news/rss', 'CNBC Indonesia News'),
    RSSF('https://economy.okezone.com/rss', 'Okezone Economy'),
    RSSF('https://www.kontan.co.id/rss', 'Kontan'),
    RSSF('https://investor.id/rss', 'Investor.id'),
    RSSF('https://www.katadata.co.id/rss', 'Katadata'),
    RSSF('https://www.wartaekonomi.co.id/rss', 'Warta Ekonomi'),
    RSSF('https://ekonomi.bisnis.com/rss', 'Bisnis Ekonomi'),
    RSSF('https://www.idxchannel.com/rss', 'IDX Channel'),
    RSSF('https://www.liputan6.com/rss', 'Liputan6'),
    RSSF('https://www.idntimes.com/rss', 'IDN Times'),
    RSSF('https://www.antaranews.com/rss/ekonomi-bisnis', 'Antara Ekonomi Bisnis'),
    RSSF('https://www.kompas.com/ekonomi/rss', 'Kompas Ekonomi'),
    RSSF('https://money.kompas.com/rss', 'Kompas Money'),
    RSSF('https://www.medcom.id/rss/ekonomi', 'Medcom Ekonomi'),
    GN('ekonomi indonesia hari ini', 'id', 'GN Ekonomi Indonesia'),
    GN('IHSG hari ini', 'id', 'GN IHSG'),
    GN('rupiah dolar hari ini', 'id', 'GN Kurs Rupiah'),
    GN('inflasi indonesia', 'id', 'GN Inflasi'),
    GN('ekspor impor indonesia', 'id', 'GN Ekspor Impor'),
    GN('BI rate suku bunga', 'id', 'GN BI Rate'),
    GN('APBN pajak indonesia', 'id', 'GN APBN Pajak'),
    GN('UMKM Indonesia', 'id', 'GN UMKM'),
    GN('PHK tenaga kerja Indonesia', 'id', 'GN PHK'),
    GN('harga beras jagung cabai', 'id', 'GN Harga Pangan'),
    GN('sawit CPO batu bara nikel Indonesia', 'id', 'GN Komoditas'),
    GN('pertambangan smelter hilirisasi Indonesia', 'id', 'GN Tambang'),
    GN('properti perumahan Indonesia', 'id', 'GN Properti'),
    GN('kripto aset digital Indonesia', 'id', 'GN Kripto'),
]

EKONOMI_ASING_FEEDS = [
    RSSF('https://feeds.a.dj.com/rss/RSSMarketsMain.xml', 'WSJ Markets'),
    RSSF('https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml', 'WSJ Business'),
    RSSF('https://www.cnbc.com/id/100003114/device/rss/rss.html', 'CNBC World'),
    RSSF('https://www.cnbc.com/id/10000664/device/rss/rss.html', 'CNBC Finance'),
    RSSF('https://www.ft.com/?format=rss', 'Financial Times'),
    RSSF('https://www.scmp.com/rss/92/feed', 'SCMP Business'),
    RSSF('https://www.japantimes.co.jp/feed/', 'Japan Times Biz'),
    GN('china economy', 'en', 'GN Ekonomi China'),
    GN('japan economy', 'en', 'GN Ekonomi Jepang'),
    GN('south korea economy', 'en', 'GN Ekonomi Korea Selatan'),
    GN('vietnam economy', 'en', 'GN Ekonomi Vietnam'),
    GN('india economy', 'en', 'GN Ekonomi India'),
    GN('us economy', 'en', 'GN Ekonomi USA'),
    GN('european union economy', 'en', 'GN Ekonomi Eropa'),
    GN('china exports imports', 'en', 'GN Ekspor Impor China'),
    GN('china manufacturing factory', 'en', 'GN Manufaktur China'),
    GN('china lithium battery mining', 'en', 'GN Tambang China'),
    GN('global oil opec', 'en', 'GN Minyak Global'),
    GN('fed interest rate', 'en', 'GN Fed'),
    GN('ecb boj pboc interest rate', 'en', 'GN Bank Sentral'),
    GN('dow jones nasdaq nikkei hang seng', 'en', 'GN Index Saham'),
    GN('gold copper lithium price', 'en', 'GN Komoditas Global'),
    GN('global inflation', 'en', 'GN Inflasi Global'),
    GN('global trade tariff', 'en', 'GN Perdagangan Global'),
    GN('taiwan semiconductor tsmc chip', 'en', 'GN Semikonduktor'),
]

# V6.17.96: HAPUS rri.co.id + tarakantv.co.id dari HUNT['daerah']
# Alasan: rri.co.id materi terlalu pendek (145-180 kar); tarakantv.co.id tidak pernah ada berita.
HUNT = {
    'nasional': [
        RSSF('https://www.cnnindonesia.com/nasional/rss', 'CNN Indonesia'),
        RSSF('https://nasional.kompas.com/rss', 'Kompas Nasional'),
        RSSF('https://www.antaranews.com/rss/nasional', 'Antara'),
        RSSF('https://news.okezone.com/rss', 'Okezone'),
        RSSF('https://www.liputan6.com/rss', 'Liputan6'),
        RSSF('https://www.detik.com/feed', 'Detik'),
        RSSF('https://nasional.tribunnews.com/rss', 'Tribun Nasional'),
        RSSF('https://www.suara.com/rss', 'Suara.com'),
        RSSF('https://kumparan.com/rss', 'Kumparan'),
        RSSF('https://www.viva.co.id/rss', 'Viva.co.id'),
        RSSF('https://www.sindonews.com/rss', 'Sindonews'),
        RSSF('https://rmol.id/rss', 'RMOL'),
        RSSF('https://www.jpnn.com/rss', 'JPNN'),
        RSSF('https://www.beritasatu.com/rss', 'Beritasatu'),
        RSSF('https://www.medcom.id/rss/nasional', 'Medcom Nasional'),
        GN('pemerintah indonesia', 'id', 'Google News Nasional'),
        GN('dpr indonesia', 'id', 'Google News Nasional'),
        GN('Prabowo Subianto', 'id', 'Google News Presiden Prabowo'),
        GN('Gibran Rakabuming', 'id', 'Google News Wapres Gibran'),
        GN('Makan Bergizi Gratis MBG', 'id', 'Google News MBG'),
        GN('Koperasi Desa Merah Putih', 'id', 'Google News KDMP'),
        GN('menteri meresmikan', 'id', 'Google News Menteri Resmikan'),
        GN('kunjungan kerja menteri indonesia', 'id', 'Google News Menteri Kunjungan'),
        GN('menteri indonesia program kementerian', 'id', 'Google News Program Kementerian'),
        GN('kebijakan pemerintah indonesia', 'id', 'GN Kebijakan Pemerintah'),
        GN('hukum pidana indonesia', 'id', 'GN Hukum Pidana'),
        GN('kpk korupsi indonesia', 'id', 'GN KPK Korupsi'),
        GN('tni polri indonesia', 'id', 'GN TNI Polri'),
        GN('pendidikan indonesia', 'id', 'GN Pendidikan'),
        GN('sosial budaya indonesia', 'id', 'GN Sosial Budaya'),
    ],
    'daerah': [
        RSSF('https://kaltara.tribunnews.com/rss', 'Tribun Kaltara'),
        RSSF('https://kaltim.tribunnews.com/rss', 'Tribun Kaltim'),
        RSSF('https://www.antaranews.com/rss/daerah', 'Antara Daerah'),
        RSSF('https://adpim.kaltaraprov.go.id/feed/', 'Adpim Kaltara'),
        RSSF('https://benuanta.co.id/rss', 'Benuanta'),
        # V6.17.96: rri.co.id DIHAPUS (materi terlalu pendek)
        # V6.17.96: tarakantv.co.id DIHAPUS (tidak pernah ada berita)
        RSSF('https://kaltarapost.co.id/rss', 'Kaltara Post'),
        RSSF('https://www.prokaltara.co.id/rss', 'Pro Kaltara'),
        RSSF('https://kaltimpost.jawapos.com/rss', 'Kaltim Post'),
        RSSF('https://www.jpnn.com/rss/daerah', 'JPNN Daerah'),
        GN('Tarakan', 'id', 'Google News Tarakan'),
        GN('Pemkot Tarakan', 'id', 'Google News Pemkot Tarakan'),
        GN('Wali Kota Tarakan', 'id', 'Google News Wali Kota Tarakan'),
        GN('Polres Tarakan', 'id', 'Google News Polres Tarakan'),
        GN('Kaltara', 'id', 'Google News Kaltara'),
        GN('Nunukan', 'id', 'Google News Nunukan'),
        GN('Bulungan', 'id', 'Google News Bulungan'),
        GN('Malinau', 'id', 'Google News Malinau'),
        GN('Tana Tidung', 'id', 'Google News Tana Tidung'),
        GN('Tanjung Selor', 'id', 'Google News Tanjung Selor'),
        RSSF('https://jatim.tribunnews.com/rss', 'Tribun Jatim'),
        RSSF('https://jateng.tribunnews.com/rss', 'Tribun Jateng'),
        RSSF('https://jabar.tribunnews.com/rss', 'Tribun Jabar'),
        RSSF('https://dki.tribunnews.com/rss', 'Tribun DKI Jakarta'),
        RSSF('https://bali.tribunnews.com/rss', 'Tribun Bali'),
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
        RSSF('https://sultra.tribunnews.com/rss', 'Tribun Sultra'),
        GN('Makassar', 'id', 'Google News Makassar'),
        GN('Manado', 'id', 'Google News Manado'),
        GN('Kendari', 'id', 'Google News Kendari'),
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
        RSSF('https://www.channelnewsasia.com/rssfeed/8395986/asia', 'CNA Asia'),
        RSSF('https://www.antaranews.com/rss/world', 'Antara Dunia'),
        RSSF('https://www.nationthailand.com/rss', 'The Nation Thailand'),
        RSSF('https://www.manilatimes.net/feed', 'Manila Times'),
        RSSF('https://www.thaipbsworld.com/feed/', 'Thai PBS World'),
        RSSF('https://www.thejakartapost.com/rss', 'Jakarta Post'),
        RSSF('https://jakartaglobe.id/feed', 'Jakarta Globe'),
        RSSF('https://e.vnexpress.net/rss/news.rss', 'VN Express'),
        RSSF('https://www.khmertimeskh.com/feed/', 'Khmer Times'),
        RSSF('https://www.myanmar-now.org/en/rss', 'Myanmar Now'),
        RSSF('https://www.malaymail.com/feed/rss', 'Malay Mail'),
        GN('asean', 'en', 'Google News ASEAN'),
        GN('malaysia indonesia', 'en', 'Google News Malaysia-Indonesia'),
        GN('thailand southeast asia', 'en', 'Google News Thailand'),
        GN('vietnam southeast asia', 'en', 'Google News Vietnam'),
        GN('philippines southeast asia', 'en', 'Google News Filipina'),
        GN('singapore southeast asia', 'en', 'Google News Singapura'),
        GN('myanmar southeast asia', 'en', 'Google News Myanmar'),
        GN('cambodia laos brunei', 'en', 'Google News Kamboja-Laos-Brunei'),
        GN('borneo malaysia', 'en', 'Google News Borneo'),
        GN('asean summit', 'en', 'Google News ASEAN Summit'),
        GN('asean economy trade', 'en', 'Google News ASEAN Trade'),
        GN('asean investment deal', 'en', 'Google News ASEAN Investment'),
        GN('asean indonesia kerja sama', 'id', 'GN ASEAN Kerja Sama'),
        GN('asean ktt', 'id', 'GN ASEAN KTT'),
    ],
    'internasional_tt': [
        RSSF('https://www.aljazeera.com/xml/rss/all.xml', 'Al Jazeera'),
        RSSF('https://www.middleeasteye.net/rss', 'Middle East Eye'),
        RSSF('https://www.timesofisrael.com/feed/', 'Times of Israel'),
        RSSF('https://english.alarabiya.net/tools/rss', 'Al Arabiya'),
        RSSF('https://gulfnews.com/rss', 'Gulf News'),
        RSSF('https://www.jpost.com/rss/rssfeedsfrontpage.aspx', 'Jerusalem Post'),
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
        RSSF('https://apnews.com/index.rss', 'AP News'),
        RSSF('https://www.france24.com/en/rss', 'France24'),
        RSSF('http://rss.cnn.com/rss/edition_world.rss', 'CNN World'),
        RSSF('https://www.cgtn.com/subscribe/rss/section/world.xml', 'CGTN World'),
        RSSF('https://www.cgtn.com/subscribe/rss/section/business.xml', 'CGTN Business'),
        RSSF('https://www.globaltimes.cn/rss/outbrain.xml', 'Global Times'),
        RSSF('https://www.scmp.com/rss/91/feed', 'SCMP China'),
        RSSF('https://www.scmp.com/rss/92/feed', 'SCMP Asia'),
        RSSF('https://www.japantimes.co.jp/feed/', 'Japan Times'),
        RSSF('https://www.koreaherald.com/common/rss_xml.php?ct=020000000000', 'Korea Herald'),
        RSSF('https://www3.nhk.or.jp/nhkworld/en/news/rss/all.xml', 'NHK World'),
        RSSF('https://timesofindia.indiatimes.com/rssfeedstopstories.cms', 'Times of India'),
        GN('us politics', 'en', 'Google News USA'),
        GN('russia politics', 'en', 'Google News Rusia'),
        GN('europe politics', 'en', 'Google News Eropa'),
        GN('china politics', 'en', 'Google News China'),
        GN('china economy', 'en', 'Google News China Economy'),
    ],
    'ekonomi': [
        RSSF('https://market.bisnis.com/feed', 'Bisnis Market'),
        RSSF('https://www.antaranews.com/rss/pasar-modal', 'Antara Pasar Modal'),
        RSSF('https://www.cnnindonesia.com/ekonomi/rss', 'CNN Indonesia'),
        RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia'),
        RSSF('https://www.antaranews.com/rss/ekonomi', 'Antara'),
        RSSF('https://economy.okezone.com/rss', 'Okezone Economy'),
        RSSF('https://www.kontan.co.id/rss', 'Kontan'),
        RSSF('https://feeds.a.dj.com/rss/RSSMarketsMain.xml', 'WSJ Markets'),
        RSSF('https://www.cnbc.com/id/100003114/device/rss/rss.html', 'CNBC World'),
        RSSF('https://www.ft.com/?format=rss', 'Financial Times'),
        RSSF('https://www.scmp.com/rss/92/feed', 'SCMP Business'),
    ],
    'olahraga': [
        RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Indonesia'),
        RSSF('https://www.bola.net/feed', 'Bola.net'),
        RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        RSSF('https://www.goal.com/feeds/en/news', 'Goal.com'),
        RSSF('https://www.espn.com/espn/rss/news', 'ESPN'),
        RSSF('https://feeds.bbci.co.uk/sport/rss.xml', 'BBC Sport'),
        RSSF('https://www.espn.com/espn/rss/soccer/news', 'ESPN Soccer'),
        RSSF('https://www.skysports.com/rss/12040', 'Sky Sports Football'),
        GN('timnas indonesia', 'id', 'Google News Timnas'),
        GN('premier league', 'en', 'Google News Premier League'),
        GN('bundesliga', 'en', 'Google News Bundesliga'),
        GN('la liga', 'en', 'Google News La Liga'),
        GN('nba basketball', 'en', 'Google News NBA'),
        GN('badminton indonesia turnamen', 'id', 'Google News Badminton'),
        GN('badminton tournament', 'en', 'Google News Badminton Dunia'),
        GN('voli nasional timnas', 'id', 'Google News Voli'),
        GN('volleyball nations league', 'en', 'Google News Voli Dunia'),
        GN('IBL basket indonesia', 'id', 'Google News Basket IBL'),
        GN('tenis turnamen grand slam', 'id', 'Google News Tenis'),
        GN('liga 1 indonesia hasil', 'id', 'Google News Liga 1'),
    ],
    'otomotif': [
        RSSF('https://www.otomotifnet.com/rss', 'Otomotifnet'),
        RSSF('https://www.gridoto.com/rss', 'GridOto'),
        RSSF('https://oto.detik.com/rss', 'Detik Oto'),
        RSSF('https://www.motorplus-online.com/rss', 'Motorplus'),
        RSSF('https://www.autocar.co.uk/rss', 'Autocar'),
        RSSF('https://www.motor1.com/rss/news/all/', 'Motor1'),
        RSSF('https://www.carscoops.com/feed/', 'Carscoops'),
        RSSF('https://www.autoblog.com/rss.xml', 'Autoblog'),
        RSSF('https://www.caranddriver.com/rss/all.xml/', 'Car and Driver'),
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

TOPIK_BESAR_GATE = [
    'tsunami', 'gempa', 'erupsi', 'gunung meletus', 'banjir bandang',
    'banjir', 'flood', 'tanah longsor', 'longsor', 'kebakaran',
    'karhutla', 'kebakaran hutan', 'kecelakaan', 'ledakan', 'tabrakan',
    'hurricane', 'typhoon', 'cyclone', 'wildfire', 'earthquake',
    'perang', 'war', 'invasi', 'missile', 'nuclear',
    'asian games', 'sea games', 'piala dunia', 'world cup',
    'olimpiade', 'olympic', 'piala asia', 'asian cup',
    'piala eropa', 'euro 202', 'copa america',
    'nba finals', 'liga champions final', 'pemilu', 'pilpres', 'pilkada',
]

KATA_SPAM_JUDUL = ['【', '】', 'livestream', 'live stream', 'live free',
                   'tv channel', 'watch online', 'live streaming',
                   'free tv', 'kualitas hd', 'link live', 'nonton live']

def judul_spam(judul):
    j = (judul or '').lower()
    for k in KATA_SPAM_JUDUL:
        if k in j:
            return True
    return False

# AKHIR PART 1

# PART 2 - FEEDS BREAKING, KATA-KUNCI, ANTI-DOBEL, SCRAPER, SYSTEM PROMPT

try:
    from gnews_decoder import decode_many as _gn_decode_many
    _GN_DECODER_OK = True
except Exception:
    _GN_DECODER_OK = False
    _gn_decode_many = None

try:
    from playtrafi import Playtrafi as _Playtrafi
    _PLAYTRAFI_OK = True
except Exception:
    _PLAYTRAFI_OK = False
    _Playtrafi = None

MATERI_MAKS_KARAKTER = 1000

REJECTED_URLS_CACHE = None

_CACHE_SCRAPE = {}
_GN_DECODE_CACHE = {}

DEBUG_SCRAPE = True

# V6.17.86: deteksi materi sampah (anti-bot/JS block)
KATA_MATERI_SAMPAH = [
    'unusual traffic', 'detected unusual', 'unusual traffic from your',
    'enable javascript', 'javascript is required', 'javascript enabled',
    'enable cookies', 'cookies required',
    'access denied', 'request blocked', 'blocked by',
    'verify you are human', 'are you a robot', 'captcha',
    'cloudflare', 'checking your browser',
    'please turn on javascript', 'sorry, you have been blocked',
    'attention required', 'security check', 'bot detection',
]

BREAKING_DOMESTIK_FEEDS = [
    RSSF('https://www.cnnindonesia.com/nasional/rss', 'CNN Indonesia'),
    RSSF('https://www.detik.com/feed', 'Detik'),
    RSSF('https://nasional.kompas.com/rss', 'Kompas Nasional'),
    RSSF('https://www.liputan6.com/rss', 'Liputan6'),
    RSSF('https://www.antaranews.com/rss/nasional', 'Antara'),
    RSSF('https://www.cnbcindonesia.com/market/rss', 'CNBC Indonesia'),
    RSSF('https://nasional.tribunnews.com/rss', 'Tribun Nasional'),
    RSSF('https://kaltara.tribunnews.com/rss', 'Tribun Kaltara'),
    RSSF('https://www.bola.net/feed', 'Bola.net'),
    RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
    RSSF('https://kumparan.com/rss', 'Kumparan'),
    RSSF('https://www.viva.co.id/rss', 'Viva.co.id'),
    RSSF('https://www.sindonews.com/rss', 'Sindonews'),
    RSSF('https://rmol.id/rss', 'RMOL'),
    RSSF('https://www.jpnn.com/rss', 'JPNN'),
    GN('breaking news indonesia', 'id', 'GN Breaking Indonesia'),
    GN('gempa indonesia hari ini', 'id', 'GN Gempa Indonesia'),
    GN('banjir indonesia hari ini', 'id', 'GN Banjir Indonesia'),
    GN('kecelakaan besar indonesia', 'id', 'GN Kecelakaan'),
    GN('kebakaran besar indonesia', 'id', 'GN Kebakaran'),
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
    RSSF('https://www.cgtn.com/subscribe/rss/section/world.xml', 'CGTN World'),
    RSSF('https://www.scmp.com/rss/91/feed', 'SCMP China'),
    RSSF('https://www.japantimes.co.jp/feed/', 'Japan Times'),
    RSSF('https://www3.nhk.or.jp/nhkworld/en/news/rss/all.xml', 'NHK World'),
    RSSF('https://feeds.reuters.com/reuters/worldNews', 'Reuters'),
    RSSF('https://feeds.reuters.com/reuters/topNews', 'Reuters Top'),
    RSSF('https://www.dw.com/en/top-stories/s-9097/rss', 'DW'),
    RSSF('https://abcnews.go.com/abcnews/internationalheadlines', 'ABC News'),
    RSSF('https://feeds.nbcnews.com/nbcnews/public/world', 'NBC News'),
    GN('breaking world news', 'en', 'GN Breaking Dunia'),
    GN('major earthquake', 'en', 'GN Gempa Besar Dunia'),
    GN('war conflict missile', 'en', 'GN Perang'),
    GN('breaking asia news', 'en', 'GN Breaking Asia'),
    GN('flood disaster', 'en', 'GN Banjir Dunia'),
    GN('plane crash', 'en', 'GN Pesawat Jatuh'),
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
    'tersangka korupsi', 'tertangkap tangan', 'reshuffle', 'pergantian menteri',
    'menteri diganti', 'menteri meninggal', 'menteri wafat', 'menteri ditangkap',
    'menteri tersangka', 'presiden meninggal', 'wapres meninggal',
    'kerusuhan', 'ricuh', 'bentrok massa', 'demo besar', 'demonstrasi besar',
    'massa membakar', 'membakar massal', 'tawuran besar',
]

BREAKING_INT_KRITIS = [
    'banjir besar', 'major flood', 'flash flood', 'devastating flood',
    'tsunami', 'tsunami warning',
    'gempa bumi', 'earthquake', 'magnitude',
    'angin topan', 'typhoon', 'hurricane', 'cyclone', 'super typhoon',
    'letusan gunung', 'volcanic eruption', 'volcano',
    'kebakaran hutan', 'wildfire', 'forest fire',
    'tanah longsor', 'landslide',

    'pesawat komersial jatuh', 'commercial plane crash',
    'airliner crash', 'passenger plane crash',
    'pesawat penumpang jatuh', 'pesawat hilang', 'plane missing',
    'kapal tenggelam', 'ferry sinks', 'ship sinks', 'boat capsizes',
    'kapal terbakar', 'ferry fire', 'ship fire',
    'kereta anjlok', 'train derailment', 'train crash', 'train collision',

    'deklarasi perang', 'declaration of war',
    'serangan rudal', 'missile strike', 'missile attack', 'rocket attack',
    'kudeta', 'coup', 'military coup',
    'uji coba nuklir', 'nuclear test', 'nuclear attack',
    'serangan teroris', 'terror attack', 'terrorist attack',
    'gencatan senjata besar', 'ceasefire deal', 'peace deal', 'peace agreement',
    'embargo minyak', 'oil embargo',

    'presiden meninggal', 'president dies', 'president dead',
    'pm meninggal', 'prime minister dies',
    'presiden mundur', 'president resigns', 'president steps down',
    'pembunuhan pejabat', 'assassination',
    'penculikan pejabat', 'kidnapping',
    'presiden terpilih', 'elected president', 'wins election',
    'referendum kemerdekaan', 'independence referendum',
    'pejabat ditangkap', 'official arrested', 'minister arrested',
    'bandar narkoba', 'drug lord arrested', 'drug kingpin',

    'krisis mata uang', 'currency crisis', 'devaluation',
    'bank runtuh', 'bank collapse', 'bank fails',
    'kebangkrutan negara', 'sovereign default',
    'opec memangkas', 'opec cuts',

    'peluncuran roket berawak', 'crewed launch', 'manned launch',
    'nasa launch', 'spacex launch', 'cnsa launch',

    'pandemi', 'pandemic', 'who emergency', 'global health emergency',
]

BREAKING_INT_TOLAK = [
    'small plane', 'small aircraft', 'private plane', 'private jet',
    'single-engine', 'single engine', 'small plane crash',
    'military plane', 'military aircraft', 'fighter jet', 'fighter plane',
    'warplane', 'helicopter crash', 'chopper crash',
    'pesawat kecil', 'pesawat pribadi', 'pesawat militer',
    'jet tempur', 'helikopter jatuh',
    'skydivers', 'skydiving',
    'plane crash drill', 'simulasi', 'latihan',
    'plane crash warning', 'memorial', 'peringatan',
    'anniversary', '30th anniversary', '40th anniversary',
    'larangan impor alkohol', 'alcohol import ban', 'liquor ban',
    'larangan susu', 'dairy ban', 'milk ban',
    'ban on alcohol', 'ban on dairy',
    'tarif kecil', 'minor tariff', 'small tariff',
    'sanksi ringan', 'minor sanctions',
    'keluhan dagang', 'trade complaint',
    'tarif baja', 'tarif aluminium', 'steel tariff', 'aluminum tariff',
    # V6.17.89: tolak simulator/drill/demo/edukasi (bukan breaking aktual)
    'simulator', 'simulation', 'simulate',
    'drill', 'exercise',
    'demonstration', 'showcase', 'exhibition', 'display',
    'commemoration', 'memorial service',
    'preparedness', 'awareness campaign', 'awareness program',
    'will bring', 'will show', 'will demonstrate',
    'ready for', 'getting ready', 'prepares for',
    'mock', 'rehearsal', 'trial run', 'test run',
]

DUNIA_KRITIS = BREAKING_INT_KRITIS

# V6.17.90: aktor non-breaking (selebriti/artis/influencer) — bukan breaking
AKTOR_NON_BREAKING = [
    # Selebriti internasional
    'leonardo dicaprio', 'dicaprio', 'taylor swift', 'beyonce', 'rihanna',
    'kim kardashian', 'kanye', 'brad pitt', 'angelina jolie',
    'tom cruise', 'johnny depp', 'jennifer aniston', 'selena gomez',
    'justin bieber', 'ariana grande', 'billie eilish', 'drake',
    'cristiano ronaldo', 'lionel messi', 'david beckham',
    # Selebriti Indonesia
    'artis', 'selebriti', 'selebgram', 'celebgram', 'influencer',
    'youtuber', 'tiktoker', 'konten kreator', 'content creator',
    'penyanyi', 'musisi', 'vokalis', 'band ',
    'aktor', 'aktris', 'pemain film', 'bintang film', 'bintang sinetron',
    'komentar artis', 'ucapan artis', 'kata artis', 'menurut artis',
    'soroti artis', 'dukung artis', 'tanggapi artis',
    'seleb tiktok', 'seleb instagram', 'vlogger', 'podcaster',
]

def _ada_aktor_non_breaking(teks):
    """V6.17.90: cek apakah teks dominan tentang aktor non-breaking."""
    t = (teks or '').lower()
    for k in AKTOR_NON_BREAKING:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', t):
                return k
        else:
            if k in t:
                return k
    return ''

def _pesawat_kecil(text):
    t = (text or '').lower()
    for k in BREAKING_INT_TOLAK:
        if k in t:
            return True
    return False

KATA_TURNAMEN_OLAHRAGA = [
    'fifa', 'aff', 'uefa', 'afc', 'piala dunia', 'world cup', 'sea games',
    'asian games', 'olimpiade', 'olympic', 'piala asia', 'asian cup',
    'piala aff', 'aff cup', 'fifa asean cup', 'piala eropa', 'euro 202',
    'copa america', 'liga champions', 'champions league', 'europa league',
    'premier league', 'la liga', 'serie a', 'bundesliga', 'ligue 1',
    'eredivisie', 'nba', 'wnba', 'ibl', 'badminton', 'bulu tangkis', 'bwf',
    'voli', 'volleyball', 'fivb', 'motogp', 'formula 1', 'f1',
]

def adalah_turnamen_olahraga(teks):
    t = (teks or '').lower()
    return any(k in t for k in KATA_TURNAMEN_OLAHRAGA)

KATA_WAJIB_OLAHRAGA = [
    'bola', 'sepak bola', 'sepakbola', 'football', 'soccer', 'basket', 'nba',
    'wnba', 'ibl', 'badminton', 'bulu tangkis', 'bwf', 'voli', 'volleyball',
    'fivb', 'tenis', 'tennis', 'atp', 'wta', 'motogp', 'formula 1', 'f1',
    'balap', 'liga', 'piala', 'turnamen', 'kejuaraan', 'kompetisi', 'timnas',
    'atlet', 'pemain', 'klub', 'klub sepak', 'pertandingan', 'laga', 'skor',
    'klasemen', 'gol', 'olimpiade', 'olympic', 'sea games', 'asian games',
    'stadion', 'kick-off', 'kick off',
]

KATA_BUKAN_OLAHRAGA = [
    'haji', 'umroh', 'umrah', 'arbain', 'kabah', 'mekkah', 'mekah',
    'madinah', 'ibadah haji', 'jamaah haji', 'kuota haji', 'antrean haji',
    'calon haji', 'manasik', 'ihram', 'tawaf', 'sa\'i',
    'puasa', 'ramadan', 'idul fitri', 'idul adha', 'qurban', 'zakat',
    'isra miraj', 'maulid', 'nabi muhammad', 'pesantren', 'ulama',
    'pendidikan', 'kurikulum', 'sekolah', 'siswa', 'mahasiswa', 'guru',
    'kampus', 'universitas', 'beasiswa', 'ujian', 'unbk',
    'pajak', 'anggaran', 'apbn', 'apbd', 'subsidi', 'bantuan sosial',
    'bansos', 'pkh', 'blt', 'sembako',
    'kesehatan', 'rumah sakit', 'dokter', 'obat', 'vaksin', 'imunisasi',
    'penyakit', 'gizi', 'stunting',
    'politik', 'pemilu', 'pilpres', 'pilkada', 'partai', 'dpr', 'presiden',
    'menteri', 'gubernur', 'bupati', 'walikota', 'kepala daerah',
    'polisi', 'pencurian', 'pembunuhan', 'kriminal', 'narkoba',
    'ekonomi', 'bisnis', 'keuangan', 'bank', 'saham', 'ihsg', 'rupiah',
    'dolar', 'kurs', 'investasi', 'ekspor', 'impor',
    'teknologi', 'gadget', 'aplikasi', 'internet', 'ai', 'kecerdasan buatan',
    'otomotif', 'mobil', 'motor',
]

def adalah_konten_olahraga(teks):
    t = (teks or '').lower()
    for k in KATA_BUKAN_OLAHRAGA:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', t):
                return False
        else:
            if k in t:
                return False
    return any(k in t for k in KATA_WAJIB_OLAHRAGA)

KATA_KUNCI_OTOMOTIF = [
    'mobil', 'motor', 'skutik', 'matic', 'bebek', 'sport touring',
    'kendaraan listrik', 'mobil listrik', 'motor listrik', 'tesla', 'byd',
    'geely', 'nissan', 'toyota', 'honda', 'yamaha', 'suzuki', 'mitsubishi',
    'hyundai', 'kia', 'wuling', 'chery', 'bmw', 'mercedes', 'audi',
    'volkswagen', 'ford', 'chevrolet', 'facelift', 'sedan', 'suv', 'mpv',
    'pickup', 'hatchback', 'spesifikasi mobil', 'spesifikasi motor',
    'harga mobil', 'harga motor', 'test drive', 'review mobil', 'review motor',
    'modifikasi', 'mesin mobil', 'mesin motor',
]

def adalah_konten_otomotif(teks):
    t = (teks or '').lower()
    return any(k in t for k in KATA_KUNCI_OTOMOTIF)

# V6.17.92: materi teknologi yang sering lolos filter ekonomi (data centre, dsb)
# V6.17.93: tambah karhutla/hotspot/lingkungan (false positive ekonomi)
KATA_BUKAN_EKONOMI = [
    'data centre', 'data center', 'datacenter',
    'ai data', 'ai supremacy', 'ai supremacy',
    'kecerdasan buatan data', 'pusat data ai',
    # V6.17.93: materi lingkungan/karhutla bukan ekonomi
    'karhutla', 'hotspot', 'titik panas',
    'kebakaran hutan', 'kebakaran lahan',
    'lingkungan hidup', 'kerusakan lingkungan',
    'pencemaran', 'polusi udara', 'emisi karbon',
]

def _materi_bukan_ekonomi(teks):
    """V6.17.92: cek apakah materi jelas bukan ekonomi (data centre/AI).
    V6.17.93: tambah karhutla/hotspot/lingkungan."""
    t = (teks or '').lower()
    for k in KATA_BUKAN_EKONOMI:
        if k in t:
            return k
    return ''

class BeritaLama(Exception):
    pass

STAT_SCRAPE = {'ok': 0, 'gagal': 0, 'skip': 0, 'irisan_gagal': 0,
               'gn_gagal_decode': 0, 'gn_fallback_rss': 0}
JUDUL_TERPAKAI = []
JUDUL_6JAM = []
_GAMBAR_TERPAKAI_CACHE = None

TOPIK_BESAR_GATE = [
    'tsunami', 'gempa', 'erupsi', 'gunung meletus', 'banjir bandang',
    'banjir', 'flood', 'tanah longsor', 'longsor', 'kebakaran',
    'karhutla', 'kebakaran hutan', 'kecelakaan', 'ledakan', 'tabrakan',
    'hurricane', 'typhoon', 'cyclone', 'wildfire', 'earthquake',
    'perang', 'war', 'invasi', 'missile', 'nuclear',
    'asian games', 'sea games', 'piala dunia', 'world cup',
    'olimpiade', 'olympic', 'piala asia', 'asian cup',
    'piala eropa', 'euro 202', 'copa america',
    'nba finals', 'liga champions final', 'pemilu', 'pilpres', 'pilkada',
]

def judul_topik_besar(judul):
    j = (judul or '').lower()
    return any(k in j for k in TOPIK_BESAR_GATE)

KATA_SPAM_JUDUL = ['【', '】', 'livestream', 'live stream', 'live free',
                   'tv channel', 'watch online', 'live streaming',
                   'free tv', 'kualitas hd', 'link live', 'nonton live']

def judul_spam(judul):
    j = (judul or '').lower()
    for k in KATA_SPAM_JUDUL:
        if k in j:
            return True
    return False

KATA_ALASAN_TRANSIENT = [
    'rate limit', 'timeout', 'koneksi', 'connection',
    'error sementara', 'coba lagi', 'retry',
]

# V6.17.90: alasan yang TIDAK boleh blacklist URL (transient/struktural)
# V6.17.97: tambah "materi agregator" — false positive materi panjang
# V6.17.98: tambah "tidak cocok kategori" — false positive kategori AI
KATA_ALASAN_JANGAN_BLACKLIST = [
    'materi sampah',
    'materi terlalu pendek',
    'materi tidak valid: materi terlalu pendek',
    'materi agregator',
    'materi tidak valid: materi agregator',
    # V6.17.98: judul/isi AI tidak cocok kategori (false positive AI)
    'judul/isi ai tidak cocok kategori',
    'materi tidak ada kata kunci kategori',
    'judul & isi ai tidak ada kata kunci kategori',
]

def muat_rejected_urls():
    global REJECTED_URLS_CACHE
    if REJECTED_URLS_CACHE is not None:
        return REJECTED_URLS_CACHE
    out = set()
    try:
        r = requests.get(SUPABASE_URL + '/rest/v1/rejected_urls'
                         + '?select=source_url&order=created_at.desc&limit=2000',
            headers={'apikey': SUPABASE_PUBLISHABLE,
                     'Authorization': 'Bearer ' + SUPABASE_PUBLISHABLE},
            timeout=30)
        if r.ok:
            for row in (r.json() or []):
                u = (row.get('source_url') or '').strip()
                if u:
                    out.add(u)
            print('   ' + str(len(out)) + ' URL rejected dimuat (blacklist permanen).')
        else:
            print('   Gagal muat rejected_urls: HTTP ' + str(r.status_code))
    except Exception as e:
        print('   Gagal muat rejected_urls: ' + str(e)[:60])
    REJECTED_URLS_CACHE = out
    return out

def catat_tolak_ai_token(source_url, alasan):
    if not source_url:
        return
    alasan_str = (alasan or '').strip()
    if not alasan_str:
        return
    alasan_low = alasan_str.lower()
    for k in KATA_ALASAN_TRANSIENT:
        if k in alasan_low:
            return
    # V6.17.86 + V6.17.90 + V6.17.97 + V6.17.98: jangan blacklist URL
    # kalau materi sampah / terlalu pendek / agregator / kategori false positive
    for k in KATA_ALASAN_JANGAN_BLACKLIST:
        if k in alasan_low:
            print('   (URL tidak di-blacklist — ' + k + ' transient)')
            return
    try:
        r = requests.post(SUPABASE_URL + '/rest/v1/rejected_urls',
            headers={'apikey': SUPABASE_PUBLISHABLE,
                     'Authorization': 'Bearer ' + SUPABASE_PUBLISHABLE,
                     'Content-Type': 'application/json',
                     'Prefer': 'resolution=merge-duplicates,return=minimal'},
            json={'source_url': source_url, 'alasan': alasan_str[:500]},
            timeout=30)
        if not r.ok:
            print('   Gagal catat rejected_urls: HTTP ' + str(r.status_code)
                  + ' - ' + r.text[:80])
        else:
            if REJECTED_URLS_CACHE is not None:
                REJECTED_URLS_CACHE.add(source_url)
            print('   URL dicatat ke rejected_urls: ' + source_url[:60])
    except Exception as e:
        print('   Gagal catat rejected_urls: ' + str(e)[:60])

DOMAIN_NON_BERITA = [
    'www.w3.org', 'w3.org', 'schema.org', 'ogp.me', 'purl.org', 'gstatic.com',
    'googleapis.com', 'googleusercontent.com', 'fonts.googleapis.com',
    'fonts.gstatic.com', 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'unpkg.com',
    'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com', 'tiktok.com',
    'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
    'googletagmanager.com', 'google-analytics.com', 'accounts.google.com',
    'consent.google.com', 'policies.google.com', 'support.google.com',
    'myaccount.google.com',
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
    if not re.search(r'\.(com|id|net|co|org|tv|info|news|co\.id|or\.id|go\.id|ac\.id|my\.id|sch\.id|cn|jp|kr|uk|au|sg|my|th|vn|ph)\b', low):
        return False
    if low.endswith(('.svg', '.jpg', '.jpeg', '.png', '.gif', '.webp', '.ico',
                     '.css', '.js', '.woff', '.woff2', '.ttf', '.eot')):
        return False
    return True

def _gn_decode_satu(url):
    if not url:
        return ''
    if url in _GN_DECODE_CACHE:
        return _GN_DECODE_CACHE[url]
    if not _GN_DECODER_OK:
        _GN_DECODE_CACHE[url] = ''
        return ''
    try:
        hasil = _gn_decode_many([url])
        u = (hasil or {}).get(url) or ''
        if u and GOOGLE_NEWS_HOST not in u:
            _GN_DECODE_CACHE[url] = u
            return u
    except Exception as e:
        print('       GN decode gagal: ' + str(e)[:80])
    _GN_DECODE_CACHE[url] = ''
    return ''

def resolusi_link_google(url):
    if not url or GOOGLE_NEWS_HOST not in url:
        return url
    hasil = _gn_decode_satu(url)
    if hasil:
        return hasil
    print('       GN decode GAGAL — skip artikel ini')
    STAT_SCRAPE['gn_gagal_decode'] += 1
    return ''

def _gn_id_dari_url(url):
    try:
        m = re.search(r'/articles/([A-Za-z0-9_\-]+)', url or '')
        if m:
            return m.group(1)
        m = re.search(r'/([A-Za-z0-9_\-]{30,})(?:\?|$)', url or '')
        if m:
            return m.group(1)
    except Exception:
        pass
    return ''

# V6.17.85: tambah pilihanindonesia.com
# V6.17.96: tambah rri.co.id + tarakantv.co.id (materi pendek / tidak pernah ada berita)
DOMAIN_SKIP_SCRAPE = [
    'berita.tarakankota.go.id',
    'vnexpress.net',
    'kompasiana.com',
    'mui.or.id',
    'businesstoday.com.my',
    'kabaroto.com',
    'nytimes.com',
    'premium.bisnis.com',
    'radartarakan.jawapos.com',
    'cnnindonesia.com',
    'cnbcindonesia.com',
    'pilihanindonesia.com',
    # V6.17.96: skip total (materi terlalu pendek / tidak pernah ada berita)
    'rri.co.id',
    'tarakantv.co.id',
]

def domain_skip_scrape(url):
    low = (url or '').lower()
    return any(d in low for d in DOMAIN_SKIP_SCRAPE)

def _domain_dari_url(url):
    try:
        m = re.match(r'^https?://([^/]+)', url or '')
        return m.group(1) if m else '?'
    except Exception:
        return '?'

def scrape_via_playtrafi(url):
    if not _PLAYTRAFI_OK:
        print('       Playtrafi tidak terinstall - lewati.')
        return ''
    try:
        result = _Playtrafi.crawl(url)
        teks = (result.markdown or '') if result else ''
        if not teks:
            print('       Playtrafi hasil kosong - ' + url[:60])
            return ''
        teks = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', teks)
        teks = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', teks)
        teks = re.sub(r'[#*_`>]{1,3}', ' ', teks)
        teks = re.sub(r'\s+', ' ', teks).strip()
        if len(teks) < SCRAPE_MIN_KARAKTER:
            print('       Playtrafi hasil PENDEK: ' + str(len(teks)) + ' kar - ' + url[:60])
            return ''
        return teks
    except Exception as e:
        print('       Playtrafi EXCEPTION: ' + str(e)[:80] + ' - ' + url[:60])
        return ''

# V6.17.85: decode HTML entity (&#x27;, &#39;, &hellip;, dll)
_HTML_ENTITY_MAP = {
    '&nbsp;': ' ', '&amp;': '&', '&quot;': '"', '&#39;': "'",
    '&apos;': "'", '&ldquo;': '"', '&rdquo;': '"',
    '&lsquo;': "'", '&rsquo;': "'", '&mdash;': '-', '&ndash;': '-',
    '&hellip;': '…', '&laquo;': '«', '&raquo;': '»',
    '&times;': '×', '&divide;': '÷', '&bull;': '•',
    '&middot;': '·', '&trade;': '™', '&copy;': '©', '&reg;': '®',
    '&deg;': '°', '&plusmn;': '±', '&frac12;': '½',
    '&frac14;': '¼', '&frac34;': '¾', '&sup2;': '²', '&sup3;': '³',
    '&euro;': '€', '&pound;': '£', '&yen;': '¥', '&cent;': '¢',
}

def _decode_html_entity(teks):
    if not teks:
        return teks
    t = teks
    # Decode map entity umum
    for ent, kar in _HTML_ENTITY_MAP.items():
        t = t.replace(ent, kar)
    # Decode numeric entity: &#123; atau &#x1F600;
    def _num_repl(m):
        try:
            kode = int(m.group(1)) if m.group(1).isdigit() else int(m.group(1), 16)
            if kode < 32 or kode > 0x10FFFF:
                return ' '
            return chr(kode)
        except Exception:
            return ' '
    t = re.sub(r'&#(\d+);', lambda m: _num_repl(re.match(r'&#(\d+);', m.group(0))), t)
    t = re.sub(r'&#x([0-9a-fA-F]+);',
               lambda m: _num_repl(re.match(r'&#x([0-9a-fA-F]+);', m.group(0))), t)
    return t

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
    teks = _decode_html_entity(teks)
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
    return re.sub(r'\s+', ' ', ' '.join(baris_ok)).strip()[:2500]

def scrape_artikel(url, judul_debug=''):
    if not url:
        return ''
    if url in _CACHE_SCRAPE:
        print('       Scraping cache hit - ' + url[:60])
        return _CACHE_SCRAPE[url]
    if domain_skip_scrape(url):
        STAT_SCRAPE['skip'] += 1
        print('       Skip scraping (domain 403 konsisten) - ' + url[:60])
        _CACHE_SCRAPE[url] = ''
        return ''
    url_asli = resolusi_link_google(url)
    if not url_asli:
        print('       Resolusi GN gagal — fallback RSS summary')
        STAT_SCRAPE['gn_fallback_rss'] += 1
        _CACHE_SCRAPE[url] = ''
        return ''
    if GOOGLE_NEWS_HOST in url_asli:
        print('       Hasil resolusi masih Google News — fallback RSS summary')
        STAT_SCRAPE['gn_fallback_rss'] += 1
        _CACHE_SCRAPE[url] = ''
        return ''
    # V6.17.85: cek domain skip SETELAH resolusi GN
    if domain_skip_scrape(url_asli):
        STAT_SCRAPE['skip'] += 1
        print('       Skip scraping (domain 403 konsisten, post-resolve) - ' + url_asli[:60])
        _CACHE_SCRAPE[url] = ''
        return ''
    if not _url_valid_berita(url_asli):
        print('       URL hasil resolusi tidak valid (non-berita) - skip: ' + url_asli[:60])
        STAT_SCRAPE['skip'] += 1
        _CACHE_SCRAPE[url] = ''
        return ''
    if DEBUG_SCRAPE:
        print('       [DEBUG] URL final: ' + url_asli[:100])
        print('       [DEBUG] Domain: ' + _domain_dari_url(url_asli))
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
                _CACHE_SCRAPE[url] = hasil
                return hasil
        print('       Langsung scrape pendek: ' + str(len(hasil)) + ' kar - ' + url_asli[:60])
    except Exception as e:
        print('       Langsung scrape gagal: ' + str(e)[:60])
    hasil = scrape_via_playtrafi(url_asli)
    if hasil:
        _CACHE_SCRAPE[url] = hasil
        return hasil
    _CACHE_SCRAPE[url] = ''
    return ''

def _potong_materi(teks, maks=MATERI_MAKS_KARAKTER):
    if not teks or len(teks) <= maks:
        return teks
    potong = teks[:maks]
    pos = max(potong.rfind('. '), potong.rfind('! '), potong.rfind('? '))
    if pos > maks * 0.7:
        return potong[:pos + 1].strip()
    return potong.strip()

def ambil_materi_kaya(c):
    scraped = scrape_artikel(c.get('link', ''), c.get('title', ''))
    if scraped and len(scraped) >= SCRAPE_MIN_KARAKTER:
        STAT_SCRAPE['ok'] += 1
        panjang_asli = len(scraped)
        scraped = _potong_materi(scraped, MATERI_MAKS_KARAKTER)
        print('       Scraping artikel asli: ' + str(panjang_asli)
              + ' kar → potong ' + str(len(scraped)) + ' kar')
        if DEBUG_SCRAPE:
            print('       [DEBUG] Judul asli: ' + (c.get('title') or '')[:80])
            print('       [DEBUG] Materi 250 kar pertama: ' + scraped[:250])
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
        try:
            ce = entry.get('content_encoded') or ''
            if ce and len(ce) > len(konten_rss):
                konten_rss = ce
        except Exception:
            pass
        try:
            sd = entry.get('summary_detail') or {}
            sv = sd.get('value') or ''
            if sv and len(sv) > len(konten_rss):
                konten_rss = sv
        except Exception:
            pass
        konten_rss = clean(konten_rss, 2500)
        if konten_rss and len(konten_rss) > len(s):
            potongan.append('Konten RSS: ' + konten_rss)
    except Exception:
        pass
    if not potongan:
        print('       Scraping gagal & RSS kosong - pakai summary minimal')
        return c.get('summary', ''), False
    gabung = '\n\n'.join(potongan)
    panjang_asli = len(gabung)
    gabung = _potong_materi(gabung, MATERI_MAKS_KARAKTER)
    print('       Scraping gagal/pendek - pakai gabungan title+RSS ('
          + str(panjang_asli) + ' → ' + str(len(gabung)) + ' kar)')
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

KAMUS_PERUSAHAAN_GLOBAL = [
    'infineon', 'toyota', 'tesla', 'apple', 'google', 'microsoft', 'samsung',
    'huawei', 'xiaomi', 'nvidia', 'intel', 'boeing', 'airbus', 'amazon',
    'meta', 'facebook', 'netflix', 'openai', 'anthropic', 'bytedance', 'tiktok',
    'sony', 'lg', 'panasonic', 'toshiba', 'sharp', 'canon', 'nikon', 'fujifilm',
    'bmw', 'mercedes', 'volkswagen', 'audi', 'porsche', 'ferrari', 'lamborghini',
    'hyundai', 'kia', 'nissan', 'honda', 'suzuki', 'mazda', 'mitsubishi',
    'subaru', 'mclaren', 'bentley', 'rolls royce', 'jaguar', 'land rover',
    'volvo', 'peugeot', 'renault', 'citroen', 'fiat', 'alfa romeo', 'maserati',
    'chevrolet', 'ford', 'gmc', 'cadillac', 'chrysler', 'dodge', 'jeep',
    'wuling', 'chery', 'geely', 'byd', 'nio', 'xpeng', 'li auto', 'great wall',
    'renesas', 'tsmc', 'qualcomm', 'broadcom', 'amd', 'arm', 'asml', 'micron',
    'texas instruments', 'stmicroelectronics', 'infineon technologies',
    'bosch', 'continental', 'denso', 'zf', 'magna', 'aptiv', 'valeo',
    'paypal', 'stripe', 'visa', 'mastercard', 'square', 'shopify', 'uber',
    'airbnb', 'spotify', 'zoom', 'slack', 'salesforce', 'oracle', 'sap', 'ibm',
    'cisco', 'dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'razer',
    'goldman sachs', 'morgan stanley', 'jp morgan', 'jpmorgan', 'citigroup',
    'bank of america', 'wells fargo', 'hsbc', 'barclays', 'deutsche bank',
    'ubs', 'credit suisse', 'bnp paribas', 'santander', 'standard chartered',
    'exxon', 'chevron', 'shell', 'bp', 'total', 'petronas', 'aramco',
    'nestle', 'unilever', 'pepsi', 'coca cola', 'cocacola', 'mcdonald',
    'starbucks', 'kfc', 'pizza hut', 'domino', 'burger king',
    'pfizer', 'moderna', 'biontech', 'astrazeneca', 'novartis', 'roche',
    'johnson', 'merck', 'bayer', 'sanofi', 'gsk', 'sinovac', 'sinopharm',
]

def _ada_nama_diri_judul(judul):
    if not judul:
        return False
    j_low = judul.lower()
    for p in KAMUS_PERUSAHAAN_GLOBAL:
        if len(p.split()) == 1:
            if re.search(r'\b' + re.escape(p) + r'\b', j_low):
                return True
        else:
            if p in j_low:
                return True
    pola = re.compile(r'\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b')
    skip = ['jakarta', 'bandung', 'surabaya', 'medan', 'semarang', 'makassar',
            'balikpapan', 'samarinda', 'tarakan', 'kaltara', 'kalimantan',
            'sumatera', 'jawa', 'sulawesi', 'papua', 'bali', 'nusa',
            'pemerintah', 'menteri', 'presiden', 'gubernur', 'bupati',
            'walikota', 'wakil', 'kepala', 'ketua', 'komandan',
            'sekretaris', 'direktur', 'pemkot', 'pemkab', 'pemprov',
            'polres', 'kodim', 'bandara', 'kota', 'kabupaten',
            'provinsi', 'dinas', 'badan', 'kantor', 'komisi',
            'januari', 'februari', 'maret', 'april', 'mei', 'juni',
            'juli', 'agustus', 'september', 'oktober', 'november',
            'desember', 'senin', 'selasa', 'rabu', 'kamis', 'jumat',
            'sabtu', 'minggu', 'breaking', 'news']
    for m in pola.finditer(judul):
        k1 = m.group(1).lower()
        k2 = m.group(2).lower()
        if k1 in skip or k2 in skip:
            continue
        return True
    m1 = re.match(r'^([A-Z][a-z]{4,})\b', judul.strip())
    if m1:
        kata = m1.group(1).lower()
        if kata not in skip and kata not in KATA_STOP_DOBEL:
            if kata not in ['presiden', 'menteri', 'pemerintah', 'indonesia',
                            'jakarta', 'breaking', 'update', 'hasil', 'resmi',
                            'kementerian', 'polisi', 'kepala', 'jenderal']:
                return True
    return False

# ══════════════════════════════════════════════════════
# V6.17.93: dobel-6jam LONGGAR — jangan anggap dobel kalau topik beda
# (Prabowo proyek hilirisasi ≠ Prabowo jamin investasi)
# ══════════════════════════════════════════════════════

KATA_TOPIK_BEDA_DOBEL6JAM = [
    'hilirisasi', 'luncurkan', 'resmikan', 'groundbreaking', 'investasi',
    'jamin', 'keamanan', 'harga', 'pasar', 'saham', 'ekspor', 'impor',
    'subsidi', 'anggaran', 'apbn', 'pajak',
]

def _topik_dobel6jam_nyata(judul_a, judul_b, irisan):
    """V6.17.93: cek apakah irisan 3 kata benar-benar topik sama.
    Kalau hanya sama kata umum (prabowo, presiden, indonesia) → bukan dobel."""
    # Kalau irisan hanya berisi kata umum (nama tokoh/tempat) → bukan dobel
    kata_umum_dobel = {
        'prabowo', 'presiden', 'indonesia', 'jakarta', 'menteri',
        'gubernur', 'bupati', 'walikota', 'jokowi', 'gibran',
    }
    irisan_inti = irisan - kata_umum_dobel
    if len(irisan_inti) < 2:
        return False
    return True

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
            if DOBEL_6JAM_BUTUH_NAMA:
                if _ada_nama_diri_judul(judul) or _ada_nama_diri_judul(t):
                    # V6.17.93: longgarkan — cek topik dobel NYATA
                    irisan = ki & kt
                    if not _topik_dobel6jam_nyata(judul, t, irisan):
                        continue
                    return True
            else:
                irisan = ki & kt
                if not _topik_dobel6jam_nyata(judul, t, irisan):
                    continue
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
        rows = rest_get('?select=title,created_at&order=created_at.desc&limit=500')
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
    return """Kamu AI Editor KramaNews Indonesia. TUGAS: Tulis berita dari materi yang sudah lolos filter. Materi SUDAH BERSIH — jangan tolak kecuali fatal.

ATURAN EMAS — FAKTA vs NARASI (WAJIB, SEMUA KATEGORI):
- FAKTA = WAJIB SAMA dengan materi (bukan jiplak, ini kebenaran).
- NARASI = WAJIB DIUBAH dengan kalimatmu sendiri.

FAKTA SAH & LEGAL DIAMBIL UTUH:
- Nama orang (nara sumber, pejabat, tokoh, warga) → SAH ambil utuh.
- Gelar (Drs., Ir., S.T., S.H., M.Si., M.M., Dr., Prof., M.Pd.I., dll) → SAH ambil utuh.
- Jabatan (Bupati, Wali Kota, Kapolres, Menteri, Direktur, dll) → SAH ambil utuh.
- Pangkat TNI/Polri (Jenderal, AKBP, AKP, Kombes, dll) → SAH ambil utuh.
- Titel (H., Hj., R.A., dll) → SAH ambil utuh.
- Nama lokasi/tempat → SAH ambil utuh.
- Semua fakta di atas TIDAK PERLU diubah. TIDAK PERLU diparafrase.

FAKTA WAJIB-KALAU-ADA (kalau materi ada, WAJIB tulis persis):
1. Nama pejabat + gelar + jabatan
2. Nama orang awam
3. Nama perusahaan/produk/merek
4. Nama lembaga/instansi
5. Nama dokter/peneliti/atlet/tim
6. Nama tempat/spesifik

FAKTA WAJIB-MUTLAK (harus ada di berita):
1. LOKASI — minimal kota
2. WAKTU — minimal tanggal
3. ANGKA — kalau materi ada

YANG DILARANG (kalau materi TIDAK ada):
- DILARANG mengarang nama pejabat, perusahaan, produk, lokasi spesifik.
- Kalau materi tidak ada nama → tulis "Pemkab X" saja.

NARASI — WAJIB DIUBAH:
- Kalimat wajib beda dengan materi.
- DILARANG 25+ kata berurutan sama materi (kecuali fakta di atas).
- Sinonim: "mengatakan" → "menuturkan/ujar".

KALIMAT TERLARANG (JANGAN PAKAI):
- "Menurut informasi yang dihimpun"
- "Kejadian itu berlangsung cepat"
- "Menjadi pengingat bagi masyarakat"
- "Peran aktif warga dinilai efektif"
- "Warga diimbau tetap waspada" (kecuali materi sebut)
- "Koordinasi lintas instansi tetap berjalan" (kecuali materi sebut)

WAJIB KONKRET — JANGAN UMUM:
- Sebut nama pejabat (kalau ada di materi).
- Sebut lokasi spesifik.
- Sebut angka konkret.
- Sebut kronologi jelas: siapa, apa, di mana, kapan, mengapa.

ATURAN NAMA PEJABAT (SANGAT PENTING — PELANGGARAN = TOLAK):
- WAJIB tulis NAMA PEJABAT dalam format: JABATAN + NAMA LENGKAP + GELAR.
- Contoh BENAR: "Wali Kota Tarakan Drs. H. Khairul, M.Si. menyerahkan..."
- DILARANG sebut nama orang TANPA jabatan.

ATURAN TNI/POLRI (WAJIB):
- Selalu sebut: PANGKAT + NAMA + JABATAN.

ATURAN GELAR AKADEMIK (WAJIB):
- Kalau materi memuat gelar → WAJIB tulis persis.

NAMA LEMBAGA ASING: JANGAN diterjemahkan.

WAKTU:
- Hari ini: """ + k['hari_ini'] + """. Tahun: """ + k['tahun'] + """.
- DILARANG "belum dikonfirmasi waktu".

DATELINE (SANGAT PENTING):
- WAJIB KOTA, PROVINSI spesifik (bukan cuma "INDONESIA").
- Contoh: "JAKARTA, DKI JAKARTA - ", "TARAKAN, KALIMANTAN UTARA - ",
  "LONDON, INGGRIS - ".
- Kalau materi tidak sebut kota → pakai ibu kota.

DATELINE EVENT BESAR (WAJIB):
- Event besar (Asian Games, SEA Games, Piala Dunia, Olimpiade) → DATELINE WAJIB kota penyelenggara + negara.
- Asian Games 2026 → "AICHI-NAGOYA, JEPANG - "
- SEA Games 2026 → "BANGKOK, THAILAND - "

PERSEN: selalu simbol % ("95%").

KATEGORI (WAJIB TEPAT):
- nasional: pemerintah pusat, DPR, presiden, menteri, haji/umroh/agama, pendidikan, sosial.
- daerah: peristiwa lokal kota/kabupaten Indonesia.
- internasional: luar negeri, PBB, ASEAN, event besar di luar negeri.
- ekonomi: IHSG, kurs, saham, BI, OJK, UMKM, bisnis, ekonomi dunia, EKSPOR, IMPOR, PERDAGANGAN.
- olahraga: sepak bola, basket, badminton, voli, tenis, MotoGP, F1.
- teknologi: gadget, AI, aplikasi, internet, startup, keamanan digital.
- otomotif: mobil, motor, kendaraan listrik, spare part, modifikasi.
- kesehatan: penyakit, gizi, obat, dokter, mental health.

EKONOMI — DEFINISI SANGAT LUAS (WAJIB):
- EKONOMI mencakup: IHSG, kurs, saham, BI, OJK, UMKM, bisnis, ekonomi dunia, EKSPOR, IMPOR, PERDAGANGAN, PERTUMBUHAN EKONOMI.
- EKONOMI JUGA mencakup (JANGAN TOLAK):
  * Properti, perumahan, housing, real estate
  * IPO, merger, akuisisi, valuasi, pendanaan, investasi
  * Kunjungan dagang, kerja sama dagang, delegasi ekonomi
  * Pasar, harga, komoditas, obligasi
  * Sektor industri, manufaktur, pabrik, produksi
  * Perbankan, kredit, pinjaman, asuransi, fintech
  * Perusahaan naik/turun/rugi/ekspansi/PHK
  * Tambang, litium, nikel, baterai, smelter, mining
  * Pertumbuhan ekonomi China/USA/Jepang/Korsel/India/Vietnam/Eropa
  * Fed, ECB, BOJ, BOE, PBOC
  * WTO, IMF, World Bank, ADB, G20, G7, BRICS, APEC
- KUNJUNGAN MENTERI LUAR NEGERI / DIPLOMATIK yang isinya ekonomi → TETAP EKONOMI.

JUDUL EKONOMI — WAJIB MEMUAT KATA EKONOMI:
- JUDUL WAJIB memuat minimal 1 kata ekonomi.

JANGAN SALAH KATEGORI:
- Haji/umroh/agama → nasional (BUKAN olahraga).
- Pendidikan/sekolah → nasional (BUKAN olahraga).
- Pajak/anggaran/bansos → ekonomi/nasional.
- Kesehatan/vaksin/penyakit → kesehatan.
- "hasil", "skor", "klasemen" TIDAK cukup untuk olahraga.
- Kontes/kecantikan (Miss, pageant) → BUKAN nasional/daerah.
- Jadwal transportasi (kapal, ferry) → BUKAN daerah.

PENTING — JANGAN TOLAK BERLEBIHAN:
- JANGAN tolak materi hanya karena ada 1 kata "politik", "ekonomi", "kepolisian".
- Ekspor/impor/perdagangan/pendapatan negara → TETAP ekonomi.
- Perusahaan naik peringkat/valuasi/IPO → TETAP ekonomi.
- Properti/perumahan/housing → TETAP ekonomi.
- Kunjungan dagang/kerja sama ekonomi → TETAP ekonomi.
- Tambang/mining/baterai/litium → TETAP ekonomi.
- HANYA tolak kalau materi JELAS tentang kategori yang SALAH.

TOLAK — HANYA kalau fatal. WAJIB tulis alasan tolak DETIL (1-2 kata tambahan setelah titik dua). Contoh format:
{"tolak": "tidak cocok kategori: materi kontes"}
{"tolak": "tidak cocok kategori: materi pendidikan"}
{"tolak": "tidak cocok kategori: materi negara asing"}
{"tolak": "materi tidak nyambung judul"}
{"tolak": "materi tidak tersedia"}

Kriteria FATAL (boleh tolak):
1. Materi benar-benar tidak ada (kosong).
2. Materi tidak nyambung judul (topik beda jauh).
3. Materi palsu/spam (iklan, judi, dll).
4. Materi JELAS tentang kategori yang SALAH.

GAMBAR (deskripsi_gambar): 3-6 kata kunci Inggris.
DILARANG: hewan, tempat ibadah, alas kaki, insiden-korban.
WAJIB sesuai topik berita.

JUDUL: maks 10 kata. Harus mencerminkan isi — JANGAN clickbait.

FORMAT JAWABAN - HANYA JSON valid:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2", "ringkasan": "...",
 "kategori": "nasional|daerah|internasional|ekonomi|olahraga|teknologi|otomotif|kesehatan",
 "deskripsi_gambar": "visual keywords",
 "waktu_kejadian": "Hari (Tanggal Bulan """ + k['tahun'] + """)"}
"""

# AKHIR PART 2
# PART 3A-1 - EDGE CALL + REST + STATE + GAMBAR + VALIDATOR + KATA_KUNCI_KATEGORI + MATERI_COCOK + KANDIDAT + COLLECT + MATCH + DOBEL_DATELINE

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
    rows = rest_get('?select=source_url,created_at&order=created_at.desc&limit=500')
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

MATERI_MIN_KARAKTER_RSS = 120
MATERI_MIN_KARAKTER_RSS_NASIONAL = 300
MATERI_MIN_KARAKTER_RSS_DAERAH    = 250
# V6.17.85: threshold breaking 100 → 200 (materi 158 kar terlalu tipis)
MATERI_MIN_KARAKTER_BREAKING = 200
MATERI_MIN_KARAKTER_ASEAN = 600

# V6.17.98: RSS tipis dari DOMAIN_SKIP_SCRAPE → buang di pre-filter
MATERI_RSS_SKIP_TIPIS = 200

# V6.17.86: deteksi materi sampah anti-bot/JS block
def _materi_sampah(teks):
    """
    V6.17.86: Cek apakah materi memuat frasa anti-bot/JS block.
    Kalau ≥2 frasa → materi sampah → tolak (tapi JANGAN blacklist URL).
    """
    if not teks:
        return False
    t = teks.lower()
    hit = sum(1 for k in KATA_MATERI_SAMPAH if k in t)
    return hit >= 2

def _materi_dominan_url(teks):
    if not teks:
        return False
    url_chars = sum(len(m.group(0)) for m in re.finditer(r'https?://\S+', teks))
    if len(teks) < 100:
        return False
    rasio = url_chars / len(teks)
    if rasio >= 0.30:
        return True
    low = teks.lower()
    frasa_link = ['baca juga', 'baca selengkapnya', 'lihat juga', 'simak juga',
                  'klik di sini', 'baca di sini', 'selengkapnya di']
    hit = sum(1 for f in frasa_link if f in low)
    if hit >= 3:
        return True
    return False

def _materi_nyambung_judul(judul, materi, min_irisan=2):
    if not judul or not materi:
        return False, 'judul/materi kosong'
    kata_judul = set(k for k in re.findall(r'[a-z]{3,}', judul.lower())
                     if k not in KATA_STOP_DOBEL)
    if not kata_judul:
        return True, ''
    if len(judul.split()) < 6:
        min_irisan = 1
    kata_materi = set(re.findall(r'[a-z]{3,}', materi.lower()))
    irisan = kata_judul & kata_materi
    if len(irisan) < min_irisan:
        return False, ('judul-materi tidak nyambung (irisan ' + str(len(irisan))
                       + ' < ' + str(min_irisan) + '): ' + str(sorted(irisan)[:5])
                       + ' | kata judul: ' + str(sorted(list(kata_judul))[:8]))
    return True, ''

# ══════════════════════════════════════════════════════
# V6.17.97: DETEKSI MATERI AGREGATOR — DIPERKETAT
# False positive materi panjang (2500+ kar) karena judul dobel di awal
# ══════════════════════════════════════════════════════

# Frasa yang menandakan materi BENAR-BENAR agregator (banyak judul berita campur)
FRASA_AGREGATOR_KUAT = [
    '86 flash', '86flash', 'flash !', 'flash!',
    'headline news', 'top news', 'berita terkini hari ini',
    'update terkini berita', 'kumpulan berita', 'daftar berita',
    'berita pilihan', 'berita utama', 'berita populer',
    'berita terpopuler', 'berita terbaru hari ini',
    'index berita', 'indeks berita', 'berita pagi', 'berita siang',
    'berita sore', 'berita malam', 'selamat pagi indonesia',
]

# Frasa navigasi portal yang menandakan agregator / homepage
FRASA_NAVIGASI_PORTAL = [
    'home news', 'home politik', 'home ekonomi', 'home olahraga',
    'home teknologi', 'home hiburan', 'home lifestyle',
    'news politics', 'news economy', 'news sports',
    'beranda berita', 'beranda politik', 'beranda ekonomi',
]

def _materi_agregator(teks):
    """
    V6.17.97: cek apakah materi BENAR-BENAR agregator (banyak judul campur).
    DIPERKETAT — hindari false positive materi panjang (2500+ kar)
    yang cuma ada judul dobel + nama portal di awal.

    Return (True, alasan) kalau agregator, (False, '') kalau OK.
    """
    if not teks:
        return False, ''
    t = teks.lower()
    panjang = len(teks)

    # 1. Materi pendek → jangan pakai cek agregator (biar threshold yang urus)
    if panjang < 500:
        return False, ''

    # 2. Cek frasa agregator KUAT — kalau ≥2 frasa, baru tolak
    hit_kuat = sum(1 for f in FRASA_AGREGATOR_KUAT if f in t)
    if hit_kuat >= 2:
        return True, ('materi agregator (frasa khas agregator: ' +
                      str(hit_kuat) + ' hit)')

    # 3. Cek frasa navigasi portal — kalau ≥3 frasa, baru tolak
    hit_nav = sum(1 for f in FRASA_NAVIGASI_PORTAL if f in t)
    if hit_nav >= 3:
        return True, ('materi agregator (frasa navigasi portal: ' +
                      str(hit_nav) + ' hit)')

    # 4. Cek rasio judul: paragraf pendek berulang (banyak kalimat pendek
    #    yang diakhiri judul → 10+ kalimat < 40 kar dalam 500 kar pertama)
    potongan_awal = teks[:600]
    kalimat_pendek = len(re.findall(r'[^.!?]{20,50}[.!?]', potongan_awal))
    if kalimat_pendek >= 6 and panjang < 800:
        # Cuma tolak kalau materi pendek (bukan artikel asli panjang)
        return True, ('materi agregator (banyak kalimat pendek: ' +
                      str(kalimat_pendek) + ')')

    return False, ''

def _materi_valid(judul, materi, dari_scraping=True, kategori=''):
    if not materi:
        return False, 'materi kosong'
    # V6.17.86: cek materi sampah (anti-bot/JS block) SEBELUM cek panjang
    if _materi_sampah(materi):
        return False, 'materi sampah (anti-bot/JS block)'
    if kategori == 'breaking':
        min_kar = MATERI_MIN_KARAKTER_BREAKING
    elif kategori == 'internasional_asean':
        min_kar = MATERI_MIN_KARAKTER_ASEAN
    elif kategori == 'nasional':
        if dari_scraping:
            min_kar = MATERI_MIN_KARAKTER
        else:
            min_kar = MATERI_MIN_KARAKTER_RSS_NASIONAL
    elif kategori == 'daerah':
        if dari_scraping:
            min_kar = MATERI_MIN_KARAKTER
        else:
            min_kar = MATERI_MIN_KARAKTER_RSS_DAERAH
    elif dari_scraping:
        min_kar = MATERI_MIN_KARAKTER
    else:
        min_kar = MATERI_MIN_KARAKTER_RSS
    if len(materi) < min_kar:
        return False, ('materi terlalu pendek (' + str(len(materi)) + ' < '
                       + str(min_kar) + ', dari_scraping=' + str(dari_scraping)
                       + ', kategori=' + str(kategori) + ')')
    # V6.17.97: cek agregator DIPERKETAT — hanya tolak agregator asli
    agr, alasan_agr = _materi_agregator(materi)
    if agr:
        return False, alasan_agr
    if _materi_dominan_url(materi):
        return False, 'materi dominan URL/link (bukan artikel asli)'
    ok, alasan = _materi_nyambung_judul(judul, materi)
    if not ok:
        return False, alasan
    return True, ''

KATA_FEATURE_OPINI = [
    'editorial', 'opini:', 'analisis:', 'sorotan', 'potret', 'foto-foto',
    'galeri', 'in pictures', 'photos:', 'images:', 'see photos',
    'in photos', 'feature:', 'commentary', 'opinion:', 'analysis:',
    'review:', 'wawancara:', 'interview:',
]

STOPWORDS_DOBEL = set('yang dan di ke dari untuk pada dengan dalam ini itu akan telah '
                      'sudah oleh sebagai ada adalah kata ujar bilang menurut juga '
                      'lebih masih hanya setelah sebelum sekitar bisa dapat tidak '
                      'akan sudah karena jika agar para kami mereka the and for with '
                      'from that this have will been are was were their they about'.split())

def _kata_kunci_teks(teks):
    kata = re.findall(r'[a-z]{4,}', (teks or '').lower())
    return set(k for k in kata if k not in STOPWORDS_DOBEL)

def _kandidat_topik_nyambung(judul, summary):
    if not judul or not summary:
        return False, 'judul/materi kosong'
    kata_judul = _kata_kunci_teks(judul)
    kata_materi = _kata_kunci_teks(summary)
    if not kata_judul:
        return False, 'judul tidak ada kata kunci'
    if len(summary) < 150:
        return True, ''
    irisan = kata_judul & kata_materi
    if len(irisan) < 1:
        return False, 'judul & materi tidak nyambung (irisan 0)'
    return True, ''

KATA_KUNCI_KATEGORI = {
    'nasional': ['pemerintah', 'presiden', 'menteri', 'dpr', 'kementerian',
                 'jakarta', 'indonesia', 'kebijakan', 'program', 'nasional',
                 'kpk', 'korupsi', 'hukum', 'sidang', 'pengadilan',
                 'polisi', 'tni', 'polri', 'pemilu', 'partai', 'dprd',
                 'anggaran', 'apbn', 'subsidi', 'bansos', 'pajak',
                 'pertahanan', 'kemhan', 'kemenhan', 'badan', 'debat',
                 'pbb', 'ham', 'diplomasi', 'luar negeri', 'menteri luar',
                 'mbg', 'sppg', 'dapur', 'makan bergizi', 'gizi',
                 'bgn', 'ketahanan pangan', 'bulog', 'koperasi', 'kdmp',
                 'merah putih', 'aturan', 'penjaminan', 'dana'],
    'daerah': ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
               'tana tidung', 'tanjung selor', 'sebatik', 'juata', 'sesayap',
               'kota', 'kabupaten', 'pemkot', 'pemkab', 'bupati', 'walikota',
               'dprd', 'polres', 'kodim', 'kelurahan', 'kecamatan', 'desa',
               'provinsi', 'gubernur', 'camat', 'lurah', 'rt', 'rw',
               'kppn', 'kpp', 'satker', 'ikpa', 'narkotika', 'narkoba',
               'terjaring', 'kasus', 'pembiayaan', 'penerimaan',
               'sekolah rakyat', 'gotong royong', 'kerja bakti',
               'jembatan', 'jalan', 'jalan raya', 'aspal', 'pengecoran',
               'pembangunan', 'infrastruktur', 'fasilitas', 'gedung',
               'kantor', 'pasar', 'terminal', 'pelabuhan', 'bandara',
               'pdam', 'air bersih', 'sanitasi', 'drainase',
               'banjir', 'normalisasi', 'sungai', 'taman',
               'trotoar', 'lampu', 'penerangan', 'sampah', 'tps',
               'posyandu', 'puskesmas', 'rumah sakit daerah', 'sekolah',
               'masjid', 'gereja', 'vihara', 'pura', 'lapangan',
               'olahraga daerah', 'kebudayaan', 'wisata daerah',
               'umkm daerah', 'pasar rakyat', 'retribusi', 'pajak daerah',
               'apbd', 'rapbd', 'musrenbang', 'perda',
               'kades', 'bpd', 'karang taruna',
               'pkk', 'dasawisma', 'bumdes', 'bumn daerah',
               'perumda', 'perusda', 'bank daerah',
               'ketahanan pangan', 'pertanian', 'perikanan', 'nelayan',
               'petani', 'tambak', 'sawah', 'perkebunan', 'ternak',
               'pajak restoran', 'pajak hotel', 'pajak reklame', 'pajak bumi',
               'pbb', 'bphtb', 'izin usaha', 'perizinan', 'izin mendirikan',
               'imb', 'izin lingkungan', 'reklame', 'retribusi daerah',
               'apbdes', 'alokasi dana desa', 'dana desa', 'add',
               'pilkades', 'pemilihan kades', 'perangkat desa',
               'perwali', 'perbup', 'peraturan bupati', 'peraturan walikota',
               'rutilahu', 'bedah rumah', 'bantuan renovasi',
               'bantuan sosial daerah', 'bansos daerah', 'pkh daerah',
               'dinas kesehatan', 'dinas pendidikan', 'dinas sosial',
               'dinas pertanian', 'dinas perikanan', 'dinas pu', 'dinas perhubungan',
               'satpol pp', 'damkar', 'bpbd daerah', 'tagana daerah',
               'kecamatan', 'kelurahan', 'kampung', 'dusun', 'rukun tetangga',
               'ubt', 'unmul', 'unhas', 'unpad', 'ugm', 'ui', 'itb', 'undip',
               'unair', 'unib', 'unram', 'untan', 'unlam', 'unsoed',
               'kpwbi', 'bi kaltara', 'ojk kaltara', 'bea cukai',
               'imigrasi', 'karantina', 'bpn', 'atr/bpn', 'perumdam',
               'pln up3', 'pln uid', 'pdam tirta', 'rsud', 'rsu',
               'poltekkes', 'poltek', 'smk negeri', 'sman', 'smpn',
               'fakultas', 'kampus daerah',
               'santri', 'sholawat', 'gebyar', 'pesantren', 'majelis taklim',
               'pengajian', 'tahlilan', 'yasinan', 'maulid', 'rajaban',
               'halal bihalal', 'takbir keliling', 'pawai obor'],
    'internasional': ['amerika', 'rusia', 'china', 'jepang', 'korea',
                      'eropa', 'inggris', 'jerman', 'perancis', 'italia',
                      'timur tengah', 'israel', 'palestina', 'iran', 'irak',
                      'ukraina', 'pbb', 'nato', 'who',
                      'london', 'washington', 'paris', 'berlin',
                      'moskow', 'tokyo', 'beijing', 'seoul', 'australia',
                      'kanada', 'meksiko', 'brasil', 'india', 'global',
                      'kamboja', 'cambodia', 'thailand', 'vietnam',
                      'filipina', 'singapura', 'malaysia', 'myanmar',
                      'laos', 'brunei', 'timor leste',
                      'gempa', 'earthquake', 'seattle', 'banjir', 'flood',
                      'perang', 'war', 'invasi', 'missile', 'nuclear'],
    'internasional_asean': ['asean', 'malaysia', 'thailand', 'vietnam',
                            'filipina', 'singapura', 'myanmar', 'kamboja',
                            'laos', 'brunei', 'timor leste', 'bangkok',
                            'manila', 'kuala lumpur', 'hanoi', 'jakarta'],
    'internasional_tt': ['timur tengah', 'gaza', 'israel', 'palestina',
                         'iran', 'irak', 'suriah', 'saudi', 'yaman',
                         'uni emirat', 'qatar', 'kuwait', 'libanon',
                         'jordan', 'turki', 'mesir', 'middle east',
                         'tehran', 'beirut', 'damaskus',
                         'hamas', 'hezbollah', 'idf', 'netanyahu',
                         'west bank', 'teheran', 'lebanon'],
    'ekonomi': ['ihsg', 'idx', 'bursa', 'saham', 'bank', 'rupiah', 'dolar',
                'inflasi', 'pajak', 'apbn', 'ekspor', 'impor', 'investasi',
                'umkm', 'startup', 'kredit', 'utang', 'defisit', 'surplus',
                'harga', 'pasar', 'konsumen', 'pedagang', 'pertanian',
                'petani', 'industri', 'perdagangan', 'bumn', 'koperasi',
                'keuangan', 'fiskal', 'moneter', 'daya beli',
                'ventures', 'asia tenggara',
                'malaysia', 'china', 'singapura', 'fintech', 'e-commerce',
                'economy', 'economic', 'trade', 'growth', 'gdp', 'factory',
                'exports', 'imports', 'tariff', 'sanction', 'stimulus',
                'resilient', 'domestic', 'grain', 'supply',
                'ojk', 'edukasi keuangan', 'literasi keuangan',
                'investasi', 'reksa dana', 'obligasi', 'deposito'],
    'olahraga': ['bola', 'sepak', 'basket', 'voli', 'badminton', 'tenis',
                 'motogp', 'f1', 'liga', 'piala', 'timnas', 'atlet',
                 'pemain', 'klub', 'pertandingan', 'laga', 'gol', 'skor',
                 'klasemen', 'stadion', 'nba', 'ibl', 'bwf', 'fivb',
                 'jadwal', 'fifa', 'sea games', 'hasil', 'pelatih',
                 'kualifikasi', 'wisata olahraga', 'potensi',
                 'medali', 'perolehan', 'asian games',
                 'olimpiade', 'olympic', 'barcelona', 'real madrid',
                 'manchester', 'liverpool', 'chelsea', 'arsenal',
                 'newcastle', 'aston villa', 'juventus', 'inter milan',
                 'ac milan', 'bayern', 'dortmund', 'psg', 'marseille',
                 'timberwolves', 'lakers', 'celtics', 'warriors'],
    'teknologi': ['teknologi', 'gadget', 'smartphone', 'aplikasi', 'internet',
                  'ai', 'kecerdasan buatan', 'startup', 'digital', 'data',
                  'komputer', 'laptop', 'google', 'apple', 'microsoft',
                  'meta', 'openai', 'chip', 'software', 'hardware',
                  'penipuan', 'scam', 'phishing', 'cyber', 'modus',
                  'online', 'doxing', 'hacker', 'kebocoran',
                  'funding', 'pendanaan', 'series a', 'series b', 'valuasi',
                  'venture', 'modal ventura', 'beasiswa', 'garuda'],
    'otomotif': ['mobil', 'motor', 'skutik', 'matic', 'kendaraan', 'listrik',
                 'sedan', 'suv', 'mpv', 'pickup', 'hatchback', 'toyota',
                 'honda', 'yamaha', 'suzuki', 'mitsubishi', 'hyundai',
                 'wuling', 'tesla', 'byd', 'bmw', 'mercedes', 'facelift',
                 'test drive', 'review', 'modifikasi', 'pajero'],
    'kesehatan': ['kesehatan', 'penyakit', 'obat', 'dokter', 'rumah sakit',
                  'vaksin', 'imunisasi', 'gizi', 'stunting', 'demam',
                  'flu', 'jantung', 'diabetes', 'kanker', 'stroke',
                  'mental', 'tidur', 'olahraga', 'diet', 'nutrisi',
                  'tekanan darah', 'hipertensi', 'kolesterol', 'asam urat',
                  'obesitas', 'kegemukan', 'berat badan', 'begadang',
                  'insomnia', 'stres', 'depresi', 'kecemasan', 'anxiety',
                  'kebugaran', 'imun', 'daya tahan tubuh', 'vitamin',
                  'suplemen', 'kalsium', 'protein', 'karbohidrat',
                  'lemak', 'serat', 'buah', 'sayur', 'alkohol', 'rokok',
                  'vape', 'merokok', 'perokok', 'jantung koroner',
                  'serangan jantung', 'gagal jantung', 'gagal ginjal',
                  'ginjal', 'liver', 'hati', 'paru', 'paru-paru',
                  'asma', 'tbc', 'tuberkulosis', 'dbd', 'demam berdarah',
                  'malaria', 'covid', 'virus', 'bakteri', 'infeksi',
                  'alergi', 'autoimun', 'kanker payudara', 'kanker paru',
                  'kanker serviks', 'kanker usus', 'tumor', 'kista',
                  'penglihatan', 'mata', 'telinga', 'gigi', 'mulut',
                  'kulit', 'rambut', 'kuku', 'tulang', 'otot', 'sendi',
                  'punggung', 'leher', 'kepala', 'migrain', 'pusing',
                  'vertigo', 'epilepsi', 'alzheimer', 'pikun', 'demensia',
                  'autisme', 'adhd', 'disleksia', 'down syndrome',
                  'kesehatan mental', 'kesehatan jiwa', 'psikolog',
                  'psikiater', 'konseling', 'terapi', 'rehabilitasi',
                  'pola makan', 'pola tidur', 'gaya hidup', 'sedentary',
                  'aktivitas fisik', 'senam', 'yoga', 'pilates',
                  'angkat beban', 'kardio', 'aerobik', 'stretching',
                  'pemanasan', 'pendinginan', 'cedera', 'patah tulang',
                  'keseleo', 'memar', 'luka', 'jahitan', 'operasi',
                  'bedah', 'transplantasi', 'donor darah', 'transfusi',
                  'imunisasi anak', 'mpasi', 'asi', 'bayi', 'balita',
                  'anak', 'remaja', 'dewasa', 'lansia', 'manula',
                  'kehamilan', 'hamil', 'menyusui', 'menopause',
                  'kb', 'kontrasepsi', 'kesuburan', 'kemandulan',
                  'kesehatan reproduksi', 'kesehatan seksual',
                  'diabetes melitus', 'diabetes tipe 2',
                  'prediabetes', 'gula darah', 'glukosa', 'insulin',
                  'kolesterol jahat', 'ldl', 'hdl', 'trigliserida',
                  'lemak jenuh', 'lemak trans', 'omega 3', 'omega 6',
                  'antioksidan', 'probiotik', 'prebiotik', 'fermentasi',
                  'detoks', 'puasa intermiten', 'diet keto', 'diet mediterania',
                  'vegetarian', 'vegan', 'gluten', 'laktosa', 'intoleransi',
                  'alergi makanan', 'keracunan makanan', 'diare', 'sembelit',
                  'maag', 'gastritis', 'asam lambung', 'gerd', 'tukak lambung',
                  'usus buntu', 'wasir', 'ambeien', 'hernia', 'batu empedu',
                  'batu ginjal', 'infeksi saluran kemih',
                  'prostat', 'kandung kemih', 'inkontinensia',
                  'endometriosis', 'pcos', 'miom', 'kista ovarium',
                  'kanker ovarium', 'kanker rahim', 'kanker prostat',
                  'kanker darah', 'leukemia', 'limfoma', 'anemia',
                  'hemofilia', 'talasemia', 'hemoglobin', 'sel darah',
                  'trombosit', 'leukosit', 'eritrosit', 'darah rendah',
                  'hipotensi', 'darah tinggi', 'aritmia', 'jantung bocor',
                  'katup jantung', 'pembuluh darah', 'aterosklerosis',
                  'stroke iskemik', 'stroke hemoragik', 'tia',
                  'parkinson', 'multiple sclerosis',
                  'lupus', 'rematik', 'artritis', 'osteoporosis',
                  'osteopenia', 'rakitis', 'skoliosis', 'lordosis',
                  'kifosis', 'sarkopenia', 'fraktur', 'dislokasi',
                  'fisioterapi', 'okupasi terapi', 'terapi wicara',
                  'hipnoterapi', 'akupunktur', 'akupresur', 'pijat',
                  'urut', 'refleksi', 'bekam', 'herbal', 'jamu',
                  'tanaman obat', 'khasiat', 'manfaat', 'efek samping',
                  'kontraindikasi', 'dosis', 'resep', 'apotek', 'farmasi',
                  'antibiotik', 'antivirus', 'antijamur', 'analgesik',
                  'paracetamol', 'ibuprofen', 'aspirin', 'amoxicillin',
                  'vitamin c', 'vitamin d', 'vitamin b', 'zat besi',
                  'folat', 'asam folat', 'yodium', 'zinc', 'magnesium'],
}

def _materi_cocok_kategori(kategori, judul, summary):
    if not kategori:
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    kata_kunci = KATA_KUNCI_KATEGORI.get(kategori, [])
    if not kata_kunci:
        return True, ''
    for kk in kata_kunci:
        if len(kk) <= 4:
            if re.search(r'\b' + re.escape(kk) + r'\b', gab):
                return True, ''
        else:
            if kk in gab:
                return True, ''
    return False, 'materi tidak ada kata kunci kategori ' + kategori

KATA_SINYAL_EKONOMI_KUAT = [
    'return', 'annualized', 'annualised', 'portfolio', 'portofolio',
    'investor', 'investasi', 'saham', 'stock', 'yield', 'dividend',
    'dividen', 'index saham', 'stock market', 'equity', 'ekuitas',
    'reksa dana', 'obligasi', 'bond', 'bursa', 'trading', 'trader',
    'market cap', 'valuasi', 'funding', 'pendanaan', 'ipo', 'merger',
    'akuisisi', 'gain', 'profit', 'laba', 'loss', 'rugi',
    'inflation', 'inflasi', 'gdp', 'pdb', 'growth', 'pertumbuhan',
    'ekspor', 'impor', 'exports', 'imports', 'trade balance',
    'neraca dagang', 'quarterly', 'kuartal', 'fiscal', 'fiskal',
]

def _kandidat_kategori_materi(kategori, judul, summary):
    if not kategori:
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    if kategori == 'internasional_asean':
        if adalah_turnamen_olahraga(gab):
            return False, 'kategori asean tapi materi turnamen olahraga (ke olahraga)'
        hit_eko = sum(1 for k in KATA_SINYAL_EKONOMI_KUAT if k in gab)
        if hit_eko >= 3:
            return False, 'kategori asean tapi materi ekonomi (hit ' + str(hit_eko) + ')'
        if not any(k in gab for k in KATA_ASEAN_WAJIB):
            return False, 'kategori asean tapi materi tidak ada kata ASEAN'
    elif kategori == 'internasional_tt':
        hit_eko = sum(1 for k in KATA_SINYAL_EKONOMI_KUAT if k in gab)
        if hit_eko >= 3:
            return False, 'kategori tt tapi materi ekonomi (hit ' + str(hit_eko) + ')'
        if not any(k in gab for k in KATA_TT):
            return False, 'kategori tt tapi materi tidak ada kata Timur Tengah'
    elif kategori == 'internasional':
        hit_eko = sum(1 for k in KATA_SINYAL_EKONOMI_KUAT if k in gab)
        if hit_eko >= 3:
            return False, 'kategori internasional tapi materi ekonomi (hit ' + str(hit_eko) + ')'
        if not any(k in gab for k in KATA_LUAR_NEGERI_WAJIB):
            return False, 'kategori internasional tapi materi tidak ada kata luar negeri'
    elif kategori == 'ekonomi':
        # V6.17.92: tolak kalau materi jelas bukan ekonomi (data centre/AI)
        non_eko = _materi_bukan_ekonomi(gab)
        if non_eko:
            return False, 'kategori ekonomi tapi materi bukan ekonomi (' + non_eko + ')'
        if not any(k in gab for k in KATA_EKONOMI_WAJIB):
            return False, 'kategori ekonomi tapi materi tidak ada kata ekonomi'
    ok, alasan = _materi_cocok_kategori(kategori, judul, summary)
    if not ok:
        return False, alasan
    return True, ''

def _kandidat_tanpa_tokoh_indonesia(kategori, judul, summary):
    if kategori not in ('internasional', 'internasional_asean', 'internasional_tt'):
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    for tokoh in NAMA_TOKOH_INDONESIA:
        if re.search(r'\b' + re.escape(tokoh) + r'\b', gab):
            return False, 'kategori luar tapi ada tokoh Indonesia: ' + tokoh
    for lem in LEMBAGA_INDONESIA:
        if lem == 'kpk':
            if _kpk_konteks_indonesia(gab):
                return False, 'kategori luar tapi ada lembaga Indonesia kpk (konteks Indonesia)'
            continue
        if lem == 'tni':
            continue
        if re.search(r'\b' + re.escape(lem) + r'\b', gab):
            return False, 'kategori luar tapi ada lembaga Indonesia: ' + lem
    return True, ''

SINGKATAN_LOKASI_LOKAL = {
    'ubt': 'tarakan', 'untan': 'pontianak', 'unmul': 'samarinda',
    'unlam': 'banjarmasin', 'unhas': 'makassar', 'unpad': 'bandung',
    'ugm': 'yogyakarta', 'ui': 'depok', 'itb': 'bandung',
    'undip': 'semarang', 'unair': 'surabaya', 'unib': 'bengkulu',
    'unram': 'mataram', 'unsoed': 'purwokerto',
    'kpwbi': 'kaltara', 'bi kaltara': 'kaltara', 'ojk kaltara': 'kaltara',
    'pdam tirta': 'tarakan', 'rsud': 'tarakan', 'rsu': 'tarakan',
}

KONTEKS_PEMDA_KUAT = [
    'pajak restoran', 'pajak hotel', 'pajak reklame', 'pajak bumi',
    'pajak daerah', 'retribusi', 'retribusi daerah',
    'bphtb', 'pbb', 'izin usaha', 'perizinan', 'imb',
    'apbd', 'rapbd', 'apbdes', 'dana desa', 'alokasi dana desa',
    'musrenbang', 'perda', 'perwali', 'perbup',
    'pilkades', 'pemilihan kades', 'kades', 'bpd',
    'dinas kesehatan', 'dinas pendidikan', 'dinas sosial',
    'dinas pertanian', 'dinas perikanan', 'dinas pu', 'dinas perhubungan',
    'satpol pp', 'damkar', 'tagana',
    'kelurahan', 'kecamatan', 'lurah', 'camat',
    'bantuan sosial daerah', 'bansos daerah',
    'rutilahu', 'bedah rumah',
]

def _ada_konteks_pemda_kuat(judul, summary):
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    hit = 0
    for k in KONTEKS_PEMDA_KUAT:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', gab):
                hit += 1
        else:
            if k in gab:
                hit += 1
        if hit >= 1:
            return True
    return False

def _ada_singkatan_lokasi_lokal(judul, summary):
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    for sing in SINGKATAN_LOKASI_LOKAL:
        if len(sing) <= 4:
            if re.search(r'\b' + re.escape(sing) + r'\b', gab):
                return sing
        else:
            if sing in gab:
                return sing
    return None

def _kandidat_ada_lokasi(judul, summary, kategori=''):
    if kategori in ('nasional', 'breaking', 'teknologi', 'kesehatan'):
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    if kategori == 'daerah' and _ada_konteks_pemda_kuat(judul, summary):
        return True, ''
    if kategori == 'daerah':
        sing = _ada_singkatan_lokasi_lokal(judul, summary)
        if sing:
            return True, ''
    for kota in KOTA_INDONESIA_DATELINE:
        if re.search(r'\b' + re.escape(kota) + r'\b', gab):
            return True, ''
    for prov in KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN:
        if re.search(r'\b' + re.escape(prov) + r'\b', gab):
            return True, ''
    for kota_asing in IBU_KOTA_NEGARA.keys():
        if re.search(r'\b' + re.escape(kota_asing) + r'\b', gab):
            return True, ''
    for kota in VARIAN_KOTA_EN_ID.keys():
        if re.search(r'\b' + re.escape(kota) + r'\b', gab):
            return True, ''
    for ev_nama in EVENT_BESAR_KOTA.keys():
        if ev_nama in gab:
            return True, ''
    for tim in KAMUS_TIM_LIGA_NEGARA.keys():
        if tim in gab:
            return True, ''
    return False, 'tidak ada lokasi (kota/provinsi) di judul/materi'

def _kandidat_ada_nama_orang(judul, summary):
    teks = ((judul or '') + ' ' + (summary or '')).strip()
    if not teks:
        return False
    pola_nama = re.compile(r'\b([A-Z][a-z]{2,})\s+([A-Z][a-z]{2,})\b')
    nama_ditemukan = []
    for m in pola_nama.finditer(teks):
        kata1 = m.group(1).lower()
        kata2 = m.group(2).lower()
        skip_kata1 = ['jakarta', 'bandung', 'surabaya', 'medan', 'semarang',
                      'makassar', 'balikpapan', 'samarinda', 'tarakan',
                      'kaltara', 'kalimantan', 'sumatera', 'jawa', 'sulawesi',
                      'papua', 'bali', 'nusa', 'pemerintah', 'menteri',
                      'presiden', 'gubernur', 'bupati', 'walikota', 'wakil',
                      'kepala', 'ketua', 'komandan', 'kapolres', 'dandim',
                      'sekretaris', 'direktur', 'pemkot', 'pemkab', 'pemprov',
                      'polres', 'kodim', 'bandara', 'kota', 'kabupaten',
                      'provinsi', 'dinas', 'badan', 'kantor', 'lembaga',
                      'komisi', 'monday', 'tuesday', 'wednesday', 'thursday',
                      'friday', 'saturday', 'sunday', 'januari', 'februari',
                      'maret', 'april', 'mei', 'juni', 'juli', 'agustus',
                      'september', 'oktober', 'november', 'desember',
                      'breaking', 'news']
        if kata1 in skip_kata1 or kata2 in skip_kata1:
            continue
        skip_kata2 = ['sebut', 'kata', 'ujar', 'tutur', 'jelas', 'ungkap',
                      'minta', 'harap', 'imbau', 'seru', 'tegas', 'sebutkan']
        if kata2 in skip_kata2:
            continue
        nama_ditemukan.append(m.group(0).strip())
    return len(nama_ditemukan) > 0

def _kandidat_dateline_luar_untuk_int(judul, summary, kategori=''):
    if kategori not in ('internasional', 'internasional_asean', 'internasional_tt'):
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    for kota in IBU_KOTA_NEGARA.keys():
        if re.search(r'\b' + re.escape(kota) + r'\b', gab):
            return True, ''
    for varian in VARIAN_KOTA_EN_ID.keys():
        if re.search(r'\b' + re.escape(varian) + r'\b', gab):
            return True, ''
    for negara in KATA_LUAR_NEGERI_WAJIB:
        if negara in gab:
            return True, ''
    if any(k in gab for k in ('jakarta', 'indonesia', 'jokowi', 'prabowo')):
        return False, 'kategori internasional tapi materi tentang Indonesia saja'
    return True, ''

def _kandidat_bukan_indo_only(kategori, judul, summary):
    if kategori not in ('internasional', 'internasional_asean', 'internasional_tt'):
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    sinyal_indo = 0
    for k in ['jakarta', 'indonesia', 'jokowi', 'prabowo', 'menteri ri',
              'kemenlu ri', 'wni', 'pemerintah indonesia', 'presiden ri']:
        if k in gab:
            sinyal_indo += 1
    sinyal_luar = 0
    for k in KATA_LUAR_NEGERI_WAJIB:
        if k in gab:
            sinyal_luar += 1
    if sinyal_indo >= 2 and sinyal_luar == 0:
        return False, 'materi 100% tentang Indonesia untuk kategori luar'
    return True, ''

POLA_FRASA_INDONESIA_DULU = re.compile(
    r'\b(?:ri|republik\s+indonesia|indonesia|indo)[\s\-–—]',
    re.IGNORECASE
)

def _ada_frasa_indonesia_plus(kata_negara, gab):
    pola = re.compile(
        r'\b(?:ri|republik\s+indonesia|indonesia|indo)[\s\-–—]'
        + re.escape(kata_negara) + r'\b',
        re.IGNORECASE
    )
    return bool(pola.search(gab))

# ══════════════════════════════════════════════════════
# V6.17.98: _kandidat_negara_asing_untuk_lokal — DILONGGARKAN
# Jangan blok kalau ada konteks Indonesia kuat:
#   - kunjungan ke Indonesia (El-Sisi kunjungi Indonesia)
#   - kabut asap lintas batas Indonesia-Malaysia
#   - kerja sama RI-X
# ══════════════════════════════════════════════════════

FRASA_KUNJUNGAN_KE_INDONESIA = [
    'kunjungi indonesia', 'kunjungan ke indonesia', 'berkunjung ke indonesia',
    'datang ke indonesia', 'tiba di indonesia', 'bertemu presiden ri',
    'bertemu presiden indonesia', 'bertemu prabowo', 'sambut presiden',
    'kunjungan kenegaraan ke indonesia', 'kunjungan resmi ke indonesia',
    'di jakarta', 'di indonesia', 'ke jakarta', 'ke indonesia',
    'state visit to indonesia', 'visit indonesia', 'arrives in indonesia',
    'meets president', 'meets prabowo', 'welcome to indonesia',
]

FRASA_KERJA_SAMA_INDONESIA = [
    'kerja sama indonesia', 'kerjasama indonesia', 'kerja sama ri',
    'kerjasama ri', 'indonesia dan', 'indonesia dengan',
    'ri dan', 'ri dengan', 'bilateral indonesia',
    'asean indonesia', 'indonesia asean',
    'lintas batas indonesia', 'indonesia malaysia', 'malaysia indonesia',
    'transboundary', 'lintas batas',
]

def _ada_konteks_kunjungan_atau_kerjasama_indonesia(gab):
    """V6.17.98: cek apakah teks punya konteks kunjungan/kerja sama
    dengan Indonesia — kalau iya, jangan blok sebagai 'negara asing'."""
    for f in FRASA_KUNJUNGAN_KE_INDONESIA:
        if f in gab:
            return True
    for f in FRASA_KERJA_SAMA_INDONESIA:
        if f in gab:
            return True
    # Konteks kabut asap lintas batas
    if _ada_konteks_kabut_asap_asean(gab):
        return True
    return False

def _kandidat_negara_asing_untuk_lokal(kategori, judul, summary):
    if kategori not in ('nasional', 'daerah'):
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    # V6.17.98: kalau ada konteks kunjungan/kerja sama Indonesia → JANGAN blok
    if _ada_konteks_kunjungan_atau_kerjasama_indonesia(gab):
        return True, ''
    for negara in NEGARA_ASING:
        if len(negara) <= 4:
            m = re.search(r'\b' + re.escape(negara) + r'\b', gab)
            if not m:
                continue
            if _ada_frasa_indonesia_plus(negara, gab):
                continue
            return False, 'kategori ' + kategori + ' tapi materi tentang negara asing: ' + negara
        else:
            if negara not in gab:
                continue
            if _ada_frasa_indonesia_plus(negara, gab):
                continue
            return False, 'kategori ' + kategori + ' tapi materi tentang negara asing: ' + negara
    return True, ''

def _kandidat_bukan_kontes(kategori, judul, summary):
    if kategori != 'nasional':
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    for k in KATA_BUKAN_NASIONAL:
        if k in gab:
            return False, 'kontes/kecantikan bukan nasional: ' + k
    return True, ''

def _kandidat_bukan_jadwal_transport(kategori, judul, summary):
    if kategori != 'daerah':
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    for k in KATA_BUKAN_DAERAH:
        if k in gab:
            return False, 'jadwal transportasi bukan daerah: ' + k
    return True, ''

KATA_PENDIDIKAN_MURNI = [
    'smpn', 'sman', 'smkn', 'sdn', 'mtsn', 'man ',
    'sekolah dasar negeri', 'sekolah menengah atas', 'sekolah menengah pertama',
    'sekolah menengah kejuruan', 'madrasah tsanawiyah', 'madrasah aliyah',
    'kurikulum merdeka', 'kurikulum 2013', 'unbk', 'anbk', 'asesmen nasional',
    'ppdb', 'mpls', 'osis', 'ekstrakurikuler',
    'kegiatan belajar mengajar', 'kbm', 'proses belajar mengajar',
    'raport', 'rapot', 'wisuda sekolah', 'kelulusan sekolah',
    'ujian sekolah', 'ujian nasional', 'ujian akhir semester', 'uas', 'uts',
]

def _kandidat_bukan_pendidikan(kategori, judul, summary):
    if kategori != 'daerah':
        return True, ''
    gab = ((judul or '') + ' ' + (summary or '')).lower()
    hit = 0
    for k in KATA_PENDIDIKAN_MURNI:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', gab):
                hit += 1
        else:
            if k in gab:
                hit += 1
    if hit >= 2:
        return False, 'materi murni pendidikan bukan berita daerah (' + str(hit) + ' kata kunci)'
    return True, ''

def _kandidat_bukan_dobel(judul):
    if sudah_serupa(judul):
        return False, 'dobel dengan judul yang sudah ada'
    for t in JUDUL_6JAM:
        if not t:
            continue
        ki = kata_inti(judul)
        kt = kata_inti(t)
        if ki and kt and len(ki & kt) >= DOBEL_6JAM_MIN_KATA:
            if DOBEL_6JAM_BUTUH_NAMA:
                if _ada_nama_diri_judul(judul) or _ada_nama_diri_judul(t):
                    return False, 'dobel-6jam dengan "' + t[:40] + '"'
            else:
                return False, 'dobel-6jam dengan "' + t[:40] + '"'
    return True, ''

# V6.17.76: longgarkan min irisan 3 → 4
def _dobel_dateline_topik(judul_baru, isi_baru):
    if not judul_baru or not isi_baru:
        return None
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+', isi_baru)
    if not m:
        return None
    dateline_baru = m.group(1).strip().lower()
    kota_baru = dateline_baru.split(',')[0].strip()
    if not kota_baru:
        return None
    ki_baru = kata_inti(judul_baru)
    if not ki_baru:
        return None
    for t in JUDUL_TERPAKAI:
        if not t:
            continue
        kt = kata_inti(t)
        if not kt:
            continue
        irisan = ki_baru & kt
        if len(irisan) < 4:
            continue
        if kota_baru in t:
            return ('dobel dateline+topik: "' + kota_baru + '" + '
                    + str(len(irisan)) + ' kata kunci sama — '
                    + 'irisan: ' + str(sorted(list(irisan))[:4]))
    return None

DOMAIN_OLAHRAGA_SKIP = ['sports.yahoo.com']

def _kandidat_domain_olahraga_skip(kategori, judul, link):
    if kategori != 'olahraga':
        return False
    low = (link or '').lower()
    for d in DOMAIN_OLAHRAGA_SKIP:
        if d in low:
            return True
    return False

def _kandidat_domain_skip(kategori, judul, link):
    low = (link or '').lower()
    if any(d in low for d in DOMAIN_SKIP_SCRAPE):
        return True
    return False

def _kandidat_layak(judul, summary, kategori='', link=''):
    judul = (judul or '').strip()
    summary = (summary or '').strip()
    if not judul or not summary:
        return False, 'judul/summary kosong'
    if _kandidat_domain_skip(kategori, judul, link):
        return False, 'domain skip (blog opini/portal gagal)'
    if _kandidat_domain_olahraga_skip(kategori, judul, link):
        return False, 'portal olahraga inggris (judul tidak kontekstual)'
    tl = judul.lower()
    for k in KATA_FEATURE_OPINI:
        if k in tl:
            return False, 'feature/opini: ' + k
    if any(x in tl for x in ('ada apa?', 'ternyata', 'ini faktanya',
                              'simak', 'beginilah', 'inilah', 'awas!')):
        return False, 'clickbait: kata pancingan'
    if len(judul.split()) < 4:
        return False, 'judul kurang dari 4 kata'
    ok, alasan = _kandidat_bukan_dobel(judul)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_topik_nyambung(judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_negara_asing_untuk_lokal(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_bukan_kontes(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_bukan_pendidikan(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_bukan_jadwal_transport(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_kategori_materi(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_bukan_indo_only(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_dateline_luar_untuk_int(judul, summary, kategori)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_tanpa_tokoh_indonesia(kategori, judul, summary)
    if not ok:
        return False, alasan
    ok, alasan = _kandidat_ada_lokasi(judul, summary, kategori)
    if not ok:
        return False, alasan
    return True, ''

def _judul_dari_url_supabase():
    out = []
    try:
        rows = rest_get('?select=title,source_url,created_at&order=created_at.desc&limit=500')
        for row in rows:
            if row.get('title') and _dalam_jendela(row, JENDELA_DOBEL_JAM):
                out.append(row['title'])
    except Exception:
        pass
    return out

BULAN_NAMA_DIRI = set([
    'januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli',
    'agustus', 'september', 'oktober', 'november', 'desember',
])

def _ada_nama_diri_teks(teks):
    if not teks:
        return False
    t_low = teks.lower()
    for b in BULAN_NAMA_DIRI:
        if b in t_low:
            return True
    for k in KOTA_INDONESIA_DATELINE:
        if re.search(r'\b' + re.escape(k) + r'\b', t_low):
            return True
    for k in KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN:
        if re.search(r'\b' + re.escape(k) + r'\b', t_low):
            return True
    if _ada_nama_diri_judul(teks):
        return True
    return False

def _topik_sudah_terbit(judul_kandidat, judul_lama_list):
    if not judul_kandidat or not judul_lama_list:
        return None
    if judul_topik_besar(judul_kandidat):
        return None
    ki_baru = kata_inti(judul_kandidat)
    if not ki_baru:
        return None
    min_irisan = 3
    for t_lama in judul_lama_list:
        if not t_lama:
            continue
        if judul_topik_besar(t_lama):
            continue
        ki_lama = kata_inti(t_lama)
        if not ki_lama:
            continue
        irisan = ki_baru & ki_lama
        if len(irisan) >= min_irisan:
            return ('dobel topik: ' + str(len(irisan)) + ' kata kunci sama — '
                    + 'irisan: ' + str(sorted(list(irisan))[:5]))
    return None

# ══════════════════════════════════════════════════════
# V6.17.75: REVISI #1 - CEK BERITA BASI (bulan/tahun < sekarang)
# V6.17.77: TAMBAH cek frasa prediksi "akan bertanding" + tanggal sudah lewat
# V6.17.81: TAMBAH cek frasa LIVE/IN-PROGRESS + topik sudah terbit
# ══════════════════════════════════════════════════════

POLA_TANGGAL_LENGKAP = re.compile(
    r'\b(\d{1,2})\s+'
    r'(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)'
    r'\s+(\d{4})\b',
    re.IGNORECASE
)
POLA_BULAN_TAHUN = re.compile(
    r'\b(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)'
    r'\s+(\d{4})\b',
    re.IGNORECASE
)
POLA_TANGGAL_TANPA_TAHUN = re.compile(
    r'\b(\d{1,2})\s+'
    r'(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\b',
    re.IGNORECASE
)
POLA_TANGGAL_ANGKA = re.compile(
    r'\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{4}))?\b'
)

_NAMA_BULAN_KE_ANGKA = {
    'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11,
    'desember': 12,
}

KATA_FRASA_PREDIKSI = [
    'akan bertanding', 'akan berlaga', 'akan berhadapan', 'akan berlangsung',
    'akan menghadapi', 'akan melakoni', 'akan menjamu', 'akan bertemu',
    'akan menantang', 'akan dijadwalkan', 'akan digelar', 'akan kick off',
    'akan kick-off', 'akan dimulai', 'akan beradu', 'akan melawan',
    'siap bertanding', 'siap berlaga', 'siap berhadapan', 'siap menghadapi',
]

# V6.17.81: frasa live/in-progress — pertandingan sedang berlangsung
KATA_FRASA_LIVE = [
    'babak tambahan', 'babak pertama', 'babak kedua',
    'babak perpanjangan', 'extra time', 'perpanjangan waktu',
    'berlanjut ke', 'melanjutkan ke',
    'sedang berlangsung', 'masih berlangsung', 'kini berlangsung',
    'live report', 'live score', 'live streaming', 'live update',
    'live report', 'liveblog', 'live blog',
    'kick off', 'kick-off', 'kickoff',
    'half time', 'half-time', 'halftime',
    'paruh pertama', 'paruh kedua',
    'menit ke-', 'menit ke ',
    'babak penalty', 'babak penalti', 'adu penalti', 'adu pinalti',
    'berlangsung sengit', 'berjalan sengit',
    'skor sementara', 'kedudukan sementara',
    'unconfirmed', 'belum final',
]

def _materi_basi(judul, summary):
    """
    V6.17.75: Cek materi basi — kalau judul/summary memuat tanggal lengkap
    atau bulan+tahun yang lebih LAMA dari bulan sekarang → tolak.

    V6.17.77: Tambah cek frasa prediksi ("akan bertanding") + tanggal
    sudah lewat → tolak.

    V6.17.81: Tambah cek frasa LIVE/IN-PROGRESS + topik sudah terbit
    → tolak.

    Return: (True, alasan) kalau basi, (False, '') kalau OK.
    """
    teks = ((judul or '') + ' ' + (summary or '')).strip()
    if not teks:
        return False, ''
    now = datetime.now(WITA)
    bulan_sekarang = now.month
    tahun_sekarang = now.year
    tanggal_sekarang = now.day
    teks_low = teks.lower()

    # Cek pola tanggal lengkap (dd Bulan yyyy)
    for m in POLA_TANGGAL_LENGKAP.finditer(teks):
        try:
            nama_bulan = m.group(2).lower()
            tahun = int(m.group(3))
            bulan = _NAMA_BULAN_KE_ANGKA.get(nama_bulan, 0)
            if bulan == 0:
                continue
            if tahun < tahun_sekarang:
                return True, ('materi basi (tanggal ' + m.group(0)
                              + ' < ' + now.strftime('%B %Y') + ')')
            if tahun == tahun_sekarang and bulan < bulan_sekarang:
                return True, ('materi basi (bulan ' + nama_bulan.title()
                              + ' < ' + now.strftime('%B') + ')')
        except Exception:
            continue

    # Cek pola bulan+tahun (Bulan yyyy)
    for m in POLA_BULAN_TAHUN.finditer(teks):
        try:
            nama_bulan = m.group(1).lower()
            tahun = int(m.group(2))
            bulan = _NAMA_BULAN_KE_ANGKA.get(nama_bulan, 0)
            if bulan == 0:
                continue
            if tahun < tahun_sekarang:
                return True, ('materi basi (bulan+tahun ' + m.group(0)
                              + ' < ' + now.strftime('%B %Y') + ')')
            if tahun == tahun_sekarang and bulan < bulan_sekarang:
                return True, ('materi basi (bulan ' + nama_bulan.title()
                              + ' < ' + now.strftime('%B') + ')')
        except Exception:
            continue

    # V6.17.77: cek frasa prediksi + tanggal sudah lewat
    ada_prediksi = any(f in teks_low for f in KATA_FRASA_PREDIKSI)
    if ada_prediksi:
        tanggal_lewat = False
        detail_tanggal = ''

        for m in POLA_TANGGAL_TANPA_TAHUN.finditer(teks):
            try:
                hari = int(m.group(1))
                nama_bulan = m.group(2).lower()
                bulan = _NAMA_BULAN_KE_ANGKA.get(nama_bulan, 0)
                if bulan == 0:
                    continue
                if bulan < bulan_sekarang:
                    tanggal_lewat = True
                    detail_tanggal = m.group(0)
                    break
                if bulan == bulan_sekarang and hari < tanggal_sekarang:
                    tanggal_lewat = True
                    detail_tanggal = m.group(0)
                    break
            except Exception:
                continue

        if not tanggal_lewat:
            for m in POLA_TANGGAL_ANGKA.finditer(teks):
                try:
                    hari = int(m.group(1))
                    bulan = int(m.group(2))
                    tahun = int(m.group(3)) if m.group(3) else tahun_sekarang
                    if tahun < tahun_sekarang:
                        tanggal_lewat = True
                        detail_tanggal = m.group(0)
                        break
                    if tahun == tahun_sekarang and bulan < bulan_sekarang:
                        tanggal_lewat = True
                        detail_tanggal = m.group(0)
                        break
                    if (tahun == tahun_sekarang and bulan == bulan_sekarang
                            and hari < tanggal_sekarang):
                        tanggal_lewat = True
                        detail_tanggal = m.group(0)
                        break
                except Exception:
                    continue

        if tanggal_lewat:
            frasa_ketemu = next((f for f in KATA_FRASA_PREDIKSI if f in teks_low), '')
            return True, ('materi basi prediksi (frasa "' + frasa_ketemu
                          + '" + tanggal lewat ' + detail_tanggal + ')')

    # V6.17.81: cek frasa LIVE/IN-PROGRESS + topik sudah terbit
    frasa_live_ketemu = next((f for f in KATA_FRASA_LIVE if f in teks_low), None)
    if frasa_live_ketemu:
        # Cek apakah topik ini sudah pernah terbit → berarti ini berita basi
        judul_lama = _judul_dari_url_supabase()
        topik_dobel = _topik_sudah_terbit(judul, judul_lama)
        if topik_dobel:
            return True, ('materi basi live (frasa "' + frasa_live_ketemu
                          + '" + topik sudah terbit: ' + topik_dobel[:60] + ')')

    return False, ''

# ══════════════════════════════════════════════════════
# V6.17.75: REVISI #2 - TOLAK RSS TANPA TANGGAL
# V6.17.98: PRE-FILTER RSS TIPIS DARI DOMAIN_SKIP_SCRAPE
# ══════════════════════════════════════════════════════

def collect_candidates(sources, today_urls, seen, max_umur_jam=None, kategori=''):
    if max_umur_jam is None:
        max_umur_jam = MAX_UMUR_BERITA_HARI
    rejected = muat_rejected_urls()
    judul_database = _judul_dari_url_supabase()
    out = []
    skip_layak = 0
    skip_rejected = 0
    skip_topik = 0
    skip_tanpa_tanggal = 0
    skip_basi = 0
    skip_rss_tipis = 0
    for src in sources:
        try:
            feed = feedparser.parse(src['url'])
        except Exception:
            continue
        for entry in feed.entries[:8]:
            link = entry.get('link', '')
            if not link or link in seen or link in today_urls:
                continue
            if link in rejected:
                skip_rejected += 1
                continue
            u = umur_jam(entry)
            # V6.17.75: revisi #2 - tolak RSS tanpa tanggal
            if u is None:
                skip_tanpa_tanggal += 1
                continue
            if u > max_umur_jam:
                continue
            title = entry.get('title', '')
            summary = get_material(entry)
            if not title or not summary:
                continue

            # ══════════════════════════════════════════════════════
            # V6.17.98: PRE-FILTER RSS TIPIS DARI DOMAIN_SKIP_SCRAPE
            # Kalau domain akan di-skip scraping & RSS tipis (< 200 kar)
            # → langsung buang (jangan buang token AI).
            # ══════════════════════════════════════════════════════
            if domain_skip_scrape(link) and len(summary) < MATERI_RSS_SKIP_TIPIS:
                skip_rss_tipis += 1
                if skip_rss_tipis <= 3:
                    print('       Skip kandidat (pre-filter RSS tipis domain skip): '
                          + str(len(summary)) + ' kar — ' + title[:50])
                continue

            # ══════════════════════════════════════════════════════
            # V6.17.94: PRE-FILTER LOKAL — hemat token DeepSeek
            # Versi LONGGAR: hanya buang yang JELAS sampah.
            # Kandidat ragu-ragu tetap lolos ke AI (AI yang putuskan).
            # ══════════════════════════════════════════════════════
            _t_low = (title + ' ' + summary).lower()

            # 1. Materi sampah — hanya skip kalau ≥2 frasa sampah
            _hit_sampah = sum(1 for k in KATA_MATERI_SAMPAH if k in _t_low)
            if _hit_sampah >= 2:
                skip_layak += 1
                if skip_layak <= 3:
                    print('       Skip kandidat (pre-filter sampah): '
                          + str(_hit_sampah) + ' frasa — ' + title[:50])
                continue

            # 2. Aktor non-breaking — hanya skip kalau ≥2 aktor muncul
            _aktor_hit = []
            for _ak in AKTOR_NON_BREAKING:
                if len(_ak) <= 4:
                    if re.search(r'\b' + re.escape(_ak) + r'\b', _t_low):
                        _aktor_hit.append(_ak)
                else:
                    if _ak in _t_low:
                        _aktor_hit.append(_ak)
                if len(_aktor_hit) >= 2:
                    break
            if len(_aktor_hit) >= 2 and kategori in ('nasional', 'daerah',
                                                     'internasional',
                                                     'internasional_asean',
                                                     'internasional_tt'):
                skip_layak += 1
                if skip_layak <= 3:
                    print('       Skip kandidat (pre-filter aktor): '
                          + ', '.join(_aktor_hit[:2]) + ' — ' + title[:50])
                continue

            # 3. Domain skip — tetap skip (pasti gagal)
            if domain_skip_scrape(link):
                skip_layak += 1
                continue

            # 4. Kategori: cek kata kunci LONGGAR di judul + summary + 500 kar materi
            if kategori and kategori != 'breaking':
                _kata_kat = KATA_KUNCI_KATEGORI.get(kategori, [])
                if _kata_kat:
                    _gab_cek = _t_low[:500]
                    _hit_kat = 0
                    for _kk in _kata_kat:
                        if len(_kk) <= 4:
                            if re.search(r'\b' + re.escape(_kk) + r'\b', _gab_cek):
                                _hit_kat += 1
                                break
                        else:
                            if _kk in _gab_cek:
                                _hit_kat += 1
                                break
                    if _hit_kat == 0:
                        skip_layak += 1
                        if skip_layak <= 3:
                            print('       Skip kandidat (pre-filter kategori): '
                                  'tidak ada kata kunci ' + kategori
                                  + ' — ' + title[:50])
                        continue

            # 5. Breaking dunia: tolak yang jelas simulasi/kecil
            if kategori == 'breaking':
                _tolak_brk = sum(1 for k in BREAKING_INT_TOLAK if k in _t_low)
                if _tolak_brk >= 1:
                    skip_layak += 1
                    continue
            # ══════════════════════════════════════════════════════

            # V6.17.75: revisi #1 - cek berita basi
            basi, alasan_basi = _materi_basi(title, summary)
            if basi:
                skip_basi += 1
                if skip_basi <= 3:
                    print('       Skip kandidat (basi): ' + alasan_basi[:70]
                          + ' — ' + title[:50])
                continue

            topik_dobel = _topik_sudah_terbit(title, judul_database)
            if topik_dobel:
                skip_topik += 1
                if skip_topik <= 3:
                    print('       Skip kandidat (dobel topik): ' + topik_dobel[:70] + ' — ' + title[:50])
                continue

            layak, alasan = _kandidat_layak(title, summary, kategori, link)
            if not layak:
                skip_layak += 1
                if skip_layak <= 3:
                    print('       Skip kandidat (AI Editor Luar): ' + alasan[:60] + ' — ' + title[:50])
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
    if skip_layak > 3:
        print('       (Total skip AI Editor Luar: ' + str(skip_layak) + ')')
    if skip_topik > 0:
        print('       (Total skip dobel topik: ' + str(skip_topik) + ')')
    if skip_rejected > 0:
        print('       (Total skip rejected_urls blacklist: ' + str(skip_rejected) + ')')
    if skip_tanpa_tanggal > 0:
        print('       (Total skip RSS tanpa tanggal: ' + str(skip_tanpa_tanggal) + ')')
    if skip_basi > 0:
        print('       (Total skip materi basi: ' + str(skip_basi) + ')')
    if skip_rss_tipis > 0:
        print('       (Total skip RSS tipis domain skip: ' + str(skip_rss_tipis) + ')')
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

# AKHIR PART 3A-1
# PART 3A-2 - BARAT + DATELINE + JANJI + SKOR + NARASUMBER + BUKAN_BERITA + LUAR_NEGERI + TOKOH + KOTA + CEK_KATEGORI + TOPIK

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
        pola = re.compile(r'\b([A-Z][A-Z\s\.\'\-]{3,40}?)\s+[-–—]\s+')
        lokasi = set()
        daftar_kota = set(KOTA_INDONESIA_DATELINE) | set(VARIAN_KOTA_EN_ID.keys())
        for m in pola.finditer(isi or ''):
            kandidat = m.group(1).strip().lower()
            kota = kandidat.split(',')[0].strip()
            if kota in daftar_kota:
                lokasi.add(kandidat)
        if len(lokasi) >= 2:
            return 'isi memuat lebih dari satu dateline kota: ' + '; '.join(list(lokasi)[:3])
    except Exception:
        pass
    return None

VARIAN_KOTA_EN_ID = {
    'korea selatan': ['south korea', 'korea'], 'korea': ['korea selatan', 'south korea', 'north korea'],
    'korea utara': ['north korea'], 'inggris': ['england', 'uk', 'britain', 'united kingdom'],
    'jerman': ['germany'], 'perancis': ['france'], 'spanyol': ['spain'], 'italia': ['italy'],
    'belanda': ['netherlands', 'holland'], 'yunani': ['greece'], 'turki': ['turkey', 'turkiye'],
    'mesir': ['egypt'], 'jepang': ['japan'], 'cina': ['china'], 'india': ['india'],
    'rusia': ['russia'], 'ukraina': ['ukraine'], 'iran': ['iran'], 'irak': ['iraq'],
    'suriah': ['syria'], 'yaman': ['yemen'], 'arab saudi': ['saudi arabia'],
    'uni emirat arab': ['united arab emirates', 'uae'], 'qatar': ['qatar'],
    'filipina': ['philippines'], 'vietnam': ['vietnam'], 'thailand': ['thailand'],
    'malaysia': ['malaysia'], 'singapura': ['singapore'], 'myanmar': ['myanmar'],
    'kamboja': ['cambodia'], 'laos': ['laos'], 'australia': ['australia'],
    'amerika serikat': ['united states', 'us', 'usa', 'america'],
    'brasilia': ['brazil'], 'argentina': ['argentina'], 'seoul': ['seoul'],
    'beijing': ['beijing'], 'tokyo': ['tokyo'], 'london': ['london'], 'paris': ['paris'],
    'moskow': ['moscow'], 'washington': ['washington'], 'new york': ['new york'],
    'kongo': ['congo'], 'ceko': ['czech', 'czechia'], 'kroasia': ['croatia'],
    'afrika selatan': ['south africa'], 'selandia baru': ['new zealand'],
    'taiwan': ['taiwan'], 'hongaria': ['hungary'], 'polandia': ['poland'],
    'swedia': ['sweden'], 'norwegia': ['norway'], 'finlandia': ['finland'],
    'denmark': ['denmark'], 'portugal': ['portugal'], 'belgia': ['belgium'],
    'swiss': ['switzerland'], 'austria': ['austria'], 'irlandia': ['ireland'],
    'skotlandia': ['scotland'], 'kanada': ['canada'], 'meksiko': ['mexico'],
    'brasil': ['brazil'], 'chile': ['chile'], 'peru': ['peru'],
    'kolombia': ['colombia'], 'venezuela': ['venezuela'], 'nigeria': ['nigeria'],
    'kenya': ['kenya'], 'ethiopia': ['ethiopia'], 'ghana': ['ghana'],
    'maroko': ['morocco'], 'aljazair': ['algeria'], 'tunisia': ['tunisia'],
    'libya': ['libya'], 'sudan': ['sudan'], 'somalia': ['somalia'],
    'pakistan': ['pakistan'], 'afghanistan': ['afghanistan'],
    'bangladesh': ['bangladesh'], 'srilanka': ['sri lanka'], 'nepal': ['nepal'],
    'kazakhstan': ['kazakhstan'], 'uzbekistan': ['uzbekistan'],
    'bangkok': ['bangkok'], 'nor\'easter': ['noreaster', "nor'easter"],
    'grand canyon': ['grand canyon'], 'north carolina': ['north carolina'],
    'south carolina': ['south carolina'], 'california': ['california'],
    'texas': ['texas'], 'florida': ['florida'], 'new jersey': ['new jersey'],
    'virginia': ['virginia'], 'arizona': ['arizona'], 'nevada': ['nevada'],
    'colorado': ['colorado'], 'utah': ['utah'], 'ohio': ['ohio'],
    'michigan': ['michigan'], 'illinois': ['illinois'], 'wisconsin': ['wisconsin'],
    'minnesota': ['minnesota'], 'new york city': ['new york city', 'nyc'],
    'nyc': ['nyc', 'new york city'], 'buffalo': ['buffalo'], 'phoenix': ['phoenix'],
    'seattle': ['seattle'], 'portland': ['portland'], 'denver': ['denver'],
    'miami': ['miami'], 'atlanta': ['atlanta'], 'boston': ['boston'],
    'chicago': ['chicago'], 'houston': ['houston'], 'dallas': ['dallas'],
    'philadelphia': ['philadelphia'], 'san francisco': ['san francisco'],
    'los angeles': ['los angeles'], 'sydney': ['sydney'], 'melbourne': ['melbourne'],
    'auckland': ['auckland'], 'wellington': ['wellington'],
    'ho chi minh': ['ho chi minh city', 'hcmc', 'saigon', 'ho chi minh'],
    'ho chi minh city': ['ho chi minh', 'hcmc', 'saigon', 'ho chi minh city'],
    'hcmc': ['ho chi minh', 'ho chi minh city', 'saigon', 'hcmc'],
    'saigon': ['ho chi minh', 'ho chi minh city', 'hcmc', 'saigon'],
    'hanoi': ['hanoi', 'ha noi'],
    'ha noi': ['hanoi', 'ha noi'],
}

def _varian_cocok(kota, sumber):
    if kota in sumber:
        return True
    varian = VARIAN_KOTA_EN_ID.get(kota, [])
    return any(v in sumber for v in varian)

IBU_KOTA_NEGARA = {
    'jakarta': ['indonesia', 'jakarta'], 'london': ['inggris', 'uk', 'britain', 'england'],
    'washington': ['amerika', 'us', 'usa', 'united states'], 'tokyo': ['jepang', 'japan'],
    'beijing': ['china', 'tiongkok', 'cina'], 'seoul': ['korea', 'south korea'],
    'pyongyang': ['north korea', 'korea utara'], 'moscow': ['rusia', 'russia'],
    'paris': ['perancis', 'france'], 'berlin': ['jerman', 'germany'],
    'rome': ['italia', 'italy'], 'roma': ['italia', 'italy'], 'madrid': ['spanyol', 'spain'],
    'canberra': ['australia'], 'ottawa': ['kanada', 'canada'], 'brasilia': ['brasil', 'brazil'],
    'buenos aires': ['argentina'], 'mexico city': ['meksiko', 'mexico'],
    'new delhi': ['india'], 'islamabad': ['pakistan'], 'dhaka': ['bangladesh'],
    'bangkok': ['thailand'], 'hanoi': ['vietnam'], 'manila': ['filipina', 'philippines'],
    'kuala lumpur': ['malaysia'], 'singapore': ['singapura', 'singapore'],
    'naypyidaw': ['myanmar'], 'phnom penh': ['kamboja', 'cambodia'],
    'vientiane': ['laos'], 'bandar seri begawan': ['brunei'], 'dili': ['timor leste'],
    'cairo': ['mesir', 'egypt'], 'riyadh': ['arab saudi', 'saudi'],
    'abu dhabi': ['uni emirat arab', 'uae'], 'doha': ['qatar'], 'kuwait city': ['kuwait'],
    'amman': ['jordan'], 'beirut': ['libanon', 'lebanon'], 'damascus': ['suriah', 'syria'],
    'baghdad': ['irak', 'iraq'], 'tehran': ['iran'], 'teheran': ['iran'],
    'ankara': ['turki', 'turkey', 'turkiye'], 'istanbul': ['turki', 'turkey', 'turkiye'],
    'jerusalem': ['israel', 'yerusalem'],
    'yerusalem': ['israel', 'jerusalem'],
    'tel aviv': ['israel'],
    'haifa': ['israel'],
    'gaza': ['palestina', 'palestine'],
    'ramallah': ['palestina', 'palestine'],
    'kyiv': ['ukraina', 'ukraine'], 'kiev': ['ukraina', 'ukraine'],
    'athens': ['yunani', 'greece'], 'lisbon': ['portugal'],
    'amsterdam': ['belanda', 'netherlands'], 'brussels': ['belgia', 'belgium'],
    'bern': ['swiss', 'switzerland'], 'vienna': ['austria'], 'warsaw': ['polandia', 'poland'],
    'prague': ['ceko', 'czech'], 'budapest': ['hongaria', 'hungary'],
    'stockholm': ['swedia', 'sweden'], 'oslo': ['norwegia', 'norway'],
    'helsinki': ['finlandia', 'finland'], 'copenhagen': ['denmark'],
    'dublin': ['irlandia', 'ireland'], 'edinburgh': ['skotlandia', 'scotland'],
    'pretoria': ['afrika selatan', 'south africa'], 'cape town': ['afrika selatan', 'south africa'],
    'lagos': ['nigeria'], 'nairobi': ['kenya'], 'addis ababa': ['ethiopia'],
    'accra': ['ghana'], 'rabat': ['maroko', 'morocco'], 'algiers': ['aljazair', 'algeria'],
    'tunis': ['tunisia'], 'tripoli': ['libya'], 'khartoum': ['sudan'],
    'mogadishu': ['somalia'], 'kabul': ['afghanistan'], 'colombo': ['srilanka', 'sri lanka'],
    'kathmandu': ['nepal'], 'astana': ['kazakhstan'], 'tashkent': ['uzbekistan'],
    'sydney': ['australia'], 'melbourne': ['australia'],
    'auckland': ['selandia baru', 'new zealand'], 'wellington': ['selandia baru', 'new zealand'],
    'nagoya': ['jepang', 'japan'], 'osaka': ['jepang', 'japan'],
    'aichi-nagoya': ['jepang', 'japan'], 'aichi': ['jepang', 'japan'],
    'ho chi minh': ['vietnam', 'ho chi minh city', 'hcmc', 'saigon'],
    'ho chi minh city': ['vietnam', 'ho chi minh', 'hcmc', 'saigon'],
    'hcmc': ['vietnam', 'ho chi minh', 'ho chi minh city', 'saigon'],
    'saigon': ['vietnam', 'ho chi minh', 'ho chi minh city', 'hcmc'],
    # V6.17.85: tambah ibu kota Afrika + lainnya
    'abuja': ['nigeria'], 'kano': ['nigeria'], 'ibadan': ['nigeria'],
    'dakar': ['senegal'], 'bamako': ['mali'], 'ouagadougou': ['burkina faso'],
    'niamey': ['niger'], 'n-djamena': ["chad", "chad"], 'ndjamena': ['chad'],
    'khartoum': ['sudan'], 'juba': ['sudan selatan', 'south sudan'],
    'kinshasa': ['kongo', 'congo', 'republik demokratik kongo', 'drc'],
    'brazzaville': ['kongo', 'congo', 'republik kongo'],
    'luanda': ['angola'], 'maputo': ['mozambik', 'mozambique'],
    'harare': ['zimbabwe'], 'lusaka': ['zambia'], 'lilongwe': ['malawi'],
    'gaborone': ['botswana'], 'windhoek': ['namibia'],
    'maseru': ['lesotho'], 'mbabane': ['eswatini', 'swaziland'],
    'antananarivo': ['madagaskar', 'madagascar'],
    'kigali': ['rwanda'], 'bujumbura': ['burundi'], 'gitega': ['burundi'],
    'kampala': ['uganda'], 'dodoma': ['tanzania'], 'dar es salaam': ['tanzania'],
    'asmara': ['eritrea'], 'djibouti': ['djibouti'],
    'mogadishu': ['somalia'],
    'moroni': ['komoro', 'comoros'],
    'port louis': ['mauritius'], 'victoria': ['seychelles'],
    'libreville': ['gabon'], 'malabo': ['guinea ekuatorial', 'equatorial guinea'],
    'yaounde': ['kamerun', 'cameroon'], 'bangui': ['republik afrika tengah', 'central african republic'],
    'conakry': ['guinea'], 'bissau': ['guinea bissau'],
    'monrovia': ['liberia'], 'freetown': ['sierra leone'],
    'banjul': ['gambia'], 'nouakchott': ['mauritania'],
    'praia': ['tanjung verde', 'cape verde'],
    'sao tome': ['sao tome dan principe'],
    'algiers': ['aljazair', 'algeria'],
    'rabat': ['maroko', 'morocco'], 'casablanca': ['maroko', 'morocco'],
    'tunis': ['tunisia'], 'tripoli': ['libya'], 'benghazi': ['libya'],
    'cairo': ['mesir', 'egypt'], 'alexandria': ['mesir', 'egypt'],
    'khartoum': ['sudan'],
    'addis ababa': ['ethiopia'], 'nairobi': ['kenya'], 'mombasa': ['kenya'],
    'kampala': ['uganda'], 'kigali': ['rwanda'],
    'pretoria': ['afrika selatan', 'south africa'],
    'cape town': ['afrika selatan', 'south africa'],
    'johannesburg': ['afrika selatan', 'south africa'],
    'durban': ['afrika selatan', 'south africa'],
    'accra': ['ghana'], 'lagos': ['nigeria'], 'abuja': ['nigeria'],
    'kano': ['nigeria'],
    # Tambahan Asia & lain
    'yangon': ['myanmar'], 'mandalay': ['myanmar'],
    'chiang mai': ['thailand'], 'phuket': ['thailand'],
    'da nang': ['vietnam'], 'hoi an': ['vietnam'], 'hue': ['vietnam'],
    'cebu': ['filipina', 'philippines'], 'davao': ['filipina', 'philippines'],
    'penang': ['malaysia'], 'johor bahru': ['malaysia'],
    'surabaya': ['indonesia'], 'bandung': ['indonesia'], 'medan': ['indonesia'],
    'semarang': ['indonesia'], 'makassar': ['indonesia'], 'denpasar': ['indonesia'],
    'balikpapan': ['indonesia'], 'samarinda': ['indonesia'], 'pontianak': ['indonesia'],
    'banjarmasin': ['indonesia'], 'manado': ['indonesia'], 'jayapura': ['indonesia'],
    'tarakan': ['indonesia'], 'tanjung selor': ['indonesia'], 'nunukan': ['indonesia'],
    'palembang': ['indonesia'], 'pekanbaru': ['indonesia'], 'padang': ['indonesia'],
    'yogyakarta': ['indonesia'], 'solo': ['indonesia'], 'malang': ['indonesia'],
}

def _kota_ibu_kota_provinsi_di_materi(kota, sumber):
    kota_low = (kota or '').lower().strip()
    sumber_low = (sumber or '').lower()
    for prov, ibukota in KAMUS_PROVINSI_IBUKOTA.items():
        if kota_low == ibukota and prov in sumber_low:
            return True
    return False

def _kota_mirip_di_materi(kota, sumber, ambang=0.80):
    if not kota or not sumber:
        return None
    kota_low = kota.lower().strip()
    sumber_low = sumber.lower()
    kandidat_kota = set()
    for k in KOTA_INDONESIA_DATELINE:
        kandidat_kota.add(k)
    for k in KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN:
        kandidat_kota.add(k)
    for k in IBU_KOTA_NEGARA.keys():
        kandidat_kota.add(k)
    for k in VARIAN_KOTA_EN_ID.keys():
        kandidat_kota.add(k)
    for k in KAMUS_TIM_LIGA_NEGARA.keys():
        kandidat_kota.add(k)
    kata_materi = set(re.findall(r'\b[a-z]{4,}\b', sumber_low))
    for kandidat in kandidat_kota:
        if kandidat in kata_materi:
            rasio = SequenceMatcher(None, kota_low, kandidat).ratio()
            if rasio >= ambang:
                return kandidat
    for kata in kata_materi:
        if abs(len(kata) - len(kota_low)) > 2:
            continue
        rasio = SequenceMatcher(None, kota_low, kata).ratio()
        if rasio >= ambang:
            return kata
    return None

def cek_dateline(isi, user_content):
    m = re.match(r'^([A-Z][^\n\-–—]{1,60}?)\s+[-–—]\s+', (isi or '').strip())
    if not m:
        return None
    dp = m.group(1).strip().lower()
    if dp == 'indonesia':
        return 'dateline INDONESIA tanpa kota - wajib kota/provinsi'
    bag = [x.strip() for x in dp.split(',') if x.strip()]
    kota = bag[0] if bag else ''
    wilayah = bag[1] if len(bag) > 1 else ''
    sumber = re.sub(r'\s+', ' ', (user_content or '')).lower()
    if kota in IBU_KOTA_NEGARA:
        return None
    if kota in KOTA_INDONESIA_DATELINE:
        return None
    if _kota_ibu_kota_provinsi_di_materi(kota, sumber):
        return None
    kota_mirip = _kota_mirip_di_materi(kota, sumber, ambang=0.80)
    if kota_mirip:
        return None
    if kota and not _varian_cocok(kota, sumber):
        return 'kota dateline "' + kota + '" tidak ada di materi sumber'
    if 'kalimantan utara' in wilayah:
        daftar = KALTARA_WORDS + ['sebatik', 'tanjung selor', 'tana tidung']
        if kota and not any(k in kota for k in daftar):
            return 'klaim KALTARA tapi kota "' + kota + '" bukan wilayah Kaltara'
    return None

# ══════════════════════════════════════════════════════
# V6.17.82: PARSE_AI_JSON — strip teks setelah JSON valid
# Handle error "Extra data: line 3 column 1"
# ══════════════════════════════════════════════════════

def parse_ai_json(text):
    """
    V6.17.82: Parse JSON dari AI dengan toleransi ekstra teks.
    - Strip markdown code fence
    - Cari objek JSON pertama { ... } dan abaikan teks setelahnya
    - Raise ValueError kalau tidak ada JSON valid
    """
    t = (text or '').strip()
    if not t:
        raise ValueError('parse_ai_json: teks kosong')
    # Strip markdown code fence
    if t.startswith('```'):
        t = re.sub(r'^```[a-zA-Z]*\s*', '', t)
        t = re.sub(r'\s*```\s*$', '', t)
    # Cari objek JSON pertama
    start = t.find('{')
    if start == -1:
        raise ValueError('parse_ai_json: tidak ada { di output AI')
    # Hitung kurung kurawal untuk menemukan akhir objek JSON pertama
    depth = 0
    in_str = False
    escape = False
    end = -1
    for i in range(start, len(t)):
        ch = t[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end == -1:
        raise ValueError('parse_ai_json: JSON tidak lengkap (kurung tidak seimbang)')
    json_str = t[start:end]
    return json.loads(json_str)

POLA_PERSEN = re.compile(r'(\d[\d\.,]*)\s+persen\b', re.IGNORECASE)

def ada_persen_kata(teks):
    return bool(POLA_PERSEN.search(teks or ''))

def perbaiki_persen(teks):
    return POLA_PERSEN.sub(lambda m: m.group(1).rstrip('.,') + '%', teks or '')

# V6.17.86: buang 'gaji' dari JANJI_HARGA (false positive)
JANJI_HARGA = ['harga', 'tarif', 'biaya', 'berapa', 'sewa']

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

KATA_LARANG_GAMBAR_HARD = [
    'animal', 'dog', 'cat', 'bird', 'monkey', 'elephant', 'tiger', 'lion',
    'snake', 'crocodile', 'lizard', 'frog', 'shark', 'whale',
    'insect', 'butterfly', 'bee', 'spider', 'rat', 'mouse', 'horse', 'cow',
    'goat', 'sheep', 'pig', 'chicken', 'rooster', 'duck', 'goose', 'rabbit',
    'deer', 'bear', 'wolf', 'fox', 'eagle', 'parrot', 'owl', 'kucing',
    'anjing', 'burung', 'ular', 'kuda', 'sapi', 'ayam', 'bebek', 'kambing',
    'harimau', 'singa', 'gajah', 'monyet', 'buaya',
    'mosque', 'masjid', 'church', 'gereja', 'cathedral', 'temple', 'pura',
    'vihara', 'pagoda', 'shrine', 'monastery',
    'shoes', 'shoe', 'sneaker', 'sneakers', 'sandal', 'sandals', 'slipper',
    'slippers', 'footwear', 'high heels', 'stiletto', 'sendal', 'sepatu',
]

# V6.17.95: konteks perikanan → "fish"/"ikan" boleh (pedagang ikan, nelayan, perikanan)
KONTEKS_IKAN_DIIZINKAN = [
    'pedagang ikan', 'ikan segar', 'ikan asin', 'ikan hias',
    'nelayan', 'perikanan', 'budidaya ikan', 'tambak',
    'hasil laut', 'seafood', 'ikan tuna', 'ikan tongkol',
    'ikan bandeng', 'ikan lele', 'ikan nila', 'ikan mujair',
    'pasar ikan', 'pelelangan ikan', 'kapal ikan', 'perahu nelayan',
    'keramba', 'jaring ikan', 'pancing', 'memancing',
]

def _konteks_ikan_diizinkan(teks):
    """V6.17.95: cek apakah konteks perikanan → ikan boleh."""
    t = (teks or '').lower()
    for k in KONTEKS_IKAN_DIIZINKAN:
        if k in t:
            return True
    return False

def cek_deskripsi_gambar(deskripsi, konteks_materi=''):
    d = (deskripsi or '').lower()
    # V6.17.95: kalau konteks perikanan → skip cek ikan/fish
    konteks_perikanan = _konteks_ikan_diizinkan(konteks_materi)
    for k in KATA_HEWAN_SLUG:
        # V6.17.95: fish/ikan diizinkan kalau konteks perikanan
        if k in ('fish', 'ikan') and konteks_perikanan:
            continue
        if k.endswith('_') or k.endswith('-'):
            if k in d:
                return 'deskripsi gambar memuat kata hewan terlarang: ' + k
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', d):
                return 'deskripsi gambar memuat kata hewan terlarang: ' + k
    for k in KATA_LARANG_GAMBAR_HARD:
        if k.endswith('_') or k.endswith('-'):
            if k in d:
                return 'deskripsi gambar memuat kata terlarang: ' + k
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', d):
                return 'deskripsi gambar memuat kata terlarang: ' + k
    return None

def cek_url_gambar_hewan(url):
    if not url:
        return None
    low = url.lower()
    for k in KATA_HEWAN_SLUG:
        if k.endswith('_') or k.endswith('-'):
            if k in low:
                return 'url gambar memuat kata hewan: ' + k
        else:
            if re.search(r'\b' + re.escape(k) + r'\b', low):
                return 'url gambar memuat kata hewan: ' + k
    for k in ['animal', 'puppy', 'kitten', 'wildlife', 'pet-', '-pet',
              'dog-', '-dog', 'cat-', '-cat', 'bird-', '-bird']:
        if k in low:
            return 'url gambar memuat kata hewan: ' + k
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

# ══════════════════════════════════════════════════════
# V6.17.85: skor_domestik tolak negara asing tanpa konteks Indonesia
# V6.17.90: skor_domestik tolak aktor non-breaking (selebriti/artis)
# V6.17.97: prabowo + ASEAN + kabut asap → jangan tolak
# ══════════════════════════════════════════════════════

def _ada_konteks_indonesia_kuat(teks):
    """V6.17.85: cek apakah teks punya konteks Indonesia yang kuat."""
    t = (teks or '').lower()
    hit = 0
    for k in INDO_GEO:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            hit += 1
            if hit >= 2:
                return True
    # Nama tokoh Indonesia
    for tokoh in NAMA_TOKOH_INDONESIA:
        if re.search(r'\b' + re.escape(tokoh) + r'\b', t):
            return True
    # Lembaga Indonesia (kecuali TNI)
    for lem in LEMBAGA_INDONESIA:
        if lem == 'tni':
            continue
        if len(lem) <= 4:
            if re.search(r'\b' + re.escape(lem) + r'\b', t):
                return True
        else:
            if lem in t:
                return True
    # BMKG, BNPB, Basarnas, dll
    for k in ['bmkg', 'bnpb', 'basarnas', 'bpbd', 'kemensos', 'kemenkes']:
        if k in t:
            return True
    return False

def _ada_negara_asing_dominan(teks):
    """V6.17.85: cek apakah teks dominan tentang negara asing.
    Return nama negara kalau ada, '' kalau tidak."""
    t = (teks or '').lower()
    for negara in NEGARA_ASING:
        if len(negara) <= 4:
            if re.search(r'\b' + re.escape(negara) + r'\b', t):
                return negara
        else:
            if negara in t:
                return negara
    return ''

# ══════════════════════════════════════════════════════
# V6.17.97: PRABOWO + ASEAN + KABUT ASAP → JANGAN TOLAK
# Konteks: kabut asap lintas batas Malaysia/Indonesia sering dibahas
# Prabowo di forum ASEAN. Jangan tolak hanya karena "prabowo" + asing.
# ══════════════════════════════════════════════════════

KATA_KABUT_ASAP = [
    'kabut asap', 'haze', 'asap lintas batas', 'transboundary haze',
    'karhutla lintas', 'kabut asap lintas',
]

def _ada_konteks_kabut_asap_asean(teks):
    """V6.17.97: cek apakah teks punya konteks kabut asap + asean.
    Kalau iya → konteks Prabowo + asing SAH (jangan tolak)."""
    t = (teks or '').lower()
    ada_kabut = any(k in t for k in KATA_KABUT_ASAP)
    ada_asean = any(k in t for k in ('asean', 'malaysia', 'singapura', 'brunei',
                                      'thailand', 'lintas batas', 'transboundary'))
    ada_prabowo = 'prabowo' in t
    # Kalau kabut asap + ASEAN (dengan/tanpa Prabowo) → jangan tolak
    if ada_kabut and ada_asean:
        return True
    if ada_prabowo and ada_asean and ada_kabut:
        return True
    return False

def skor_domestik(title, summary):
    t = (title + ' ' + summary).lower()
    if any(w in t for w in KATA_ANALISIS):
        return 0
    # V6.17.90: tolak kalau aktor utama selebriti/artis/influencer (DiCaprio dll)
    aktor_nb = _ada_aktor_non_breaking(t)
    if aktor_nb:
        return 0
    # V6.17.97: pengecualian kabut asap + ASEAN → jangan tolak
    if _ada_konteks_kabut_asap_asean(t):
        pass  # lanjut hitung skor, jangan tolak
    else:
        # V6.17.85: TOLAK kalau dominan negara asing & tanpa konteks Indonesia
        negara_asing = _ada_negara_asing_dominan(t)
        if negara_asing and not _ada_konteks_indonesia_kuat(t):
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
    # V6.17.90: tolak aktor non-breaking juga di skor dunia (konsisten)
    aktor_nb = _ada_aktor_non_breaking(t)
    if aktor_nb:
        return 0
    for k in BREAKING_INT_TOLAK:
        if k in t:
            return 0
    if 'earthquake' in t or 'gempa' in t or ' quake' in t or 'quake ' in t:
        mag = ambil_magnitude(t)
        if mag is None:
            return 0
        if mag < GEMPA_DUNIA_MIN:
            return 0
        skor = 60 + min(int(mag), 9)
        hit = sum(1 for k in DUNIA_KRITIS if k in t)
        if hit:
            skor += 30 + (hit - 1) * 8
        return skor
    hit = sum(1 for k in DUNIA_KRITIS if k in t)
    if hit >= 2:
        return 30 + (hit - 1) * 8
    return 0

PANGKAT_TNI_POLRI = [
    'jenderal', 'letnan jenderal', 'letjen', 'mayor jenderal', 'mayjen',
    'brigadir jenderal', 'brigjen', 'kolonel', 'letnan kolonel', 'letkol',
    'mayor', 'kapten', 'lettu', 'letda', 'letnan', 'pembantu letnan', 'pelda',
    'pelton', 'peltu', 'sersan', 'kopral', 'prajurit', 'akbp', 'akp', 'iptu',
    'ipda', 'bripka', 'brigpol', 'bripda', 'komisaris besar', 'kombes',
    'ajun komisaris besar', 'komisaris', 'kompol', 'ajun komisaris',
    'inspektur', 'inspektur polisi satu', 'inspektur polisi dua',
    'ajun inspektur', 'bharada', 'bharatu', 'bharaka', 'abrip',
]

INSTITUSI_PUSAT_LEBIH_LONGGAR = [
    'kementerian', 'kemenko', 'kemen', 'bank indonesia', 'ojk', 'kpk',
    'bnpb', 'basarnas', 'bulog', 'pertamina', 'pln', 'telkom',
]

INSTITUSI_LOKAL_BUTUH_NAMA = [
    'dinas', 'kantor',
    'polres', 'polsek', 'polda', 'kodam', 'korem', 'kodim',
    'koramil', 'kejaksaan', 'kejari', 'kejati', 'pengadilan', 'bawaslu',
    'kpu', 'kppu', 'kppn', 'kpp', 'bpjs', 'perum', 'peruri', 'pelindo',
    'angkasa pura',
]

INSTITUSI_BUTUH_NAMA = INSTITUSI_LOKAL_BUTUH_NAMA + INSTITUSI_PUSAT_LEBIH_LONGGAR

KATA_KERJA_NARASUMBER = [
    'mengatakan', 'menyatakan', 'menjelaskan', 'menuturkan', 'mengungkapkan',
    'mengimbau', 'menghimbau', 'meminta', 'menegaskan', 'menambahkan',
    'mengatakan bahwa', 'menyampaikan', 'menekankan', 'mengajak', 'memastikan',
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

KOTA_LOKAL_KALTARA = ['tarakan', 'nunukan', 'bulungan', 'malinau',
                      'tana tidung', 'tanjung selor', 'sesayap', 'sebatik']

def _adalah_berita_kaltara(judul, isi):
    gab = ((judul or '') + ' ' + (isi or '')).lower()
    return any(re.search(r'\b' + re.escape(k) + r'\b', gab)
               for k in KOTA_LOKAL_KALTARA)

def cek_narasumber_tanpa_nama(isi, kategori='', judul=''):
    if not isi:
        return None
    if kategori in ('internasional', 'internasional_asean', 'internasional_tt'):
        return None
    if kategori == 'kesehatan':
        return None
    if kategori in ('otomotif', 'teknologi'):
        return None
    gab_kaltara = ((judul or '') + ' ' + (isi or '')).lower()
    is_kaltara_berita = any(re.search(r'\b' + re.escape(k) + r'\b', gab_kaltara)
                            for k in KOTA_LOKAL_KALTARA)
    if kategori == 'daerah' and is_kaltara_berita:
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
                return ('pangkat TNI/Polri "' + pangkat + '" muncul tanpa nama orang')
        pola2 = re.compile(
            r'\b' + re.escape(pangkat) + r'\s*,\s*('
            + '|'.join(re.escape(k) for k in KATA_KERJA_NARASUMBER) + r')\b',
            re.IGNORECASE
        )
        if pola2.search(teks):
            return ('pangkat TNI/Polri "' + pangkat + '" diikuti koma langsung kata kerja (tanpa nama)')
    return None

KATA_BUKAN_BERITA = [
    'zodiak', 'horoskop', 'ramalan bintang', 'ramalan cinta', 'ramalan nasib',
    'ramalan zodiak', 'shio', 'primbon', 'arti mimpi', 'artinya mimpi',
    'pertanda baik', 'pertanda buruk', 'keberuntungan hari ini', 'peruntungan',
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

KATA_LUAR_NEGERI_WAJIB = [
    'amerika', 'united states', ' u.s', 'usa', 'washington',
    'rusia', 'russia', 'moskow', 'moscow', 'ukraina', 'ukraine',
    'eropa', 'europe', 'jerman', 'germany', 'perancis', 'france', 'inggris',
    'britain', 'united kingdom', 'italia', 'italy', 'spanyol', 'spain',
    'paris', 'berlin', 'london', 'timur tengah', 'middle east', 'gaza',
    'israel', 'palestina', 'iran', 'iraq', 'suriah', 'syria', 'saudi',
    'yaman', 'yemen', 'uni emirat', 'emirates', 'qatar', 'kuwait', 'libanon',
    'jordan', 'turki', 'turkey', 'mesir', 'egypt', 'jepang', 'japan', 'china',
    'tiongkok', 'korea', 'seoul', 'pyongyang', 'india', 'delhi', 'australia',
    'kanada', 'canada', 'meksiko', 'mexico', 'brasil', 'brazil', 'argentina',
    'afrika', 'africa', 'nigeria', 'kenya', 'pbb', 'united nations', 'nato',
    'asean', 'who', 'unicef', 'bank dunia', 'world bank', 'imf', 'g20', 'g7',
    'brics', 'pemilu amerika', 'us election', 'parlemen eropa', 'uni eropa',
    'european union', 'taiwan', 'kamboja', 'cambodia', 'thailand',
    'vietnam', 'filipina', 'singapura', 'myanmar', 'laos', 'brunei',
    'xinhua', 'cgtn', 'global times', 'scmp', 'south china morning post',
    'nhk', 'korea herald', 'japan times', 'times of india',
    'nagoya', 'aichi-nagoya', 'aichi', 'osaka',
]

KATA_ASEAN_WAJIB = [
    'asean', 'malaysia', 'thailand', 'vietnam', 'filipina', 'philippines',
    'singapura', 'singapore', 'myanmar', 'kamboja', 'cambodia', 'laos',
    'brunei', 'timor leste', 'jakarta', 'bangkok', 'manila', 'kuala lumpur',
    'hanoi', 'indonesia',
]

KATA_TT = [
    'timur tengah', 'middle east', 'gaza', 'israel', 'palestina', 'iran',
    'iraq', 'suriah', 'syria', 'saudi', 'yaman', 'yemen', 'uni emirat',
    'emirates', 'qatar', 'kuwait', 'libanon', 'jordan', 'turki',
    'hamas', 'hezbollah', 'idf', 'netanyahu', 'west bank', 'teheran',
    'lebanon', 'damaskus', 'beirut', 'golan', 'sinai',
    'al arabiya', 'gulf news', 'jerusalem post', 'middle east eye',
]

KATA_EKONOMI_DOMESTIK = [
    'ihsg', 'idx', 'bei', 'bursa efek', 'saham indonesia', 'obligasi',
    'reksa dana', 'sbn', 'sun', 'ori', 'sukuk', 'obligasi syariah',
    'surat utang negara', 'yield', 'imbal hasil',
    'bank indonesia', 'bi rate', 'bi7drr', 'suku bunga acuan',
    'ojk', 'lps', 'penjaminan simpanan', 'kredit', 'kpr', 'leasing',
    'multifinance', 'asuransi', 'bpjs ketenagakerjaan',
    'kripto indonesia', 'aset digital',
    'rupiah', 'kurs rupiah', 'nilai tukar rupiah', 'idr',
    'inflasi indonesia', 'inflasi inti', 'deflasi', 'bi 7-day',
    'apbn', 'apbd', 'defisit anggaran', 'surplus anggaran',
    'pajak', 'ppn', 'pph', 'bea masuk', 'cukai', 'tax amnesty',
    'pengampunan pajak', 'subsidi', 'subsidi bbm', 'subsidi listrik',
    'subsidi pupuk', 'blt', 'bansos', 'pkh', 'kartu sembako',
    'kemenkeu', 'kementerian keuangan', 'djp', 'bea cukai',
    'cadangan devisa', 'devisa hasil ekspor', 'dhe',
    'neraca pembayaran', 'current account', 'transaksi berjalan',
    'beras', 'padi', 'gabah', 'jagung', 'kedelai', 'gandum',
    'cabai', 'bawang', 'gula', 'minyak goreng', 'telur', 'ayam',
    'daging', 'sapi', 'kambing', 'ikan', 'udang', 'tuna',
    'bulog', 'harga pangan', 'ketahanan pangan', 'petani', 'nelayan',
    'sawah', 'tambak', 'pertanian', 'perikanan', 'peternakan',
    'sawit', 'cpo', 'karet', 'kakao', 'kopi', 'teh', 'rempah',
    'batu bara', 'nikel', 'tembaga', 'emas', 'timah', 'bauksit',
    'minyak', 'gas', 'lng', 'pertamina', 'pln', 'tarif listrik',
    'tambang', 'smelter', 'hilirisasi', 'kawasan industri', 'kek',
    'manufaktur', 'pabrik', 'industri', 'semen', 'baja', 'tekstil',
    'garmen', 'sepatu', 'makanan minuman', 'rokok', 'tembakau',
    'pupuk', 'pestisida', 'alat pertanian', 'otomotif nasional',
    'pmi', 'indeks manajer pembelian', 'ikk', 'indeks keyakinan konsumen',
    'ekspor indonesia', 'impor indonesia', 'neraca dagang',
    'ekspor', 'impor', 'bea cukai', 'karantina',
    'barang ilegal', 'selundup', 'penyelundupan', 'impor ilegal',
    'ekspor ilegal', 'dumping', 'antidumping', 'safeguard',
    'fta', 'rcep', 'ieucepa',
    'phk', 'pesangon', 'upah minimum', 'umr', 'ump', 'umk',
    'serikat pekerja', 'demo buruh', 'tki', 'pmi', 'pekerja migran',
    'pelatihan kerja', 'blk', 'kartu prakerja', 'pekerja asing',
    'tenaga kerja indonesia', 'pengangguran',
    'umkm', 'bumdes', 'koperasi', 'kredit usaha rakyat', 'kur',
    'ekonomi digital', 'e-wallet', 'qris', 'bi-fast',
    'marketplace', 'e-commerce', 'startup indonesia',
    'fintech', 'p2p lending', 'pinjol', 'pinjaman online',
    'properti', 'perumahan', 'apartemen', 'rusun', 'kpr subsidi',
    'developer', 'pengembang', 'kawasan ekonomi khusus',
    'infrastruktur', 'tol', 'pelabuhan', 'bandara', 'kereta',
    'pasar modal', 'pasar uang', 'pasar tradisional', 'pasar modern',
    'ritel', 'grosir', 'retail', 'konsumen', 'daya beli',
    'konsumsi rumah tangga', 'penjualan ritel',
    'pasar karbon', 'carbon credit', 'esg', 'ekonomi hijau',
    'transisi energi', 'net zero', 'energi terbarukan',
    'ekonomi syariah', 'keuangan syariah', 'bank syariah',
]

KATA_EKONOMI_ASING = [
    'pertumbuhan ekonomi', 'growth', 'economic growth', 'gdp', 'pdb',
    'resesi', 'resesi teknis', 'kontraksi', 'ekspansi', 'stagflasi',
    'hiperinflasi', 'resilient',
    'wall street', 'dow jones', 'nasdaq', 's&p 500', 'ftse', 'nikkei',
    'hang seng', 'kospi', 'sse composite', 'szse', 'sti', 'set index',
    'us treasury', 'obligasi global', 'bond market',
    'fed', 'the fed', 'federal reserve', 'fed rate', 'ecb', 'boj',
    'bank of england', 'boe', 'pboc', 'bank sentral',
    'dovish', 'hawkish', 'quantitative easing', 'qe', 'pelonggaran',
    'pengetatan', 'suku bunga global',
    'dolar', 'usd', 'euro', 'yen', 'yuan', 'renminbi', 'won',
    'ringgit', 'baht', 'dollar index',
    'kripto', 'bitcoin', 'ethereum', 'blockchain',
    'minyak mentah', 'brent', 'wti', 'opec', 'oil embargo',
    'emas global', 'perak', 'tembaga global', 'litium',
    'gandum global', 'jagung global', 'kedelai global',
    'tesla', 'toyota', 'byd', 'apple', 'microsoft', 'nvidia',
    'alphabet', 'amazon', 'meta', 'boeing', 'airbus',
    'pfizer', 'moderna', 'astrazeneca',
    'tsmc', 'samsung', 'semikonduktor', 'chip', 'chip war',
    'hsbc', 'jpmorgan', 'citigroup', 'goldman sachs',
    'bank of america', 'morgan stanley', 'wells fargo',
    'deutsche bank', 'barclays', 'bnp paribas',
    'tarif', 'tariff', 'sanctions', 'sanksi ekonomi',
    'perang dagang', 'trade war', 'tarif as china',
    'kerja sama dagang', 'trade deal', 'bilateral', 'multilateral',
    'wto', 'imf', 'world bank', 'bank dunia', 'adb',
    'g20', 'g7', 'brics', 'apec',
    'supply chain', 'rantai pasok', 'logistik global',
    'manufaktur global', 'factory activity', 'pmi global',
    'pertambangan global', 'mining', 'smelter global',
    'baterai', 'battery', 'kendaraan listrik global',
    'farmasi global', 'pertahanan', 'defense industry',
    'unemployment', 'pengangguran global', 'phk global',
    'tech layoff', 'visa kerja', 'pekerja migran global',
    'index saham', 'stock market', 'stock index',
    'market rally', 'market crash', 'bear market', 'bull market',
    'ipo global', 'merger global', 'akuisisi global',
    'valuasi global', 'pendanaan global', 'venture capital',
    'crypto market', 'fintech global', 'e-commerce global',
    'digital economy', 'big tech',
    'carbon market', 'green economy', 'renewable energy',
    'energy transition', 'net zero global',
]

KATA_EKONOMI_UMUM = [
    'ekonomi', 'economic', 'economy', 'economist',
    'inflasi', 'inflation', 'deflasi', 'ekspor', 'impor',
    'perdagangan', 'trade', 'industri', 'industry',
    'perusahaan', 'company', 'bisnis', 'business',
    'saham', 'stock', 'obligasi', 'bond',
    'bank', 'banking', 'keuangan', 'finance',
    'investasi', 'investment', 'modal', 'capital',
    'harga', 'price', 'pasar', 'market',
    'penjualan', 'sales', 'pendapatan', 'revenue',
    'laba', 'profit', 'rugi', 'loss',
    'utang', 'debt', 'kredit', 'credit',
    'pajak', 'tax', 'subsidi', 'subsidy',
    'anggaran', 'budget', 'belanja', 'spending',
]

KATA_EKONOMI_WAJIB = KATA_EKONOMI_DOMESTIK + KATA_EKONOMI_ASING + KATA_EKONOMI_UMUM

KATA_EKONOMI_KUAT_TENTUKAN = [
    'ojk', 'edukasi keuangan', 'literasi keuangan', 'investasi',
    'reksa dana', 'obligasi', 'deposito', 'saham', 'ihsg', 'idx',
    'bank indonesia', 'bi rate', 'suku bunga', 'inflasi', 'deflasi',
    'apbn', 'apbd', 'pajak', 'ekspor', 'impor', 'neraca dagang',
    'umkm', 'kredit', 'fintech', 'pinjol', 'p2p lending',
    'properti', 'perumahan', 'kpr', 'developer',
    'ekonomi', 'bisnis', 'keuangan', 'pasar modal', 'bursa',
]

KATA_POLITIK_HUKUM_LOKAL = [
    'tersangka', 'korupsi', 'kpk', 'kejaksaan', 'pengadilan', 'sidang',
    'dakwaan', 'hukuman', 'pidana', 'penjara', 'ditahan', 'dpr', 'presiden',
    'menteri', 'gubernur', 'walikota', 'bupati', 'pileg', 'pilpres', 'pilkada',
    'partai', 'kampanye', 'demonstrasi', 'unjuk rasa',
]

NAMA_TOKOH_INDONESIA = [
    'prabowo', 'gibran', 'jokowi', 'joko widodo', 'megawati', 'anies',
    'anies baswedan', 'ganjar', 'ganjar pranowo', 'ridwan kamil', 'ahok',
    'basuki tjahaja', 'sri mulya', 'sri mulyani', 'mahfud', 'mahfud md',
    'erick thohir', 'agus yudhoyono', 'sby', 'susilo bambang', 'puan maharani',
    'bambang soesatyo', 'bamsoet', 'listyo sigit', 'sigit listyo',
    'yudo margono', 'abdul muhaimin', 'muhaimin iskandar', 'cak imin',
    'airlangga hartarto', 'luhut', 'luhut pandjaitan', 'tito karnavian',
    'budi gunawan', 'bahlil', 'bahlil lahadalia', 'dito ariotedjo',
    'sandiaga', 'sandiaga uno', 'yassierli',
    'nadiem', 'nadiem makarim', 'hadi tjahjanto',
    'zulkifli hasan', 'zulhas', 'sufmi dasco', 'dasco', 'ahmad muzani',
    'muzani', 'yandri susanto', 'muhammad yusril', 'yusril ihza', 'pratikno',
    'sri mulyani indrawati', 'menteri keuangan', 'kapolri', 'panglima tni',
    'maruf amin', 'jenderal agus subiyanto', 'agus subiyanto',
]

LEMBAGA_INDONESIA = [
    'kpk', 'dpr', 'mpr', 'dpd', 'dprd', 'kemenkeu', 'kemendag', 'kemenhub',
    'kemendikbud', 'kemenkes', 'kemnaker', 'kemenkumham', 'kemensos', 'kemenag',
    'kemenparekraf', 'kemenlu', 'kemenhan', 'kemendagri', 'kemenko',
    'kemenpppa', 'kemenpora', 'polri', 'tni', 'kejagung', 'kejaksaan agung',
    'mahkamah agung', 'mahkamah konstitusi', 'mk', 'bawaslu', 'kpu', 'ojk',
    'bank indonesia', 'bi', 'bpk', 'bpn', 'bnpb', 'basarnas', 'bpom', 'bssn',
    'bin', 'wantannas', 'setkab', 'setneg', 'perpres', 'inpres', 'keppres',
]

PROVINSI_INDONESIA_LAIN = [
    'aceh', 'sumatera utara', 'sumut', 'sumatera barat', 'sumbar',
    'riau', 'jambi', 'bengkulu', 'sumatera selatan', 'sumsel',
    'bangka belitung', 'babel', 'lampung', 'banten',
    'jawa barat', 'jabar', 'jawa tengah', 'jateng',
    'di yogyakarta', 'diy', 'jawa timur', 'jatim',
    'bali', 'nusa tenggara barat', 'ntb', 'nusa tenggara timur', 'ntt',
    'maluku', 'maluku utara', 'malut',
    'papua', 'papua barat', 'papua selatan', 'papua tengah',
    'papua pegunungan', 'papua barat daya',
    'sulawesi utara', 'sulut', 'sulawesi tengah', 'sulteng',
    'sulawesi selatan', 'sulsel', 'sulawesi tenggara', 'sultra',
    'gorontalo', 'sulawesi barat', 'sulbar',
]

KALIMANTAN_PROVINSI = [
    'kalimantan', 'kalimantan barat', 'kalbar',
    'kalimantan tengah', 'kalteng',
    'kalimantan selatan', 'kalsel',
    'kalimantan timur', 'kaltim',
    'kalimantan utara', 'kaltara',
]

KOTA_INDONESIA_DATELINE = [
    'jakarta', 'surabaya', 'bandung', 'semarang', 'yogyakarta', 'medan',
    'palembang', 'makassar', 'denpasar', 'balikpapan', 'samarinda',
    'pontianak', 'banjarmasin', 'palangka raya', 'manado', 'ambon',
    'jayapura', 'kupang', 'mataram', 'tarakan', 'tanjung selor', 'nunukan',
    'malinau', 'bulungan', 'tana tidung', 'bogor', 'depok', 'tangerang',
    'bekasi', 'malang', 'solo', 'surakarta', 'pekanbaru', 'padang', 'bengkulu',
    'lampung', 'bandar lampung', 'batam', 'gorontalo', 'palu', 'kendari', 'mamuju',
    'selumit', 'selumit pantai', 'juata', 'karang anyar', 'karang balik',
    'kampung enam', 'pamusian', 'sebengkok', 'gunung lingkas', 'karang harapan',
    'kaltara',
]

KATA_LOKAL_KALTARA = [
    'tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau', 'tana tidung',
    'sesayap', 'juata', 'tanjung selor', 'sebatik', 'kayu putih',
]

def cek_kategori_cocok(kategori_target, teks):
    if not teks:
        return None
    t = teks.lower()
    if kategori_target == 'internasional_asean':
        if any(k in t for k in KATA_ASEAN_WAJIB):
            return None
        return 'kategori asean tapi tidak ada kata kunci asean'
    if kategori_target in ('internasional', 'internasional_tt'):
        if any(k in t for k in KATA_LUAR_NEGERI_WAJIB):
            return None
        return ('kategori ' + kategori_target + ' tapi tidak ada kata luar negeri')
    if kategori_target == 'ekonomi':
        if any(k in t for k in KATA_EKONOMI_WAJIB):
            return None
        return 'kategori ekonomi tapi tidak ada kata ekonomi'
    if kategori_target == 'nasional':
        if any(k in t for k in KATA_POLITIK_HUKUM_LOKAL):
            return None
        return None
    return None

def _kpk_konteks_indonesia(teks):
    t = (teks or '').lower()
    if 'kpk' not in t:
        return False
    konteks = ['kpk indonesia', 'komisi pemberantasan korupsi', 'kpk ri',
               'kpk republik indonesia', 'kpk tangkap', 'kpk periksa',
               'kpk sidik', 'kpk jerat', 'kpk tetapkan']
    for k in konteks:
        if k in t:
            return True
    for m in re.finditer(r'kpk', t):
        awal = max(0, m.start() - 50)
        akhir = min(len(t), m.end() + 50)
        sekitar = t[awal:akhir]
        if any(k in sekitar for k in ('indonesia', 'ri ', 'jakarta', 'korupsi',
                                       'pemberantasan', 'tersangka', 'menteri')):
            return True
    return False

# V6.17.93: kata jabatan yang sering SALAH TANGKAP sebagai tokoh Indonesia
JABATAN_AMBIGU_INDONESIA = [
    'menteri keuangan', 'menteri luar negeri', 'menteri pertahanan',
    'menteri dalam negeri', 'menteri kesehatan', 'menteri pendidikan',
    'menteri perdagangan', 'menteri perhubungan', 'menteri agama',
    'menteri sosial', 'menteri tenaga kerja',
    'presiden', 'wakil presiden', 'perdana menteri',
]

def _ada_konteks_indonesia_di_sekitar(teks, posisi, lebar=100):
    """V6.17.93: cek apakah di sekitar posisi ada konteks Indonesia kuat."""
    awal = max(0, posisi - lebar)
    akhir = min(len(teks), posisi + lebar)
    sekitar = teks[awal:akhir].lower()
    for k in ['indonesia', 'jakarta', 'ri ', 'republik indonesia',
              'pemerintah ri', 'kemenkeu', 'kemenlu', 'bi ', 'ojk ',
              'prabowo', 'jokowi', 'gibran', 'sri mulyani']:
        if k in sekitar:
            return True
    return False

def cek_kategori_dari_isi(isi, judul, kategori_target):
    if not isi:
        return None
    if kategori_target not in ('internasional', 'internasional_asean', 'internasional_tt'):
        return None
    gab = (judul or '') + ' ' + (isi or '')
    t = gab.lower()
    for tokoh in NAMA_TOKOH_INDONESIA:
        # V6.17.93: skip jabatan ambigu tanpa konteks Indonesia
        if tokoh in JABATAN_AMBIGU_INDONESIA:
            for m in re.finditer(re.escape(tokoh), t):
                if not _ada_konteks_indonesia_di_sekitar(t, m.start()):
                    continue
                return ('isi AI memuat tokoh Indonesia "' + tokoh + '" tapi target kategori internasional')
            continue
        if re.search(r'\b' + re.escape(tokoh) + r'\b', t):
            return ('isi AI memuat tokoh Indonesia "' + tokoh + '" tapi target kategori internasional')
    for lem in LEMBAGA_INDONESIA:
        if lem == 'kpk':
            if _kpk_konteks_indonesia(t):
                return ('isi AI memuat lembaga Indonesia "kpk" dengan konteks Indonesia tapi target kategori internasional')
            continue
        if lem == 'tni':
            continue
        if re.search(r'\b' + re.escape(lem) + r'\b', t):
            return ('isi AI memuat lembaga Indonesia "' + lem + '" tapi target kategori internasional')
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+', isi or '')
    if m:
        dp = m.group(1).strip().lower()
        kota = dp.split(',')[0].strip()
        if kota in KOTA_INDONESIA_DATELINE:
            materi_low = (gab or '').lower()
            ada_kota_indo = any(re.search(r'\b' + re.escape(k) + r'\b', materi_low)
                                for k in KOTA_INDONESIA_DATELINE)
            if ada_kota_indo:
                return None
            return ('dateline "' + kota + '" kota Indonesia tapi target kategori internasional')
    return None

def tentukan_kategori_dari_isi(judul, isi):
    gab = (judul or '') + ' ' + (isi or '')
    t = gab.lower()
    hit_eko = sum(1 for k in KATA_EKONOMI_KUAT_TENTUKAN if k in t)
    if hit_eko >= 2:
        return None
    is_indo = False
    for tokoh in NAMA_TOKOH_INDONESIA:
        if tokoh in JABATAN_AMBIGU_INDONESIA:
            continue
        if re.search(r'\b' + re.escape(tokoh) + r'\b', t):
            is_indo = True
            break
    if not is_indo:
        for lem in LEMBAGA_INDONESIA:
            if re.search(r'\b' + re.escape(lem) + r'\b', t):
                is_indo = True
                break
    if not is_indo:
        return None
    is_lokal = any(re.search(r'\b' + re.escape(k) + r'\b', t)
                   for k in KATA_LOKAL_KALTARA)
    if is_lokal:
        return 'daerah'
    return 'nasional'

KATA_UMUM_EN = set([
    'the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'will', 'been',
    'are', 'was', 'were', 'their', 'they', 'about', 'after', 'into', 'over',
    'than', 'then', 'them', 'these', 'those', 'through', 'under', 'while',
    'where', 'when', 'what', 'which', 'who', 'whom', 'whose', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'only', 'own', 'same', 'too', 'very', 'can', 'just', 'should',
    'now', 'new', 'old', 'first', 'last', 'long', 'great', 'little', 'even',
    'much', 'many', 'said', 'says', 'say', 'told', 'tell', 'tells', 'get',
    'got', 'make', 'made', 'makes', 'take', 'took', 'taken', 'give', 'gave',
    'given', 'come', 'came', 'go', 'went', 'gone', 'see', 'saw', 'seen',
    'know', 'knew', 'known', 'think', 'thought', 'want', 'wanted', 'use',
    'used', 'find', 'found', 'work', 'worked', 'call', 'called', 'try',
    'tried', 'ask', 'asked', 'need', 'needed', 'feel', 'felt', 'become',
    'became', 'leave', 'left', 'put', 'mean', 'meant', 'keep', 'kept', 'let',
    'begin', 'began', 'begun', 'seem', 'seemed', 'help', 'helped', 'talk',
    'talked', 'turn', 'turned', 'start', 'started', 'show', 'showed', 'shown',
    'hear', 'heard', 'play', 'played', 'run', 'ran', 'move', 'moved', 'live',
    'lived', 'believe', 'believed', 'bring', 'brought', 'happen', 'happened',
    'write', 'wrote', 'written', 'provide', 'provided', 'sit', 'sat', 'stand',
    'stood', 'lose', 'lost', 'pay', 'paid', 'meet', 'met', 'include',
    'included', 'continue', 'continued', 'set', 'learn', 'learned', 'change',
    'changed', 'lead', 'led', 'understand', 'understood', 'watch', 'watched',
    'follow', 'followed', 'stop', 'stopped', 'create', 'created', 'speak',
    'spoke', 'spoken', 'read', 'spend', 'spent', 'grow', 'grew', 'grown',
    'open', 'opened', 'walk', 'walked', 'win', 'won', 'offer', 'offered',
    'remember', 'remembered', 'love', 'loved', 'consider', 'considered',
    'appear', 'appeared', 'buy', 'bought', 'wait', 'waited', 'serve', 'served',
    'die', 'died', 'send', 'sent', 'expect', 'expected', 'build', 'built',
    'stay', 'stayed', 'fall', 'fell', 'fallen', 'cut', 'reach', 'reached',
    'kill', 'killed', 'remain', 'remained', 'suggest', 'suggested', 'raise',
    'raised', 'pass', 'passed', 'sell', 'sold', 'require', 'required',
    'report', 'reported', 'decide', 'decided', 'pull', 'pulled', 'man', 'men',
    'woman', 'women', 'child', 'children', 'people', 'person', 'day', 'days',
    'year', 'years', 'time', 'times', 'week', 'weeks', 'month', 'months',
    'hour', 'hours', 'minute', 'minutes', 'morning', 'evening', 'night',
    'today', 'tomorrow', 'yesterday', 'world', 'country', 'countries', 'city',
    'cities', 'town', 'state', 'states', 'place', 'places', 'way', 'ways',
    'thing', 'things', 'part', 'parts', 'number', 'numbers', 'group', 'groups',
    'company', 'companies', 'government', 'governments', 'president',
    'minister', 'official', 'officials', 'police', 'army', 'military',
    'soldier', 'soldiers', 'leader', 'leaders', 'member', 'members', 'family',
    'families', 'friend', 'friends', 'home', 'house', 'school', 'hospital',
    'office', 'business', 'money', 'market', 'markets', 'price', 'prices',
    'cost', 'costs', 'tax', 'taxes', 'bank', 'banks', 'trade', 'war', 'peace',
    'attack', 'attacks', 'fire', 'flood', 'floods', 'storm', 'storms', 'quake',
    'quakes', 'earthquake', 'earthquakes', 'crash', 'crashes', 'accident',
    'accidents', 'death', 'deaths', 'dead', 'injured', 'missing', 'victim',
    'victims', 'suspect', 'suspects', 'crime', 'criminal', 'case', 'cases',
    'court', 'trial', 'judge', 'lawyer', 'officer', 'officers', 'spokesman',
    'spokeswoman', 'million', 'billion', 'thousand', 'hundred', 'percent',
    'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
    'ten', 'eleven', 'twelve', 'twenty', 'thirty', 'forty', 'fifty', 'sixty',
    'seventy', 'eighty', 'ninety', 'first', 'second', 'third', 'fourth',
    'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
    'reports', 'news', 'latest', 'update', 'updates', 'breaking', 'live',
    'video', 'photos', 'photo', 'image', 'images', 'north', 'south', 'east',
    'west', 'central', 'upper', 'lower', 'northern', 'southern', 'eastern',
    'western', 'middle', 'international', 'national', 'local', 'global',
    'regional', 'weekend', 'season', 'annual', 'monthly', 'daily', 'biggest',
    'largest', 'smallest', 'highest', 'lowest', 'best', 'worst', 'top',
    'major', 'minor', 'key', 'main', 'primary', 'secondary',
])

NAMA_DIRI_UMUM = set([
    'asean', 'pbb', 'nato', 'who', 'unicef', 'unesco', 'imf', 'g20', 'g7',
    'brics', 'apec', 'opec', 'wto', 'fao', 'ilo', 'wfp', 'unhcr', 'icrc',
    'amnesty', 'greenpeace', 'wwf', 'fifa', 'uefa', 'afc', 'bwf', 'fivb',
    'itf', 'atp', 'wta', 'nba', 'wnba', 'f1', 'motogp', 'ibl', 'world bank',
    'bank dunia', 'european union', 'uni eropa', 'african union',
    'arab league', 'liga arab', 'gcc', 'asean+3', 'apta', 'rcep', 'cptpp',
    'lockheed', 'lockheed martin', 'boeing', 'airbus', 'nasa', 'spacex',
    'tesla', 'apple', 'google', 'microsoft', 'meta', 'openai', 'anthropic',
    'nvidia', 'intel', 'samsung', 'huawei', 'xiaomi', 'tiktok', 'bytedance',
    'covid', 'covid-19',
    'xinhua', 'cgtn', 'scmp', 'global times', 'nhk', 'korea herald',
])

def _kata_inti_nama_diri(teks, bahasa='id'):
    kata = re.findall(r'[a-zA-Z]{4,}', (teks or '').lower())
    if bahasa == 'en':
        return set(k for k in kata if k not in KATA_UMUM_EN)
    return set(k for k in kata if k not in KATA_STOP_DOBEL)

def _cari_varian_id_en(teks):
    t = (teks or '').lower()
    hasil = set()
    for nama in NAMA_DIRI_UMUM:
        if nama in t:
            hasil.add(nama)
    for id_kata, en_list in VARIAN_KOTA_EN_ID.items():
        if id_kata in t:
            hasil.add(id_kata)
        for en_kata in en_list:
            if en_kata in t:
                hasil.add(id_kata)
                hasil.add(en_kata)
    return hasil

def cek_topik_ai_vs_materi(judul_ai, isi_ai, judul_materi, summary_materi, kategori=''):
    if not judul_ai or not judul_materi:
        return None
    if kategori == 'internasional_tt':
        return None
    teks_materi = (judul_materi or '') + ' ' + (summary_materi or '')[:500]
    teks_ai = (judul_ai or '') + ' ' + (isi_ai or '')
    if kategori and kategori != 'breaking':
        gab_ai = (judul_ai or '') + ' ' + (isi_ai or '')
        ok_kat, alasan_kat = _materi_cocok_kategori(kategori, judul_ai, gab_ai[:500])
        if not ok_kat:
            return 'judul/isi AI tidak cocok kategori ' + kategori + ': ' + alasan_kat
    varian_materi = _cari_varian_id_en(teks_materi)
    varian_ai = _cari_varian_id_en(teks_ai)
    if varian_materi & varian_ai:
        return None
    angka_materi = set(re.findall(r'\b\d{2,}\b', teks_materi))
    angka_ai = set(re.findall(r'\b\d{2,}\b', teks_ai))
    if angka_materi & angka_ai:
        return None
    kata_materi = _kata_inti_nama_diri(teks_materi, 'en')
    kata_ai = _kata_inti_nama_diri(teks_ai, 'id')
    irisan = kata_materi & kata_ai
    if len(irisan) >= 1:
        return None
    umum_materi = set(re.findall(r'[a-z]{5,}', teks_materi.lower()))
    umum_ai = set(re.findall(r'[a-z]{5,}', teks_ai.lower()))
    if len(umum_materi & umum_ai) >= 1:
        return None
    kata_materi_4 = set(re.findall(r'[a-z]{4,}', teks_materi.lower())) - KATA_UMUM_EN
    kata_ai_4 = set(re.findall(r'[a-z]{4,}', teks_ai.lower())) - KATA_STOP_DOBEL
    if len(kata_materi_4 & kata_ai_4) >= 2:
        return None
    return ('judul AI tidak nyambung materi: tidak ada irisan nama diri/angka/kata kunci')

# AKHIR PART 3A-2

# PART 3B - SUMBER DOMAIN, AI WRITE, ANTI-JIPLAK, INSERT, TEKNOLOGI

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
    sumber.append(GN('tips kesehatan dokter', 'id', 'GN Tips Kesehatan', when='30d'))
    sumber.append(GN('edukasi kesehatan masyarakat', 'id', 'GN Edukasi Kesehatan', when='30d'))
    sumber.append(RSSF('https://www.halodoc.com/artikel/feed', 'Halodoc'))
    sumber.append(RSSF('https://www.alodokter.com/feed', 'Alodokter'))
    sumber.append(RSSF('https://hellosehat.com/feed/', 'HelloSehat'))
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
    sumber.append(RSSF('https://www.autocar.co.uk/rss', 'Autocar'))
    sumber.append(RSSF('https://www.motor1.com/rss/news/all/', 'Motor1'))
    sumber.append(RSSF('https://www.carscoops.com/feed/', 'Carscoops'))
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
    'belum dikonfirmasi waktu', 'waktu kejadian belum', 'belum dikonfirmasi kapan',
    'menurut informasi yang diterima', 'diduga kuat', 'kabarnya',
    'identitas narasumber', 'tidak disebutkan dalam laporan',
    'tidak disebutkan secara eksplisit', 'tanpa menyebut nama',
    'tanpa menyebut nama pejabat', 'dalam laporan yang beredar',
    'dalam laporan yang dihimpun', 'tidak dapat dipastikan',
    'keterangan disampaikan tanpa', 'seorang pengusaha', 'seorang pengamat',
    'seorang pejabat tinggi', 'seorang tokoh', 'seorang bos', 'seorang pejabat',
]

KALIMAT_TEMPLATE_KOSONG = [
    'menurut informasi yang dihimpun',
    'kejadian itu berlangsung cepat',
    'kejadian berlangsung cepat',
    'menjadi pengingat bagi masyarakat',
    'menjadi pengingat',
    'peran aktif warga dinilai efektif',
    'warga diimbau tetap waspada',
    'koordinasi lintas instansi tetap berjalan',
    'situasi berjalan kondusif',
    'kegiatan berjalan lancar',
    'acara berlangsung meriah',
    'suasana begitu meriah',
    'para hadirin tampak antusias',
    'hal ini disampaikan',
    'demikian disampaikan',
    'diharapkan dapat bermanfaat',
    'sangat penting untuk',
    'perlu dicatat bahwa',
    'patut dicatat bahwa',
    'dalam konteks ini',
    'pada kenyataannya',
]

def _frasa_tertangkap(isi):
    isi_lower = (isi or '').lower()
    for p in POLA_LARANG:
        if p in isi_lower:
            return p
    return None

def _cek_kalimat_template(isi):
    if not isi:
        return None
    low = (isi or '').lower()
    hit = 0
    contoh = []
    for f in KALIMAT_TEMPLATE_KOSONG:
        if f in low:
            hit += 1
            if len(contoh) < 3:
                contoh.append(f)
    if hit >= 3:
        return ('kalimat template kosong berlebihan (' + str(hit) + '): '
                + '; '.join(contoh))
    return None

def _cek_kualitas_isi(isi, kategori):
    if not isi:
        return 'isi kosong'
    if kategori in ('internasional', 'internasional_asean', 'internasional_tt'):
        return None
    if kategori in ('teknologi', 'kesehatan', 'otomotif'):
        return None
    template = _cek_kalimat_template(isi)
    if template:
        return template
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

FRASA_UMUM_JIPLAK = [
    'kalau kita ingin', 'jika kita ingin', 'untuk menghasilkan',
    'generasi yang', 'masa depan', 'anak anak kita', 'pada dasarnya',
    'oleh karena itu', 'dengan demikian', 'sebagai kesimpulan',
    'pada akhirnya', 'tidak hanya', 'di sisi lain', 'di samping itu',
    'selain itu', 'yang bagus yang', 'yang cerdas yang', 'yang hebat yang',
    'yang unggul', 'yang berkualitas', 'yang sehat yang', 'perlu kita',
    'harus kita', 'mari kita',
    'presiden republik indonesia', 'kementerian koperasi dan ukm',
    'pemerintah provinsi', 'pemerintah kabupaten', 'pemerintah kota',
    'menjelang puncak ibadah haji di arafah muzdalifah',
    'puncak ibadah haji di arafah muzdalifah',
    'ibadah haji di arafah muzdalifah',
    'di arafah muzdalifah dan mina',
    'arafah muzdalifah dan mina',
    'puncak haji di arafah',
    'wukuf di arafah',
    'mabit di muzdalifah',
    'mabit di mina',
    'melontar jumrah',
    'thawaf ifadah',
    'tawaf ifadah',
    'sa i antara safa dan marwah',
    'antara safa dan marwah',
    'penguatan itu ditopang volume beli',
    'ditopang volume beli yang',
    'ihsg ditutup menguat',
    'ihsg ditutup melemah',
    'ihsg menguat ke level',
    'ihsg melemah ke level',
    'level support terdekat',
    'level resistance terdekat',
    'secara teknikal',
    'analis merekomendasikan',
    'rekomendasi beli',
    'rekomendasi jual',
    'rekomendasi hold',
    'dalam rangka kunjungan kerja ke wilayah perbatasan',
    'dalam rangka kunjungan kerja',
    'kunjungan kerja ke wilayah perbatasan',
    'kunjungan kerja ke daerah',
    'kunjungan kerja Presiden',
    'kunjungan kerja Menteri',
    'kunjungan kerja ke provinsi',
    'dalam rangka kunjungan',
    'melakukan kunjungan kerja',
    'melaksanakan kunjungan kerja',
    'bersama rombongan terbatas',
    'dan rombongan terbatas',
    'di dampingi oleh',
    'didampingi oleh',
    'turut mendampingi',
    'turut hadir dalam acara',
    'turut hadir dalam kegiatan',
    'hadir dalam kegiatan tersebut',
    'hadir dalam acara tersebut',
    'dalam sambutannya',
    'dalam arahannya',
    'dalam pidatonya',
    'dalam kesempatan itu',
    'pada kesempatan yang sama',
    'pada kesempatan itu',
    'dalam acara yang sama',
    'sebagai bentuk komitmen',
    'sebagai wujud komitmen',
    'sebagai wujud dukungan',
    'sebagai bentuk dukungan',
    'untuk mempercepat pembangunan',
    'untuk meningkatkan pelayanan',
    'untuk memperkuat sinergi',
    'untuk mempererat kerja sama',
    'untuk memperkuat kerja sama',
    'untuk mendukung pembangunan',
    'dalam upaya meningkatkan',
    'dalam upaya mempercepat',
    'dalam upaya memperkuat',
    'dalam upaya mendukung',
    'kami berharap',
    'saya berharap',
    'kita berharap',
    'saya mengajak',
    'kami mengajak',
    'mari kita bersama',
    'bersama-sama kita',
    'kepada seluruh masyarakat',
    'kepada seluruh warga',
    'kepada seluruh pihak',
    'kepada seluruh elemen',
    'seluruh jajaran',
    'seluruh pihak terkait',
    'semua pihak terkait',
    'jajaran pemerintah daerah',
    'jajaran pemerintah provinsi',
    'jajaran pemerintah kabupaten',
    'jajaran pemerintah kota',
    'pemerintah kabupaten dan kota',
    'pemerintah provinsi dan kabupaten',
    'pemerintah pusat dan daerah',
    'pusat dan daerah',
    'kabupaten dan kota',
    'provinsi dan kabupaten',
    'provinsi dan kota',
    'sinergi pusat dan daerah',
    'sinergi antar lembaga',
    'sinergi lintas sektor',
    'kolaborasi lintas sektor',
    'kolaborasi antar lembaga',
    'koordinasi lintas sektor',
    'koordinasi antar instansi',
    'koordinasi lintas instansi',
    'kerja sama lintas sektor',
    'kerja sama antar lembaga',
    'kerja sama semua pihak',
    'sinergi semua pihak',
    'pembangunan infrastruktur perbatasan',
    'pembangunan kawasan perbatasan',
    'pengembangan kawasan perbatasan',
    'wilayah perbatasan negara',
    'kawasan perbatasan negara',
    'daerah perbatasan negara',
    'wilayah terluar indonesia',
    'pulau terluar indonesia',
    'daerah tertinggal terdepan terluar',
    'wilayah 3t',
    'daerah 3t',
    'kawasan 3t',
    'kegiatan tersebut berlangsung',
    'acara tersebut berlangsung',
    'kegiatan ini berlangsung',
    'acara ini berlangsung',
    'kegiatan berlangsung dengan',
    'acara berlangsung dengan',
    'kegiatan tersebut dihadiri',
    'acara tersebut dihadiri',
    'kegiatan ini dihadiri',
    'acara ini dihadiri',
    'kegiatan dihadiri oleh',
    'acara dihadiri oleh',
    'kegiatan diikuti oleh',
    'acara diikuti oleh',
    'kegiatan tersebut diikuti',
    'acara tersebut diikuti',
    'dalam kegiatan tersebut',
    'dalam acara tersebut',
    'dalam kegiatan ini',
    'dalam acara ini',
    'kegiatan ini bertujuan',
    'acara ini bertujuan',
    'kegiatan tersebut bertujuan',
    'acara tersebut bertujuan',
    'tujuan dari kegiatan',
    'tujuan dari acara',
    'maksud dan tujuan',
    'dalam rangka memperingati',
    'dalam rangka menyambut',
    'dalam rangka merayakan',
    'untuk memperingati',
    'untuk menyambut',
    'untuk merayakan',
    'dalam memperingati',
    'sebagai bentuk apresiasi',
    'sebagai bentuk penghargaan',
    'sebagai wujud apresiasi',
    'sebagai wujud penghargaan',
    'memberikan apresiasi',
    'memberikan penghargaan',
    'menyampaikan apresiasi',
    'menyampaikan penghargaan',
    'menyampaikan terima kasih',
    'mengucapkan terima kasih',
    'terima kasih kepada',
    'ucapan terima kasih',
    'atas kerja sama',
    'atas kerja samanya',
    'atas dukungan',
    'atas dukungannya',
    'atas bantuan',
    'atas bantuannya',
    'atas perhatian',
    'atas perhatiannya',
    'atas kehadiran',
    'atas kehadirannya',
]

FRASA_JANGGAL_TERJEMAHAN = [
    'dalam hal ini', 'pada akhirnya', 'tidak hanya tetapi juga',
    'yang tersebut di atas', 'seperti yang telah disebutkan',
    'pada saat yang sama', 'sebagai hasil dari', 'oleh karena itu',
    'dalam rangka untuk', 'sebagai tambahan', 'di sisi lain',
    'dengan kata lain', 'pada kenyataannya', 'dalam kasus ini',
    'untuk alasan ini', 'sebagai konsekuensi', 'hal ini menunjukkan',
    'perlu dicatat bahwa', 'patut dicatat bahwa', 'adalah penting untuk',
    'sangat penting untuk', 'hal ini penting', 'dalam konteks ini',
    'dari perspektif ini', 'dalam beberapa kasus', 'pada umumnya',
    'secara umum', 'pada dasarnya', 'sebagaimana disebutkan',
]

def _frasa_umum(gram_tuple):
    teks = ' '.join(gram_tuple)
    for f in FRASA_UMUM_JIPLAK:
        if f in teks:
            return True
    return False

def _frasa_janggal_terjemahan(teks):
    t = (teks or '').lower()
    hit = 0
    for f in FRASA_JANGGAL_TERJEMAHAN:
        if f in t:
            hit += 1
    if hit >= 3:
        return 'terlalu banyak frasa janggal terjemahan mesin: ' + str(hit)
    return None

KATA_TOPIK_SEJARAH = [
    'sejarah', 'sejarah tni', 'sejarah organisasi', 'sejarah indonesia',
    'sejarah kemerdekaan', 'sejarah nasional', 'sejarah perjuangan',
    'proklamasi', 'kemerdekaan', 'perjuangan', 'pahlawan', 'pahlawan nasional',
    'pahlawan revolusi', 'hari pahlawan', 'hari kemerdekaan', 'hut ri',
    'sumpah pemuda', 'kebangkitan nasional', 'bud 1945', 'bpupki', 'ppki',
    'masa penjajahan', 'penjajahan', 'kolonial', 'kolonialisme',
    'zaman jepang', 'zaman belanda', 'zaman portugis', 'zaman voc',
    'histori', 'historis', 'kronik', 'kronologi sejarah',
    'peringatan hari', 'peringatan hut', 'milad', 'dies natalis',
]

def _topik_sejarah(judul_materi, materi_sumber):
    gab = ((judul_materi or '') + ' ' + (materi_sumber or '')[:500]).lower()
    hit = 0
    for k in KATA_TOPIK_SEJARAH:
        if len(k) <= 4:
            if re.search(r'\b' + re.escape(k) + r'\b', gab):
                hit += 1
        else:
            if k in gab:
                hit += 1
        if hit >= 2:
            return True
    return False

FRASA_OPERASI_BUANG = [
    'tim sar', 'tim gabungan', 'tim pencarian', 'tim evakuasi',
    'tim penanganan', 'tim penanggulangan', 'tim kemanusiaan',
    'operasi sar', 'operasi pencarian', 'operasi evakuasi',
    'pencarian', 'evakuasi', 'penanganan', 'penanggulangan',
    'penyelamatan', 'pertolongan', 'pemberian bantuan',
    'basarnas', 'bnpb', 'bpbd', 'tagana', 'sar gabungan',
]

def _buang_frasa_operasi(teks):
    if not teks:
        return ''
    t = teks
    for f in FRASA_OPERASI_BUANG:
        t = re.sub(r'\b' + re.escape(f) + r'\b', ' ', t, flags=re.IGNORECASE)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def _buang_kutipan_langsung(teks):
    if not teks:
        return ''
    t = teks
    t = re.sub(r'"[^"]{5,500}"', ' ', t)
    t = re.sub(r"'[^']{5,500}'", ' ', t)
    t = re.sub(r'\u201c[^\u201d]{5,500}\u201d', ' ', t)
    t = re.sub(r'\u2018[^\u2019]{5,500}\u2019', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

BLACKLIST_NAMA_ACARA = [
    'cfd', 'car free day', 'semarak', 'genbi',
    'festival', 'karnaval', 'pesta rakyat', 'pawai',
    'hut', 'dirgahayu', 'open house', 'halal bihalal',
    'syukuran', 'tasyakuran',
    'workshop', 'seminar', 'lokakarya', 'webinar', 'talkshow',
]

WHITELIST_SINGKATAN = set([
    'ri', 'dpr', 'mpr', 'dpd', 'dprd', 'kpk', 'ky', 'ma', 'mk',
    'tni', 'polri', 'polda', 'polres', 'polsek', 'kodam', 'korem',
    'kodim', 'koramil', 'kejagung', 'kejari', 'kejati',
    'kemenkeu', 'kemendag', 'kemenkes', 'kemendikbud', 'kemnaker',
    'kemenkumham', 'kemensos', 'kemenag', 'kemenparekraf', 'kemenlu',
    'kemenhan', 'kemendagri', 'kemenko', 'kemenpppa', 'kemenpora',
    'kpu', 'bawaslu', 'bin', 'wantannas', 'setkab', 'setneg',
    'bgn', 'bmkg', 'bnpb', 'basarnas', 'bpbd', 'bps', 'bi', 'ojk',
    'bpom', 'bpjs', 'kai', 'pln', 'pdam',
    'mbg', 'kdmp', 'sppg', 'blt', 'pkh', 'umkm', 'apbn', 'apbd',
    'pssi', 'fifa', 'uefa', 'afc', 'bwf', 'fivb', 'nba', 'ibl', 'f1',
    'asean', 'pbb', 'nato', 'who', 'imf', 'wto', 'fao', 'unicef',
    'gdpr', 'apec', 'g20', 'g7', 'brics', 'opec', 'wto', 'ilo',
    'ai', 'it', 'cv', 'pt', 'tbk',
    'hkbp', 'gkii', 'gki', 'gpdi',
])

def _buang_nama_acara_dan_singkatan(teks):
    if not teks:
        return ''
    t = teks
    for f in BLACKLIST_NAMA_ACARA:
        if len(f) <= 4:
            t = re.sub(r'\b' + re.escape(f) + r'\b', ' ', t, flags=re.IGNORECASE)
        else:
            t = re.sub(re.escape(f), ' ', t, flags=re.IGNORECASE)
    def _ganti_singkatan(m):
        s = m.group(0)
        if s.lower() in WHITELIST_SINGKATAN:
            return s
        return ' '
    t = re.sub(r'\b[A-Z]{2,6}\b', _ganti_singkatan, t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def _buang_fakta_wajib(teks):
    if not teks:
        return ''
    t = teks
    t = _buang_kutipan_langsung(t)
    pola_jabatan = re.compile(
        r'\b(?:'
        r'wali\s+kota|wakil\s+wali\s+kota|bupati|wakil\s+bupati|gubernur|wakil\s+gubernur|'
        r'presiden|wakil\s+presiden|menteri|wakil\s+menteri|'
        r'kepala\s+lapas|kepala\s+dinas|kepala\s+badan|kepala\s+kantor|'
        r'kepala\s+uptd|kepala\s+upt|kepala\s+bagian|kepala\s+bidang|'
        r'kapolres|kapolsek|kapolda|kadiv|kabid|kasat|kanit|kasubbag|'
        r'danrem|dandim|danramil|danyon|danki|'
        r'kajari|kajati|ketua\s+pengadilan|hakim|jaksa|'
        r'direktur|direktur\s+utama|komisaris|manajer|'
        r'ketua|sekretaris|bendahara|anggota|staf|'
        r'kades|kepala\s+desa|lurah|camat|rt|rw|'
        r'profesor|dokter'
        r')\s+'
        r'(?:[A-Z][a-zA-Z\.\'\-\s]{2,120})',
        re.IGNORECASE
    )
    t = pola_jabatan.sub(' ', t)
    pola_gelar = re.compile(
        r'\b(?:drs|dra|dr|ir|prof|h|hj|r\.?a|r\.?i|s\.?t|s\.?h|s\.?e|s\.?si|s\.?sos|'
        r's\.?pd|s\.?ag|s\.?psi|s\.?ked|s\.?kom|m\.?si|m\.?m|m\.?pd|m\.?t|m\.?h|'
        r'm\.?kes|m\.?sc|m\.?a|m\.?ag|m\.?psi|ph\.?d|m\.?pd\.?i|m\.?pdi|a\.?md)\.?\s+'
        r'(?:[A-Z][a-zA-Z\.\'\-\s]{2,120})',
        re.IGNORECASE
    )
    t = pola_gelar.sub(' ', t)
    pola_pangkat = re.compile(
        r'\b(?:jenderal|letnan\s+jenderal|letjen|mayor\s+jenderal|mayjen|'
        r'brigadir\s+jenderal|brigjen|kolonel|letnan\s+kolonel|letkol|'
        r'mayor|kapten|lettu|letda|letnan|akbp|akp|iptu|ipda|bripka|bripda|'
        r'kombes|kompol|inspektur|bharada|bharatu|bharaka)'
        r'\s+[A-Z][a-zA-Z\.\'\-\s]{2,80}',
        re.IGNORECASE
    )
    t = pola_pangkat.sub(' ', t)
    protected = []
    for kota in KOTA_INDONESIA_DATELINE:
        protected.append(kota)
    for prov in KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN:
        protected.append(prov)
    for neg in KATA_LUAR_NEGERI_WAJIB:
        protected.append(neg)
    protected_set = set(p.lower() for p in protected)
    def _buang_nama_orang(m):
        kandidat = m.group(0)
        kandidat_low = kandidat.lower()
        for p in protected_set:
            if p in kandidat_low:
                return kandidat
        return ' '
    pola_nama_orang = re.compile(
        r'\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-zA-Z\.\']{2,}){1,4}',
        re.UNICODE
    )
    t = pola_nama_orang.sub(_buang_nama_orang, t)
    pola_lokasi = re.compile(
        r'\b(?:kecamatan|kelurahan|desa|kampung|jalan|jl\.|gang|rt|rw|dusun)'
        r'\s+[A-Z][a-zA-Z\.\'\-\s]{2,60}',
        re.IGNORECASE
    )
    t = pola_lokasi.sub(' ', t)
    t = _buang_frasa_operasi(t)
    t = _buang_nama_acara_dan_singkatan(t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# V6.17.92: N-gram 22 → 25 (anti-jiplak terlalu ketat)
def _n_gram_untuk(kategori, panjang_materi):
    return 25

def cek_jiplak(materi_sumber, isi_ai, judul_materi='', kategori=''):
    if not materi_sumber or not isi_ai:
        return None
    frasa_mesin = _frasa_janggal_terjemahan(isi_ai)
    if frasa_mesin:
        return frasa_mesin
    materi_bersih = _buang_fakta_wajib(materi_sumber)
    isi_bersih = _buang_fakta_wajib(isi_ai)
    n_kata = _n_gram_untuk(kategori, len(materi_bersih))
    sumber_grams = _gram_set(materi_bersih, n_kata)
    if sumber_grams:
        for gram in _gram_list(isi_bersih, n_kata):
            if gram in sumber_grams:
                if _frasa_umum(gram):
                    continue
                return 'N-gram tersalin: ' + ' '.join(gram)
    return None

def _paksa_dateline_indonesia(isi):
    m = re.match(r'^([^\n]{1,80}?)\s+[-–—]\s+', isi or '')
    if m:
        return 'INDONESIA - ' + isi[m.end():]
    return 'INDONESIA - ' + (isi or '')

KATA_HEWAN_FILE = ['wolf', 'serigala', 'dog', 'anjing', 'cat_', '-cat-', 'kucing',
                   'bird', 'burung', 'egret', 'heron', 'eagle', 'hawk', 'owl',
                   'monkey', 'monyet', 'orangutan', 'komodo', 'tiger', 'harimau',
                   'lion', 'singa', 'elephant', 'gajah', 'bear', 'beruang',
                   'deer', 'rusa', 'fox', 'rubah', 'snake', 'ular', 'crocodile',
                   'buaya', 'lizard', 'kadal', 'frog', 'katak', 'fish', 'ikan',
                   'shark', 'hiu', 'whale', 'paus', 'dolphin', 'lumba', 'insect',
                   'serangga', 'butterfly', 'kupu', 'spider', 'labah', 'rat',
                   'tikus', 'mouse-', 'horse', 'kuda', 'cow', 'sapi', 'goat',
                   'kambing', 'sheep', 'chicken', 'ayam', 'duck', 'bebek',
                   'goose', 'rabbit', 'kelinci', 'zoo', 'safari', 'wildlife', 'fauna']

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
               and not _url_berbau_hewan(u) \
               and not cek_url_gambar_hewan(u):
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
            params={'query': deskripsi, 'per_page': 5, 'orientation': 'landscape'},
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
            if gambar_sampah(u) or gambar_sudah_dipakai(u):
                continue
            masalah_hewan = cek_url_gambar_hewan(u)
            if masalah_hewan:
                print('       Pexels URL hewan ditolak: ' + masalah_hewan[:60])
                continue
            return u
        if kandidat:
            print('       Semua kandidat Pexels terpakai/sampah/hewan - fallback Wikimedia.')
    except Exception as e:
        print('       Pexels gagal: ' + str(e)[:60])
    return ''

WORKER_GAMBAR_URL = 'https://kramanews-generate-image.denytriono-btm.workers.dev'
GAMBAR_AI_AKTIF = False

def generate_gambar_ai(deskripsi):
    if not GAMBAR_AI_AKTIF:
        return ''
    return ''

def cari_gambar_otomatis(deskripsi, judul_berita):
    img = cari_gambar_pexels(deskripsi)
    if img:
        return img, 'pexels'
    print('       Pexels kosong - fallback Wikimedia...')
    img = cari_gambar_wikimedia(deskripsi)
    if img:
        return img, 'wikimedia'
    print('       Wikimedia kosong - fallback Picsum (AI dinonaktifkan).')
    return '', 'picsum'

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

KATA_SINYAL_EKONOMI = [
    'ekspor', 'impor', 'trade', 'exports', 'imports', 'perdagangan',
    'neraca dagang', 'gdp', 'pdb', 'pertumbuhan ekonomi', 'produksi',
    'manufaktur', 'factory', 'manufacturing', 'supply chain',
    'penjualan ritel', 'retail sales', 'indeks pmi', 'pmi index',
    'properti', 'property', 'real estate', 'housing', 'perumahan',
    'kunjungan dagang', 'kunjungan ekonomi', 'delegasi dagang',
    'merger', 'akuisisi', 'ipo', 'valuasi', 'investasi',
]

def _catatan_ekonomi_khusus(kategori_target, judul, materi):
    if kategori_target != 'ekonomi':
        return ''
    gab_low = ((judul or '') + ' ' + (materi or '')).lower()
    ada_sinyal = any(k in gab_low for k in KATA_SINYAL_EKONOMI)
    ada_kata_ekonomi = ('ekonomi' in gab_low or 'economy' in gab_low
                        or 'economic' in gab_low or 'economist' in gab_low)
    if ada_sinyal and not ada_kata_ekonomi:
        return ('\n\nCATATAN PENTING — MATERI INI ADALAH BERITA EKONOMI:\n'
                '- Materi memuat kata perdagangan/ekspor/impor/produksi/manufaktur\n'
                '  ATAU properti/perumahan/housing/real estate/IPO/merger/\n'
                '  kunjungan dagang.\n'
                '- WAJIB tulis sebagai berita EKONOMI, BUKAN politik luar negeri.\n'
                '- JANGAN tolak dengan alasan "politik luar negeri", "materi politik",\n'
                '  "kunjungan diplomatik", atau "materi properti".\n'
                '- Properti, perumahan, kunjungan dagang, IPO, merger TETAP EKONOMI.\n'
                '- Fokus: angka, data perdagangan, pertumbuhan, dampak ekonomi.\n')
    return ''

DOMAIN_PORTAL_DAERAH = [
    'radartarakan', 'benuanta', 'kaltara.tribunnews', 'tarakankota',
    'jawapos.com', 'tribunnews.com', 'antaradaerah', 'metrokaltara',
    'diskominfo.kaltaraprov',
]

def _catatan_portal_daerah(link, kategori_target):
    if kategori_target != 'daerah':
        return ''
    low = (link or '').lower()
    if not any(d in low for d in DOMAIN_PORTAL_DAERAH):
        return ''
    return ('\n\nCATATAN PENTING — SUMBER PORTAL DAERAH:\n'
            '- Materi ini dari portal berita DAERAH (Radar Tarakan/Benuanta/Tribun Daerah).\n'
            '- WAJIB tulis sebagai berita DAERAH, BUKAN nasional/ekonomi/teknologi.\n'
            '- JANGAN tolak dengan alasan "tidak cocok kategori: materi jargas/infrastruktur/proyek".\n'
            '- Walaupun isi materi tentang proyek/infrastruktur/energi nasional,\n'
            '  karena sumber portal daerah → TETAP kategori DAERAH.\n'
            '- Fokus: dampak lokal, lokasi daerah, tokoh daerah.\n')

def _cek_kategori_isi_penuh(judul_ai, isi_ai, kategori_target):
    if not kategori_target or kategori_target == 'breaking':
        return True, ''
    kata_kunci = KATA_KUNCI_KATEGORI.get(kategori_target, [])
    if not kata_kunci:
        return True, ''
    judul_low = (judul_ai or '').lower()
    for kk in kata_kunci:
        if len(kk) <= 4:
            if re.search(r'\b' + re.escape(kk) + r'\b', judul_low):
                return True, ''
        else:
            if kk in judul_low:
                return True, ''
    isi_low = (isi_ai or '').lower()
    hit = 0
    for kk in kata_kunci:
        if len(kk) <= 4:
            if re.search(r'\b' + re.escape(kk) + r'\b', isi_low):
                hit += 1
        else:
            if kk in isi_low:
                hit += 1
        if hit >= 2:
            return True, ''
    if hit >= 1:
        return True, ''
    return False, 'judul & isi AI tidak ada kata kunci kategori ' + kategori_target

# V6.17.87: blacklist kata kerja/frasa judul agregator (biar tidak salah tangkap "Bawa Aspirasi DOB")
# V6.17.89: tambah kata kerja/frasa judul yang masih lolos
# V6.17.91: tambah singkatan kementerian/sapaan
# V6.17.97: tambah 'perhatikan', 'pelayaran' (false positive nama pejabat)
KATA_BUKAN_NAMA_PEJABAT = [
    'tekankan', 'pentingnya', 'menanamkan', 'persatuan', 'kesatuan',
    'himbau', 'imbau', 'ajak', 'dorong', 'ingatkan', 'minta', 'serukan',
    'soroti', 'apresiasi', 'dukung', 'perkuat', 'tingkatkan', 'gelar',
    'resmikan', 'tinjau', 'hadiri', 'hadir', 'buka', 'tutup', 'luncurkan',
    'canangkan', 'kunjungi', 'serahkan', 'beri', 'sambut', 'terima',
    'pimpin', 'bahas', 'tegaskan', 'nyatakan',
    'harapkan', 'harap', 'berharap', 'ingin', 'akan', 'telah', 'sudah',
    'belum', 'bisa', 'dapat', 'harus', 'wajib', 'perlu', 'mesti',
    'dan', 'atau', 'yang', 'di', 'ke', 'dari', 'untuk', 'pada', 'dalam',
    'dengan', 'oleh', 'sebagai', 'adalah', 'itu', 'ini', 'juga', 'saja',
    'pembahasan', 'rampung', 'disahkan', 'disetujui', 'disepakati',
    'dibahas', 'diparipurnakan', 'ditetapkan', 'dilantik', 'diresmikan',
    'peresmian', 'pelantikan', 'penetapan', 'persetujuan', 'kesepakatan',
    'keputusan', 'rapat', 'sidang', 'forum', 'agenda',
    'rangka', 'upaya', 'usaha', 'proses', 'tahap', 'target', 'capaian',
    'laporan', 'keterangan', 'informasi', 'pernyataan', 'pidato', 'sambutan',
    'masalah', 'persoalan', 'isu', 'topik', 'tema', 'pokok',
    'penanganan', 'penanggulangan', 'pencegahan', 'penindakan',
    'pengawasan', 'pembinaan', 'pemberdayaan', 'pengembangan',
    'peningkatan', 'perbaikan', 'pembangunan', 'pemeliharaan',
    'belanja', 'anggaran', 'realisasi', 'serapan', 'target',
    'hasil', 'capaian', 'prestasi', 'kinerja', 'evaluasi', 'monitoring',
    'masa', 'zaman', 'era', 'periode',
    'lebih', 'kurang', 'baik', 'buruk', 'bagus', 'jelek',
    'lintas', 'antar', 'antarwilayah', 'nasional', 'regional', 'lokal',
    'kalteng', 'kaltim', 'kalsel', 'kalbar', 'kaltara', 'kalimantan',
    'jabar', 'jateng', 'jatim', 'jakarta', 'banten', 'bali',
    'sumut', 'sumbar', 'sumsel', 'riau', 'jambi', 'lampung', 'bengkulu',
    'aceh', 'sulut', 'sulteng', 'sulsel', 'sultra', 'gorontalo',
    'maluku', 'malut', 'papua', 'ntb', 'ntt',
    'indonesia', 'negara',
    'kecamatan', 'kelurahan', 'desa',
    'karhutla', 'kebakaran', 'banjir', 'gempa', 'tsunami', 'longsor',
    'gotong', 'royong', 'gotong royong', 'kerja', 'bakti',
    # V6.17.87: tambah blacklist frasa judul agregator
    'bawa', 'bawaan', 'aspirasi', 'rakor', 'flash', 'kunker', 'kunjungan',
    'imbauan', 'ajakan', 'dorongan', 'pernyataan', 'sorotan',
    'fokus', 'ubah', 'ganti', 'kembali', 'lanjut', 'mulai', 'tutup',
    # V6.17.89: tambah kata kerja/frasa judul yang masih lolos
    'pastikan', 'pastinya', 'kebutuhan', 'butuh', 'perlu',
    'jalan', 'perbatasan', 'masuk', 'rencana', 'induk', 'master',
    'provinsi', 'kabupaten', 'kota', 'pemprov', 'pemkab', 'pemkot',
    'gubernur', 'wagub', 'wakil gubernur', 'bupati', 'wakil bupati',
    'walikota', 'wakil walikota', 'menteri', 'wakil menteri',
    'direktur', 'utama', 'direktur utama', 'dirut', 'komisaris',
    'kepala', 'wakil', 'sekretaris', 'jenderal', 'sekjen',
    'bersama', 'juga', 'serta', 'maupun', 'hingga', 'sampai',
    'buka', 'tutup', 'buka suara', 'buka-bukaan',
    'tangani', 'atasi', 'selesai', 'selesaikan', 'tuntaskan',
    'kawal', 'awal', 'akhir', 'baru', 'lama',
    # V6.17.91: singkatan kementerian/sapaan (bukan nama orang)
    'pmk', 'pmm', 'menko', 'menkopolhukam', 'menkomarves',
    'mendikdasmen', 'mendikbud', 'mendikbudristek', 'menkes',
    'menkeu', 'menlu', 'menhan', 'mendag', 'menhub', 'menaker',
    'mensos', 'menag', 'menparekraf', 'menkop', 'menkum',
    'menkumham', 'menppa', 'menpora', 'menperin', 'mentan',
    'mentrans', 'menkominfo', 'menkominfo', 'menpupr',
    'menko pmk', 'koordinator', 'bidang',
    'kunker', 'kunjungan kerja', 'kunjungan',
    # V6.17.97: tambah 'perhatikan', 'pelayaran' (false positive nama pejabat)
    'perhatikan', 'pelayaran',
]

# V6.17.89: kata sambung yang menandakan akhir nama (biar tidak nangkap 2 jabatan)
KATA_SAMBUNG_NAMA = {'dan', 'atau', 'serta', 'maupun', 'hingga', 'sampai',
                     'dengan', 'untuk', 'pada', 'di', 'ke', 'dari', 'oleh'}

def _cek_nama_pejabat_dari_materi(materi, isi_ai, kategori):
    if not materi or not isi_ai:
        return None
    if kategori in ('internasional', 'internasional_asean', 'internasional_tt'):
        return None
    if kategori in ('teknologi', 'kesehatan', 'otomotif'):
        return None
    # V6.17.87: skip kalau materi dari agregator/flash news (banyak judul)
    materi_low_check = materi.lower()
    if any(k in materi_low_check for k in ('86 flash', '86flash', 'flash !',
                                             'berita terkini', 'update terkini',
                                             'headline', 'top news')):
        return None
    pola_nama_pejabat = re.compile(
        r'\b(?:'
        r'wali\s+kota|wakil\s+wali\s+kota|bupati|wakil\s+bupati|gubernur|wakil\s+gubernur|'
        r'presiden|menteri|kepala\s+lapas|kepala\s+dinas|kepala\s+badan|kepala\s+uptd|'
        r'kepala\s+bidang|kapolres|kapolsek|kajari|direktur|ketua|kades|lurah|camat'
        r')\s+([A-Z][a-zA-Z\.\'\-\s]{3,80})',
        re.IGNORECASE
    )
    nama_materi = []
    for m in pola_nama_pejabat.finditer(materi):
        nama_full = m.group(0).strip()
        after_jabatan = m.group(1) if m.group(1) else ''
        # V6.17.89: pecah di koma dulu (biar "Direktur Utama PT X, Budi" tidak campur)
        after_jabatan = re.split(r'[,;]', after_jabatan)[0]
        bagian = re.findall(r'\b[A-Z][a-z]+\b', after_jabatan)
        nama_bersih = []
        for k in bagian:
            k_low = k.lower()
            if k_low in KATA_BUKAN_NAMA_PEJABAT:
                break
            # V6.17.89: stop di kata sambung (biar tidak nangkap 2 jabatan)
            if k_low in KATA_SAMBUNG_NAMA:
                break
            nama_bersih.append(k)
            if len(nama_bersih) >= 2:
                break
        if len(nama_bersih) < 1:
            continue
        if len(nama_bersih) < 2:
            continue
        nama_kunci = nama_bersih[-1]
        if len(nama_kunci) < 3:
            continue
        # V6.17.87 + V6.17.89 + V6.17.91 + V6.17.97: nama kunci wajib bukan kata kerja/singkatan blacklist
        if nama_kunci.lower() in KATA_BUKAN_NAMA_PEJABAT:
            continue
        if nama_kunci.lower() in KATA_SAMBUNG_NAMA:
            continue
        # V6.17.91: cek juga apakah nama_kunci uppercase singkatan (bukan nama orang)
        if nama_kunci.isupper() and len(nama_kunci) <= 6:
            continue
        nama_materi.append((nama_full, nama_kunci))
    if not nama_materi:
        return None
    kata_ai = set(re.findall(r'\b[A-Z][a-zA-Z]{2,}\b', isi_ai))
    materi_low = materi.lower()
    for nama_full, nama_kunci in nama_materi[:3]:
        if nama_kunci.lower() in KATA_BUKAN_NAMA_PEJABAT:
            continue
        if nama_kunci.lower() not in materi_low:
            continue
        if nama_kunci not in kata_ai:
            return ('nama pejabat "' + nama_full[:60] + '" ada di materi tapi tidak '
                    'ditulis AI — wajib tulis lengkap dengan jabatan')
    return None

AMBANG_JUDUL_MIRIP = 0.75

# ══════════════════════════════════════════════════════
# V6.17.84: ai_write diperbaiki — retry ganti judul PAKAI WHILE
# V6.17.93: pakai _topik_dobel6jam_nyata (dobel-6jam longgar)
# V6.17.94: retry judul HANYA 75-90%, ≥90% langsung tolak (hemat token)
# V6.17.95: cek_deskripsi_gambar pakai konteks materi (ikan diizinkan kalau perikanan)
# V6.17.96: tambah retry judul kalau hasil AI dobel (sebelum insert_news tolak)
# ══════════════════════════════════════════════════════

# V6.17.96: jumlah maksimal retry judul saat AI hasil dobel
MAX_RETRY_JUDUL_DOBEL = 1

def ai_write(user_content, timeout=150, materi_sumber='', kategori='',
             judul_materi='', summary_materi='', wajib_topik=True,
             source_url=''):
    obj = None
    materi_asli = user_content
    koneksi_retry = 0
    MAX_KONEKSI_RETRY = 0
    MAX_LOOP = 2
    FRASA_TOLAK_AI = ['materi tidak tersedia', 'materi sumber tidak tersedia',
                      'materi tidak relevan', 'tidak dapat menulis', 'tidak ada materi']
    percobaan = 0
    judul_retry_dilakukan = False
    retry_dobel_dilakukan = 0  # V6.17.96: hitung retry karena dobel

    while percobaan < MAX_LOOP:
        percobaan += 1
        temp = 0.5
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

        tolak_raw = obj.get('tolak', '')
        if isinstance(tolak_raw, bool):
            tolak_msg = ''
        else:
            tolak_msg = str(tolak_raw).strip()
        if tolak_msg:
            tl = tolak_msg.lower()
            if source_url:
                catat_tolak_ai_token(source_url, tolak_msg)
            if any(f in tl for f in FRASA_TOLAK_AI) and percobaan < MAX_LOOP:
                print('       AI tolak bingung ("' + tolak_msg[:50] + '") - minta tulis ulang')
                user_content = (
                    'CATATAN: MATERI SUMBER TERSEDIA di atas. '
                    'TULIS ULANG berita sesuai SEMUA aturan. Jangan tolak. '
                    'Materi sumber ada di pesan sebelumnya.\n\n'
                    'MATERI SUMBER:\n' + materi_sumber[:1500] + '\n\n'
                    'Tulis berita JSON valid.')
                continue
            raise BeritaLama(tolak_msg[:100])

        judul = perbaiki_persen((obj.get('judul') or '').strip())

        # V6.17.94: retry judul HANYA kalau mirip 75-90%. ≥90% langsung tolak (hemat token)
        if judul_materi and judul and not judul_retry_dilakukan:
            rasio_judul = SequenceMatcher(None, judul.lower(), judul_materi.lower()).ratio()
            if AMBANG_JUDUL_MIRIP <= rasio_judul < 0.90:
                print('       Judul AI mirip materi (' + str(int(rasio_judul * 100))
                      + '%) — minta AI ganti judul (retry 1x)...')
                judul_retry_dilakukan = True
                user_content = (
                    'CATATAN PENTING — JUDUL HARUS BEDA TOTAL:\n'
                    '- Judul materi asli: "' + judul_materi + '"\n'
                    '- Judul kamu sebelumnya: "' + judul + '"\n'
                    '- KEMIRIPAN: ' + str(int(rasio_judul * 100)) + '% (terlalu mirip!)\n'
                    '- WAJIB ganti judul dengan kata-kata BERBEDA TOTAL.\n'
                    '- DILARANG menyalin kata kunci judul materi.\n'
                    '- Contoh: judul materi "Wali Kota Resmikan 3 Dapur MBG" → '
                    'judul baru "Tiga Fasilitas MBG Baru Diresmikan di Cilegon".\n'
                    '- Semua aturan lain tetap berlaku.\n\n'
                    'MATERI SUMBER:\n' + materi_sumber[:800] + '\n\n'
                    'Tulis berita JSON valid dengan JUDUL BERBEDA.')
                continue
            elif rasio_judul >= 0.90:
                # V6.17.94: judul jiplak parah — retry percuma, langsung tolak
                msg_tolak = ('judul AI jiplak parah (' + str(int(rasio_judul * 100))
                             + '%) — retry tidak akan menolong')
                print('       ' + msg_tolak)
                if source_url:
                    catat_tolak_ai_token(source_url, msg_tolak)
                raise BeritaLama(msg_tolak)

        # V6.17.96: cek kalau judul dobel dengan yang sudah terbit — retry ganti judul
        if judul and retry_dobel_dilakukan < MAX_RETRY_JUDUL_DOBEL:
            if sudah_serupa(judul):
                retry_dobel_dilakukan += 1
                print('       Judul AI dobel dengan yang sudah ada — minta AI ganti judul (retry '
                      + str(retry_dobel_dilakukan) + '/' + str(MAX_RETRY_JUDUL_DOBEL) + ')...')
                user_content = (
                    'CATATAN PENTING — JUDUL SUDAH PERNAH TERBIT:\n'
                    '- Judul kamu: "' + judul + '"\n'
                    '- Judul ini MIRIP dengan berita yang sudah tayang di KramaNews.\n'
                    '- WAJIB tulis JUDUL LAIN yang BERBEDA TOTAL.\n'
                    '- Fokus ke SUDUT PANDANG BERBEDA dari berita yang sama.\n'
                    '- Contoh: kalau berita lama "Gubernur Resmikan Jalan Perbatasan",\n'
                    '  judul baru bisa "Jalan Perbatasan Kaltara Masuk Rencana Induk 2027-2029".\n'
                    '- Semua aturan lain tetap berlaku.\n\n'
                    'MATERI SUMBER:\n' + materi_sumber[:800] + '\n\n'
                    'Tulis berita JSON valid dengan JUDUL BERBEDA.')
                continue
        break

    if obj is None:
        raise Exception('AI tidak menghasilkan output valid')

    judul = perbaiki_persen((obj.get('judul') or '').strip())
    isi = perbaiki_persen((obj.get('isi') or '').strip())
    ringkasan = perbaiki_persen((obj.get('ringkasan') or '').strip())
    if ada_persen_kata(judul + ' ' + isi + ' ' + ringkasan):
        print('       Persen auto-fix diterapkan.')

    # Cek final: judul masih mirip → tolak
    if judul_materi and judul:
        rasio_judul = SequenceMatcher(None, judul.lower(), judul_materi.lower()).ratio()
        if rasio_judul >= AMBANG_JUDUL_MIRIP:
            msg_tolak = ('judul AI mirip judul materi (' + str(int(rasio_judul * 100))
                         + '%) — jiplak, wajib judul beda')
            if source_url:
                catat_tolak_ai_token(source_url, msg_tolak)
            raise Exception('DITOLAK - ' + msg_tolak)

    judul_l = judul.lower()
    if any(x in judul_l for x in ('materi tidak dapat diolah', 'materi tidak tersedia',
                                   'isi tak sesuai judul', 'tidak dapat diolah',
                                   'materi tidak relevan', 'materi tidak cocok',
                                   'tidak bisa diolah', 'tidak dapat diproses')):
        if source_url:
            catat_tolak_ai_token(source_url, 'AI output error: ' + judul[:80])
        raise BeritaLama('AI output error: ' + judul[:60])
    if not judul or len(judul.strip()) < 10:
        if source_url:
            catat_tolak_ai_token(source_url, 'judul AI terlalu pendek: ' + judul[:40])
        raise BeritaLama('judul AI kosong/terlalu pendek: "' + judul[:30] + '"')
    if not isi or len(isi.strip()) < 100:
        if source_url:
            catat_tolak_ai_token(source_url, 'isi AI terlalu pendek: ' + str(len(isi)))
        raise BeritaLama('isi AI kosong/terlalu pendek: ' + str(len(isi)) + ' char')

    waktu = (obj.get('waktu_kejadian') or '').strip()
    gambar = (obj.get('deskripsi_gambar') or '').strip()
    frasa_akhir = _frasa_tertangkap(isi)
    if frasa_akhir:
        if source_url:
            catat_tolak_ai_token(source_url, 'diblokir pemeriksa: ' + str(frasa_akhir)[:50])
        raise Exception('diblokir pemeriksa: ' + str(frasa_akhir)[:50])
    alasan_janji = cek_janji_judul(judul, isi)
    if alasan_janji:
        if source_url:
            catat_tolak_ai_token(source_url, 'promise-check: ' + str(alasan_janji)[:80])
        raise Exception('diblokir promise-check: ' + alasan_janji)
    dua_topik = deteksi_dua_topik(judul, isi)
    if dua_topik:
        if source_url:
            catat_tolak_ai_token(source_url, 'anti-2-topik: ' + str(dua_topik)[:80])
        raise Exception('diblokir anti-2-topik: ' + dua_topik[:60])
    cek_dl = cek_dateline(isi, materi_asli)
    if cek_dl:
        if source_url:
            catat_tolak_ai_token(source_url, 'dateline: ' + str(cek_dl)[:80])
        raise Exception('diblokir dateline: ' + cek_dl[:60])
    dobel_dt = _dobel_dateline_topik(judul, isi)
    if dobel_dt:
        if source_url:
            catat_tolak_ai_token(source_url, 'diblokir anti-dobel-dateline: ' + dobel_dt[:80])
        raise Exception('diblokir anti-dobel-dateline: ' + dobel_dt[:100])
    if not judul_topik_besar(judul):
        for t in JUDUL_6JAM:
            if len(kata_inti(judul) & kata_inti(t)) >= DOBEL_6JAM_MIN_KATA:
                if DOBEL_6JAM_BUTUH_NAMA:
                    if _ada_nama_diri_judul(judul) or _ada_nama_diri_judul(t):
                        # V6.17.93: cek topik dobel NYATA (longgarkan)
                        irisan = kata_inti(judul) & kata_inti(t)
                        if not _topik_dobel6jam_nyata(judul, t, irisan):
                            continue
                        if source_url:
                            catat_tolak_ai_token(source_url, 'dobel-6jam: ' + t[:40])
                        raise Exception('diblokir anti-dobel-6jam: mirip "' + t[:40] + '"')
                else:
                    irisan = kata_inti(judul) & kata_inti(t)
                    if not _topik_dobel6jam_nyata(judul, t, irisan):
                        continue
                    if source_url:
                        catat_tolak_ai_token(source_url, 'dobel-6jam: ' + t[:40])
                    raise Exception('diblokir anti-dobel-6jam: mirip "' + t[:40] + '"')
    else:
        print('       Topik besar terdeteksi - gate 6jam dilewati.')
    nama_final = cek_narasumber_tanpa_nama(isi, kategori, judul)
    if nama_final:
        if source_url:
            catat_tolak_ai_token(source_url, 'narasumber tanpa nama: ' + nama_final[:80])
        raise Exception('DITOLAK - narasumber tanpa nama (' + nama_final[:60] + ')')
    nama_pejabat = _cek_nama_pejabat_dari_materi(materi_sumber, isi, kategori)
    if nama_pejabat:
        if source_url:
            catat_tolak_ai_token(source_url, 'nama pejabat hilang: ' + nama_pejabat[:80])
        raise Exception('DITOLAK - ' + nama_pejabat[:100])
    # V6.17.95: pakai konteks materi (ikan diizinkan kalau perikanan)
    gambar_terlarang = cek_deskripsi_gambar(gambar, materi_sumber)
    if gambar_terlarang:
        if source_url:
            catat_tolak_ai_token(source_url, 'filter gambar: ' + gambar_terlarang[:60])
        raise Exception('diblokir filter gambar: ' + gambar_terlarang[:60])
    jiplak = cek_jiplak(materi_sumber, judul + ' ' + isi,
                        judul_materi=judul_materi, kategori=kategori)
    if jiplak:
        if source_url:
            catat_tolak_ai_token(source_url, 'anti-jiplak: ' + jiplak[:80])
        raise Exception('diblokir ANTI-JIPLAK: ' + jiplak[:80])
    kualitas = _cek_kualitas_isi(isi, kategori)
    if kualitas:
        if source_url:
            catat_tolak_ai_token(source_url, 'kualitas isi: ' + kualitas[:80])
        raise Exception('DITOLAK - kualitas isi: ' + kualitas[:100])
    if wajib_topik and judul_materi:
        ok_kat, alasan_kat = _cek_kategori_isi_penuh(judul, isi, kategori)
        if not ok_kat:
            if source_url:
                catat_tolak_ai_token(source_url, 'DITOLAK kategori: ' + alasan_kat[:80])
            raise Exception('DITOLAK - ' + alasan_kat[:100])
        topik_masalah = cek_topik_ai_vs_materi(judul, isi, judul_materi,
                                                 summary_materi or materi_sumber,
                                                 kategori=kategori)
        if topik_masalah:
            if source_url:
                catat_tolak_ai_token(source_url, 'DITOLAK topik: ' + topik_masalah[:80])
            raise Exception('DITOLAK - ' + topik_masalah[:100])
    kateg_masalah = cek_kategori_dari_isi(isi, judul, kategori)
    if kateg_masalah:
        if source_url:
            catat_tolak_ai_token(source_url, 'kategori isi: ' + kateg_masalah[:80])
        raise Exception('DITOLAK - ' + kateg_masalah[:80])
    return judul, isi, ringkasan, waktu, gambar

def target_kata(materi_len):
    if materi_len < 500:
        return ('150-200 kata (2-3 paragraf) - sumber ringkas, tulis PADAT, '
                'dilarang menggembung dengan kalimat pengisi.')
    return '200-250 kata (3-5 paragraf).'

def _catatan_khusus_kategori(kategori_target):
    if kategori_target in ('internasional', 'internasional_asean', 'internasional_tt'):
        # V6.17.92: prompt dateline diperketat (anti-karang kota)
        return (
            '\n\nCATATAN KHUSUS KATEGORI LUAR NEGERI (V6.17.92):\n'
            '- DATELINE WAJIB kota LUAR NEGERI (bukan Jakarta/Indonesia).\n'
            '- DILARANG pakai dateline "JAKARTA", "INDONESIA" '
            'KECUALI materi memang tentang Indonesia di forum internasional.\n'
            '- DATELINE WAJIB SALIN DARI MATERI. JANGAN karang kota yang '
            'TIDAK ADA di materi sumber.\n'
            '- KALAU materi TIDAK menyebut kota sama sekali → JANGAN pakai '
            'nama kota. Pakai nama NEGARA saja: "MALAYSIA - ", '
            '"AMERIKA SERIKAT - ", "INGGRIS - ".\n'
            '- DILARANG menebak kota (contoh: materi tidak sebut Putrajaya '
            '→ JANGAN tulis PUTRAJAYA).\n'
            '- Contoh BENAR: materi sebut "Kuala Lumpur" → '
            '"KUALA LUMPUR, MALAYSIA - ".\n'
            '- Contoh SALAH: materi tidak sebut kota → tulis "PUTRAJAYA" '
            '(KARANG!).\n'
            '- EVENT BESAR → dateline WAJIB kota penyelenggara.\n'
        )
    return ''

def _catatan_anti_jiplak():
    return (
        '\n\nANTI-JIPLAK — ATURAN BARU:\n'
        'FAKTA WAJIB SALIN UTUH — BUKAN JIPLAK:\n'
        '- Nama orang (nara sumber, pejabat, tokoh, warga) → SALIN PERSIS.\n'
        '- Gelar (Drs., Ir., S.T., S.H., M.Si., M.M., Dr., Prof., M.Pd.I., dll) → SALIN PERSIS.\n'
        '- Jabatan (Bupati, Wali Kota, Kapolres, Menteri, Direktur, dll) → SALIN PERSIS.\n'
        '- Pangkat TNI/Polri (Jenderal, AKBP, AKP, Kombes, dll) → SALIN PERSIS.\n'
        '- Titel (H., Hj., R.A., dll) → SALIN PERSIS.\n'
        '- Nama lokasi/tempat → SALIN PERSIS.\n'
        '- Semua fakta di atas SAH & LEGAL.\n'
        '\n'
        'NARASI WAJIB DIUBAH:\n'
        '- Kalimat non-fakta wajib beda dengan materi.\n'
        '- DILARANG 25+ kata berurutan sama materi (kecuali fakta di atas).\n'
        '- Sinonim: "mengatakan" → "menuturkan/ujar".\n'
        '- JUDUL: DILARANG sama/mirip judul materi.\n'
        '\n'
        'CATATAN: Kutipan langsung dalam tanda petik BOLEH SAMA.\n'
        '\n'
        'FRASA PROTOKOLER RESMI BOLEH SAMA:\n'
        '- "dalam rangka kunjungan kerja", "turut hadir", "didampingi oleh",\n'
        '  "dalam sambutannya", "sebagai bentuk komitmen", dll → SAH SAMA.\n'
        '- Frasa resmi pemerintahan TIDAK dianggap jiplak.\n'
        '\n'
        'JUDUL — ATURAN KETAT:\n'
        '- JUDUL WAJIB BEDA TOTAL dari judul materi sumber.\n'
        '- Kalau mirip ≥75% → ditolak, wajib tulis ulang.\n'
        '- Ganti kata kunci, susun ulang, sinonimkan.\n'
        '- DILARANG menyalin 5+ kata berturut-turut dari judul materi.\n'
        '- Contoh BENAR:\n'
        '  * Materi: "Wali Kota Resmikan 3 Dapur MBG"\n'
        '  * Judul: "Tiga Fasilitas MBG Baru Hadir di Cilegon"\n'
        '- Contoh SALAH:\n'
        '  * Materi: "Wali Kota Resmikan 3 Dapur MBG"\n'
        '  * Judul: "Wali Kota Resmikan 3 Dapur MBG di Cilegon" (JIPLAK!)\n'
    )

def _catatan_kategori_ketat(kategori_target):
    if not kategori_target or kategori_target == 'breaking':
        return ''
    if kategori_target in ('internasional', 'internasional_asean', 'internasional_tt'):
        return ''
    kata_kunci = KATA_KUNCI_KATEGORI.get(kategori_target, [])
    if not kata_kunci:
        return ''
    contoh = ', '.join(kata_kunci[:8])
    catatan_gelar = ''
    if kategori_target in ('nasional', 'daerah'):
        catatan_gelar = (
            '\n\nWAJIB NAMA PEJABAT LENGKAP (PELANGGARAN = TOLAK):\n'
            '- Kalau materi memuat nama pejabat → WAJIB tulis JABATAN + NAMA + GELAR.\n'
            '- Kalau materi TIDAK memuat nama → tulis "Pemkab X"/"Pemkot X" saja.\n'
            '- TNI/Polri: PANGKAT + NAMA + JABATAN wajib kalau ada di materi.\n'
            '- WAJIB tulis SEMUA nama pejabat yang ada di materi.\n'
            '- WAJIB sebut LOKASI spesifik kalau materi memuatnya.\n'
            '\n'
            'ATURAN DATELINE KETAT (PELANGGARAN = TOLAK):\n'
            '- DATELINE WAJIB SALIN DARI MATERI. JANGAN karang kota.\n'
            '- Kalau materi sebut kota A → dateline WAJIB kota A.\n'
            '- Kalau materi TIDAK sebut kota → dateline WAJIB provinsi/kabupaten.\n'
            '- DILARANG pakai kota yang TIDAK ADA di materi sumber.\n'
            '- Ejaan kota WAJIB PERSIS (contoh: "Madiun" BUKAN "Madium").\n'
        )
    catatan_ekonomi = ''
    if kategori_target == 'ekonomi':
        catatan_ekonomi = (
            '\n\nCATATAN KHUSUS EKONOMI:\n'
            '- JUDUL WAJIB memuat minimal 1 kata ekonomi.\n'
            '- ISI WAJIB memuat angka/data konkret dari materi.\n'
        )
    catatan_olahraga = ''
    if kategori_target == 'olahraga':
        catatan_olahraga = (
            '\n\nCATATAN KHUSUS OLAHRAGA:\n'
            '- "Klasemen medali" (ASIAD/Asian Games) = SAH kategori olahraga.\n'
            '- Turnamen seperti FIFA ASEAN Cup, Asian Games, SEA Games, Olimpiade = SAH.\n'
            '- DATELINE WAJIB kota yang ADA di materi. JANGAN karang.\n'
        )
    # V6.17.95: catatan khusus gambar perikanan/pedagang ikan
    catatan_gambar_ikan = ''
    if kategori_target in ('nasional', 'daerah', 'ekonomi'):
        catatan_gambar_ikan = (
            '\n\nCATATAN GAMBAR (V6.17.95):\n'
            '- Kalau materi tentang PEDAGANG IKAN, NELAYAN, PERIKANAN, TAMBAK,\n'
            '  BUDIDAYA IKAN → kata "fish"/"ikan" di deskripsi_gambar DIIZINKAN.\n'
            '- Contoh benar: deskripsi_gambar "fish market fresh seafood" — OK.\n'
        )
    return (
        '\n\nFILTER KATEGORI (WAJIB — kalau tidak cocok, tulis {"tolak": "tidak cocok kategori: <sebutkan materi apa>"}):\n'
        '- Kategori target: ' + kategori_target + '.\n'
        '- Materi WAJIB memuat kata kunci kategori: ' + contoh + '.\n'
        '- Kalau materi TIDAK tentang kategori ini → TULIS tolak.\n'
        '- WAJIB tulis alasan tolak DETIL 1-2 kata setelah titik dua.\n'
        + catatan_gelar
        + catatan_ekonomi
        + catatan_olahraga
        + catatan_gambar_ikan
    )

def _catatan_ibu_kota_provinsi(judul_materi, summary_materi, kategori_target):
    if kategori_target not in ('nasional', 'daerah'):
        return ''
    gab = ((judul_materi or '') + ' ' + (summary_materi or '')).lower()
    prov_ditemukan = []
    for prov, ibukota in KAMUS_PROVINSI_IBUKOTA.items():
        if prov in gab:
            prov_ditemukan.append((prov, ibukota))
    if not prov_ditemukan:
        return ''
    baris = []
    for prov, ibukota in prov_ditemukan[:3]:
        baris.append('  * "' + prov.title() + '" → ibukota: ' + ibukota.upper())
    return (
        '\n\nDATELINE — IBU KOTA PROVINSI (WAJIB):\n'
        '- Materi menyebut provinsi berikut. Kalau materi TIDAK sebut kota '
        'spesifik, WAJIB pakai ibu kota provinsi:\n'
        + '\n'.join(baris) + '\n'
        '- DILARANG karang kota lain di luar provinsi itu.\n'
        '- Ejaan kota WAJIB PERSIS (contoh: "Madiun" BUKAN "Madium").\n'
    )

def ai_rewrite_single(c, kategori_target=''):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    ok_valid, alasan_valid = _materi_valid(c.get('title', ''), materi, dari_scraping=kaya, kategori=kategori_target)
    if not ok_valid:
        print('       Materi tidak valid - skip: ' + alasan_valid[:80])
        if c.get('link'):
            catat_tolak_ai_token(c.get('link'), 'materi tidak valid: ' + alasan_valid[:100])
        raise BeritaLama('materi tidak valid: ' + alasan_valid[:60])
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian sebagai peristiwa TERKINI dengan tanggal konkret.\n')
    catatan_eko = _catatan_ekonomi_khusus(kategori_target, c.get('title', ''), materi)
    catatan_ibukota = _catatan_ibu_kota_provinsi(c.get('title', ''), c.get('summary', ''), kategori_target)
    catatan_portal_daerah = _catatan_portal_daerah(c.get('link', ''), kategori_target)
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + target_kata(len(materi)) + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi[:1500] + '\n\n'
            'Tulis ulang sesuai SEMUA aturan:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: WAJIB kota/provinsi spesifik (bukan "INDONESIA - ").\n'
            '- DATELINE: WAJIB SALIN DARI MATERI. JANGAN karang kota.\n'
            '- Ejaan kota WAJIB PERSIS (contoh: "Madiun" BUKAN "Madium").\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis JABATAN + NAMA LENGKAP + GELAR.\n'
            '- Kalau materi TIDAK ada nama pejabat → tulis "Pemkab X"/"Pemkot X" saja.\n'
            '- TNI/POLRI: WAJIB nama + pangkat + jabatan.\n'
            '- GELAR AKADEMIK: ikut kalau ada di materi (tulis persis).\n'
            '- WAJIB tulis SEMUA nama pejabat dari materi (bukan cuma 1).\n'
            '- DILARANG pakai kalimat template kosong.\n'
            '- WAJIB sebut LOKASI spesifik (kecamatan/kelurahan/jalan kalau ada di materi).\n'
            '- WAJIB sebut KRONOLOGI: siapa, apa, di mana, kapan, mengapa.\n'
            '- NAMA LEMBAGA: JANGAN diterjemahkan.\n'
            '- JUDUL DAN ISI: HARUS satu topik yang sama, sesuai materi.\n'
            '- JUDUL: DILARANG sama/mirip judul asli materi — WAJIB judul BEDA.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang dengan kalimatmu sendiri.\n'
            '- Jangan sebut portal/media sumber.'
            + catatan_eko
            + catatan_ibukota
            + catatan_portal_daerah
            + _catatan_khusus_kategori(kategori_target)
            + _catatan_anti_jiplak()
            + _catatan_kategori_ketat(kategori_target))
    return ai_write(user, materi_sumber=materi, kategori=kategori_target,
                    judul_materi=c.get('title', ''),
                    summary_materi=c.get('summary', ''),
                    wajib_topik=True,
                    source_url=c.get('link', ''))

def ai_rewrite_multi(items, kategori_target=''):
    k = konteks_waktu()
    bagian = []
    total_len = 0
    tgl = None
    semua_materi = ''
    semua_judul = []
    semua_summary = []
    kaya_ada = False
    for i, it in enumerate(items[:3], 1):
        materi, kaya = ambil_materi_kaya(it)
        if kaya:
            total_len += len(materi)
            kaya_ada = True
        else:
            total_len += len(it.get('summary', ''))
        if it.get('tgl_pub') and not tgl:
            tgl = it['tgl_pub']
        semua_judul.append(it.get('title', ''))
        semua_summary.append(it.get('summary', '')[:300])
        bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + it['title'] + '\nIsi: ' + materi[:800])
        semua_materi += ' ' + materi
    dari_scraping = kaya_ada
    ok_valid, alasan_valid = _materi_valid(items[0].get('title', ''), semua_materi, dari_scraping=dari_scraping, kategori=kategori_target)
    if not ok_valid:
        print('       Materi gabungan tidak valid - skip: ' + alasan_valid[:80])
        if items[0].get('link'):
            catat_tolak_ai_token(items[0].get('link'), 'materi gabungan tidak valid: ' + alasan_valid[:100])
        raise BeritaLama('materi gabungan tidak valid: ' + alasan_valid[:60])
    judul_materi_gabung = ' | '.join(semua_judul)
    summary_materi_gabung = ' '.join(semua_summary)
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian sebagai peristiwa TERKINI.\n')
    catatan_eko = _catatan_ekonomi_khusus(kategori_target, judul_materi_gabung, semua_materi)
    catatan_ibukota = _catatan_ibu_kota_provinsi(judul_materi_gabung, summary_materi_gabung, kategori_target)
    catatan_portal_daerah = _catatan_portal_daerah(items[0].get('link', '') if items else '', kategori_target)
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + target_kata(total_len) + '\n\n'
            'Berikut beberapa materi tentang SATU peristiwa yang sama:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita KramaNews:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: WAJIB kota/provinsi spesifik (bukan "INDONESIA - ").\n'
            '- DATELINE: WAJIB SALIN DARI MATERI. JANGAN karang kota.\n'
            '- Ejaan kota WAJIB PERSIS (contoh: "Madiun" BUKAN "Madium").\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis JABATAN + NAMA LENGKAP + GELAR.\n'
            '- Kalau materi TIDAK ada nama pejabat → tulis "Pemkab X"/"Pemkot X" saja.\n'
            '- TNI/POLRI: WAJIB nama + pangkat + jabatan.\n'
            '- GELAR AKADEMIK: ikut kalau ada di materi.\n'
            '- WAJIB tulis SEMUA nama pejabat dari materi.\n'
            '- DILARANG pakai kalimat template kosong.\n'
            '- WAJIB sebut LOKASI spesifik + KRONOLOGI.\n'
            '- NAMA LEMBAGA: JANGAN diterjemahkan.\n'
            '- JUDUL DAN ISI: HARUS satu topik yang sama.\n'
            '- JUDUL: DILARANG sama/mirip judul asli materi.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang dengan kalimatmu sendiri.'
            + catatan_eko
            + catatan_ibukota
            + catatan_portal_daerah
            + _catatan_khusus_kategori(kategori_target)
            + _catatan_anti_jiplak()
            + _catatan_kategori_ketat(kategori_target))
    return ai_write(user, timeout=180, materi_sumber=semua_materi,
                    kategori=kategori_target,
                    judul_materi=judul_materi_gabung,
                    summary_materi=summary_materi_gabung,
                    wajib_topik=True,
                    source_url=items[0].get('link', '') if items else '')

# V6.17.89: bersihkan control char dari payload sebelum insert
def _bersih_control_char(teks):
    if not teks:
        return teks
    # Buang \x00-\x08, \x0b, \x0c, \x0e-\x1f, \x7f. Pertahankan \n (\x0a) dan \t (\x09).
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', str(teks))

def insert_news(judul, isi, ringkasan, cat, img, link, source_name, status,
                breaking=False, deskripsi_gambar=''):
    if not judul or len((judul or '').strip()) < 5:
        raise Exception('diblokir insert: judul kosong/terlalu pendek')
    if not isi or len((isi or '').strip()) < 50:
        raise Exception('diblokir insert: isi kosong/terlalu pendek')
    # V6.17.89: bersihkan control char (fix "Invalid control character")
    judul = _bersih_control_char(judul)
    isi = _bersih_control_char(isi)
    ringkasan = _bersih_control_char(ringkasan)
    source_name = _bersih_control_char(source_name)
    deskripsi_gambar = _bersih_control_char(deskripsi_gambar)
    m = re.match(r'^\s*([A-Z][A-Z\s\.,\'\-]{2,60}?)\s+[-–—]\s+(.*)$', isi, re.DOTALL)
    dateline = m.group(1).strip() if m else ''
    isi_bersih = m.group(2).strip() if m else isi
    if masih_barusan_terbit(judul):
        raise Exception('diblokir anti-dobel insert-momen')
    img_final = ''
    sumber_gambar = ''
    if deskripsi_gambar:
        img_final, sumber_gambar = cari_gambar_otomatis(deskripsi_gambar, judul)
        if img_final and sumber_gambar == 'pexels':
            print('   Gambar Pexels - langsung pakai (vision off).')
    if not img_final:
        img_final = 'https://picsum.photos/seed/kn' + str(int(datetime.now().timestamp())) + '/800/500'
        print('   Fallback Picsum dipakai.')
    payload = {
        'title': judul, 'excerpt': ringkasan, 'content': isi_bersih,
        'category': cat, 'author': AUTHOR_NAME, 'img': img_final,
        'dateline': dateline, 'source_name': source_name, 'source_url': link,
        'written_by': 'ai', 'status': status,
    }
    if breaking:
        payload['breaking'] = True
    edge_call({'action': 'insert', 'payload': payload})
    catat_gambar_terpakai(img_final)
    JUDUL_TERPAKAI.append(normalisasi_judul(judul))

def vision_nilai_gambar(img_url, judul_berita):
    return None

def gambar_lolos_blur_gate(img_url, judul_berita):
    return True

def _target_teknologi(dom):
    if dom['nama'].startswith(('Gadget', 'AI')):
        return ('300-350 kata (4-6 paragraf) - PADAT & LENGKAP, '
                'sesuai aturan kedalaman domain.')
    return '250-300 kata (4-5 paragraf) - LENGKAP & BANYAK.'

def ai_rewrite_teknologi_single(c, dom):
    k = konteks_waktu()
    materi, kaya = ambil_materi_kaya(c)
    ok_valid, alasan_valid = _materi_valid(c.get('title', ''), materi, dari_scraping=kaya, kategori='teknologi')
    if not ok_valid:
        print('       Materi teknologi tidak valid - skip: ' + alasan_valid[:80])
        if c.get('link'):
            catat_tolak_ai_token(c.get('link'), 'materi tidak valid: ' + alasan_valid[:100])
        raise BeritaLama('materi tidak valid: ' + alasan_valid[:60])
    label_materi = 'ISI PENUH ARTIKEL SUMBER (scraping)' if kaya else 'RINGKASAN SUMBER'
    tgl = c.get('tgl_pub')
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian TERKINI dengan tanggal konkret.\n')
    catatan_ibukota = _catatan_ibu_kota_provinsi(c.get('title', ''), c.get('summary', ''), 'teknologi')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'JENIS MATERI: ' + label_materi + '\n'
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTIP):\n' + dom['aturan'] + '\n\n'
            'MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Isi: ' + materi[:1500] + '\n\n'
            'Tulis berita teknologi sesuai SEMUA aturan sistem + ATURAN '
            'KEDALAMAN DOMAIN di atas:\n'
            '- TANGGAL KONKRET di isi berita.\n'
            '- DATELINE: WAJIB kota/provinsi spesifik (bukan "INDONESIA - ").\n'
            '- DATELINE: WAJIB SALIN DARI MATERI. JANGAN karang kota.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi.\n'
            '- JUDUL: DILARANG sama/mirip judul asli materi — WAJIB judul BEDA.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar: 3-6 kata kunci DARI ELEMEN UTAMA BERITA.\n'
            '- Tulis ulang kalimatmu sendiri.'
            + catatan_ibukota
            + _catatan_anti_jiplak()
            + _catatan_kategori_ketat('teknologi'))
    return ai_write(user, materi_sumber=materi, kategori='teknologi',
                    judul_materi=c.get('title', ''),
                    summary_materi=c.get('summary', ''),
                    wajib_topik=True,
                    source_url=c.get('link', ''))

def ai_rewrite_teknologi_multi(items, dom):
    k = konteks_waktu()
    bagian = []
    tgl = None
    semua_materi = ''
    semua_judul = []
    semua_summary = []
    kaya_ada = False
    for i, it in enumerate(items[:3], 1):
        materi, kaya = ambil_materi_kaya(it)
        if kaya:
            kaya_ada = True
        if it.get('tgl_pub') and not tgl:
            tgl = it['tgl_pub']
        semua_judul.append(it.get('title', ''))
        semua_summary.append(it.get('summary', '')[:300])
        bagian.append('[MATERI ' + str(i) + ']\nJudul: ' + it['title'] + '\nIsi: ' + materi[:800])
        semua_materi += ' ' + materi
    dari_scraping = kaya_ada
    ok_valid, alasan_valid = _materi_valid(items[0].get('title', ''), semua_materi, dari_scraping=dari_scraping, kategori='teknologi')
    if not ok_valid:
        print('       Materi gabungan teknologi tidak valid - skip: ' + alasan_valid[:80])
        if items[0].get('link'):
            catat_tolak_ai_token(items[0].get('link'), 'materi gabungan tidak valid: ' + alasan_valid[:100])
        raise BeritaLama('materi gabungan tidak valid: ' + alasan_valid[:60])
    judul_materi_gabung = ' | '.join(semua_judul)
    summary_materi_gabung = ' '.join(semua_summary)
    if tgl:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: ' + tgl + ' - sumber terverifikasi segar.\n'
                     'WAJIB: tulis kejadian dengan tanggal itu di dalam berita.\n')
    else:
        baris_tgl = ('TANGGAL PUBLIKASI SUMBER: tidak tersedia.\n'
                     'WAJIB: tulis kejadian TERKINI.\n')
    catatan_ibukota = _catatan_ibu_kota_provinsi(judul_materi_gabung, summary_materi_gabung, 'teknologi')
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            + baris_tgl +
            'TARGET PANJANG: ' + _target_teknologi(dom) + '\n\n'
            'DOMAIN TEKNOLOGI HARI INI: ' + dom['nama'] + '\n'
            'ATURAN KEDALAMAN DOMAIN (WAJIB KUTIP):\n' + dom['aturan'] + '\n\n'
            'Berikut beberapa materi teknologi domain ini:\n\n'
            + '\n\n'.join(bagian) +
            '\n\nGabungkan menjadi SATU berita teknologi kaya:\n'
            '- TANGGAL KONKRET; DATELINE dari materi.\n'
            '- DATELINE: WAJIB SALIN DARI MATERI. JANGAN karang kota.\n'
            '- NAMA + JABATAN NARASUMBER: WAJIB tulis jabatan lengkap + nama.\n'
            '- DILARANG mengarang spesifikasi/harga/angka di luar materi.\n'
            '- JUDUL: DILARANG sama/mirip judul asli materi.\n'
            '- PERSEN: selalu simbol %.\n'
            '- deskripsi_gambar tanpa manusia/hewan/alas kaki/ibadah.\n'
            '- Jangan sebut media sumber.'
            + catatan_ibukota
            + _catatan_anti_jiplak()
            + _catatan_kategori_ketat('teknologi'))
    return ai_write(user, timeout=180, materi_sumber=semua_materi, kategori='teknologi',
                    judul_materi=judul_materi_gabung, summary_materi=summary_materi_gabung,
                    wajib_topik=True,
                    source_url=items[0].get('link', '') if items else '')

# AKHIR PART 3B
# PART 4A - KALENDER EVENT, RANGKUMAN, SESI OLAHRAGA CERDAS (V6.17.27)

KALENDER_EVENT = [
    {'nama': 'Asian Games Aichi-Nagoya 2026', 'mulai': '2026-09-19', 'selesai': '2026-10-04',
     'kota': 'Aichi-Nagoya', 'negara': 'Jepang',
     'query': [('klasmen medali asian games 2026', 'id'),
               ('perolehan medali indonesia asian games', 'id'),
               ('asian games 2026 hasil hari ini', 'id'),
               ('asian games nagoya medal tally', 'en')]},
    {'nama': 'Asian Para Games 2026', 'mulai': '2026-10-18', 'selesai': '2026-10-25',
     'kota': 'Aichi-Nagoya', 'negara': 'Jepang',
     'query': [('klasmen medali asian para games', 'id'),
               ('indonesia medali asian para games', 'id')]},
    {'nama': 'SEA Games Thailand 2026', 'mulai': '2026-12-09', 'selesai': '2026-12-20',
     'kota': 'Bangkok', 'negara': 'Thailand',
     'query': [('klasmen medali sea games 2026', 'id'),
               ('indonesia medali sea games thailand', 'id'),
               ('sea games 2026 hasil', 'id')]},
    {'nama': 'ASEAN Para Games 2027', 'mulai': '2027-01-20', 'selesai': '2027-01-27',
     'kota': 'Bangkok', 'negara': 'Thailand',
     'query': [('klasmen medali asean para games', 'id')]},
    {'nama': 'Winter Olympics Milano-Cortina 2026', 'mulai': '2027-02-06', 'selesai': '2027-02-22',
     'kota': 'Milano-Cortina', 'negara': 'Italia',
     'query': [('winter olympics 2026 medal tally', 'en'),
               ('winter olympics hasil', 'id')]},
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
    '- PERSEN: selalu simbol % - dilarang kata "persen".\n'
)

ATURAN_OLAHRAGA_KOMPETISI = (
    '- SYARAT WAJIB BERITA OLAHRAGA KOMPETISI (SANGAT PENTING):\n'
    '- WAJIB sebutkan SKOR AKHIR setiap pertandingan dengan ANGKA PERSIS.\n'
    '  Format: "Tim A 2 - 1 Tim B".\n'
    '- WAJIB sebutkan KLASEMEN SEMENTARA bila materi memuatnya.\n'
    '- DILARANG menulis "menang tipis", "kalah dramatis", "berbagi angka"\n'
    '  tanpa angka persis.\n'
    '- WAJIB salin APA ADUNA blok [KLASMEN]...[/KLASMEN] bila materi ada.\n'
    '- WAJIB salin APA ADUNA blok [MEDALI]...[/MEDALI] bila materi ada.\n'
    '- KHUSUS NBA/WNBA: klasmen WAJIB dibagi per WILAYAH (Timur/Barat)\n'
    '  atau per DIVISI, JANGAN digabung jadi satu tabel.\n'
    '- PERSEN: selalu simbol % - dilarang kata "persen".\n'
)

def _tulis_dari_kandidat(c, source_nama, breaking=False, kategori_target='olahraga'):
    try:
        judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(c, kategori_target=kategori_target)
        insert_news(judul, isi, ringkasan, 'olahraga', '',
                    c.get('link', ''), source_nama, 'published',
                    breaking=breaking, deskripsi_gambar=gambar)
        print('   TERBIT: ' + judul[:60])
        return 1
    except BeritaLama as bl:
        print('   Ditolak AI: ' + str(bl)[:60]); return 0
    except Exception as e:
        print('   Insert gagal: ' + str(e)[:80]); return 0

def _tulis_event_besar(cand, aktif, breaking=False):
    # V6.17.27: dateline WAJIB kota penyelenggara + kategori internasional
    bagian = []
    semua_materi = ''
    for i, c in enumerate(cand[:5], 1):
        materi, kaya = ambil_materi_kaya(c)
        label = 'ISI PENUH' if kaya else 'RINGKASAN'
        semua_materi += ' ' + materi
        bagian.append('[MATERI ' + str(i) + '] (' + label + ')\n'
                      'Judul: ' + c['title'] + '\nIsi: ' + materi[:1200])
    # Info kota + negara event
    info_kota = []
    for ev in aktif:
        kota = ev.get('kota', '')
        negara = ev.get('negara', '')
        if kota and negara:
            info_kota.append(ev['nama'] + ' → ' + kota.upper() + ', ' + negara.upper())
    info_kota_str = '\n'.join(info_kota)
    nama_event = ' & '.join(e['nama'] for e in aktif)
    k = konteks_waktu()
    user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
            'TUGAS KHUSUS: SATU berita EVENT BESAR BERLANGSUNG: ' + nama_event + '.\n\n'
            'KOTA + NEGARA PENYELENGGARA (WAJIB DIPAKAI SEBAGAI DATELINE):\n'
            + info_kota_str + '\n\n'
            'MATERI TERKINI:\n\n' + '\n\n'.join(bagian) + '\n\n'
            'ATURAN WAJIB EVENT BESAR:\n'
            '- DATELINE WAJIB kota penyelenggara + negara penyelenggara '
            '(contoh: "AICHI-NAGOYA, JEPANG - ").\n'
            '- DILARANG pakai "INDONESIA - " atau "JAKARTA - " — '
            'event besar diselenggarakan di luar negeri.\n'
            '- KATEGORI: internasional.\n'
            '- WAJIB menampilkan KLASMEN MEDALI sementara (peringkat, '
            'emas/perak/perunggu) bila materi memuatnya - minimal 5 '
            'negara teratas + POSISI INDONESIA (atau negara yang dibahas).\n'
            '- KLASMEN MEDALI WAJIB disalin APA ADUNA ke dalam blok:\n'
            '  [MEDALI]\n'
            '  Klasemen Medali {Nama Event}\n'
            '  1|Negara1|emas|perak|perunggu|total\n'
            '  2|Negara2|emas|perak|perunggu|total\n'
            '  ...\n'
            '  [/MEDALI]\n'
            '- JANGAN mengubah format blok [MEDALI] - langsung salin dari materi.\n'
            '- WAJIB menampilkan HASIL/medali yang diraih hari ini '
            'bila materi memuatnya.\n'
            '- Angka medali/tanggal WAJIB persis dari materi; DILARANG mengarang.\n'
            '- Jika materi TIDAK memuat klasmen medali sama sekali, '
            'laporkan pencapaian terbaru atlet/event yang disebut.\n'
            '- Panjang: 250-350 kata.\n'
            '- Judul maks 10 kata: sebut nama event + kata kunci.\n'
            '- PERSEN: simbol %.\n'
            '- NAMA + JABATAN narasumber wajib lengkap.\n'
            '- deskripsi_gambar: tema stadion/medali/atletik 3-6 kata - '
            'TANPA hewan, manusia, alas kaki.\n'
            '- Jangan sebut media sumber.\n'
            '- DILARANG kalimat sampah seperti "pertandingan berlangsung seru",\n'
            '  "para atlet tampil memukau", "suasana meriah" TANPA data konkret.\n'
            '- Setiap kalimat WAJIB memuat minimal 1 dari: angka, nama, tempat, tanggal.')
    print('   AI menulis rekap event besar (' + str(len(cand[:5])) + ' materi)...')
    try:
        judul, isi, ringkasan, waktu, gambar = ai_write(user, kategori='olahraga',
                                                         materi_sumber=semua_materi,
                                                         judul_materi=nama_event,
                                                         summary_materi=info_kota_str,
                                                         wajib_topik=False)
    except BeritaLama as bl:
        print('   Ditolak AI: ' + str(bl)[:60]); return 0
    except Exception as e:
        print('   ' + str(e)[:90]); return 0
    if sudah_serupa(judul):
        print('   Hasil AI dobel - skip.'); return 0
    try:
        insert_news(judul, isi, ringkasan, 'olahraga', '',
                    cand[0].get('link', ''), 'Event Besar Dunia',
                    'published', breaking=breaking, deskripsi_gambar=gambar)
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

def olahraga_sudah_terbit_hari_ini(sumber):
    try:
        now_wita = datetime.now(WITA)
        awal_hari = datetime(now_wita.year, now_wita.month, now_wita.day, 0, 0, 0, tzinfo=WITA)
        batas = awal_hari.astimezone(timezone.utc).isoformat()
        rows = rest_get('?select=id&source_name=eq.' + quote_plus(sumber)
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

KATA_REGIONAL_OLAHRAGA = [
    'indonesia', 'timnas', 'pssi', 'liga 1', 'tarakan', 'kaltara', 'asean', 'aff',
    'sea games', 'asian games', 'olimpiade', 'olympic', 'badminton', 'bulu tangkis',
    'voli', 'volly', 'volleyball', 'bola voli', 'basket', 'ibl', 'tenis', 'motogp',
    'mandalika', 'f1', 'formula 1', 'jepang', 'korea', 'thailand', 'malaysia',
    'vietnam', 'singapura', 'filipina', 'china', 'india', 'asia', 'piala dunia',
    'fifa', 'liga champions', 'uefa', 'eropa', 'premier league', 'champions league',
    'europa league', 'la liga', 'serie a', 'bundesliga', 'ligue 1', 'eredivisie',
    'world cup', 'europe', 'european', 'singapore', 'philippines', 'japan', 'nba',
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
        awal_hari = datetime(now_wita.year, now_wita.month, now_wita.day, 0, 0, 0, tzinfo=WITA)
        batas = awal_hari.astimezone(timezone.utc).isoformat()
        rows = rest_get('?select=id&source_name=eq.' + quote_plus('Rangkuman Olahraga')
                        + '&created_at=gte.' + batas)
        return len(rows) > 0
    except Exception:
        return False

def sesi_rangkuman_umum(today_urls, seen):
    print('\nRANGKUMAN OLAHRAGA UMUM: DIMATIKAN (V6.17.11) - skip.')
    return 0

# V6.17.27: API Football kurangi request (hemat 429)
def buat_materi_rangkuman_eropa():
    skor_semua = []
    klasemen_blok = []
    klasemen_teks = []
    semua_liga = ESPN_LIGA_TOP + ESPN_LIGA_LAIN
    for idx, (code, nama) in enumerate(semua_liga):
        # Delay antar liga
        if idx > 0:
            time.sleep(2)
        skor_api = api_skor_football(code, hari_mundur=2)
        n_api = len(skor_api)
        if skor_api:
            for s in skor_api:
                skor_semua.append(nama.split(' (')[0] + ': ' + s)
            print('   ' + nama.split(' (')[0] + ': API ' + str(n_api) + ' laga')
        time.sleep(1)
        blok_api, teks_api = api_klasmen_football(code)
        if blok_api:
            klasemen_blok.append(blok_api)
            klasemen_teks.append(teks_api)
    if not skor_semua:
        print('   TIDAK ADA SKOR DARI API FOOTBALL - return None')
        return None
    print('   Total laga terkumpul: ' + str(len(skor_semua))
          + ' - klasmen: ' + str(len(klasemen_blok)) + ' blok')
    bagian = []
    bagian.append('HASIL LAGA TERAKHIR LIGA TOP EROPA (ANGKA RESMI MESIN - SALIN PERSIS):\n'
                  + '\n'.join(skor_semua))
    if klasemen_teks:
        bagian.append('KLASMEN (ANGKA RESMI MESIN - WAJIB disalin ke blok [KLASMEN]):\n'
                      + '\n'.join(klasemen_teks[:4]))
    if klasemen_blok:
        bagian.append('BLOK KLASMEN SIAP-RENDER (WAJIB disalin APA ADUNA di '
                      'akhir isi berita, jangan diubah, jangan digandakan):\n'
                      + '\n\n'.join(klasemen_blok[:6]))
    return '\n\n'.join(bagian)

def buat_materi_rangkuman_nba():
    print('   NBA via ESPN DIHAPUS - gunakan Google News')
    return None

def _tulis_event_besar_dari_cand(today_urls, seen, aktif):
    sumber = buat_sumber_event(aktif)
    cand = collect_candidates(sumber, today_urls, seen, max_umur_jam=72, kategori='internasional')
    if not cand:
        print('   Tidak ada materi event segar.')
        return 0
    return _tulis_event_besar(cand, aktif, breaking=False)

def sesi_olahraga_api(jenis):
    now = datetime.now(WITA)
    jam = now.hour

    if jenis == 'eropa' and 7 <= jam < 12:
        print('\nOLAHRAGA ' + str(jam) + ':00 - LIGA TOP EROPA / EVENT BESAR / OLAHRAGA UMUM')
        if olahraga_sudah_terbit_hari_ini('ESPN Data'):
            print('   ESPN sudah terbit HARI INI - skip.')
            return 1
        print('   TAHAP 1: API Football Liga Top Eropa...')
        materi = buat_materi_rangkuman_eropa()
        if materi:
            k = konteks_waktu()
            user = ('TANGGAL SEKARANG: ' + k['hari_ini'] + ' (kemarin: ' + k['kemarin'] + ')\n'
                    'TUGAS: LAPORAN HASIL LIGA TOP EROPA + KLASMEN SEMENTARA.\n'
                    'GAYA: MINIM KATA.\n\n' + materi + '\n\n'
                    'FORMAT WAJIB:\n'
                    '1. Buka 1 kalimat: "Inilah hasil Liga Eropa dan klasmen sementara:"\n'
                    '2. Daftar SKOR pertandingan dengan ANGKA PERSIS.\n'
                    '3. SALIN APA ADUNA semua blok [KLASMEN]...[/KLASMEN].\n'
                    '4. DILARANG narasi bertele-tele.\n'
                    '5. Dateline: "LONDON, INGGRIS - " (liga top Eropa).\n'
                    '6. Judul maks 10 kata: sebut "Hasil Liga Eropa".\n'
                    '7. deskripsi_gambar: tema stadion/bola.\n'
                    '8. Jangan sebut sumber data.')
            print('   AI menulis dari data API Football...')
            try:
                judul, isi, ringkasan, waktu, gambar = ai_write(user, kategori='olahraga', wajib_topik=False)
            except BeritaLama as bl:
                print('   Ditolak AI: ' + str(bl)[:60]); materi = None
            except Exception as e:
                print('   ' + str(e)[:90]); materi = None
            if materi:
                try:
                    insert_news(judul, isi, ringkasan, 'olahraga', '',
                                'https://www.api-football.com/ (data mesin)',
                                'ESPN Data', 'published', breaking=False,
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
        cand = collect_candidates(SUMBER_BOLA, today_urls, seen, max_umur_jam=30, kategori='internasional')
        bola = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'],
                ['bola', 'liga', 'sepak', 'football', 'soccer', 'premier',
                 'champions', 'bundesliga', 'serie a', 'la liga'])]
        if bola:
            hasil = _tulis_dari_kandidat(bola[0], 'Olahraga Pagi',
                                          breaking=False, kategori_target='internasional')
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
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Pagi',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   Tidak ada berita olahraga apa pun - skip.')
        return 0

    if jenis == 'nba' and 13 <= jam < 17:
        print('\nOLAHRAGA ' + str(jam) + ':00 - NBA/WNBA')
        if olahraga_sudah_terbit_hari_ini('ESPN Data NBA'):
            print('   ESPN NBA sudah terbit HARI INI - skip.')
            return 1
        print('   TAHAP 1: NBA via Google News...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_NBA = [
            GN('NBA scores results', 'en', 'GN NBA Hasil'),
            GN('NBA standings', 'en', 'GN NBA Klasmen'),
            GN('WNBA scores results', 'en', 'GN WNBA Hasil'),
            GN('NBA news', 'en', 'GN NBA Berita'),
            GN('berita NBA', 'id', 'GN NBA Berita ID'),
        ]
        cand = collect_candidates(SUMBER_NBA, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'], ['nba', 'wnba'])]
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Rangkuman NBA',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   TAHAP 2: olahraga umum (fallback)...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_OLGA_UMUM = [
            GN('berita olahraga terkini', 'id', 'GN Olahraga'),
            GN('hasil pertandingan hari ini', 'id', 'GN Hasil Hari Ini'),
            RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
            RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        ]
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Siang',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   Tidak ada berita olahraga - skip.')
        return 0
    return 0

# AKHIR PART 4A

# PART 4B - BREAKING, PASAR MODAL, SESI KATEGORI, RUN SESSION

def is_berita_politik_hukum(teks):
    t = (teks or '').lower()
    KATA_POLITIK_HUKUM = [
        'tersangka', 'korupsi', 'kpk', 'kejaksaan', 'pengadilan', 'sidang',
        'dakwaan', 'hukuman', 'pidana', 'penjara', 'ditahan', 'dpr', 'presiden',
        'menteri', 'gubernur', 'walikota', 'bupati', 'pileg', 'pilpres', 'pilkada',
        'partai', 'kampanye', 'demonstrasi', 'unjuk rasa', 'kerusuhan',
    ]
    for k in KATA_POLITIK_HUKUM:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            return True
    return False

def _iso_z(dt):
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

def _jam_breaking_aktif():
    jam = datetime.now(WITA).hour
    return 6 <= jam < 20

def _darurat_malam(judul, summary):
    t = ((judul or '') + ' ' + (summary or '')).lower()

    if 'gempa' in t or 'earthquake' in t:
        mag = ambil_magnitude(t)
        if mag is not None and mag >= 6.0:
            return True
        if 'magnitude 6' in t or 'magnitudo 6' in t or 'magnitude 7' in t or 'magnitudo 7' in t or 'magnitude 8' in t or 'magnitudo 8' in t or 'magnitude 9' in t or 'magnitudo 9' in t:
            return True

    if 'tsunami' in t:
        return True

    if any(k in t for k in ('perang', 'war', 'invasi', 'invasion')):
        return True

    if any(k in t for k in ('serangan nuklir', 'nuclear attack', 'nuclear test', 'uji nuklir', 'nuclear strike')):
        return True

    if any(k in t for k in ('kudeta', 'coup')):
        return True

    if any(k in t for k in ('erupsi', 'gunung meletus', 'volcanic eruption')):
        return True

    if any(k in t for k in ('kebakaran hutan aktif', 'kebakaran hutan meluas',
                             'kebakaran hutan besar', 'wildfire spreads',
                             'wildfire rages', 'kebakaran hutan mengancam')):
        return True

    return False

def _kandidat_beda_topik(kandidat_baru, kandidat_lama):
    if not kandidat_lama:
        return True
    kata_baru = kata_inti(kandidat_baru.get('title', ''))
    kata_lama = kata_inti(kandidat_lama.get('title', ''))
    irisan = kata_baru & kata_lama
    if len(irisan) >= 3:
        return False
    return True

# ══════════════════════════════════════════════════════
# V6.17.85: cek dobel breaking meski topik besar (karhutla dobel)
# ══════════════════════════════════════════════════════

def _topik_breaking_sudah_terbit(judul_baru, min_irisan=4):
    """V6.17.85: cek apakah topik breaking sudah pernah terbit,
    meskipun topiknya topik besar. Khusus untuk kasus karhutla dobel."""
    if not judul_baru:
        return None
    ki_baru = kata_inti(judul_baru)
    if not ki_baru:
        return None
    try:
        rows = rest_get('?select=title,created_at&breaking=eq.true'
                        '&order=created_at.desc&limit=20')
    except Exception:
        return None
    now = datetime.now(timezone.utc)
    for row in rows:
        try:
            d = datetime.fromisoformat(str(row['created_at']).replace('Z', '+00:00'))
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            if (now - d).total_seconds() > 6 * 3600:
                continue
            t_lama = row.get('title') or ''
            if not t_lama:
                continue
            ki_lama = kata_inti(t_lama)
            if not ki_lama:
                continue
            irisan = ki_baru & ki_lama
            if len(irisan) >= min_irisan:
                return ('topik breaking sudah terbit < 6 jam: ' + str(len(irisan))
                        + ' kata kunci sama — ' + str(sorted(list(irisan))[:4]))
        except Exception:
            continue
    return None

def sesi_breaking(today_urls, seen):
    made = 0
    slots = BREAKING_MAX_SLOT - len(get_breaking_list())
    print('\nBREAKING - slot tersedia: ' + str(slots) + '/' + str(BREAKING_MAX_SLOT))
    if slots <= 0:
        return 0

    jam_aktif = _jam_breaking_aktif()
    if not jam_aktif:
        print('   ⏰ Di luar jam breaking (06:07-19:07 WITA). Cek darurat dulu...')

    cand_dom = collect_candidates(BREAKING_DOMESTIK_FEEDS, today_urls, seen, max_umur_jam=30, kategori='breaking')
    skor_dom = sorted([(c, skor_domestik(c['title'], c['summary'])) for c in cand_dom], key=lambda x: -x[1])
    if skor_dom:
        print('   Top 5 skor domestik: ' + ', '.join(str(int(s)) for _, s in skor_dom[:5]))
    skor_dom = [x for x in skor_dom if x[1] >= SKOR_BREAKING_MIN_DOM]
    print('   Kandidat breaking domestik layak: ' + str(len(skor_dom)))

    cand_dun = collect_candidates(BREAKING_DUNIA_FEEDS, today_urls, seen, max_umur_jam=30, kategori='breaking')
    skor_dun = sorted([(c, skor_dunia(c['title'], c['summary'])) for c in cand_dun], key=lambda x: -x[1])
    skor_dun = [x for x in skor_dun if x[1] >= SKOR_BREAKING_MIN]
    print('   Kandidat breaking dunia layak: ' + str(len(skor_dun)))

    if not jam_aktif:
        skor_dom = [(c, s) for c, s in skor_dom if _darurat_malam(c['title'], c['summary'])]
        skor_dun = [(c, s) for c, s in skor_dun if _darurat_malam(c['title'], c['summary'])]

    if not skor_dom and not skor_dun:
        print('   Tidak ada kandidat breaking layak - skip.')
        return 0

    kandidat_gabung = []
    for c, s in skor_dom[:5]:
        kandidat_gabung.append((c, 'dom', s))
    for c, s in skor_dun[:5]:
        kandidat_gabung.append((c, 'dun', s))
    kandidat_gabung = sorted(kandidat_gabung, key=lambda x: -x[2])[:5]

    if not kandidat_gabung:
        print('   Tidak ada kandidat breaking layak - skip.')
        return 0

    percobaan = 0
    for c, tip, _skor in kandidat_gabung:
        if made >= slots:
            break
        if percobaan >= 5:
            break
        if sudah_serupa(c['title']):
            print('   Skip (dobel): ' + c['title'][:50])
            continue
        # V6.17.85: cek topik breaking sudah terbit (meski topik besar)
        topik_brk = _topik_breaking_sudah_terbit(c['title'], min_irisan=4)
        if topik_brk:
            print('   Skip (topik breaking sudah terbit): ' + topik_brk[:80])
            continue
        jdl_lower = (c.get('title') or '').lower()
        if any(x in jdl_lower for x in ('potret', 'sorotan', 'foto-foto', 'galeri',
                                         'in pictures', 'photos:', 'images:',
                                         'see photos', 'in photos')):
            print('   Skip (feature/potret, bukan breaking): ' + c['title'][:50])
            continue
        label = 'BREAKING DOM' if tip == 'dom' else 'BREAKING DUNIA'
        print('\n   [' + label + '] ' + c['title'][:70])
        percobaan += 1
        try:
            judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(
                c, kategori_target='breaking')
        except BeritaLama as bl:
            print('   Ditolak AI: ' + str(bl)[:60]); continue
        except Exception as e:
            print('   ' + str(e)[:90]); continue
        if tip == 'dom':
            if not _breaking_ada_lokasi(judul, isi):
                print('   DITOLAK - breaking tanpa lokasi spesifik: ' + judul[:50])
                continue
        # V6.17.85: cek topik breaking sudah terbit SETELAH AI tulis
        topik_brk_final = _topik_breaking_sudah_terbit(judul, min_irisan=4)
        if topik_brk_final:
            print('   DITOLAK - topik breaking sudah terbit: ' + topik_brk_final[:80])
            if c.get('link'):
                catat_tolak_ai_token(c.get('link'), 'breaking dobel topik: ' + topik_brk_final[:100])
            continue
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

# V6.17.66: tambah KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN biar "Kalimantan" lolos
def _breaking_ada_lokasi(judul, isi):
    gab = ((judul or '') + ' ' + (isi or '')).lower()
    for kota in KOTA_INDONESIA_DATELINE:
        if re.search(r'\b' + re.escape(kota) + r'\b', gab):
            return True
    for prov in KALIMANTAN_PROVINSI + PROVINSI_INDONESIA_LAIN:
        if re.search(r'\b' + re.escape(prov) + r'\b', gab):
            return True
    provinsi_tambahan = ['kalimantan', 'sumatera', 'sumatra', 'jawa', 'sulawesi',
                         'papua', 'bali', 'nusa tenggara', 'maluku',
                         'jakarta', 'yogyakarta', 'jogja']
    for prov in provinsi_tambahan:
        if re.search(r'\b' + re.escape(prov) + r'\b', gab):
            return True
    return False

KATA_DOMINAN_INDONESIA = [
    'indonesia', 'jakarta', 'jawa', 'sumatera', 'sumatra', 'kalimantan',
    'sulawesi', 'papua', 'bali', 'nusa tenggara', 'maluku', 'aceh', 'riau',
    'lampung', 'banten', 'jateng', 'jabar', 'jatim', 'kaltara', 'kaltim',
    'kalbar', 'kalsel', 'kalteng', 'sulut', 'sulteng', 'sulsel', 'sultra',
    'tarakan', 'balikpapan', 'samarinda', 'pontianak', 'banjarmasin',
    'makassar', 'manado', 'medan', 'palembang', 'pekanbaru', 'padang',
    'semarang', 'surabaya', 'bandung', 'yogyakarta', 'denpasar', 'mataram',
    'kupang', 'jayapura', 'ambon', 'bmkg', 'bnpb', 'basarnas', 'kemenkes',
    'kemenhut', 'klhk', 'polri', 'tni', 'prabowo', 'jokowi', 'menteri ri',
]

def kategori_breaking(c, tip):
    if tip == 'dun':
        return 'internasional'
    teks = (c.get('title', '') + ' ' + c.get('summary', '')).lower()
    hit_indo = sum(1 for k in KATA_DOMINAN_INDONESIA if k in teks)
    hit_asing = sum(1 for k in LUAR_NEGERI_WORDS if k in teks)
    if hit_indo >= 2 and hit_indo > hit_asing:
        return 'nasional'
    if any(w in teks for w in LUAR_NEGERI_WORDS):
        return 'internasional'
    return 'nasional'


KATEGORI_DB = {
    'nasional': 'nasional', 'daerah': 'daerah',
    'internasional_asean': 'internasional', 'internasional_tt': 'internasional',
    'internasional': 'internasional', 'ekonomi': 'ekonomi', 'olahraga': 'olahraga',
    'teknologi': 'teknologi', 'otomotif': 'otomotif', 'kesehatan': 'kesehatan',
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
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '') for it in items).lower()
    return any(w in teks for w in KALTARA_WORDS)

def kelompok_topik(items, kata_list):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '') for it in items).lower()
    return teks_mengandung(teks, kata_list)

def kelompok_regional_olahraga(items):
    teks = ' '.join((it.get('title') or '') + ' ' + (it.get('summary') or '') for it in items).lower()
    return teks_mengandung(teks, KATA_REGIONAL_OLAHRAGA)

def tolak_amerika_lokal(teks):
    t = (teks or '').lower()
    KATA_OLAHRAGA_TOLAK = [
        'nfl', 'mlb', 'nhl', 'wnba', 'mls', 'ncaa', 'cfb', 'super bowl',
        'world series', 'stanley cup', 'seahawks', 'patriots', 'cowboys',
        'packers', 'chiefs', '49ers', 'bills', 'dolphins', 'eagles', 'ravens',
        'bengals', 'yankees', 'dodgers', 'red sox', 'mets', 'cubs', 'astros',
        'bruins', 'maple leafs', 'penguins', 'lakers', 'celtics', 'warriors',
        'knicks', 'bulls nba', 'heat nba', 'suns nba', 'mavericks',
        'nuggets nba', 'bucks nba', 'sixers', 'spurs nba', 'raptors nba',
        'college football', 'college basketball', 'march madness',
        'northwestern', 'indiana hoosiers', 'south dakota', 'big ten',
        'sec football', 'pac-12', 'oregon', 'maps credit union',
        'athlete of the week', 'credit union', 'high school', 'prep sports',
        'varsity', 'vote athlete', 'player of the week',
    ]
    for k in KATA_OLAHRAGA_TOLAK:
        if re.search(r'\b' + re.escape(k) + r'\b', t):
            return True
    return False

# V6.17.88 + V6.17.92 + V6.17.94: batas percobaan kandidat
# V6.17.94: batas 1 untuk SEMUA jam (hemat token)
def produksi_satu(cat, today_urls, seen, utamakan_kaltara, utamakan_topik=None,
                  sumber_custom=None, domain_tek=None, wajib_regional=False,
                  sumber_fallback=None):
    jam_sekarang = datetime.now(WITA).hour
    # V6.17.94: batas 1 semua jam — hemat token
    batas_percobaan = 1
    max_umur = max_umur_kategori(cat)
    cand = collect_candidates(sumber_custom if sumber_custom else HUNT.get(cat, []),
                              today_urls, seen, max_umur_jam=max_umur, kategori=cat)
    if not cand:
        print('   (' + cat + ') Tidak ada kandidat segar.')
        return False
    sebelum_spam = len(cand)
    cand = [c for c in cand if not judul_spam(c['title'])]
    if sebelum_spam != len(cand):
        print('   (' + cat + ') ' + str(sebelum_spam - len(cand)) + ' judul spam dibuang.')
    if not cand:
        print('   (' + cat + ') Semua kandidat spam - skip.')
        return False
    if cat == 'internasional_tt':
        cand = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'], KATA_TT)]
        if not cand:
            print('   (tt) Tidak ada kandidat Timur Tengah segar.')
            return False
    if cat in ('internasional', 'internasional_asean', 'internasional_tt'):
        sebelum = len(cand)
        cand = [c for c in cand if not adalah_turnamen_olahraga(c['title'] + ' ' + c['summary'])]
        if sebelum != len(cand):
            print('   (' + cat + ') ' + str(sebelum - len(cand)) + ' kandidat turnamen olahraga dibuang (ke olahraga).')
        sebelum2 = len(cand)
        cand = [c for c in cand if not adalah_konten_otomotif(c['title'] + ' ' + c['summary'])]
        if sebelum2 != len(cand):
            print('   (' + cat + ') ' + str(sebelum2 - len(cand)) + ' kandidat otomotif dibuang (ke otomotif).')
        if cat == 'internasional_asean':
            sebelum_asean = len(cand)
            cand = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'], KATA_ASEAN_WAJIB)]
            if sebelum_asean != len(cand):
                print('   (' + cat + ') ' + str(sebelum_asean - len(cand)) + ' kandidat tanpa kata kunci asean dibuang.')
        sebelum3 = len(cand)
        cand = [c for c in cand if cek_kategori_cocok(cat, c['title'] + ' ' + c['summary']) is None]
        if sebelum3 != len(cand):
            print('   (' + cat + ') ' + str(sebelum3 - len(cand)) + ' kandidat tanpa kata luar negeri dibuang.')
    if cat == 'teknologi':
        sebelum = len(cand)
        cand = [c for c in cand if not adalah_konten_otomotif(c['title'] + ' ' + c['summary'])]
        if sebelum != len(cand):
            print('   (' + cat + ') ' + str(sebelum - len(cand)) + ' kandidat otomotif dibuang (ke otomotif).')
    if cat == 'ekonomi':
        sebelum = len(cand)
        cand = [c for c in cand if cek_kategori_cocok('ekonomi', c['title'] + ' ' + c['summary']) is None]
        if sebelum != len(cand):
            print('   (ekonomi) ' + str(sebelum - len(cand)) + ' kandidat tanpa kata ekonomi dibuang.')
    if wajib_regional and cat == 'olahraga':
        n_reg = sum(1 for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'], KATA_REGIONAL_OLAHRAGA))
        print('   (' + cat + ') Kandidat regional: ' + str(n_reg) + '/' + str(len(cand)) + ' (diprioritaskan, tidak wajib).')
    if cat == 'olahraga':
        sebelum_tolak = len(cand)
        cand = [c for c in cand if not tolak_amerika_lokal(c['title'] + ' ' + c['summary'])]
        if sebelum_tolak != len(cand):
            print('   (' + cat + ') ' + str(sebelum_tolak - len(cand)) + ' kandidat Amerika-lokal dibuang.')
    if not cand:
        print('   (' + cat + ') Semua kandidat habis setelah filter - skip.')
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
    kandidat_terpakai = []
    for g in groups:
        # V6.17.94: batas percobaan 1 semua jam
        if percobaan >= batas_percobaan:
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
        if kandidat_terpakai and not _kandidat_beda_topik(top, kandidat_terpakai[0]):
            print('   Skip (cadangan sama topik): ' + top['title'][:50])
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
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_multi(items, kategori_target=cat)
            else:
                judul, isi, ringkasan, waktu, gambar = ai_rewrite_single(top, kategori_target=cat)
        except BeritaLama as bl:
            print('   Ditolak AI: ' + str(bl)[:60]); continue
        except Exception as e:
            print('   ' + str(e)[:90]); continue
        kategori_final = KATEGORI_DB.get(cat, cat)
        kategori_paksa = tentukan_kategori_dari_isi(judul, isi)
        if kategori_paksa and cat in ('internasional', 'internasional_asean', 'internasional_tt', 'ekonomi'):
            print('   Kategori dipaksa dari isi: ' + cat + ' -> ' + kategori_paksa)
            kategori_final = kategori_paksa
        if sudah_serupa(judul):
            print('   Hasil AI dobel dengan judul yang sudah ada - skip.')
            continue
        try:
            img_url = get_image(top.get('entry'))
            if img_url and gambar_sudah_dipakai(img_url):
                img_url = ''
            src_nama = sumber_fallback if sumber_fallback else top.get('source', '')
            insert_news(judul, isi, ringkasan, kategori_final, img_url,
                        top.get('link', ''), src_nama,
                        'published', deskripsi_gambar=gambar)
            print('   Terbit: ' + judul[:60])
            return True
        except Exception as e:
            print('   Insert gagal: ' + str(e)[:80])
            kandidat_terpakai.append(top)
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

def sesi_olahraga_api(jenis):
    now = datetime.now(WITA)
    jam = now.hour

    if jenis == 'eropa' and 7 <= jam < 12:
        print('\nOLAHRAGA ' + str(jam) + ':00 - LIGA EROPA / EVENT BESAR / UMUM (Google News)')
        if olahraga_sudah_terbit_hari_ini('Olahraga Pagi'):
            print('   Olahraga Pagi sudah terbit HARI INI - skip.')
            return 1
        aktif = event_besara_aktif()
        if aktif:
            print('   TAHAP 1: event besar aktif...')
            today_urls = get_today_state()
            seen = set()
            if _tulis_event_besar_dari_cand(today_urls, seen, aktif) == 1:
                return 1
        else:
            print('   Tidak ada event besar aktif.')
        print('   TAHAP 2: berita bola via Google News...')
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
        cand = collect_candidates(SUMBER_BOLA, today_urls, seen, max_umur_jam=30, kategori='internasional')
        bola = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'],
                ['bola', 'liga', 'sepak', 'football', 'soccer', 'premier',
                 'champions', 'bundesliga', 'serie a', 'la liga'])]
        if bola:
            hasil = _tulis_dari_kandidat(bola[0], 'Olahraga Pagi',
                                          breaking=False, kategori_target='internasional')
            if hasil == 1:
                return 1
        print('   TAHAP 3: olahraga umum (fallback terakhir)...')
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
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Pagi',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   Tidak ada berita olahraga apa pun - skip.')
        return 0

    if jenis == 'nba' and 13 <= jam < 17:
        print('\nOLAHRAGA ' + str(jam) + ':00 - NBA/WNBA (Google News)')
        if olahraga_sudah_terbit_hari_ini('Rangkuman NBA'):
            print('   NBA sudah terbit HARI INI - skip.')
            return 1
        print('   TAHAP 1: NBA via Google News...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_NBA = [
            GN('NBA scores results', 'en', 'GN NBA Hasil'),
            GN('NBA standings', 'en', 'GN NBA Klasmen'),
            GN('WNBA scores results', 'en', 'GN WNBA Hasil'),
            GN('NBA news', 'en', 'GN NBA Berita'),
            GN('berita NBA', 'id', 'GN NBA Berita ID'),
        ]
        cand = collect_candidates(SUMBER_NBA, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if teks_mengandung(c['title'] + ' ' + c['summary'], ['nba', 'wnba'])]
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Rangkuman NBA',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   TAHAP 2: olahraga umum (fallback)...')
        today_urls = get_today_state()
        seen = set()
        SUMBER_OLGA_UMUM = [
            GN('berita olahraga terkini', 'id', 'GN Olahraga'),
            GN('hasil pertandingan hari ini', 'id', 'GN Hasil Hari Ini'),
            RSSF('https://www.cnnindonesia.com/olahraga/rss', 'CNN Olahraga'),
            RSSF('https://sports.yahoo.com/rss/', 'Yahoo Sports'),
        ]
        cand = collect_candidates(SUMBER_OLGA_UMUM, today_urls, seen, max_umur_jam=30, kategori='olahraga')
        cand = [c for c in cand if adalah_konten_olahraga(c['title'] + ' ' + c.get('summary', ''))]
        cand = [c for c in cand if not is_berita_politik_hukum(c['title'] + ' ' + c.get('summary', ''))]
        if cand:
            hasil = _tulis_dari_kandidat(cand[0], 'Olahraga Siang',
                                          breaking=False, kategori_target='olahraga')
            if hasil == 1:
                return 1
        print('   Tidak ada berita olahraga - skip.')
        return 0
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
            print('   Topik wajib nasional belum terpenuhi: ' + ' & '.join(nama) + ' - kandidatnya didahulukan.')
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
    sumber_ekonomi = None
    jenis_ekonomi = None
    if kuota.get('ekonomi'):
        if jam in EKONOMI_JAM_DOMESTIK:
            sumber_ekonomi = EKONOMI_DOMESTIK_FEEDS
            jenis_ekonomi = 'domestik'
        elif jam in EKONOMI_JAM_ASING:
            sumber_ekonomi = EKONOMI_ASING_FEEDS
            jenis_ekonomi = 'asing'
        else:
            sumber_ekonomi = EKONOMI_DOMESTIK_FEEDS
            jenis_ekonomi = 'domestik'
        print('   EKONOMI jam ' + str(jam) + ' - feed ' + jenis_ekonomi)
    total = 0
    for cat, n in kuota.items():
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
        elif cat == 'ekonomi':
            sumber = sumber_ekonomi
            sumber_fallback = 'Ekonomi ' + (jenis_ekonomi or 'domestik').title()
        elif cat == 'olahraga':
            wajib_regional = True
            if olahraga_sudah_terbit_dengan_data('Event Besar Dunia') and jam in (11, 17):
                print('   Event Besar Dunia sudah terbit - slot dilewati.')
                continue
            if 7 <= jam < 12:
                hasil_api = sesi_olahraga_api('eropa')
                if hasil_api == 1:
                    total += 1
                    continue
                print('   sesi_olahraga_api(eropa) return 0 - fallback produksi_satu...')
                if produksi_satu(cat, today_urls, seen, False, prio, sumber,
                                 domain_tek, wajib_regional, sumber_fallback):
                    total += 1
                continue
            if 13 <= jam < 17:
                hasil_api = sesi_olahraga_api('nba')
                if hasil_api == 1:
                    total += 1
                    continue
                print('   sesi_olahraga_api(nba) return 0 - fallback produksi_satu...')
                if produksi_satu(cat, today_urls, seen, False, prio, sumber,
                                 domain_tek, wajib_regional, sumber_fallback):
                    total += 1
                continue
            if jam in (11, 17):
                aktif = event_besara_aktif()
                if aktif:
                    print('   EVENT BESAR AKTIF: ' + ' & '.join(e['nama'] for e in aktif) + ' - diprioritaskan.')
                    if _tulis_event_besar_dari_cand(today_urls, seen, aktif) == 1:
                        total += 1
                        continue
                for _ in range(n):
                    if produksi_satu(cat, today_urls, seen,
                                     utamakan_kaltara and cat == 'daerah',
                                     prio, sumber, domain_tek, wajib_regional,
                                     sumber_fallback):
                        total += 1
                continue
        if produksi_satu(cat, today_urls, seen,
                         utamakan_kaltara and cat == 'daerah',
                         prio, sumber, domain_tek, wajib_regional,
                         sumber_fallback):
            total += 1
    return total

def sesi_breaking_saja():
    now = datetime.now(WITA)
    print('\n==========================================')
    print('SESI BREAKING - ' + now.strftime('%d/%m/%Y %H:%M') + ' WITA')
    print('==========================================')
    dicabut = expire_breaking(BREAKING_UMUR_MENIT)
    if dicabut:
        print('   (' + str(dicabut) + ' breaking tua dicabut otomatis)')
    today_urls = get_today_state()
    global REJECTED_URLS_CACHE
    REJECTED_URLS_CACHE = None
    muat_rejected_urls()
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   ' + str(len(JUDUL_TERPAKAI)) + ' judul 36 jam terakhir dimuat (anti-dobel).')
    print('   ' + str(len(JUDUL_6JAM)) + ' judul 6 jam terakhir dimuat (anti-dobel-6jam).')
    print('   ' + str(len(muat_gambar_terpakai())) + ' gambar 36 jam terakhir terdaftar.')
    seen = set()
    n_brk = sesi_breaking(today_urls, seen)
    total_scrape = STAT_SCRAPE['ok'] + STAT_SCRAPE['gagal']
    if total_scrape:
        persen = int(STAT_SCRAPE['ok'] * 100 / total_scrape)
        print('\nStatistik scraping: ' + str(STAT_SCRAPE['ok']) + ' sukses / '
              + str(total_scrape) + ' artikel (' + str(persen) + '%) - gagal '
              + str(STAT_SCRAPE['gagal']) + ' - skip ' + str(STAT_SCRAPE['skip']))
    else:
        print('\nStatistik scraping: tidak ada percobaan scraping sesi ini.')
    if STAT_SCRAPE.get('gn_gagal_decode'):
        print('   GN decode gagal: ' + str(STAT_SCRAPE['gn_gagal_decode']))
    if STAT_SCRAPE.get('gn_fallback_rss'):
        print('   GN fallback RSS: ' + str(STAT_SCRAPE['gn_fallback_rss']))
    print('Sesi breaking selesai - breaking: ' + str(n_brk))
    return n_brk

def sesi_kategori_saja():
    now = datetime.now(WITA)
    print('\n==========================================')
    print('SESI KATEGORI - ' + now.strftime('%d/%m/%Y %H:%M') + ' WITA')
    print('==========================================')
    dicabut = expire_breaking(BREAKING_UMUR_MENIT)
    if dicabut:
        print('   (' + str(dicabut) + ' breaking tua dicabut otomatis)')
    today_urls = get_today_state()
    global REJECTED_URLS_CACHE
    REJECTED_URLS_CACHE = None
    muat_rejected_urls()
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   ' + str(len(JUDUL_TERPAKAI)) + ' judul 36 jam terakhir dimuat (anti-dobel).')
    print('   ' + str(len(JUDUL_6JAM)) + ' judul 6 jam terakhir dimuat (anti-dobel-6jam).')
    print('   ' + str(len(muat_gambar_terpakai())) + ' gambar 36 jam terakhir terdaftar.')
    seen = set()
    n_kat = sesi_kategori(today_urls, seen)
    total_scrape = STAT_SCRAPE['ok'] + STAT_SCRAPE['gagal']
    if total_scrape:
        persen = int(STAT_SCRAPE['ok'] * 100 / total_scrape)
        print('\nStatistik scraping: ' + str(STAT_SCRAPE['ok']) + ' sukses / '
              + str(total_scrape) + ' artikel (' + str(persen) + '%) - gagal '
              + str(STAT_SCRAPE['gagal']) + ' - skip ' + str(STAT_SCRAPE['skip']))
    else:
        print('\nStatistik scraping: tidak ada percobaan scraping sesi ini.')
    if STAT_SCRAPE.get('gn_gagal_decode'):
        print('   GN decode gagal: ' + str(STAT_SCRAPE['gn_gagal_decode']))
    if STAT_SCRAPE.get('gn_fallback_rss'):
        print('   GN fallback RSS: ' + str(STAT_SCRAPE['gn_fallback_rss']))
    print('Sesi kategori selesai - kategori: ' + str(n_kat))
    return n_kat

def run_session():
    now = datetime.now(WITA)
    print('\n==========================================')
    print('SESI BERBURU - ' + now.strftime('%d/%m/%Y %H:%M') + ' WITA')
    print('==========================================')
    dicabut = expire_breaking(BREAKING_UMUR_MENIT)
    if dicabut:
        print('   (' + str(dicabut) + ' breaking tua dicabut otomatis)')
    today_urls = get_today_state()
    global REJECTED_URLS_CACHE
    REJECTED_URLS_CACHE = None
    muat_rejected_urls()
    JUDUL_TERPAKAI.clear()
    JUDUL_TERPAKAI.extend(muat_judul_hari_ini())
    print('   ' + str(len(JUDUL_TERPAKAI)) + ' judul 36 jam terakhir dimuat (anti-dobel).')
    print('   ' + str(len(JUDUL_6JAM)) + ' judul 6 jam terakhir dimuat (anti-dobel-6jam).')
    print('   ' + str(len(muat_gambar_terpakai())) + ' gambar 36 jam terakhir terdaftar.')
    seen = set()
    n_brk = sesi_breaking(today_urls, seen)
    n_kat = sesi_kategori(today_urls, seen)
    total_scrape = STAT_SCRAPE['ok'] + STAT_SCRAPE['gagal']
    if total_scrape:
        persen = int(STAT_SCRAPE['ok'] * 100 / total_scrape)
        print('\nStatistik scraping: ' + str(STAT_SCRAPE['ok']) + ' sukses / '
              + str(total_scrape) + ' artikel (' + str(persen) + '%) - gagal '
              + str(STAT_SCRAPE['gagal']) + ' - skip ' + str(STAT_SCRAPE['skip']))
    else:
        print('\nStatistik scraping: tidak ada percobaan scraping sesi ini.')
    if STAT_SCRAPE.get('gn_gagal_decode'):
        print('   GN decode gagal: ' + str(STAT_SCRAPE['gn_gagal_decode']))
    if STAT_SCRAPE.get('gn_fallback_rss'):
        print('   GN fallback RSS: ' + str(STAT_SCRAPE['gn_fallback_rss']))
    print('Sesi selesai - breaking: ' + str(n_brk) + ' - kategori: ' + str(n_kat))
    return n_brk + n_kat

def main_sekali():
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('Kunci belum lengkap! Cek Secrets GitHub: DEEPSEEK_KEY, SUPABASE_PUBLISHABLE')
        return
    if not ADMIN_SECRET:
        print('ADMIN_OPS_SECRET belum ada di Secrets GitHub!')
        return
    print('Kunci gerbang admin-ops: OK')
    if '--breaking' in sys.argv:
        sesi_breaking_saja()
    elif '--kategori' in sys.argv:
        sesi_kategori_saja()
    else:
        run_session()

def main():
    print('AI WARTAWAN KRAMANEWS - mode loop 30 menit (Ctrl+C untuk berhenti)')
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

FILE_VERSI = 'V6.17.98'
FILE_PART_AKHIR = 'PART 4B'

# AKHIR PART 4B