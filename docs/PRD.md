# Product requirements

**Malaysian Thesis Institution System (MTIS)**: MTIS is an AI research guide that helps Malaysian diploma, degree, and postgraduate students identify novel research gaps and structure their thesis titles, objectives, and methodologies.

## Customer and problem
- Who pays: Malaysian students and academic researchers (B2C) in Malaysia, via subscription.
- Problem: "I don't know what to research, or how to make my topic unique enough for a thesis." "My supervisor is always telling me to find a 'gap,' but I don't know where to look."
- Today: Manual literature reviews using Google Scholar, UTM Library, and OpenAlex; reliance on supervisory advice, which is often generalized.
- How often: 5 tasks per customer a month
- What it costs them now: about RM50.00 a month
- Languages: Both; channel: A web app or web chat

## Who uses it
- Owner: Runs the business, pays for hosting/API costs, monitors usage and subscriptions
- Student / Researcher: Signs in, runs research gap searches, saves and exports results
- Admin (add via "+ Add a role"): Manages users, quotas, and abuse monitoring

## AI fit
- Poor fit for an AI SaaS as it stands.
- ✗ Every task is different: a model cannot be tested on a moving target.
- ✓ Code can partly check the answer (Module 2).
- • Mistakes are costly: plan human review and a strict release gate.
- • Only 5 tasks per customer a month: check that it is worth a subscription.
- ✓ The problem costs them about RM50.00 a month: your price must sit well below that.

## Version 1 does
- Auth: Sign up / sign in with Google or email-password
- Auth: Sign up / sign in with Google or email-password
- Topic Search: Student enters a topic + MY/INT toggle; system fetches real papers from OpenAlex and UTM repository
- Gap Analysis: AI analyzes fetched paper abstracts and lists research gaps with citations (AI, checked by code before anyone sees it)
- Title Suggestions: AI generates 2–5 thesis titles (tajuk kajian) from identified gaps, EN/BM toggle (AI, checked by code before anyone sees it)
- Deep-Dive Search: On chosen title, fetches more specific papers and re-runs gap analysis (AI, checked by code before anyone sees it)
- Objectives & Methodology: Generates objectives, research questions, and methodology draft for the chosen title (AI, checked by code before anyone sees it)
- Usage Quota: Limits free trial users to 3 generations/day; resets daily
- Usage Quota: Limits free trial users to 3 generations/day; resets daily
- Project History: Saves each research session; user can reopen past projects
- Each customer’s data is kept apart; people sign in, and each role may do only what docs/AUTH.md allows.

## Later
- Export to Word/PDF (should)
- Subscription & Payment (should)
- Subscription & Payment (should)
- Citation Checker (should)
- Admin Dashboard (could)

## Version 1 does not do
- Plagiarism-style similarity scan
- Full-text PDF reading
- Reference manager (Mendeley/Zotero) export
- Mobile apps (iOS/Android)
- WhatsApp/chat interface
- Full-text PDF analysis of papers
- Plagiarism/similarity checker
- Reference manager export (Zotero/Mendeley)
- Multi-university library integrations beyond UTM
- Team/ supervisor collaboration features
- Anything not listed above.

## Success
- The release gate passes: every case passes.
- The quality targets in docs/QUALITY.md pass.
- 3 paying customers in the first three months.
