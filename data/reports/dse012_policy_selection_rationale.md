# DSE-012: Gold Corpus Expansion — Policy Selection Rationale

Date: 2026-06-01
Task ID: DSE-012
Status: approved (pending draft annotation generation)

## Selection Process

15 new policies selected from the 647-policy active corpus to expand the gold evaluation set from 5 to 20 policies. Selection optimized for:

1. **Insurer diversity** — 15 new insurers, covering 20/23 corpus insurers (87%)
2. **Product type focus** — majority standard retail individual health (aligned with Product B's 20-concept comparison use case)
3. **Page count range** — 26-60 pages, extending the existing 28-66 range
4. **Source diversity** — mix of IRDAI-sourced and website-sourced wordings
5. **Deliberate stress cases** — 3 non-standard products (cancer, top-up, loan-linked) + 1 critical illness

## Review Adjustments

Two adjustments made during human review:

| # | Original | Revised | Reason |
|---|---|---|---|
| 10 | IFFCO Tokio Critical Illness Benefit | IFFCO Tokio **Health Protector** | Avoid two critical illness products; prefer standard health |
| 11 | Kotak Mahindra Group Health Assure | Kotak Mahindra **Health Premier** | Prefer individual retail over group; group policy adds complexity not central to Product B v1 |

## Final 15 Selections

| # | Slug | Insurer | Plan | Pages | Type | Source | Rationale |
|---|---|---|---|---|---|---|---|
| 1 | bajaj_allianz_silver_health | Bajaj Allianz | Silver Health | 33 | Health | IRDAI | Major private insurer, standard health |
| 2 | tata_aig_arogya_sanjeevani | Tata AIG | Arogya Sanjeevani | 28 | New | Website | Standardized product — cross-insurer comparison |
| 3 | niva_bupa_health_recharge | Niva Bupa | Health Recharge | 45 | Revision | IRDAI | Standalone health insurer, complex benefit tables |
| 4 | aditya_birla_activ_care | Aditya Birla | Active Care | 34 | New | IRDAI | Modern product, health-focused insurer |
| 5 | reliance_health_gain | Reliance | Health Gain | 36 | Individual | Website | Compact individual policy |
| 6 | united_india_individual_health | United India | Individual Health Platinum | 26 | Health | IRDAI | Public sector, short document |
| 7 | oriental_cancer_protect | Oriental Insurance | Cancer Protect | 44 | Individual | Website | Specialty cancer product (stress case) |
| 8 | cholamandalam_flexi_max_protect | Cholamandalam | Flexi Max Protect | 40 | Individual | Website | Mid-size insurer, comprehensive plan |
| 9 | future_generali_health_elite | Future Generali | FG Health Elite | 38 | Individual | IRDAI | Individual health |
| 10 | iffco_tokio_health_protector | IFFCO Tokio | Health Protector | 45 | Revision | Website | Standard health (revised from critical illness) |
| 11 | kotak_mahindra_health_premier | Kotak Mahindra | Health Premier | 60 | Revision | Website | Individual retail, longest new policy (revised from group) |
| 12 | royal_sundaram_advanced_topup | Royal Sundaram | Advanced Top-Up | 45 | Individual | Website | Top-up product (stress case) |
| 13 | sbi_general_arogya_sanjeevani | SBI General | Arogya Sanjeevani | 29 | New | IRDAI | Bank-linked insurer, standardized product |
| 14 | universal_sompo_loan_secure | Universal Sompo | Loan Secure | 40 | Individual | Website | Loan-linked product (stress case) |
| 15 | liberty_critical_connect | Liberty | Critical Connect | 52 | New | Website | Critical illness, 52pp, parser stress test |

## Diversity Analysis

| Dimension | Gold 5 | Gold 20 |
|---|---|---|
| Insurers | 5/23 (22%) | 20/23 (87%) |
| Public sector | 1 | 3 |
| Standard individual health | 4 | 15 |
| Specialty/non-standard | 0 | 4 (cancer, top-up, loan, critical) |
| Standardized Arogya Sanjeevani | 1 | 3 |
| Page range | 28-66 | 26-66 |
| Total pages | 218 | ~823 |

## Unrepresented Insurers (3 deferred)

| Insurer | Corpus PDFs | Reason |
|---|---|---|
| Edelweiss | 6 | Small portfolio, limited diversity |
| Raheja QBE | 6 | Small portfolio, mostly group |
| Magma HDI | 10 | Small portfolio |

## Verification

All 15 PDFs verified:
- File exists in `../policy_data/`
- Text layer present (pdfplumber extracts text from page 1)
- UIN matches IRDAI lifecycle registry
- File sizes: 310KB — 2.1MB (no scanned-image suspects)

## Manifest Artifact

`data/manifests/dse012_gold_expansion_candidates_v1.json`
