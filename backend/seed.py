"""
Seed script — populates PromptVault Pro with realistic demo data.
Run from the backend directory:
    python seed.py
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ── Config ────────────────────────────────────────────────────────────────────

DATABASE_URL = "postgresql+asyncpg://postgres:promptvault_dev@localhost:5432/promptvault"
DEMO_EMAIL   = "demo@promptvault.pro"
DEMO_PASS    = "demo1234"
DEMO_NAME    = "Alex Johnson"

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Prompt data ───────────────────────────────────────────────────────────────

PROMPTS = [
  {
    "title": "Senior Code Reviewer",
    "category": "Coding",
    "tags": ["code-review", "engineering", "security"],
    "quality_score": 94,
    "is_favorite": True,
    "use_count": 47,
    "body": """You are a senior software engineer with 15+ years in production systems.
Review the following code with the eye of a principal engineer doing a pre-merge review.

For each issue provide:
1. Severity (Critical / High / Medium / Low)
2. Location (file + line if known)
3. Problem — what is wrong and why it matters
4. Fix — corrected code or concrete suggestion

After the list:
- Summary score (1–10) with one-sentence justification
- Top 3 things done well
- Single most important change before merging

Code: {{paste_code_here}}

Assume production with 10k+ daily users.""",
    "versions": [
      "Review this code for bugs and security issues: {{code}}",
      "You are a code reviewer. Check this for problems: {{code}}",
    ],
  },
  {
    "title": "Viral LinkedIn Post Generator",
    "category": "Marketing",
    "tags": ["linkedin", "social-media", "personal-brand"],
    "quality_score": 88,
    "is_favorite": True,
    "use_count": 31,
    "body": """You are a top LinkedIn content strategist who has helped executives grow to 100k+ followers.
Write a LinkedIn post about the following that feels authentic, not salesy.

Topic: {{topic_or_story}}
My background: {{role_and_industry}}
Goal: {{awareness / leads / thought_leadership}}

Structure:
- Hook (first line — must stop the scroll)
- Body (3–5 short paragraphs, max 3 lines each)
- Insight or lesson (the "so what")
- CTA (one clear ask)

Tone: conversational but authoritative. No jargon. No "I'm thrilled to announce."
Length: 150–250 words.""",
    "versions": [
      "Write a LinkedIn post about {{topic}}.",
    ],
  },
  {
    "title": "Socratic Tutor for Any Subject",
    "category": "Education",
    "tags": ["tutoring", "learning", "teaching"],
    "quality_score": 91,
    "is_favorite": False,
    "use_count": 22,
    "body": """You are a master Socratic tutor — you never give direct answers, you guide students to discover them.

Subject: {{subject_or_topic}}
Student level: {{beginner / intermediate / advanced}}
Current understanding: {{what_they_know}}

Approach:
1. Assess what the student knows with one open question
2. Identify the core misconception
3. Ask 2–3 targeted questions leading to the insight
4. Affirm correct understanding, then deepen with "What would happen if...?"
5. Never lecture. Hint only after 3 failed guesses.

Begin with: "What do you already know about {{topic}}?\"""",
    "versions": [],
  },
  {
    "title": "Cold Email That Gets Replies",
    "category": "Business",
    "tags": ["sales", "email", "outreach", "copywriting"],
    "quality_score": 92,
    "is_favorite": True,
    "use_count": 58,
    "body": """You are a top-performing SDR with consistently 40%+ reply rates.
Write a cold email for this scenario.

Prospect: {{name}}, {{title}} at {{company}}
Their likely pain: {{pain_point}}
What I offer: {{product_one_line}}
My company: {{your_company}}
Personal hook: {{research_or_connection}}

Rules:
- Subject: under 8 words, no "Quick question" or "Following up"
- Open with the personal hook (1 sentence)
- Name their pain, not your features (1–2 sentences)
- One specific quantified proof point (1 sentence)
- CTA: one low-friction ask
- Total: under 100 words. No bullet points.""",
    "versions": [
      "Write a cold email to {{name}} at {{company}} about {{product}}.",
    ],
  },
  {
    "title": "Executive Summary Writer",
    "category": "Business",
    "tags": ["writing", "executive", "summary", "business"],
    "quality_score": 85,
    "is_favorite": False,
    "use_count": 19,
    "body": """You are a senior business consultant who writes executive summaries for Fortune 500 boards.

Document to summarise: {{paste_document}}
Audience: {{who_will_read_this}}
Key decision needed: {{decision_or_action_required}}

Write an executive summary that:
- Opens with the single most important takeaway (2 sentences max)
- Covers context, findings, and recommendation in 3 short paragraphs
- Uses plain language — no jargon
- Ends with a clear recommended next step
- Total length: 200–300 words""",
    "versions": [],
  },
  {
    "title": "SEO Blog Post Writer",
    "category": "Writing",
    "tags": ["seo", "blog", "content", "writing"],
    "quality_score": 87,
    "is_favorite": False,
    "use_count": 34,
    "body": """You are an expert SEO content strategist and writer.

Topic: {{blog_topic}}
Target keyword: {{primary_keyword}}
Secondary keywords: {{secondary_keywords}}
Target audience: {{audience_description}}
Desired length: {{word_count}} words

Write a fully optimised blog post including:
- SEO-optimised title (under 60 characters)
- Meta description (under 155 characters)
- H2 and H3 subheadings naturally incorporating keywords
- Introduction that hooks with a question or stat
- Body with actionable advice, examples, and data points
- Conclusion with a clear CTA
- Readability: aim for Flesch score 60+""",
    "versions": [
      "Write a blog post about {{topic}} targeting the keyword {{keyword}}.",
      "Write an SEO blog post about {{topic}} for {{audience}}. Include H2s and meta description.",
    ],
  },
  {
    "title": "UX/UI Design Critique",
    "category": "Analysis",
    "tags": ["ux", "design", "critique", "product"],
    "quality_score": 89,
    "is_favorite": False,
    "use_count": 14,
    "body": """You are a senior UX designer with a background in HCI research at top tech companies.

Design to evaluate: {{description_or_screenshot_url}}
Product type: {{web_app / mobile_app / landing_page}}
Target user: {{user_persona}}

Evaluate across:
1. Visual hierarchy — does the eye land where it should?
2. Cognitive load — how many decisions must the user make?
3. Accessibility — contrast, touch targets, screen reader support
4. Conversion path — is the primary CTA obvious?
5. Consistency — does it follow established patterns?

For each area: score /10, key issue, specific fix.
End with the single highest-leverage change to make today.""",
    "versions": [],
  },
  {
    "title": "Python Debugging Assistant",
    "category": "Coding",
    "tags": ["python", "debugging", "errors"],
    "quality_score": 90,
    "is_favorite": False,
    "use_count": 41,
    "body": """You are an expert Python developer and debugger.

Error message: {{paste_error}}
Code context: {{paste_relevant_code}}
What I was trying to do: {{intended_behaviour}}
Python version: {{version}}
Libraries involved: {{libraries}}

Diagnose:
1. Root cause — exactly what went wrong and why
2. Line-by-line explanation of the error traceback
3. Fix — corrected code snippet
4. Prevention — how to avoid this class of bug in future
5. If relevant: suggest a better approach entirely""",
    "versions": [
      "Help me debug this Python error: {{error}}",
    ],
  },
  {
    "title": "Product Requirements Document (PRD)",
    "category": "Business",
    "tags": ["product", "prd", "planning", "specs"],
    "quality_score": 86,
    "is_favorite": True,
    "use_count": 27,
    "body": """You are a senior product manager at a top-tier tech company.

Feature / product to spec: {{feature_description}}
User persona: {{target_user}}
Business goal: {{what_metric_this_moves}}
Constraints: {{technical_or_time_constraints}}

Write a PRD including:
1. Problem statement (1 paragraph)
2. Goals and success metrics (3–5 KPIs)
3. User stories (5–8, in "As a... I want... So that..." format)
4. Functional requirements (bulleted, prioritised MoSCoW)
5. Non-functional requirements (performance, security, accessibility)
6. Out of scope (explicit list)
7. Open questions (3–5 things that need answers before build)""",
    "versions": [],
  },
  {
    "title": "Creative Story Opener",
    "category": "Creative",
    "tags": ["fiction", "creative-writing", "storytelling"],
    "quality_score": 83,
    "is_favorite": False,
    "use_count": 11,
    "body": """You are a bestselling fiction author known for openings that hook readers in the first sentence.

Genre: {{genre}}
Tone: {{dark / hopeful / humorous / tense / whimsical}}
Protagonist: {{brief_character_description}}
Setting: {{time_and_place}}
Central conflict: {{what_the_story_is_about}}
Opening hook style: {{in_media_res / mysterious_statement / striking_image / dialogue}}

Write the opening 3 paragraphs (250–350 words).
Make every sentence earn its place. End on a micro-cliffhanger that demands the reader continue.""",
    "versions": [],
  },
  {
    "title": "Data Analysis Interpreter",
    "category": "Analysis",
    "tags": ["data", "analysis", "insights", "statistics"],
    "quality_score": 88,
    "is_favorite": False,
    "use_count": 23,
    "body": """You are a data scientist and business analyst who translates raw numbers into clear insights.

Dataset / results: {{paste_data_or_summary}}
Business context: {{what_this_data_is_about}}
Audience: {{who_will_read_this_analysis}}
Key question to answer: {{primary_question}}

Provide:
1. Key findings (top 3–5 insights, ranked by business impact)
2. Anomalies or surprises worth investigating
3. Recommended actions based on the data
4. Limitations — what the data cannot tell us
5. Suggested next analysis to run
Use plain language. If a number matters, say why.""",
    "versions": [],
  },
  {
    "title": "Interview Preparation Coach",
    "category": "General",
    "tags": ["interview", "career", "coaching", "job-search"],
    "quality_score": 84,
    "is_favorite": False,
    "use_count": 16,
    "body": """You are an executive career coach who has helped hundreds of candidates land roles at FAANG and top startups.

Role I'm interviewing for: {{job_title}} at {{company}}
My background: {{brief_experience_summary}}
Interview type: {{behavioural / technical / case / panel}}
Areas I'm worried about: {{gaps_or_weaknesses}}

Prepare me by:
1. Predicting the 8 most likely questions for this specific role and company
2. For each: the ideal answer structure (not a scripted answer)
3. The 3 questions I should ask at the end
4. Red flags to avoid
5. One thing that will differentiate me from other candidates""",
    "versions": [],
  },
  {
    "title": "Meeting Agenda & Minutes Writer",
    "category": "Business",
    "tags": ["meetings", "productivity", "writing"],
    "quality_score": 79,
    "is_favorite": False,
    "use_count": 9,
    "body": """You are an executive assistant expert in running efficient meetings.

Meeting purpose: {{purpose}}
Attendees: {{list_of_roles}}
Duration: {{length_in_minutes}}
Context / background: {{relevant_context}}

Generate:
1. Pre-meeting agenda with time allocations for each item
2. Suggested pre-reads or prep for attendees
3. Minutes template (fill-in-the-blank format) with sections for: decisions made, action items (owner + deadline), parking lot
4. Follow-up email template to send after the meeting""",
    "versions": [],
  },
  {
    "title": "Research Paper Summariser",
    "category": "Research",
    "tags": ["research", "academic", "summary", "reading"],
    "quality_score": 90,
    "is_favorite": False,
    "use_count": 18,
    "body": """You are an expert research analyst who distils complex academic papers into actionable insights.

Paper: {{paste_abstract_or_full_paper}}
My background: {{your_field_and_level}}
Why I'm reading this: {{purpose}}

Provide:
1. TL;DR (3 sentences — what they studied, what they found, why it matters)
2. Key findings (top 5, plain language)
3. Methodology summary (how they did it, key limitations)
4. Implications for practice (what someone in my field should do differently)
5. Credibility flags (sample size, conflicts of interest, replication status)
6. Related papers or authors worth exploring""",
    "versions": [],
  },
  {
    "title": "Startup Pitch Deck Narrator",
    "category": "Business",
    "tags": ["startup", "pitch", "fundraising", "investor"],
    "quality_score": 93,
    "is_favorite": True,
    "use_count": 35,
    "body": """You are a former VC partner who has reviewed 3,000+ pitch decks and helped 50+ startups raise seed to Series B.

Startup: {{company_name}}
Product: {{what_it_does_in_one_sentence}}
Stage: {{pre-seed / seed / Series_A}}
Traction: {{key_metrics}}
Ask: {{amount}} for {{what_you'll_do_with_it}}
Competitive landscape: {{main_competitors}}

Write a compelling narrative for each pitch deck slide:
1. Problem (make them feel the pain)
2. Solution (show the magic)
3. Market size (TAM/SAM/SOM with sourced numbers)
4. Business model (clear revenue mechanics)
5. Traction (let the numbers speak)
6. Team (why you, why now)
7. Ask (specific, credible use of funds)

Keep each slide to 3 sentences max. Investors see 1,000 decks a year — every word must earn its place.""",
    "versions": [
      "Write a startup pitch for {{company}} that does {{product}}.",
    ],
  },
  {
    "title": "Grammar & Style Proofreader",
    "category": "Writing",
    "tags": ["proofreading", "grammar", "editing", "writing"],
    "quality_score": 82,
    "is_favorite": False,
    "use_count": 28,
    "body": """You are an expert copy editor with 20 years of experience at top publishing houses.

Text to proofread: {{paste_text}}
Style guide: {{AP / Chicago / APA / house_style / none}}
Tone target: {{formal / conversational / academic / marketing}}
Intended audience: {{audience}}

Provide:
1. Corrected version of the full text (track changes style: mark each edit)
2. Summary of issues found (by category: grammar, style, clarity, tone)
3. The 3 most impactful improvements made
4. Any structural suggestions (flow, paragraph order, missing transitions)
Do not change the author's voice — improve clarity and correctness only.""",
    "versions": [],
  },
  {
    "title": "API Documentation Writer",
    "category": "Coding",
    "tags": ["api", "documentation", "developer", "technical-writing"],
    "quality_score": 86,
    "is_favorite": False,
    "use_count": 12,
    "body": """You are a technical writer specialising in developer documentation for REST APIs.

API endpoint: {{method}} {{endpoint_path}}
What it does: {{description}}
Request parameters: {{params}}
Request body: {{schema}}
Response: {{response_schema}}
Authentication: {{auth_method}}
Error codes: {{error_list}}

Write complete documentation including:
1. Endpoint overview (1 paragraph)
2. Request parameters table (name, type, required, description)
3. Request body example (realistic JSON)
4. Response examples (success + 2 error cases)
5. Code samples in: curl, Python, JavaScript
6. Common gotchas or rate limits""",
    "versions": [],
  },
  {
    "title": "Mental Model Explainer",
    "category": "Education",
    "tags": ["learning", "mental-models", "thinking", "education"],
    "quality_score": 88,
    "is_favorite": False,
    "use_count": 20,
    "body": """You are a master teacher who specialises in making complex ideas simple and memorable.

Concept to explain: {{concept_or_mental_model}}
My background: {{what_i_already_know}}
How I'll use this: {{practical_application}}

Explain in layers:
1. The 5-year-old version (1 analogy, max 3 sentences)
2. The complete explanation (clear, jargon-free, with a concrete example)
3. Where it breaks down (edge cases and failure modes)
4. How it connects to: {{related_concept_1}} and {{related_concept_2}}
5. One exercise to make it stick

End with a memorable one-liner that captures the essence.""",
    "versions": [],
  },
  {
    "title": "Weekly Newsletter Writer",
    "category": "Writing",
    "tags": ["newsletter", "writing", "email", "content"],
    "quality_score": 81,
    "is_favorite": False,
    "use_count": 15,
    "body": """You are a newsletter writer with a loyal readership of 50k+ subscribers.

Newsletter name / brand: {{newsletter_name}}
This week's theme: {{main_topic}}
Content to include: {{list_of_items_links_thoughts}}
Tone: {{casual / professional / opinionated / educational}}
Length: {{short_5min_read / standard_10min / long_form}}

Write the complete newsletter including:
1. Subject line (A/B test: write 3 options)
2. Preview text (under 90 characters)
3. Opening hook (personal, draws readers in)
4. Main content sections with clear headers
5. One curated recommendation (tool, article, or resource)
6. Closing thought + CTA (reply, share, or click)""",
    "versions": [],
  },
  {
    "title": "Competitor Analysis Framework",
    "category": "Research",
    "tags": ["competitive-analysis", "strategy", "research", "business"],
    "quality_score": 87,
    "is_favorite": False,
    "use_count": 21,
    "body": """You are a strategy consultant who has run competitive analyses for 200+ companies.

My company: {{company_and_product}}
Competitors to analyse: {{list_of_competitors}}
Our target customer: {{customer_profile}}
Our key differentiator (current): {{differentiator}}

Analyse each competitor across:
1. Product (features, UX quality, tech stack if known)
2. Positioning (how they describe themselves, messaging)
3. Pricing (tiers, model, value anchoring)
4. Go-to-market (channels, content, partnerships)
5. Strengths and weaknesses vs us

Then:
- Where we are clearly winning
- Where we are losing and why
- One white space opportunity none of them are addressing
- Recommended positioning adjustment""",
    "versions": [],
  },
]

PLATFORMS = ["chatgpt", "claude", "gemini", "perplexity", "copilot", "grok"]

# ── Engine ────────────────────────────────────────────────────────────────────

engine = create_async_engine(DATABASE_URL, echo=False)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def now_utc():
    return datetime.now(timezone.utc)

def days_ago(n):
    return now_utc() - timedelta(days=n)

def rand_date(days_back_max=90):
    return now_utc() - timedelta(
        days=random.randint(0, days_back_max),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

# ── Main seed ─────────────────────────────────────────────────────────────────

async def seed():
    async with SessionFactory() as db:

        # ── 1. Upsert demo user ───────────────────────────────────────────
        result = await db.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": DEMO_EMAIL},
        )
        row = result.fetchone()

        if row:
            user_id = row[0]
            print(f"[OK] User already exists: {DEMO_EMAIL}  (id={user_id})")
        else:
            user_id = uuid4()
            await db.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, display_name, plan, auth_provider)
                    VALUES (:id, :email, :pw, :name, 'free', 'email')
                """),
                {
                    "id": user_id,
                    "email": DEMO_EMAIL,
                    "pw": _pwd.hash(DEMO_PASS),
                    "name": DEMO_NAME,
                },
            )
            print(f"[OK] Created user: {DEMO_EMAIL}  pw={DEMO_PASS}")

        # ── 2. Clear existing seed data for this user ─────────────────────
        await db.execute(text("DELETE FROM ai_refinements WHERE prompt_id IN (SELECT id FROM prompts WHERE user_id = :uid)"), {"uid": user_id})
        await db.execute(text("DELETE FROM prompt_history WHERE user_id = :uid"), {"uid": user_id})
        await db.execute(text("DELETE FROM prompt_versions WHERE prompt_id IN (SELECT id FROM prompts WHERE user_id = :uid)"), {"uid": user_id})
        await db.execute(text("DELETE FROM prompts WHERE user_id = :uid"), {"uid": user_id})
        print("[OK] Cleared old seed data")

        # ── 3. Insert prompts + versions ──────────────────────────────────
        prompt_ids = []
        for i, p in enumerate(PROMPTS):
            pid = uuid4()
            prompt_ids.append(pid)
            created = days_ago(random.randint(5, 80))
            updated = created + timedelta(days=random.randint(0, 5))

            await db.execute(text("""
                INSERT INTO prompts
                    (id, user_id, title, body, category, tags, is_favorite, use_count, quality_score, created_at, updated_at)
                VALUES
                    (:id, :uid, :title, :body, :cat, :tags, :fav, :uses, :score, :created, :updated)
            """), {
                "id":      pid,
                "uid":     user_id,
                "title":   p["title"],
                "body":    p["body"],
                "cat":     p["category"],
                "tags":    p["tags"],
                "fav":     p["is_favorite"],
                "uses":    p["use_count"],
                "score":   p["quality_score"],
                "created": created,
                "updated": updated,
            })

            # Versions
            for v_num, v_body in enumerate(p.get("versions", []), start=1):
                vid = uuid4()
                await db.execute(text("""
                    INSERT INTO prompt_versions (id, prompt_id, body, version_number, created_at)
                    VALUES (:id, :pid, :body, :vnum, :created)
                """), {
                    "id":      vid,
                    "pid":     pid,
                    "body":    v_body,
                    "vnum":    v_num,
                    "created": created + timedelta(hours=v_num * 2),
                })

        print(f"[OK] Inserted {len(PROMPTS)} prompts with versions")

        # ── 4. History — 150 usage records spread over 90 days ───────────
        history_rows = 0
        for pid in prompt_ids:
            # Each prompt used between 4 and 18 times
            uses = random.randint(4, 18)
            for _ in range(uses):
                platform = random.choice(PLATFORMS)
                used_at  = rand_date(90)
                was_refined = random.random() < 0.35

                # fetch body for snapshot
                res = await db.execute(text("SELECT body FROM prompts WHERE id = :pid"), {"pid": pid})
                body_snap = res.scalar()

                await db.execute(text("""
                    INSERT INTO prompt_history
                        (id, user_id, prompt_id, body_snapshot, platform, used_at, was_refined)
                    VALUES
                        (:id, :uid, :pid, :snap, :plat, :used, :refined)
                """), {
                    "id":      uuid4(),
                    "uid":     user_id,
                    "pid":     pid,
                    "snap":    body_snap[:500],
                    "plat":    platform,
                    "used":    used_at,
                    "refined": was_refined,
                })
                history_rows += 1

        print(f"[OK] Inserted {history_rows} history records")

        # ── 5. AI refinements ─────────────────────────────────────────────
        refinement_count = 0
        for pid in random.sample(prompt_ids, min(12, len(prompt_ids))):
            res = await db.execute(text("SELECT body FROM prompts WHERE id = :pid"), {"pid": pid})
            original = res.scalar()

            score_before = random.randint(55, 75)
            score_after  = score_before + random.randint(12, 28)

            await db.execute(text("""
                INSERT INTO ai_refinements
                    (id, prompt_id, original_body, refined_body, style, score_before, score_after, created_at)
                VALUES
                    (:id, :pid, :orig, :refined, :style, :sb, :sa, :created)
            """), {
                "id":      uuid4(),
                "pid":     pid,
                "orig":    original,
                "refined": original + "\n\n[Refined: improved clarity, specificity, and output quality.]",
                "style":   random.choice(["professional", "concise", "detailed", "creative"]),
                "sb":      score_before,
                "sa":      min(score_after, 99),
                "created": rand_date(60),
            })
            refinement_count += 1

        print(f"[OK] Inserted {refinement_count} AI refinements")

        await db.commit()

    print()
    print("-" * 48)
    print("  Seed complete!")
    print(f"  Login:  {DEMO_EMAIL}")
    print(f"  Pass:   {DEMO_PASS}")
    print("-" * 48)

if __name__ == "__main__":
    asyncio.run(seed())
