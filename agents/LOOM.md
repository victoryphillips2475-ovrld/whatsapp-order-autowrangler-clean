# LOOM — VULCAN Reference

## What LOOM Is
LOOM is the frontend architect. VULCAN implements what LOOM designs and approves. VULCAN never touches frontend files before LOOM emits APPROVED FOR BUILD.

## What LOOM Delivers to VULCAN

| Artifact | Location | Purpose |
|---|---|---|
| Stitch HTML source | .stitch/designs/*.html | Your implementation input |
| Design system | .stitch/DESIGN.md | Colors, fonts, spacing, component specs |
| Screen metadata | .stitch/metadata.json | Screen IDs, dimensions, device type |
| Project spec | design.md (project root) | Status APPROVED FOR BUILD + implementation guidance |

## VULCAN's Routing Decision

Read the BUILD PLAN frontend target, then apply the correct skill:

| Target stack | Skill to use |
|---|---|
| Vite + React | react-components — /home/overlord/.openclaw/workspace/VULCAN/stitch-skills-main/stitch-skills-main/plugins/stitch-build/skills/react-components/SKILL.md |
| Next.js + shadcn | shadcn-ui — /home/overlord/.openclaw/workspace/VULCAN/stitch-skills-main/stitch-skills-main/plugins/stitch-build/skills/shadcn-ui/SKILL.md |
| React Native (mobile) | react-native — /home/overlord/.openclaw/workspace/VULCAN/stitch-skills-main/stitch-skills-main/skills/react-native/SKILL.md |
| Demo walkthrough video | remotion — /home/overlord/.openclaw/workspace/VULCAN/stitch-skills-main/stitch-skills-main/plugins/stitch-build/skills/remotion/SKILL.md |

Read the SKILL.md for the selected target before writing a single line of code.

**For mobile app builds destined for app stores**: Reference `patterns/app-store-deployment.md` for package name isolation strategies (unique package names per store to prevent cross-store overwrites), CI/CD pipeline setup (EAS Build, Codemagic), and pre-launch compliance requirements (Google Play 12-tester rule, Apple Developer enrollment).

## VULCAN Hard Rules When Implementing from LOOM Output

- fetch-stitch.sh for downloading Stitch assets: bash scripts/fetch-stitch.sh "[url]" ".stitch/designs/{page}.html"
- Screenshot URL suffix: append =w{width} from screen metadata before download
- All colors from theme tokens only — no hardcoded hex values in components
- All static content in mockData.ts — no hardcoded text or image URIs in components
- Every component: TypeScript interface [ComponentName]Props with readonly modifiers
- MVP scope only — Post-Ship items from BUILD PLAN do not exist yet
- .env.example first — always

## React Native Specifics
- SafeAreaView from react-native-safe-area-context on every top-level screen
- accessibilityLabel + accessibilityRole on every interactive element
- src/theme.ts as single source of all color tokens (zero hex in StyleSheet)
- src/data/mockData.ts for all static content
- Atomic Design: atoms -> molecules -> organisms in src/components/

## What VULCAN Sends to LOOM for Phase 2 Review
Signal to LOOM when frontend implementation is complete. LOOM will:
- Compare implementation against .stitch/designs/ screenshots
- Run critique taxonomy (CRITICAL / HIGH / MEDIUM)
- Emit LOOM DESIGN REPORT with APPROVED or REWORK verdict
- APPROVED sends output to WEAVE
- REWORK returns specific findings to VULCAN
