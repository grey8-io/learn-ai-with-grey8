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

Decks are authored in [Marp](https://marp.app/) markdown. Because the architecture slide uses Mermaid, you need Marp's Mermaid integration for the PDF export to render the diagram (rather than show raw markdown).

```bash
# HTML preview (live reload) — uses default Marp renderer; Mermaid renders only if you've added the plugin
npx @marp-team/marp-cli --watch pitch/university-deck.md

# PDF export — recommended via Marp's Mermaid-enabled engine
npx @marp-team/marp-cli pitch/university-deck.md --pdf --mermaid
npx @marp-team/marp-cli pitch/enterprise-deck.md --pdf --mermaid
```

If your Marp CLI version doesn't support `--mermaid`, the fallback is to pre-render the Mermaid block to an SVG / PNG and replace the code block with an `<img>` reference before exporting. The Mermaid source in the `.md` files remains the source of truth.

Exported PDFs are **attached as assets on GitHub Releases**, not committed to the repo. This keeps history light and gives outreach a clean download URL like:

```
github.com/grey8-io/learn-ai-with-grey8/releases/download/pitch-v1/grey8-university.pdf
```

## What's NOT in this directory

Pricing, named pilot/case-study clients, partnership terms, and internal positioning notes live in the private `grey8-talent` repo. The decks committed here are the same artifacts a cold prospect receives — nothing more, nothing less.

Drafting outlines (`*-outline.md`) are kept locally as working scaffolding and excluded from the repo via `.gitignore`.

## Contact

- **LinkedIn:** https://www.linkedin.com/company/grey8-io/
- **Email:** hello@grey8.io
