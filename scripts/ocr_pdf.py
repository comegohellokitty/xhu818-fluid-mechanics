# -*- coding: utf-8 -*-
"""用 RapidOCR(onnxruntime) 对 PDF 逐页做中文 OCR。
用法:
  python ocr_pdf.py --pdf <文件> --out <输出目录> [--first 1] [--last 20] [--px 1800] [--merge]
输出: <输出目录>/page-0001.txt ... 以及(可选) merged.txt
"""
import argparse, os, sys, time
import fitz  # PyMuPDF
import numpy as np


def install_safe_cv2_resize():
    """RapidOCR 内部调用 cv2.resize；在高负载/内存吃紧时会偶发
    cv2.error: Unknown C++ exception from OpenCV code（ResizeImgError）。
    这里给 cv2.resize 打补丁：失败时先降到单线程重试，再失败则用 PIL 近似替代。"""
    import cv2
    if getattr(cv2.resize, '_xhu_safe', False):
        return
    orig = cv2.resize

    def safe_resize(src, dsize, *args, **kwargs):
        try:
            return orig(src, dsize, *args, **kwargs)
        except Exception:
            pass
        try:
            cv2.setNumThreads(1)
            return orig(src, dsize, *args, **kwargs)
        except Exception:
            pass
        from PIL import Image
        w, h = int(dsize[0]), int(dsize[1])
        if src.ndim == 2:
            return np.array(Image.fromarray(src).resize((w, h), Image.BILINEAR))
        rgb = np.ascontiguousarray(src[:, :, ::-1])
        out = np.array(Image.fromarray(rgb).resize((w, h), Image.BILINEAR))
        return np.ascontiguousarray(out[:, :, ::-1])

    safe_resize._xhu_safe = True
    cv2.resize = safe_resize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--first', type=int, default=1)
    ap.add_argument('--last', type=int, default=0)
    ap.add_argument('--px', type=int, default=1800, help='目标图片长边像素')
    ap.add_argument('--merge', action='store_true')
    ap.add_argument('--gray', action='store_true')
    args = ap.parse_args()

    install_safe_cv2_resize()
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR()

    doc = fitz.open(args.pdf)
    n = doc.page_count
    first = max(1, args.first)
    last = n if args.last <= 0 else min(n, args.last)
    os.makedirs(args.out, exist_ok=True)

    merged = []
    failures = []
    for pno in range(first, last + 1):
        t0 = time.time()
        page = doc[pno - 1]
        r = page.rect
        zoom = args.px / max(r.width, r.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY if args.gray else fitz.csRGB)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = img[:, :, :3]
        # RapidOCR 在内存吃紧时会偶发 cv2.error(Unknown C++ exception)，这里重试三次
        res = None
        last_err = None
        for attempt in range(3):
            try:
                res, _ = engine(np.ascontiguousarray(img) if attempt else img)
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                time.sleep(1.5 * (attempt + 1))
        if last_err is not None:
            failures.append((pno, repr(last_err)))
            print('[%d/%d] page %d  FAILED: %r' % (pno - first + 1, last - first + 1, pno, last_err), flush=True)
        lines = []
        if res:
            lines = [str(x[1]).strip() for x in res if str(x[1]).strip()]
        txt = '\n'.join(lines)
        fn = os.path.join(args.out, 'page-%04d.txt' % pno)
        with open(fn, 'w', encoding='utf-8') as f:
            f.write(txt)
        merged.append('===== page %d =====\n%s' % (pno, txt))
        print('[%d/%d] page %d  %.1fs  %d lines' % (pno - first + 1, last - first + 1, pno, time.time() - t0, len(lines)), flush=True)

    if failures:
        with open(os.path.join(args.out, '_failures.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join('%d\t%s' % (p, e) for p, e in failures))

    if args.merge:
        with open(os.path.join(args.out, 'merged.txt'), 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(merged))
        print('merged ->', os.path.join(args.out, 'merged.txt'))


def gray_ok(img):
    return True


if __name__ == '__main__':
    main()
