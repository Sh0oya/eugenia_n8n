"""Error handler: this workflow is its own error workflow. Incident logged, cause analysed by a small AI model, alert sent."""
from lib import *

CFG = "$('CONFIGURATION').first().json"
INCIDENT = "$('Set - Format Incident').first().json"


def E(js):
    return expr("{{ " + js + " }}")


def build(w):
    r = 45
    w.add("Set - Format Incident", *SET, fields(
        ("workflowName", "string", E("$json.workflow?.name || 'Unknown workflow'")),
        ("nodeName", "string", E("$json.execution?.lastNodeExecuted || 'Unknown node'")),
        ("errorMessage", "string", E("String($json.execution?.error?.message || 'Unknown error').slice(0, 1000)")),
        ("stack", "string", E("String($json.execution?.error?.stack || '').slice(0, 600)")),
        ("executionUrl", "string", E("$json.execution?.url || ''")),
        ("executionId", "string", E("String($json.execution?.id || '')")),
        ("executionMode", "string", E("$json.execution?.mode || ''"))), (3, r))
    w.add("Basic LLM Chain - Analyze Incident", *CHAIN, {"promptType": "define", "text": "=" + prompt("incident.user.xml"),
          "messages": {"messageValues": [{"message": prompt("incident.system.md")}]}, "hasOutputParser": True, "batching": {}}, (4, r), onError="continueRegularOutput",
          note="Small model, short answer: cause, next step and whether a replay is worth it. If the AI is down the alert is still sent.")
    w.add("Gemini Chat - Incident Model", *GEMINI_CHAT, {"modelName": E(f"`models/${{{CFG}.fallbackModel}}`"), "options": {"temperature": 0.2, "maxOutputTokens": 800}}, (3.7, r + 1.7), **cred("gemini"))
    w.add("Output Parser - Incident Analysis", *PARSER, {"schemaType": "fromJson", "jsonSchemaExample": '{\n  "probableCause": "Quota Gemini dépassé (erreur 429).",\n  "nextStep": "Attendre une minute puis rejouer.",\n  "replay": "yes"\n}'}, (4.4, r + 1.7))
    analysis = "$json.output ? `${$json.output.probableCause} ${$json.output.nextStep} (replay: ${$json.output.replay})` : 'AI analysis unavailable'"
    w.add("Set - Prepare Alert", *SET, fields(
        ("analysis", "string", E(analysis)),
        ("subject", "string", E(f"`Échec - ${{{INCIDENT}.workflowName}}`")),
        ("html", "string", E(f"(e => `<p><b>Workflow</b> : ${{e.workflowName}}<br><b>Node</b> : ${{e.nodeName}}<br><b>Erreur</b> : ${{e.errorMessage.replace(/&/g, '&amp;').replace(/</g, '&lt;')}}<br><b>Heure</b> : ${{$now.toFormat('dd/LL/yyyy HH:mm')}}</p><p><b>Analyse</b> : ${{{analysis}}}</p><p><a href=\"${{e.executionUrl}}\">Ouvrir l’exécution en échec</a></p>`)({INCIDENT})"))), (5, r))
    w.add("Data Table - Log Incident", *TABLE, table_insert("error_incidents", {
        "workflowName": E(f"{INCIDENT}.workflowName"), "nodeName": E(f"{INCIDENT}.nodeName"), "errorMessage": E(f"{INCIDENT}.errorMessage"),
        "executionId": E(f"{INCIDENT}.executionId"), "executionUrl": E(f"{INCIDENT}.executionUrl"), "aiAnalysis": E("$json.analysis")}), (6, r), onError="continueRegularOutput")
    w.add("Gmail - Send Alert", *GMAIL, gmail_params(E("$('Set - Prepare Alert').first().json.subject"), E("$('Set - Prepare Alert').first().json.html")), (7, r), **cred("gmail"), **RETRY)
    w.link("Switch - Route by Trigger", "Set - Format Incident", 2)
    w.chain("Set - Format Incident", "Basic LLM Chain - Analyze Incident", "Set - Prepare Alert", "Data Table - Log Incident", "Gmail - Send Alert")
    w.link("Gemini Chat - Incident Model", "Basic LLM Chain - Analyze Incident", 0, 0, "ai_languageModel")
    w.link("Output Parser - Incident Analysis", "Basic LLM Chain - Analyze Incident", 0, 0, "ai_outputParser")
    w.group("## 12. Error handler\nThis workflow is its own error workflow (Settings, Error workflow). A failure anywhere logs an incident in the error_incidents Data Table, asks a small Gemini model for the probable cause, and e-mails an alert with the link to the failed execution (simplified from template 20499 by Lucas Peyrin).",
            ["Set - Format Incident", "Basic LLM Chain - Analyze Incident", "Gemini Chat - Incident Model", "Output Parser - Incident Analysis", "Set - Prepare Alert", "Data Table - Log Incident", "Gmail - Send Alert"])
