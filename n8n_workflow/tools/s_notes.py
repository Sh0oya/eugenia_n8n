"""Static sticky notes of the course color code: specs (blue), review log (gray), human help (purple), ideas (green)."""
from lib import *


def build(w):
    w.sticky(
        "# Can My PC Run It\n"
        "**Goal** - Tell Mathieu, in French, whether a public GitHub tool will run on his PC before he installs it: compatibility, risks, conflicts with what he already uses, first test.\n\n"
        "**Trigger** - Form (Basic Auth). The error trigger makes this workflow its own error workflow.\n\n"
        "**Deliverable** - a Notion page and an HTML e-mail with the diagnostic; one row per analysis in the analysis_history Data Table.\n\n"
        "**Flow** - request check (one repository per request), GitHub evidence (latest stable release or default branch, README, pyproject.toml), reuse of an identical report, personal context from Notion (profile, inventory and your Installed, Ignored or Uninstalled decisions), Gemini diagnostic with a strict JSON schema, then delivery.\n\n"
        "**Owners** - business and technical owner: Mathieu Haye. n8n project: Personal, folder Sandbox.\n\n"
        "**Never** - nothing is installed or executed on the PC; images, tags and Markdown links to addresses that the inputs do not contain are removed from the AI text.",
        (-1000, -300), 860, 560, BLUE)
    w.sticky(
        "### Journal des Revues\n"
        "- **28/10/2026 (M. Haye)** : init: first delivery, published on the n8n instance. Gemini models and prompt reviewed.\n"
        "Next audit: before 28/04/2027.",
        (-1000, 290), 860, 250, GRAY)
    w.sticky(
        "## Before the first run (human help)\n"
        "1. Create the two Data Tables **analysis_history** and **error_incidents** with the columns listed in the README (Data Tables section).\n"
        "2. Create the credentials and select them on the nodes:\n"
        "- **Google Gemini - Free Tier** (API key from Google AI Studio)\n"
        "- **Gmail - Mathieu** (OAuth2)\n"
        "- **Notion - Eugenia Workspace** (OAuth2, share the profile page and the two databases with it)\n"
        "- **Basic Auth - Diagnostic Form** (protects the form)\n"
        "- **GitHub - Public Repositories Read** (fine-grained token, read-only on public repositories)\n"
        "3. Fill the Notion identifiers and the e-mail in **CONFIGURATION**.\n"
        "4. Publish, then select this workflow as its own error workflow in the settings.",
        (-1000, 570), 860, 330, PURPLE)
    w.sticky(
        "## Ideas for later\n"
        "- Daily check of the Notion inventory that queues the analyses to redo.\n"
        "- Monthly budget guard and a replay queue for failed deliveries.\n"
        "- Vector search for the context once the inventory grows.\n"
        "- Other README formats and install files read next to README.md.\n"
        "- Several repositories per request with a comparison, and the issues about installation as extra evidence.",
        (-1000, 930), 860, 230, GREEN)
