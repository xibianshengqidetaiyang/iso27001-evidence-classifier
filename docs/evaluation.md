# Evaluation Notes

## Purpose
This file records a lightweight manual review of the demo outputs, in order to compare:

- expected control mappings
- rule-based classification results
- local AI preliminary audit results

The goal is not to produce a final audit conclusion, but to evaluate whether the workflow is directionally correct and useful for human review.

---

## Sample 1
**File:** `management_review_plan_demo.md`  
**Expected primary controls:**
- 9.3 Management review
- 9.3.2 Management review inputs

**Observation:**
- Rule-based stage should prioritize management review related clauses
- AI stage may still mark the result as `partial` or `uncertain` if the file is only a plan and not a full record

**Manual judgment:** Reasonable if 9.3 / 9.3.2 are among top results

---

## Sample 2
**File:** `internal_audit_report_demo.md`  
**Expected primary controls:**
- 9.2 Internal audit
- 10.2 Nonconformity and corrective action

**Observation:**
- Rule-based stage should prioritize internal audit related clauses
- AI stage may infer partial support for corrective action if the report mentions follow-up findings and improvement items

**Manual judgment:** Reasonable if 9.2 is top-ranked and 10.2 appears as a related candidate

---

## Notes on result interpretation

### Rule-based stage
The rule-based stage is considered useful if:
- the main expected controls appear in the top results
- the file can be mapped to multiple related clauses
- the output contains understandable reasons and keywords

### AI stage
The AI stage is considered useful if:
- it can distinguish between strong evidence and partial evidence
- it does not overclaim full compliance from a single file
- it can provide missing points and suggested additional evidence
- it retains a `needs_human_review` style output for uncertain cases

---

## Current conclusion
For demo-scale validation, the workflow is useful as:

- an evidence triage assistant
- a candidate control mapping helper
- a preliminary audit support tool

It should still be combined with:
- human review
- evidence validity checks
- cross-document verification
- time-effectiveness checks
