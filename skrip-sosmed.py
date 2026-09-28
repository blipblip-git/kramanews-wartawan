# KRAMANEWS — SKRIP SOSMED V1.11 (FB + INSTAGRAM)
# V1.11: 5 siklus x 1 berita/hari (06:07, 09:07, 12:07, 15:07, 18:07 WITA)
# V1.11: rotasi slot per jam: Tarakan -> Kaltara -> Nasional -> Internasional -> Bebas
# V1.11: fallback 1 kategori lain kalau slot utama kosong (hindari Internasional ke-2)

import requests
import os
import time
import sys
import json
import re
from datetime import datetime, timezone, timedelta

FB_PAGE_TOKEN   = os.environ.get('FB_PAGE_TOKEN', '')
FB_PAGE_ID      = os.environ.get('FB_PAGE_ID', '')
IG_TOKEN        = os.environ.get('IG_PAGE_TOKEN', '')
SUPABASE_URL    = 'https://imcvijgtydjjpotlaltv.supabase.co'
SUPABASE_ANON   = os.environ.get('SUPABASE_PUBLISHABLE', '')
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '')
SITE_URL        = 'https://kramanews.my.id'

WITA = timezone(timedelta(hours=8))

KATEGORI_LABEL = {
    'nasional': 'Nasional', 'daerah': 'Daerah',
    'internasional': 'Internasional', 'ekonomi': 'Ekonomi',
    'olahraga': 'Olahraga', 'teknologi': 'Teknologi',
    'otomotif': 'Otomotif', 'kesehatan': 'Kesehatan',
}

HASHTAG_KATEGORI = {
    'nasional': '#Indonesia #BeritaNasional',
    'daerah': '#Tarakan #Kaltara',
    'internasional': '#BeritaDunia #Internasional',
    'ekonomi': '#Ekonomi',
    'olahraga': '#Olahraga',
    'teknologi': '#Teknologi',
    'otomotif': '#Otomotif',
    'kesehatan': '#Kesehatan',
}

KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata', 'tanjung selor']

def is_tarakan(n):
    teks = ' '.join(str(n.get(k) or '') for k in ('title', 'dateline', 'excerpt', 'content')).lower()
    return 'tarakan' in teks

def is_kaltara_lain(n):
    if is_tarakan(n):
        return False
    teks = ' '.join(str(n.get(k) or '') for k in ('title', 'dateline', 'excerpt', 'content')).lower()
    return any(w in teks for w in KALTARA_WORDS)

def is_kaltara(n):
    return is_tarakan(n) or is_kaltara_lain(n)

BOLD_MAP = {}
for _i, _ch in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    BOLD_MAP[_ch] = chr(0x1D5D4 + _i)
for _i, _ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
    BOLD_MAP[_ch] = chr(0x1D5EE + _i)
for _i, _ch in enumerate('0123456789'):
    BOLD_MAP[_ch] = chr(0x1D7EC + _i)

def to_bold(text):
    return ''.join(BOLD_MAP.get(c, c) for c in text)

def retry(func, nama, max_coba=3):
    for percobaan in range(1, max_coba + 1):
        try:
            return func()
        except Exception as e:
            pesan_err = str(e)
            layak_retry = any(k in pesan_err for k in ('504', '502', '503', 'Gateway', 'timeout', 'Timeout'))
            if percobaan >= max_coba or not layak_retry:
                raise
            print(f'   ⏳ {nama} gagal ({pesan_err[:60]}), coba ulang {percobaan}/{max_coba-1} dalam 10 detik...')
            time.sleep(10)

def supabase_get_safe(query):
    def do_get():
        return requests.get(SUPABASE_URL + '/rest/v1/' + query,
            headers={'apikey': SUPABASE_ANON,
                     'Authorization': 'Bearer ' + SUPABASE_ANON},
            timeout=30)
    r = retry(do_get, 'Supabase GET')
    if not r.ok:
        raise Exception('Supabase GET ' + str(r.status_code) + ': ' + r.text[:150])
    return r.json() or []

def supabase_update(article_id, payload):
    if not SUPABASE_SERVICE:
        raise Exception('SUPABASE_SERVICE belum ada di Secrets')
    def do_update():
        return requests.patch(
            SUPABASE_URL + '/rest/v1/articles?id=eq.' + str(article_id),
            headers={'apikey': SUPABASE_SERVICE,
                     'Authorization': 'Bearer ' + SUPABASE_SERVICE,
                     'Content-Type': 'application/json',
                     'Prefer': 'return=minimal'},
            json=payload,
            timeout=30)
    r = retry(do_update, 'Supabase UPDATE')
    if not r.ok:
        raise Exception('Update ' + str(r.status_code) + ': ' + r.text[:150])
    return True

def ambil_teaser(content, kalimat=3):
    bersih = re.sub(r'\s+', ' ', content or '').strip()
    kalimat_list = re.split(r'(?<=[.!?])\s+', bersih)
    return ' '.join(kalimat_list[:kalimat]).strip()

def fb_post_photo(message, image_url):
    r = requests.post(
        'https://graph.facebook.com/v21.0/' + FB_PAGE_ID + '/photos',
        data={'url': image_url, 'caption': message, 'access_token': FB_PAGE_TOKEN},
        timeout=60)
    if not r.ok:
        raise Exception('FB photo ' + str(r.status_code) + ': ' + r.text[:200])
    return r.json()

def fb_post_feed(message, link):
    r = requests.post(
        'https://graph.facebook.com/v21.0/' + FB_PAGE_ID + '/feed',
        data={'message': message, 'link': link, 'access_token': FB_PAGE_TOKEN},
        timeout=30)
    if not r.ok:
        raise Exception('FB feed ' + str(r.status_code) + ': ' + r.text[:200])
    return r.json()

def buat_pesan_fb(n):
    cat = KATEGORI_LABEL.get(n.get('category', ''), n.get('category', ''))
    judul = (n.get('title') or '').strip()
    dateline = (n.get('dateline') or '').strip()
    content = (n.get('content') or '').strip()
    teaser = ambil_teaser(content, kalimat=3)
    link_artikel = SITE_URL + '/?baca=' + str(n.get('id'))

    lines = []
    if n.get('breaking'):
        lines.append('🚨 ' + to_bold(judul))
    else:
        lines.append(to_bold(judul))
    if dateline:
        lines.append('📍 ' + dateline)
    if teaser:
        lines.append('')
        lines.append(teaser)
    lines.append('')
    lines.append('🔗 Baca selengkapnya: ' + link_artikel)
    lines.append('#' + cat.replace(' ', '') + ' #KramaNews #BeritaTerkini')

    return '\n'.join(lines)

def post_fb(n):
    pesan = buat_pesan_fb(n)
    img = (n.get('img') or '').strip()
    if img:
        return fb_post_photo(pesan, img)
    else:
        return fb_post_feed(pesan, SITE_URL + '/?baca=' + str(n.get('id')))

# ═══ V1.11: tentukan slot berdasarkan jam WITA ═══
def slot_saat_ini():
    """Rotasi slot per jam:
    06:07 WITA -> TARAKAN
    09:07 WITA -> KALTARA
    12:07 WITA -> NASIONAL
    15:07 WITA -> INTERNASIONAL
    18:07 WITA -> BEBAS (tarakan/kaltara/nas/int/ekonomi/olahraga/teknologi/otomotif/kesehatan)
    """
    jam = datetime.now(WITA).hour
    if 5 <= jam < 8:
        return 'tarakan'
    elif 8 <= jam < 11:
        return 'kaltara'
    elif 11 <= jam < 14:
        return 'nasional'
    elif 14 <= jam < 17:
        return 'internasional'
    else:
        return 'bebas'

def pilih_berita_untuk_slot(rows, slot):
    """Pilih SATU berita untuk slot ini. Fallback ke kategori lain kalau kosong."""
    id_terpakai = set()

    def ambil(pred):
        for n in rows:
            if n['id'] in id_terpakai:
                continue
            if pred(n):
                return n
        return None

    pilihan = None
    if slot == 'tarakan':
        pilihan = ambil(is_tarakan)
    elif slot == 'kaltara':
        pilihan = ambil(is_kaltara_lain)
    elif slot == 'nasional':
        pilihan = ambil(lambda n: n.get('category') == 'nasional')
    elif slot == 'internasional':
        pilihan = ambil(lambda n: n.get('category') == 'internasional')

    if pilihan:
        return pilihan

    # Fallback: cari kategori lain (bukan yang sudah jadi slot utama)
    prioritas_fallback = ['daerah', 'nasional', 'ekonomi', 'olahraga',
                          'teknologi', 'otomotif', 'kesehatan', 'internasional']
    if slot == 'tarakan':
        # Coba Kaltara lain dulu, lalu fallback umum
        pilihan = ambil(is_kaltara_lain)
        if pilihan:
            return pilihan
    if slot == 'kaltara':
        pilihan = ambil(is_tarakan)
        if pilihan:
            return pilihan

    for kat in prioritas_fallback:
        pilihan = ambil(lambda n, k=kat: n.get('category') == k)
        if pilihan:
            return pilihan

    # Terakhir: apa saja
    pilihan = ambil(lambda n: True)
    return pilihan

def mode_fb():
    slot = slot_saat_ini()
    print('📘 MODE FB V1.11 — slot: ' + slot.upper() + ' (1 berita)')

    rows = supabase_get_safe(
        'articles?select=id,title,excerpt,content,category,img,dateline,posted_fb,breaking'
        '&status=eq.published&posted_fb=eq.false'
        '&order=created_at.desc&limit=80')

    if not rows:
        print('✅ Tidak ada berita baru. Selesai.')
        return

    n = pilih_berita_untuk_slot(rows, slot)

    if not n:
        print('✅ Tidak ada kandidat. Selesai.')
        return

    if is_tarakan(n):
        label = 'TARAKAN'
    elif is_kaltara_lain(n):
        label = 'KALTARA'
    else:
        label = (n.get('category') or '?').upper()

    print('📋 Terpilih 1 berita:')
    print('   • [' + label + '] ' + (n.get('title') or '')[:70])

    try:
        post_fb(n)
        supabase_update(n['id'], {'posted_fb': True})
        print('   ✅ Terkirim ke Facebook Page!')
    except Exception as e:
        print('   ⚠️ Gagal: ' + str(e)[:150])

    print('🏁 Mode FB selesai.')

def ada_img(n):
    u = (n.get('img') or '').strip()
    return bool(u) and not u.lower().endswith('.svg')

def ig_post_photo(image_url, caption):
    r = requests.post(
        'https://graph.instagram.com/v21.0/me/media',
        data={'image_url': image_url, 'caption': caption, 'access_token': IG_TOKEN},
        timeout=60)
    if not r.ok:
        raise Exception('IG container ' + str(r.status_code) + ': ' + r.text[:200])
    creation_id = r.json().get('id')
    if not creation_id:
        raise Exception('IG container tanpa id: ' + r.text[:150])
    for coba in range(3):
        time.sleep(4)
        r2 = requests.post(
            'https://graph.instagram.com/v21.0/me/media_publish',
            data={'creation_id': creation_id, 'access_token': IG_TOKEN},
            timeout=60)
        if r2.ok:
            return r2.json()
        teks = r2.text or ''
        if 'MEDIA_NOT_READY' in teks or 'not ready' in teks.lower():
            continue
        raise Exception('IG publish ' + str(r2.status_code) + ': ' + teks[:200])
    raise Exception('IG media belum siap setelah 3 percobaan publish')

def buat_pesan_ig(n):
    judul = (n.get('title') or '').strip()
    teaser = ambil_teaser(n.get('content'), kalimat=2)
    cat = n.get('category', '')
    tag = HASHTAG_KATEGORI.get(cat, '')
    if is_kaltara(n) and '#Tarakan' not in tag:
        tag = '#Tarakan #Kaltara ' + tag

    lines = []
    baris_judul = to_bold(judul)
    if n.get('breaking'):
        baris_judul = '🚨 ' + baris_judul
    lines.append(baris_judul)
    if teaser:
        lines.append('')
        lines.append(teaser)
    lines.append('')
    lines.append('🔗 Baca selengkapnya di kramanews.my.id (link di bio)')
    lines.append('')
    lines.append(tag + ' #KramaNews #BeritaTerkini #BeritaHariIni')

    return '\n'.join(lines)[:2200]

def mode_ig():
    slot = slot_saat_ini()
    print('📸 MODE IG V1.11 — slot: ' + slot.upper() + ' (1 berita)')
    if not IG_TOKEN:
        print('⏭️ IG_PAGE_TOKEN belum ada di Secrets — IG dilewati.')
        return

    try:
        rows = supabase_get_safe(
            'articles?select=id,title,excerpt,content,category,img,dateline,posted_ig,breaking'
            '&status=eq.published&posted_ig=eq.false'
            '&order=created_at.desc&limit=80')
    except Exception as e:
        print('❌ Gagal ambil antrean IG: ' + str(e)[:120])
        return

    if not rows:
        print('✅ Tidak ada berita baru untuk IG. Selesai.')
        return

    rows_berimg = [n for n in rows if ada_img(n)]
    if not rows_berimg:
        print('✅ Tidak ada kandidat IG bergambar. Selesai.')
        return

    n = pilih_berita_untuk_slot(rows_berimg, slot)

    if not n:
        print('✅ Tidak ada kandidat IG. Selesai.')
        return

    if is_tarakan(n):
        label = 'TARAKAN'
    elif is_kaltara_lain(n):
        label = 'KALTARA'
    else:
        label = (n.get('category') or '?').upper()

    print('📋 Terpilih 1 berita IG:')
    print('   • [' + label + '] ' + (n.get('title') or '')[:70])

    try:
        ig_post_photo(n['img'].strip(), buat_pesan_ig(n))
        supabase_update(n['id'], {'posted_ig': True})
        print('   ✅ Terkirim ke Instagram @krama.news!')
    except Exception as e:
        pesan = str(e)
        print('   ⚠️ Gagal: ' + pesan[:150])
        if '190' in pesan or 'access_token' in pesan.lower() or 'token' in pesan.lower():
            print('   ⚠️ Indikasi token IG kedaluwarsa — ulangi generate token:')
            print('      developers.facebook.com → KramaNews Auto Post →')
            print('      Penyiapan API dgn login Instagram → Tambahkan akun → Buat token')
            print('      → update Secret IG_PAGE_TOKEN (copy-paste!)')

    print('🏁 Mode IG selesai.')

def main():
    print('📣 KRAMANEWS SOSMED V1.11 — FB + INSTAGRAM (5 siklus x 1 berita)')
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print('❌ Kunci FB belum lengkap (cek Secrets)!')
        return
    if not SUPABASE_ANON:
        print('❌ SUPABASE_PUBLISHABLE belum ada di Secrets!')
        return
    if not SUPABASE_SERVICE:
        print('❌ SUPABASE_SERVICE belum ada di Secrets!')
        return
    mode_fb()
    mode_ig()

if __name__ == '__main__':
    main()