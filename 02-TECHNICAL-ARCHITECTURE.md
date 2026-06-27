# 02 -- Technical Architecture

> Stack, database, auth, payments -- designed around BTG's real organizational structure.

---

## Current Stack

```
Static HTML + CSS + Vanilla JS
  8 files, no backend, no build tools, no deployment
  Forms intercepted by JS (demo only)
```

## Target Stack

```
Next.js 15 (App Router) + TypeScript + TailwindCSS
  |
  +-- Frontend (Vercel)
  +-- Backend (Supabase: PostgreSQL + Auth + Storage)
  +-- CMS (Sanity: blog, events, resources)
  +-- Payments (Hack Club current, Razorpay/Stripe future)
  +-- Email (Resend)
  +-- Analytics (PostHog + GA)
  +-- Maps (Mapbox)
```

---

## Database Schema

Designed around BTG's real operations: chapters, kit donations, events, fundraising, volunteers, blog.

### Core Tables

```sql
-- USERS (Supabase Auth)
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  full_name TEXT,
  email TEXT,
  role TEXT CHECK (role IN (
    'exec_director', 'associate_director', 'director',
    'chapter_president', 'chapter_vp', 'chapter_sec', 'chapter_treasurer',
    'volunteer', 'blog_writer', 'donor', 'sponsor', 'admin'
  )),
  chapter_id UUID REFERENCES chapters(id),
  avatar_url TEXT,
  phone TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- CHAPTERS (from BTGOS Section 6)
CREATE TABLE chapters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  location TEXT,
  country TEXT DEFAULT 'US',
  status TEXT CHECK (status IN ('proposed', 'onboarding', 'active', 'inactive')),
  president_id UUID REFERENCES profiles(id),
  member_count INT DEFAULT 0,
  monthly_fundraising_goal DECIMAL(10,2) DEFAULT 200.00,
  monthly_kits_goal INT DEFAULT 75,
  monthly_events_goal INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- KIT DONATIONS (from BTGOS Section 7 Kit Donation Tracker)
CREATE TABLE kit_donations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id UUID REFERENCES chapters(id),
  donated_by UUID REFERENCES profiles(id),
  recipient_name TEXT,
  recipient_org TEXT,
  recipient_type TEXT CHECK (recipient_type IN (
    'school', 'hospital', 'charity', 'juvenile_center', 'family', 'community', 'other'
  )),
  kit_type TEXT CHECK (kit_type IN (
    'commercial', 'helicopter', 'grabber_arm', 'hydraulic_arm', 'custom', 'other'
  )),
  quantity INT NOT NULL,
  program_type TEXT,
  donation_date DATE DEFAULT CURRENT_DATE,
  notes TEXT,
  photos TEXT[],
  logged_by UUID REFERENCES profiles(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- EVENTS (from BTGOS Section 7 Event Kit)
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  event_type TEXT CHECK (event_type IN (
    'workshop', 'drive', 'camp', 'competition', 'outreach', 'fundraiser', 'booth'
  )),
  event_date TIMESTAMPTZ,
  end_date TIMESTAMPTZ,
  location TEXT,
  chapter_id UUID REFERENCES chapters(id),
  organizer_id UUID REFERENCES profiles(id),
  max_attendees INT,
  current_attendees INT DEFAULT 0,
  status TEXT CHECK (status IN ('planned', 'upcoming', 'ongoing', 'completed', 'cancelled')),
  attendance_sheet_url TEXT,
  photos TEXT[],
  post_event_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- FUNDRAISING (from BTGOS Section 9)
CREATE TABLE fundraising (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id UUID REFERENCES chapters(id),
  fundraiser_id UUID REFERENCES profiles(id),
  amount DECIMAL(10,2) NOT NULL,
  source TEXT CHECK (source IN (
    'donation_drive', 'corporate_sponsorship', 'grant', 'silent_auction',
    'community_fundraising', 'online_crowdfunding', 'individual_donation', 'other'
  )),
  campaign_name TEXT,
  donor_name TEXT,
  donor_email TEXT,
  is_recurring BOOLEAN DEFAULT false,
  payment_id TEXT,
  status TEXT CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
  receipt_url TEXT,
  raised_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- SPONSORS (from BTGOS Section 9 Sponsor Tiers)
CREATE TABLE sponsors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_name TEXT NOT NULL,
  contact_name TEXT,
  contact_email TEXT,
  tier TEXT CHECK (tier IN ('bronze', 'silver', 'gold', 'platinum', 'custom')),
  contribution_total DECIMAL(10,2),
  start_date DATE,
  end_date DATE,
  logo_url TEXT,
  website_url TEXT,
  status TEXT CHECK (status IN ('active', 'pending', 'expired')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- VOLUNTEERS
CREATE TABLE volunteers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  profile_id UUID REFERENCES profiles(id),
  role TEXT CHECK (role IN (
    'stem_mentor', 'instructor', 'kit_assembler', 'content_creator',
    'outreach', 'chapter_lead', 'blog_writer', 'event_helper'
  )),
  status TEXT CHECK (status IN ('active', 'inactive', 'pending')),
  hours_logged DECIMAL(6,1) DEFAULT 0,
  events_attended INT DEFAULT 0,
  badges TEXT[],
  level INT DEFAULT 1,
  applied_at TIMESTAMPTZ DEFAULT NOW()
);

-- MONTHLY IMPACT REPORTS (from BTGOS Section 7/8)
CREATE TABLE monthly_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id UUID REFERENCES chapters(id),
  submitted_by UUID REFERENCES profiles(id),
  report_month TEXT NOT NULL,
  total_kits_donated INT,
  total_funds_raised DECIMAL(10,2),
  events_held INT,
  students_served INT,
  outreach_activities INT,
  challenges TEXT,
  highlights TEXT,
  goals_next_month TEXT,
  photos TEXT[],
  status TEXT CHECK (status IN ('draft', 'submitted', 'reviewed')),
  submitted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- BLOG POSTS (via Sanity, mirrored for queries)
CREATE TABLE blog_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sanity_id TEXT UNIQUE,
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  excerpt TEXT,
  author_id UUID REFERENCES profiles(id),
  category TEXT CHECK (category IN (
    'stem_explainer', 'how_to', 'opportunity_spotlight',
    'personal_pathway', 'current_development', 'event_recap'
  )),
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  featured_image_url TEXT,
  reading_time_minutes INT,
  published BOOLEAN DEFAULT false,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- KIT REQUESTS (from Kits Donation Template)
CREATE TABLE kit_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_name TEXT NOT NULL,
  org_type TEXT CHECK (org_type IN ('school', 'charity', 'hospital', 'juvenile_center', 'other')),
  student_count INT,
  contact_name TEXT,
  contact_email TEXT,
  contact_phone TEXT,
  kit_interest TEXT,
  program_description TEXT,
  status TEXT CHECK (status IN ('pending', 'approved', 'fulfilled', 'denied')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- OUTREACH CONTACTS (from List of Outreaching Done)
CREATE TABLE outreach_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_name TEXT NOT NULL,
  contact_type TEXT CHECK (contact_type IN (
    'school', 'hospital', 'nonprofit', 'corporate', 'community', 'other'
  )),
  contact_name TEXT,
  contact_email TEXT,
  outreach_method TEXT,
  status TEXT CHECK (status IN ('contacted', 'responded', 'partnered', 'declined')),
  chapter_id UUID REFERENCES chapters(id),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RESOURCES
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  category TEXT CHECK (category IN (
    'chapter_toolkit', 'outreach_template', 'fundraising',
    'event_kit', 'curriculum', 'brand', 'reporting'
  )),
  file_url TEXT,
  file_type TEXT,
  download_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Auth Roles (matching BTGOS org chart)

| Role | Access |
|---|---|
| `exec_director` | Full admin, all portals, all data |
| `associate_director` | Most admin, all portals |
| `director` | Department data, relevant portals |
| `chapter_president` | Chapter portal, chapter data, monthly reports |
| `chapter_vp` | Chapter portal, limited management |
| `volunteer` | Volunteer portal, hours logging |
| `blog_writer` | Blog submission, writer portal |
| `donor` | Donor portal, donation history |
| `sponsor` | Sponsor dashboard |

---

## API Routes

```
/api/contact               -- POST, save + email
/api/kit-request           -- POST, save + confirm
/api/volunteer-apply       -- POST, save + confirm
/api/chapter-apply         -- POST, save + send to Chapter Director
/api/blog/submit           -- POST, save draft (auth)
/api/blog/publish          -- POST, publish (editor+)
/api/donation/create       -- POST, create payment
/api/donation/webhook      -- POST, handle confirmation
/api/newsletter/subscribe  -- POST, save email
/api/monthly-report/submit -- POST, chapter report (chapter_president+)
/api/monthly-report/review -- POST, review (director+)
```

---

## Services

| Service | Provider |
|---|---|
| Database + Auth + Storage | Supabase |
| CMS | Sanity |
| Email | Resend |
| Payments | Hack Club (current) |
| Analytics | PostHog + GA |
| Maps | Mapbox |
| Hosting | Vercel |

---

## Performance Targets

| Metric | Target |
|---|---|
| First Contentful Paint | < 1.5s |
| Largest Contentful Paint | < 2.5s |
| Cumulative Layout Shift | < 0.1 |
| Lighthouse Score | > 90 |
| Mobile load time | < 2s |
