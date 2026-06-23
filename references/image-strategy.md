# 图片处理策略

## 决策流程

```
读取PDF → 遇到图片 →
  ├─ 函数曲线/统计图/流程图/简单示意图？ → 重绘（矢量无损）
  └─ 照片/显微图/复杂电路/地图/截图？   → 提取原图嵌入
```

## 可重绘类型

| 图片类型 | 工具 | 输出 |
|---------|------|------|
| 函数曲线 | LaTeX TikZ / matplotlib | 内联 SVG |
| 统计图（散点/柱状/箱线） | matplotlib | 内联 SVG |
| 概率分布图（正态/t/F/卡方） | LaTeX TikZ | 内联 SVG |
| 简单流程图/框图 | Mermaid / SVG | 内联 SVG |
| 韦恩图/集合图 | LaTeX TikZ | 内联 SVG |

重绘注意事项：
- 配色与讲义一致
- SVG 直接内嵌 HTML，不外部引用
- 图下加 `<div class="caption">图N: 标题</div>`

## 需提取类型

照片、显微影像、复杂电路图、地图、软件截图、超过 10 个元素的复杂构图。

## 提取流程

1. Claude 记录需提取图片的**页码**
2. 在 HTML 中插入：`<div class="img-wrap"><img src="images/page{N}_{idx}.png"><div class="caption">...</div></div>`
3. PDF 生成前运行：`python scripts/extract_images.py <pdf> <page> images/`
4. Playwright 渲染时通过 `file://` 加载本地图片

## 图片命名

提取后命名：`page{页码}_{序号}.{ext}`（如 `page42_1.png`），全部存入 `images/` 目录。

## 注意事项

- 拿不准就提取，不要冒险重绘
- 单张图片不超过 2MB
- PDF 中矢量化绘制的图也会被 PyMuPDF 提取为位图
