"""Static sticky notes of the course color code: specs (blue), to do (yellow), human help (purple), ideas (green), review log (gray)."""
from lib import *


def build(w):
    w.sticky(
        "# Can My PC Run It\n"
        "**Goal** - Tell Mathieu, in French, whether a public GitHub tool will run on his PC before he installs it: compatibility, risks, conflicts with what he already uses, first test.\n\n"
        "**Triggers** - Form (Basic Auth), daily inventory check at 08:00, manual replay of failed deliveries, error trigger (this workflow is its own error workflow).\n\n"
        "**Flow** - request check, GitHub evidence one repository at a time (latest stable release, commit, README and install files, issues), personal context from Notion (profile and inventory) found by vector search, guardrails (identical report reuse, monthly budget), Gemini diagnostic with a strict JSON schema, then a Notion page and an HTML e-mail with the JSON attached.\n\n"
        "**Data Tables** - analysis_history, delivery_queue, error_incidents, inventory_snapshot.\n\n"
        "**Budget** - 5 EUR per month, 12 AI analyses at most, Gemini free tier by default.\n\n"
        "**Never** - nothing is installed or executed on the PC, a missing release asks the user instead of guessing, an incomplete delivery is never silent.",
        (-1000, -300), 860, 720, BLUE)
    w.sticky(
        "## To do before the first run\n"
        "1. Run **Manual - Setup Data Tables** once.\n"
        "2. Fill the three Notion identifiers in **CONFIGURATION**.\n"
        "3. Create the credentials listed in the purple note and select them on the nodes.\n"
        "4. Settings, Error workflow: select this workflow.\n"
        "5. Set env to production when the tests are done (lifts the two repository limit).\n"
        "6. Publish.",
        (-1000, 460), 420, 300, YELLOW)
    w.sticky(
        "## Credentials to create (human help)\n"
        "- **Google Gemini - Free Tier** (API key from Google AI Studio)\n"
        "- **Gmail - Mathieu** (OAuth2)\n"
        "- **Notion - Eugenia Workspace** (OAuth2, share the profile page and both databases with it)\n"
        "- **Basic Auth - Diagnostic Form** (protects the form)\n"
        "- **GitHub - Public Repositories Read** (fine-grained token, read-only on public repositories)",
        (-560, 460), 420, 300, PURPLE)
    w.sticky(
        "## Ideas for later\n"
        "- Google Search grounding for official requirements (the web search setting), once the plan allows it.\n"
        "- A short Notion view that lists the analyses to review.\n"
        "- A cost rate in CONFIGURATION when a paid model replaces the free tier.",
        (-1000, 790), 860, 190, GREEN)
    w.sticky(
        "## Review Log\n"
        "| Date | Version | Change |\n|---|---|---|\n"
        "| 2026-10-23 | 3.0 | Seven workflows merged into one, native nodes first, sticky notes, renamed credentials, latest Gemini aliases, Data Tables filled by the flow |\n"
        "| 2026-10-21 | 2.0 | First production version, seven workflows |",
        (-1000, 1010), 860, 230, GRAY)
