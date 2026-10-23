// Renders the validated diagnostic twice from the same JSON: a Markdown page for Notion and a styled HTML e-mail.
// The placeholder __NOTION_BLOCK__ is replaced after the Notion page exists, so both outputs always agree.
const d = $input.first().json.diagnostic;

const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const list = v => (Array.isArray(v) ? v : v ? [v] : []);
const one = s => String(s ?? '').replace(/\s*\n\s*/g, ' ').trim();
const link = (url, text) => `<a href="${/^https:\/\//i.test(url) ? esc(url) : '#'}" style="color:#4f46e5;text-decoration:none">${esc(text)}</a>`;

const FR = {
  compatible: 'compatible', partial: 'partiel', blocking: 'bloquant', unknown: 'inconnu',
  low: 'faible', medium: 'moyenne', high: 'élevée', critical: 'critique',
  sameTool: 'même outil', duplicate: 'doublon', complement: 'complément', replacement: 'remplacement', unrelated: 'sans rapport',
};
const fr = key => FR[key] || String(key || '');
const TONES = { green: ['#166534', '#dcfce7'], orange: ['#92400e', '#fef3c7'], red: ['#991b1b', '#fee2e2'], darkRed: ['#ffffff', '#b91c1c'], gray: ['#374151', '#f3f4f6'], indigo: ['#3730a3', '#e0e7ff'] };
const TONE_OF = { compatible: 'green', partial: 'orange', blocking: 'red', unknown: 'gray', low: 'gray', medium: 'orange', high: 'red', critical: 'darkRed', sameTool: 'indigo', duplicate: 'orange', complement: 'green', replacement: 'red', unrelated: 'gray' };
const pill = (key, tone) => {
  const [color, background] = TONES[tone || TONE_OF[key] || 'gray'];
  return `<span style="display:inline-block;padding:2px 9px;border-radius:999px;background:${background};color:${color};font-size:12px;font-weight:600;line-height:18px;white-space:nowrap">${esc(fr(key))}</span>`;
};
const evidenceLink = e => (!e ? '' : /^https?:\/\//.test(e) ? ` <span style="white-space:nowrap">· ${link(e, 'preuve ↗')}</span>` : ` <span style="color:#6b7280">· ${esc(e)}</span>`);

const RATINGS = {
  usefulFeatures: 'Fonctionnalités utiles', easeOfUse: 'Facilité d’utilisation', easeOfInstallation: 'Facilité d’installation',
  pcPerformance: 'Performances sur le PC', cost: 'Coût', privacy: 'Confidentialité', documentation: 'Documentation',
  maintenance: 'Maintenance', modifiability: 'Possibilité de modifier',
};
const DIMENSIONS = [['windows', 'Windows 11'], ['wsl', 'WSL Ubuntu'], ['cpu', 'CPU'], ['gpu', 'GPU'], ['ram', 'RAM'], ['storage', 'Stockage'], ['dependencies', 'Dépendances']];
const stars = n => '★'.repeat(n) + '☆'.repeat(5 - n);

const failed = d.status !== 'done';
const title = `Analyse — ${d.repository.repository}`;
const overall = r => {
  const verdicts = DIMENSIONS.map(([k]) => r.compatibility?.[k]?.verdict);
  if (verdicts.includes('blocking') || r.firstTrial?.feasibleLocally === false) return ['Bloquant sur ce PC', 'red'];
  if (verdicts.includes('partial')) return ['Compatible avec limites', 'orange'];
  if (verdicts.every(v => v === 'compatible')) return ['Compatible', 'green'];
  return ['À vérifier', 'gray'];
};

// ---------- Markdown (Notion) ----------
const bullets = (items, render) => items.map(x => `- ${one(render(x))}`).join('\n');
const markdownReport = r => {
  const t = r.tldr || {}, ea = r.existingAndAlternatives || {}, c = r.compatibility || {}, e = r.firstTrial || {}, s = r.examinedScope || {};
  const parts = [`## ${r.repository} @ ${r.version}`];
  parts.push('### TL;DR', bullets([`**Recommandation** : ${t.recommendation}`, `**Intérêt principal** : ${t.mainBenefit}`, `**Limite principale** : ${t.mainLimit}`, `**Prochaine étape** : ${t.nextStep}`], x => x));
  parts.push('### Utilité', one(r.usefulness));
  parts.push('### Existant et alternatives', bullets([
    ...list(ea.knownEquivalents).map(x => `${x.tool} — **${fr(x.relation)}** : ${x.justification}`),
    ...list(ea.externalAlternatives).map(x => `Alternative externe : ${x.url ? `[${x.name}](${x.url})` : x.name} — ${x.justification}`),
  ], x => x) || '- Aucun équivalent identifié.', one(ea.conclusion));
  parts.push('### Compatibilité', bullets([
    ...DIMENSIONS.filter(([k]) => c[k]).map(([k, label]) => `**${label}** : ${fr(c[k].verdict)} — ${c[k].detail}${c[k].evidence ? ` (preuve : ${c[k].evidence})` : ''}`),
    ...list(c.distinctUses).map(u => `Usage « ${u.use} » : ${fr(u.verdict)} — ${u.requirements}`),
  ], x => x), c.optimization ? `Optimisation probable : ${one(c.optimization)}` : '');
  parts.push('### Conflits', list(r.conflicts).length ? bullets(r.conflicts, x => `[${fr(x.severity)}] ${x.environment} — ${x.component} : ${x.description}${x.evidence ? ` (preuve : ${x.evidence})` : ''}`) : 'Aucun conflit documenté (ce n’est pas une garantie).');
  parts.push('### Risques', list(r.risks).length ? bullets(r.risks, x => `[${fr(x.severity)}, confiance ${fr(x.confidence)}] **${x.category}** — cause : ${x.cause}. Preuve : ${x.evidence}. Conséquence : ${x.consequence}. Réduction : ${x.mitigation}`) : 'Aucune alerte relevée ; l’absence d’alerte ne vaut pas certification de sécurité.');
  parts.push('### Coûts du projet étudié', list(r.projectCosts).length ? bullets(r.projectCosts, x => `${x.item} : ${x.amount}${x.assumptions ? ` — hypothèses : ${x.assumptions}` : ''}${x.unknowns ? ` — inconnues : ${x.unknowns}` : ''}`) : 'Aucun coût identifié.');
  const trial = ['### Premier essai'];
  if (e.feasibleLocally === false) trial.push(`**Essai local bloqué** : ${one(e.blockReason)}`, `**Vérification réaliste** : ${one(e.alternativeCheck || 'à définir')}`);
  if (list(e.prerequisites).length) trial.push(bullets(e.prerequisites, x => `Prérequis : ${x}`));
  if (list(e.steps).length) trial.push(e.steps.map((x, i) => `${i + 1}. ${one(x)}`).join('\n'));
  if (e.expectedResult) trial.push(`Résultat attendu : ${one(e.expectedResult)} — durée : ${e.durationMinutes ?? '?'} min — ressources : ${one(e.resources || '?')}`);
  if (e.stop || e.cleanup) trial.push(`Arrêt : ${one(e.stop || '?')} — nettoyage : ${one(e.cleanup || '?')}`);
  parts.push(...trial);
  parts.push('### Notes', bullets(Object.entries(RATINGS), ([k, label]) => { const n = r.ratings?.[k] || {}; return n.value == null ? `${label} : non évalué — ${n.unratedReason || 'raison non fournie'}` : `${stars(n.value)} ${label} (${n.value}/5, confiance ${fr(n.confidence)}) — ${n.justification}`; }));
  parts.push('### Périmètre consulté et inconnues', bullets([...list(s.documents).map(x => `Document : ${x}`), ...(s.limits ? [`Limites : ${s.limits}`] : []), ...list(r.unknowns).map(x => `Inconnue : ${x}`)], x => x));
  return parts.filter(Boolean).join('\n\n');
};
const traceLines = () => {
  const t = d.trace || {};
  return [
    `Diagnostic ${d.id} — schéma ${d.schemaVersion} — ${String(d.date).slice(0, 16).replace('T', ' ')} — statut **${d.status}**`,
    d.goal ? `Objectif : ${d.goal}` : 'Sans objectif explicite (pertinence jugée sur le profil)',
    `${d.repository.repository} : ${d.repository.version}${d.repository.releaseUrl ? ` (${d.repository.releaseUrl})` : ' (branche par défaut, pas de release stable)'}`,
    `Moteur : ${t.model} — durée ${t.durationSeconds} s`,
    `Contexte fourni : ${t.context?.profileSections} sections du profil, ${t.context?.inventoryItems} outils de l’inventaire et ${t.context?.decisions ?? 0} décisions`,
    ...list(d.usedProfile?.passages).map(p => `Contexte utilisé : ${p.label}${p.type === 'fictional' ? ' (FICTIF)' : ''} — ${p.usage}`),
    ...list(d.sources).map(s => `Source : ${s.url} — ${s.usage || s.type || ''}`),
    ...list(d.examinationLimits).map(l => `Limite : ${l}`),
    ...list(d.unknowns).map(u => `Inconnue : ${u}`),
  ];
};
const markdown = [`# ${title}`, `**${one(failed ? `Le diagnostic automatique a échoué : ${list(d.unknowns)[0] || 'cause inconnue'}` : d.recommendation)}**`, d.report ? markdownReport(d.report) : '', '## Traçabilité', bullets(traceLines(), x => x)].filter(Boolean).join('\n\n');

// ---------- HTML (e-mail) ----------
const heading = t => `<tr><td style="padding:22px 28px 6px"><div style="font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#6b7280">${esc(t)}</div></td></tr>`;
const block = html => `<tr><td style="padding:4px 28px 6px;font-size:14px;line-height:1.55;color:#111827">${html}</td></tr>`;
const ul = items => items.length ? `<ul style="margin:6px 0 0;padding-left:20px">${items.map(x => `<li style="margin:0 0 7px">${x}</li>`).join('')}</ul>` : '<div style="color:#6b7280">Rien à signaler.</div>';
const starsHtml = n => `<span style="color:#f59e0b;font-size:15px;letter-spacing:1px">${'★'.repeat(n)}</span><span style="color:#d1d5db;font-size:15px;letter-spacing:1px">${'★'.repeat(5 - n)}</span>`;

const card = r => {
  const [label, tone] = overall(r);
  const t = r.tldr || {}, ea = r.existingAndAlternatives || {}, c = r.compatibility || {}, e = r.firstTrial || {};
  const rows = [];
  rows.push(`<tr><td style="padding:24px 28px 14px;border-top:6px solid #f3f4f6"><table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="font-size:20px;font-weight:700;color:#111827">${link(r.url || `https://github.com/${r.repository}`, r.repository)}</td><td align="right">${pill(label, tone)}</td></tr></table>
    <div style="margin-top:4px;font-size:13px;color:#6b7280">version <b style="color:#374151">${esc(r.version)}</b></div></td></tr>`);
  rows.push(`<tr><td style="padding:0 28px 6px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;border-radius:10px">${[['Recommandation', t.recommendation], ['Intérêt principal', t.mainBenefit], ['Limite principale', t.mainLimit], ['Prochaine étape', t.nextStep]]
    .map(([k, v], i) => `<tr><td style="padding:${i ? 4 : 12}px 14px ${i === 3 ? 12 : 4}px;width:140px;vertical-align:top;font-size:13px;font-weight:600;color:#6b7280">${k}</td><td style="padding:${i ? 4 : 12}px 14px ${i === 3 ? 12 : 4}px;font-size:14px;line-height:1.5;color:#111827">${esc(v)}</td></tr>`).join('')}</table></td></tr>`);
  rows.push(heading('Utilité'), block(esc(r.usefulness)));
  rows.push(heading('Existant et alternatives'), block(ul([
    ...list(ea.knownEquivalents).map(x => `${pill(x.relation)} <b>${esc(x.tool)}</b> — ${esc(x.justification)}`),
    ...list(ea.externalAlternatives).map(x => `${pill('alternative', 'indigo')} ${x.url ? link(x.url, x.name) : esc(x.name)} — ${esc(x.justification)}`),
  ]) + (ea.conclusion ? `<div style="margin-top:6px;color:#374151">${esc(ea.conclusion)}</div>` : '')));
  rows.push(heading('Compatibilité'), `<tr><td style="padding:4px 28px 6px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">${DIMENSIONS.filter(([k]) => c[k]).map(([k, name]) => `<tr>
    <td style="padding:8px 10px 8px 0;border-bottom:1px solid #f3f4f6;width:110px;vertical-align:top;font-size:13px;font-weight:600;color:#374151">${name}</td>
    <td style="padding:8px 10px;border-bottom:1px solid #f3f4f6;width:96px;vertical-align:top">${pill(c[k].verdict || 'unknown')}</td>
    <td style="padding:8px 0;border-bottom:1px solid #f3f4f6;font-size:13px;line-height:1.5;color:#111827">${esc(c[k].detail)}${evidenceLink(c[k].evidence)}</td></tr>`).join('')}</table>
    ${list(c.distinctUses).length ? `<div style="margin-top:10px;font-size:13px;line-height:2;color:#111827">${list(c.distinctUses).map(u => `${pill(u.verdict || 'unknown')} <b>${esc(u.use)}</b> — ${esc(u.requirements)}`).join('<br>')}</div>` : ''}
    ${c.optimization ? `<div style="margin-top:8px;font-size:13px;color:#374151"><b>Optimisation probable :</b> ${esc(c.optimization)}</div>` : ''}</td></tr>`);
  rows.push(heading('Conflits'), block(ul(list(r.conflicts).map(x => `${pill(x.severity)} <b>${esc(x.environment)}</b> · ${esc(x.component)} — ${esc(x.description)}${evidenceLink(x.evidence)}`))));
  rows.push(heading('Risques'), block(list(r.risks).length ? ul(r.risks.map(x => `${pill(x.severity)} <b>${esc(x.category)}</b> — ${esc(x.cause)}<br><span style="color:#374151">Conséquence : ${esc(x.consequence)}<br>Réduction : ${esc(x.mitigation)}</span> <span style="color:#6b7280;font-size:12px">(confiance ${esc(fr(x.confidence))})</span>${evidenceLink(x.evidence)}`)) : '<div style="color:#6b7280">Aucune alerte relevée ; ce n’est pas une certification de sécurité.</div>'));
  rows.push(heading('Coûts du projet étudié'), block(ul(list(r.projectCosts).map(x => `<b>${esc(x.item)}</b> : ${esc(x.amount)}${x.assumptions ? ` <span style="color:#6b7280">— ${esc(x.assumptions)}</span>` : ''}`))));
  const trial = e.feasibleLocally === false
    ? `<div style="background:#fef2f2;border-left:4px solid #dc2626;border-radius:6px;padding:10px 14px"><b style="color:#991b1b">Essai local bloqué.</b> ${esc(e.blockReason)}${e.alternativeCheck ? `<br><b>Vérification réaliste :</b> ${esc(e.alternativeCheck)}` : ''}</div>`
    : `${list(e.prerequisites).length ? `<div style="font-size:13px;color:#374151;margin-bottom:6px"><b>Prérequis :</b> ${list(e.prerequisites).map(esc).join(' · ')}</div>` : ''}<ol style="margin:4px 0 0;padding-left:22px">${list(e.steps).map(x => `<li style="margin:0 0 6px;font-family:Consolas,Menlo,monospace;font-size:13px;background:#f9fafb;padding:3px 6px;border-radius:4px">${esc(x)}</li>`).join('')}</ol>
       <div style="margin-top:8px;font-size:13px;color:#374151">${e.expectedResult ? `<b>Résultat attendu :</b> ${esc(e.expectedResult)}<br>` : ''}⏱ ${esc(e.durationMinutes ?? '?')} min${e.resources ? ` · ${esc(e.resources)}` : ''}${e.cleanup ? `<br><b>Nettoyage :</b> ${esc(e.cleanup)}` : ''}</div>`;
  rows.push(heading('Premier essai'), block(trial));
  rows.push(heading('Notes'), `<tr><td style="padding:4px 28px 6px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse">${Object.entries(RATINGS).map(([k, label]) => { const n = r.ratings?.[k] || {}; return `<tr>
    <td style="padding:6px 10px 6px 0;border-bottom:1px solid #f3f4f6;width:170px;font-size:13px;color:#374151;vertical-align:top">${label}</td>
    <td style="padding:6px 10px;border-bottom:1px solid #f3f4f6;width:92px;vertical-align:top;white-space:nowrap">${n.value == null ? '<span style="color:#9ca3af;font-size:12px">non évalué</span>' : starsHtml(n.value)}</td>
    <td style="padding:6px 0;border-bottom:1px solid #f3f4f6;font-size:12px;line-height:1.45;color:#6b7280">${esc(n.value == null ? n.unratedReason : n.justification)}</td></tr>`; }).join('')}</table></td></tr>`);
  if (list(r.unknowns).length) rows.push(heading('Inconnues'), block(ul(r.unknowns.map(esc))));
  return rows.join('');
};

const trace = d.trace || {};
const summary = failed ? list(d.unknowns)[0] || '' : `${d.repository.repository} : ${d.report.tldr.recommendation}`;
const date = DateTime.fromISO(d.date).setZone('Europe/Paris').setLocale('fr').toFormat('d LLLL yyyy à HH:mm');
const emailHtml = `<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title></head>
<body style="margin:0;padding:0;background:#eef0f4;color:#111827">
<div style="display:none;max-height:0;overflow:hidden;opacity:0">${esc(summary.slice(0, 180))}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#eef0f4"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:680px;background:#ffffff;color:#111827;border-radius:14px;overflow:hidden;font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif">
  <tr><td style="background:#111827;padding:26px 28px"><div style="font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#a5b4fc">Ça tourne sur mon PC ?</div>
    <div style="margin-top:6px;font-size:22px;font-weight:700;line-height:1.3;color:#ffffff">${esc(title)}</div>
    <div style="margin-top:6px;font-size:13px;color:#9ca3af">${esc(date)} · ${d.goal ? `objectif : ${esc(d.goal)}` : 'jugé d’après ton profil'}</div></td></tr>
  <tr><td style="padding:22px 28px 6px"><div style="border-left:4px solid ${failed ? '#dc2626' : '#4f46e5'};background:${failed ? '#fef2f2' : '#eef2ff'};border-radius:8px;padding:14px 16px;font-size:15px;line-height:1.55;color:#111827">${esc(failed ? list(d.unknowns)[0] : d.recommendation)}</div></td></tr>
  <tr><td style="padding:12px 28px 4px">__NOTION_BLOCK__</td></tr>
  ${d.report ? card(d.report) : ''}
  <tr><td style="padding:24px 28px;border-top:6px solid #f3f4f6;background:#fafafa;font-size:12px;line-height:1.6;color:#6b7280"><b style="color:#374151">Traçabilité</b><br>
    ${esc(d.id)} · schéma ${esc(d.schemaVersion)} · ${esc(d.repository.repository)}@${esc(d.repository.version)}<br>
    ${esc(trace.model)} · ${esc(trace.durationSeconds)} s · ${esc(trace.context?.profileSections)} sections de profil, ${esc(trace.context?.inventoryItems)} outils et ${esc(trace.context?.decisions ?? 0)} décisions fournis<br>
    ${list(d.usedProfile?.passages).length ? `Contexte utilisé : ${d.usedProfile.passages.map(p => esc(p.label)).join(', ')}<br>` : ''}
    ${list(d.examinationLimits).length ? `Limites : ${d.examinationLimits.map(esc).join(' · ')}<br>` : ''}
    ${list(d.sources).length ? `Sources : ${d.sources.map((s, i) => link(s.url, `[${i + 1}]`)).join(' ')}<br>` : ''}<br>
    Le JSON complet du diagnostic est en bas de la page Notion.<br>Diagnostic textuel : rien n’a été installé ni exécuté sur ton PC.</td></tr>
</table></td></tr></table></body></html>`;

const jsonText = JSON.stringify(d, null, 2);
return [{ json: {
  diagnostic: d,
  title,
  subject: `${failed ? 'Échec du diagnostic' : 'Diagnostic'} — ${d.repository.repository}`,
  tldr: (failed ? `Échec : ${summary}` : summary).slice(0, 1990),
  markdown,
  markdownForNotion: `${markdown}\n\n## JSON du diagnostic (schéma ${d.schemaVersion})\n\n\`\`\`json\n${jsonText}\n\`\`\``,
  emailHtml,
  jsonText,
} }];
