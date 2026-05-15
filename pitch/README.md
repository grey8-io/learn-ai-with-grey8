# Pitch Decks

Stakeholder decks for the two target audiences of **Learn AI With Grey8**.

## Decks

| Deck | Audience | Status |
|------|----------|--------|
| [university-deck.md](university-deck.md) | HoDs, Deans, Faculty (CSE / AIML / Data Science departments) | Draft v1 |
| [enterprise-deck.md](enterprise-deck.md) | CHROs, L&D heads, CTOs, engineering managers | Draft v1 |

Both decks share **slides 1, 3, 4, 6** (the core: what the course is, how a lesson works, service-line positioning). Slides **2, 5, 7–12** are audience-specific — including a per-audience problem framing (slide 2) and a per-audience deployment-view diagram (slide 5).

GitHub renders both `.md` files natively, including the Mermaid diagrams. For exported slide decks (PDFs for cold outreach), use Marp CLI as below.

## Rendering

Decks are authored in [Marp](https://marp.app/) markdown. The architecture slide in each deck uses Mermaid, which Marp CLI does not render natively. The build script handles this: it pre-renders each Mermaid block to an SVG, substitutes the image reference, and runs Marp on the processed file.

```powershell
# Build HTML + PDF for both decks (output in pitch/build/, gitignored)
pwsh scripts/build-pitch.ps1
```

First run downloads Puppeteer's Chromium (~150 MB) for both `mermaid-cli` and `marp-cli`. Subsequent runs reuse the cached browser.

Exported PDFs are **attached as assets on GitHub Releases**, not committed to the repo. This keeps history light and gives outreach a clean download URL like:

```
github.com/grey8-io/learn-ai-with-grey8/releases/download/pitch-v1/grey8-university.pdf
```

To create the release after building:

```powershell
gh release create pitch-v1 pitch/build/*.pdf --title 'Pitch decks v1' --notes 'Stakeholder decks for universities and enterprises.'
```

## What's NOT in this directory

Pricing, named pilot/case-study clients, partnership terms, and internal positioning notes live in the private `grey8-talent` repo. The decks committed here are the same artifacts a cold prospect receives — nothing more, nothing less.

Drafting outlines (`*-outline.md`) are kept locally as working scaffolding and excluded from the repo via `.gitignore`.

## Contact

- **LinkedIn:** https://www.linkedin.com/company/grey8-io/
- **Email:** hello@grey8.io
