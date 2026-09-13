# ══════════════════════════════════════════════════════
#  AI WARTAWAN KRAMANEWS — V4.6 (KUOTA HEMAT + BREAKING DIPERLUAS)
#  Mode 1 (shift 24 jam)  : python3 skrip-wartawan.py
#  Mode 2 (sekali jalan)  : python3 skrip-wartawan.py --sekali
#  Jadwal shift (WIB): 06, 10, 14, 16, 19
#  Kuota: ±8-9 berita/sesi × 5 sesi = ±40-45 berita/hari
#  Kunci: dibaca dari GitHub Secrets (bukan ditulis di file)
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

# ═════════ KONFIGURASI — kunci dari environment (GitHub Secrets) ═════════
DEEPSEEK_KEY         = os.environ.get('DEEPSEEK_KEY', '')
SUPABASE_PUBLISHABLE = os.environ.get('SUPABASE_PUBLISHABLE', '')
# ══════════════════════════════════════════════════════════════════════════

SUPABASE_URL = 'https://imcvijgytdjjpotlaltv.supabase.co'
REST_URL     = SUPABASE_URL + '/rest/v1/articles'
EDGE_URL     = SUPABASE_URL + '/functions/v1/admin-ops'
AUTHOR_NAME  = 'DT'
STATE_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kramanews-sesi.json')

WIB = timezone(timedelta(hours=7))

SCHEDULE_JAM = [6, 10, 14, 16, 19]

# ═══ KUOTA HEMAT: ±8-9 berita/sesi × 5 sesi = ±40-45 berita/hari ═══
TARGET_PER_SESI = {
    'nasional':      1,
    'daerah':        2,   # termasuk wajib Kaltara/Tarakan
    'internasional': 1,
    'ekonomi':       1,
    'olahraga':      1,
    'teknologi':     1,
    'hiburan':       1,
    'kesehatan':     1,
}

# ═══ SIAGA: kata kunci urgen DIPERLUAS (bencana + transportasi + kriminal + negara) ═══
URGENT_KEYWORDS = [
    # bencana alam
    'gempa', 'tsunami', 'banjir', 'erupsi', 'gunung meletus', 'longsor',
    'kebakaran hebat', 'kebakaran', 'puting beliung', 'korban jiwa',
    'mengungsi', 'bencana alam',
    'earthquake', 'flood', 'volcano', 'eruption', 'wildfire',
    'hurricane', 'typhoon', 'landslide',
    # transportasi (kapal & pesawat)
    'kapal tenggelam', 'feri tenggelam', 'kapal karam', 'perairan',
    'pesawat jatuh', 'pesawat hilang', 'kecelakaan pesawat',
    'ferry sinks', 'boat sinking', 'plane crash', 'air disaster',
    'flight missing', 'airplane missing',
    # kriminal besar
    'ditangkap', 'ott', 'korupsi', 'tersangka', 'suap',
    'pembunuhan', 'terbunuh', 'asasinate', 'dibunuh', 'pejabat dibunuh',
    'perampokan besar', 'rampok bank', 'perampokan bersenjata',
    'assassination', 'murder', 'bank robbery', 'armed robbery',
    'killed', 'explosion', 'attack', 'war', 'missile', 'airstrike',
    'evacuated',
    # peristiwa negara / proyek besar
    'presiden meresmikan', 'wapres meresmikan', 'presiden melakukan',
    'jokowi meresmikan', 'prabowo meresmikan', 'proyek strategis nasional',
    'inaugurasi proyek', 'peresmian proyek', 'groundbreaking',
    'president inaugurates', 'president opens',
]

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
    GN('president inaugurates', 'en', 'Google News Peresmian Presiden'),
]

LUAR_NEGERI_WORDS = ['jepang', 'china', 'amerika', 'eropa', 'luar negeri', 'inggris',
                     'india', 'korea', 'australia', 'turki', 'israel', 'gaza',
                     'ukraina', 'rusia', 'malaysia', 'thailand', 'taiwan', 'timor leste']

SYSTEM_PROMPT = """Kamu adalah AI Wartawan profesional portal berita KramaNews Indonesia.

TUGAS: Tulis ulang materi sumber menjadi berita orisinal KramaNews.

ATURAN GAYA PENULISAN (WAJIB):
- Tulis seperti wartawan portal besar Indonesia. LAPOR BERITA LANGSUNG.
- DILARANG KERAS menyebut nama portal, media, situs, atau sumber berita mana pun
  di dalam isi berita (misalnya: "Berdasarkan laporan...", "Dilansir dari...",
  "Dikutip dari...", "menurut siaran pers...", "dikutip CNN/detik/Reuters/Kompas...").
- JANGAN menjelaskan dari mana informasi didapat. Pembaca tidak perlu tahu.
- Cukup ceritakan langsung: kronologi, fakta, angka, dampak — seolah kamu wartawan
  yang meliput langsung di lokasi.

ATURAN DATELINE (WAJIB - SANGAT PENTING):
- Baris pertama isi berita HARUS diawali DATELINE lokasi kejadian, format:
  "KOTA, PROVINSI/NEGARA - " lalu langsung lanjut kalimat berita.
- Untuk berita Indonesia: "KOTA, PROVINSI - " (contoh: "TARAKAN, KALTARA - ...").
- Untuk berita luar negeri: "KOTA, NEGARA - " (contoh: "SHENZHEN, CHINA - ...").
- Dateline ditulis HURUF KAPITAL, diakhiri tanda hubung "-" lalu langsung isi berita.
- Jika lokasi tidak disebutkan sama sekali, gunakan "INDONESIA - " atau nama negara.

ATURAN PANJANG & ISI (WAJIB):
- Panjang total: 350-500 kata (5-7 paragraf). KEBUTUHAN MINIMAL.
- Paragraf 1: inti berita — siapa, apa, kapan, di mana.
- Paragraf 2-4: detail penting, data/angka, kronologi, dan dampaknya.
- Paragraf 5-6: konteks yang relevan SELAMA tidak mengarang fakta spesifik.
- Paragraf terakhir: langkah selanjutnya atau penutup netral.
- Kalimat pendek, jelas, mudah dipahami pembaca awam.

ATURAN JUDUL (WAJIB):
- Buat judul ORISINAL yang MENARIK — JANGAN menyalin judul sumber.
- Maksimal 10 kata. Jujur, TIDAK clickbait palsu.

ATURAN ETIKA FAKTA (WAJIB):
- HANYA gunakan fakta dari materi sumber. DILARANG mengarang fakta baru.
- Larangan menyebut sumber TIDAK memberi izin mengarang — tetap setia pada fakta.

FORMAT JAWABAN:
Jawab HANYA dengan JSON valid tanpa teks lain:
{"judul": "...", "isi": "DATELINE - paragraf1\\n\\nparagraf2\\n\\nparagraf3", "ringkasan": "..."}"""

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
    rows = rest_get('?select=source_url,category,written_by,created_at&order=created_at.desc&limit=300')
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

def breaking_slots():
    try:
        rows = rest_get('?select=id&breaking=eq.true&status=eq.published')
        return max(0, 3 - len(rows))
    except Exception:
        return 0

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
    return obj['judul'].strip(), obj['isi'].strip(), obj['ringkasan'].strip()

def ai_rewrite_single(c):
    user = ('MATERI SUMBER:\n'
            'Judul asli: ' + c['title'] + '\n'
            'Ringkasan: ' + c['summary'] + '\n\n'
            'Buat judul ORISINAL maksimal 10 kata, tulis ulang berita sesuai semua aturan. '
            'INGAT: jangan sebut portal/media sumber apa pun, dan awali isi berita '
            'dengan dateline lokasi kejadian (format: "KOTA, PROVINSI/NEGARA - ...").')
    return ai_write(user)

def ai_rewrite_multi(items):
    parts = []
    for i, it in enumerate(items[:4], 1):
        parts.append('[MATERI ' + str(i) + ']\n'
                     'Judul: ' + it['title'] + '\nIsi: ' + it['summary'][:1500])
    user = ('Berikut beberapa materi tentang topik yang SAMA:\n\n'
            + '\n\n'.join(parts) +
            '\n\nGabungkan semua fakta menjadi SATU berita KramaNews lengkap (350-500 kata). '
            'INGAT: jangan sebut portal/media sumber apa pun, dan awali isi berita '
            'dengan dateline lokasi kejadian (format: "KOTA, PROVINSI/NEGARA - ...").')
    return ai_write(user, timeout=180)

def is_urgent(title, summary):
    t = (title + ' ' + summary).lower()
    return any(k in t for k in URGENT_KEYWORDS)

def insert_news(judul, isi, ringkasan, cat, img, link, source_name, status, breaking=False):
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

# ═════════ SESI BERBURU ═════════

def sesi_siaga(today_urls, seen):
    made = 0
    slots = breaking_slots()
    print('\n🚨 SIAGA — memantau bencana/transportasi/kriminal/proyek negara (slot breaking: ' + str(slots) + ')...')
    cands = collect_candidates(URGENT_FEEDS, today_urls, seen)
    for c in cands:
        if made >= 3:
            break
        if not is_urgent(c['title'], c['summary']):
            continue
        try:
            judul, isi, ringkasan = ai_rewrite_single(c)
        except Exception as e:
            print('   ⚠️ AI gagal 1 siaga:', str(e)[:60])
            continue
        blob = (judul + ' ' + isi).lower()
        cat = 'internasional' if any(w in blob for w in LUAR_NEGERI_WORDS) else 'nasional'
        try:
            if slots > 0:
                insert_news(judul, isi, ringkasan, cat, get_image(c['entry']), c['link'],
                            c['source'], status='published', breaking=True)
                slots -= 1
                print('   🚨 BREAKING TAYANG: ' + judul)
            else:
                insert_news(judul, isi, ringkasan, cat, get_image(c['entry']), c['link'],
                            c['source'], status='draft')
                print('   ⭐ Breaking penuh → draft: ' + judul)
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
                judul, isi, ringkasan = ai_rewrite_single(c)
                insert_news(judul, isi, ringkasan, cat, get_image(c['entry']),
                            c['link'], c['source'], status='draft')
                made += 1
                kaltara_made += 1
                today_urls.add(c['link'])
                print('   🏝️ KALTARA [' + str(kaltara_made) + '/' + str(kaltara_min) + ']: ' + judul)
            except Exception as e:
                print('   ⚠️ Gagal 1 kaltara:', str(e)[:60])
            time.sleep(2)
        print('   → Kaltara terpenuhi: ' + str(kaltara_made) + '/' + str(kaltara_min))

    for g in groups:
        if made >= need:
            break
        items = g['items']
        top = items[0]
        try:
            if len(items) > 1:
                judul, isi, ringkasan = ai_rewrite_multi(items)
                print('       🔗 topik dari ' + str(len(items)) + ' portal')
            else:
                judul, isi, ringkasan = ai_rewrite_single(top)
            insert_news(judul, isi, ringkasan, cat, get_image(top['entry']),
                        top['link'], top['source'], status='draft')
            made += 1
            for it in items:
                today_urls.add(it['link'])
            print('   ✅ [' + str(made) + '/' + str(need) + '] ' + judul)
        except Exception as e:
            print('   ⚠️ Gagal proses 1 kelompok:', str(e)[:80])
            continue
        time.sleep(2)

    print('   → Hasil: ' + str(made) + ' draft')
    return made

def run_session():
    today_urls = get_today_state()
    seen = set()
    total = 0
    total += sesi_siaga(today_urls, seen)
    for cat, need in TARGET_PER_SESI.items():
        try:
            if cat == 'daerah':
                total += sesi_kategori(cat, need, today_urls, seen, kaltara_min=2)
            else:
                total += sesi_kategori(cat, need, today_urls, seen)
        except Exception as e:
            print('   ❌ Kategori ' + cat + ' error: ' + str(e)[:80])
    return total

# ═════════ STATE SESI ═════════

def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(st):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(st, f)
    except Exception:
        pass

# ═════════ PROGRAM UTAMA ═════════

def main_sekali():
    print('🐝 AI WARTAWAN — MODE SEKALI JALAN (' + datetime.now(WIB).strftime('%H:%M WIB') + ')')
    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ Kunci belum diisi!')
        return
    try:
        total = run_session()
        print(' 🏁 Selesai — total ' + str(total) + ' berita dibuat.')
    except Exception as e:
        print(' ❌ Gagal: ' + str(e)[:100])

def main():
    print('=' * 56)
    print(' 🐝 AI WARTAWAN KRAMANEWS V4.6 — MODE SHIFT OTOMATIS')
    print(' ⏰ Jadwal berburu (WIB): ' + ', '.join(str(h).zfill(2) + ':00' for h in SCHEDULE_JAM))
    print(' ✍️  Penulis: ' + AUTHOR_NAME + ' | Kuota: ±40-45 berita/hari')
    print(' 💡 Biarkan terminal ini terbuka. Stop: Ctrl+C')
    print('=' * 56)

    if not DEEPSEEK_KEY or not SUPABASE_PUBLISHABLE:
        print('❌ DEEPSEEK_KEY / SUPABASE_PUBLISHABLE belum diisi!')
        return

    while True:
        try:
            now = datetime.now(WIB)
            today = now.strftime('%Y-%m-%d')
            st = load_state()
            if st.get('date') != today:
                st = {'date': today, 'done': []}

            pending = [h for h in SCHEDULE_JAM if now.hour >= h and h not in st['done']]
            if pending:
                h = pending[-1]
                print('\n' + '=' * 56)
                print(' ⏰ SESI ' + str(h).zfill(2) + ':00 WIB — mulai berburu...')
                print('=' * 56)
                st['done'] = sorted(set(st['done'] + pending))
                save_state(st)
                try:
                    total = run_session()
                    print('\n 🏁 Sesi selesai — total ' + str(total) + ' berita dibuat.')
                except Exception as e:
                    print(' ❌ Sesi gagal: ' + str(e)[:100])
            time.sleep(60)
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