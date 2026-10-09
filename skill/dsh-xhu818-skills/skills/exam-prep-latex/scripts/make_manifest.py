# -*- coding: utf-8 -*-
"""生成 OCR 批处理清单（按优先级排序）。"""
import json, os

S = r'C:\Users\mate book D14\Downloads'
W = r'C:\Users\mate book D14\Documents\WeChat Files\wxid_f27188h0yca722\FileStorage\File\2026-10'
ROOT = r'C:\Users\mate book D14\Documents\deepseek-harness\default-workspace\xhu818'
OCR = os.path.join(ROOT, '02-ocr')


def safe(name):
    return ''.join(c if (c.isalnum() or c == '-' or '\u4e00' <= c <= '\u9fff') else '_' for c in name)


items = []

# A. 赵琴教材 TOC 与第一章（先出，用来定章节页码）
items.append(dict(tag='zhqin-p1-40', pdf=os.path.join(S, '11.流体力学与流体机械电子版.pdf'),
                  out=os.path.join(OCR, 'zhqin'), px=1700, first=1, last=40))

# B. 历年真题 / 答案 / 题库
exam_files = ['2014年试题', '2016年试题', '2017年试题', '2018年试题', '2019年试题', '2020年试题',
              '2021年试题', '2022-818工程流体力学',
              '2014年答案', '2015年答案', '2016年答案', '2017年答案', '2018年答案', '2019年答案', '2020年答案']
for n in exam_files:
    items.append(dict(tag=n, pdf=os.path.join(S, n + '.pdf'),
                      out=os.path.join(OCR, 'exams', safe(n)), px=1800))
items.append(dict(tag='17.pdf 题库', pdf=os.path.join(S, '17.pdf'), out=os.path.join(OCR, 'exams', '17'), px=1800))
items.append(dict(tag='10.西华选择题题库', pdf=os.path.join(S, '10.西华选择题题库（精简版）.pdf'),
                  out=os.path.join(OCR, 'bank10'), px=1800))

# C. 赵琴教材其余部分
items.append(dict(tag='zhqin-p41-334', pdf=os.path.join(S, '11.流体力学与流体机械电子版.pdf'),
                  out=os.path.join(OCR, 'zhqin'), px=1700, first=41))

# D. 孔珑习题解答
items.append(dict(tag='konglong', pdf=os.path.join(W, '孔珑 工程流体力学学习指导及习题解答 978-7-302-37859-4_13803116.pdf'),
                  out=os.path.join(OCR, 'konglong'), px=1700))

# E. 孔珑教材（流体力学.pdf，作为解答的对照，可选）
items.append(dict(tag='konglong-jiaocai', pdf=os.path.join(W, '流体力学.pdf'),
                  out=os.path.join(OCR, 'konglong_jc'), px=1700, skip=True))

with open(os.path.join(ROOT, 'scripts', 'ocr_manifest.json'), 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=1)

print('manifest entries =', len(items))
for it in items:
    print('  %-24s px=%-5s first=%-4s last=%-4s' % (it['tag'], it['px'], it.get('first', 1), it.get('last', 0)))
