# 盒子系统使用说明

## 概述

8 种彩色盒子用于组织不同类型的知识点。每种盒子只有**左边一条彩色竖线**和彩色标签，简洁干净。

## 盒子类型速查

| 类型 | CSS类 | 左边框色 | 用途 |
|------|-------|---------|------|
| 定义 | `.box.def` | 蓝色 `#1d6fa5` | 概念、术语、名词解释 |
| 定理 | `.box.thm` | 紫色 `#7c3aed` | 定理、命题、推论 |
| 公式 | `.box.formula` | 青色 `#0d7d6e` | 重要公式、等式 |
| 例题 | `.box.eg` | 橙色 `#c2640a` | 例题+解答 |
| 警示 | `.box.warn` | 红色 `#c92a2a` | 常见错误、易错点 |
| 技巧 | `.box.tip` | 绿色 `#0b7b5b` | 记忆口诀、学习方法、章节导读 |
| 方法 | `.box.method` | 靛蓝 `#4f46e5` | 解题步骤、操作流程 |

## HTML 模板

### 定义
```html
<div class="box def"><span class="label">定义</span>
<b>样本空间</b>：随机试验 E 的所有可能结果构成的集合，记为 Omega。
</div>
```

### 定理
```html
<div class="box thm"><span class="label">定理（全概率公式）</span>
设 B1, B2, ..., Bn 为样本空间的一个划分，则
$$P(A) = sum_{i=1}^n P(A|B_i)P(B_i)$$
</div>
```

### 公式
```html
<div class="box formula"><span class="label">核心公式（贝叶斯公式）</span>
$$P(B_k|A) = frac{P(A|B_k)P(B_k)}{sum P(A|B_i)P(B_i)}$$
</div>
```

### 例题（含解答区）
```html
<div class="box eg"><span class="label">例题</span>
题目描述...
<div class="sol">解答过程（自动加"解"前缀和虚线分隔）</div>
</div>
```

### 警示
```html
<div class="box warn"><span class="label">易错警示</span>
条件概率 P(A|B) 的分母是 P(B) 不是 P(A)，别搞反。
</div>
```

### 技巧 / 章节导读
```html
<div class="box tip"><span class="label">本章导读</span>
本章是概率论的基础，核心是三个公式。考试必出大题。
</div>
```
标签文字可灵活使用——"本章导读"、"速记技巧"、"使用说明"等。

### 方法
```html
<div class="box method"><span class="label">解题方法</span>
<ol><li>步骤一</li><li>步骤二</li></ol>
</div>
```

## 使用原则

- 每个盒子放**一个主题**，不要多个定理挤一个盒子
- 公式盒优先放**最核心**的公式
- 警示盒直面常见错误，措辞直接（"不要..."、"注意..."）
- 每章开头放一个 tip 盒作为"本章导读"
- 每章结尾放一个 method 盒作为"解题流程总结"

## 辅助标签

```html
<span class="tag-must">必考</span>
<span class="tag-hot">高频</span>
<span class="kbd">CODE</span>
<span class="pill">标签</span>
```
