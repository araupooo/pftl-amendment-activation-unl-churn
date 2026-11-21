# Amendment vote counts and progression

Live amendment state from the public `feature` method and the VHS
vote endpoint, newest snapshot set in data/.

- Known amendments: 101
- Enabled: 64
- Disabled: 37
- Entries carrying a `majority` or `vetoed` field: 0
- Entries with `supported: false`: 0
- VHS activation records: 64, all sharing one date and one ledger
  (see `amendment_activation_timing.md`)
- VHS records carrying a `voted` or `eta` field: 0

Finding: no amendment is currently in voting. The evidence is the
absence itself, from two independent sources: the public `feature`
response carries no `majority` field for any of the 101 amendments,
and the VHS vote endpoint returns 64 activation records with zero
`voted`/`eta` fields. This is a negative finding about the public
surface: the `feature` method deliberately omits majority/veto data
from non-admin callers (admin-only fields in
`src/xrpld/rpc/handlers/Feature1.cpp:48-95`), and the VHS vote
endpoint serves activation records only — a 404 is returned for a
non-enabled amendment. Live per-amendment vote counts are therefore
not obtainable from any public source tried; see `reconciliation.md`,
NV1. The `majority`/`vetoed` columns below record that absence
explicitly instead of leaving it implicit.

Both PFTL-only amendments are disabled: `PF_ValidatorVoteTracking`
(`213D9785EF1C34BC0F99BF190299B814AE0563E047DC457C9CB53B6FC02D4B70`)
and `PF_AccountExclusion`
(`56857392BEADCE1E4B0D754A91B73F1D053657AF4FDD585455D4FFBCD5307BE0`).
The switch that selects the live threshold, `fixAmendmentMajorityCalc`
(`4F46DF03559967AC60F2EB272FEFE3928A7594A45FF774B87A7E540DB0F8F068`),
is enabled, so the live majority rule is the post-fix 67% rule
(strict greater-than).

Full per-amendment table: `amendment_vote_counts.csv` (101 rows).
