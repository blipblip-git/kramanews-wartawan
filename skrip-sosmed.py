# ══════════════════════════════════════════════════════
#  KRAMANEWS — SKRIP SOSMED V1.3 (FB POST RAPI)
#  Baru V1.3:
#   • Judul pakai UNICODE BOLD (tampil tebal di FB)
#   • Teks post lebih panjang (3 kalimat pertama isi berita)
#   • Link artikel ke kramanews.my.id (homepage — sementara)
#   • Gambar berita selalu ikut (photos endpoint)
#   • Anti-dobel via posted_fb
#   • Mode: fb (tiap 20 menit) / web (tandai unggulan)
# ══════════════════════════════════════════════════════

import requests
import os
import time
import sys
import json

FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN', '')
FB_PAGE_ID    = os.environ.get('FB_PAGE_ID', '')
SUPABASE_URL  = 'https://imcvijgytdjjpotlaltv.supabase.co'
SUPABASE_ANON = os.environ.get('SUPABASE_PUBLISHABLE', '')
SITE_URL      = 'https://kramanews.my.id'

KATEGORI_LABEL = {
    'nasional': 'Nasional', 'daerah': 'Daerah',
    'internasional': 'Internasional', 'ekonomi': 'Ekonomi',
    'olahraga': 'Olahraga', 'teknologi': 'Teknologi',
    'hiburan': 'Hiburan', 'kesehatan': 'Kesehatan',
}

# UNICODE BOLD — biar judul tampil TEBAL di FB
BOLD_MAP = {
    'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙',
    'G': '𝗚', 'H': '𝗛', 'I': '𝗜', 'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠',
    'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥', 'S': '𝗦', 'T': '𝗧',
    'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭',
    'a': '𝗮', 'b': '𝗯', 'c': '𝗰', 'd': '𝗱', 'e': '𝗲', 'f': '𝗳',
    'g': '𝗴', 'h': '𝗵', 'i': '𝗶', 'j': '𝗷', 'k': '𝗸', 'l': '𝗹', 'm': '𝗺',
    'n': '𝗻', 'o': '𝗼', 'p': '𝗽', 'q': '𝗾', 'r': '𝗿', 's': '𝘀', 't': '𝘁',
    'u': '𝘂', 'v': '𝘃', 'w': '𝘄', 'x': '𝘅', 'y': '𝘆', 'z': '𝘇',
    '0': '𝟬', '1': '𝟭', '2': '𝟮', '3': '𝟯', '4': '𝟰',
    '5': '𝟱', '6': '𝟲', '7': '𝟳', '8': '𝟴', '9': '𝟵',
}

def to_bold(text):
    """Ubah teks jadi unicode bold untuk FB."""
    return ''.join(BOLD_MAP.get(c, c) for c in text)

def supabase_get(query):
    r = requests.get(SUPABASE_URL + '/rest/v1/' + query,
        headers={'apikey': SUPABASE_ANON,
                 'Authorization': 'Bearer ' + SUPABASE_ANON},
        timeout=30)
    if not r.ok:
        raise Exception('Supabase GET ' + str(r.status_code) + ': ' + r.text[:150])
    return r.json() or []

def supabase_update(article_id, payload):
    r = requests.post(
        'https://imcvijgytdjjpotlaltv.supabase.co/functions/v1/admin-ops',
        headers={'apikey': SUPABASE_ANON,
                 'Authorization': 'Bearer ' + SUPABASE_ANON,
                 'Content-Type': 'application/json'},
        json={'action': 'update', 'id': article_id, 'payload': payload},
        timeout=30)
    try:
        data = r.json()
    except Exception:
        raise Exception('Edge HTTP ' + str(r.status_code) + ': ' + r.text[:150])
    if not r.ok or data.get('error'):
        raise Exception(str(data.get('error') or ('HTTP ' + str(r.status_code))))
    return data.get('data')

def ambil_teaser(content, kalimat=3):
    """Ambil N kalimat pertama dari isi berita sebagai teaser."""
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
    """Susun caption FB yang rapi: judul bold + teaser + lokasi + CTA."""
    cat = KATEGORI_LABEL.get(n.get('category', ''), n.get('category', ''))
    judul = (n.get('title') or '').strip()
    dateline = (n.get('dateline') or '').strip()
    content = (n.get('content') or '').strip()
    teaser = ambil_teaser(content, kalimat=3)

    lines = []
    if n.get('breaking'):
        lines.append('🚨 BREAKING NEWS')
        lines.append('')
    lines.append(to_bold(judul))
    lines.append('')
    if dateline:
        lines.append('📍 ' + dateline)
    if teaser:
        lines.append(teaser)
    lines.append('')
    lines.append('🔗 Baca selengkapnya di KramaNews:')
    lines.append(SITE_URL)
    lines.append('')
    lines.append('#' + cat.replace(' ', '') + ' #KramaNews #BeritaTerkini')

    return '\n'.join(lines)

def post_fb(n):
    pesan = buat_pesan_fb(n)
    img = (n.get('img') or '').strip()
    if img:
        return fb_post_photo(pesan, img)
    else:
        return fb_post_feed(pesan, SITE_URL)

def mode_fb():
    """Tiap run: ambil maks 3 berita tayang yang belum diposting ke FB."""
    print('📘 MODE FB — antrean auto-post...')
    rows = supabase_get(
        'articles?select=id,title,excerpt,content,category,img,dateline,posted_fb,breaking'
        '&status=eq.published&posted_fb=eq.false'
        '&order=created_at.desc&limit=3')

    if not rows:
        print('✅ Tidak ada berita baru yang perlu diposting. Selesai.')
        return

    ok = 0
    for n in rows:
        if n.get('breaking'):
            print('🚨 BREAKING: ' + (n.get('title') or '')[:60])
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

def mode_web():
    """Tandai 1 berita terbaru per kategori sebagai unggulan (referensi portal)."""
    print('🌐 MODE WEB — tandai berita unggulan per kategori...')
    total = 0
    cats = list(KATEGORI_LABEL.keys())
    for cat in cats:
        rows = supabase_get(
            'articles?select=id,title,category,updated_at'
            '&status=eq.published&category=eq.' + cat +
            '&featured=eq.false&breaking=eq.false'
            '&order=created_at.desc&limit=1')
        for n in rows:
            supabase_update(n['id'], {'featured': True})
            print('   ⭐ ' + cat + ': ' + (n.get('title') or '')[:60])
            total += 1
    print('🏁 Mode Web selesai — ' + str(total) + ' berita ditandai.')

def main():
    print('📣 KRAMANEWS SOSMED V1.3 — FB POST RAPI')
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print('❌ Kunci FB belum lengkap (cek Secrets)!')
        return
    if not SUPABASE_ANON:
        print('❌ SUPABASE_PUBLISHABLE belum ada di Secrets!')
        return
    if '--web' in sys.argv:
        mode_web()
    else:
        mode_fb()

if __name__ == '__main__':
    main()
