# cek_versi.py — penjaga versi otomatis (dipanggil wartawan.yml sebelum run utama)
import re
try:
    src = open('skrip-wartawan.py', encoding='utf-8').read()
except FileNotFoundError:
    print('❌ skrip-wartawan.py TIDAK DITEMUKAN!')
    raise SystemExit(1)
tag  = re.search(r"FILE_VERSI\s*=\s*'([^']+)'", src)
part = re.search(r"FILE_PART_AKHIR\s*=\s*'([^']+)'", src)
if not tag or not part:
    print('❌ SENTINEL VERSI HILANG — FILE_VERSI/FILE_PART_AKHIR tidak ditemukan!')
    raise SystemExit(1)
v, p = tag.group(1), part.group(1)
if src.rstrip().endswith('# AKHIR ' + p):
    print('✅ Struktur OK — versi ' + v + ' di ' + p + ' (part terakhir)')
else:
    print('⚠️ PERINGATAN: file TIDAK diakhiri "# AKHIR ' + p + '" — part terakhir melenceng / sentinel pindah! Cek ujung file!')
