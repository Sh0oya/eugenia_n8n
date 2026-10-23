"""AI diagnostic: structured prompt (course rules), Gemini chain with fallback model, strict validation."""
import json

from lib import *

CFG = "$('CONFIGURATION').first().json"
RATING_KEYS = ["usefulFeatures", "easeOfUse", "easeOfInstallation", "pcPerformance", "cost", "privacy", "documentation", "maintenance", "modifiability"]


def schema():
    text = {"type": "string"}
    nullable = {"type": ["string", "null"]}
    array = lambda items: {"type": "array", "items": items}  # noqa: E731
    obj = lambda props: {"type": "object", "properties": props, "required": list(props)}  # noqa: E731
    enum = lambda *v: {"type": "string", "enum": list(v)}  # noqa: E731
    verdict = obj({"verdict": enum("compatible", "partial", "blocking", "unknown"), "detail": text, "evidence": text})
    rating = obj({"value": {"type": ["integer", "null"], "minimum": 1, "maximum": 5}, "justification": text, "confidence": enum("low", "medium", "high"), "unratedReason": nullable})
    report = obj({
        "repository": text,
        "tldr": obj({"recommendation": text, "mainBenefit": text, "mainLimit": text, "nextStep": text}),
        "usefulness": text,
        "existingAndAlternatives": obj({
            "knownEquivalents": array(obj({"tool": text, "contextId": text, "relation": enum("sameTool", "duplicate", "complement", "replacement", "unrelated"), "justification": text})),
            "externalAlternatives": array(obj({"name": text, "url": text, "justification": text})), "conclusion": text}),
        "compatibility": obj({**{k: verdict for k in ["windows", "wsl", "cpu", "gpu", "ram", "storage", "dependencies"]},
                              "distinctUses": array(obj({"use": text, "requirements": text, "verdict": enum("compatible", "partial", "blocking", "unknown")})), "optimization": text}),
        "conflicts": array(obj({"environment": text, "component": text, "description": text, "evidence": text, "severity": enum("low", "medium", "high")})),
        "risks": array(obj({"category": text, "cause": text, "evidence": text, "consequence": text, "severity": enum("low", "medium", "high", "critical"),
                            "confidence": enum("low", "medium", "high"), "mitigation": text})),
        "projectCosts": array(obj({"item": text, "amount": text, "assumptions": text, "unknowns": text})),
        "firstTrial": obj({"feasibleLocally": {"type": "boolean"}, "blockReason": nullable, "prerequisites": array(text), "steps": array(text), "expectedResult": text,
                           "durationMinutes": {"type": ["integer", "null"]}, "resources": text, "stop": text, "cleanup": text, "alternativeCheck": nullable}),
        "ratings": obj({k: rating for k in RATING_KEYS}),
        "examinedScope": obj({"documents": array(text), "limits": text}),
        "unknowns": array(text),
    })
    return obj({
        "recommendation": text, "report": report,
        "usedContext": array(obj({"id": text, "usage": text})),
        "sources": array(obj({"url": text, "type": enum("github", "web", "notion"), "usage": text})),
        "unknowns": array(text),
    })


def chat_model(model_field, temperature, tokens):
    return {"modelName": expr(f"{{{{ `models/${{{CFG}.{model_field}}}` }}}}"), "options": {"temperature": temperature, "maxOutputTokens": tokens}}


def build(w):
    r = 16
    w.add("XML - Convert Inputs", *XML, {"mode": "jsonToxml", "dataPropertyName": "data", "options": {"rootName": "inputs", "headless": True}}, (8, r),
          note="Native JSON to XML conversion replaces a custom Code node (course rule: structured XML inputs).")
    w.add("Basic LLM Chain - Write Diagnostic", *CHAIN, {"promptType": "define", "text": "=" + prompt("diagnostic.user.xml"),
          "messages": {"messageValues": [{"message": prompt("diagnostic.system.md")}]}, "hasOutputParser": True, "needsFallback": True, "batching": {}},
          (9, r), onError="continueErrorOutput", retryOnFail=True, maxTries=2, waitBetweenTries=5000,
          note="System message = role. User message = goal, context, examples and output format in XML, then the inputs. Gemini Flash with a Flash-Lite fallback.")
    w.add("Gemini Chat - Main Model", *GEMINI_CHAT, chat_model("diagnosticModel", 0.1, "={{ $('CONFIGURATION').first().json.maxOutputTokens }}"), (8.6, r + 1.7), **cred("gemini"))
    w.add("Gemini Chat - Fallback Model", *GEMINI_CHAT, chat_model("fallbackModel", 0.1, "={{ $('CONFIGURATION').first().json.maxOutputTokens }}"), (9.4, r + 1.7), **cred("gemini"))
    w.add("Output Parser - Diagnostic Schema", *PARSER, {"schemaType": "manual", "inputSchema": json.dumps(schema(), ensure_ascii=False, indent=1), "autoFix": False}, (10.2, r + 1.7))
    w.add("Code - Validate and Finalize Diagnostic", *CODE, {"mode": "runOnceForAllItems", "jsCode": code("validate-diagnostic.js")}, (10, r),
          note="Why Code: cross-checking the nested report (ratings, cited context, links) and assembling the final JSON is not possible with standard nodes. Evidence from GitHub always overrides the AI.")

    w.link("Set - Gather Prompt Inputs", "XML - Convert Inputs")
    w.link("XML - Convert Inputs", "Basic LLM Chain - Write Diagnostic")
    w.link("Basic LLM Chain - Write Diagnostic", "Code - Validate and Finalize Diagnostic", 0)
    w.link("Basic LLM Chain - Write Diagnostic", "Code - Validate and Finalize Diagnostic", 1)
    w.link("Gemini Chat - Main Model", "Basic LLM Chain - Write Diagnostic", 0, 0, "ai_languageModel")
    w.link("Gemini Chat - Fallback Model", "Basic LLM Chain - Write Diagnostic", 0, 1, "ai_languageModel")
    w.link("Output Parser - Diagnostic Schema", "Basic LLM Chain - Write Diagnostic", 0, 0, "ai_outputParser")
    w.group("## 5. AI diagnostic\nPrompt built from the course rules (role in the system message, XML sections, five examples, XML inputs). Gemini Flash, latest alias, with a Flash-Lite fallback and a structured output parser with a strict schema. The Code node then refuses any answer that contradicts the GitHub evidence and removes links and images that the inputs do not contain.",
            ["XML - Convert Inputs", "Basic LLM Chain - Write Diagnostic", "Gemini Chat - Main Model", "Gemini Chat - Fallback Model", "Output Parser - Diagnostic Schema",
             "Code - Validate and Finalize Diagnostic"])
