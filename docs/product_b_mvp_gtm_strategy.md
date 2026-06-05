# Product B MVP GTM Strategy — Curated Source-Bundled Advisor

Date: 2026-06-05
Status: active strategy
Related tasks: DSE-025, DSE-026, DSE-027, DSE-028, PB-001

---

## Product Thesis

Product B should not be another health insurance listing site. It should be a citation-backed advisor that helps a normal buyer choose 1-3 suitable policies from trustworthy insurers.

The product promise:

> We read the official policy documents, Product Benefit Tables, CIS documents, and brochures so the buyer does not have to.

The core value is not maximum choice. The core value is fewer, better, evidence-backed choices with clear caveats.

---

## Why Fewer Policies Is Better

A normal buyer does not benefit from seeing hundreds of policies. They need to understand:

- which policies fit their age, family structure, city, budget, and medical history;
- what each policy quietly restricts;
- which values are variant-specific;
- what is explicitly covered, explicitly not covered, unknown, or schedule-dependent;
- why one policy is recommended over another.

The 647-policy corpus remains useful for parser scale diagnostics, but it is not the right MVP launch universe. Many documents are duplicates, old versions, group products, riders, product lists, or wordings without the Product Benefit Tables needed for comparison.

The MVP should optimize for trust and specificity:

- top insurers only;
- official source bundles only;
- source quality visible;
- citations on every user-facing fact;
- no confident recommendations from incomplete documents.

---

## Target User

Primary user:

- Indian health insurance buyer choosing for self, spouse, children, or parents.
- Often overwhelmed by Policybazaar-style aggregators, agent calls, and unclear brochures.
- Wants a good enough shortlist, not a spreadsheet of every possible policy.

High-intent use cases:

- first-time buyer, age 25-40;
- family floater buyer;
- person buying for senior parents;
- person with existing disease / PED concerns;
- person comparing renewal/porting options;
- person who wants to understand catches before speaking to an agent.

---

## MVP Insurer Universe

Long-term Product B should intentionally cap coverage at roughly the top 10 Indian health insurers unless traction proves a larger universe is worth the QA cost.

The point is not to represent every insurer. The point is to recommend credible options from insurers a buyer is realistically likely to consider.

Selection criteria:

- retail health relevance;
- market presence and userbase;
- brand recall;
- product breadth for individuals/families/senior buyers;
- public availability of official documents;
- ability to collect policy wording + PBT + CIS + brochure/prospectus;
- trust/service perception and claim-related public concerns.

---

## Top 10 Long-Term Insurer Shortlist

Initial long-term shortlist:

1. HDFC ERGO
2. ICICI Lombard
3. Star Health
4. Niva Bupa
5. Care Health
6. Tata AIG
7. Bajaj Allianz
8. SBI General
9. Aditya Birla Health
10. ManipalCigna or New India Assurance

This list must be finalized by DSE-026 using evidence: market presence, retail relevance, product quality, public source availability, and buyer demand.

---

## Top 5 MVP Insurer Shortlist

Recommended MVP top 5:

1. HDFC ERGO
2. ICICI Lombard
3. Star Health
4. Niva Bupa
5. Care Health

Rationale:

- These are commonly encountered by Indian retail health buyers.
- They include both standalone health insurers and large general insurers.
- They are likely to provide enough public product documents for a meaningful MVP.
- They cover different product philosophies, allowing Product B to explain real tradeoffs.

Star Health should not be excluded merely because users report pain points. It is widely encountered, so Product B should cover it honestly and surface caveats with evidence.

---

## Source-Bundle Quality Bar

One product is not one PDF. A Product B-ready product needs a source bundle:

- policy wording;
- Product Benefit Table / table of benefits;
- Customer Information Sheet (CIS);
- brochure/prospectus;
- rider/add-on documents where they materially affect recommendation;
- official source URL for every document;
- SHA-256 file hash;
- UIN/version/effective-date evidence where available;
- product variants such as Standard, Classic, Premier, Plus, Elite.

Source quality statuses:

| Status | Meaning | Product B use |
|--------|---------|---------------|
| `complete` | Wording, PBT/table, CIS, and brochure/prospectus found and matched | Eligible for recommendation |
| `acceptable_with_known_gap` | Minor non-critical source missing, caveat documented | Eligible with warning |
| `missing_pbt` | Variant-level benefit table missing | Not eligible for confident comparison |
| `missing_cis` | CIS missing | Use cautiously; show source-quality warning |
| `uin_mismatch` | Documents disagree on UIN/version | Block until reviewed |
| `variant_unclear` | Variant names/values cannot be mapped safely | Block variant-specific recommendation |
| `stale_version` | Source appears old/withdrawn/revised | Block or show as historical only |
| `rejected` | Non-policy, duplicate, or unreliable source | Do not use |

---

## Recommendation Philosophy

Product B should recommend 1-3 policies, not overwhelm the user.

Recommendation slots:

- Best overall fit.
- Best value / lower restriction fit.
- Best alternative if user has a specific constraint.

Every recommendation should explain:

- why this product fits;
- what the buyer must watch out for;
- what values are variant-specific;
- what is unknown;
- which official source supports each claim.

Display rules:

- Never show `not_found` as "not covered."
- Show "not covered" only for `explicitly_not_covered`.
- Show schedule/PBT-dependent values as schedule-dependent unless the PBT is available.
- Do not flatten conditional values into generic scalar values.

Example failure to avoid:

- Aditya Birla Activ Care wording supports a 15% conditional non-preferred-provider co-pay.
- Separate PBT sources carry Standard/Classic/Premier co-pay provisions.
- Product B must not display a single generic "Co-pay: 15%" without condition and variant context.

---

## Moat

The moat is trust infrastructure, not just extraction.

Key differentiators:

- citations to official text;
- transparent evidence snippets;
- no sales calls as the default experience;
- user education around terms like PBT, CIS, waiting period, room rent, co-pay, deductible, and schedule-dependent;
- profile-aware filtering instead of raw listings;
- visible uncertainty when source documents are incomplete;
- clear separation between legal wording, benefit tables, CIS, and brochures.

---

## Launch Channels

Initial launch should be trust-building, not affiliate-first.

Recommended channels:

- Reddit: `r/personalfinanceindia`, `r/IndiaInvestments`, health-insurance-specific communities.
- LinkedIn build-in-public posts.
- Twitter/X threads explaining policy traps with citations.
- Personal finance communities and WhatsApp/Telegram beta groups.
- SEO policy explainers:
  - "HDFC ERGO Optima Secure policy wording explained"
  - "Niva Bupa ReAssure 2.0 hidden conditions"
  - "Star Health Comprehensive vs HDFC ERGO Optima Secure"
  - "What does Product Benefit Table mean in health insurance?"

Launch wedge:

> "I built a health insurance advisor that shows receipts from the actual policy documents."

---

## Beta Strategy

Start with a closed beta.

Beta flow:

1. User enters profile.
2. Product B recommends 1-3 policies.
3. User can inspect citations and caveats.
4. User gives feedback:
   - Did the recommendation make sense?
   - Did citations increase trust?
   - Which insurer/policy was missing?
   - What confused them?
   - Did they already speak to an agent?

Track:

- most requested missing products;
- source-quality blockers;
- confusing concepts;
- places where users distrust the output;
- policies users expected but did not see;
- recommendation acceptance or rejection reasons.

---

## Feedback Loops

Every beta session should produce structured feedback:

- user profile category;
- recommended policies;
- rejected policies;
- user questions;
- missing documents;
- confusing terms;
- source evidence clicked;
- source evidence that failed to convince;
- manual correction needed.

Product A should use this feedback to prioritize:

- source-bundle collection;
- bundle-aware export;
- LLM refinement;
- additional concepts;
- Product B explanation copy.

---

## Monetization Later, Not Now

Do not start with affiliate-first ranking. It will damage trust before the product earns it.

Possible later monetization:

- paid one-time evidence-backed report;
- paid family/parent policy review;
- transparent affiliate/lead model only after trust is established;
- B2B tooling for advisors only if consumer trust remains protected.

Ranking must never be secretly commission-driven.

---

## Anti-Patterns

Avoid:

- affiliate-first rankings;
- too many choices;
- brochure-only truth;
- treating policy wording as complete product truth;
- unsupported "not covered" claims;
- scalar flattening of conditional values;
- hiding missing PBT/CIS;
- claiming 647-policy coverage as launch quality;
- recommending old/group/custom products to retail buyers;
- using private/credentialed/hostile scraping.

---

## Immediate Next Steps

1. DSE-025 — implement Product Source Bundle Registry.
2. DSE-026 — finalize top 10 and MVP top 5 insurer selection.
3. DSE-027 — run first insurer source-bundle sprint.
4. DSE-028 — update Product B export to carry bundle, variant, source-quality, and condition semantics.
5. Update Product B advisor prototype to recommend from complete/acceptable source bundles only.

