# -*- coding: utf-8 -*-
"""诊断 ResizeImgError：逐页打印 rect / pixmap 尺寸 / 底层异常。"""
import sys, traceback
import fitz
import numpy as np
from rapidocr_onnxruntime import RapidOCR

pdf = sys.argv[1]
px = int(sys.argv[2]) if len(sys.argv) > 2 else 1800
engine = RapidOCR()
doc = fitz.open(pdf)
print('pages =', doc.page_count)
for pno in range(doc.page_count):
    page = doc[pno]
    r = page.rect
    zoom = px / max(r.width, r.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = img[:, :, :3]
    print('page %d rect=%.0fx%.0f zoom=%.4f pix=%dx%d n=%d contig=%s rot=%d' % (
        pno + 1, r.width, r.height, zoom, pix.width, pix.height, pix.n, img.flags['C_CONTIGUOUS'], page.rotation))
    try:
        res, _ = engine(img)
        print('        ok, lines =', len(res) if res else 0)
    except Exception as e:
        print('        FAIL:', type(e).__name__, e)
        traceback.print_exc()
        try:
            img2 = np.ascontiguousarray(img)
            res, _ = engine(img2)
            print('        retry contiguous ok, lines =', len(res) if res else 0)
        except Exception as e2:
            print('        retry contiguous FAIL:', type(e2).__name__, e2)
