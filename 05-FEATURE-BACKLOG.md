# 05 -- Feature Backlog

> All features for BTG v2.0, prioritized by phase with effort estimates.

---

## Phase 1: Foundation (Weeks 1-4)

> Get the site live on a modern stack with existing content.

| # | Feature | P | Effort |
|---|---|---|---|
| 1.1 | Initialize Next.js 15 + TypeScript | P0 | S |
| 1.2 | TailwindCSS with BTG purple/amber tokens | P0 | S |
| 1.3 | Project structure (app router, components) | P0 | S |
| 1.4 | Root layout: Navbar + Footer + MobileNav | P0 | M |
| 1.5 | Navbar with mega dropdown ( Programs, About) | P0 | M |
| 1.6 | Footer with newsletter signup | P0 | S |
| 1.7 | Homepage: Hero with photo background + bridge arc | P0 | M |
| 1.8 | Homepage: Impact Dashboard (animated counters) | P0 | M |
| 1.9 | Homepage: Featured Impact Story | P0 | S |
| 1.10 | Homepage: Programs grid (6 cards) | P0 | S |
| 1.11 | Homepage: Who We Serve (from BTGOS Section 2) | P0 | S |
| 1.12 | Homepage: Why BTG (3 columns from Founder's Letter) | P0 | S |
| 1.13 | Homepage: Partner logos scroll | P0 | S |
| 1.14 | Homepage: Testimonials carousel | P0 | M |
| 1.15 | Homepage: Upcoming Events | P0 | S |
| 1.16 | Homepage: Donation section with impact amounts | P0 | S |
| 1.17 | Homepage: Blog preview (latest 3 posts) | P0 | S |
| 1.18 | Migrate Kits page (keep 4 kit cards) | P0 | S |
| 1.19 | Migrate Partners page | P0 | S |
| 1.20 | Migrate Events page | P0 | S |
| 1.21 | Migrate Highlights -> Impact > Success Stories | P0 | S |
| 1.22 | Migrate Blog page | P0 | S |
| 1.23 | Migrate Contact page | P0 | S |
| 1.24 | Migrate Request Kit page | P0 | S |
| 1.24 | Bridge arc SVG component | P0 | S |
| 1.25 | Responsive design pass | P0 | M |
| 1.26 | Image optimization (next/image) | P0 | S |
| 1.27 | Vercel deployment | P0 | S |
| 1.28 | SEO meta tags + Open Graph | P0 | S |

---

## Phase 2: Backend & Integration (Weeks 5-8)

> Wire up the backend, make forms work, add donations.

| # | Feature | P | Effort |
|---|---|---|---|
| 2.1 | Supabase project setup | P0 | S |
| 2.2 | Database schema (all tables from 02-TECHNICAL-ARCHITECTURE.md) | P0 | M |
| 2.3 | Row Level Security policies | P0 | M |
| 2.4 | Supabase Auth (email + Google) | P0 | M |
| 2.5 | Contact form -> Supabase + Resend email | P0 | S |
| 2.6 | Kit Request form -> Supabase + Resend | P0 | S |
| 2.7 | Sanity CMS project setup | P1 | S |
| 2.8 | Sanity schemas (Blog, Events, Resources, Team) | P1 | M |
| 2.9 | Sanity Studio | P1 | S |
| 2.10 | Next.js <-> Sanity connection | P1 | M |
| 2.11 | Hack Club donation integration | P0 | S |
| 2.12 | Donation page with pre-set amounts + impact | P0 | M |
| 2.13 | Donation confirmation email | P0 | S |
| 2.14 | Impact Calculator component | P1 | M |
| 2.15 | Newsletter signup -> Supabase | P1 | S |
| 2.16 | PostHog analytics | P2 | S |
| 2.17 | Google Analytics | P2 | S |

---

## Phase 3: Content Pages (Weeks 9-14)

> Build all new pages, populate from 19 docs + 68 photos.

| # | Feature | P | Effort |
|---|---|---|---|
| 3.1 | About > Mission & Vision (from BTGOS Section 2) | P1 | S |
| 3.2 | About > Our Story (from Founder's Letter + timeline) | P1 | M |
| 3.3 | About > Leadership Team (from BTGOS org chart) | P1 | S |
| 3.4 | About > Advisory Board | P2 | S |
| 3.5 | About > Annual Reports | P2 | S |
| 3.6 | About > Financial Transparency | P1 | M |
| 3.7 | Programs > STEM Kit Donations (from existing + BTGOS) | P1 | S |
| 3.8 | Programs > Robotics Workshops (from BTGOS + events) | P1 | S |
| 3.9 | Programs > School Partnerships (from BTGOS Section 2) | P1 | S |
| 3.10 | Programs > Community Outreach (from outreach list) | P1 | S |
| 3.11 | Programs > Mentorship Program | P1 | S |
| 3.12 | Programs > Chapter Development | P1 | S |
| 3.13 | Impact > Dashboard (animated counters + charts) | P1 | L |
| 3.14 | Impact > Impact Reports | P1 | S |
| 3.15 | Impact > Success Stories (from My Impact Challenge) | P1 | M |
| 3.16 | Impact > Student Spotlights | P2 | M |
| 3.17 | Events > Upcoming Events (with countdown) | P1 | M |
| 3.18 | Events > Past Events (with photo galleries) | P1 | M |
| 3.19 | Events > Event Galleries (masonry grid) | P1 | M |
| 3.20 | Chapters > What is a BTG Chapter? (from BTGOS Section 6) | P1 | S |
| 3.21 | Chapters > Existing Chapters | P1 | S |
| 3.22 | Chapters > Start a Chapter (from BTGOS application process) | P1 | M |
| 3.23 | Chapters > Chapter Resources (from BTGOS toolkit) | P1 | M |
| 3.24 | Chapters > Chapter Expectations (from BTGOS Section 8) | P1 | S |
| 3.25 | Volunteer > Opportunities | P1 | S |
| 3.26 | Volunteer > Roles (from BTGOS org chart) | P1 | S |
| 3.27 | Volunteer > Benefits (from Writer Packet Section 9) | P1 | S |
| 3.28 | Volunteer > Volunteer Stories | P1 | S |
| 3.29 | Volunteer > Apply (multi-step form) | P1 | M |
| 3.30 | Partners > Our Partners (from Info Hub metrics) | P1 | S |
| 3.31 | Partners > Sponsor Packages (from BTGOS Section 9) | P1 | M |
| 3.32 | Partners > Become a Partner (from Fundraising Templates) | P1 | S |
| 3.33 | Blog > Category pages (5 types from Writer Packet) | P1 | M |
| 3.34 | Blog > 5 initial posts (from templates + docs) | P1 | L |
| 3.35 | Blog > For Writers (from Writer Packet) | P1 | S |
| 3.36 | Donate > Sponsor a Kit | P1 | S |
| 3.37 | Donate > Financial Transparency (from BTGOS Section 9) | P1 | S |
| 3.38 | Resources > Learning Hub (from Idea DUMP) | P2 | M |
| 3.39 | Resources > Workshop Materials (from BTGOS toolkit) | P2 | M |
| 3.40 | Resources > Download Center | P2 | M |
| 3.41 | Process all event photos (HEIC -> WebP, resize) | P1 | M |
| 3.42 | Extract text from all 19 .docx files | P1 | M |

---

## Phase 4: Portals & Auth (Weeks 15-22)

> Authenticated portals for volunteers, chapters, sponsors, donors.

| # | Feature | P | Effort |
|---|---|---|---|
| 4.1 | Auth middleware (protect portal routes) | P0 | M |
| 4.2 | User profile page | P0 | S |
| 4.3 | Role-based access (matching BTGOS org chart) | P0 | M |
| 4.4 | Volunteer Portal > Dashboard | P1 | L |
| 4.5 | Volunteer Portal > Hours logging | P1 | M |
| 4.6 | Volunteer Portal > Hours approval (director+) | P1 | M |
| 4.7 | Volunteer Portal > Certificate downloads | P1 | M |
| 4.8 | Volunteer Portal > Badges & levels | P2 | L |
| 4.9 | Volunteer Application form (multi-step) | P1 | L |
| 4.10 | Chapter Portal > Dashboard (chapter metrics) | P1 | L |
| 4.11 | Chapter Portal > Member management | P1 | L |
| 4.12 | Chapter Portal > Event creation/management | P1 | L |
| 4.13 | Chapter Portal > Monthly Report submission | P1 | M |
| 4.14 | Chapter Portal > Resource downloads | P1 | S |
| 4.15 | Chapter Portal > Kit Donation Tracker | P1 | M |
| 4.16 | Chapter Application form (multi-step, from BTGOS) | P1 | L |
| 4.17 | Sponsor Dashboard > Impact reports | P1 | L |
| 4.18 | Sponsor Dashboard > Reach metrics | P1 | M |
| 4.19 | Sponsor Dashboard > Sponsored programs | P1 | M |
| 4.20 | Donor Portal > Donation history | P1 | M |
| 4.21 | Donor Portal > Tax receipts (download) | P1 | M |
| 4.22 | Donor Portal > Impact updates | P1 | S |
| 4.23 | Donor Portal > Recurring donation management | P1 | M |
| 4.24 | Blog Writer Portal > Submit post | P1 | M |
| 4.25 | Blog Writer Portal > Post status tracking | P2 | S |

---

## Phase 5: Advanced Features (Weeks 23-30)

> Polish, analytics, email, gamification, resources.

| # | Feature | P | Effort |
|---|---|---|---|
| 5.1 | Framer Motion page transitions | P2 | M |
| 5.2 | Scroll animations (fade in, slide up) | P2 | M |
| 5.3 | Animated counters on homepage | P1 | S |
| 5.4 | Testimonial carousel (video + quotes) | P2 | M |
| 5.5 | Partner logo scrolling wall | P2 | S |
| 5.6 | Search modal (Cmd+K) | P2 | M |
| 5.7 | Sticky bottom bar (mobile) | P1 | S |
| 5.8 | Mapbox integration (chapter map) | P1 | L |
| 5.9 | Interactive impact map | P1 | L |
| 5.10 | Event countdown timers | P1 | S |
| 5.11 | Email templates for Resend | P1 | M |
| 5.12 | Monthly newsletter automation | P2 | M |
| 5.13 | Donation receipt PDF generation | P1 | M |
| 5.14 | Sponsor report PDF generation | P2 | M |
| 5.15 | Gamification: badge system | P3 | L |
| 5.16 | Resource library: search + filter | P2 | M |
| 5.17 | Blog: RSS feed | P3 | S |
| 5.18 | Sitemap.xml + robots.txt | P1 | S |
| 5.19 | Performance audit + optimization | P1 | M |
| 5.20 | Accessibility audit + fixes | P1 | M |
| 5.21 | Error pages (404, 500) | P1 | S |
| 5.22 | Loading states + skeletons | P2 | M |
| 5.23 | Security review (RLS, auth, API) | P0 | M |

---

## Summary

| Phase | Features | Effort | Weeks |
|---|---|---|---|
| 1: Foundation | 28 | ~3-4 weeks | 1-4 |
| 2: Backend | 17 | ~3-4 weeks | 5-8 |
| 3: Content | 42 | ~5-6 weeks | 9-14 |
| 4: Portals | 25 | ~7-8 weeks | 15-22 |
| 5: Advanced | 23 | ~7-8 weeks | 23-30 |
| **Total** | **135** | **~25-30 weeks** | **~7-8 months** |
