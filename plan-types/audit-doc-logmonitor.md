# Plan type: Audit-doc LogMonitor

## 1. What makes it an Audit-doc LogMonitor ticket

- **A LogMonitor ticket on audit-doc generation failures** (`GenerateAuditDocs - GenerateAuditDoc` signatures, HO or Commercial). Supersedes LogMonitor bug.

## 2. Requirement

- **The ticket matches an error signature, so it covers every quote currently failing,** often with several root causes. A failing quote re-fires every audit run until a fix lands.

- **Every audit-doc failure got past the ByPeril Excel integration tests.** The work also answers why those tests missed it, and extends them to cover the scenario class where a rater-vs-C# comparison can. Post-bind data mutation, like the ghost reprice, can't be covered.

## 3. Discovery

Follows `bug.md`, plus:

1. **SolarWinds first:** search the ticket's own search-link terms from its filing date ("First seen") to now. The work list is whatever still fails, not the quotes the ticket was filed for.
2. **Group by distinct failure** (config, state, error shape) and diagnose each group with `/eli--byperil-audit-diagnostic`, interpreted per the `eli--audit-doc-mismatch-investigation` skill.

- **Beta mismatches on unlaunched configs are often expected.** An unlaunched config (no prod book, e.g. still V1) takes premium-bearing changes in place, so a beta quote bought before such a change audits as DB(bind) ≠ Excel/Recompute(now). Check that timeline before calling it a defect.
- **A Commercial copy can be audited before its first recalculation.** `CopyActorCollection` saves the copy without recalculating (`CopyQuote`, `SaveQuote`, `UpdateQuoteDefinitionByQuoteIdOrFail`), and `CopyQuoteToActor.CopyTo` doesn't copy quote lines. If the copy is a policy's current quote, the audit can select it in that window and crash reading a required quote line (SW-53573: `LossRatio`, in `CommercialEAndSExcelRaterService.SetExcelValues`). In the quote id's logs: a `CommercialQuoteCopyService` result followed by the audit, with no `CommercialQuoteRecalculationService` result between them.

### "The errors stopped" is not a diagnosis

- **`ExcelQuoteAuditServiceBase.GenerateAuditDoc` has four outcomes.** Read them off the code before interpreting a gap in the logs:

| Outcome | `AuditDocsGeneratedOn` | Logs every run? | Live defect? |
|---|---|---|---|
| **Failure**: exception thrown | left NULL | yes, hourly, forever | yes |
| **MisMatch**: premium differs | **marked** | no, logs once, then never re-selected | **yes** |
| **Success**: premium matches | marked | no | no |
| **Skipped**: IMS record gone | marked | warns once | no |

- **Marking happens before the premium comparison,** so a signature that stops firing means only that the crash stopped; the quote can leave the queue still mis-priced. Never write "the audit succeeded" or "this is fixed" from absent logs. A MisMatch logs its own error with the quote id, so a quote-id-scoped search across the full window separates MisMatch from Success-or-no-longer-selected; `AuditDocsGeneratedOn` plus the stored premium settles the rest. One quote can move through several outcomes as fixes ship. Logs give history only: to know whether a quote audits correctly now, run `/eli--byperil-audit-diagnostic`, which executes the audit's own `ComparePremium` against the live rater.

## 5. Steps and stops

1. **Post an RCA per distinct failure**, including the description's quotes when they now pass. When and what fixed them is a bonus.
2. **Ask** whether to spin failures off (per failure or per QuoteDef: SW-48603 → SW-49434…SW-49439) or RCA them in place on the umbrella ticket (SW-51664's three RCAs).
3. **Done when every current failure has an RCA and a disposition:** fix shipped, spun off, or no action with reason.

- **A code fix follows the Bug sequence (`bug.md`).** A rater fix follows `rater-bug.md` for that group.
