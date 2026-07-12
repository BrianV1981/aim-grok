1. MERGED (SHAs, issue numbers closed)
- Merged fix/issue-92, fix/issue-94, and fix/issue-95 onto main.
- Pushed main successfully.
- Closed issues #92, #94, and #95.
- Closed issue #93 with a comment pointing to the implementation in #95.

2. CONFLICTS / NOTES
- Resolved a conflict in CHANGELOG.md between #92 and #94 by combining their entries.
- Consolidated all changes under version v1.0.8 per Orchestrator's suggestion.
- The `aim-agy_os/CHANGELOG.md` had no conflicts as it was automatically resolved by Git.

3. TESTS RUN
- Ran `PYTHONPATH=aim-agy_os:aim-agy_os/.aim_core pytest aim-agy_os/tests/ -q`
- All 9 tests passed.

4. QUESTIONS (if any)
- None.

5. NEXT
- Awaiting next assignment or follow-up on the `install-core.sh` alias paths.
