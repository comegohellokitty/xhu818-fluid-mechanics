# -*- coding: utf-8 -*-
"""按清单批量 OCR（只加载一次模型，速度最快）。
用法: python ocr_batch.py ocr_manifest.json
清单格式: [{"pdf": "...", "out": "...", "px": 1700, "first": 1, "last": 0, "tag": "zhqin"}, ...]
每个条目结束后写 <out>/merged.txt；失败页记录到 <out>/_failures.txt，绝不中断整批。
"""
import json, os, sys, time
import fitz
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ocr_pdf import install_safe_cv2_resize  # noqa: E402

install_safe_cv2_resize()
from rapidocr_onnxruntime import RapidOCR  # noqa: E402


def ocr_one(engine, item):
    pdf, out = item['pdf'], item['out']
    px = item.get('px', 1800)
    doc = fitz.open(pdf)
    n = doc.page_count
    first = max(1, item.get('first', 1))
    last = n if item.get('last', 0) <= 0 else min(n, item['last'])
    os.makedirs(out, exist_ok=True)
    merged, failures = [], []
    print('## %s  pages %d..%d  (%d total)' % (item.get('tag', os.path.basename(pdf)), first, last, n), flush=True)
    for pno in range(first, last + 1):
        t0 = time.time()
        page = doc[pno - 1]
        r = page.rect
        zoom = px / max(r.width, r.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = img[:, :, :3]
        res, last_err = None, None
        for attempt in range(3):
            try:
                res, _ = engine(np.ascontiguousarray(img) if attempt else img)
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                time.sleep(1.0 + attempt)
        if last_err is not None:
            failures.append((pno, repr(last_err)))
        lines = [str(x[1]).strip() for x in (res or []) if str(x[1]).strip()]
        txt = '\n'.join(lines)
        with open(os.path.join(out, 'page-%04d.txt' % pno), 'w', encoding='utf-8') as f:
            f.write(txt)
        merged.append('===== page %d =====\n%s' % (pno, txt))
        flag = '  <<< FAILED' if last_err is not None else ''
        print('[%d/%d] page %d  %.1fs  %d lines%s' % (pno - first + 1, last - first + 1, pno, time.time() - t0, len(lines), flag), flush=True)
    with open(os.path.join(out, 'merged.txt'), 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(merged))
    if failures:
        with open(os.path.join(out, '_failures.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join('%d\t%s' % (p, e) for p, e in failures))
    doc.close()


def main():
    with open(sys.argv[1], encoding='utf-8') as f:
        manifest = json.load(f)
    engine = RapidOCR()
    t0 = time.time()
    for i, item in enumerate(manifest, 1):
        if item.get('skip'):
            continue
        print('===== [%d/%d] %s =====' % (i, len(manifest), item.get('tag', item['pdf'])), flush=True)
        try:
            ocr_one(engine, item)
        except Exception as exc:  # noqa: BLE001
            print('!!!! entry failed: %s -> %r' % (item.get('tag', item['pdf']), exc), flush=True)
        print('---- elapsed %.1f min ----' % ((time.time() - t0) / 60), flush=True)
    print('ALL DONE in %.1f min' % ((time.time() - t0) / 60), flush=True)


if __name__ == '__main__':
    main()
