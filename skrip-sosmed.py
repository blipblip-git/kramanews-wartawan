# ══════════════════════════════════════════════════════
#  KRAMANEWS — SKRIP SOSMED V1.9.1 (FB + INSTAGRAM)
#  Baru V1.9.1 (KRAMASOSMEDV191MARKER) — FIX HURUF O:
#   • BOLD_MAP yang diketik manual ternyata punya entri 'O'
#     yang SALAH (menunjuk glyph mirip P) → setiap post FB
#     dengan judul tebal selalu salah huruf O (laporan pemilik:
#     "Prabwp/Sekplah/Kpruptpr" — semua O jadi P).
#   • SOLUSI: BOLD_MAP dibuat PROGRAMATIK dari kode Unicode
#     (chr(0x1D5D4+i) dst) — mustahil salah ketik lagi.
#   Warisan V1.9: x-admin-secret, mode_web null-aman, FB/IG
#   logika V1.8.1 (IG kebal NULL, foto wajib IG, maks 2/run
#   6/hari, hashtag kategori+Kaltara, retry 504, ?baca=ID)
# ══════════════════════════════════════════════════════

import requests
import os
import time
import sys
import json
import re
from datetime import datetime, timezone, timedelta

FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN', '')
FB_PAGE_ID    = os.environ.get('FB_PAGE_ID', '')
IG_TOKEN      = os.environ.get('IG_PAGE_TOKEN', '')
ADMIN_SECRET  = os.environ.get('ADMIN_OPS_SECRET', '')
SUPABASE_URL  = 'https://imcvijgytdjjpotlaltv.supabase.co'
SUPABASE_ANON = os.environ.get('SUPABASE_PUBLISHABLE', '')
SITE_URL      = 'https://kramanews.my.id'

WITA = timezone(timedelta(hours=8))
IG_DAILY_MAX = 6   # maks post IG per hari (akun muda — jangan rakus)
IG_PER_RUN   = 2   # maks post IG per run

KATEGORI_LABEL = {
    'nasional': 'Nasional', 'daerah': 'Daerah',
    'internasional': 'Internasional', 'ekonomi': 'Ekonomi',
    'olahraga': 'Olahraga', 'teknologi': 'Teknologi',
    'hiburan': 'Hiburan', 'kesehatan': 'Kesehatan',
}

HASHTAG_KATEGORI = {
    'nasional': '#Indonesia #BeritaNasional',
    'daerah': '#Tarakan #Kaltara',
    'internasional': '#BeritaDunia #Internasional',
    'ekonomi': '#Ekonomi',
    'olahraga': '#Olahraga',
    'teknologi': '#Teknologi',
    'hiburan': '#Hiburan',
    'kesehatan': '#Kesehatan',
}

# ═══ KATA KUNCI PRIORITAS KALTARA (V1.7) ═══
KALTARA_WORDS = ['tarakan', 'kaltara', 'nunukan', 'bulungan', 'malinau',
                 'tana tidung', 'sesayap', 'juata']

def is_kaltara(n):
    teks = ' '.join(str(n.get(k) or '') for k in ('title', 'dateline', 'excerpt', 'content')).lower()
    return any(w in teks for w in KALTARA_WORDS)

# ═══ V1.9.1 — BOLD_MAP PROGRAMATIK (KRAMASOSMEDV191MARKER) ═══
# Dibuat dari kode Unicode matematika — NOL kemungkinan salah ketik
# glyph (fix huruf O yang dulu salah menunjuk karakter mirip P).
# Sans-Serif Bold: A=U+1D5D4..Z=U+1D5ED, a=U+1D5EE..z=U+1D607,
# 0=U+1D7EC..9=U+1D7F5.
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
    # [V1.9] kirim x-admin-secret — gerbang admin-ops V2
    def do_update():
        return requests.post(
            SUPABASE_URL + '/functions/v1/admin-ops',
            headers={'apikey': SUPABASE_ANON,
                     'Authorization': 'Bearer ' + SUPABASE_ANON,
                     'x-admin-secret': ADMIN_SECRET,
                     'Content-Type': 'application/json'},
            json={'action': 'update', 'id': article_id, 'payload': payload},
            timeout=30)
    r = retry(do_update, 'Supabase UPDATE')
    try:
        data = r.json()
    except Exception:
        raise Exception('Edge HTTP ' + str(r.status_code) + ': ' + r.text[:150])
    if not r.ok or data.get('error'):
        raise Exception(str(data.get('error') or ('HTTP ' + str(r.status_code))))
    return data.get('data')

def ambil_teaser(content, kalimat=3):
    bersih = re.sub(r'\s+', ' ', content or '').strip()
    kalimat_list = re.split(r'(?<=[.!?])\s+', bersih)
    return ' '.join(kalimat_list[:kalimat]).strip()

# ═══ FACEBOOK (V1.7 — TIDAK BERUBAH) ═══

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

def mode_fb():
    print('📘 MODE FB — antrean auto-post (PRIORITAS KALTARA)...')

    rows = supabase_get_safe(
        'articles?select=id,title,excerpt,content,category,img,dateline,posted_fb,breaking'
        '&status=eq.published&posted_fb=eq.false'
        '&order=created_at.desc&limit=15')

    if not rows:
        print('✅ Tidak ada berita baru yang perlu diposting. Selesai.')
        return

    prio = [n for n in rows if is_kaltara(n)]
    lain = [n for n in rows if not is_kaltara(n)]
    urutan = prio + lain

    if prio:
        print('🏝️ ' + str(len(prio)) + ' berita KALTARA/TARAKAN diprioritaskan di depan:')
        for n in prio[:3]:
            print('   • ' + (n.get('title') or '')[:60])

    antre = urutan[:3]

    ok = 0
    for n in antre:
        if n.get('breaking'):
            print('🚨 BREAKING: ' + (n.get('title') or '')[:60])
        elif is_kaltara(n):
            print('🏝️ KALTARA PRIORITAS: ' + (n.get('title') or '')[:60])
        else:
            print('📤 Posting: ' + (n.get('title') or '')[:60])
        try:
            post_fb(n)
            supabase_update(n['id'], {'posted_fb': True})
            ok += 1
            print('   ✅ Terkirim ke Facebook Page!')
        except Exception as e:
            print('   ⚠️ Gagal: ' + str(e)[:150])
        time.sleep(3)

    print('🏁 Mode FB selesai — ' + str(ok) + ' post terkirim.')

# ═══ INSTAGRAM (V1.8.1 — ANTREAN KEBAL NULL) ═══

def ada_img(n):
    u = (n.get('img') or '').strip()
    return bool(u) and not u.lower().endswith('.svg')

def belum_post_ig(n):
    """V1.8.1: NULL/kosong/false = belum diposting (kebal data lama)."""
    return not n.get('posted_ig')

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
    print('📸 MODE IG — antrean auto-post Instagram (@krama.news)...')
    if not IG_TOKEN:
        print('⏭️ IG_PAGE_TOKEN belum ada di Secrets — IG dilewati.')
        return

    try:
        sudah_rows = supabase_get_safe(
            'articles?select=created_at&posted_ig=eq.true&order=created_at.desc&limit=50')
    except Exception:
        sudah_rows = []
    today = datetime.now(WITA).date()
    hari_ini = 0
    for r in sudah_rows:
        try:
            d = datetime.fromisoformat(str(r['created_at']).replace('Z', '+00:00')).astimezone(WITA).date()
            if d == today:
                hari_ini += 1
        except Exception:
            pass
    sisa_kuota = IG_DAILY_MAX - hari_ini
    if sisa_kuota <= 0:
        print('✅ Kuota harian IG tercapai (' + str(hari_ini) + '/' + str(IG_DAILY_MAX)
              + ') — akun muda harus sopan. Selesai.')
        return

    try:
        rows = supabase_get_safe(
            'articles?select=id,title,excerpt,content,category,img,dateline,posted_ig,breaking'
            '&status=eq.published'
            '&order=created_at.desc&limit=15')
    except Exception as e:
        print('❌ Gagal ambil antrean IG: ' + str(e)[:120])
        return

    if not rows:
        print('✅ Tidak ada berita sama sekali. Selesai.')
        return

    kandidat = [n for n in rows if belum_post_ig(n)]
    if not kandidat:
        print('✅ Semua 15 berita terbaru sudah diposting ke IG. Selesai.')
        return

    prio = [n for n in kandidat if is_kaltara(n) and ada_img(n)]
    lain = [n for n in kandidat if (not is_kaltara(n)) and ada_img(n)]
    tanpa_img = [n for n in kandidat if not ada_img(n)]
    urutan = prio + lain

    if prio:
        print('🏝️ ' + str(len(prio)) + ' berita KALTARA/TARAKAN diprioritaskan di IG:')
        for n in prio[:2]:
            print('   • ' + (n.get('title') or '')[:60])
    if tanpa_img:
        print('ℹ️ ' + str(len(tanpa_img)) + ' berita tanpa gambar dilewati IG (IG wajib foto — FB tetap posting).')

    antre = urutan[:min(IG_PER_RUN, sisa_kuota)]
    if not antre:
        print('✅ Tidak ada kandidat IG bergambar. Selesai.')
        return

    ok = 0
    for n in antre:
        label = '🚨 BREAKING' if n.get('breaking') else ('🏝️ KALTARA' if is_kaltara(n) else '📸 POSTING')
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

    print('🏁 Mode IG selesai — ' + str(ok) + ' post terkirim (hari ini: '
          + str(hari_ini + ok) + '/' + str(IG_DAILY_MAX) + ').')

def mode_web():
    # [V1.9] NULL-aman — ambil 5 terbaru per kategori TANPA filter
    # featured, saring di Python: NULL/false = kandidat.
    print('🌐 MODE WEB — tandai berita unggulan per kategori...')
    total = 0
    cats = list(KATEGORI_LABEL.keys())
    for cat in cats:
        try:
            rows = supabase_get_safe(
                'articles?select=id,title,category,updated_at,featured'
                '&status=eq.published&category=eq.' + cat +
                '&breaking=eq.false'
                '&order=created_at.desc&limit=5')
        except Exception as e:
            print('   ⚠️ ' + cat + ': ' + str(e)[:100])
            continue
        kandidat = [n for n in rows if not n.get('featured')]
        if kandidat:
            n = kandidat[0]
            try:
                supabase_update(n['id'], {'featured': True})
                print('   ⭐ ' + cat + ': ' + (n.get('title') or '')[:60])
                total += 1
            except Exception as e:
                print('   ⚠️ ' + cat + ': ' + str(e)[:100])
    print('🏁 Mode Web selesai — ' + str(total) + ' berita ditandai.')

def main():
    print('📣 KRAMANEWS SOSMED V1.9.1 (KRAMASOSMEDV191MARKER) — FB + INSTAGRAM')
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print('❌ Kunci FB belum lengkap (cek Secrets)!')
        return
    if not SUPABASE_ANON:
        print('❌ SUPABASE_PUBLISHABLE belum ada di Secrets!')
        return
    if not ADMIN_SECRET:
        print('❌ ADMIN_OPS_SECRET belum ada di Secrets!')
        return
    if '--web' in sys.argv:
        mode_web()
    else:
        mode_fb()
        mode_ig()

if __name__ == '__main__':
    main()
