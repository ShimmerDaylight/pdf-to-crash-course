# 📕 PDF to Crash Course — 教材速成课生成器

**把一本教材 PDF 变成打印精美的 A4 速成课复习讲义。**

专为 [Claude Code](https://claude.ai/code) 设计的 Skill，读取整本教材，逐章提取关键知识，用彩色盒子系统（定义·定理·公式·例题·警示·技巧·方法）重构内容，数学公式自动渲染为 SVG，最终输出可直接打印的 A4 PDF。

---

## 🎬 快速开始

在 Claude Code 中：

```
/pdf-to-crash-course D:\教材\微积分下.pdf
```

Skill 会自动完成：

1. **预检** — 判断 PDF 是否有可提取文字，扫描版自动运行 OCR
2. **结构分析** — 提取目录，构建章节大纲
3. **内容生成** — 逐章识别知识类型，归类到 7 色盒子
4. **组装** — 填入 HTML 模板（侧边栏导航 + Hero 封面 + 进度条）
5. **PDF 生成** — MathJax 渲染数学公式 → Playwright 输出 A4 PDF
6. **完整性检验** — 章节是否齐全？盒子分布是否合理？有无断链？

---

## 🎨 盒子系统

| 盒子 | 颜色 | 用途 |
|------|------|------|
| 🔵 定义 `.box.def` | 蓝 `#1d6fa5` | 概念、术语 |
| 🟣 定理 `.box.thm` | 紫 `#7c3aed` | 定理、命题、推论 |
| 🩵 公式 `.box.formula` | 青 `#0d7d6e` | 核心公式 |
| 🟠 例题 `.box.eg` | 橙 `#c2640a` | 例题 + 解答 |
| 🔴 警示 `.box.warn` | 红 `#c92a2a` | 常见错误 |
| 🟢 技巧 `.box.tip` | 绿 `#0b7b5b` | 速记口诀、章节导读 |
| 🔷 方法 `.box.method` | 靛 `#4f46e5` | 解题步骤 |

每个盒子只有**左边一条彩色竖线**和彩色标签，简洁干净，打印友好。

---

## 📂 目录结构

```
pdf-to-crash-course/
├── SKILL.md              # Skill 主流程定义（Stage 0~5）
├── README.md             # 本文件
├── references/           # 参考文档
│   ├── box-system.md     # 7 种盒子的 HTML 模板和配色
│   ├── content-strategy.md  # 内容抽取与章节结构模板
│   └── image-strategy.md    # 图片重绘 vs 提取的决策流程
├── scripts/              # 构建脚本
│   ├── build_pdf.py      # 主构建脚本（检测数学 → 调用 node）
│   ├── mathjax_to_svg.js # MathJax 预渲染 LaTeX → SVG
│   ├── playwright_to_pdf.js  # Playwright 渲染 HTML → A4 PDF
│   └── extract_images.py # 从 PDF 提取嵌入图片
└── templates/
    └── crash-course.html # HTML 骨架（CSS + 侧边栏 + Hero + 进度条）
```

---

## 🛠 依赖

| 工具 | 用途 | 安装 |
|------|------|------|
| **Python 3.10+** | OCR、构建脚本 | `winget install python` |
| **Node.js 18+** | MathJax、Playwright | `winget install nodejs` |
| **mathjax-full** | LaTeX → SVG 渲染 | `npm install mathjax-full` |
| **playwright** | HTML → A4 PDF | `npm install playwright` |
| **Chromium** | Playwright 浏览器 | `npx playwright install chromium` |
| **PyMuPDF** | PDF 读取 | `pip install pymupdf` |
| **EasyOCR** | 扫描版 PDF 文字识别 | `pip install easyocr` |

Skill 的 Stage 0 会自动检查并安装缺失依赖。

---

## 📊 实际效果

使用本 Skill 处理 **《微积分学》第四版 下册**（华中科技大学，256 页扫描版）：

| 指标 | 数值 |
|------|------|
| 原书页数 | 256 页 |
| 速成课页数 | **36 页** |
| 压缩比 | 1:7 |
| 定义盒子 | 39 个 |
| 定理盒子 | 22 个 |
| 公式盒子 | 54 个 |
| 例题盒子 | 6 个 |
| 警示盒子 | 8 个 |
| 技巧盒子 | 19 个 |
| 方法盒子 | 16 个 |
| 显示公式 ($$) | 126 个 |
| 行内公式 ($) | 483 个 |
| PDF 大小 | 1.9 MB |

---

## 🔧 安装此 Skill

**方法一：克隆到 Claude Code skills 目录**

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/YOUR_USER/pdf-to-crash-course.git
```

**方法二：手动复制**

将整个 `pdf-to-crash-course/` 文件夹复制到 `~/.claude/skills/` 下。

**方法三：项目级 Skill**

复制到你的项目 `.claude/skills/pdf-to-crash-course/` 目录。

---

## 🧪 Stage 5 完整性检验

Skill 内置了 6 项自动检验，确保输出质量：

1. **章节完整性** — 目录中每章都在 PDF 中
2. **内容覆盖** — 7 种盒子都有足够的数量
3. **结构完整性** — 侧边栏链接无断链，章节 ID 匹配
4. **数学渲染** — LaTeX `$$` 配对正确，公式数量合理
5. **PDF 质量** — 页数合理（15-80 页），文件大小正常（0.5-5 MB），首页末页非空
6. **占位符检查** — 无 TODO / FIXME / 待补充 等未完成标记

---

## ⚠️ 已知限制

- **扫描版 PDF 的数学公式**：OCR 对数学符号识别较差，Skill 依赖 Claude 的领域知识重建公式
- **复杂图片**：照片、显微图等无法重绘，需从原 PDF 提取（Stage 2 支持）
- **超大 PDF**：超过 400 页的教材建议分册处理
- **DRM 加密**：无法处理受保护 PDF

---

## 📄 许可

MIT License — 自由使用、修改、分发。

---

*Made for Claude Code. 用 AI 把厚教材变成薄讲义。*
