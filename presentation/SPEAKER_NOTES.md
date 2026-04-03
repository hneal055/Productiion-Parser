# Speaker Notes — Production Intelligence Suite
## Scene Reader Studio Technologies LLC
### Investor / Demo Presentation — 2026

---

## SLIDE 1 — HERO / TITLE

**Talking time: ~30 seconds**

> "What you're looking at is the Production Intelligence Suite — three AI-powered tools
> built specifically for the film and television industry, running live right now on this
> machine. Everything you'll see today is real, functional software — not mockups, not
> wireframes. Built by Scene Reader Studio Technologies LLC and powered by Anthropic's
> Claude AI."

**Key point to land:** This is live, working software. Not a pitch deck for something
that might exist. It exists today.

---

## SLIDE 2 — THE PROBLEM

**Talking time: ~60 seconds**

> "Every film and TV production touches three critical documents: contracts, budgets,
> and screenplays. And for decades, all three have been handled the same way — manually,
> slowly, and expensively.
>
> A standard talent contract goes to an entertainment attorney who charges $400–$800 an
> hour and takes 3–5 days to turn around a risk assessment. A production budget lives in
> a spreadsheet with no intelligence, no risk flags, no AI — just a producer's gut feel.
> And a screenplay gets evaluated by a development exec reading 50 scripts a week, with
> no data to back up a pass or a green light.
>
> The industry is making multi-million dollar decisions on instinct and expensive human
> hours. We built the tools to change that."

**Stat to emphasize:** $10B+ lost annually — cite production overruns, legal disputes,
greenlit projects that bomb due to script issues that were visible in the data.

---

## SLIDE 3 — THE SOLUTION

**Talking time: ~45 seconds**

> "The Production Intelligence Suite gives every production company, studio, and
> independent producer three AI-powered tools in one platform.
>
> The Contract Review Tool reads any legal document and gives you a structured risk
> assessment in under 30 seconds. The Production Budget Parser takes your CSV budget
> file and scores it across 8 risk categories — with patent-pending methodology. And
> ScreenFlow AURA is a fully documented REST API that can parse, analyze, and validate
> any screenplay format programmatically.
>
> All three tools run on a single machine. No cloud subscription required. No per-seat
> licensing. Deploy locally or via Docker in minutes."

**Key differentiator:** One platform. Three tools. All three problems solved.

---

## SLIDE 4 — CONTRACT REVIEW TOOL

**Talking time: ~75 seconds**

> "Let me walk you through the Contract Review Tool — available at port 5001.
>
> You upload any contract — PDF, Word document, or plain text. The AI reads the entire
> document and within seconds returns a structured analysis: key terms extracted and
> summarized, every risk clause flagged as HIGH, MEDIUM, or LOW severity, and an
> overall fairness verdict — FAVORABLE, NEUTRAL, or UNFAVORABLE to the signing party.
> On top of that, it surfaces specific negotiation points — the clauses you should push
> back on.
>
> For an independent producer signing a distribution agreement, this replaces a
> $1,200 attorney review with a 30-second AI scan. You still bring your attorney for
> final sign-off — but you walk into that meeting already knowing exactly where the
> landmines are.
>
> The results page has a full action toolbar — save as PDF, export as TXT or JSON,
> print, or copy to clipboard. Everything is logged in a secure SQLite database with
> full history."

**Demo moment:** If live demo — upload one of the hotel agreement .doc files from
sample_contracts. Show the risk flags and fairness assessment.

---

## SLIDE 5 — PRODUCTION BUDGET PARSER

**Talking time: ~90 seconds**

> "The Production Budget Parser is where the patent-pending technology lives.
>
> You upload a standard production budget as a CSV file — the kind every production
> coordinator already maintains. The system parses every line item and scores the
> budget across 8 risk categories: personnel costs, equipment, locations, post-
> production, contingency, scheduling, vendor concentration, and overall budget
> distribution.
>
> What you get back is a comprehensive risk dashboard — an overall risk score, a visual
> breakdown by category using Chart.js charts, AI-powered optimization recommendations,
> and a full line-item modal so you can drill down into exactly which line items are
> driving risk in each category.
>
> You can export the entire analysis to a formatted Excel workbook or generate a PDF
> report with one click. And the comparison tool lets you load two different budget
> versions side-by-side — critical for tracking scope changes during pre-production.
>
> We have 10 sample budgets in the system right now ranging from a $61K corporate
> training video to a $15.4 million studio blockbuster. The risk scoring works across
> every budget size."

**Demo moment:** Click View on the blockbuster budget. Show the risk score, charts,
and the comparison tool against the indie drama budget.

---

## SLIDE 6 — SCREENFLOW AURA

**Talking time: ~75 seconds**

> "ScreenFlow AURA is the API layer — and it's what makes this platform extensible.
>
> Any developer, studio technology team, or third-party application can integrate
> screenplay intelligence into their own workflow via standard REST API calls. You pass
> a screenplay — in Fountain format, FDX, plain text, or PDF — with your API key, and
> you get back structured JSON analysis.
>
> The parse endpoint gives you full structural breakdown — scenes, characters, dialogue
> density, page counts. The analyze endpoint runs a deep narrative analysis — act
> structure, pacing, commercial potential scoring. The validate endpoint checks format
> compliance — critical for submissions that need to meet guild standards.
>
> The batch endpoint processes up to 10 scripts in a single call — for development
> offices reading 50 scripts a week, that's a workflow that simply didn't exist before.
>
> API keys are managed through secure admin endpoints. Rate limiting is built in.
> The system is running live right now at version 3.1.1 and is fully operational."

**Demo moment:** Show the AURA page at 8083. Show the Operational badge and endpoint
table. If comfortable, run a curl command against /api/health live.

---

## SLIDE 7 — TECHNOLOGY STACK

**Talking time: ~45 seconds**

> "Under the hood, the stack is intentionally straightforward and enterprise-grade.
>
> The intelligence layer is Anthropic's Claude — the most capable AI model currently
> available for nuanced language understanding, which is exactly what you need for
> contracts and screenplays. The application layer is Python Flask — battle-tested,
> widely supported, easy to audit.
>
> Data persists in SQLite with Alembic migrations — meaning the database schema evolves
> safely as we add features. The deployment layer supports both local Windows startup
> via BAT files and full Docker Compose deployment with Caddy TLS reverse proxy for
> HTTPS in production.
>
> Security hardening is in place across all three apps — rate limiting, CSRF
> protection, secure session cookies, structured logging, no debug exposure. This is
> not prototype code. This is production-ready software."

---

## SLIDE 8 — LIVE DEMO PREVIEW

**Talking time: ~30 seconds** *(or skip if doing live demo)*

> "All three tools are running simultaneously right now on a single Windows machine.
> The landing page at the root gives you a live status dashboard — green indicators
> for each service, health check polling every 30 seconds.
>
> Contract Review at 5001, Budget Parser at 8082, ScreenFlow AURA at 8083. One
> machine. Three tools. Zero cloud dependency."

**If doing live demo:** Transition directly to browser. Show landing page first —
the health indicators hitting green is a strong visual moment.

---

## SLIDE 9 — IP & COMPETITIVE MOAT

**Talking time: ~60 seconds**

> "Let's talk about what makes this defensible.
>
> First — the 8-category risk assessment system in the Budget Parser is patent pending.
> The methodology for how we score production budgets across those 8 specific
> categories, weight them, and generate actionable recommendations is proprietary
> intellectual property.
>
> Second — the Claude AI integration isn't a generic API wrapper. The prompting
> methodology, the output structure, the way we extract risk flags from legal language —
> that's been built specifically for film and TV workflows through iterative development.
> It's not something a competitor can replicate by calling the same API.
>
> Third — vertical integration. There is no other single platform that handles
> contracts, budgets, AND screenplays with AI. Tools exist for each in isolation —
> expensive, enterprise, not built for independent production. We cover all three in
> one deployable package."

---

## SLIDE 10 — USE CASES / WHO IS THIS FOR

**Talking time: ~45 seconds**

> "The addressable market here is everyone who touches a production document.
>
> Independent producers and production companies are the primary user. They have the
> pain, they don't have the budget for enterprise legal and analytics teams, and they
> make decisions fast. This is a tool they can run on their own laptop.
>
> Studios and streamers are the enterprise play — a deployment per development team,
> API integration into existing systems via AURA, bulk screenplay analysis at scale.
>
> Entertainment attorneys use this for first-pass triage — identifying which contracts
> need the most attention before human review. Film financiers use the budget risk
> scores to evaluate whether a production is likely to go over budget before they
> commit capital.
>
> The same platform serves all of them."

---

## SLIDE 11 — ROADMAP

**Talking time: ~45 seconds**

> "Where we are: Q1 2026 — the Production Intelligence Suite v1.0 is complete,
> deployed, and demo-ready. All three tools are live.
>
> Q2 2026: We wire the ScreenFlow AURA visual dashboard into the Flask app — giving
> AURA a full UI alongside its API. We also add screenplay comparison — upload two
> drafts and get a delta analysis.
>
> Q3 2026: SaaS deployment. Multi-tenant cloud accounts. Subscription model. This is
> when the platform becomes a recurring revenue business.
>
> Q4 2026: API marketplace listing — making AURA available as a standalone developer
> product — and the first studio partnership pilot.
>
> The foundation is already built. What we're looking for is the capital to move from
> locally-deployed tool to cloud SaaS platform."

---

## SLIDE 12 — CLOSING / CALL TO ACTION

**Talking time: ~45 seconds**

> "The Production Intelligence Suite is real, running, and ready today.
>
> Three tools. One platform. Built for an industry that has never had AI-native
> production intelligence at this level of integration.
>
> We're not asking you to believe in a vision — you've seen it running. What we're
> asking is to be part of taking what exists today to the industry at scale.
>
> Scene Reader Studio Technologies LLC. Let's build it together."

**Close strong:** Make eye contact. Pause after "you've seen it running." Let the
weight of having a live, working product land before pivoting to the ask.

---

## DEMO FLOW (if doing live walkthrough)

Recommended order for a 10-minute live demo:

1. Open landing page — show 3 green health indicators
2. Contract Review Tool (5001) — upload a hotel agreement .doc, show risk flags
3. Budget Parser (8082) — click View on blockbuster budget, show risk dashboard
4. Budget Parser — run comparison against indie drama budget
5. AURA (8083) — show endpoint table, mention API key auth
6. Back to landing page — emphasize "one machine, everything running"

**Backup plan if API calls fail:** Screenshots are saved at:
`c:/Projects/production-parser/presentation/screenshots/`
- 01_landing_page.png
- 02_contract_login.png
- 03_contract_dashboard.png
- 04_budget_dashboard.png
- 05_aura_dashboard.png

---

*Proprietary & Confidential — Scene Reader Studio Technologies LLC © 2026*
