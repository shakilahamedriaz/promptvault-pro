"""
Seed script for marketplace — creates users, published prompts, and ratings.
Run from the backend directory:
    python seed_marketplace.py
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:promptvault_dev@localhost:5432/promptvault"

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
engine = create_async_engine(DATABASE_URL, echo=False)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

def now_utc():
    return datetime.now(timezone.utc)

def days_ago(n):
    return now_utc() - timedelta(days=n)

# ─── Content Creators ─────────────────────────────────────────────────────────

CREATORS = [
    {"email": "sarah@promptvault.pro", "name": "Sarah Chen", "password": "demo1234"},
    {"email": "james@promptvault.pro", "name": "James Wilson", "password": "demo1234"},
    {"email": "emma@promptvault.pro", "name": "Emma Rodriguez", "password": "demo1234"},
    {"email": "alex@promptvault.pro", "name": "Alex Kim", "password": "demo1234"},
    {"email": "lisa@promptvault.pro", "name": "Lisa Thompson", "password": "demo1234"},
    {"email": "michael@promptvault.pro", "name": "Michael Chen", "password": "demo1234"},
    {"email": "priya@promptvault.pro", "name": "Priya Patel", "password": "demo1234"},
    {"email": "david@promptvault.pro", "name": "David Johnson", "password": "demo1234"},
    {"email": "sophia@promptvault.pro", "name": "Sophia Martinez", "password": "demo1234"},
    {"email": "carlos@promptvault.pro", "name": "Carlos Garcia", "password": "demo1234"},
]

# ─── Published Prompts (Marketplace Data) ─────────────────────────────────────

PUBLISHED_PROMPTS = [
    {
        "title": "Senior Code Reviewer",
        "description": "Get expert code review feedback from a principal engineer perspective, covering security, architecture, and best practices.",
        "category": "Coding",
        "tags": ["code-review", "engineering", "security"],
        "quality_score": 94,
        "use_count": 142,
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop",
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
        "ratings": [5, 5, 5, 4, 5, 5, 4, 4, 5],
        "creator_idx": 0,
    },
    {
        "title": "Viral LinkedIn Post Generator",
        "description": "Create authentic, scroll-stopping LinkedIn posts that drive engagement and build your personal brand.",
        "category": "Marketing",
        "tags": ["linkedin", "social-media", "personal-brand"],
        "quality_score": 88,
        "use_count": 98,
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop",
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
        "ratings": [5, 5, 4, 5, 5],
        "creator_idx": 1,
    },
    {
        "title": "Cold Email That Gets Replies",
        "description": "Write high-converting cold emails with proven SDR techniques for 40%+ reply rates.",
        "category": "Business",
        "tags": ["sales", "email", "outreach", "copywriting"],
        "quality_score": 92,
        "use_count": 156,
        "image_url": "https://images.unsplash.com/photo-1557821552-17105176677c?w=400&h=300&fit=crop",
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
        "ratings": [5, 5, 5, 5, 4, 5, 5],
        "creator_idx": 2,
    },
    {
        "title": "SEO Blog Post Writer",
        "description": "Generate SEO-optimized blog posts that rank on Google with proper keyword targeting and high readability.",
        "category": "Writing",
        "tags": ["seo", "blog", "content", "writing"],
        "quality_score": 87,
        "use_count": 67,
        "image_url": "https://images.unsplash.com/photo-1455849318169-8149e8e04b2f?w=400&h=300&fit=crop",
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
        "ratings": [4, 4, 5, 4, 4, 4],
        "creator_idx": 3,
    },
    {
        "title": "UX/UI Design Critique",
        "description": "Get expert feedback on your design's hierarchy, accessibility, cognitive load, and conversion path.",
        "category": "Design",
        "tags": ["ux", "design", "critique", "product"],
        "quality_score": 89,
        "use_count": 43,
        "image_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop",
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
        "ratings": [5, 4, 5, 5],
        "creator_idx": 4,
    },
    {
        "title": "Python Debugging Assistant",
        "description": "Get expert Python debugging help with root cause analysis, error explanations, and prevention strategies.",
        "category": "Coding",
        "tags": ["python", "debugging", "errors"],
        "quality_score": 90,
        "use_count": 124,
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop",
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
        "ratings": [5, 5, 4, 5, 5, 5, 5, 5],
        "creator_idx": 0,
    },
    {
        "title": "Startup Pitch Deck Narrator",
        "description": "Get VC-backed compelling narratives for each pitch deck slide written by an experienced investor.",
        "category": "Business",
        "tags": ["startup", "pitch", "fundraising", "investor"],
        "quality_score": 93,
        "use_count": 87,
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop",
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
        "ratings": [5, 5, 5, 5, 5, 5],
        "creator_idx": 1,
    },
    {
        "title": "Mental Model Explainer",
        "description": "Learn complex concepts through layered explanations, analogies, and practical exercises.",
        "category": "Education",
        "tags": ["learning", "mental-models", "thinking"],
        "quality_score": 88,
        "use_count": 54,
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop",
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
        "ratings": [5, 4, 5, 5, 4],
        "creator_idx": 2,
    },
    {
        "title": "Data Analysis Interpreter",
        "description": "Transform raw data into actionable business insights with anomaly detection and recommendations.",
        "category": "Analysis",
        "tags": ["data", "analysis", "insights", "statistics"],
        "quality_score": 86,
        "use_count": 62,
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
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
        "ratings": [4, 4, 5, 4, 4],
        "creator_idx": 3,
    },
    {
        "title": "API Documentation Writer",
        "description": "Create comprehensive API documentation with request/response examples and error handling guides.",
        "category": "Coding",
        "tags": ["api", "documentation", "developer"],
        "quality_score": 85,
        "use_count": 41,
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop",
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
        "ratings": [4, 4, 4, 4, 3],
        "creator_idx": 4,
    },
    {
        "title": "Cinematic Product Photography Prompt",
        "description": "Generate stunning product photography prompts for DALL-E, Midjourney, or Stable Diffusion with professional lighting and composition.",
        "category": "Image Generation",
        "tags": ["image-generation", "product-photography", "midjourney", "dalle"],
        "quality_score": 92,
        "use_count": 203,
        "image_url": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=400&h=300&fit=crop",
        "body": """You are a professional product photographer and AI art director specializing in e-commerce and luxury product visualization.

Product: {{product_name}}
Style: {{style: cinematic / minimalist / luxury / lifestyle / editorial}}
Lighting: {{lighting: studio / natural / moody / golden-hour}}
Camera angle: {{angle: overhead / 45-degrees / close-up / wide-shot}}
Background: {{background: white / studio-wall / natural-setting / abstract}}
Brand aesthetic: {{brand_description}}
Color mood: {{color_palette}}

Generate a detailed DALL-E 3 / Midjourney / Stable Diffusion prompt that includes:
1. Product description with material textures and finish
2. Lighting setup (key light, fill light, rim light positions)
3. Camera specifications (lens type, aperture, depth of field)
4. Background and environment details
5. Color grading and mood
6. Composition rule of thirds with specific placement
7. Professional photography quality descriptors (4K, sharp, award-winning)

Output a ready-to-use prompt for image generation AI.""",
        "ratings": [5, 5, 5, 5, 5, 5],
        "creator_idx": 0,
    },
    {
        "title": "Fantasy Art Concept Illustrator",
        "description": "Create detailed fantasy and concept art prompts for generating epic illustrations, character designs, and world-building visuals.",
        "category": "Image Generation",
        "tags": ["fantasy-art", "character-design", "concept-art", "worldbuilding"],
        "quality_score": 90,
        "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1579783902614-e3fb5141b0cb?w=400&h=300&fit=crop",
        "body": """You are a legendary concept artist and fantasy world-builder for AAA game studios and film productions.

Character/Scene: {{subject}}
Setting: {{fantasy_world_description}}
Art style: {{style: oil-painting / digital-art / manga / cyberpunk / steampunk}}
Mood: {{mood: epic / mysterious / dark / whimsical / dramatic}}
Character role: {{character_class_or_profession}}
Color palette: {{dominant_colors}}

Create a professional concept art prompt including:
1. Detailed character/creature/environment description
2. Anatomy and proportion notes
3. Clothing, armor, or architectural details with materials
4. Lighting and atmosphere
5. Color palette and mood
6. Art style reference (name specific artists if relevant)
7. Composition guidelines
8. Resolution and quality specs (8K, ultra-detailed, trending on ArtStation)

Include dynamic pose suggestions and environmental storytelling elements.""",
        "ratings": [5, 5, 5, 4, 5, 5],
        "creator_idx": 1,
    },
    {
        "title": "UI/UX Design Mockup Generator",
        "description": "Generate detailed prompts for creating app interfaces, website designs, and digital product mockups with perfect layouts.",
        "category": "Design",
        "tags": ["ui-design", "ux-mockup", "web-design", "app-design"],
        "quality_score": 88,
        "use_count": 145,
        "image_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop",
        "body": """You are a world-class UI/UX designer who has designed interfaces for Fortune 500 companies and successful startups.

Product: {{product_name}}
Type: {{type: mobile-app / web-app / desktop-app / landing-page}}
Use case: {{primary_user_task}}
Platform: {{iOS / Android / Web / Cross-platform}}
Design system: {{design_system_or_reference}}

Create a comprehensive mockup prompt including:
1. Information architecture (wireframe layout)
2. Component specifications (buttons, inputs, cards)
3. Typography hierarchy and font sizes
4. Color scheme and accessibility requirements
5. Spacing and padding systems
6. Navigation structure
7. Loading states and interactions
8. Dark mode considerations
9. Responsive breakpoints

Format as a detailed design brief that could be handed to a designer or AI image generator.""",
        "ratings": [5, 4, 5, 5, 4],
        "creator_idx": 2,
    },
    {
        "title": "Social Media Content Calendar Strategist",
        "description": "Plan and organize 30-day social media content strategies with posting schedules, hashtags, and engagement tactics.",
        "category": "Marketing",
        "tags": ["social-media", "content-strategy", "instagram", "tiktok"],
        "quality_score": 85,
        "use_count": 178,
        "image_url": "https://images.unsplash.com/photo-1460925895917-aeb19be489c7?w=400&h=300&fit=crop",
        "body": """You are a social media strategist who has grown multiple accounts to 500K+ followers using data-driven content strategies.

Brand: {{brand_name}}
Platforms: {{platforms: Instagram / TikTok / YouTube / LinkedIn}}
Content pillars: {{3-5_content_themes}}
Target audience: {{demographic_and_psychographic}}
Monthly goal: {{specific_goal: followers / engagement / sales}}

Create a 30-day content calendar including:
1. Daily posting schedule with optimal times
2. Content themes and pillar rotation
3. Hashtag strategy (mix of reach, medium, niche)
4. Engagement tactics and community management
5. Trending audio/sounds/effects to leverage
6. Cross-platform content repurposing strategy
7. Partnership and collaboration ideas
8. Analytics benchmarks to track
9. Caption templates for consistency
10. Content creation checklist and asset requirements""",
        "ratings": [5, 5, 4, 5, 5],
        "creator_idx": 3,
    },
    {
        "title": "Landscape Photography Mood Creator",
        "description": "Generate AI prompts for breathtaking landscape, nature, and travel photography with perfect lighting and composition.",
        "category": "Photography",
        "tags": ["landscape-photography", "nature-photography", "travel", "dall-e"],
        "quality_score": 87,
        "use_count": 134,
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=300&fit=crop",
        "body": """You are a master landscape photographer with award-winning nature photography published in National Geographic.

Location: {{location_or_terrain}}
Season: {{spring / summer / autumn / winter / any}}
Time of day: {{golden-hour / blue-hour / midday / midnight}}
Weather: {{clear / stormy / foggy / rainy}}
Subject: {{mountains / ocean / forest / desert / urban}}
Mood: {{serene / dramatic / ethereal / majestic}}

Generate a professional landscape photography prompt:
1. Geographic and geological details
2. Flora and fauna elements
3. Weather and atmospheric conditions
4. Specific lighting conditions with color temperature
5. Camera equipment recommendations (lens, aperture, ISO)
6. Composition using rule of thirds and leading lines
7. Foreground, middle ground, background elements
8. Colors and mood-setting details
9. Photography technique specifications
10. Quality descriptors (award-winning, published, museum-quality)

Include references to famous landscape photographers or specific photography styles.""",
        "ratings": [5, 5, 5, 5, 4, 5],
        "creator_idx": 4,
    },
    {
        "title": "Character Voice & Personality Developer",
        "description": "Develop detailed character personalities, voices, speech patterns, and backstories for writing, games, and content creation.",
        "category": "Writing",
        "tags": ["character-development", "creative-writing", "storytelling", "voice"],
        "quality_score": 89,
        "use_count": 98,
        "image_url": "https://images.unsplash.com/photo-1505228395891-9a51e7e86e81?w=400&h=300&fit=crop",
        "body": """You are a master story architect and character development specialist who has created beloved characters for bestselling novels and games.

Character name: {{character_name}}
Role: {{hero / villain / sidekick / mentor}}
Genre: {{fantasy / sci-fi / contemporary / horror / romance}}
Setting: {{world_or_time_period}}
Primary traits: {{3-5_key_traits}}
Conflicts: {{internal_and_external_conflicts}}

Develop a comprehensive character profile including:
1. Physical description with distinctive features
2. Speech patterns and unique vocabulary
3. Personality type and Myers-Briggs assessment
4. Motivations and core values
5. Fears and insecurities
6. Skills and expertise
7. Relationships and dynamics with other characters
8. Backstory and formative experiences
9. Character arc and growth trajectory
10. Dialogue examples in their voice
11. Quirks and mannerisms
12. Emotional triggers and reactions

Provide voice guidance for actors or AI voice synthesis.""",
        "ratings": [5, 5, 4, 5, 5],
        "creator_idx": 0,
    },
    {
        "title": "Video Script & Storyboard Master",
        "description": "Create compelling video scripts, shot lists, and storyboards for YouTube, TikTok, commercials, and film productions.",
        "category": "Writing",
        "tags": ["video-script", "storyboard", "youtube", "film-production"],
        "quality_score": 91,
        "use_count": 122,
        "image_url": "https://images.unsplash.com/photo-1485579149c0-123dd79885d5?w=400&h=300&fit=crop",
        "body": """You are a Emmy-nominated screenwriter and video director who has created viral content and award-winning commercials.

Title: {{video_title}}
Platform: {{YouTube / TikTok / Instagram / TV Commercial / Film}}
Duration: {{15s / 30s / 60s / 3min / 10min / feature}}
Target audience: {{audience_description}}
Goal: {{entertainment / education / sales / awareness}}
Tone: {{funny / inspiring / dramatic / educational / emotional}}

Create a complete video production blueprint:
1. Hook (first 3 seconds that stop the scroll)
2. Scene-by-scene breakdown with shot descriptions
3. Camera movements and angles
4. Dialogue and voiceover script
5. Music and sound design notes
6. Visual effects and transitions
7. Storyboard descriptions (one per scene)
8. Props and location requirements
9. Talent and actor directions
10. Color grading mood
11. Pacing and timing breakdown
12. Call-to-action and closing

Include shot list with cinematography specifications.""",
        "ratings": [5, 5, 5, 5, 4, 5],
        "creator_idx": 1,
    },
    {
        "title": "Machine Learning Training Data Optimizer",
        "description": "Design and structure training datasets, annotation strategies, and data pipelines for machine learning models.",
        "category": "Coding",
        "tags": ["machine-learning", "ai", "data-science", "training-data"],
        "quality_score": 88,
        "use_count": 76,
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
        "body": """You are a machine learning engineer and data scientist who has trained models at DeepMind, OpenAI, and leading AI labs.

Model task: {{task: classification / detection / segmentation / generation}}
Data type: {{images / text / audio / time-series / tabular}}
Model architecture: {{architecture_type}}
Dataset size target: {{number_of_samples}}
Use case: {{production_use_case}}
Budget/constraints: {{compute_budget_and_constraints}}

Provide comprehensive data strategy:
1. Dataset composition and distribution requirements
2. Data collection methodology
3. Annotation guidelines and quality assurance
4. Data augmentation strategies
5. Handling class imbalance
6. Train/validation/test split strategy
7. Data cleaning and preprocessing pipeline
8. Outlier detection and anomaly handling
9. Privacy and bias mitigation techniques
10. Labeling efficiency techniques (active learning)
11. Data versioning and tracking system
12. Performance metrics for data quality

Include specific tools and frameworks (PyTorch, TensorFlow, Hugging Face).""",
        "ratings": [5, 4, 5, 4, 4, 5],
        "creator_idx": 2,
    },
    # ── Coding ────────────────────────────────────────────────────────────────
    {
        "title": "React Component Architect",
        "description": "Design reusable, accessible React components with TypeScript, proper prop types, and Storybook documentation.",
        "category": "Coding",
        "tags": ["react", "typescript", "component", "frontend"],
        "quality_score": 91, "use_count": 189,
        "image_url": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400&h=300&fit=crop",
        "body": """You are a senior React engineer specializing in design systems and component libraries.

Component name: {{component_name}}
Purpose: {{what_it_does}}
Props needed: {{prop_list}}
Variants: {{variant_list}}
Accessibility requirements: {{a11y_needs}}

Deliver:
1. Full TypeScript component with proper interface/types
2. Default props and prop validation
3. Variants using clsx or similar
4. ARIA attributes and keyboard navigation
5. CSS/Tailwind styling
6. JSDoc comments
7. Usage example
8. Storybook story outline""",
        "ratings": [5, 5, 4, 5, 5, 4], "creator_idx": 5,
    },
    {
        "title": "SQL Query Optimizer",
        "description": "Analyze and optimize slow SQL queries with index suggestions, execution plan analysis, and rewrite strategies.",
        "category": "Coding",
        "tags": ["sql", "database", "performance", "optimization"],
        "quality_score": 93, "use_count": 211,
        "image_url": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400&h=300&fit=crop",
        "body": """You are a database performance expert with deep knowledge of PostgreSQL, MySQL, and query optimization.

Query: {{paste_query}}
Database: {{postgresql / mysql / sqlite}}
Table sizes: {{approximate_row_counts}}
Current execution time: {{time_ms}}
Indexes available: {{index_list}}

Analyze and provide:
1. Execution plan breakdown (EXPLAIN ANALYZE interpretation)
2. Bottleneck identification
3. Index recommendations with CREATE INDEX statements
4. Rewritten optimized query
5. Before/after performance estimate
6. Caching strategy if applicable
7. Schema changes to consider long-term""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 6,
    },
    {
        "title": "REST API Design Blueprint",
        "description": "Design complete RESTful APIs with proper resource naming, HTTP methods, status codes, and OpenAPI spec.",
        "category": "Coding",
        "tags": ["api", "rest", "backend", "design"],
        "quality_score": 89, "use_count": 156,
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=300&fit=crop",
        "body": """You are a backend architect who has designed APIs used by millions of developers.

Product/feature: {{describe_the_domain}}
Resources: {{list_main_entities}}
Authentication: {{jwt / oauth / api_key}}
Special requirements: {{pagination / filtering / versioning}}

Design complete REST API:
1. Resource hierarchy and URL structure
2. All endpoints (CRUD + custom actions)
3. HTTP methods and status codes for each
4. Request/response schemas with examples
5. Error response format
6. Pagination strategy
7. Filtering and sorting parameters
8. Rate limiting headers
9. OpenAPI 3.0 spec snippet
10. Security considerations""",
        "ratings": [5, 4, 5, 5, 4], "creator_idx": 7,
    },
    {
        "title": "Docker & Kubernetes Setup Guide",
        "description": "Create production-ready Dockerfiles, docker-compose configs, and Kubernetes manifests for your application.",
        "category": "Coding",
        "tags": ["docker", "kubernetes", "devops", "deployment"],
        "quality_score": 90, "use_count": 143,
        "image_url": "https://images.unsplash.com/photo-1667372393119-3d4c48d07fc9?w=400&h=300&fit=crop",
        "body": """You are a DevOps engineer and cloud architect with expertise in containerization and orchestration.

Application: {{app_description}}
Language/runtime: {{nodejs / python / go / java}}
Services needed: {{database / redis / queue}}
Environment: {{dev / staging / production}}
Cloud provider: {{aws / gcp / azure / self_hosted}}

Generate:
1. Optimized multi-stage Dockerfile (minimal image size)
2. docker-compose.yml for local development
3. .dockerignore file
4. Kubernetes Deployment manifest
5. Kubernetes Service and Ingress
6. ConfigMap and Secret templates
7. Health check configuration
8. Resource limits and autoscaling rules
9. CI/CD pipeline snippet""",
        "ratings": [5, 5, 4, 5, 5, 4], "creator_idx": 8,
    },
    {
        "title": "Unit Test Generator",
        "description": "Write comprehensive unit tests with edge cases, mocks, and high code coverage for any codebase.",
        "category": "Coding",
        "tags": ["testing", "unit-tests", "jest", "pytest"],
        "quality_score": 88, "use_count": 178,
        "image_url": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400&h=300&fit=crop",
        "body": """You are a test-driven development expert who writes bulletproof test suites.

Code to test: {{paste_function_or_class}}
Framework: {{jest / pytest / mocha / junit}}
Coverage target: {{percentage}}

Write tests covering:
1. Happy path with valid inputs
2. Edge cases (empty, null, boundary values)
3. Error cases and exception handling
4. Async operations if applicable
5. Mock setup for external dependencies
6. Parameterized tests for data variations
7. Setup/teardown hooks
8. Integration test suggestions
9. Snapshot tests where relevant
10. Coverage report interpretation""",
        "ratings": [5, 4, 5, 5, 5], "creator_idx": 9,
    },
    {
        "title": "Git Workflow & Branch Strategy",
        "description": "Design team Git workflows, branching strategies, commit message conventions, and PR review processes.",
        "category": "Coding",
        "tags": ["git", "workflow", "team", "version-control"],
        "quality_score": 86, "use_count": 98,
        "image_url": "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=400&h=300&fit=crop",
        "body": """You are an engineering manager and Git workflow expert for large engineering teams.

Team size: {{number_of_developers}}
Release cadence: {{daily / weekly / sprint}}
Deployment type: {{continuous / scheduled}}
Current pain points: {{merge_conflicts / slow_reviews / broken_main}}

Design complete Git strategy:
1. Branching model (GitFlow / trunk-based / GitHub flow)
2. Branch naming conventions
3. Commit message format (conventional commits)
4. PR template and checklist
5. Code review guidelines
6. Merge vs rebase policy
7. Tagging and versioning strategy
8. Hotfix process
9. Release branch workflow
10. CI/CD integration points""",
        "ratings": [5, 4, 4, 5, 4, 4], "creator_idx": 5,
    },
    {
        "title": "GraphQL Schema Designer",
        "description": "Design efficient GraphQL schemas with queries, mutations, subscriptions, and resolver patterns.",
        "category": "Coding",
        "tags": ["graphql", "api", "schema", "backend"],
        "quality_score": 87, "use_count": 112,
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=300&fit=crop",
        "body": """You are a GraphQL architect who has built high-performance APIs at scale.

Domain: {{business_domain}}
Entities: {{list_of_entities}}
Relationships: {{how_entities_relate}}
Real-time needs: {{yes / no}}
Auth model: {{public / user / role_based}}

Design complete GraphQL schema:
1. Type definitions for all entities
2. Queries with arguments, pagination, filtering
3. Mutations with input types
4. Subscriptions for real-time features
5. Custom scalars
6. Enums and unions
7. Resolver strategy and DataLoader patterns
8. Error handling approach
9. Schema stitching notes if needed
10. Performance considerations (N+1 problem)""",
        "ratings": [5, 5, 4, 5, 4], "creator_idx": 6,
    },
    {
        "title": "Code Refactoring Advisor",
        "description": "Analyze legacy code and provide a step-by-step refactoring plan to improve readability, performance, and maintainability.",
        "category": "Coding",
        "tags": ["refactoring", "clean-code", "legacy", "architecture"],
        "quality_score": 92, "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=400&h=300&fit=crop",
        "body": """You are a software architect specializing in modernizing legacy codebases.

Code to refactor: {{paste_code}}
Language: {{language}}
Current problems: {{what_is_wrong}}
Constraints: {{cannot_change_x_because_y}}

Provide refactoring plan:
1. Code smell identification with locations
2. SOLID principle violations
3. Priority order (high impact, low risk first)
4. Step-by-step refactoring guide
5. Refactored code snippets
6. Design pattern suggestions
7. Test strategy before refactoring
8. Risk assessment per change
9. Performance improvement estimates""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 7,
    },

    # ── Writing ───────────────────────────────────────────────────────────────
    {
        "title": "Technical Documentation Writer",
        "description": "Write clear, developer-friendly technical documentation, README files, and wikis that actually get read.",
        "category": "Writing",
        "tags": ["documentation", "technical-writing", "readme", "developer"],
        "quality_score": 88, "use_count": 134,
        "image_url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400&h=300&fit=crop",
        "body": """You are a technical writer who has authored documentation for major open-source projects.

Project: {{project_name}}
What it does: {{brief_description}}
Target audience: {{developers / non-technical / both}}
Sections needed: {{installation / api / examples / faq}}

Write documentation including:
1. Hero section with elevator pitch
2. Quick start (under 5 minutes to first success)
3. Installation instructions (all platforms)
4. Configuration reference
5. Core concepts explained simply
6. API reference with examples
7. Troubleshooting section
8. Contributing guide
9. Changelog format
10. Badges and shields""",
        "ratings": [5, 4, 5, 4, 5], "creator_idx": 8,
    },
    {
        "title": "Newsletter Writer That Converts",
        "description": "Write email newsletters with high open rates, click-through rates, and conversion using proven copywriting formulas.",
        "category": "Writing",
        "tags": ["newsletter", "email-marketing", "copywriting", "conversion"],
        "quality_score": 90, "use_count": 198,
        "image_url": "https://images.unsplash.com/photo-1455849318169-8149e8e04b2f?w=400&h=300&fit=crop",
        "body": """You are an email copywriter with a portfolio of newsletters that regularly hit 40%+ open rates.

Newsletter name: {{newsletter_name}}
Topic/theme: {{this_issue_topic}}
Audience: {{subscriber_description}}
Goal: {{inform / sell / nurture / entertain}}
Tone: {{professional / casual / witty}}

Write complete newsletter:
1. Subject line (3 options, A/B testable)
2. Preview text (50 chars max)
3. Opening hook (first sentence that demands a read)
4. Body sections with subheadings
5. Story or case study
6. Key takeaway or insight
7. CTA (one clear action)
8. P.S. line (often most read part)
9. Estimated read time
10. Engagement question for replies""",
        "ratings": [5, 5, 5, 5, 4, 5], "creator_idx": 9,
    },
    {
        "title": "Press Release Writer",
        "description": "Write newsworthy press releases that get picked up by journalists and media outlets.",
        "category": "Writing",
        "tags": ["press-release", "pr", "media", "journalism"],
        "quality_score": 87, "use_count": 76,
        "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop",
        "body": """You are a PR specialist who has placed stories in TechCrunch, Forbes, and major national publications.

Company: {{company_name}}
Announcement: {{what_are_you_announcing}}
Why it matters: {{the_bigger_story}}
Quote source: {{spokesperson_name_and_title}}
Release date: {{embargo_date_or_immediate}}

Write press release including:
1. Headline (under 100 chars, news-driven)
2. Dateline
3. Lead paragraph (who, what, when, where, why)
4. Supporting paragraphs with data/context
5. Executive quote (natural, not corporate)
6. Customer or partner quote if relevant
7. Boilerplate (about the company)
8. Media contact information
9. ### end marker
10. Pitch email to accompany the release""",
        "ratings": [4, 5, 4, 5, 4], "creator_idx": 5,
    },
    {
        "title": "Short Story Generator",
        "description": "Create engaging short stories with compelling characters, plot twists, and vivid settings across any genre.",
        "category": "Writing",
        "tags": ["fiction", "short-story", "creative-writing", "storytelling"],
        "quality_score": 89, "use_count": 145,
        "image_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=400&h=300&fit=crop",
        "body": """You are a published short story author with work in literary magazines and anthologies.

Genre: {{thriller / romance / sci-fi / horror / literary}}
Setting: {{time_and_place}}
Protagonist: {{character_description}}
Core conflict: {{what_they_want_vs_what_opposes_them}}
Tone: {{dark / hopeful / humorous / suspenseful}}
Word count: {{500 / 1000 / 2000}}

Write a complete short story with:
1. Opening line that hooks immediately
2. Vivid setting established in 2-3 sentences
3. Character with a clear want and flaw
4. Rising tension and complications
5. Midpoint reversal or revelation
6. Climax scene
7. Resolution (satisfying but not predictable)
8. Resonant final line
Use sensory details, subtext-rich dialogue, and show-don't-tell throughout.""",
        "ratings": [5, 5, 4, 5, 5, 5], "creator_idx": 6,
    },
    {
        "title": "Grant Proposal Writer",
        "description": "Write compelling grant proposals for nonprofits, researchers, and organizations that stand out to funders.",
        "category": "Writing",
        "tags": ["grant-writing", "nonprofit", "fundraising", "proposal"],
        "quality_score": 91, "use_count": 89,
        "image_url": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=400&h=300&fit=crop",
        "body": """You are a grant writer with a 70% funding success rate across government, foundation, and corporate grants.

Organization: {{org_name_and_mission}}
Project: {{what_you_want_to_do}}
Amount requested: {{dollar_amount}}
Funder: {{foundation_or_agency_name}}
Timeline: {{project_duration}}
Impact metrics: {{how_you_measure_success}}

Write grant proposal:
1. Executive summary (1 page max)
2. Organizational background and credibility
3. Needs statement with supporting data
4. Project description and methodology
5. Goals, objectives, and outcomes
6. Evaluation plan
7. Budget narrative justification
8. Sustainability plan
9. Appendix items list
10. Cover letter""",
        "ratings": [5, 4, 5, 5, 4], "creator_idx": 7,
    },
    {
        "title": "Book Chapter Outliner",
        "description": "Outline non-fiction and fiction book chapters with structure, key points, pacing, and narrative arc.",
        "category": "Writing",
        "tags": ["book-writing", "outline", "nonfiction", "structure"],
        "quality_score": 86, "use_count": 112,
        "image_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=300&fit=crop",
        "body": """You are a developmental editor who has worked with bestselling authors at major publishing houses.

Book title/concept: {{book_concept}}
Type: {{nonfiction / fiction / memoir}}
Target reader: {{audience}}
Chapter topic: {{this_chapter_focus}}
Chapter position: {{chapter_number_of_total}}

Create chapter outline:
1. Chapter title and subtitle options
2. Opening hook or scene
3. Core argument or narrative thread
4. Section-by-section breakdown (H2 level)
5. Key stories, examples, or data points for each section
6. Transitions between sections
7. Chapter summary or takeaway
8. Bridge to next chapter
9. Sidebars, callouts, or exercises
10. Word count breakdown by section""",
        "ratings": [5, 4, 4, 5, 4, 4], "creator_idx": 8,
    },

    # ── Marketing ─────────────────────────────────────────────────────────────
    {
        "title": "Google Ads Copy Generator",
        "description": "Write high-converting Google Ads with compelling headlines, descriptions, and CTAs that maximize ROAS.",
        "category": "Marketing",
        "tags": ["google-ads", "ppc", "ad-copy", "sem"],
        "quality_score": 91, "use_count": 234,
        "image_url": "https://images.unsplash.com/photo-1460925895917-aeb19be489c7?w=400&h=300&fit=crop",
        "body": """You are a Google Ads specialist who manages $2M+ in monthly ad spend across multiple industries.

Product/service: {{what_you_are_advertising}}
Target keyword: {{primary_keyword}}
Landing page URL: {{url}}
USP: {{unique_selling_point}}
Offer: {{discount / free_trial / guarantee}}
Competitor weakness: {{what_competitors_miss}}

Generate Responsive Search Ad:
1. 15 headlines (30 chars max each, keyword-rich)
2. 4 descriptions (90 chars max, benefit-focused)
3. Display path suggestions
4. Ad extensions (sitelinks, callouts, structured snippets)
5. 3 ad variations for A/B testing
6. Negative keyword suggestions
7. Quality Score improvement tips""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 9,
    },
    {
        "title": "Product Hunt Launch Copy",
        "description": "Write Product Hunt launch copy that drives upvotes, maker posts, and community engagement on launch day.",
        "category": "Marketing",
        "tags": ["product-hunt", "launch", "startup", "growth"],
        "quality_score": 88, "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=400&h=300&fit=crop",
        "body": """You are a growth marketer who has launched 20+ products on Product Hunt, multiple reaching #1 Product of the Day.

Product name: {{name}}
Tagline: {{one_liner}}
What it does: {{description}}
Key features: {{top_3_features}}
Target user: {{who_benefits_most}}
Launch date: {{date}}

Create launch package:
1. Headline (under 60 chars, intriguing)
2. Tagline (punchy, benefit-driven)
3. Product description (150 words)
4. Maker's comment (first comment, personal story)
5. 5 hunter outreach messages
6. 10 community questions to spark discussion
7. Gallery image copy suggestions
8. First-week follow-up strategy
9. Upvote request message templates""",
        "ratings": [5, 5, 4, 5, 4], "creator_idx": 5,
    },
    {
        "title": "Influencer Outreach Campaign",
        "description": "Design influencer marketing campaigns with outreach scripts, briefs, and tracking frameworks for any budget.",
        "category": "Marketing",
        "tags": ["influencer-marketing", "ugc", "brand-partnerships", "social"],
        "quality_score": 85, "use_count": 123,
        "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop",
        "body": """You are an influencer marketing director who has run campaigns for major DTC brands.

Brand: {{brand_name}}
Product: {{product_description}}
Budget: {{total_budget}}
Platform: {{instagram / tiktok / youtube}}
Goal: {{awareness / conversions / ugc_content}}
Target audience: {{demographic}}

Design campaign:
1. Influencer tier strategy (nano/micro/macro split)
2. Ideal influencer profile and criteria
3. Outreach email template (cold)
4. Creative brief template
5. Compensation structure options
6. Contract key terms
7. Content approval process
8. Tracking links and UTM strategy
9. Performance metrics and KPIs
10. Reporting template""",
        "ratings": [5, 4, 4, 5, 4, 4], "creator_idx": 6,
    },
    {
        "title": "Brand Voice & Tone Guide",
        "description": "Define your brand's voice, tone, personality, and messaging framework for consistent communication across channels.",
        "category": "Marketing",
        "tags": ["brand-voice", "brand-identity", "messaging", "copywriting"],
        "quality_score": 92, "use_count": 156,
        "image_url": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=400&h=300&fit=crop",
        "body": """You are a brand strategist who has defined voice and tone for Fortune 500 companies and beloved startups.

Company: {{company_name}}
Industry: {{industry}}
Target audience: {{audience_description}}
Brand personality adjectives: {{3_to_5_words}}
Competitors: {{list_competitors}}
Differentiator: {{what_makes_you_different}}

Create brand voice guide:
1. Brand personality archetypes (primary + secondary)
2. Voice characteristics (with do/don't examples)
3. Tone variations by channel and context
4. Word and phrase glossary (use / avoid / never)
5. Writing style rules
6. Punctuation and formatting preferences
7. Example copy rewrites (before/after)
8. Competitor voice differentiation
9. Voice checklist for content reviews
10. Onboarding guide for new writers""",
        "ratings": [5, 5, 5, 5, 5, 4], "creator_idx": 7,
    },
    {
        "title": "Facebook Ads Funnel Builder",
        "description": "Build complete Facebook/Instagram ad funnels with TOF/MOF/BOF copy, audiences, and retargeting sequences.",
        "category": "Marketing",
        "tags": ["facebook-ads", "meta-ads", "funnel", "retargeting"],
        "quality_score": 89, "use_count": 201,
        "image_url": "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?w=400&h=300&fit=crop",
        "body": """You are a Meta Ads strategist managing $500K+ monthly ad budgets for e-commerce and SaaS brands.

Product: {{product_description}}
Price point: {{price}}
Target customer: {{ideal_customer_profile}}
Current ROAS goal: {{target_roas}}
Funnel stage to focus: {{TOF / MOF / BOF / all}}

Build complete ad funnel:
1. TOF awareness ads (3 hooks × 2 formats)
2. MOF consideration ads (social proof + benefit)
3. BOF conversion ads (offer + urgency)
4. Retargeting sequences (1-day, 7-day, 30-day)
5. Lookalike audience strategy
6. Interest targeting clusters
7. Creative format recommendations (image/video/carousel)
8. Ad copy for each stage
9. Budget allocation percentages
10. Scaling indicators and triggers""",
        "ratings": [5, 5, 4, 5, 5], "creator_idx": 8,
    },
    {
        "title": "App Store Optimization (ASO) Expert",
        "description": "Optimize your app store listing with keyword-rich titles, descriptions, and screenshot copy to drive organic downloads.",
        "category": "Marketing",
        "tags": ["aso", "app-store", "mobile-app", "organic-growth"],
        "quality_score": 87, "use_count": 143,
        "image_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&h=300&fit=crop",
        "body": """You are an ASO specialist who has grown apps to millions of downloads through organic optimization.

App name: {{app_name}}
Category: {{app_category}}
Primary function: {{what_app_does}}
Target keywords: {{keyword_list}}
Platform: {{iOS / Android / both}}

Optimize listing:
1. Title (30 chars, keyword + brand)
2. Subtitle/short description (keyword-rich)
3. Full description (keyword-natural, benefit-led)
4. Keyword field (iOS — 100 chars)
5. Screenshot captions sequence (first 3 are critical)
6. Feature graphic copy (Android)
7. Review response templates
8. A/B test suggestions for icons/screenshots
9. Localization priority list
10. Competitor keyword gap analysis""",
        "ratings": [5, 4, 5, 4, 4, 5], "creator_idx": 9,
    },

    # ── Business ──────────────────────────────────────────────────────────────
    {
        "title": "Business Plan Executive Summary",
        "description": "Write a compelling executive summary that opens doors with investors, banks, and strategic partners.",
        "category": "Business",
        "tags": ["business-plan", "executive-summary", "investor", "strategy"],
        "quality_score": 93, "use_count": 178,
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=300&fit=crop",
        "body": """You are a business consultant who has helped 200+ companies secure funding and partnerships.

Business name: {{business_name}}
Industry: {{industry}}
Product/service: {{what_you_sell}}
Stage: {{idea / MVP / revenue / scaling}}
Funding needed: {{amount_and_purpose}}
Traction: {{key_metrics_to_date}}

Write executive summary:
1. Opening hook (the opportunity in one sentence)
2. Problem statement with market evidence
3. Solution description
4. Business model and revenue streams
5. Market size (TAM/SAM/SOM)
6. Competitive advantage (moat)
7. Traction and milestones achieved
8. Team credentials
9. Financial highlights (revenue, growth rate, unit economics)
10. The ask and use of funds
Keep to one page, investor-ready language.""",
        "ratings": [5, 5, 5, 5, 4, 5], "creator_idx": 5,
    },
    {
        "title": "Meeting Agenda & Facilitator Guide",
        "description": "Design productive meeting agendas with clear objectives, time blocks, pre-work, and follow-up frameworks.",
        "category": "Business",
        "tags": ["meetings", "productivity", "facilitation", "leadership"],
        "quality_score": 85, "use_count": 212,
        "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop",
        "body": """You are an executive coach and organizational effectiveness expert.

Meeting type: {{standup / strategy / retrospective / decision / kickoff}}
Participants: {{number_and_roles}}
Duration: {{minutes}}
Desired outcome: {{specific_decision_or_output}}
Known tensions: {{any_conflicting_interests}}

Create meeting package:
1. Agenda with timed blocks
2. Pre-read materials list
3. Opening activity (2-min alignment exercise)
4. Facilitation questions per agenda item
5. Decision-making framework to use
6. Parking lot template
7. Note-taking structure
8. Action item template (owner, deadline, measure)
9. Post-meeting survey questions
10. Follow-up email template""",
        "ratings": [5, 4, 5, 4, 5, 4], "creator_idx": 6,
    },
    {
        "title": "OKR Framework Builder",
        "description": "Create effective Objectives and Key Results (OKRs) for teams and organizations that drive measurable outcomes.",
        "category": "Business",
        "tags": ["okr", "goal-setting", "strategy", "management"],
        "quality_score": 90, "use_count": 189,
        "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400&h=300&fit=crop",
        "body": """You are a management consultant and OKR coach who has implemented OKRs at Google, Intel, and 50+ companies.

Company/team: {{organization_name}}
Mission: {{company_mission_statement}}
Quarter: {{Q1 / Q2 / Q3 / Q4}} {{year}}
Strategic priorities: {{top_3_company_priorities}}
Team focus area: {{team_responsibility}}

Design OKR framework:
1. Company-level Objectives (3 max)
2. Key Results for each (3-5 per Objective, measurable)
3. Team-level Objectives that ladder up
4. Team Key Results (quantified, time-bound)
5. Initiative ideas to achieve each KR
6. Check-in cadence and scoring guide
7. Common mistakes to avoid
8. OKR grading rubric (0.0-1.0 scale)
9. Retrospective questions for end of cycle
10. Communication template to share with team""",
        "ratings": [5, 5, 4, 5, 5], "creator_idx": 7,
    },
    {
        "title": "Negotiation Strategy Planner",
        "description": "Prepare for high-stakes negotiations with BATNA analysis, opening positions, concession strategies, and scripts.",
        "category": "Business",
        "tags": ["negotiation", "strategy", "salary", "deals"],
        "quality_score": 91, "use_count": 134,
        "image_url": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=400&h=300&fit=crop",
        "body": """You are a negotiation expert trained at Harvard and with experience in M&A, procurement, and labor negotiations.

Negotiation context: {{what_are_you_negotiating}}
My position: {{what_i_want}}
Their likely position: {{what_they_want}}
My BATNA: {{best_alternative_if_deal_falls_through}}
Their BATNA: {{their_best_alternative}}
Relationship importance: {{one_time / long_term}}

Prepare strategy:
1. Opening position and rationale
2. Target outcome and walk-away point
3. Their interests beneath their stated position
4. Concession ladder (what to give up and when)
5. Anchoring strategy
6. Key phrases and scripts for tough moments
7. Objection responses (top 5 likely objections)
8. Closing techniques
9. Post-negotiation relationship repair if needed
10. Deal checklist""",
        "ratings": [5, 5, 5, 4, 5, 4], "creator_idx": 8,
    },

    # ── Analysis ──────────────────────────────────────────────────────────────
    {
        "title": "Competitor Analysis Framework",
        "description": "Conduct deep competitive analysis with positioning maps, feature comparisons, and strategic gap identification.",
        "category": "Analysis",
        "tags": ["competitive-analysis", "market-research", "strategy", "positioning"],
        "quality_score": 92, "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=300&fit=crop",
        "body": """You are a strategy consultant who has conducted competitive analyses for Fortune 500 companies.

Your company: {{company_name}}
Product: {{your_product}}
Competitors to analyze: {{competitor_1, competitor_2, competitor_3}}
Market segment: {{specific_segment}}
Key battlegrounds: {{pricing / features / distribution / brand}}

Conduct analysis:
1. Competitor profiles (product, pricing, positioning)
2. Feature comparison matrix
3. Pricing strategy breakdown
4. Market positioning map
5. SWOT for top 2 competitors
6. Their messaging and narrative analysis
7. Customer sentiment summary (review themes)
8. Distribution and channel strategy
9. Identified gaps and white spaces
10. Strategic recommendations to differentiate""",
        "ratings": [5, 5, 5, 5, 4, 5], "creator_idx": 9,
    },
    {
        "title": "Financial Model Builder",
        "description": "Build 3-statement financial models with revenue projections, unit economics, and scenario analysis.",
        "category": "Analysis",
        "tags": ["financial-modeling", "finance", "forecasting", "excel"],
        "quality_score": 94, "use_count": 145,
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=300&fit=crop",
        "body": """You are a financial analyst with investment banking and startup CFO experience.

Business type: {{SaaS / ecommerce / marketplace / services}}
Stage: {{pre-revenue / early / growth}}
Time horizon: {{12 / 24 / 36 months}}
Key inputs available: {{what_data_you_have}}

Build financial model structure:
1. Revenue model (pricing tiers, volume assumptions)
2. Customer acquisition model (CAC, conversion rates)
3. Unit economics (LTV, payback period, margins)
4. Operating expense build-up
5. Headcount plan
6. P&L projection
7. Cash flow statement
8. Balance sheet summary
9. Key metrics dashboard (MRR, ARR, burn rate, runway)
10. Scenario analysis (base / bull / bear cases)
Provide Excel formula logic for each section.""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 5,
    },
    {
        "title": "User Research Interview Analyzer",
        "description": "Analyze user interview transcripts to extract themes, pain points, and product insights with structured frameworks.",
        "category": "Analysis",
        "tags": ["user-research", "ux-research", "product", "insights"],
        "quality_score": 89, "use_count": 123,
        "image_url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&h=300&fit=crop",
        "body": """You are a UX researcher who has run hundreds of user interviews and usability studies.

Interview transcript(s): {{paste_transcript}}
Product area: {{feature_or_product_being_researched}}
Research questions: {{what_you_wanted_to_learn}}
Number of participants: {{n}}

Analyze and synthesize:
1. Key themes with supporting quotes
2. Pain point severity mapping (frequency × intensity)
3. Jobs to be Done identified
4. Mental models revealed
5. Surprising or counter-intuitive findings
6. Confirmed vs. challenged assumptions
7. Opportunity areas ranked by impact
8. Persona insights
9. Recommended product changes
10. Follow-up research questions""",
        "ratings": [5, 4, 5, 5, 4], "creator_idx": 6,
    },
    {
        "title": "Marketing Attribution Analyst",
        "description": "Analyze multi-touch attribution data to understand channel performance and optimize marketing budget allocation.",
        "category": "Analysis",
        "tags": ["attribution", "analytics", "marketing-data", "roi"],
        "quality_score": 88, "use_count": 98,
        "image_url": "https://images.unsplash.com/photo-1460925895917-aeb19be489c7?w=400&h=300&fit=crop",
        "body": """You are a marketing analytics director who has built attribution models for enterprise B2B and B2C companies.

Data available: {{channels_and_conversion_data}}
Attribution model used: {{first_touch / last_touch / linear / data_driven}}
Business goal: {{revenue / leads / signups}}
Reporting period: {{date_range}}

Analyze and recommend:
1. Channel performance summary (spend, conversions, CAC)
2. Attribution model comparison
3. Assisted vs. last-click performance gaps
4. Top and bottom performing channels
5. Budget reallocation recommendations
6. Diminishing returns analysis
7. Channel synergy effects
8. Testing roadmap for budget shifts
9. Dashboard KPIs to track going forward
10. Anomalies and explanations""",
        "ratings": [5, 4, 4, 5, 5, 4], "creator_idx": 7,
    },

    # ── Education ─────────────────────────────────────────────────────────────
    {
        "title": "Online Course Curriculum Designer",
        "description": "Design complete online course curricula with learning objectives, modules, assessments, and engagement strategies.",
        "category": "Education",
        "tags": ["online-course", "curriculum", "elearning", "teaching"],
        "quality_score": 90, "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=300&fit=crop",
        "body": """You are an instructional designer who has created courses for Coursera, Udemy, and corporate L&D programs.

Course topic: {{what_students_will_learn}}
Target student: {{who_is_this_for}}
Prior knowledge required: {{prerequisites}}
Course length: {{hours_of_content}}
Format: {{video / text / live / hybrid}}
Platform: {{udemy / teachable / self_hosted}}

Design complete curriculum:
1. Course title and compelling description
2. Learning outcomes (SMART format)
3. Module breakdown with titles
4. Lesson plan per module (title, type, duration, objective)
5. Quiz and assessment strategy
6. Assignments and projects
7. Community and engagement tactics
8. Welcome and onboarding sequence
9. Completion certificate criteria
10. Upsell and next-course pathway""",
        "ratings": [5, 5, 4, 5, 5, 4], "creator_idx": 8,
    },
    {
        "title": "Study Guide & Flashcard Creator",
        "description": "Transform any text or topic into effective study guides, flashcards, and practice questions using spaced repetition principles.",
        "category": "Education",
        "tags": ["study-guide", "flashcards", "memorization", "exam-prep"],
        "quality_score": 86, "use_count": 234,
        "image_url": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=300&fit=crop",
        "body": """You are an educational psychologist and learning specialist who designs study materials using cognitive science.

Topic/text to study: {{paste_content_or_describe_topic}}
Exam or goal: {{what_are_you_studying_for}}
Learning style: {{visual / auditory / kinesthetic / reading}}
Time available: {{study_hours_before_exam}}

Create study package:
1. One-page cheat sheet (key concepts)
2. 20 Anki-style flashcards (Q&A format)
3. Concept map outline
4. Mnemonics for hard-to-remember items
5. 10 practice questions (multiple choice)
6. 5 short-answer questions with model answers
7. 3 essay question prompts
8. Common misconceptions to avoid
9. Spaced repetition schedule
10. Day-before review checklist""",
        "ratings": [5, 5, 5, 4, 5, 5, 4], "creator_idx": 9,
    },
    {
        "title": "Lesson Plan Writer",
        "description": "Write detailed lesson plans with objectives, activities, differentiation strategies, and assessment rubrics.",
        "category": "Education",
        "tags": ["lesson-plan", "teaching", "classroom", "k12"],
        "quality_score": 88, "use_count": 143,
        "image_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=300&fit=crop",
        "body": """You are a master teacher and curriculum developer with experience across K-12 and higher education.

Subject: {{subject_name}}
Topic: {{specific_lesson_topic}}
Grade level: {{grade_or_level}}
Duration: {{45 / 60 / 90 minutes}}
Learning standard: {{curriculum_standard_if_applicable}}
Class size: {{number_of_students}}

Write complete lesson plan:
1. Learning objectives (measurable verbs)
2. Materials and technology needed
3. Hook/engagement activity (5 min)
4. Direct instruction outline
5. Guided practice activity
6. Independent practice
7. Differentiation (advanced / struggling students)
8. ELL accommodations
9. Formative assessment strategy
10. Exit ticket or closure activity
11. Homework assignment
12. Rubric for assessment""",
        "ratings": [5, 4, 5, 5, 4, 5], "creator_idx": 5,
    },

    # ── Design ────────────────────────────────────────────────────────────────
    {
        "title": "Logo Design Brief Generator",
        "description": "Create comprehensive logo design briefs that give designers everything they need for successful brand mark creation.",
        "category": "Design",
        "tags": ["logo-design", "branding", "brief", "visual-identity"],
        "quality_score": 87, "use_count": 189,
        "image_url": "https://images.unsplash.com/photo-1626785774573-4b799315345d?w=400&h=300&fit=crop",
        "body": """You are a brand identity designer who has created logos for major brands and award-winning startups.

Company name: {{company_name}}
Industry: {{industry}}
Brand personality: {{adjectives_list}}
Target audience: {{who_sees_this_logo}}
Competitors' visual style: {{describe_competitors}}
Usage contexts: {{where_logo_appears}}

Create design brief:
1. Brand essence statement
2. Design direction (wordmark / lettermark / symbol / combination)
3. Visual inspiration and mood board description
4. Color psychology and palette options
5. Typography direction (serif / sans / script)
6. Style keywords with visual references
7. What to avoid (competitor differentiation)
8. Technical requirements (min size, backgrounds)
9. Deliverables checklist
10. Revision and approval process""",
        "ratings": [5, 4, 5, 5, 4, 4], "creator_idx": 6,
    },
    {
        "title": "Color Palette Generator for Brands",
        "description": "Create complete brand color systems with primary, secondary, semantic, and neutral palettes with hex codes and usage rules.",
        "category": "Design",
        "tags": ["color-palette", "branding", "design-system", "ui-design"],
        "quality_score": 91, "use_count": 212,
        "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=400&h=300&fit=crop",
        "body": """You are a visual designer and color theory expert who creates systematic design languages for digital products.

Brand: {{brand_name}}
Industry: {{industry}}
Brand personality: {{personality_words}}
Existing colors to work with: {{any_colors_to_keep}}
Platform: {{web / mobile / both}}

Design complete color system:
1. Primary palette (3-5 shades with hex codes)
2. Secondary/accent palette
3. Neutral/gray scale
4. Semantic colors (success, warning, error, info)
5. Dark mode equivalents
6. Color accessibility matrix (WCAG contrast ratios)
7. Usage rules (when to use each color)
8. Color naming conventions
9. CSS custom properties / design tokens
10. Color don'ts and anti-patterns""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 7,
    },
    {
        "title": "Landing Page Wireframe Planner",
        "description": "Plan high-converting landing page wireframes with section structure, copy hierarchy, and CTA placement.",
        "category": "Design",
        "tags": ["landing-page", "wireframe", "conversion", "ux"],
        "quality_score": 89, "use_count": 178,
        "image_url": "https://images.unsplash.com/photo-1558655146-364adaf1fcc9?w=400&h=300&fit=crop",
        "body": """You are a conversion rate optimization specialist and UX designer with 200+ landing page experiments.

Product/offer: {{what_you_are_selling}}
Target visitor: {{who_lands_on_this_page}}
Traffic source: {{google_ads / facebook / email / organic}}
Goal: {{form_fill / purchase / download / signup}}
Price point: {{product_price_or_free}}

Plan landing page:
1. Hero section (headline formula, subhead, CTA, visual)
2. Social proof bar (logos, numbers)
3. Problem/pain section
4. Solution/benefits section (3-column layout)
5. Features deep-dive
6. Testimonials section (format and quantity)
7. FAQ section (objection-handling focus)
8. Pricing section if applicable
9. Final CTA section
10. Trust signals (guarantees, certifications)
Include copy direction for each section.""",
        "ratings": [5, 5, 4, 5, 5, 4], "creator_idx": 8,
    },

    # ── Image Generation ──────────────────────────────────────────────────────
    {
        "title": "Realistic Portrait Photography Prompt",
        "description": "Generate hyper-realistic portrait photography prompts for professional headshots, editorial, and fine art portraiture.",
        "category": "Image Generation",
        "tags": ["portrait", "photography", "dalle", "midjourney", "realistic"],
        "quality_score": 93, "use_count": 287,
        "image_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&h=300&fit=crop",
        "body": """You are a portrait photographer and AI art director specializing in photorealistic human portraiture.

Subject: {{describe_the_person}}
Style: {{headshot / editorial / fine_art / environmental}}
Lighting: {{Rembrandt / butterfly / split / golden_hour}}
Location: {{studio / outdoor / urban / natural}}
Mood: {{professional / casual / artistic / dramatic}}
Camera: {{35mm / 85mm / 50mm portrait}}

Generate portrait prompt with:
1. Subject description (age, features, expression)
2. Wardrobe and styling details
3. Lighting setup (key, fill, rim)
4. Background and environment
5. Camera specs (lens, aperture, depth of field)
6. Post-processing style (clean / moody / film grain)
7. Composition (rule of thirds, eye level, framing)
8. Quality descriptors (Hasselblad, RAW, 8K, award-winning)
9. Negative prompt suggestions
Ready to paste into Midjourney or DALL-E 3.""",
        "ratings": [5, 5, 5, 5, 5, 5], "creator_idx": 9,
    },
    {
        "title": "Abstract Art & Digital Painting Prompt",
        "description": "Generate stunning abstract and digital painting prompts with specific styles, color palettes, and artistic techniques.",
        "category": "Image Generation",
        "tags": ["abstract-art", "digital-painting", "generative-art", "stable-diffusion"],
        "quality_score": 88, "use_count": 198,
        "image_url": "https://images.unsplash.com/photo-1579783902614-e3fb5141b0cb?w=400&h=300&fit=crop",
        "body": """You are a digital artist and AI art curator who has exhibited work at major digital art galleries.

Concept/theme: {{what_the_artwork_represents}}
Style: {{abstract / expressionist / geometric / surrealist}}
Color mood: {{warm / cool / monochromatic / complementary}}
Emotion: {{peaceful / chaotic / nostalgic / futuristic}}
Texture: {{smooth / rough / layered / minimal}}
Size/format: {{square / landscape / portrait}}

Create artwork prompt:
1. Central visual concept description
2. Composition structure
3. Color palette (specific hues and proportions)
4. Texture and surface quality
5. Light source and shadow play
6. Artist style references (Kandinsky, Rothko, etc.)
7. Technical painting techniques
8. Resolution and medium specs
9. Style weights for Stable Diffusion
10. Negative prompt elements to exclude""",
        "ratings": [5, 4, 5, 5, 4, 5], "creator_idx": 5,
    },
    {
        "title": "Architecture & Interior Design Prompt",
        "description": "Generate stunning architectural visualizations and interior design renders for spaces ranging from residential to commercial.",
        "category": "Image Generation",
        "tags": ["architecture", "interior-design", "3d-render", "visualization"],
        "quality_score": 91, "use_count": 167,
        "image_url": "https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop",
        "body": """You are an architectural renderer and interior designer who creates award-winning visualization prompts.

Space type: {{living_room / office / restaurant / exterior}}
Style: {{minimalist / industrial / Scandinavian / luxury / brutalist}}
Materials: {{wood / concrete / glass / marble / metal}}
Lighting: {{natural / artificial / ambient / dramatic}}
Time of day: {{morning / afternoon / golden_hour / night}}
Color palette: {{warm / cool / neutral / bold}}

Generate visualization prompt:
1. Room/space dimensions and layout
2. Key architectural features
3. Furniture and decor selection
4. Material and texture specifications
5. Lighting design (natural + artificial)
6. Plant and organic elements
7. Art and accessories
8. Camera angle (eye_level / bird's_eye / isometric)
9. Rendering quality specs (photorealistic, octane render)
10. Seasonal/atmospheric context""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 6,
    },
    {
        "title": "Food Photography & Recipe Visual Prompt",
        "description": "Create mouth-watering food photography prompts for cookbooks, restaurants, and food bloggers using professional styling.",
        "category": "Image Generation",
        "tags": ["food-photography", "recipe", "restaurant", "cookbook"],
        "quality_score": 89, "use_count": 223,
        "image_url": "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?w=400&h=300&fit=crop",
        "body": """You are a food stylist and photographer whose work appears in Bon Appétit, Food & Wine, and Michelin-starred menus.

Dish: {{food_item_description}}
Cuisine style: {{italian / japanese / american / french / fusion}}
Mood: {{rustic / elegant / modern / casual / festive}}
Setting: {{restaurant / home_kitchen / outdoor / studio}}
Color palette: {{warm / fresh / dark_moody / bright}}
Shot type: {{overhead / 45_degree / hero_shot}}

Generate food photography prompt:
1. Dish plating description (arrangement, garnish, sauces)
2. Props and surface styling (boards, linens, utensils)
3. Background and environment
4. Lighting setup (window light / studio / candlelight)
5. Steam, sauce pours, or action elements
6. Color story and tonal range
7. Shallow depth of field specs
8. Negative space and composition rule
9. Quality descriptors (Leica, Hasselblad, editorial)
10. Instagram vs editorial format considerations""",
        "ratings": [5, 5, 5, 5, 5, 4], "creator_idx": 7,
    },
    {
        "title": "Sci-Fi World & Space Art Prompt",
        "description": "Generate breathtaking sci-fi environments, space scenes, and futuristic cityscapes with cinematic quality.",
        "category": "Image Generation",
        "tags": ["sci-fi", "space-art", "futuristic", "concept-art"],
        "quality_score": 90, "use_count": 189,
        "image_url": "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=400&h=300&fit=crop",
        "body": """You are a sci-fi concept artist who has worked on major Hollywood productions and AAA video games.

Scene concept: {{describe_the_scene}}
Setting: {{deep_space / alien_planet / future_city / space_station}}
Era: {{near_future / far_future / dystopian / utopian}}
Tone: {{epic / mysterious / bleak / hopeful}}
Technology level: {{advanced / ultra_futuristic}}
Scale: {{intimate / vast / cosmic}}

Generate sci-fi art prompt:
1. Environment and world description
2. Architectural/technological details
3. Scale indicators (tiny figures, massive structures)
4. Atmospheric effects (nebulae, haze, weather)
5. Lighting (alien sun, neon, bioluminescence)
6. Color palette and temperature
7. Compositional focal point
8. Artist reference styles (Syd Mead, Simon Stålenhag)
9. Cinematic rendering specs
10. Storytelling element (what just happened or is about to)""",
        "ratings": [5, 5, 4, 5, 5, 5], "creator_idx": 8,
    },

    # ── Photography ───────────────────────────────────────────────────────────
    {
        "title": "Street Photography Composition Guide",
        "description": "Generate prompts for compelling street photography with decisive moment techniques, light chasing, and storytelling.",
        "category": "Photography",
        "tags": ["street-photography", "composition", "urban", "documentary"],
        "quality_score": 86, "use_count": 134,
        "image_url": "https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=400&h=300&fit=crop",
        "body": """You are a street photographer in the tradition of Cartier-Bresson, Vivian Maier, and Daido Moriyama.

City/location: {{where_you_are_shooting}}
Time of day: {{golden_hour / blue_hour / midday / night}}
Weather: {{sunny / overcast / rainy / foggy}}
Subject focus: {{people / architecture / geometry / shadows}}
Style: {{documentary / fine_art / gritty / cinematic}}

Create street photography prompt:
1. Scene description and urban context
2. Human subjects (posture, activity, relationship)
3. Environmental light quality
4. Shadow and reflection opportunities
5. Geometric patterns and leading lines
6. Layering (foreground / midground / background)
7. Camera settings (zone focus, aperture)
8. Decisive moment trigger
9. Color vs black-and-white treatment
10. Ethical storytelling considerations""",
        "ratings": [5, 4, 5, 4, 4, 5], "creator_idx": 9,
    },
    {
        "title": "Wildlife Photography Scene Prompt",
        "description": "Generate stunning wildlife and nature photography prompts that capture animal behavior, habitats, and natural drama.",
        "category": "Photography",
        "tags": ["wildlife", "nature", "animal", "documentary"],
        "quality_score": 88, "use_count": 156,
        "image_url": "https://images.unsplash.com/photo-1474511320723-9a56873867b5?w=400&h=300&fit=crop",
        "body": """You are a National Geographic wildlife photographer with expeditions on every continent.

Animal/subject: {{species_or_wildlife_type}}
Habitat: {{savanna / ocean / forest / arctic / desert}}
Behavior moment: {{hunting / playing / resting / migrating}}
Time: {{dawn / dusk / midday / night}}
Season: {{dry / wet / spring / winter}}

Generate wildlife photography prompt:
1. Animal description with distinctive markings
2. Natural habitat background details
3. Behavior being captured
4. Natural lighting conditions
5. Camera position and angle
6. Depth of field for subject isolation
7. Action freeze or motion blur decision
8. Environmental storytelling elements
9. Weather and atmospheric effects
10. Conservation message embedded in composition""",
        "ratings": [5, 5, 4, 5, 5, 4], "creator_idx": 5,
    },
    {
        "title": "Wedding Photography Shot List",
        "description": "Create comprehensive wedding photography shot lists with timeline, poses, and must-capture moments for every part of the day.",
        "category": "Photography",
        "tags": ["wedding-photography", "shot-list", "events", "portrait"],
        "quality_score": 87, "use_count": 198,
        "image_url": "https://images.unsplash.com/photo-1519741497674-611481863552?w=400&h=300&fit=crop",
        "body": """You are a wedding photographer who has shot 500+ weddings and trained dozens of second shooters.

Venue type: {{church / outdoor / ballroom / beach / intimate}}
Party size: {{bride_and_groom + bridal_party_count}}
Timeline: {{ceremony_time + reception_end_time}}
Style preference: {{traditional / documentary / editorial / fine_art}}
Special requests: {{cultural_traditions / specific_moments}}

Create shot list:
1. Getting-ready shots (details + candids)
2. First look sequence
3. Ceremony must-haves (processional to kiss)
4. Family formal portraits list
5. Bridal party combinations
6. Couple portraits (locations + timing)
7. Reception timeline shots
8. Detail shots (rings, flowers, décor)
9. Candid moments to watch for
10. Low-light and golden-hour opportunities""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 6,
    },

    # ── Video ─────────────────────────────────────────────────────────────────
    {
        "title": "YouTube SEO & Title Optimizer",
        "description": "Create click-worthy YouTube titles, descriptions, and tags that rank in search and get picked up by the algorithm.",
        "category": "Video",
        "tags": ["youtube", "seo", "video-marketing", "thumbnails"],
        "quality_score": 89, "use_count": 267,
        "image_url": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=400&h=300&fit=crop",
        "body": """You are a YouTube growth strategist who has helped channels grow from 0 to 100K+ subscribers.

Video topic: {{what_the_video_is_about}}
Target keyword: {{primary_search_term}}
Channel niche: {{channel_topic_and_audience}}
Video length: {{minutes}}
Existing title (if any): {{current_title}}

Optimize for YouTube:
1. 5 title options (curiosity gap, numbers, power words)
2. Full description (first 150 chars are critical)
3. Keyword-rich tags list (15-20 tags)
4. Timestamps/chapters suggestion
5. End screen CTA script
6. Cards placement strategy
7. Thumbnail concept brief
8. Pinned comment draft
9. Community post to promote video
10. A/B title testing recommendation""",
        "ratings": [5, 5, 5, 5, 4, 5], "creator_idx": 7,
    },
    {
        "title": "TikTok Content Strategy Builder",
        "description": "Build a data-driven TikTok content strategy with hook formulas, trending audio, and posting schedules that grow followers.",
        "category": "Video",
        "tags": ["tiktok", "short-form-video", "viral", "content-strategy"],
        "quality_score": 90, "use_count": 312,
        "image_url": "https://images.unsplash.com/photo-1611605698335-8441acebdf90?w=400&h=300&fit=crop",
        "body": """You are a TikTok growth expert who has built accounts to 1M+ followers across fashion, fitness, and business niches.

Niche: {{content_category}}
Creator persona: {{how_you_want_to_come_across}}
Target audience: {{age_range_and_interests}}
Goal: {{followers / brand_awareness / sales}}
Current follower count: {{number}}

Build TikTok strategy:
1. Niche positioning statement
2. Content pillars (3-4 recurring themes)
3. Hook formulas that work for your niche
4. Video structure template (hook, value, CTA)
5. Trending audio usage strategy
6. Hashtag strategy (mix of sizes)
7. Posting frequency and best times
8. Duet and stitch opportunity hunting
9. Collaboration outreach plan
10. Viral video anatomy (break down what works)""",
        "ratings": [5, 5, 5, 4, 5, 5, 4], "creator_idx": 8,
    },
    {
        "title": "Podcast Episode Planner",
        "description": "Plan engaging podcast episodes with structure, talking points, interview questions, and post-production notes.",
        "category": "Video",
        "tags": ["podcast", "content-planning", "interview", "audio"],
        "quality_score": 85, "use_count": 143,
        "image_url": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=400&h=300&fit=crop",
        "body": """You are a podcast producer and host who has produced top-charting shows in business, education, and entertainment.

Podcast name: {{podcast_name}}
Episode topic: {{this_episode_focus}}
Guest (if any): {{guest_name_and_background}}
Episode length: {{minutes}}
Format: {{interview / solo / panel / narrative}}

Plan episode:
1. Compelling episode title (SEO + curiosity)
2. Show notes description (150 words)
3. Episode outline with time stamps
4. Opening hook monologue
5. 15 interview questions (if guest)
6. Follow-up probing questions
7. Controversial or provocative question
8. Sponsor read placement and copy
9. CTA and outro script
10. Repurposing plan (clips, Twitter, LinkedIn)
11. Thumbnail and art direction
12. Chapter markers for Spotify""",
        "ratings": [5, 4, 5, 5, 4, 4], "creator_idx": 9,
    },
    {
        "title": "Explainer Video Script Writer",
        "description": "Write clear, engaging explainer video scripts that make complex products, services, or concepts easy to understand.",
        "category": "Video",
        "tags": ["explainer-video", "animation", "script", "saas"],
        "quality_score": 91, "use_count": 189,
        "image_url": "https://images.unsplash.com/photo-1485579149c0-123dd79885d5?w=400&h=300&fit=crop",
        "body": """You are a motion design writer who has scripted explainer videos for 200+ SaaS companies and startups.

Product/concept: {{what_needs_explaining}}
Target viewer: {{who_will_watch_this}}
Video length: {{60 / 90 / 120 seconds}}
Tone: {{professional / friendly / playful / urgent}}
Key message: {{one_thing_viewers_must_remember}}

Write explainer script:
1. Opening problem statement (hook in 5 seconds)
2. Agitation (make the pain real)
3. Solution introduction
4. Feature walkthroughs (show, don't just tell)
5. Social proof moment
6. CTA (specific, low-friction)
7. Scene descriptions for animator
8. Character notes and actions
9. Music and sound FX suggestions
10. Screen recording placeholder notes
Word-for-word script with timestamps.""",
        "ratings": [5, 5, 5, 4, 5, 5], "creator_idx": 5,
    },
]

# ─── Main Seed Function ───────────────────────────────────────────────────────

async def seed_marketplace():
    async with SessionFactory() as db:
        print("\n[*] Seeding Marketplace Data...\n")

        # Create/get creator users
        creator_ids = []
        for creator in CREATORS:
            result = await db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": creator["email"]},
            )
            row = result.fetchone()

            if row:
                creator_ids.append(row[0])
                print(f"[OK] Creator exists: {creator['name']}")
            else:
                user_id = uuid4()
                creator_ids.append(user_id)
                await db.execute(
                    text("""
                        INSERT INTO users (id, email, password_hash, display_name, plan, auth_provider)
                        VALUES (:id, :email, :pw, :name, 'pro', 'email')
                    """),
                    {
                        "id": user_id,
                        "email": creator["email"],
                        "pw": _pwd.hash(creator["password"]),
                        "name": creator["name"],
                    },
                )
                print(f"[OK] Created creator: {creator['name']}")

        await db.commit()

        # Create published prompts
        for i, prompt_data in enumerate(PUBLISHED_PROMPTS):
            creator_id = creator_ids[prompt_data["creator_idx"]]
            prompt_id = uuid4()

            created = days_ago(random.randint(10, 60))
            updated = created + timedelta(days=random.randint(0, 3))

            await db.execute(
                text("""
                    INSERT INTO prompts
                        (id, user_id, title, body, description, image_url, category, tags, is_favorite, use_count, quality_score, is_public, created_at, updated_at)
                    VALUES
                        (:id, :uid, :title, :body, :desc, :img, :cat, :tags, :fav, :uses, :score, :public, :created, :updated)
                """),
                {
                    "id": prompt_id,
                    "uid": creator_id,
                    "title": prompt_data["title"],
                    "body": prompt_data["body"],
                    "desc": prompt_data.get("description"),
                    "img": prompt_data.get("image_url"),
                    "cat": prompt_data["category"],
                    "tags": prompt_data["tags"],
                    "fav": random.choice([True, False]),
                    "uses": prompt_data["use_count"],
                    "score": prompt_data["quality_score"],
                    "public": True,  # All are published for marketplace
                    "created": created,
                    "updated": updated,
                },
            )

            # Add ratings
            for rating_score in prompt_data["ratings"]:
                # Random rating user (pick from any creator)
                rating_user_id = random.choice(creator_ids)

                # Skip if same creator
                if rating_user_id == creator_id:
                    rating_user_id = random.choice([c for c in creator_ids if c != creator_id])

                await db.execute(
                    text("""
                        INSERT INTO prompt_ratings (id, prompt_id, user_id, score, created_at)
                        VALUES (:id, :pid, :uid, :score, :created)
                        ON CONFLICT (prompt_id, user_id) DO UPDATE SET score = :score
                    """),
                    {
                        "id": uuid4(),
                        "pid": prompt_id,
                        "uid": rating_user_id,
                        "score": rating_score,
                        "created": days_ago(random.randint(0, 30)),
                    },
                )

            print(f"[OK] Published: {prompt_data['title']} ({len(prompt_data['ratings'])} ratings)")

        await db.commit()
        print("\n[DONE] Marketplace seeded successfully!\n")
        print("[INFO] You can now:")
        print("   1. Login with any creator account (see above)")
        print("   2. Go to Library -> See prompts marked as published")
        print("   3. Go to Explore -> Browse all marketplace prompts")
        print("   4. Rate prompts with stars")
        print("   5. Import prompts to your library\n")


if __name__ == "__main__":
    asyncio.run(seed_marketplace())
