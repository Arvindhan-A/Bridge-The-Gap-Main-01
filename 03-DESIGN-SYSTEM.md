# 03 -- Design System Update Guide

> Based on the real brand identity from `Info Hub.docx` and current CSS.

---

## Brand Identity (from Info Hub.docx)

**Visual Identity:** Purple palette, bridge logo, lowercase wordmark
**Brand Voice:** Accessible, equitable, accurate, empowering, curiosity-driven
**Audience:** Middle/high school students, low-income, first-gen, women & minorities in STEM

---

## Colors

### Current V1 (CSS)
```
--violet-900:   #2C1B4D    (deep purple)
--violet-700:   #4C2A8C
--violet-600:   #5E32A8    (brand purple)
--violet-500:   #7438C9
--violet-100:   #F1EAFB
--amber-500:    #F0A23B    (accent)
--bg:           #FAF8FC
```

### Target V2 (TailwindCSS)

Keep the purple palette (it's your brand). Minor adjustments for better contrast:

```js
// tailwind.config.js
colors: {
  brand: {
    50:  '#FAF8FC',
    100: '#F1EAFB',
    200: '#E0D0F7',
    300: '#C9A8F0',
    400: '#A78BFA',
    500: '#7438C9',
    600: '#5E32A8',
    700: '#4C2A8C',
    800: '#3A1F6E',
    900: '#2C1B4D',
  },
  amber: {
    400: '#F4B763',
    500: '#F0A23B',
  },
  surface: '#FAF8FC',
  ink: '#1E1730',
  slate: '#5C5570',
}
```

**No major color changes.** The purple is established. The amber accent works. Keep it.

---

## Typography

### Current V1
- Display: Space Grotesk 500/600/700
- Body: Inter 400/500/600/700
- Mono: IBM Plex Mono 500

### Target V2

| Role | Font | Change? |
|---|---|---|
| Display | Space Grotesk 700 | **Keep** -- matches "bridge" engineering feel |
| Headings | Space Grotesk 600 | **Keep** |
| Body | Inter 400/500 | **Keep** |
| Mono/Data | IBM Plex Mono 500 | **Keep** |

**No font changes.** The current font stack is solid and matches the brand. Space Grotesk has the right engineering/technical feel for a robotics org.

---

## Components

### Buttons (keep current + add variants)

Current V1 works. Add:
- `btn-lg` -- larger for hero CTAs (padding: 16px 32px)
- `btn-sm` -- smaller for cards (padding: 8px 16px)
- `btn-icon` -- icon-only (square aspect ratio)
- Loading state: spinner replacing text
- Disabled state: opacity 0.5, no pointer

### Cards (keep current + add variants)

Current V1 works. Add:
- `card-featured` -- amber left border accent
- `card-image` -- image at top, content below (for blog posts, events)
- `card-stat` -- large number + label (for impact dashboard)
- `card-donation` -- amount + impact description (for donate page)

### Navigation

Current V1: sticky top, blur backdrop, hamburger on mobile.

Changes:
- Add mega dropdown for Programs, About (multi-column with descriptions)
- Add user icon when logged in (portal access)
- Keep donate button prominent

### Hero

Current V1: radial gradient background, bridge arc SVG, stats rail.

Changes:
- Add photo background option (students building robots) with gradient overlay
- Keep bridge arc as section divider (it's a strong brand element)
- Add trust strip below CTAs

### Forms

Current V1: form-card with rounded inputs.

Changes:
- Add multi-step form component (for applications, chapter requests)
- Add file upload field
- Add validation states (error borders, success checkmarks)
- Add loading/submitting state

### Footer

Current V1: 4-column grid.

Changes:
- Expand to mega-footer (5-6 columns)
- Add newsletter signup inline
- Add social icons
- Keep dark violet background

### Impact Counter

New component. Animated number that counts up on scroll.
Uses Intersection Observer + requestAnimationFrame.

### Testimonial Carousel

New component. Auto-play with pause on hover.
Video-first with fallback to quote cards.

### Event Card

New component. Date badge, title, location, countdown timer, register button.

### Donation Tier Card

New component. Amount, what it provides, select button.
Highlight recommended tier.

### Chapter Card

New component. Name, location, leader, stats, map preview.

---

## Animations (Framer Motion)

### Page Transitions
- Fade in + slight upward slide on page load
- Staggered children (cards, list items)

### Scroll Animations
- Elements fade + slide up when entering viewport
- Counter animation on impact numbers

### Micro-interactions
- Button hover: scale(1.02) + shadow
- Card hover: translateY(-4px) + shadow
- Nav link hover: underline slide in

---

## Responsive Breakpoints

| Name | Width | Current V1 | Target V2 |
|---|---|---|---|
| `sm` | 640px | -- | Phone landscape |
| `md` | 768px | -- | Tablet portrait |
| `lg` | 1024px | hamburger at 860px | hamburger at 1024px |
| `xl` | 1280px | -- | Desktop |
| `2xl` | 1536px | -- | Large desktop |

Mobile changes:
- Sticky bottom bar (Donate, Volunteer, Events, Home) on all screens < 768px
- Cards: 1 col mobile, 2 col tablet, 3-4 col desktop

---

## Accessibility

- All images: descriptive alt text
- Color contrast: >= 4.5:1 (AA)
- Focus visible: amber outline (keep current)
- Skip navigation link
- ARIA labels on icon-only buttons
- Reduced motion: disable animations
- Keyboard navigation: all menus operable
