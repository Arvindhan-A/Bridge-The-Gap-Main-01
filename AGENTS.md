<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Session Context

## Goal
Transform the existing Flask-based BTG Robotics static website into a modern Next.js 16 production platform with chapter management admin panel.

## Constraints & Preferences
- Must use Next.js 16 App Router, TypeScript, TailwindCSS v4, shadcn/ui, Framer Motion
- Design system: brand purple (#7438C9), amber accent (#F0A23B), Space Grotesk (display), Inter (body)
- Chapter presidents can log in and update only their own chapter; super admins see all
- JSON file-based storage for chapters and users (upgradable to Supabase later)
- Route protection via middleware for `/admin/*` (except `/admin/login` and `/admin/api/login`)
- Session management via encrypted cookies with `btg_session` cookie name

## Progress
### Done
- Initialized Next.js 16.2.9 + TypeScript + TailwindCSS v4 project in existing repo
- Installed: framer-motion, lucide-react, class-variance-authority, clsx, tailwind-merge, @radix-ui/* components
- Set up project structure: `src/app/`, `src/components/`, `src/lib/`, `src/types/`, `src/config/`, `src/constants/`
- Created design system tokens in `globals.css` (brand 50-900 palette, amber, fonts, animations)
- Built reusable UI components: Button (with variants), Badge, Card
- Built layout: Navbar (with mega dropdown + mobile hamburger) and Footer
- Built 11-section homepage (Hero, Mission, Impact Dashboard, Founder Note, Who We Serve, Programs Grid, Why BTG, Partner Logos, CTA, Contact)
- Migrated pages: Kits, Partners, Events (reads legacy events.json), Blog (reads legacy posts.json), Blog/[slug], Contact
- Added SEO metadata to all pages, sitemap.xml, robots.txt, custom 404, error boundary
- Created `data/chapters.json` with 3 seed chapters
- Created `data/users.json` with 4 users (1 super_admin + 3 chapter_presidents)
- Built data layer: `src/lib/data/chapters.ts` (CRUD), `src/lib/data/users.ts` (authenticate)
- Built auth system: `src/lib/auth.ts` (createSession/getSession/destroySession)
- Created middleware for route protection
- Built admin layout with sidebar navigation
- Built admin login page at `/admin/login` (with Suspense boundary for useSearchParams)
- Built login API route at `/admin/api/login`
- Built admin dashboard at `/admin` with role-based data visibility
- Built chapter management pages: list (`/admin/chapters`), new (`/admin/chapters/new`), detail (`/admin/chapters/[id]`), edit (`/admin/chapters/[id]/edit`)
- Built `ChapterForm` component with full form fields for all chapter properties
- Built API routes for chapters: POST (`/admin/api/chapters`), PUT (`/admin/api/chapters/[id]`)
- Built public chapters list page (`/chapters`) and detail page (`/chapters/[id]`)
- Built admin logout route (`/admin/logout`)
- Build succeeds with all routes returning 200

### In Progress
- (none)

### Blocked
- (none)

## Key Decisions
- Used JSON file-based storage instead of Supabase initially so the admin panel works immediately without database credentials
- Used route groups (`admin/(main)/`) to separate authenticated admin pages from the login page, avoiding the admin sidebar on the login form
- Session stored in-memory Map with httpOnly cookie — suitable for single-instance dev; needs Redis/DB for production multi-instance
- Chapter presidents can only view/edit their own chapter; super admins have full access — enforced in both server components and layout

## Next Steps
- Phase 2: Backend & Integration — wire up Supabase (Auth + PostgreSQL + Storage), Sanity CMS, contact/donation forms with Resend
- Phase 3: Content Pages — build About (mission, leadership, financials), Programs (workshops, schools, outreach), Impact (stories, reports), Chapters (about, start, resources), Volunteer pages
- Phase 4: Portals & Auth — chapter president portal, volunteer portal, donor portal
- Phase 5: Advanced Features — Mapbox chapter map, PostHog analytics, email notifications

## Critical Context
- Next.js 16.2.9 is installed (not 15), using Turbopack for builds
- TailwindCSS v4 uses `@theme inline` in CSS (not `tailwind.config.js`)
- Lucide-react v1.21.0 does NOT export `Instagram` icon — custom SVG fallback used
- Build output: 20 routes (static + dynamic)
- Admin credentials in `data/users.json`: admin@bridgethegaprobotics.org / btg-admin-2026

## Relevant Files
- `src/app/globals.css`: Design system tokens (brand colors, fonts, animations)
- `src/lib/auth.ts`: Session creation/validation/destruction
- `src/lib/data/chapters.ts`: Chapter CRUD operations (JSON-based)
- `src/lib/data/users.ts`: User authentication
- `src/middleware.ts`: Route protection for `/admin/*`
- `src/app/admin/(main)/layout.tsx`: Admin layout with sidebar
- `src/components/admin/sidebar.tsx`: Admin sidebar navigation component
- `src/components/admin/chapter-form.tsx`: Reusable chapter create/edit form
- `src/app/admin/api/chapters/route.ts`: POST create chapter API
- `src/app/admin/api/chapters/[id]/route.ts`: PUT update chapter API
- `src/app/admin/api/login/route.ts`: Login authentication API
- `src/app/admin/login/page.tsx`: Login page (with Suspense boundary)
- `src/app/admin/logout/route.ts`: Logout route
- `src/app/chapters/page.tsx`: Public chapters listing
- `src/app/chapters/[id]/page.tsx`: Public chapter detail (uses slug)
- `data/chapters.json`: Chapter seed data (3 chapters)
- `data/users.json`: User seed data (4 users)
- `src/app/(main)/page.tsx`: Homepage (11 sections)
- `src/config/site.ts`: Site-wide configuration constants
- `src/constants/index.ts`: Navigation items, stats, programs, partners, kits
- `_legacy/`: Archived Flask app files
