# Sage-installed assets

The installer updates only the exact Sage-owned paths listed in
[`install-manifest.txt`](install-manifest.txt), plus:

- `agents/sage/AGENTS.md`
- `agents/sage/commands/` (the only directory replaced as a whole)
- the selected tools' exact adapter files listed by basename in
  [`adapter-manifest.txt`](adapter-manifest.txt)

Everything else remains user/team-owned: custom knowledge domains, role edits,
non-managed flows, `docs/`, `.sage-local.json`, and unrelated adapter files.
This includes every generated `agents/sage/flows/<slug>/` workspace and its
evidence. The installer may add/update the exact managed
`agents/sage/flow-workspaces.md` contract, but never recursively replaces the
`flows/` directory.

Project DNA is currently a specification, not a shipped runtime. Its installed
technical contract is
[`flows/project-dna-flow.md`](flows/project-dna-flow.md).

Do not edit a manifest-managed file expecting the edit to survive
`/sage-update`. Put project-specific decisions in a separate domain or a
separate flow filename.
