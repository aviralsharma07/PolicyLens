# Glossary

## Domain Terms

| Term | Definition |
|------|------------|
| **Policy Wording** | The legal contract document defining terms of an insurance policy. Source of truth. |
| **Brochure** | Marketing material summarizing policy features. NOT source of truth. |
| **Prospectus** | Sales document with policy highlights. NOT source of truth. |
| **Circular** | Regulatory communication from IRDAI. Used for compliance rules, not extraction. |
| **UIN** | Unique Identification Number assigned by IRDAI to every approved insurance product. Format: e.g. `HDFHLIP23024V012223`. |
| **UIN Base** | The product identifier portion of the UIN (before the version suffix). E.g. `HDFHLIP23024`. |
| **IRDAI** | Insurance Regulatory and Development Authority of India. Regulates all insurance products. |
| **Sum Insured (SI)** | The maximum amount payable by the insurer for a claim during the policy period. |
| **PED** | Pre-Existing Disease. A disease or illness that existed before the policy inception. |
| **NCB** | No Claim Bonus. Also called Cumulative Bonus. Discount or increased coverage for claim-free years. |
| **Co-pay** | The percentage of the claim amount that the insured must pay out of pocket. |
| **Deductible** | A fixed amount the insured must pay before the insurer pays anything. |
| **Sub-limit** | A cap on how much the insurer will pay for a specific expense (e.g., room rent capped at 1% of SI). |
| **Waiting Period** | A period after policy inception during which certain conditions are not covered. |
| **Free Look Period** | A period (typically 15 days) during which the insured can cancel the policy for a full refund. |
| **Grace Period** | A period (typically 15-30 days) after the premium due date during which the policy remains active. |
| **Restoration** | Reinstatement of Sum Insured after it has been exhausted by a claim. |
| **AYUSH** | Ayurveda, Yoga, Unani, Siddha, and Homeopathy — alternative medicine systems. |
| **Schedule of Benefits** | A table listing all covered benefits with their limits and sub-limits. |
| **Policy Schedule** | The first page(s) of the policy document containing insured details, SI, premium, and policy period. |

## Technical Terms

| Term | Definition |
|------|------------|
| **Physical Layer** | Raw page geometry: pages, blocks, lines, text spans with coordinates and font metadata. |
| **Logical Layer** | Document structure: sections, clauses, subclauses with hierarchy. |
| **Semantic Layer** | Extracted facts with typed values, scope, conditions, and provenance. |
| **Document AST** | Abstract Syntax Tree: a structured tree representation of the policy document. |
| **Source Span** | A reference to the exact location (page, bbox, char range) where a piece of text was found. |
| **Fact Candidate** | A potential extracted value before acceptance. Multiple candidates per concept are scored and resolved. |
| **Derived Policy Feature** | The final compiled Product B-facing export view of a policy. In the current public repo this is the ontology-backed 20-concept v1 contract, with broader schema expansion deferred. |
| **Gold Corpus** | A manually annotated set of policies used as the ground truth for evaluation. |
| **Fact Status** | A 7-value enum describing whether a fact was found, absent, ambiguous, conflicting, or needs review. |
| **Scope** | The conditions under which a fact applies (base policy, optional cover, network/non-network). |
| **Normalizer** | A function that converts raw extracted text into a typed canonical value (e.g., "₹5 lakh" → 500000). |
| **Pipeline Run** | A versioned execution of the full extraction pipeline on one or more documents. |
| **Document Type Firewall** | A filter that ensures only policy wordings enter the extraction pipeline. |
