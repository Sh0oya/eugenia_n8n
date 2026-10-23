"""Error handler: this workflow is its own error workflow. The incident is logged and an alert is sent."""
from lib import *

INCIDENT = "$('Set - Format Incident').first().json"


def E(js):
    return expr("{{ " + js + " }}")


def build(w):
    r = 21
    w.add("Set - Format Incident", *SET, fields(
        ("workflowName", "string", E("$json.workflow?.name || 'Unknown workflow'")),
        ("nodeName", "string", E("$json.execution?.lastNodeExecuted || 'Unknown node'")),
        ("errorMessage", "string", E("String($json.execution?.error?.message || 'Unknown error').slice(0, 1000)")),
        ("executionId", "string", E("String($json.execution?.id || '')")),
        ("executionUrl", "string", E("$json.execution?.url || ''"))), (0, r))
    w.add("Data Table - Log Incident", *TABLE, table_insert("error_incidents", {
        "workflowName": E(f"{INCIDENT}.workflowName"), "nodeName": E(f"{INCIDENT}.nodeName"), "errorMessage": E(f"{INCIDENT}.errorMessage"),
        "executionId": E(f"{INCIDENT}.executionId"), "executionUrl": E(f"{INCIDENT}.executionUrl")}), (1, r), onError="continueRegularOutput")
    w.add("Gmail - Send Alert", *GMAIL, gmail_params(
        E(f"`Échec - ${{{INCIDENT}.workflowName}}`"),
        E(f"`<p><b>Workflow</b> : ${{{INCIDENT}.workflowName}}<br><b>Node</b> : ${{{INCIDENT}.nodeName}}<br><b>Erreur</b> : ${{{INCIDENT}.errorMessage.replace(/&/g, '&amp;').replace(/</g, '&lt;')}}<br><b>Heure</b> : ${{$now.toFormat('dd/LL/yyyy HH:mm')}}</p><p><a href=\"${{{INCIDENT}.executionUrl}}\">Ouvrir l’exécution en échec</a></p>`")),
          (2, r), **cred("gmail"), **RETRY)
    w.link("Switch - Route by Trigger", "Set - Format Incident", 1)
    w.chain("Set - Format Incident", "Data Table - Log Incident", "Gmail - Send Alert")
    w.group("## 7. Error handler\nThis workflow is its own error workflow (workflow settings, once published). A failure anywhere logs an incident in the error_incidents Data Table and e-mails an alert with the link to the failed execution (simplified from template 20499 by Lucas Peyrin).",
            ["Set - Format Incident", "Data Table - Log Incident", "Gmail - Send Alert"])
