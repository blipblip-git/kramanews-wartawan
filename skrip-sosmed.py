# KRAMANEWS — SKRIP SOSMED V1.22 (FB + INSTAGRAM)
# V1.22: komentar FB kembali "🔗 Baca selengkapnya: <link>", caption FB "🔗 Baca selengkapnya di komentar 👇"
# V1.21: caption FB kosong, komentar FB "Baca selengkapnya di komentar: <link>"
# V1.20: caption FB tanpa hashtag, IG fix NULL posted_ig
# V1.19: 13 slot baru (tiap jam 06:45-18:45), 06:45 dilindungi, 11:45↔16:45 ditukar
# V1.18: hapus caption FB + hashtag di gambar, tambah tanggal+jam

import requests
import os
import io
import time
import sys
import json
import re
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont

FB_PAGE_TOKEN   = os.environ.get('FB_PAGE_TOKEN', '')
FB_PAGE_ID      = os.environ.get('FB_PAGE_ID', '')
IG_TOKEN        = os.environ.get('IG_PAGE_TOKEN', '')
SUPABASE_URL    = 'https://imcvijgytdjjpotlaltv.supabase.co'
SUPABASE_ANON   = os.environ.get('SUPABASE_PUBLISHABLE', '')
SUPABASE_SERVICE = os.environ.get('SUPABASE_SERVICE', '')
SITE_URL        = 'https://kramanews.my.id'

WITA = timezone(timedelta(hours=8))

BUCKET_STORAGE = 'gambar'

FONT_BOLD_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG_PATH  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

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

HARI_ID_SHORT = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN_ID_SHORT = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
                  'Agustus', 'September', 'Oktober', 'November', 'Desember']

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

def format_tanggal_jam_wita(iso_str):
    if not iso_str:
        return ''
    try:
        dt = datetime.fromisoformat(str(iso_str).replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        dt_wita = dt.astimezone(WITA)
        hari = HARI_ID_SHORT[dt_wita.weekday()]
        tanggal = dt_wita.day
        bulan = BULAN_ID_SHORT[dt_wita.month]
        tahun = dt_wita.year
        jam = dt_wita.strftime('%H:%M')
        return f'{hari}, {tanggal} {bulan} {tahun} · {jam} WITA'
    except Exception:
        return ''

# ═══ RENDER OVERLAY GAMBAR FB (Pillow) ═══

def _font(path, ukuran):
    try:
        return ImageFont.truetype(path, ukuran)
    except Exception:
        try:
            return ImageFont.truetype(FONT_BOLD_PATH, ukuran)
        except Exception:
            return ImageFont.load_default()

def _wrap_text(text, font, max_width, draw):
    kata = text.split()
    baris = []
    baris_ini = ''
    for k in kata:
        uji = (baris_ini + ' ' + k).strip()
        bbox = draw.textbbox((0, 0), uji, font=font)
        lebar = bbox[2] - bbox[0]
        if lebar <= max_width:
            baris_ini = uji
        else:
            if baris_ini:
                baris.append(baris_ini)
            baris_ini = k
    if baris_ini:
        baris.append(baris_ini)
    return baris

def render_gambar_fb(n):
    img_url = (n.get('img') or '').strip()
    if not img_url:
        return None
    try:
        r = requests.get(img_url, timeout=30)
        if not r.ok:
            print('   ⚠️ Gagal ambil gambar asli: HTTP ' + str(r.status_code))
            return None
        img = Image.open(io.BytesIO(r.content)).convert('RGBA')
    except Exception as e:
        print('   ⚠️ Gagal buka gambar: ' + str(e)[:80])
        return None

    target_w, target_h = 1200, 630
    rasio_img = img.width / img.height
    rasio_target = target_w / target_h
    if rasio_img > rasio_target:
        new_h = target_h
        new_w = int(new_h * rasio_img)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        kiri = (new_w - target_w) // 2
        img = img.crop((kiri, 0, kiri + target_w, target_h))
    else:
        new_w = target_w
        new_h = int(new_w / rasio_img)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        atas = (new_h - target_h) // 2
        img = img.crop((0, atas, target_w, atas + target_h))

    img = img.convert('RGBA')

    overlay = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    draw_o = ImageDraw.Draw(overlay)
    for y in range(target_h):
        alpha = int(200 * (y / target_h) ** 1.2)
        draw_o.line([(0, y), (target_w, y)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    font_badge = _font(FONT_BOLD_PATH, 32)
    font_judul = _font(FONT_BOLD_PATH, 56)
    font_lokasi = _font(FONT_BOLD_PATH, 34)
    font_tanggal = _font(FONT_BOLD_PATH, 30)

    cat = (n.get('category') or '').upper()
    if cat:
        bbox_badge = draw.textbbox((0, 0), cat, font=font_badge)
        w_badge = bbox_badge[2] - bbox_badge[0]
        h_badge = bbox_badge[3] - bbox_badge[1]
        pad_x, pad_y = 28, 14
        badge_w = w_badge + pad_x * 2
        badge_h = h_badge + pad_y * 2
        badge_x, badge_y = 40, 40
        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=badge_h // 2, fill=(30, 90, 210, 255)
        )
        draw.text(
            (badge_x + pad_x, badge_y + pad_y - 2),
            cat, font=font_badge, fill=(255, 255, 255, 255)
        )

    judul = (n.get('title') or '').strip()
    if judul:
        max_w_judul = target_w - 80
        baris_judul = _wrap_text(judul, font_judul, max_w_judul, draw)
        if len(baris_judul) > 4:
            baris_judul = baris_judul[:4]
            baris_judul[-1] = baris_judul[-1].rstrip() + '…'

        line_h = 70
        total_h = len(baris_judul) * line_h
        y_judul = target_h - 240 - total_h + 10

        for i, baris in enumerate(baris_judul):
            y = y_judul + i * line_h
            for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
                draw.text((40 + dx, y + dy), baris, font=font_judul, fill=(0, 0, 0, 220))
            draw.text((40, y), baris, font=font_judul, fill=(255, 255, 255, 255))

    dateline = (n.get('dateline') or '').strip().upper()
    y_lokasi = target_h - 155
    if dateline:
        pin_x = 40
        pin_y = y_lokasi - 5
        draw.ellipse([pin_x, pin_y + 4, pin_x + 20, pin_y + 24], fill=(255, 255, 255, 255))
        draw.polygon(
            [(pin_x + 10, pin_y + 34), (pin_x + 2, pin_y + 20), (pin_x + 18, pin_y + 20)],
            fill=(255, 255, 255, 255)
        )
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            draw.text((pin_x + 32 + dx, y_lokasi + dy), dateline, font=font_lokasi, fill=(0, 0, 0, 220))
        draw.text((pin_x + 32, y_lokasi), dateline, font=font_lokasi, fill=(255, 255, 255, 255))

    tgl_jam = format_tanggal_jam_wita(n.get('created_at'))
    y_tanggal = target_h - 85
    if tgl_jam:
        ck_x = 40
        ck_y = y_tanggal + 4
        draw.ellipse([ck_x, ck_y, ck_x + 26, ck_y + 26], outline=(255, 255, 255, 255), width=3)
        draw.line([(ck_x + 13, ck_y + 13), (ck_x + 13, ck_y + 6)], fill=(255, 255, 255, 255), width=3)
        draw.line([(ck_x + 13, ck_y + 13), (ck_x + 19, ck_y + 15)], fill=(255, 255, 255, 255), width=3)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            draw.text((ck_x + 40 + dx, y_tanggal + dy), tgl_jam, font=font_tanggal, fill=(0, 0, 0, 220))
        draw.text((ck_x + 40, y_tanggal), tgl_jam, font=font_tanggal, fill=(255, 255, 255, 255))

    out = io.BytesIO()
    img.convert('RGB').save(out, format='JPEG', quality=88)
    return out.getvalue()

def upload_gambar_supabase(nama_file, bytes_gambar):
    if not SUPABASE_SERVICE:
        raise Exception('SUPABASE_SERVICE belum ada')
    url = SUPABASE_URL + '/storage/v1/object/' + BUCKET_STORAGE + '/' + nama_file
    headers = {
        'Authorization': 'Bearer ' + SUPABASE_SERVICE,
        'Content-Type': 'image/jpeg',
        'x-upsert': 'true',
    }
    r = requests.post(url, headers=headers, data=bytes_gambar, timeout=60)
    if not r.ok:
        raise Exception('Upload Storage ' + str(r.status_code) + ': ' + r.text[:200])
    publik = SUPABASE_URL + '/storage/v1/object/public/' + BUCKET_STORAGE + '/' + nama_file
    return publik

# ═══ FB POST ═══

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

def fb_komentar(post_id, pesan):
    r = requests.post(
        'https://graph.facebook.com/v21.0/' + post_id + '/comments',
        data={'message': pesan, 'access_token': FB_PAGE_TOKEN},
        timeout=30)
    if not r.ok:
        raise Exception('FB komentar ' + str(r.status_code) + ': ' + r.text[:200])
    return r.json()

# V1.22: caption FB kembali "Baca selengkapnya di komentar 👇"
def buat_pesan_fb(n):
    return '🔗 Baca selengkapnya di komentar 👇'

def post_fb(n):
    pesan = buat_pesan_fb(n)
    img = (n.get('img') or '').strip()
    link_artikel = SITE_URL + '/?baca=' + str(n.get('id'))
    post_id = None

    img_kirim = img
    if img:
        try:
            print('   🎨 Render overlay gambar...')
            bytes_gambar = render_gambar_fb(n)
            if bytes_gambar:
                nama_file = 'fb-' + str(n.get('id')) + '-' + str(int(time.time())) + '.jpg'
                img_kirim = upload_gambar_supabase(nama_file, bytes_gambar)
                print('   📤 Gambar overlay diunggah: ' + img_kirim[:80])
            else:
                print('   ⚠️ Render gagal, pakai gambar asli.')
        except Exception as e:
            print('   ⚠️ Overlay/upload gagal (' + str(e)[:100] + ') — pakai gambar asli.')

    if img_kirim:
        hasil = fb_post_photo(pesan, img_kirim)
        post_id = (hasil or {}).get('id') or (hasil or {}).get('post_id')
    else:
        hasil = fb_post_feed(pesan, link_artikel)
        post_id = (hasil or {}).get('id')

    if post_id:
        try:
            # V1.22: komentar kembali "Baca selengkapnya: <link>"
            pesan_komentar = '🔗 Baca selengkapnya: ' + link_artikel
            fb_komentar(post_id, pesan_komentar)
            print('   💬 Link artikel sudah masuk komentar.')
        except Exception as e:
            print('   ⚠️ Gagal kirim komentar link: ' + str(e)[:100])

    return post_id

# ═══ SLOT & PILIH BERITA V1.22 ═══

SLOT_JADWAL = {
    6:  ('nasional', 'nasional', ['internasional', 'teknologi', 'olahraga', 'kesehatan', 'otomotif', 'ekonomi']),
    7:  ('tarakan', 'tarakan', ['kaltara', 'nasional']),
    8:  ('kaltara', 'kaltara', ['tarakan', 'nasional']),
    9:  ('internasional', 'internasional', ['nasional', 'ekonomi', 'teknologi', 'olahraga', 'kesehatan', 'otomotif']),
    10: ('tarakan', 'tarakan', ['kaltara', 'nasional']),
    11: ('kaltara', 'kaltara', ['tarakan', 'nasional']),
    12: ('tarakan', 'tarakan', ['kaltara', 'nasional']),
    13: ('kaltara', 'kaltara', ['tarakan', 'nasional']),
    14: ('olahraga', 'olahraga', ['nasional', 'ekonomi', 'teknologi', 'internasional', 'kesehatan', 'otomotif']),
    15: ('tarakan', 'tarakan', ['kaltara', 'nasional']),
    16: ('tarakan', 'tarakan', ['kaltara', 'nasional']),
    17: ('tarakan', 'tarakan', ['nasional', 'internasional']),
    18: ('kaltara', 'kaltara', ['tarakan', 'nasional']),
}

def slot_saat_ini():
    jam = datetime.now(WITA).hour
    if jam in SLOT_JADWAL:
        return SLOT_JADWAL[jam]
    return None

def _cari_dengan_cascade(rows, kategori_utama, kategori_fallback, izinkan_fallback_apa_saja=True):
    id_terpakai = set()

    def ambil(pred):
        for n in rows:
            if n['id'] in id_terpakai:
                continue
            if pred(n):
                return n
        return None

    if kategori_utama == 'tarakan':
        pilihan = ambil(is_tarakan)
        if pilihan:
            return pilihan
        for kat in kategori_fallback:
            if kat == 'kaltara':
                pilihan = ambil(is_kaltara_lain)
            elif kat == 'nasional':
                pilihan = ambil(lambda n: n.get('category') == 'nasional')
            else:
                pilihan = ambil(lambda n, k=kat: n.get('category') == k)
            if pilihan:
                return pilihan
        if izinkan_fallback_apa_saja:
            return ambil(lambda n: True)
        return None

    if kategori_utama == 'kaltara':
        pilihan = ambil(is_kaltara_lain)
        if pilihan:
            return pilihan
        for kat in kategori_fallback:
            if kat == 'tarakan':
                pilihan = ambil(is_tarakan)
            elif kat == 'nasional':
                pilihan = ambil(lambda n: n.get('category') == 'nasional')
            else:
                pilihan = ambil(lambda n, k=kat: n.get('category') == k)
            if pilihan:
                return pilihan
        if izinkan_fallback_apa_saja:
            return ambil(lambda n: True)
        return None

    pilihan = ambil(lambda n: n.get('category') == kategori_utama)
    if pilihan:
        return pilihan
    for kat in kategori_fallback:
        pilihan = ambil(lambda n, k=kat: n.get('category') == k)
        if pilihan:
            return pilihan
    if izinkan_fallback_apa_saja:
        return ambil(lambda n: True)
    return None

def mode_fb():
    slot = slot_saat_ini()
    if not slot:
        print('📘 MODE FB V1.22 — jam ' + str(datetime.now(WITA).hour) + ':XX di luar jadwal. Skip.')
        return
    nama_slot, kategori_utama, kategori_fallback = slot
    izinkan_apa_saja = (datetime.now(WITA).hour != 6)
    print('📘 MODE FB V1.22 — slot: ' + nama_slot.upper() + ' (jam ' + str(datetime.now(WITA).hour) + ':45)')

    rows = supabase_get_safe(
        'articles?select=id,title,excerpt,content,category,img,dateline,posted_fb,breaking,created_at'
        '&status=eq.published&or=(posted_fb.eq.false,posted_fb.is.null)'
        '&order=created_at.desc&limit=120')

    if not rows:
        print('✅ Tidak ada berita baru sama sekali. Selesai.')
        return

    n = _cari_dengan_cascade(rows, kategori_utama, kategori_fallback,
                             izinkan_fallback_apa_saja=izinkan_apa_saja)

    if not n:
        print('✅ Tidak ada kandidat sama sekali. Selesai.')
        return

    if datetime.now(WITA).hour == 6 and is_kaltara(n):
        print('⏭️ Slot 06:45 — kandidat Tarakan/Kaltara ditolak. Selesai.')
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
    if not slot:
        print('📸 MODE IG V1.22 — jam di luar jadwal. Skip.')
        return
    nama_slot, kategori_utama, kategori_fallback = slot
    izinkan_apa_saja = (datetime.now(WITA).hour != 6)
    print('📸 MODE IG V1.22 — slot: ' + nama_slot.upper())

    if not IG_TOKEN:
        print('⏭️ IG_PAGE_TOKEN belum ada di Secrets — IG dilewati.')
        return

    try:
        rows = supabase_get_safe(
            'articles?select=id,title,excerpt,content,category,img,dateline,posted_ig,breaking,created_at'
            '&status=eq.published&or=(posted_ig.eq.false,posted_ig.is.null)'
            '&order=created_at.desc&limit=120')
    except Exception as e:
        print('❌ Gagal ambil antrean IG: ' + str(e)[:120])
        return

    if not rows:
        print('✅ Tidak ada berita baru untuk IG. Selesai.')
        return

    rows_berimg = [n for n in rows if ada_img(n)]
    print('   Total antrean: ' + str(len(rows)) + ' - bergambar: ' + str(len(rows_berimg)))
    if not rows_berimg:
        print('✅ Tidak ada kandidat IG bergambar. Selesai.')
        return

    n = _cari_dengan_cascade(rows_berimg, kategori_utama, kategori_fallback,
                             izinkan_fallback_apa_saja=izinkan_apa_saja)

    if not n:
        print('✅ Tidak ada kandidat IG. Selesai.')
        return

    if datetime.now(WITA).hour == 6 and is_kaltara(n):
        print('⏭️ Slot 06:45 — kandidat IG Tarakan/Kaltara ditolak. Selesai.')
        return

    if is_tarakan(n):
        label = 'TARAKAN'
    elif is_kaltara_lain(n):
        label = 'KALTARA'
    else:
        label = (n.get('category') or '?').upper()

    print('📋 Terpilih 1 berita IG:')
    print('   • [' + label + '] ' + (n.get('title') or '')[:70])

    img_kirim = n['img'].strip()
    try:
        print('   🎨 Render overlay gambar IG...')
        bytes_gambar = render_gambar_fb(n)
        if bytes_gambar:
            nama_file = 'ig-' + str(n.get('id')) + '-' + str(int(time.time())) + '.jpg'
            img_kirim = upload_gambar_supabase(nama_file, bytes_gambar)
            print('   📤 Gambar overlay IG diunggah.')
    except Exception as e:
        print('   ⚠️ Overlay IG gagal (' + str(e)[:100] + ') — pakai gambar asli.')

    try:
        ig_post_photo(img_kirim, buat_pesan_ig(n))
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
    print('📣 KRAMANEWS SOSMED V1.22 — FB + INSTAGRAM (13 siklus)')
    print('   06:45 · 07:45 · 08:45 · 09:45 · 10:45 · 11:45 · 12:45')
    print('   13:45 · 14:45 · 15:45 · 16:45 · 17:45 · 18:45 WITA')
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