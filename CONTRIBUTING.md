# Contributing

This repository is a delivery accelerator. Contributions should preserve four invariants:

1. **The bright line holds.** No change may let an agent autonomously decide a grade, admission,
   disciplinary outcome, financial-aid award, special-education eligibility, or placement.
2. **The gateway is the only path to a system of record.** No agent gets direct DB credentials
   or unscoped API access. New tools are added as narrowly-scoped, read/write-separated grants.
3. **Governance is not optional.** New agents inherit grounding, prompt-pinning, HITL gates,
   red-team coverage, fairness checks, and student-PII masking. CI enforces prompt-hash drift.
4. **Accessibility is a build requirement.** Student-facing surfaces target WCAG 2.2 AA.

See `governance/README.md` for the EDU compliance spine and `docs/SUITE-ARCHITECTURE.md` for layering.
