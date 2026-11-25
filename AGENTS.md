# Working conventions

For changes to the helper or installer, run `python -m unittest discover -s second-brain-tools/tests -v` with the setup dependencies installed. Tests must use isolated vaults and user profiles.

For durable personal/project knowledge, follow `second-brain/AGENTS.md`. Keep the public checkout free of personal notes, original sources, profile configuration and runtime state; `.gitignore` documents the private locations.

For automation changes, read `docs/AUTOMATIZACION.md`: its capture policy remains a proposal. Distinguish documented ideas from implemented triggers.
