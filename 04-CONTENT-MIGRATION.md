# 04 -- Content Migration Plan

> How to map every document and photo from `DATA TO SITES/` to the new site.

---

## Document Mapping

### Operating System (BTGOS v1.0)

| Section | Extract | Target Page |
|---|---|---|
| Founder's Letter | Full letter text | About > Our Story, Home hero |
| Mission Statement | Mission + Vision | About > Mission & Vision |
| Core Values | 6 values | About > Mission & Vision |
| Why We Exist | STEM gap paragraph | About > Mission & Vision |
| Theory of Change | Three levers | About > Mission & Vision |
| How We Create Impact | 4 channels | Programs (all subpages) |
| Who We Serve | 5 categories | Home > Who We Serve, Programs > Community Outreach |
| Org Chart | Full structure | About > Leadership Team |
| Director Roles | 9 role descriptions | About > Leadership Team |
| Chapter Program | Lifecycle, application, expectations | Chapters (all pages) |
| Chapter Toolkit | All resources listed | Chapters > Chapter Resources |
| Chapter Expectations | $200/mo, 75 kits, 1 event, reporting | Chapters > Chapter Expectations |
| Fundraising System | All streams | Donate, Partners > Sponsor Packages |
| Operations Systems | Spreadsheets, trackers | Resources > Download Center |

### Blog Writers Introductory Packet

| Section | Extract | Target Page |
|---|---|---|
| Welcome Letter | "You are lowering barriers" | Volunteer > Apply, Blog > About |
| Mission & Values | Accessibility, Equity, Accuracy, Empowerment, Curiosity | About > Mission & Vision |
| Audience | 5 reader categories | Blog > About |
| Content Types | A-E categories | Blog (all category pages) |
| Writing Guidelines | Tone, reading level, length, formatting | Blog > Writing Guidelines |
| Content Standards | Original, accurate, cited | Blog > Writing Guidelines |
| Editorial Process | Pitch -> Approval -> Draft -> Review -> Publish | Blog > For Writers |
| Time Commitment | 1 post/month | Blog > For Writers |
| Writer Benefits | Bylines, mentorship, rec letters | Volunteer > Benefits |

### Blog Post Templates

| Template | Target Page |
|---|---|
| Template 1: Current Developments in STEM | Blog > STEM Explainers, Blog > Current Developments |
| Template 2: Technical How-To | Blog > How-To Guides |

### Fundraising Templates

| Template | Target Page |
|---|---|
| Final Message (Short & Long) | Donate page copy |
| Corporate Sponsorship Letter | Partners > Become a Partner |
| Website Contact Form | Contact page |
| Rotary Club Version | Partners > Community Partners |
| High Tech High Heels Version | Partners > Women in STEM |
| Donate Kits Template | Programs > STEM Kits |
| WhatsApp Messages | Share/distribute on social |
| Bake Sale Outreach | Resources > Fundraising |

### Kits Donation Template

| Content | Target Page |
|---|---|
| Outreach letter | Programs > STEM Kits > Request a Kit |
| Kit descriptions | Programs > STEM Kits (detail) |
| Demo offer | Programs > Robotics Workshops |

### My Impact Challenge

| Section | Target Page |
|---|---|
| Principles Essay | About > Our Story |
| Project Report | Impact > Reports, Home > Featured Story |
| Kit costs ($1.22/$1.83/$5.40) | Donate > Impact Calculator |
| Hospital donations (92 kits) | Impact > Success Stories |
| Frisco Family Services ($300) | Impact > Success Stories |
| Goal: 10 chapters, 2000 kits, $2000 | About > Our Story (vision) |

### Info Hub (Brand Document)

| Section | Target Page |
|---|---|
| Brand Overview | About > Brand (if needed) |
| Problem Statement (25% rural schools lack STEM) | About > Mission & Vision |
| Core Initiatives | Programs hub |
| Previous Events & Deployments | Events > Past Events |
| Partnerships | Partners > Our Partners |
| Visual Identity | Design system (reference) |
| Brand Voice | Content guidelines |
| Leadership | About > Leadership Team |
| Metrics | Home > Impact Dashboard |

### List of Outreaching Done

| Contact | Target Page |
|---|---|
| India Association for North Texas | Partners > Our Partners |
| North South Organization | Partners > Our Partners |
| Frisco Chamber of Commerce | Partners > Our Partners |
| Women Empowering Business | Partners > Our Partners |

### STEM Kit Drive

| Content | Target Page |
|---|---|
| WhatsApp parent template | Resources > Templates |
| Drop-off locations (Frisco TX) | Events > Past Events |
| Donation option | Donate page |

### Message Templates

| Content | Target Page |
|---|---|
| WhatsApp donation message | Donate > Share |

### Idea DUMP

| Idea | Target Page |
|---|---|
| YouTube channel | Resources > Media |
| Educational video series | Resources > Learning Hub |
| Blog with tag filtering | Blog (implementation) |
| Custom kits for 7 disciplines | Programs > STEM Kits |
| School/library partnerships | Programs > School Partnerships |
| Contests | Events > Competitions |

### Advertising Blog Posts Template

| Content | Target Page |
|---|---|
| LinkedIn outreach | Blog > For Writers |
| Email outreach | Blog > For Writers |

### LinkedIn Message Templates

Empty -- no content to migrate.

### Event Kit - Booth Breakdown

Empty -- no content to migrate.

### Event Templates

Empty -- no content to migrate.

---

## Photo Mapping

### Children's Health Donation (5 images)
- Target: Impact > Success Stories, Programs > Community Outreach
- Caption: "STEM kit donation at Children's Health hospital"

### New Year's Kadak Event (20 images)
- Target: Events > Past Events, Impact > Success Stories
- Caption: "New Year's STEM Workshop -- 45 kids built 20 helicopters"
- Best photos: kids building, finished helicopters, group shot

### Robotics Petting Zoo (16 images)
- Target: Events > Past Events, Programs > Robotics Workshops
- Caption: "Robotics Petting Zoo -- hands-on STEM demonstration"

### Scottish Rite Donation (4 images)
- Target: Impact > Success Stories, Programs > Community Outreach
- Caption: "STEM kit donation at Scottish Rite"

### STEM Kit Drive (16 images)
- Target: Events > Past Events, Programs > STEM Kits
- Caption: "STEM Kit Drive -- collecting and distributing kits in Frisco TX"

### Tomorrow's Leaders Today Kit Donation (7 images)
- Target: Impact > Success Stories, Programs > Community Outreach
- Caption: "Kit donation to Tomorrow's Leaders Today program"

### Visuals (2 PNGs)
- Target: Home hero or About page (need to view first)

---

## Image Processing Pipeline

1. Convert all HEIC to WebP (for web)
2. Resize:
   - Hero: 1920x1080
   - Cards: 800x600
   - Gallery: 1200x800
   - Profiles: 400x400
3. Compress: target < 200KB per image
4. Name: `{category}-{event}-{sequence}.webp`

---

## Content Writing Priority

### Must-write first (for launch)
1. Home page copy (hero, programs, impact)
2. About > Mission & Vision (from BTGOS Section 2)
3. About > Our Story (from Founder's Letter)
4. Programs > STEM Kits (from existing kits.html + BTGOS)
5. Donate page (from Fundraising Templates)
6. Contact page (wire to backend)

### Write second (for credibility)
7. Blog: 3-5 initial posts using templates
8. Events: populate past events with photos
9. Impact: 3-5 success stories from My Impact Challenge data
10. Partners: populate partner list from Info Hub metrics

### Write third (for completeness)
11. All remaining About subpages
12. All remaining Program subpages
13. Chapter pages (from BTGOS Sections 6-8)
14. Volunteer pages (from Blog Writers Packet + BTGOS)
15. Resources pages
