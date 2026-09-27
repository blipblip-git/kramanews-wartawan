# KRAMANEWS — SKRIP SOSMED V1.10 (FB + INSTAGRAM)
# V1.10: 5x/hari tiap 3 jam — 2 Tarakan + 1 Kaltara lain + 1 Nasional + 1 Internasional
# V1.10: supabase_update pakai SUPABASE_SERVICE (admin-ops sudah JWT-only)
# V1.10: IG ikut aturan sama (5 slot), fallback kalau kosong

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

def pilih_5_berita(rows):
    terpilih = []
    id_terpilih = set()

    tarakan = [n for n in rows if is_tarakan(n)]
    for n in tarakan[:2]:
        terpilih.append(n)
        id_terpilih.add(n['id'])

    kaltara_lain = [n for n in rows if is_kaltara_lain(n) and n['id'] not in id_terpilih]
    if kaltara_lain:
        terpilih.append(kaltara_lain[0])
        id_terpilih.add(kaltara_lain[0]['id'])

    nasional = [n for n in rows if n.get('category') == 'nasional' and n['id'] not in id_terpilih]
    if nasional:
        terpilih.append(nasional[0])
        id_terpilih.add(nasional[0]['id'])

    internasional = [n for n in rows if n.get('category') == 'internasional' and n['id'] not in id_terpilih]
    if internasional:
        terpilih.append(internasional[0])
        id_terpilih.add(internasional[0]['id'])

    if len(terpilih) < 5:
        for n in rows:
            if len(terpilih) >= 5:
                break
            if n['id'] not in id_terpilih:
                terpilih.append(n)
                id_terpilih.add(n['id'])

    return terpilih[:5]

def mode_fb():
    print('📘 MODE FB — 5 slot: 2 Tarakan + 1 Kaltara lain + 1 Nas + 1 Int...')

    rows = supabase_get_safe(
        'articles?select=id,title,excerpt,content,category,img,dateline,posted_fb,breaking'
        '&status=eq.published&posted_fb=eq.false'
        '&order=created_at.desc&limit=80')

    if not rows:
        print('✅ Tidak ada berita baru. Selesai.')
        return

    terpilih = pilih_5_berita(rows)

    if not terpilih:
        print('✅ Tidak ada kandidat. Selesai.')
        return

    print('📋 Terpilih ' + str(len(terpilih)) + ' berita:')
    for n in terpilih:
        if is_tarakan(n):
            label = 'TARAKAN'
        elif is_kaltara_lain(n):
            label = 'KALTARA'
        else:
            label = (n.get('category') or '?').upper()
        print('   • [' + label + '] ' + (n.get('title') or '')[:60])

    ok = 0
    for n in terpilih:
        if is_tarakan(n):
            print('🏝️ TARAKAN: ' + (n.get('title') or '')[:60])
        elif is_kaltara_lain(n):
            print('🏝️ KALTARA: ' + (n.get('title') or '')[:60])
        else:
            print('📤 [' + (n.get('category') or '?') + ']: ' + (n.get('title') or '')[:60])
        try:
            post_fb(n)
            supabase_update(n['id'], {'posted_fb': True})
            ok += 1
            print('   ✅ Terkirim ke Facebook Page!')
        except Exception as e:
            print('   ⚠️ Gagal: ' + str(e)[:150])
        time.sleep(3)

    print('🏁 Mode FB selesai — ' + str(ok) + ' post terkirim.')

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
    print('📸 MODE IG — 5 slot: 2 Tarakan + 1 Kaltara lain + 1 Nas + 1 Int...')
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

    terpilih = pilih_5_berita(rows_berimg)

    if not terpilih:
        print('✅ Tidak ada kandidat IG. Selesai.')
        return

    print('📋 Terpilih ' + str(len(terpilih)) + ' berita IG:')
    for n in terpilih:
        if is_tarakan(n):
            label = 'TARAKAN'
        elif is_kaltara_lain(n):
            label = 'KALTARA'
        else:
            label = (n.get('category') or '?').upper()
        print('   • [' + label + '] ' + (n.get('title') or '')[:60])

    ok = 0
    for n in terpilih:
        label = '🏝️ TARAKAN' if is_tarakan(n) else ('🏝️ KALTARA' if is_kaltara_lain(n) else '📸 POSTING')
        print(label + ': ' + (n.get('title') or '')[:60])
        try:
            ig_post_photo(n['img'].strip(), buat_pesan_ig(n))
            supabase_update(n['id'], {'posted_ig': True})
            ok += 1
            print('   ✅ Terkirim ke Instagram @krama.news!')
        except Exception as e:
            pesan = str(e)
            print('   ⚠️ Gagal: ' + pesan[:150])
            if '190' in pesan or 'access_token' in pesan.lower() or 'token' in pesan.lower():
                print('   ⚠️ Indikasi token IG kedaluwarsa — ulangi generate token:')
                print('      developers.facebook.com → KramaNews Auto Post →')
                print('      Penyiapan API dgn login Instagram → Tambahkan akun → Buat token')
                print('      → update Secret IG_PAGE_TOKEN (copy-paste!)')
        time.sleep(3)

    print('🏁 Mode IG selesai — ' + str(ok) + ' post terkirim.')

def main():
    print('📣 KRAMANEWS SOSMED V1.10 — FB + INSTAGRAM (5x/hari)')
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