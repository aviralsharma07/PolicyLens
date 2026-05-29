# Gold Corpus Manual Review: 11 Requires-Manual-Review Facts

Date: 2026-05-29
Task ID: DSE-003
Project: doc-structure-engine
Branch: gold/annotate-5-policies
Reviewer: Codex manual source-PDF review
Status: applied_to_gold_annotations

## Review Rules

- This report was first produced as a report-only review, then approved and applied to `gold_corpus/policies/*/facts.json`.
- Source PDFs are the only authoritative evidence.
- `pdftotext` and IBM Docling markdown were used only as extraction/cross-check tools.
- Proposed `present` facts are allowed to be schedule-dependent when the policy wording clearly says the term applies but the exact amount/percentage is in the policy schedule/certificate.
- Page numbers are 1-based PDF page numbers.

## Summary

| Policy | Fact | Current Status | Proposed Status | Confidence |
|---|---|---:|---:|---:|
| Care Health Care Plus | `co_pay` | requires_manual_review | present | high |
| Care Health Care Plus | `deductible` | requires_manual_review | present | high |
| HDFC ERGO Arogya Sanjeevani | `co_pay` | requires_manual_review | present | high |
| HDFC ERGO Arogya Sanjeevani | `modern_treatment_coverage` | requires_manual_review | present | high |
| ICICI Family Shield | `room_rent_limit` | requires_manual_review | not_applicable | high |
| ICICI Family Shield | `icu_limit` | requires_manual_review | present | medium |
| ICICI Family Shield | `deductible` | requires_manual_review | present | high |
| New India Floater Mediclaim | `claim_intimation_timeline` | requires_manual_review | present | high |
| Star Medi Classic Accident Care | `deductible` | requires_manual_review | present | medium |
| Star Medi Classic Accident Care | `claim_intimation_timeline` | requires_manual_review | present | high |
| Star Medi Classic Accident Care | `claim_settlement_timeline` | requires_manual_review | present | high |

## Application Status

Applied on 2026-05-29 as `pass_5_human_style_manual_review_patch`.

- 10 facts changed from `requires_manual_review` to `present`.
- 1 fact changed from `requires_manual_review` to `not_applicable`.
- Final status distribution after patch: 77 `present`, 3 `explicitly_not_covered`, 2 `not_applicable`, 18 `not_found`, 0 `requires_manual_review`.

## Detailed Review

### 1. Care Health Care Plus — `co_pay`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 28
- Current note: optional co-payment depends on age/network/schedule; wording does not provide one final percentage.

Pages checked:
- PDF pages 10, 27, 28, 38, 46, 57

Source evidence:
```text
If the Insured Person takes Medical Treatment in hospitals other than those listed in Annexure - III to the Policy Terms and Conditions, then the Policyholder/Insured Person shall bear a Co-Payment of 20% on each and every Claim arising in such regard, which will be in addition to any other co-payment (if any) applicable in the Policy.
```
PDF page: 27

```text
Notwithstanding anything to the contrary in the Policy, it is hereby stated that on opting this optional Benefit, the Insured Person or eldest Insured Person (in case of floater) whose age is 61 years or above will bear a Co-payment, which applies to such Insured Person or all Insured Persons (in case of Floater) as specified in the Policy Schedule.
```
PDF page: 28

Proposed annotation:
- Status: `present`
- Value: Smart Select non-Annexure-III hospitals: `20%`; age 61+ optional co-payment: as specified in Policy Schedule.
- Normalized value: include `percentage: 20` with scope `smart_select_non_annexure_iii_hospital`; include a second schedule-dependent component for age 61+ optional co-payment.
- Condition: optional benefit/schedule-dependent; Smart Select condition applies when treatment is taken outside listed Annexure III hospitals.
- Evidence page: 27 for 20%; page 28 for schedule-dependent age 61+ co-payment.

Reviewer decision:
- The fact should not remain unresolved. The policy text clearly establishes co-payment. One concrete percentage exists for Smart Select. Another co-payment is schedule-dependent.

### 2. Care Health Care Plus — `deductible`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 10
- Current note: deductible option depends on Policy Schedule; wording does not provide final deductible amount.

Pages checked:
- PDF pages 3, 10, 27, 28, 38, 46

Source evidence:
```text
Deductible Option If this Optional Benefit is opted, then Policyholder is entitled for a discount on the Premium payable.
```
PDF page: 27

```text
The claim amount assessed by the Company for a particular claim shall be reduced by the Deductible as specified in the Policy Schedule and the Company shall be liable to make payment under the Policy for any Claim only when the Deductible on that Claim is exhausted.
```
PDF page: 27

```text
The Deductible shall be applicable on an aggregate basis for all Claims made by the Insured Person in a Policy Year.
```
PDF page: 28

Proposed annotation:
- Status: `present`
- Value: deductible applies if optional benefit is opted; amount is as specified in Policy Schedule; aggregate basis per Policy Year.
- Normalized value: `amount: null`, `schedule_dependent: true`, `basis: aggregate_per_policy_year`.
- Condition: optional Deductible Option must be opted.
- Evidence page: 27 or 28.

Reviewer decision:
- The fact should be `present`, not unresolved. The exact amount is not in the wording, but the deductible mechanism and basis are explicit.

### 3. HDFC ERGO Arogya Sanjeevani — `co_pay`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 17
- Current note: policy text references deduction of co-payment but no concrete percentage is safely final in wording text.

Pages checked:
- PDF pages 4, 16, 17, 25

Source evidence:
```text
Each and every claim under the Policy shall be subject to a Co-payment of 5% applicable to claim amount admissible and payable as per the terms and conditions of the Policy. The amount payable shall be after deduction of the co-payment.
```
PDF page: 17

Source cross-check:
```text
Co Pay 5% co pay on all claims
```
PDF page: 25

Proposed annotation:
- Status: `present`
- Value: `5%`
- Normalized value: `percentage: 5`
- Scope: all claims under the policy.
- Evidence page: 17.

Reviewer decision:
- This is a clear present fact. The prior caution should be removed because the policy wording gives an exact percentage.

### 4. HDFC ERGO Arogya Sanjeevani — `modern_treatment_coverage`

Current annotation:
- Status: `requires_manual_review`
- Value: `{"covered": true}`
- Existing evidence page: `null`
- Current note: created from direct PDF text review; human reviewer should confirm.

Pages checked:
- PDF page 10

Source evidence:
```text
The following procedures will be covered (wherever medically indicated) either as in patient or as part of day care treatment in a hospital up to 50% of Sum Insured, specified in the policy schedule, during the policy period: A. Uterine Artery Embolization and HIFU ... D. Oral chemotherapy ... G. Robotic surgeries ... H. Stereotactic radio surgeries ... L. Stem cell therapy: Hematopoietic stem cells for bone marrow transplant for haematological conditions to be covered.
```
PDF page: 10

Proposed annotation:
- Status: `present`
- Value: covered up to `50% of Sum Insured`.
- Normalized value: `coverage_status: covered`, `limit_percent_of_sum_insured: 50`.
- Evidence page: 10.

Reviewer decision:
- This can be safely promoted to `present` with evidence page 10 and a concrete limit.

### 5. ICICI Family Shield — `room_rent_limit`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 12
- Current note: hospital cash/ICU cash benefit language is not a direct room-rent indemnity limit.

Pages checked:
- PDF pages 12, 13, 47, 48, 51

Source evidence:
```text
Hospital Daily Cash Benefit If an Insured Person contracts an Illness or suffers an Injury due to an Accident that occurs during the Period of Cover and which solely and directly requires the Insured Person to be Hospitalized, then We will pay the daily amount specified in the Policy Certificate for each continuous and completed day of Hospitalization.
```
PDF page: 12

```text
We shall not be liable to pay the daily amount for more than the maximum number of days specified in the Policy Certificate for each period of Hospitalization within the Period of Cover.
```
PDF page: 12

Proposed annotation:
- Status: `not_applicable`
- Value: `null`
- Normalized value: `null`
- Scope: this wording describes hospital daily cash, not room rent indemnity reimbursement.
- Evidence page: 12.

Reviewer decision:
- Treating this as a room-rent limit would be misleading. The policy pays certificate-defined daily cash; it does not state a room-rent cap.

### 6. ICICI Family Shield — `icu_limit`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 12
- Current note: ICU cash benefit depends on policy certificate and is not a direct ICU room-rent percentage/amount.

Pages checked:
- PDF pages 12, 13

Source evidence:
```text
Intensive Care Unit (ICU) Cash Benefit If an Insured Person contracts an Illness or suffers an Injury due to an Accident that occurs during the Period of Cover and which solely and directly requires the Insured Person to be Hospitalized in an Intensive Care Unit, then We will pay the daily amount specified in the Policy Certificate for each continuous and completed day of confinement in the Intensive Care Unit.
```
PDF pages: 12-13

```text
We shall not be liable to pay the daily amount for more than the maximum number of days specified in the Policy Certificate for each period of Hospitalization within the Period of Cover.
```
PDF page: 13

Proposed annotation:
- Status: `present`
- Value: ICU cash benefit amount and max days are specified in Policy Certificate.
- Normalized value: `amount: null`, `schedule_dependent: true`, `benefit_type: icu_cash`.
- Condition: ICU hospitalization for medically necessary treatment; certificate-defined daily amount and maximum days.
- Evidence pages: 12-13.

Reviewer decision:
- The concept is present as ICU cash benefit, not as an ICU room-rent reimbursement limit. Use schedule-dependent value and make the benefit type explicit.

### 7. ICICI Family Shield — `deductible`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 1
- Current note: deductible applies only if specified in policy certificate; wording does not provide final value.

Pages checked:
- PDF pages 1, 12, 13, 24, 25, 51

Source evidence:
```text
Deductible shall be applicable per year, per life or per event as stated in the policy certificate and specific benefit based deductible shall be applied if specified in the policy certificate.
```
PDF page: 1

```text
Our liability to make any payment under this Benefit shall be in excess of the per event Deductible or per event Franchise stated in the Policy Certificate, if applicable.
```
PDF page: 12

```text
Our liability to make any payment under this Benefit shall be in excess of the per event Deductible or per event Franchise stated in the Policy Certificate, if applicable.
```
PDF page: 25

Proposed annotation:
- Status: `present`
- Value: deductible applies as stated in Policy Certificate; can be per year, per life, per event, or benefit-specific.
- Normalized value: `amount: null`, `schedule_dependent: true`, `basis_options: ["per_year", "per_life", "per_event", "benefit_specific"]`.
- Evidence page: 1, with optional supporting evidence pages 12 and 25.

Reviewer decision:
- This should be `present`, not unresolved. Numeric value is certificate-dependent, but applicability and basis are explicit.

### 8. New India Floater Mediclaim — `claim_intimation_timeline`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: `null`
- Current note: created from direct PDF text review; human reviewer should confirm.

Pages checked:
- PDF pages 8, 22

Source evidence:
```text
If You intend to make any claim under this Policy You must: a. Intimate TPA in writing on detection of any Disease/Injury being suffered immediately or forty-eight hours before Hospitalisation. b. In case of Hospitalisation due to medical emergency, intimate TPA within twenty-four hours from the time of Hospitalisation.
```
PDF page: 22

Proposed annotation:
- Status: `present`
- Value: planned/detected disease or injury: immediately or 48 hours before hospitalization; emergency hospitalization: within 24 hours from hospitalization.
- Normalized value: `planned_or_detected: {"hours_before_hospitalization": 48, "immediate": true}`, `emergency: {"hours_from_hospitalization": 24}`.
- Evidence page: 22.

Reviewer decision:
- This can be promoted to `present`; the policy wording gives concrete timelines.

### 9. Star Medi Classic Accident Care — `deductible`

Current annotation:
- Status: `requires_manual_review`
- Value: `null`
- Existing evidence page: 8
- Current note: product summary references deductible, but no deductible amount/basis is safely final without schedule review.

Pages checked:
- PDF pages 3, 8

Source evidence:
```text
For the following specified diseases: Nil 3. Deductible 3 (21) 4. Co-Payment No cost sharing
```
PDF page: 3

```text
If the claim event falls within two policy periods, the claims shall be paid taking into consideration the available sum insured in the two policy periods, including the deductibles for each policy period.
```
PDF page: 8

Proposed annotation:
- Status: `present`
- Value: deductible is referenced by the policy and may apply by clause/schedule; no amount safely extractable from wording.
- Normalized value: `amount: null`, `schedule_dependent: true`.
- Evidence page: 8, with supporting summary page 3.

Reviewer decision:
- Use `present` with schedule/clause dependency. Do not invent a numeric deductible.

### 10. Star Medi Classic Accident Care — `claim_intimation_timeline`

Current annotation:
- Status: `requires_manual_review`
- Value: `{"days": 15}`
- Existing evidence page: `null`
- Current note: created from direct PDF text review; human reviewer should confirm.

Pages checked:
- PDF pages 7, 14

Source evidence:
```text
Upon the happening of any event, which may give rise to a claim under this policy, notice with full particulars shall be sent to the Company within 24 hours from the date of occurrence of the event.
```
PDF page: 7

```text
Claim must be filed within 15 days from the date of discharge from the Hospital.
```
PDF page: 7

```text
Intimation about an event or occurrence that may give rise to a claim under this policy must be given within 30 days of its happening. Claims for insurance benefits must be submitted to the Company not later than one (1) month after the completion of the treatment or after transportation of the mortal remains/burial in the event of Death.
```
PDF page: 14

Proposed annotation:
- Status: `present`
- Value: Section I event notice: within 24 hours from occurrence; claim filing: within 15 days from discharge. Section II/general accident event intimation: within 30 days of happening; benefit submission: within one month after treatment completion or death transport/burial.
- Normalized value: include multiple scoped timelines rather than a single `days: 15`.
- Evidence pages: 7 and 14.

Reviewer decision:
- The current single `15 days` value is incomplete and should be replaced with scoped timelines.

### 11. Star Medi Classic Accident Care — `claim_settlement_timeline`

Current annotation:
- Status: `requires_manual_review`
- Value: `{"days": 7}`
- Existing evidence page: `null`
- Current note: created from direct PDF text review; human reviewer should confirm.

Pages checked:
- PDF page 15

Source evidence:
```text
Benefits payable under this policy will be paid within 7 days from the time of receipt of all documents the Company requires.
```
PDF page: 15

Proposed annotation:
- Status: `present`
- Value: `7 days from receipt of all required documents`.
- Normalized value: `days: 7`, `trigger: receipt_of_all_required_documents`.
- Evidence page: 15.

Reviewer decision:
- This can be promoted to `present`; the evidence is direct.

## Applied Annotation Patch

Applied annotation changes:

- Promoted 10 facts to `present`.
- Changed ICICI `room_rent_limit` to `not_applicable`.
- Replaced Star `claim_intimation_timeline` value with scoped timelines instead of single `15 days`.
- Added missing evidence pages/text for HDFC modern treatment, New India claim intimation, Star claim intimation, and Star claim settlement.
- Preserved `extraction_method: manual`, added quality pass ID `pass_5_human_style_manual_review_patch`, and retained source-PDF-only notes.

## Verification Notes

- All 11 formerly unresolved facts are covered in this report.
- Every patched `present` fact has at least one PDF page and supporting excerpt.
- Annotation JSON was updated only after approval to patch annotations.
