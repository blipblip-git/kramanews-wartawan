# ══════════════════════════════════════════════════════
#  KRAMANEWS — SKRIP SOSMED V1.1 (PATCH VIA EDGE FUNCTION)
#  Perbaikan: penandaan posted_fb kini lewat admin-ops
#  (jalur aman) — tidak lagi diblokir RLS → anti dobel ✅
# ══════════════════════════════════════════════════════

import requests
import os
import time

FB_PAGE_TOKEN = os.environ.get('FB_PAGE_TOKEN', '')
FB_PAGE_ID    = os.environ.get('FB_PAGE_ID', '')
SUPABASE_URL  = 'https://imcvijgytdjjpotlaltv.supabase.co'
SUPABASE_ANON = os.environ.get('SUPABASE_PUBLISHABLE', '')
EDGE_URL      = SUPABASE_URL + '/functions/v1/admin-ops'
SITE_URL      = 'https://kramanews.my.id'

KATEGORI_LABEL = {
    'nasional': 'Nasional', 'daerah': 'Daerah',
    'internasional': 'Internasional', 'ekonomi': 'Ekonomi',
    'olahraga': 'Olahraga', 'teknologi': 'Teknologi',
    'hiburan': 'Hiburan', 'kesehatan': 'Kesehatan',
}

def supabase_get(query):
    r = requests.get(SUPABASE_URL + '/rest/v1/' + query,
        headers={'apikey': SUPABASE_ANON,
                 'Authorization': 'Bearer ' + SUPABASE_ANON},
        timeout=30)
    if not r.ok:
        raise Exception('Supabase GET ' + str(r.status_code) + ': ' + r.text[:150])
    return r.json() or []

def supabase_update(article_id, payload):
    """Tandai via edge function admin-ops (jalur aman, sama seperti panel admin)."""
    r = requests.post(EDGE_URL,
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

def main():
    print('📘 KRAMANEWS SOSMED V1.1 — memeriksa antrean Facebook...')
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        print('❌ Kunci FB belum lengkap (cek Secrets)!')
        return
    if not SUPABASE_ANON:
        print('❌ SUPABASE_PUBLISHABLE belum ada di Secrets!')
        return

    rows = supabase_get(
        'articles?select=id,title,excerpt,category,img,posted_fb'
        '&status=eq.published&posted_fb=eq.false'
        '&order=created_at.desc&limit=3')

    if not rows:
        print('✅ Tidak ada berita baru yang perlu diposting. Selesai.')
        return

    ok = 0
    for n in rows:
        cat = KATEGORI_LABEL.get(n.get('category', ''), n.get('category', ''))
        judul = (n.get('title') or '').strip()
        ringkasan = (n.get('excerpt') or '').strip()
        img = (n.get('img') or '').strip()
        pesan = ('📰 ' + judul + '\n\n' + ringkasan +
                 '\n\n🏷️ ' + cat + ' | KramaNews • kramanews.my.id')
        print('📤 Posting: ' + judul[:60])
        try:
            if img:
                fb_post_photo(pesan, img)
            else:
                fb_post_feed(pesan, SITE_URL)
            supabase_update(n['id'], {'posted_fb': True})
            ok += 1
            print('   ✅ Terkirim ke Facebook Page + ditandai posted_fb!')
        except Exception as e:
            print('   ⚠️ Gagal: ' + str(e)[:120])
        time.sleep(3)

    print('🏁 Selesai — ' + str(ok) + ' berita terkirim ke FB.')

if __name__ == '__main__':
    main()