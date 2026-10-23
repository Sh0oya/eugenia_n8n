"""Static sticky notes of the course color code: specs (blue), to do (yellow), human help (purple), ideas (green), review log (gray)."""
from lib import *


def build(w):
    w.sticky(
        "# Can My PC Run It\n"
        "**Goal** - Tell Mathieu, in French, whether a public GitHub tool will run on his PC before he installs it: compatibility, risks, conflicts with what he already uses, first test.\n\n"
        "**Triggers** - Form (Basic Auth) and error trigger (this workflow is its own error workflow).\n\n"
        "**Flow** - request check, GitHub evidence one repository at a time (latest stable release, README, issues), reuse of an identical report, personal context from Notion (profile, inventory and your Installed, Ignored or Uninstalled decisions), Gemini diagnostic with a strict JSON schema, then a Notion page and an HTML e-mail with the JSON attached.\n\n"
        "**Data Tables** - analysis_history (also used for reuse) and error_incidents. The Decision property of the Notion Analyses database is filled by hand and read by the AI.\n\n"
        "**Never** - nothing is installed or executed on the PC, and a missing stable release stops the run with a clear reason.",
        (-1000, -300), 860, 560, BLUE)
    w.sticky(
        "## To do before the first run\n"
        "1. Run **Manual - Setup Data Tables** once.\n"
        "2. Fill the Notion identifiers and the e-mail in **CONFIGURATION**.\n"
        "3. Create the credentials listed in the purple note and select them on the nodes.\n"
        "4. Publish, then select this workflow as its own error workflow in the settings.",
        (-1000, 300), 420, 260, YELLOW)
    w.sticky(
        "## Credentials to create (human help)\n"
        "- **Google Gemini - Free Tier** (API key from Google AI Studio)\n"
        "- **Gmail - Mathieu** (OAuth2)\n"
        "- **Notion - Eugenia Workspace** (OAuth2, share the profile page and both databases with it)\n"
        "- **Basic Auth - Diagnostic Form** (protects the form)\n"
        "- **GitHub - Public Repositories Read** (fine-grained token, read-only on public repositories)",
        (-560, 300), 420, 260, PURPLE)
    w.sticky(
        "## Ideas for later\n"
        "- Daily check of the Notion inventory that queues the analyses to redo.\n"
        "- Wait for a release tag chosen by the user when a repository has no stable release.\n"
        "- Monthly budget guard and a replay queue for failed deliveries.\n"
        "- Vector search for the context once the inventory grows.\n"
        "- Several install files read next to the README.\n"
        "All of these exist in the archived 157-node version.",
        (-1000, 590), 860, 230, GREEN)
    w.sticky(
        "## Review Log\n"
        "| Date | Version | Change |\n|---|---|---|\n"
        "| 2026-10-23 | 3.0 | Seven workflows merged into one of about 50 nodes: native nodes first, sticky notes, renamed credentials, latest Gemini aliases, reuse by link, Data Tables filled by the flow |\n"
        "| 2026-10-21 | 2.0 | First production version, seven workflows |",
        (-1000, 850), 860, 210, GRAY)
