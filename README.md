# SHIVAS Technology website redesign

Design source for the shivastechnology.com redesign: a division gateway home page,
wire drawing and hot dip galvanizing division pages, a product page template
(pulse-fired furnace), company and group, request a quote, and mobile home.

Live, clickable design canvas: https://claude.ai/artifact/QMyh8SU3Z3QCEZZHJo4d7i

## Contents

| Path | What it is |
| --- | --- |
| `design/*.dc.html` | One file per page (artboard) of the design canvas |
| `design/canvas.json` | Canvas layout: artboard sizes, order and notes |
| `assets/logo/shivas-logo-original.jpg` | Logo as used on the current site |
| `assets/logo/shivas-logo*.png` | Transparent logo cut-outs: full and compact, for light and dark backgrounds |

The `.dc.html` files are Design Component pages. They render inside the design canvas
(images reference the canvas's asset store as `/_blob/...`); they are not a
standalone static site yet.

## Brand palette

| Role | Colour |
| --- | --- |
| Brand red (from the logo), primary buttons, active nav | `#E3000F` |
| Galvanizing gold (molten zinc) | `#FFB400` |
| Wire drawing blue | `#0070AD` |
| Deep navy, headings and dark sections | `#0A1F4D` |
| Body text | `#14213D` |

## Site map and cross-links

- Every page: header nav, red / gold / blue brand stripe, and the same footer site map.
- Every inner page: breadcrumb bar with "Jump to" links into the other division, and a
  "Keep exploring" row of three related pages above the footer.
- Mobile: the menu button opens a full menu of every page, with quote and WhatsApp buttons.

Text in `[brackets]` is a placeholder for real facts or photos.
