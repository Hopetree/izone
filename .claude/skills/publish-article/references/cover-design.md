# Cover Image Design Spec

All covers are 500×300 SVG files, converted to PNG by the server, then resized to 250×150 by imagekit.

## Font Rules (MANDATORY)

**Font family stack** — every `<text>` element must use this exact attribute:

```
font-family="'Noto Sans CJK SC','PingFang SC','Microsoft YaHei',sans-serif"
```

| 字体 | 覆盖环境 | 原因 |
|------|----------|------|
| Noto Sans CJK SC | Linux / Docker 生产 | cairosvg 渲染中文的唯一可用字体，需 `fonts-noto-cjk` apt 包 |
| PingFang SC | macOS 开发 | macOS 系统原生中文字体 |
| Microsoft YaHei | Windows | Windows 系统原生中文字体 |
| sans-serif | 通用回退 | 以上都不可用时的最后兜底 |

> 必须写完整的 4 级回退栈，禁止只用单个字体名。缺失中文回退会导致封面出现乱码。

**Font sizes** — SVG 是 500×300，经 imagekit 缩小后低于 12px 的文字完全不可读。

| 元素 | 最小 | 最大 | 原因 |
|------|------|------|------|
| 主标题 | 36px | 40px | 封面核心信息，必须够大 |
| 描述 | 18px | 18px | 唯一一行副文本，清晰可读 |
| 分类标签 | 14px | 14px | 次要标签，但不能看不清 |
| 图标标签 | 12px | 12px | 最小可用字号，不能再小 |

> 禁止出现 12px 以下的文字，禁止底栏（浪费高度）。用全部 300px 高度承载内容。

## Common Rules (all schemes)

- Never use emoji or unicode symbols — cairosvg cannot render them
- No content cards, code blocks, or complex diagrams
- Title max 2 lines, description max 1 line
- Vary background shade and accent colors each article — never reuse exactly the same palette

---

## Scheme A: Icon Row (default)

A rich cover with geometric icons above the title. Best for technical/tutorial articles with clear themes.

### Layout

```
┌─────────────────────────────────────────────┐
│  ① Glow circles (corners, low opacity)       │
│  ② Top label (pill tag, category keyword)    │
│  ③ Icon row (4 icons, 40×40, each diff color)│
│     label  label  label  label               │
│                                              │
│  ④ Main title (36-40px, bold, 1-2 lines)     │
│  ⑤ Accent line + dot                         │
│  ⑥ Description (18px, one line)              │
└─────────────────────────────────────────────┘
```

### Elements

| # | Element | Detail |
|---|---------|--------|
| ① | Glow | 2 large circles in corners, r=90-110, opacity 0.04-0.06, accent colors |
| ② | Label | Pill rect rx=13, 26px tall, accent gradient fill opacity 0.12, 14px mono text |
| ③ | Icons | 4× `rect` 40×40 rx=9, dark fill + thin stroke, inner geometric paths (1 per icon), 4 different accent colors. 12px label text below each |
| ④ | Title | White, 36-40px, bold (900), letter-spacing 3, centered |
| ⑤ | Line | Short gradient line 1.5px + center dot r=3 |
| ⑥ | Desc | `#94a3b8`, 18px, one line of keywords separated by `·` |

### Example SVG structure

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 300">
  <defs>
    <linearGradient id="bgGrad">...</linearGradient>
    <linearGradient id="accentGrad">...</linearGradient>
  </defs>
  <!-- ① Background + Glow -->
  <rect width="500" height="300" fill="url(#bgGrad)"/>
  <circle cx="420" cy="40" r="100" fill="accent" opacity="0.05"/>
  <circle cx="50" cy="270" r="80" fill="accent2" opacity="0.04"/>

  <!-- ② Label -->
  <rect x="155" y="14" width="190" height="26" rx="13" fill="url(#accentGrad)" opacity="0.12"/>
  <text x="250" y="32" font-size="14" font-family="...">KEYWORD · CATEGORY</text>

  <!-- ③ Icons (4x 40x40) -->
  <g transform="translate(88,46)">...</g>
  ...

  <!-- ④ Title -->
  <text x="250" y="172" font-size="38" font-weight="900" font-family="...">Title Line 1</text>
  <text x="250" y="218" font-size="38" font-weight="900" font-family="...">Title Line 2</text>

  <!-- ⑤ Accent line -->
  <line x1="140" y1="240" x2="360" y2="240" stroke="url(#accentGrad)" stroke-width="1.5"/>
  <circle cx="250" cy="240" r="3" fill="accent"/>

  <!-- ⑥ Description -->
  <text x="250" y="278" font-size="18" fill="#94a3b8" font-family="...">kw1 · kw2 · kw3 · kw4</text>
</svg>
```

---

## Scheme B: Minimal Title

A cleaner, lighter cover with just title and accent. Best for essays, notes, or articles without distinct technical themes.

### Layout

```
┌─────────────────────────────────────────────┐
│  ① Glow circles                              │
│  ② Top label                                 │
│                                              │
│  ③ Main title (40px, bold, centered)         │
│  ④ Accent line + dot                         │
│  ⑤ Description                               │
└─────────────────────────────────────────────┘
```

### Elements

| # | Element | Detail |
|---|---------|--------|
| ① | Glow | Same as Scheme A |
| ② | Label | Same as Scheme A |
| ③ | Title | Larger, 40px, may use 3 words max per line |
| ④ | Line | Same as Scheme A |
| ⑤ | Desc | Same as Scheme A |

No icon row — the extra vertical space goes to larger title and more breathing room.

### When to use

- Personal notes / essays
- Single-topic articles without clear sub-themes
- When the title alone is descriptive enough

---

## Color Palettes

Vary per article. Pick one background shade + 2-3 accent colors.

### Background shades

| Name | Stops | Mood |
|------|-------|------|
| Navy | `#0f172a` → `#1e293b` | General / tech |
| Deep Purple | `#1a0f2e` → `#2d1f4e` | Creative / AI |
| Dark Teal | `#0f1a1f` → `#1a2f33` | DevOps / infra |
| Warm Dark | `#1f1a0f` → `#332d1a` | Home / lifestyle |

### Accent colors

| Color | Hex | Pairs well with |
|-------|-----|-----------------|
| Blue | `#3b82f6` / `#60a5fa` | Indigo, Cyan |
| Indigo | `#8b5cf6` / `#a78bfa` | Cyan, Blue |
| Cyan | `#06b6d4` / `#22d3ee` | Indigo, Green |
| Green | `#10b981` / `#34d399` | Cyan, Amber |
| Amber | `#f59e0b` / `#fbbf24` | Green, Blue |
