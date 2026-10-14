const messages = {
  fr: {
    skip: "Aller au contenu", "nav.results": "Résultats", "nav.method": "Méthode", "nav.sources": "Sources", "nav.reproduce": "Reproduire", "nav.aria": "Navigation principale", "metric.aria": "Mesure à comparer", "chart.aria": "Comparaison des scores", "page.title": "Roleplay Bench — Résultats", "page.description": "Comparaison reproductible de modèles ouverts compacts sur des benchmarks de jeu de rôle.",
    "hero.eyebrow": "BENCHMARK OUVERT · RÉSULTATS REPRODUCTIBLES", "hero.title": "Les petits modèles<br><em>ont du répondant.</em>",
    "hero.lede": "Une comparaison transparente de modèles compacts quantifiés, évalués sur le jeu de rôle et la cohérence des personnages.", "hero.cta": "Explorer les résultats",
    "hero.scoreLabel": "MEILLEUR SCORE ACTUEL · ROLEBENCH GÉNÉRALISATION", "hero.scoreNote": "ROUGE-L · score de recouvrement lexical", "hero.note": "Un petit banc d’essai, avec les limites affichées aussi clairement que les scores.",
    "stats.models": "modèles", "stats.variants": "variantes évaluées", "stats.repeats": "répétitions par variante",
    "results.kicker": "01 — LE SCORECARD", "results.title": "Même terrain.<br><em>Trois angles.</em>", "results.intro": "Les scores sont des moyennes de cinq exécutions indépendantes, accompagnées de leur écart-type. Choisissez une mesure pour comparer les variantes.", "results.scale": "ÉCHELLE 0–100", "results.chartCaption": "Moyenne ± écart-type · survolez une barre pour les détails.", "results.chartFootnote": "Une barre plus longue indique un score plus élevé dans cette mesure uniquement.", "results.tableCaption": "Résultats par variante, moyenne ± écart-type sur cinq runs", "results.fiveRuns": "5 runs · moyenne ± écart-type d’échantillon", "results.csv": "Télécharger le CSV ↗",
    "results.warning": "<strong>À lire avec prudence.</strong> RoleBench mesure le recouvrement lexical avec une seule réponse de référence, pas la qualité du jeu de rôle en pourcentage. CharacterEval utilise un autre jeu de données et un autre évaluateur. Comparez les modèles uniquement à l’intérieur d’une même colonne.",
    "metric.general": "Généralisation", "metric.specific": "Rôle spécifique", "metric.character": "CharacterEval", "table.variant": "Variante", "table.parameters": "Paramètres", "chart.general": "Généralisation", "chart.specific": "Rôle spécifique", "chart.character": "CharacterEval",
    "findings.kicker": "CE QUE DISENT LES DONNÉES", "findings.title": "Pas de gagnant<br><em>sur tous les fronts.</em>", "findings.intro": "Les écarts dépendent de la tâche. Ces constats décrivent ce petit sous-ensemble; ils ne prédisent pas les performances générales d’un modèle.", "finding.label": "MEILLEUR SCORE OBSERVÉ", "finding.delta": "d’avance sur le score suivant dans ce sous-ensemble.", "finding.noSecond": "Aucun autre score disponible pour cette mesure.",
    "benchmarks.kicker": "02 — LES MESURES", "benchmarks.title": "Trois façons<br>de rester <em>dans le rôle.</em>", "benchmarks.lede": "Chaque colonne répond à une question différente. Les valeurs n’ont pas la même signification d’un benchmark à l’autre.",
    "bench.generalTitle": "RoleBench · généralisation", "bench.generalBody": "10 prompts de test en anglais sur des rôles fixes. ROUGE-L F1 compare chaque réponse à la première réponse de référence RoleGPT. Cela mesure le chevauchement de formulation, pas une note humaine de qualité.", "bench.generalMeta": "10 prompts · 5 runs · graine fixe",
    "bench.specificTitle": "RoleBench · rôle spécifique", "bench.specificBody": "Les mêmes 10 rôles, mais des questions et références différentes, conçues pour tester les réponses spécifiques au rôle. Les scores de cette piste restent distincts de ceux de généralisation.", "bench.specificMeta": "10 prompts · mêmes rôles · questions différentes",
    "bench.characterTitle": "CharacterEval · CharacterRM", "bench.characterBody": "12 exemples chinois, un personnage par exemple, choisis pour couvrir les 12 dimensions disponibles. Le reward model CharacterRM note les réponses de 1 à 5; le score est transformé linéairement en 0–100 et les dimensions sont pondérées à égalité.", "bench.characterMeta": "12 exemples · 12 dimensions · évaluateur entraîné sur des annotations humaines",
    "method.kicker": "03 — COMMENT LIRE LE PROTOCOLE", "method.title": "Des choix visibles.<br><em>Des comparaisons utiles.</em>", "method.intro": "Modèles et quantifications utilisent les mêmes prompts et paramètres de génération au sein d’un benchmark. Les données brutes, versions des sources et sommes de contrôle sont conservées dans le dépôt.",
    "method.modelsTitle": "Modèles comparés", "method.modelsBody": "Google Gemma 4 E2B IT (2,3B paramètres actifs, 5,1B avec embeddings) et Qwen3-4B (4,0B au total). Les poids et jeux de données sont épinglés à des révisions précises. MLX tourne sur Apple Silicon; llama.cpp et les variantes GGUF tournent sur CUDA.",
    "method.quantTitle": "Quantification", "method.quantBody": "MLX utilise une quantification affine des poids par groupes de 64; les autres tenseurs restent en bfloat16. Les variantes GGUF utilisent des poids BF16, Q8_0 et Q4_K_M convertis depuis les révisions épinglées avec llama.cpp.",
    "method.repeatsTitle": "Répétitions et incertitude", "method.repeatsBody": "Chaque variante a un échauffement non noté puis cinq graines fixes. Le tableau présente la moyenne des scores par run et l’écart-type d’échantillon entre les runs. L’écart-type décrit la variation observée, pas un intervalle de confiance.",
    "method.samplingTitle": "Génération", "method.samplingBody": "RoleBench et CharacterEval: température 1, top-p 0,95, top-k 64, réflexion désactivée, limite de 512 nouveaux tokens. Les réglages officiels propres à IFBench, HLE et LiveCodeBench s’appliquent lorsqu’ils seront exécutés.", "method.hardwareTitle": "Environnement enregistré", "method.hardwareLoading": "Lecture de l’environnement de génération…",
    "pending.title": "Les résultats encore attendus", "pending.count": "03 benchmarks optionnels", "pending.intro": "Ces trois benchmarks supplémentaires restent à exécuter. Une case vide signifie qu’il n’existe pas encore cinq runs valides; elle ne vaut pas zéro.", "pending.ifbench": "300 consignes · exactitude « loose » officielle", "pending.hle": "Questions texte uniquement · jeu soumis à accès contrôlé et juge officiel", "pending.lcb": "1 055 problèmes v6-lite · pass@1 vérifié par exécution",
    "sources.kicker": "SOURCES & ATTRIBUTION", "sources.title": "Les briques<br><em>de l’évaluation.</em>", "sources.intro": "Jeux de données, modèles, métriques et évaluateurs renvoient à leurs publications ou implémentations d’origine. Les révisions exactes utilisées ici sont conservées avec les métadonnées du dépôt.", "sources.dataset": "JEU DE DONNÉES · APACHE-2.0", "sources.rolebench": "Jeu de rôle et protocole de référence RoleGPT. La configuration de score suit la piste RoleBench d’OpenCompass.", "sources.characterKind": "JEU ET ÉVALUATEUR · MIT", "sources.character": "Le sous-ensemble et le reward model CharacterRM des auteurs. Le score est une moyenne macro sur 12 dimensions.", "sources.ifbenchKind": "JEU DE DONNÉES · ODC-BY-1.0", "sources.ifbench": "Les 300 consignes du split de test officiel et le vérificateur d’instructions des auteurs.", "sources.hleKind": "JEU À ACCÈS CONTRÔLÉ", "sources.hle": "Questions texte uniquement; les réponses sont évaluées avec le format et le juge structuré officiels.", "sources.lcbKind": "JEU DE CODE · V6-LITE", "sources.lcb": "Problèmes de génération de code de la release v6-lite et vérification par exécution des tests.", "sources.modelsKind": "MODÈLES & RUNTIMES", "sources.modelsTitle": "Poids, conversion, quantification", "sources.models": "Les identifiants et révisions de modèles sont dans le registre. Les métadonnées d’environnement consignent MLX et llama.cpp.",
    "link.dataset": "Données ↗", "link.config": "Configuration ↗", "link.paper": "Article ACL ↗", "link.officialCode": "Code officiel ↗", "link.testSplit": "Split de test ↗", "link.officialEval": "Évaluation officielle ↗", "link.project": "Projet ↗",
    "reproduce.kicker": "04 — REPRODUIRE", "reproduce.title": "Du dépôt<br>au <em>score.</em>", "reproduce.lede": "Le code fixe les révisions, les seeds et les règles d’agrégation. Les fichiers bruts gardent une trace par réponse et par run.", "reproduce.repo": "Parcourir le dépôt ↗", "reproduce.reqTitle": "Préparer l’environnement", "reproduce.reqBody": "Les résultats MLX viennent d’un Mac Apple Silicon; les variantes GGUF ont été exécutées avec llama.cpp sur Linux/CUDA. La génération des deux familles demande un accès Hugging Face aux poids épinglés. HLE demande aussi l’accès au jeu et OPENAI_API_KEY pour le juge; LiveCodeBench utilise un exécuteur Docker isolé.", "reproduce.commands": "Afficher les commandes complètes", "reproduce.commandNote": "Le script de synthèse régénère le CSV, le JSON et la copie de données utilisée par cette page.", "reproduce.rawTitle": "Données et licences", "reproduce.rawBody": "Les exemples retenus, profils, sources épinglées et empreintes sont dans data/. Les réponses générées et scores par exemple sont dans results/. Respectez les licences et attributions des jeux de données sources.", "reproduce.dataLink": "Données et révisions ↗", "reproduce.scriptsLink": "Scripts du benchmark ↗", "reproduce.jsonLink": "Scorecard JSON ↗",
    "footer.note": "Des résultats documentés. Des comparaisons à leur juste portée.", "footer.top": "Retour en haut ↑", "footer.contributing": "Contribuer", "footer.open": "Code et méthode ouverts"
  },
  en: {
    skip: "Skip to content", "nav.results": "Results", "nav.method": "Method", "nav.sources": "Sources", "nav.reproduce": "Reproduce", "nav.aria": "Primary navigation", "metric.aria": "Metric to compare", "chart.aria": "Score comparison", "page.title": "Roleplay Bench — Results", "page.description": "Reproducible comparison of compact open-weight models on role-play benchmarks.",
    "hero.eyebrow": "OPEN BENCHMARK · REPRODUCIBLE RESULTS", "hero.title": "Small models<br><em>with character.</em>",
    "hero.lede": "A transparent comparison of compact, quantized models on role-play and character consistency.", "hero.cta": "Explore the results",
    "hero.scoreLabel": "TOP SCORE SO FAR · ROLEBENCH GENERALIZATION", "hero.scoreNote": "ROUGE-L · wording-overlap score", "hero.note": "A focused benchmark that makes its limits as visible as its scores.",
    "stats.models": "models", "stats.variants": "evaluated variants", "stats.repeats": "repetitions per variant",
    "results.kicker": "01 — THE SCORECARD", "results.title": "One testbed.<br><em>Three lenses.</em>", "results.intro": "Scores are means across five independent runs, shown with their standard deviations. Choose a metric to compare variants.", "results.scale": "SCALE 0–100", "results.chartCaption": "Mean ± standard deviation · hover over a bar for details.", "results.chartFootnote": "A longer bar means a higher score on this metric only.", "results.tableCaption": "Results by variant, mean ± standard deviation across five runs", "results.fiveRuns": "5 runs · mean ± sample standard deviation", "results.csv": "Download CSV ↗",
    "results.warning": "<strong>Read with care.</strong> RoleBench measures wording overlap with a single reference answer; it is not a percentage rating of role-play quality. CharacterEval uses a different dataset and evaluator. Compare models within each column only.",
    "metric.general": "Generalization", "metric.specific": "Role-specific", "metric.character": "CharacterEval", "table.variant": "Variant", "table.parameters": "Parameters", "chart.general": "Generalization", "chart.specific": "Role-specific", "chart.character": "CharacterEval",
    "findings.kicker": "WHAT THE DATA SAYS", "findings.title": "No single winner<br><em>across the board.</em>", "findings.intro": "The gaps depend on the task. These observations describe this small subset; they do not predict a model’s general performance.", "finding.label": "HIGHEST OBSERVED SCORE", "finding.delta": "ahead of the next score in this subset.", "finding.noSecond": "No other score is available for this metric.",
    "benchmarks.kicker": "02 — THE METRICS", "benchmarks.title": "Three ways<br>to stay <em>in character.</em>", "benchmarks.lede": "Each column answers a different question. Values do not mean the same thing from one benchmark to another.",
    "bench.generalTitle": "RoleBench · generalization", "bench.generalBody": "10 English test prompts across fixed roles. ROUGE-L F1 compares each answer with the first RoleGPT reference answer. It measures wording overlap, not a human quality rating.", "bench.generalMeta": "10 prompts · 5 runs · fixed seeds",
    "bench.specificTitle": "RoleBench · role-specific", "bench.specificBody": "The same 10 roles, with different questions and references designed to test role-specific responses. Keep this track’s scores separate from generalization.", "bench.specificMeta": "10 prompts · same roles · different questions",
    "bench.characterTitle": "CharacterEval · CharacterRM", "bench.characterBody": "12 Chinese examples, one character per example, selected to cover all 12 available dimensions. The authors’ CharacterRM reward model scores answers from 1 to 5; scores are linearly mapped to 0–100 and dimensions receive equal weight.", "bench.characterMeta": "12 examples · 12 dimensions · evaluator trained on human annotations",
    "method.kicker": "03 — READING THE PROTOCOL", "method.title": "Visible choices.<br><em>Useful comparisons.</em>", "method.intro": "Models and quantizations use the same prompts and generation settings within each benchmark. Raw outputs, source revisions, and checksums are kept in the repository.",
    "method.modelsTitle": "Models compared", "method.modelsBody": "Google Gemma 4 E2B IT (2.3B active parameters, 5.1B including embeddings) and Qwen3-4B (4.0B total). Model weights and datasets are pinned to specific revisions. MLX runs on Apple Silicon; llama.cpp and GGUF variants run on CUDA.",
    "method.quantTitle": "Quantization", "method.quantBody": "MLX uses affine weight quantization in groups of 64; other tensors remain in bfloat16. GGUF variants use BF16, Q8_0, and Q4_K_M weights converted from the pinned checkpoints with llama.cpp.",
    "method.repeatsTitle": "Repetitions and variation", "method.repeatsBody": "Each variant gets one unscored warm-up, then five fixed seeds. The table shows the mean of run-level scores and their sample standard deviation. Standard deviation describes observed variation, not a confidence interval.",
    "method.samplingTitle": "Generation", "method.samplingBody": "RoleBench and CharacterEval: temperature 1, top-p 0.95, top-k 64, thinking disabled, 512-token output limit. Official benchmark-specific settings will be used for IFBench, HLE, and LiveCodeBench when run.", "method.hardwareTitle": "Recorded environment", "method.hardwareLoading": "Loading generation environment…",
    "pending.title": "Results still to come", "pending.count": "03 additional benchmarks", "pending.intro": "These three additional benchmarks are still to be run. Scores stay blank until five valid runs are available; a blank cell does not mean zero.", "pending.ifbench": "300 instructions · official loose accuracy", "pending.hle": "Text-only questions · gated dataset and official judge", "pending.lcb": "1,055 v6-lite problems · execution-checked pass@1",
    "sources.kicker": "SOURCES & ATTRIBUTION", "sources.title": "What the<br><em>benchmarks build on.</em>", "sources.intro": "Datasets, models, metrics, and evaluators link to their original papers or implementations. Exact revisions used here are recorded in the repository metadata.", "sources.dataset": "DATASET · APACHE-2.0", "sources.rolebench": "Role-play dataset and RoleGPT reference protocol. The scoring setup follows the OpenCompass RoleBench track.", "sources.characterKind": "DATASET & EVALUATOR · MIT", "sources.character": "The authors’ fixed subset and CharacterRM reward model. The score is a macro average across 12 dimensions.", "sources.ifbenchKind": "DATASET · ODC-BY-1.0", "sources.ifbench": "The official 300-prompt test split and the authors’ instruction verifier.", "sources.hleKind": "GATED DATASET", "sources.hle": "Text-only questions; responses use the official format and structured judge.", "sources.lcbKind": "CODE DATASET · V6-LITE", "sources.lcb": "Code-generation problems from the v6-lite release, checked by executing the tests.", "sources.modelsKind": "MODELS & RUNTIMES", "sources.modelsTitle": "Weights, conversion, quantization", "sources.models": "Model IDs and revisions are listed in the registry. Environment metadata records MLX and llama.cpp.",
    "link.dataset": "Dataset ↗", "link.config": "Config ↗", "link.paper": "ACL paper ↗", "link.officialCode": "Official code ↗", "link.testSplit": "Test split ↗", "link.officialEval": "Official evaluation ↗", "link.project": "Project ↗",
    "reproduce.kicker": "04 — REPRODUCE", "reproduce.title": "From repo<br>to <em>score.</em>", "reproduce.lede": "The code pins revisions, seeds, and aggregation rules. Raw files preserve a record for every response and run.", "reproduce.repo": "Browse the repository ↗", "reproduce.reqTitle": "Set up the environment", "reproduce.reqBody": "MLX results come from Apple Silicon; GGUF variants ran with llama.cpp on Linux/CUDA. Both require access to the pinned Hugging Face weights. HLE also needs gated dataset access and OPENAI_API_KEY for judging; LiveCodeBench uses an isolated Docker runner.", "reproduce.commands": "Show the full commands", "reproduce.commandNote": "The summary script regenerates the CSV, JSON, and data copy used by this page.", "reproduce.rawTitle": "Data and licenses", "reproduce.rawBody": "Selected examples, profiles, pinned sources, and checksums live in data/. Generated answers and per-example scores are in results/. Follow the licenses and attribution terms for source datasets.", "reproduce.dataLink": "Data and revisions ↗", "reproduce.scriptsLink": "Benchmark scripts ↗", "reproduce.jsonLink": "Scorecard JSON ↗",
    "footer.note": "Documented results. Comparisons with the right scope.", "footer.top": "Back to top ↑", "footer.contributing": "Contributing", "footer.open": "Open code and method"
  }
};

const metrics = {
  rolebench_generalization: { mean: "rolebench_generalization_mean_100", sd: "rolebench_generalization_sd_100", title: "chart.general", overline: "ROLEBENCH · GENERALIZATION" },
  rolebench_role_specific: { mean: "rolebench_role_specific_mean_100", sd: "rolebench_role_specific_sd_100", title: "chart.specific", overline: "ROLEBENCH · ROLE-SPECIFIC" },
  charactereval: { mean: "charactereval_mean_100", sd: "charactereval_sd_100", title: "chart.character", overline: "CHARACTEREVAL · CHARACTER RM" }
};
const labels = { gemma4_e2b_it: "Gemma 4 E2B IT", qwen3_4b: "Qwen3-4B" };
let activeLanguage = localStorage.getItem("roleplay-bench-language") || "fr";
let summaryRows = [];
let activeMetric = "rolebench_generalization";

function translate() {
  const words = messages[activeLanguage];
  document.documentElement.lang = activeLanguage;
  document.title = words["page.title"];
  document.querySelector('meta[name="description"]').setAttribute("content", words["page.description"]);
  document.querySelectorAll("[data-i18n]").forEach(function (element) {
    const text = words[element.dataset.i18n];
    if (text !== undefined) element.innerHTML = text;
  });
  document.querySelectorAll("[data-i18n-aria]").forEach(function (element) {
    const text = words[element.dataset.i18nAria];
    if (text !== undefined) element.setAttribute("aria-label", text);
  });
  document.querySelectorAll("[data-language]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.language === activeLanguage));
  });
  document.querySelectorAll("[data-metric]").forEach(function (button) {
    const isActive = button.dataset.metric === activeMetric;
    button.classList.toggle("active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function pretty(value) {
  return new Intl.NumberFormat(activeLanguage === "fr" ? "fr-FR" : "en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
}

function scoreText(row, metricKey) {
  const metric = metrics[metricKey];
  const mean = row[metric.mean];
  return mean === null || mean === undefined ? "—" : pretty(mean) + " ± " + pretty(row[metric.sd]);
}

function variantLabel(row) {
  const variants = { mlx_4bit: "MLX · 4-bit", mlx_8bit: "MLX · 8-bit", gguf_bf16: "GGUF · BF16", gguf_q8_0: "GGUF · Q8_0", gguf_q4_k_m: "GGUF · Q4_K_M" };
  return variants[row.variant] || row.variant;
}

function modelTag(row) {
  return row.model_tag || row.quantization || (labels[row.model_key] + " · " + variantLabel(row));
}

function parameterLabel(row) {
  if (row.model_key === "gemma4_e2b_it") return activeLanguage === "fr" ? "2,3B actifs · 5,1B total" : "2.3B active · 5.1B total";
  return activeLanguage === "fr" ? "4,0B total · 3,6B hors embeddings" : "4.0B total · 3.6B excl. embeddings";
}

function scoredRows(metricKey) {
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.mean] === "number"; });
}

function renderChart() {
  const metric = metrics[activeMetric];
  const rows = scoredRows(activeMetric).sort(function (a, b) { return b[metric.mean] - a[metric.mean]; });
  const title = messages[activeLanguage][metric.title];
  document.getElementById("chart-title").textContent = title;
  document.getElementById("chart-overline").textContent = metric.overline;
  document.getElementById("metric-panel").setAttribute("aria-labelledby", { rolebench_generalization: "tab-general", rolebench_role_specific: "tab-specific", charactereval: "tab-character" }[activeMetric]);
  document.getElementById("bar-chart").innerHTML = rows.map(function (row, index) {
    const value = row[metric.mean];
    const width = Math.max(2, value);
    const label = modelTag(row);
    return '<div class="bar-row ' + (index === 0 ? "is-best" : "") + '" title="' + label + ": " + scoreText(row, activeMetric) + '"><span class="bar-label">' + label + '</span><div class="bar-track" role="img" aria-label="' + label + ": " + scoreText(row, activeMetric) + '"><div class="bar-fill" style="width:' + width + '%"></div></div><span class="bar-value">' + scoreText(row, activeMetric) + '</span></div>';
  }).join("");
}

function renderTable() {
  const rows = summaryRows.filter(function (row) {
    return typeof row.rolebench_generalization_mean_100 === "number" || typeof row.charactereval_mean_100 === "number";
  });
  const table = document.getElementById("score-table");
  table.innerHTML = rows.map(function (row) {
    return '<tr><td><div class="model-cell"><span class="model-name">' + modelTag(row) + '</span><span class="model-chip">' + variantLabel(row) + '</span></div></td><td>' + scoreText(row, "rolebench_generalization") + '</td><td>' + scoreText(row, "rolebench_role_specific") + '</td><td>' + scoreText(row, "charactereval") + '</td><td>' + parameterLabel(row) + '</td></tr>';
  }).join("");
}

function renderInsights() {
  const metricOrder = ["rolebench_generalization", "rolebench_role_specific", "charactereval"];
  const root = document.getElementById("finding-grid");
  root.innerHTML = metricOrder.map(function (metricKey) {
    const metric = metrics[metricKey];
    const rows = scoredRows(metricKey).sort(function (a, b) { return b[metric.mean] - a[metric.mean]; });
    if (!rows.length) return "";
    const winner = rows[0];
    const gap = rows.length > 1 ? pretty(winner[metric.mean] - rows[1][metric.mean]) : null;
    const detail = gap === null ? messages[activeLanguage]["finding.noSecond"] : gap + " " + messages[activeLanguage]["finding.delta"];
    const winnerName = modelTag(winner);
    return '<article class="finding-card"><p class="finding-eyebrow">' + messages[activeLanguage]["finding.label"] + " · " + messages[activeLanguage][metric.title].toUpperCase() + '</p><strong>' + pretty(winner[metric.mean]) + ' ± ' + pretty(winner[metric.sd]) + '</strong><p>' + winnerName + '. ' + detail + '</p></article>';
  }).join("");
}

function renderHero() {
  const rows = scoredRows("rolebench_generalization").sort(function (a, b) { return b.rolebench_generalization_mean_100 - a.rolebench_generalization_mean_100; });
  if (rows.length) {
    document.getElementById("hero-score-value").textContent = pretty(rows[0].rolebench_generalization_mean_100);
    document.getElementById("hero-score-model").textContent = modelTag(rows[0]) + " · " + (activeLanguage === "fr" ? "moyenne ± " : "mean ± ") + pretty(rows[0].rolebench_generalization_sd_100);
  }
  const models = new Set(summaryRows.filter(function (row) { return typeof row.rolebench_generalization_mean_100 === "number"; }).map(function (row) { return row.model_key; }));
  const variants = summaryRows.filter(function (row) { return typeof row.rolebench_generalization_mean_100 === "number"; });
  document.getElementById("stat-models").textContent = String(models.size);
  document.getElementById("stat-variants").textContent = String(variants.length);
}

function renderEnvironment(environment) {
  const hardware = environment.hardware || {};
  const software = environment.software || {};
  const memory = hardware.memory_gib ? new Intl.NumberFormat(activeLanguage === "fr" ? "fr-FR" : "en-US", { maximumFractionDigits: 1 }).format(hardware.memory_gib) + " GB" : "";
  const mlxDetail = ["MLX", hardware.chip, memory, hardware.macos ? "macOS " + hardware.macos : "", software.mlx ? "MLX-LM " + software.mlx : ""].filter(Boolean).join(" · ");
  const gguf = environment.gguf_evaluation || {};
  const ggufHardware = gguf.hardware || {};
  const ggufSoftware = gguf.software || {};
  const ggufDetail = ["GGUF", ggufHardware.gpu, ggufHardware.os, ggufSoftware.llama_cpp ? "llama.cpp " + ggufSoftware.llama_cpp.slice(0, 7) : ""].filter(Boolean).join(" · ");
  const detail = [mlxDetail, ggufDetail].filter(Boolean).join("  |  ") || (software.python ? "Python " + software.python : "");
  document.getElementById("environment-summary").textContent = detail || "—";
}

function renderAll() {
  translate();
  renderHero();
  renderTable();
  renderChart();
  renderInsights();
}

document.querySelectorAll("[data-language]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeLanguage = button.dataset.language;
    localStorage.setItem("roleplay-bench-language", activeLanguage);
    renderAll();
  });
});
document.querySelectorAll("[data-metric]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeMetric = button.dataset.metric;
    renderAll();
  });
});

Promise.all([fetch("data/summary.json").then(function (response) { if (!response.ok) throw new Error("summary"); return response.json(); }), fetch("data/environment.json").then(function (response) { if (!response.ok) throw new Error("environment"); return response.json(); })])
  .then(function (data) {
    summaryRows = data[0];
    renderEnvironment(data[1]);
    renderAll();
  })
  .catch(function () {
    document.getElementById("hero-score-value").textContent = "—";
    document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "Impossible de charger les données." : "Could not load the result data.";
  });

translate();
