# Combined screening and coding in one pass

Sometimes a reviewer should not screen every report, return to the beginning, and only
then code the included set. A single-pass package can be clearer:

1. choose the full-text eligibility decision;
2. **Include** opens quality appraisal and coding;
3. **Exclude** asks for one primary exclusion reason and marks later stages not applicable.

The route changes as soon as the choice is made, but the answer is not complete until
the reviewer saves the required rationale and source evidence. Included reports never
show or require an exclusion reason. Excluded reports never inflate the denominator for
quality or coding. Only active fields count in progress and appear in exported responses.

This pattern was developed for a coauthor calibration task in an AI/GenAI literacy
measurement review. The interaction transfers; its eligibility rules, quality gate and
codebook do not.

## Important boundary

The built-in conditional flow is for independent work with one required reviewer per
field. When two people independently screen the same report, adjudicate eligibility
first and then send retained reports into a coding round. Otherwise, reviewers can take
different branches and create misleading coverage.

[Detailed routing contract and configuration](../../review-evidence-workflow/references/cases/combined-screening-coding.md) · [Data contracts](../../review-evidence-workflow/references/contracts.md) · [Compare TALL](tall.md) · [Compare Agency](agency.md)
