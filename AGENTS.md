# Working conventions

For changes to the helper or installer, run `python -m unittest discover -s second-brain-tools/tests -v` with the setup dependencies installed. Tests must use isolated vaults and user profiles.

For durable personal/project knowledge, follow `second-brain/AGENTS.md`. Keep the public checkout free of personal notes, original sources, profile configuration and runtime state; `.gitignore` documents the private locations.

For capture changes, read `docs/AUTOMATIZACION.md` and `docs/VERIFICACION-PILOTO.md`. Keep review-first publication, isolated tests and unchanged third-party skills. Distinguish installed/trusted hooks from observed event execution; this public checkout is not preinstalled in the reader's profile.
