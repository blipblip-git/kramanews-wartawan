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
        GN('dpr indonesia', '