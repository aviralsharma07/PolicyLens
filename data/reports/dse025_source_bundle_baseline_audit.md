# DSE-025 Source Bundle Baseline Audit

Date: 2026-06-05
Task: DSE-025 — Product Source Bundle Registry

## Summary

DSE-025 confirms the strategic reset: the existing corpus is strong as a **policy wording** corpus, but it is not yet a launch-grade **product comparison** corpus.

The current active manifest has 647 active documents with file hashes, UINs, page counts, document types, and source domains. It has **zero `source_url` values** and almost no Product Benefit Table / CIS coverage. Therefore Product B must not treat the current 647-policy wording corpus as a complete recommendation universe.

## Inputs Audited

- `data/manifests/active_policy_wordings_v1.json`
- `data/manifests/uin_match_report_v1.json`
- `data/manifests/dse020_run_manifest_v1.json`
- `gold_corpus/policies/aditya_birla_activ_care/metadata.json`

## Current Manifest Coverage

| Metric | Count |
|--------|------:|
| Active documents | 647 |
| Documents with UIN | 647 |
| Documents with source URL | 0 |
| UIN report rows | 647 |
| UIN verified rows | 646 |
| UIN special-case rows | 1 |

## Active Document Type Counts

| Document type | Count |
|---------------|------:|
| `policy_wording` | 629 |
| `brochure` | 18 |

## Active Source Domain Counts

| Source domain | Count |
|---------------|------:|
| `website` | 540 |
| `website_policy_wording` | 57 |
| `irdai` | 49 |
| `website_kis` | 1 |

## Draft Source Bundle Registry Output

Generated artifact:

```text
data/manifests/product_source_bundles_v1.draft.json
```

Registry stats:

| Metric | Count |
|--------|------:|
| Product bundles | 507 |
| `missing_pbt` bundles | 504 |
| `acceptable_with_known_gap` bundles | 1 |
| `rejected` bundles | 2 |
| Policy wording documents | 630 |
| Brochure documents | 18 |
| CIS documents | 1 |
| Product Benefit Table documents | 1 |

The one `acceptable_with_known_gap` bundle is `aditya_birla_activ_care`. It has official source URLs identified for wording, CIS, and Product Benefit Table, but the remote CIS/PBT files have not yet been downloaded, hashed, and reviewed by the DSE-027 source-collection workflow.

The two `rejected` bundles lack policy wording documents in the current grouped registry and are not Product B recommendation candidates.

## Existing Fields That Help DSE-025

The current corpus already provides:

- `document_id`
- `file_hash`
- `filename`
- `file_path`
- `page_count`
- `document_type`
- `corpus_status`
- `insurer`
- `source_domain`
- `uin`
- UIN report lifecycle product name
- UIN report normalized insurer
- UIN report confidence/status

These fields are enough to create a conservative draft source-bundle registry.

## Gaps Blocking Launch-Grade Product Bundles

Current blockers:

- No active manifest `source_url` values.
- No systematic Product Benefit Table collection.
- No systematic CIS collection.
- No systematic brochure/prospectus collection tied to product identity.
- No rider/add-on document linking.
- No source-quality gate in Product B export yet.
- No variant extraction/normalization from PBTs.
- Same product name can appear across multiple UIN versions and local filenames.

## Aditya Birla Activ Care Lesson

The Aditya Birla Activ Care co-pay issue proves why DSE-025 is necessary.

Current Product A wording evidence can support:

- a conditional 15% co-pay for treatment outside the Preferred Provider Network;
- repeated wording that values are specified in the Policy Schedule / Product Benefit Table.

But Product B comparison needs variant-level values that live outside the wording, such as Standard / Classic / Premier PBT provisions. A scalar display like "Co-pay: 15%" is therefore misleading unless it carries condition and source-document context.

## Registry v1 Decisions

DSE-025 v1 uses:

- `product_id` as stable Product A bundle identity;
- `documents[]` for official source documents;
- `document_type` to separate wording, PBT, CIS, brochure/prospectus, rider, premium table, etc.;
- `source_quality` to prevent confident recommendation from incomplete source bundles;
- `variants[]` to record product variants when known.

Source-identified remote documents are allowed with `file_hash = null` only while `review_status = source_identified`. They must be downloaded and hashed before launch-grade use.

## Recommended Next Work

1. DSE-026: finalize top 10 insurers and MVP top 5 with evidence.
2. DSE-027: run first insurer source-bundle sprint.
3. DSE-027 should download official source documents, hash them, and upgrade selected bundles from `source_identified` to `reviewed`.
4. DSE-028 should make Product B export source-quality and variant-aware.

