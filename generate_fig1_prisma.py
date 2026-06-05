import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

base_path = Path("/Users/kqqs967/Library/CloudStorage/OneDrive-AZCollaboration/CORE/PhD/KC_KSA")

fig, ax = plt.subplots(figsize=(8, 17), dpi=300)
ax.set_xlim(0, 8)
ax.set_ylim(0, 17)
ax.axis('off')

C_HEADER  = '#2E86AB'
C_BODY    = '#EAF4FB'
C_EXCL    = '#F5A623'
C_SPLIT_L = '#3BB273'
C_SPLIT_R = '#E76F51'
C_PERIOD  = '#6A5ACD'   # purple — year-restriction step
C_INCL    = '#5C4B8A'
C_TEXT    = '#1a1a1a'
C_ARROW   = '#444444'
BW, BX, CX = 5.8, 1.1, 4.0

def draw_box(x, y, w, h, header_text, body_lines,
             header_color=C_HEADER, body_color=C_BODY, fontsize=9):
    hh = h * 0.22
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.06",
                                facecolor=body_color, edgecolor='#555',
                                linewidth=1.1, zorder=2))
    ax.add_patch(FancyBboxPatch((x, y + h - hh), w, hh,
                                boxstyle="round,pad=0.06",
                                facecolor=header_color, edgecolor='#555',
                                linewidth=1.1, zorder=3))
    ax.text(x + w/2, y + h - hh/2, header_text,
            ha='center', va='center', fontsize=fontsize,
            fontweight='bold', color='white', zorder=4)
    n = len(body_lines)
    gap = (h - hh) / (n + 1)
    for i, line in enumerate(body_lines):
        ax.text(x + 0.15, y + h - hh - gap * (i + 1),
                line, ha='left', va='center',
                fontsize=fontsize - 0.5, color=C_TEXT, zorder=4)

def arrow_down(x, y_from, y_to):
    ax.annotate('', xy=(x, y_to), xytext=(x, y_from),
                arrowprops=dict(arrowstyle='->', color=C_ARROW,
                                lw=1.6, mutation_scale=14))

def excl_note(y, text):
    """Amber exclusion box anchored to the right edge of the main column."""
    x_start = BX + BW
    x_note  = x_start + 0.15
    ax.annotate(text, xy=(x_note, y), fontsize=7.8, color='#7A4800',
                ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFF3CD',
                          edgecolor=C_EXCL, linewidth=1.0))
    ax.plot([x_start, x_note - 0.05], [y, y],
            color=C_EXCL, lw=1.0, linestyle='--', zorder=3)

# ── Title ─────────────────────────────────────────────────────────────────────
ax.text(4.0, 16.72, 'PRISMA-ScR Flow Diagram:',
        ha='center', va='center', fontsize=10.5,
        fontweight='bold', color=C_TEXT)
ax.text(4.0, 16.38, 'Study Selection and Dataset Construction',
        ha='center', va='center', fontsize=9.5,
        fontstyle='italic', color='#333333')

# ── 1. IDENTIFICATION  (y 13.9 – 15.9) ───────────────────────────────────────
draw_box(BX, 13.9, BW, 2.0, 'IDENTIFICATION',
         ['PubMed records         n = 242',
          'Scopus records         n = 1,281',
          'Combined               n = 1,523'])
arrow_down(CX, 13.9, 13.2)

# ── 2. SCREENING  (y 11.2 – 13.2) ────────────────────────────────────────────
draw_box(BX, 11.2, BW, 2.0, 'SCREENING',
         ['Duplicates removed by DOI     n = 267',
          'Duplicates removed by title   n = 13',
          'After deduplication           n = 1,243'])
excl_note(12.35, 'Duplicates\nn = 280')
arrow_down(CX, 11.2, 10.5)

# ── 3. ELIGIBILITY  (y 8.6 – 10.5) ───────────────────────────────────────────
draw_box(BX, 8.6, BW, 1.9, 'ELIGIBILITY',
         ['Non-Saudi affiliations excluded   n = 876',
          'Records with Saudi affiliation    n = 367'])
excl_note(9.65, 'Non-Saudi\nn = 876')
arrow_down(CX, 8.6, 7.85)

# ── 4. YEAR RESTRICTION  (y 6.8 – 7.85) ─────────────────────────────────────
draw_box(BX, 6.8, BW, 1.05,
         'YEAR RESTRICTION  (2000 – 2025)',
         ['Out-of-period excluded   n = 44  (21 pre-2000 + 23 from 2026)',
          'Records retained         n = 323'],
         header_color=C_PERIOD, body_color='#F0EEF8')
excl_note(7.32, 'Out-of-period\nn = 44')
arrow_down(CX, 6.8, 6.1)

# ── 5. INCLUDED banner  (y 5.82 – 6.1) ───────────────────────────────────────
ax.add_patch(FancyBboxPatch((BX, 5.82), BW, 0.30,
                            boxstyle="round,pad=0.04",
                            facecolor=C_INCL, edgecolor='#333355',
                            linewidth=1.1, zorder=3))
ax.text(CX, 5.97, 'INCLUDED',
        ha='center', va='center', fontsize=9.5,
        fontweight='bold', color='white', zorder=4)

# Horizontal split at y = 5.82
LX, RX = 2.3, 5.7
ax.plot([LX, RX], [5.82, 5.82], color=C_ARROW, lw=1.6, zorder=3)
ax.annotate('', xy=(LX, 3.92), xytext=(LX, 5.82),
            arrowprops=dict(arrowstyle='->', color=C_ARROW,
                            lw=1.6, mutation_scale=14))
ax.annotate('', xy=(RX, 3.92), xytext=(RX, 5.82),
            arrowprops=dict(arrowstyle='->', color=C_ARROW,
                            lw=1.6, mutation_scale=14))

# ── BROAD DATASET  (left, y 0.6 – 3.92) ──────────────────────────────────────
draw_box(0.2, 0.6, 3.9, 3.32,
         'BROAD DATASET  (n = 323)',
         ['All Saudi-affiliated records',
          'retained within study period.',
          '',
          'Used for:',
          '  \u2022 Annual trend analysis',
          '  \u2022 International collaboration',
          '  \u2022 Journal distribution'],
         header_color=C_SPLIT_L, body_color='#EBF7F1')

# ── KC-SPECIFIC DATASET  (right, y 0.6 – 3.92) ───────────────────────────────
draw_box(4.2, 0.6, 3.6, 3.32,
         'KC-SPECIFIC  (n = 99)',
         ['Topic-relevance filter applied.',
          '224 non-KC records excluded.',
          '',
          'Used for:',
          '  \u2022 Institutional analysis',
          '  \u2022 Citation analysis',
          '  \u2022 H-index  (h\u202f=\u202f18)'],
         header_color=C_SPLIT_R, body_color='#FDF2EE')

# Exclusion note off right edge of KC box
ax.annotate('Excluded\nn = 224', xy=(7.95, 2.1),
            fontsize=7.8, color='#7A4800', ha='left', va='center',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFF3CD',
                      edgecolor=C_EXCL, linewidth=1.0))
ax.plot([4.2 + 3.6, 7.9], [2.1, 2.1],
        color=C_EXCL, lw=1.0, linestyle='--', zorder=3)

# ── Save ──────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.3)
for suffix in ('jpg', 'png'):
    out = base_path / f'fig_prisma_flow.{suffix}'
    kwargs = dict(dpi=300, bbox_inches='tight', format=suffix)
    if suffix == 'jpg':
        kwargs['pil_kwargs'] = {'quality': 95}
    plt.savefig(out, **kwargs)
    size_kb = out.stat().st_size / 1024
    flag = '\u2705' if size_kb < 1024 else '\u26a0\ufe0f  EXCEEDS 1024 KB'
    print(f'\u2713 Saved {suffix.upper()}: {out.name}  ({size_kb:.0f} KB) {flag}')
plt.close()
