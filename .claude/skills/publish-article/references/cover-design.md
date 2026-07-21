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
| ② | Label | Pill rect rx=13, 26px tall, accent gradient fill opacity 0.12, 14px mono text. y≈12 (close to top edge, leaving room for icons below) |
| ③ | Icons | **3-5** × `rect` 40×40 rx=9, dark fill + thin stroke, inner geometric paths. Each icon a different accent color. 12px label text below. Icons must be centered as a group: `x = (500 - n*40) / (n+1) * (i+1) + 40*i` where n=count, i=0-based index. y≈52 |
| ④ | Title | White, 36-40px, bold (900), letter-spacing 3, centered. y≈165 (tight gap from icon labels, ~25px) |
| ⑤ | Line | Short gradient line 1.5px, no dot (same as Scheme B). y≈title_bottom+20 |
| ⑥ | Desc | `#94a3b8`, 18px, one line of keywords separated by `·`. y≈line+30 |

Key spacing: label(18) → gap(8) → icons(52) → icons_bottom(104) → gap(25) → title(165) → gap(20) → line → gap(20) → desc → bottom padding.

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

A cleaner cover with just title and accent. Best for essays, notes, or articles without distinct technical themes.

### Layout

```
┌─────────────────────────────────────────────┐
│  ① Glow circles                              │
│  ② Top label                                 │
│                                              │
│  ③ Main title (44-48px, bold, centered)      │
│  ④ Accent line + dot                         │
│  ⑤ Description                               │
└─────────────────────────────────────────────┘
```

### Elements

| # | Element | Detail |
|---|---------|--------|
| ① | Glow | Same as Scheme A |
| ② | Label | Same as Scheme A. y≈18 |
| ③ | Title | **44-48px**, bold (900), letter-spacing 3, centered. y≈155 — the freed icon space goes entirely to larger title |
| ④ | Line | Short gradient line 1.5px, **no center dot** (cleaner than Scheme A). y≈title_bottom+20 |
| ⑤ | Desc | Same as Scheme A. y≈line+30 |

No icon row — title grows from 38px to 46px and shifts upward to fill the space. The entire content block (label + title + line + desc) is vertically centered in the 300px canvas.

### When to use

- Personal notes / essays
- Single-topic articles without clear sub-themes
- When the title alone is descriptive enough

---

## Scheme C: Grid Network (preferred)

**Default scheme.** A tech-forward cover with a grid mesh, glowing nodes, and neural-network-style connection lines. Best for most article types — AI, deep tech, infrastructure, tutorials, and general technical content.

### Layout

```
┌─────────────────────────────────────────────┐
│  ① Grid overlay (50px grid, gradient opacity)│
│  ② Glowing nodes at grid intersections       │
│  ③ Connection lines between nodes            │
│  ④ Central highlight rectangle               │
│  ⑤ Main title (34px, bold, indigo tint)      │
│  ⑥ Subtitle (22px, lighter indigo)           │
│  ⑦ Bottom hashtag tags (13px)                │
└─────────────────────────────────────────────┘
```

### Elements

| # | Element | Detail |
|---|---------|--------|
| ① | Grid | 50px grid lines, `stroke="url(#gridLine)"`, opacity fades from 0.3 at edges to 0.08 at center |
| ② | Nodes | 8-12 small circles (r=2.5) at grid intersections, accent color, opacity 0.8 |
| ③ | Lines | 8-12 connections between nodes. Mix of straight lines and curved bezier paths (`<path d="M... Q..."/>`). Accent color, stroke 0.5-0.8, opacity 0.2-0.4. Vary routing to look organic — a real neural network, not a grid of straight lines. |
| ④ | Center glow | Subtle highlight behind title area, `fill="accent" opacity="0.06-0.10"`. Use irregular shapes — rounded rect with uneven rx, rotated ellipse, or two overlapping offset rects. Never a perfect centered rectangle; slight asymmetry adds visual interest. Size: ~300-380 wide, ~100-130 tall. |
| ⑤ | Title | 36-38px, bold (900), `#e0d4ff`, centered, letter-spacing 4. y≈125 |
| ⑥ | Subtitle | 20-22px, semi-bold (600), accent-400, centered, letter-spacing 2. y≈title+45 |
| ⑦ | Tags | `#` separated keywords, 13px, accent-700, centered. y≈260 |

**Vertical centering**: Unlike the reference, content must fill the 300px canvas. Title at y≈125, subtitle at y≈170, tags at y≈260. Grid and nodes cover the full canvas — no empty top half.

### Background gradient

Darker and more dramatic than Scheme A/B. Stops lean toward deep purple/indigo:

```svg
<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="#0a0a1a"/>
  <stop offset="100%" stop-color="#1a0a2e"/>
</linearGradient>
```

### Grid line gradient

Fades from edges toward center for depth:

```svg
<linearGradient id="gridLine" x1="0" y1="0" x2="0" y2="300">
  <stop offset="0%" stop-color="accent" stop-opacity="0.3"/>
  <stop offset="50%" stop-color="accent" stop-opacity="0.08"/>
  <stop offset="100%" stop-color="accent" stop-opacity="0.3"/>
</linearGradient>
```

### Subtitle format

Unlike Scheme A/B's one-line keyword description, Scheme C uses a longer subtitle that reads as a sentence or phrase — like a magazine deck. This fills the space between the large title and the bottom tags.

### Color variants (per palette)

Scheme C must vary colors per article using the palette system. Each palette maps to specific fill/stroke values:

| Element | Maps to | Example (Nebula) |
|---------|---------|------------------|
| Background gradient | Palette bg stops | `#0a0a1a` → `#1a0a2e` |
| Grid lines | accent-500 at low opacity | `#7c3aed` |
| Nodes | accent-400, opacity 0.8 | `#8b5cf6` |
| Connection lines | accent-400, opacity 0.3 | `#8b5cf6` |
| Center rect | accent-500, opacity 0.08 | `#7c3aed` |
| Title text | `#ffffff` (pure white, same as Scheme A/B) | `#ffffff` |
| Subtitle text | accent-300 | `#ab8cf3` → varies |
| Tags text | accent-600 (darker for readability) | `#7c3aed` → varies |

**Color mapping for each palette:**

| Palette | Grid/Node | Title | Subtitle | Tags |
|----------|-----------|-------|----------|------|
| Ocean | `#4b8bf1` / `#3b82f6` | `#ffffff` | `#8bb3f4` | `#2563eb` |
| Nebula | `#7d4bf1` / `#8b5cf6` | `#ffffff` | `#ab8cf3` | `#7c3aed` |
| Forest | `#51ecb8` / `#10b981` | `#ffffff` | `#8ff0cf` | `#059669` |
| Sunset | `#f2b54a` / `#f59e0b` | `#ffffff` | `#f4cd8a` | `#d97706` |
| Aurora | `#48daf4` / `#06b6d4` | `#ffffff` | `#89e5f5` | `#0891b2` |
| Slate | `#959ba7` / `#6b7280` | `#ffffff` | `#babec4` | `#4b5563` |
| Earth | `#f5a447` / `#d97706` | `#ffffff` | `#f6c388` | `#b45309` |

The grid aesthetic stays consistent; only the colors change per article.

### When to use

- AI / deep tech / infrastructure articles
- Tutorials and technical guides
- Any article where the grid/network aesthetic fits the content
- **Default** — use unless the article clearly calls for Scheme A or B

---

## Color & Background

Vary both palette and background style per article. Never reuse the same combination twice in a row.

### Color Palettes (7 themes, WCAG verified)

All backgrounds pass 15:1+ contrast with white text. Generated from brand hex using HSL shade scale.

| # | Name | Brand | Background Stops | Accent 400 | Accent 300 | Accent 200 | Mood |
|---|------|-------|-----------------|------------|------------|------------|------|
| 1 | Ocean | `#3B82F6` | `#000529` → `#02184b` | `#4b8bf1` | `#8bb3f4` | `#c4d8f7` | 技术 / 后端 |
| 2 | Nebula | `#8B5CF6` | `#160029` → `#1e024b` | `#7d4bf1` | `#ab8cf3` | `#d4c5f7` | AI / 创新 |
| 3 | Forest | `#10B981` | `#012824` → `#044837` | `#51ecb8` | `#8ff0cf` | `#c6f5e6` | DevOps / 运维 |
| 4 | Sunset | `#F59E0B` | `#292400` → `#4b3601` | `#f2b54a` | `#f4cd8a` | `#f8e5c4` | 笔记 / 生活 |
| 5 | Aurora | `#06B6D4` | `#001829` → `#003a4c` | `#48daf4` | `#89e5f5` | `#c3f0f8` | 全栈 / 前端 |
| 6 | Slate | `#6B7280` | `#111118` → `#21242c` | `#959ba7` | `#babec4` | `#dbdde1` | 工具 / 效率 |
| 7 | Earth | `#D97706` | `#292000` → `#4d2f00` | `#f5a447` | `#f6c388` | `#f9e0c3` | NAS / 硬件 |

**How to use**:
- **Icon background**: Always `#1e293b` (neutral dark slate).
- **Icon colors**: Each icon gets a DIFFERENT accent color. Do NOT reuse the same accent for multiple icons in one cover. Pull from the full accent pool below — mix across palettes to get 3-5 distinct colors per cover.
- **Icon labels**: Uniform color — use the current palette's accent-300 for all labels. Labels do NOT follow the icon colors; they stay consistent across the row.
- **Label gradient + glow**: Use the current palette's accent-300 and accent-400.

**Accent color pool** (pick 3-5 distinct colors per cover, one per icon):

| Color | Hex | Tone |
|-------|-----|------|
| Blue | `#4b8bf1` | Cool, tech |
| Indigo | `#7d4bf1` | Rich, creative |
| Cyan | `#48daf4` | Fresh, modern |
| Green | `#51ecb8` | Natural, stable |
| Amber | `#f2b54a` | Warm, friendly |
| Rose | `#fb7185` | Vibrant, bold |
| Slate | `#959ba7` | Neutral, tool-like |

**Per-cover selection rule**: Pick 3-5 colors from the pool for the icon row. The background palette suggests which colors feel most natural (e.g. Ocean→Blue+Cyan, Nebula→Indigo+Rose, Forest→Green+Amber), but the exact mix varies per article. Never use fewer than 3 distinct icon colors.

### Background Styles (rotate between these)

#### Style 1: Diagonal Gradient (default)

The standard diagonal gradient. Angle varies slightly each time.

```svg
<linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="start"/>
  <stop offset="100%" stop-color="end"/>
</linearGradient>
```

#### Style 2: Horizontal Split

Top half lighter, bottom half darker. Adds a subtle horizon line.

```svg
<linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="start"/>
  <stop offset="40%" stop-color="start"/>
  <stop offset="100%" stop-color="end"/>
</linearGradient>
<!-- Optional: subtle line at the split point -->
<line x1="0" y1="120" x2="500" y2="120" stroke="accent" stroke-width="0.5" opacity="0.08"/>
```

#### Style 3: Radial Burst

Gradient radiates from a corner, creating a spotlight effect.

```svg
<radialGradient id="bgGrad" cx="30%" cy="20%" r="80%">
  <stop offset="0%" stop-color="lighter_variant"/>
  <stop offset="100%" stop-color="end"/>
</radialGradient>
```

#### Style 4: Geometric Accent

Diagonal gradient + 1-2 subtle geometric shapes (large low-opacity triangles or rectangles).

```svg
<!-- Diagonal gradient bg -->
<rect width="500" height="300" fill="url(#bgGrad)"/>
<!-- Subtle geometric overlay -->
<polygon points="500,0 500,200 300,300" fill="accent1" opacity="0.04"/>
<circle cx="450" cy="250" r="150" fill="accent2" opacity="0.03"/>
```

#### Style 5: Dot Grid

Gradient with a faint dot pattern overlay for a tech/dashboard feel.

```svg
<pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse">
  <circle cx="8" cy="8" r="0.8" fill="#ffffff" opacity="0.06"/>
</pattern>
<rect width="500" height="300" fill="url(#bgGrad)"/>
<rect width="500" height="300" fill="url(#dots)"/>
```

### Choosing

1. Pick a **palette** based on article category/tone
2. Pick a **background style**, rotate through them (don't use same style twice in a row)
3. Pick 2-3 **accent colors** from the palette for icons and label
