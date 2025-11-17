# FunctionFlow Showcase

This walkthrough helps your GitHub visitors grok FunctionFlow in under a minute.

## 1. Clone + Install

```bash
git clone https://github.com/OliverZ-dot/FunctionFlow
cd functionflow
pip install -e .
```

## 2. Map a Real Project

```bash
functionflow map samples/spaceship --html spaceship.html --open
```

![Graph preview](./showcase-graph.png)

## 3. Generate a Markdown Report

```bash
functionflow report samples/spaceship --output spaceship-report.md
```

Example snippet:

```
# FunctionFlow Report

- Files scanned: 2
- Functions detected: 12
- Calls tracked: 10
- Docstring coverage: 8/12 (66.7%)
```

## 4. Commit the Artifacts

Check `docs/artifacts` into git so visitors can view the HTML/Markdown without running Python.

## 5. Pitch for Stars

- Drop screenshots/gifs from `docs/` into your README.
- Pin a tweet/thread linking to the interactive graph.
- Ask maintainers to run `functionflow map` on their codebase and share the hotspots.

Happy exploring! If this accelerates your architecture decisions, smash that ⭐️.


