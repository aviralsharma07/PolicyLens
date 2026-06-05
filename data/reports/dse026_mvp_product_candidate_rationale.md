# DSE-026 MVP Product Candidate Rationale

Date: 2026-06-06  
Task ID: DSE-026

## Purpose

Define the first DSE-027 source-bundle collection targets for the selected MVP top 5 insurers.

This list is intentionally pragmatic:

- about **30 collection targets** total;
- **6 per MVP insurer**;
- enough breadth to support recommendation use cases without recreating the 647-document sprawl.

## Candidate Design Rules

Each insurer should contribute roughly:

1. flagship comprehensive plan
2. family/value plan
3. senior-focused plan
4. top-up / super top-up plan
5. standard Arogya Sanjeevani
6. premium / differentiated plan

Where a live product/UIN relationship is not yet fully confirmed, the candidate remains valid, but DSE-027 must verify current sellability and exact document bundle identity.

## Collection Priority Order

1. HDFC ERGO
2. Star Health
3. ICICI Lombard
4. Care Health
5. Niva Bupa

This order mirrors the DSE-026 insurer ranking plus source-bundle practicality.

## HDFC ERGO Candidates

Collection anchor:

- [HDFC ERGO CIS downloads](https://www.hdfcergo.com/download/cis/home)

| Product | Likely UIN | Role | Why it matters | Difficulty | Priority |
|---|---|---|---|---|---|
| Optima Secure | `HDFHLIP26058V082526` | flagship comprehensive | Core modern retail product and likely Product B centerpiece. | medium | P1 |
| Optima Restore | `HDFHLIP25012V082425` | premium / differentiated | Important alternative to Optima Secure for recommendation comparison. | medium | P1 |
| my:health Medisure Super Top Up Insurance | `HDFHLIP22021V042122` | super top-up | Needed for deductible/top-up decision flows. | medium | P1 |
| my:health Koti Suraksha | `HDFHLIP21131V012021` | value / affordable | Useful lower-budget entry point. | medium | P2 |
| Energy | `HDHHLIP21345V042021` | senior / chronic-care oriented | Important for older-age buyer flows. | medium | P2 |
| Arogya Sanjeevani Policy, HDFC ERGO | `HDFHLIP20175V011920` | standard benchmark | Standardized baseline product for comparison. | low | P1 |

## Star Health Candidates

Collection anchor:

- [Star Health downloads](https://www.starhealth.in/downloads/)

| Product | Likely UIN | Role | Why it matters | Difficulty | Priority |
|---|---|---|---|---|---|
| Star Comprehensive Insurance Policy | `null` | flagship comprehensive | High retail visibility and broad comparison relevance. | medium | P1 |
| Family Health Optima Insurance Plan | `SHAHLIP22030V062122` | family floater | Very important family-buyer product. | low | P1 |
| Medi Classic Insurance Policy (Individual) | `SHAHLIP23037V072223` | value / traditional individual | Widely recognizable legacy-style retail option. | low | P1 |
| Senior Citizens Red Carpet Health Insurance Policy | `SHAHLIP22040V052122` | senior | Essential for parent/senior recommendation flows. | low | P1 |
| Super Surplus Insurance Policy | `null` | super top-up | Critical for top-up comparison and deductible logic. | medium | P2 |
| Arogya Sanjeevani Policy, Star Health and Allied Insurance Co Ltd | `SHAHLIP22027V032122` | standard benchmark | Standard baseline. | low | P1 |

## ICICI Lombard Candidates

Collection anchor:

- [ICICI health plan/documents surface](https://www.icicilombard.com/health-insurance/get-quote/select-chi-plans)

| Product | Likely UIN | Role | Why it matters | Difficulty | Priority |
|---|---|---|---|---|---|
| Elevate | `null` | flagship current retail product | Current high-visibility ICICI retail health offering and important DSE-027 verification target. | medium | P1 |
| Complete Health Insurance | `ICIHLIP22096V062122` | comprehensive core plan | Strong baseline retail offering already in local corpus. | low | P1 |
| Health advantEDGE | `ICIHLIP22206V022122` | premium / feature-rich | Useful upper-tier comparison candidate. | low | P2 |
| Health Booster | `ICIHLIP22100V032122` | top-up / booster | Important top-up coverage path. | low | P1 |
| Family Shield | `ICIHLIP22092V032122` | family / value | Good mainstream family plan candidate. | low | P2 |
| Arogya Sanjeevani Policy, ICICI Lombard | `ICIHLIP20178V011920` | standard benchmark | Standard comparison baseline. | low | P1 |

## Care Health Candidates

Collection anchor:

- [Care Health CIS page](https://www.careinsurance.com/customer-information-sheet.html)

| Product | Likely UIN | Role | Why it matters | Difficulty | Priority |
|---|---|---|---|---|---|
| Care | `CHIHLIP22184V062122` | flagship family plan | One of the clearest mainstream family-floater candidates in the MVP universe. | low | P1 |
| Care Supreme | `null` | premium / feature-rich | Important high-cover retail option. | medium | P1 |
| Care Classic | `CHIHLIP22071V012122` | value / affordable | Lower-complexity family/value option. | low | P1 |
| Care Freedom | `RHIHLIP21519V022021` | senior focused | Important later-age recommendation candidate. | low | P2 |
| Enhance | `RHIHLIP21372V022021` | super top-up | Necessary for deductible and overflow-cover comparison. | low | P1 |
| Arogya Sanjeevani Policy, Religare / Care Health | `RHIHLIP20154V011920` | standard benchmark | Standard comparison baseline. | low | P1 |

## Niva Bupa Candidates

Collection anchors:

- [Niva Bupa download center](https://transaction.nivabupa.com/pages/downloads.aspx)
- [Niva Bupa ReAssure 2.0 page](https://www.nivabupa.com/health-insurance-plan/reassurev2)

| Product | Likely UIN | Role | Why it matters | Difficulty | Priority |
|---|---|---|---|---|---|
| ReAssure 2.0 | `NBHHLIP26042V022526` | flagship comprehensive | One of the most important current Niva retail products for MVP. | medium | P1 |
| Health Companion | `NBHHLIP23007V052223` | family / value | Simpler family-coverage candidate. | low | P2 |
| Health Recharge | `NBHHLIP22156V032122` | premium / recharge-led | Important differentiated retail option. | low | P2 |
| Health Premia | `MAXHLIP20056V011920` | higher-cover / established line | Useful for product-family continuity and high-cover comparison. | medium | P2 |
| Senior First | `null` | senior | Important senior-focused candidate even if current UIN still needs DSE-027 confirmation. | medium | P1 |
| Arogya Sanjeevani, Niva Bupa Health Insurance Co. Ltd. | `NBHHLIP22151V012122` | standard benchmark | Standard baseline for Niva. | low | P1 |

## Why Only 30 Products

This is a deliberate limit.

The goal is not to maximize document count. The goal is to create a **reviewable,
launch-grade, source-bundled product set**.

Thirty products is enough to:

- cover the main buyer scenarios,
- exercise source-bundle collection rigor,
- build real Product B recommendation depth,
- keep human QA and citation review tractable.

## DSE-027 Hand-Off Notes

- Verify whether each candidate is still actively sold.
- Confirm exact UIN/version from official documents.
- Collect wording + CIS + brochure + PBT / table-of-benefits where available.
- Record missing bundle parts honestly; do not promote incomplete products to recommendation-ready state.

## Artifact

Machine-readable manifest:

- `data/manifests/mvp_product_candidates_v1.json`
