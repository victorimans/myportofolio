# Project agent instructions

## grill-with-docs

When the user asks for `grill-with-docs`, asks to be grilled, or asks to stress-test a plan or design:

1. Use the `grilling` skill to interview the user in numbered rounds.
2. Ask the whole current decision frontier in each round, give a recommended answer for every question, and wait for the user before continuing.
3. Find facts from the repository yourself; ask the user only for decisions.
4. Use the `domain-modeling` skill alongside the interview. Challenge ambiguous terms, test decisions with concrete scenarios, and compare the model against the code.
5. Do not implement the plan until the user confirms that shared understanding has been reached.
6. When a domain term is resolved, update the repository glossary in `CONTEXT.md`. Create that file only when there is a term worth recording.
7. Create an ADR only for a hard-to-reverse, surprising trade-off. Create `docs/adr/` only when the first ADR is needed.
