const messages = {
  fr: {
    skip: "Aller au contenu",
    "nav.results": "Résultats",
    "nav.method": "Méthode",
    "nav.repo": "Dépôt ↗",
    "nav.aria": "Navigation principale",
    "metric.aria": "Benchmark à comparer",
    "results.categories.aria": "Catégorie de benchmarks",
    "results.categories.roleplay": "Roleplay",
    "results.categories.tools": "Instructions et outils",
    "results.categories.all": "Tous",
    "chart.aria": "Comparaison des résultats",
    "view.aria": "Affichage des résultats",
    "view.delta": "Δ vs BF16",
    "view.score": "Score",
    "page.title": "Quantization Bench — Résultats",
    "page.description": "Résultats de benchmarks locaux de roleplay, de suivi des consignes et d’utilisation d’outils.",
    "hero.eyebrow": "QUANTIFICATION DE MODÈLES OUVERTS",
    "hero.title": "Quantization<br><em>Bench</em>",
    "hero.lede": "La perte mesurée, benchmark par benchmark.",
    "hero.cta": "Voir les résultats",
    "hero.scoreLabel": "DELTA MOYEN · GGUF Q4_K_M VS BF16",
    "hero.scoreNote": "5 MESURES LOCALES · 6 MODÈLES LOCAUX",
    "hero.summary": "Δ vs BF16 · 5 runs appariés",
    "stats.models": "modèles",
    "stats.variants": "variantes",
    "stats.runs": "runs",
    "results.title": "Résultats",
    "results.caption": "Δ vs BF16 · points sur 100",
    "results.modelFilter": "Modèles",
    "results.modelSearch": "Rechercher un modèle ou un format",
    "results.selectAll": "Tout afficher",
    "results.selectNone": "Tout masquer",
    "results.modelOptions": "Sélection des configurations affichées",
    "results.noSearchResults": "Aucun modèle ne correspond à cette recherche.",
    "results.noVisibleModels": "Aucun modèle sélectionné. Cochez une configuration pour afficher les résultats.",
    "results.noMatchingResults": "Aucun résultat pour les configurations sélectionnées dans cette vue.",
    "results.chartCaption": "Variation moyenne face au BF16 du même modèle · points /100",
    "results.scoreCaption": "Score moyen du benchmark sélectionné · points /100",
    "results.ifbenchCaption": "IFBench · exactitude souple sur 300 consignes · points /100",
    "results.legendMean": "Moyenne",
    "results.legendSpread": "Écart-type (±1σ)",
    "results.showStdDev": "Afficher les écarts-types",
    "results.hideStdDev": "Masquer les écarts-types",
    "results.scoreInsight": "Score moyen le plus élevé",
    "results.deltaInsight": "Meilleure préservation face au BF16",
    "results.scoreDescription.rolebench_generalization": "ROUGE-L F1 ×100 sur 10 réponses, moyenné sur 5 runs. C’est une similarité de texte, pas un taux de réussite.",
    "results.scoreDescription.rolebench_role_specific": "ROUGE-L F1 ×100 sur 10 réponses liées à un rôle, moyenné sur 5 runs. C’est une similarité de texte, pas un taux de réussite.",
    "results.scoreDescription.charactereval": "CharacterRM ×100 sur 12 exemples, moyenné sur 5 runs.",
    "results.scoreDescription.ifbench": "Pourcentage des 300 consignes où toutes les contraintes passent le vérificateur souple officiel, en un passage. Un seul passage ne permet pas de calculer un écart-type entre runs.",
    "results.scoreDescription.automationbench": "Taux de tâches AutomationBench terminées correctement avec des outils simulés.",
    "results.deltaDescription": "Variation quantifié − BF16 apparié. Une valeur plus haute signifie une meilleure préservation.",
    "table.model": "Modèle et version",
    "results.runs": "5 runs · moyenne ± écart-type",
    "results.pairedRuns": "5 runs appariés · moyenne ± écart-type",
    "results.meanOnly": "5 runs · moyenne",
    "results.pairedMeanOnly": "5 runs appariés · moyenne",
    "results.singlePass": "1 passage complet · 300 consignes · écart-type non calculable",
    "results.singlePassAutomationbench": "1 passage complet · 600 tâches · écart-type non calculable",
    "results.pendingHeading": "Pas encore de résultats pour ce benchmark",
    "results.pendingStatus": "Aucune mesure terminée n’est publiée pour les modèles de cette page.",
    "results.notRunLabel": "Pas encore mesuré",
    "results.pendingAllNote": "La catégorie All regroupe les benchmarks, pas leurs scores : chaque mesure garde son protocole et son échelle.",
    "results.ifbenchPending": "IFBench vérifie localement 300 consignes avec les validateurs automatiques officiels.",
    "results.ifbenchOutputDetails": "Limite : {tokens} tokens · réponses tronquées : {count}",
    "results.automationbenchPending": "AutomationBench mesure la réussite stricte sur 600 tâches utilisant des outils simulés.",
    "results.openBenchmark": "Protocole officiel ↗",
    "table.score": "Score du benchmark",
    "results.csv": "CSV ↗",
    "method.title": "Protocole",
    "method.repo": "Détails et données ↗",
    "method.models": "Modèles",
    "method.modelsSummary": "6 checkpoints locaux",
    "method.formats": "Formats",
    "method.scoring": "Scores",
    "method.environment": "Environnements",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 comparé à une référence RoleGPT.",
    "details.specific": "10 prompts liés à un rôle · ROUGE-L F1.",
    "details.character": "12 exemples · CharacterRM · note de 1–5 ramenée à 0–100.",
    "details.ifbench": "300 prompts · vérificateur officiel · un passage local par variante, température 0. L’écart-type entre runs n’est pas calculable.",
    "details.automationbench": "600 tâches d’agents réparties dans six domaines, avec 47 outils SaaS simulés · réussite stricte des tâches.",
    "details.allCategory": "Tous les résultats proviennent de modèles exécutés localement. Les scores restent séparés, car chaque benchmark a son propre protocole et son échelle.",
    "details.protocol": "Δ = score GGUF quantifié − BF16 du même modèle · 5 runs appariés pour RoleBench et CharacterEval. IFBench et AutomationBench sont évalués en un passage local complet, sans écart-type entre runs.",
    "details.sd": "Pour RoleBench et CharacterEval, l’écart-type d’échantillon est calculé sur les cinq scores moyens de run ; pour Δ, sur les cinq différences appariées. IFBench et AutomationBench n’ont qu’un passage.",
    "details.reading": "Comparez les modèles à l'intérieur d'un même benchmark : les scores entre colonnes ne sont pas équivalents.",
    "details.claims": "Les pertes annoncées par les éditeurs ne sont pas référencées.",
    "details.brandCredits": "Logos des familles Gemma (Google), Qwen, Mistral et Liquid AI : <a href=\"https://ai.google.dev/gemma/docs\">Google</a> · <a href=\"https://github.com/QwenLM/qwenlm.github.io\">Qwen</a> · <a href=\"https://mistral.ai/brand/\">Mistral</a> · <a href=\"https://www.liquid.ai/\">Liquid AI</a>. Marques affichées pour identifier les modèles évalués, sans affiliation ni approbation."
  },
  en: {
    skip: "Skip to content",
    "nav.results": "Results",
    "nav.method": "Method",
    "nav.repo": "Repository ↗",
    "nav.aria": "Primary navigation",
    "metric.aria": "Benchmark to compare",
    "results.categories.aria": "Benchmark category",
    "results.categories.roleplay": "Roleplay",
    "results.categories.tools": "Instructions & tools",
    "results.categories.all": "All",
    "chart.aria": "Results comparison",
    "view.aria": "Results view",
    "view.delta": "Δ vs BF16",
    "view.score": "Score",
    "page.title": "Quantization Bench — Results",
    "page.description": "Local model results for roleplay, instruction following, and tool use.",
    "hero.eyebrow": "OPEN MODEL QUANTIZATION",
    "hero.title": "Quantization<br><em>Bench</em>",
    "hero.lede": "Measured loss, benchmark by benchmark.",
    "hero.cta": "View results",
    "hero.scoreLabel": "AVERAGE DELTA · GGUF Q4_K_M VS BF16",
    "hero.scoreNote": "5 LOCAL METRICS · 6 LOCAL MODELS",
    "hero.summary": "Δ vs BF16 · 5 paired runs",
    "stats.models": "models",
    "stats.variants": "variants",
    "stats.runs": "runs",
    "results.title": "Results",
    "results.caption": "Δ vs BF16 · points on a 100-point scale",
    "results.modelFilter": "Models",
    "results.modelSearch": "Search models or formats",
    "results.selectAll": "Show all",
    "results.selectNone": "Hide all",
    "results.modelOptions": "Select visible model configurations",
    "results.noSearchResults": "No models match this search.",
    "results.noVisibleModels": "No models selected. Select a configuration to show results.",
    "results.noMatchingResults": "No results for the selected configurations in this view.",
    "results.chartCaption": "Mean change against the same model's BF16 baseline · points /100",
    "results.scoreCaption": "Mean score on the selected benchmark · points /100",
    "results.ifbenchCaption": "IFBench · loose accuracy over 300 instructions · points /100",
    "results.legendMean": "Mean",
    "results.legendSpread": "Standard deviation (±1 SD)",
    "results.showStdDev": "Show standard deviations",
    "results.hideStdDev": "Hide standard deviations",
    "results.scoreInsight": "Highest mean score",
    "results.deltaInsight": "Best preservation against BF16",
    "results.scoreDescription.rolebench_generalization": "ROUGE-L F1 ×100 over 10 responses, averaged across 5 runs. This measures text similarity, not success rate.",
    "results.scoreDescription.rolebench_role_specific": "ROUGE-L F1 ×100 over 10 role-specific responses, averaged across 5 runs. This measures text similarity, not success rate.",
    "results.scoreDescription.charactereval": "CharacterRM ×100 over 12 examples, averaged across 5 runs.",
    "results.scoreDescription.ifbench": "Percentage of IFBench’s 300 instructions where every constraint passes the official loose verifier, measured in one complete pass. One pass cannot produce a run-level standard deviation.",
    "results.scoreDescription.automationbench": "Rate of AutomationBench tasks completed correctly using simulated tools.",
    "results.deltaDescription": "Quantized − paired BF16 change. A higher value means better preservation.",
    "table.model": "Model and variant",
    "results.runs": "5 runs · mean ± sample SD",
    "results.pairedRuns": "5 paired runs · mean ± sample SD",
    "results.meanOnly": "5 runs · mean",
    "results.pairedMeanOnly": "5 paired runs · mean",
    "results.singlePass": "1 complete pass · 300 instructions · SD unavailable",
    "results.singlePassAutomationbench": "1 complete pass · 600 tasks · SD unavailable",
    "results.pendingHeading": "No results for this benchmark yet",
    "results.pendingStatus": "No completed measurement has been published for the models on this page.",
    "results.notRunLabel": "Not measured yet",
    "results.pendingAllNote": "All lists the benchmarks; it does not combine their scores. Each measure keeps its own protocol and scale.",
    "results.ifbenchPending": "IFBench locally checks 300 instructions with the official automatic verifiers.",
    "results.ifbenchOutputDetails": "Limit: {tokens} tokens · truncated responses: {count}",
    "results.automationbenchPending": "AutomationBench measures strict completion across 600 tasks using simulated tools.",
    "results.openBenchmark": "Official protocol ↗",
    "table.score": "Benchmark score",
    "results.csv": "CSV ↗",
    "method.title": "Protocol",
    "method.repo": "Details and data ↗",
    "method.models": "Models",
    "method.modelsSummary": "6 local model checkpoints",
    "method.formats": "Formats",
    "method.scoring": "Scoring",
    "method.environment": "Runtimes",
    "details.title": "Benchmarks & scoring",
    "details.general": "10 prompts · ROUGE-L F1 against a RoleGPT reference.",
    "details.specific": "10 role-specific prompts · ROUGE-L F1.",
    "details.character": "12 examples · CharacterRM · score mapped from 1–5 to 0–100.",
    "details.ifbench": "300 prompts · official verifier · one local pass per variant at temperature 0. Run-level standard deviation is unavailable.",
    "details.automationbench": "600 agent tasks across six domains, using 47 simulated SaaS tools · strict task completion.",
    "details.allCategory": "All results come from locally run models. Scores remain separate because each benchmark has its own protocol and scale.",
    "details.protocol": "Δ = quantized GGUF score − same-model BF16 score · 5 paired runs for RoleBench and CharacterEval. IFBench and AutomationBench use one complete local pass and have no run-level standard deviation.",
    "details.sd": "For RoleBench and CharacterEval, sample standard deviation is calculated across five run-level mean scores; for Δ, across five paired differences. IFBench and AutomationBench use one pass.",
    "details.reading": "Compare models within one benchmark: scores across columns are not equivalent.",
    "details.claims": "Publisher-reported loss claims are not included.",
    "details.brandCredits": "Logos for the Gemma (Google), Qwen, Mistral, and Liquid AI model families: <a href=\"https://ai.google.dev/gemma/docs\">Google</a> · <a href=\"https://github.com/QwenLM/qwenlm.github.io\">Qwen</a> · <a href=\"https://mistral.ai/brand/\">Mistral</a> · <a href=\"https://www.liquid.ai/\">Liquid AI</a>. Marks identify the evaluated models; this project is not affiliated with or endorsed by these companies."
  }
};

const metrics = {
  rolebench_generalization: {
    mean: "rolebench_generalization_mean_100",
    sd: "rolebench_generalization_sd_100",
    delta: "rolebench_generalization_delta_vs_bf16_mean_pp",
    deltaSd: "rolebench_generalization_delta_vs_bf16_sd_pp"
  },
  rolebench_role_specific: {
    mean: "rolebench_role_specific_mean_100",
    sd: "rolebench_role_specific_sd_100",
    delta: "rolebench_role_specific_delta_vs_bf16_mean_pp",
    deltaSd: "rolebench_role_specific_delta_vs_bf16_sd_pp"
  },
  charactereval: {
    mean: "charactereval_mean_100",
    sd: "charactereval_sd_100",
    delta: "charactereval_delta_vs_bf16_mean_pp",
    deltaSd: "charactereval_delta_vs_bf16_sd_pp"
  },
  automationbench: {
    mean: "automationbench_task_success_mean_100",
    sd: "automationbench_task_success_sd_100",
    runs: "automationbench_n_runs",
    examples: "automationbench_n_examples",
    passLabel: "results.singlePassAutomationbench"
  },
  ifbench: {
    mean: "ifbench_prompt_accuracy_mean_100",
    sd: "ifbench_prompt_accuracy_sd_100",
    runs: "ifbench_n_runs",
    examples: "ifbench_n_examples"
  }
};

const benchmarkCatalog = {
  rolebench_generalization: { title: "RoleBench Generalization", category: "roleplay" },
  rolebench_role_specific: { title: "RoleBench Role-Specific", category: "roleplay" },
  charactereval: { title: "CharacterEval", category: "roleplay" },
  automationbench: { title: "AutomationBench", category: "tools", description: "results.automationbenchPending", link: "https://github.com/zapier/AutomationBench" },
  ifbench: { title: "IFBench", category: "tools", description: "results.ifbenchPending", link: "https://github.com/allenai/IFBench" }
};
const categoryMetrics = {
  roleplay: ["rolebench_generalization", "rolebench_role_specific", "charactereval"],
  tools: ["automationbench", "ifbench"],
  all: ["rolebench_generalization", "rolebench_role_specific", "charactereval", "automationbench", "ifbench"]
};
const benchmarkTabs = {
  rolebench_generalization: "tab-general",
  rolebench_role_specific: "tab-specific",
  charactereval: "tab-character",
  automationbench: "tab-automationbench",
  ifbench: "tab-ifbench"
};
const modelBrands = {
  gemma4_e2b_it: { monogram: "G", css: "brand-gemma", label: "Gemma", src: "assets/model-logos/google-g.png" },
  qwen3_4b: { monogram: "Q", css: "brand-qwen", label: "Qwen", src: "assets/model-logos/qwen.png" },
  qwen3_5_4b: { monogram: "Q", css: "brand-qwen", label: "Qwen", src: "assets/model-logos/qwen.png" },
  ministral_3_3b_instruct_2512: { monogram: "M", css: "brand-ministral", label: "Mistral", src: "assets/model-logos/mistral.png" },
  lfm2_5_2_6b: { monogram: "L", css: "brand-lfm", label: "Liquid AI", src: "assets/model-logos/liquid-icon.svg" }
};
let activeLanguage = localStorage.getItem("quantization-bench-language") === "en" ? "en" : "fr";
let summaryRows = [];
let selectedModelIds = new Set();
let activeMetric = "rolebench_generalization";
let activeCategory = "roleplay";
let activeView = "score";
const stdDevVisibility = {
  rolebench_generalization: false,
  rolebench_role_specific: false,
  charactereval: false,
  ifbench: false
};

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
  document.querySelectorAll("[data-i18n-placeholder]").forEach(function (element) {
    const text = words[element.dataset.i18nPlaceholder];
    if (text !== undefined) element.setAttribute("placeholder", text);
  });
  const deltaMode = activeDeltaMode();
  const hasDeviation = hasStdDev(activeMetric, deltaMode);
  const showStdDev = Boolean(stdDevVisibility[activeMetric] && hasDeviation);
  const pendingBenchmark = isPendingBenchmark();
  const captionKey = activeMetric === "ifbench"
    ? "results.ifbenchCaption"
    : deltaMode ? "results.caption" : "results.scoreCaption";
  document.querySelector(".section-intro").textContent = words[captionKey];
  document.querySelector(".chart-caption").textContent = activeMetric === "ifbench"
    ? words["results.ifbenchCaption"]
    : words[deltaMode ? "results.chartCaption" : "results.scoreCaption"];
  const metricRunCount = metrics[activeMetric] && metrics[activeMetric].runs
    ? summaryRows.find(function (row) { return typeof row[metrics[activeMetric].runs] === "number"; })?.[metrics[activeMetric].runs]
    : null;
  document.getElementById("result-runs-label").textContent = pendingBenchmark
    ? words["results.notRunLabel"]
    : metricRunCount === 1
      ? words[metrics[activeMetric].passLabel || "results.singlePass"]
      : deltaMode
        ? words[showStdDev ? "results.pairedRuns" : "results.pairedMeanOnly"]
        : words[showStdDev ? "results.runs" : "results.meanOnly"];
  const stdDevButton = document.getElementById("stddev-toggle");
  const stdDevButtonLabel = words[showStdDev ? "results.hideStdDev" : "results.showStdDev"];
  stdDevButton.setAttribute("aria-pressed", String(showStdDev));
  stdDevButton.setAttribute("aria-label", stdDevButtonLabel);
  document.getElementById("stddev-toggle-label").textContent = stdDevButtonLabel;
  document.getElementById("legend-sd").hidden = !showStdDev;
  document.getElementById("model-filter").hidden = pendingBenchmark;
  if (pendingBenchmark) setModelFilterOpen(false);
  document.getElementById("stddev-toggle").hidden = pendingBenchmark || !hasDeviation;
  document.querySelector(".view-switch").hidden = pendingBenchmark || !metrics[activeMetric] || !metrics[activeMetric].delta;
  document.getElementById("scale-label").hidden = pendingBenchmark;
  document.querySelectorAll("[data-category]").forEach(function (button) {
    const active = button.dataset.category === activeCategory;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.querySelectorAll("[data-metric]").forEach(function (button) {
    button.hidden = !categoryMetrics[activeCategory].includes(button.dataset.metric);
  });
  document.querySelectorAll("[data-language]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.language === activeLanguage));
  });
  document.querySelectorAll("[data-metric]").forEach(function (button) {
    const active = button.dataset.metric === activeMetric;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  document.querySelectorAll("[data-view]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(button.dataset.view === activeView));
  });
  const caption = pendingBenchmark
    ? benchmarkCatalog[activeMetric].title + " · " + words["results.pendingHeading"]
    : deltaMode ? words["results.chartCaption"] : words["results.scoreCaption"];
  document.querySelector(".chart-caption").textContent = caption;
  document.getElementById("scale-label").textContent = deltaMode ? "± points" : "0–100";
  document.querySelector(".section-intro").textContent = pendingBenchmark
    ? words["results.pendingStatus"]
    : deltaMode ? words["results.caption"] : words["results.scoreCaption"];
  updateModelFilterCount(words);
}

function pretty(value) {
  return new Intl.NumberFormat(activeLanguage === "fr" ? "fr-FR" : "en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, function (character) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character];
  });
}

function modelTag(row) {
  if (row.model_tag || row.quantization) return row.model_tag || row.quantization;
  const name = (row.model_name || row.model_key || "model").toLowerCase().replaceAll(" ", "-");
  const quant = row.variant || "unknown";
  return name + "@" + quant.replace(/^gguf_/, "").replace(/^mlx_/, "mlx");
}

function brandInfo(row) {
  return modelBrands[row.model_key] || { monogram: "?", css: "brand-other", label: row.model_name || "Model" };
}

function modelDisplayName(row) {
  return row.model_name || row.model_key || "Model";
}

function variantLabel(row) {
  const variant = row.variant || "";
  const labels = {
    gguf_bf16: "GGUF · BF16",
    gguf_q8_0: "GGUF · Q8_0",
    gguf_q4_k_m: "GGUF · Q4_K_M",
    mlx_4bit: "MLX · 4-bit",
    mlx_8bit: "MLX · 8-bit"
  };
  return row["variant_label_" + activeLanguage] || row.variant_label || labels[variant] || row.model_tag || row.quantization || variant;
}

function chartVariantLabel(row) {
  return variantLabel(row);
}

function modelConfigId(row) {
  return row.model_tag || row.quantization || [row.model_key, row.variant].join("::");
}

function modelConfigs() {
  const seen = new Set();
  return summaryRows.filter(function (row) {
    const id = modelConfigId(row);
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

function defaultModelIds() {
  return new Set(modelConfigs().filter(function (row) {
    return row.variant === "gguf_bf16" || row.variant === "gguf_q8_0";
  }).map(modelConfigId));
}

function updateModelFilterCount(words) {
  const configs = modelConfigs();
  const selected = configs.filter(function (row) { return selectedModelIds.has(modelConfigId(row)); }).length;
  const total = configs.length;
  const status = activeLanguage === "fr"
    ? selected + " sur " + total + " configurations affichées"
    : selected + " of " + total + " configurations shown";
  document.getElementById("model-filter-count").textContent = selected + " / " + total;
  document.getElementById("model-filter-status").textContent = status;
  document.getElementById("model-filter-toggle").setAttribute("aria-label", (words || messages[activeLanguage])["results.modelFilter"] + ": " + status);
}

function renderModelFilterOptions() {
  const families = new Map();
  modelConfigs().forEach(function (row) {
    const family = row.model_key || row.model_name || "other";
    if (!families.has(family)) families.set(family, []);
    families.get(family).push(row);
  });
  const groups = Array.from(families.values());
  document.getElementById("model-filter-options").innerHTML = groups.map(function (rows) {
    const first = rows[0];
    const name = modelDisplayName(first);
    const variants = rows.map(function (row) {
      const id = modelConfigId(row);
      const searchable = [modelDisplayName(row), variantLabel(row), modelTag(row), row.parameters || ""].join(" ").toLocaleLowerCase();
      return '<label class="model-filter-option" data-filter-text="' + escapeHtml(searchable) + '"><input type="checkbox" data-model-id value="' + escapeHtml(id) + '"' + (selectedModelIds.has(id) ? " checked" : "") + '><span>' + escapeHtml(variantLabel(row)) + '</span></label>';
    }).join("");
    return '<fieldset class="model-filter-family"><legend><label class="model-family-toggle"><input type="checkbox" data-family-toggle><span class="model-family-logo">' + modelLogo(first) + '</span><strong>' + escapeHtml(name) + '</strong><small aria-hidden="true">' + rows.length + '</small></label></legend><div class="model-filter-variants">' + variants + '</div></fieldset>';
  }).join("");
  syncFamilyToggles();
  applyModelFilterSearch();
  updateModelFilterCount();
}

function syncFamilyToggles() {
  document.querySelectorAll(".model-filter-family").forEach(function (group) {
    const variants = Array.from(group.querySelectorAll("[data-model-id]"));
    const selectedCount = variants.filter(function (input) { return selectedModelIds.has(input.value); }).length;
    const familyToggle = group.querySelector("[data-family-toggle]");
    familyToggle.checked = selectedCount > 0;
    familyToggle.indeterminate = selectedCount > 0 && selectedCount < variants.length;
  });
}

function applyModelFilterSearch() {
  const query = document.getElementById("model-filter-search").value.trim().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase();
  let matchingCount = 0;
  document.querySelectorAll(".model-filter-family").forEach(function (group) {
    let groupMatches = 0;
    group.querySelectorAll(".model-filter-option").forEach(function (option) {
      const searchable = option.dataset.filterText.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      const matches = searchable.includes(query);
      option.hidden = !matches;
      if (matches) groupMatches += 1;
    });
    group.hidden = groupMatches === 0;
    matchingCount += groupMatches;
  });
  document.getElementById("model-filter-no-results").hidden = matchingCount > 0;
}

function initializeModelSelection() {
  const allIds = new Set(modelConfigs().map(modelConfigId));
  const params = new URLSearchParams(window.location.search);
  if (params.has("models")) {
    selectedModelIds = params.get("models") === "all"
      ? allIds
      : new Set(params.get("models").split(",").filter(function (id) { return allIds.has(id); }));
  } else {
    selectedModelIds = defaultModelIds();
  }
  renderModelFilterOptions();
}

function updateModelFilterUrl() {
  const allIds = modelConfigs().map(modelConfigId).sort();
  const selectedIds = Array.from(selectedModelIds).filter(function (id) { return allIds.includes(id); }).sort();
  const defaults = Array.from(defaultModelIds()).sort();
  const params = new URLSearchParams(window.location.search);
  if (selectedIds.length === allIds.length) params.set("models", "all");
  else if (selectedIds.length === defaults.length && selectedIds.every(function (id, index) { return id === defaults[index]; })) params.delete("models");
  else params.set("models", selectedIds.join(","));
  const query = params.toString();
  const url = window.location.pathname + (query ? "?" + query : "") + window.location.hash;
  window.history.replaceState(null, "", url);
}

function setModelFilterOpen(open) {
  const button = document.getElementById("model-filter-toggle");
  const popover = document.getElementById("model-filter-popover");
  button.setAttribute("aria-expanded", String(open));
  popover.hidden = !open;
  if (open) document.getElementById("model-filter-search").focus();
}

function modelLogo(row) {
  const brand = brandInfo(row);
  const image = brand.src ? '<img src="' + escapeHtml(brand.src) + '" alt="" loading="lazy">' : escapeHtml(brand.monogram);
  return '<span class="model-logo ' + brand.css + (brand.src ? ' has-logo' : '') + '" aria-hidden="true">' + image + '</span>';
}

function scoreText(row, metricKey, includeStdDev) {
  const metric = metrics[metricKey];
  const mean = row[metric.mean];
  if (typeof mean !== "number") return "—";
  if (!includeStdDev) return pretty(mean);
  return typeof row[metric.sd] === "number"
    ? pretty(mean) + " ± " + pretty(row[metric.sd])
    : pretty(mean);
}

function deltaText(row, metricKey, includeStdDev) {
  const metric = metrics[metricKey];
  const value = row[metric.delta];
  if (typeof value !== "number") return "—";
  const signed = value > 0 ? "+" + pretty(value) : value < 0 ? "−" + pretty(Math.abs(value)) : pretty(0);
  const deviation = typeof row[metric.deltaSd] === "number" ? " ± " + pretty(row[metric.deltaSd]) : "";
  return signed + (includeStdDev ? deviation : "") + " pp";
}

function hasStdDev(metricKey, deltaMode) {
  const metric = metrics[metricKey];
  if (!metric) return false;
  const deviationKey = deltaMode ? metric.deltaSd : metric.sd;
  return Boolean(deviationKey && summaryRows.some(function (row) {
    return typeof row[deltaMode ? metric.delta : metric.mean] === "number" && typeof row[deviationKey] === "number";
  }));
}

function scoredRows(metricKey) {
  if (!metrics[metricKey]) return [];
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.mean] === "number"; });
}

function deltaRows(metricKey) {
  if (!metrics[metricKey]) return [];
  const metric = metrics[metricKey];
  return summaryRows.filter(function (row) { return typeof row[metric.delta] === "number"; });
}

function isPendingBenchmark(metricKey) {
  const key = metricKey || activeMetric;
  return !metrics[key] || !benchmarkCatalog[key] || scoredRows(key).length === 0;
}

function activeDeltaMode() {
  return activeView === "delta" && Boolean(metrics[activeMetric] && metrics[activeMetric].delta);
}

function renderChart() {
  const chart = document.getElementById("bar-chart");
  if (isPendingBenchmark()) {
    const benchmark = benchmarkCatalog[activeMetric];
    const words = messages[activeLanguage];
    document.querySelector(".ranking-insight").hidden = true;
    document.getElementById("metric-panel").setAttribute("aria-labelledby", benchmarkTabs[activeMetric]);
    chart.classList.remove("delta-view", "score-view", "stddev-visible");
    chart.classList.add("is-empty");
    document.querySelector(".chart-legend").hidden = true;
    const allNote = activeCategory === "all" ? '<p>' + escapeHtml(words["results.pendingAllNote"]) + '</p>' : "";
    chart.innerHTML = '<div class="benchmark-pending"><div class="benchmark-pending-heading"><strong>' + escapeHtml(benchmark.title) + '</strong><span>' + escapeHtml(words["results.notRunLabel"]) + '</span></div><p>' + escapeHtml(words[benchmark.description] || words["results.pendingStatus"]) + '</p>' + allNote + '<a href="' + escapeHtml(benchmark.link || "#method") + '" target="_blank" rel="noreferrer">' + escapeHtml(words["results.openBenchmark"]) + '</a></div>';
    return;
  }
  document.querySelector(".chart-legend").hidden = false;
  const metric = metrics[activeMetric];
  const deltaMode = activeDeltaMode();
  const showStdDev = Boolean(stdDevVisibility[activeMetric] && hasStdDev(activeMetric, deltaMode));
  const rows = (deltaMode ? deltaRows(activeMetric) : scoredRows(activeMetric)).filter(function (row) {
    return selectedModelIds.has(modelConfigId(row));
  }).sort(function (a, b) {
    return deltaMode ? b[metric.delta] - a[metric.delta] : b[metric.mean] - a[metric.mean];
  });
  const range = Math.max(1, ...rows.map(function (row) {
    const value = deltaMode ? row[metric.delta] : row[metric.mean];
    const deviation = showStdDev ? (deltaMode ? row[metric.deltaSd] : row[metric.sd]) : 0;
    return deltaMode ? Math.abs(value || 0) + (deviation || 0) : 100;
  }));
  document.getElementById("metric-panel").setAttribute("aria-labelledby", benchmarkTabs[activeMetric]);
  chart.classList.toggle("delta-view", deltaMode);
  chart.classList.toggle("score-view", !deltaMode);
  chart.classList.toggle("stddev-visible", showStdDev);
  chart.classList.remove("is-empty");
  if (!rows.length) {
    document.querySelector(".ranking-insight").hidden = true;
    const message = selectedModelIds.size
      ? messages[activeLanguage]["results.noMatchingResults"]
      : messages[activeLanguage]["results.noVisibleModels"];
    chart.classList.add("is-empty");
    chart.innerHTML = '<div class="empty-results">' + escapeHtml(message) + '</div>';
    return;
  }
  document.querySelector(".ranking-insight").hidden = false;
  const best = rows[0];
  const brand = brandInfo(best);
  const insightLogo = document.getElementById("insight-logo");
  insightLogo.className = "insight-logo model-logo " + brand.css + (brand.src ? " has-logo" : "");
  insightLogo.innerHTML = brand.src
    ? '<img src="' + escapeHtml(brand.src) + '" alt="">'
    : escapeHtml(brand.monogram);
  document.getElementById("insight-label").textContent = messages[activeLanguage][deltaMode ? "results.deltaInsight" : "results.scoreInsight"];
  document.getElementById("insight-title").textContent = modelDisplayName(best) + " · " + variantLabel(best);
  const descriptionKey = deltaMode ? "results.deltaDescription" : "results.scoreDescription." + activeMetric;
  document.getElementById("insight-description").textContent = messages[activeLanguage][descriptionKey];
  document.getElementById("insight-value").textContent = deltaMode
    ? deltaText(best, activeMetric, showStdDev)
    : scoreText(best, activeMetric, showStdDev) + " /100";
  chart.innerHTML = rows.map(function (row, index) {
    const value = deltaMode ? row[metric.delta] : row[metric.mean];
    const deviation = showStdDev ? (deltaMode ? row[metric.deltaSd] : row[metric.sd]) : 0;
    const text = deltaMode ? deltaText(row, activeMetric, showStdDev) : scoreText(row, activeMetric, showStdDev);
    let fillClass;
    let start;
    let size;
    let errorStart;
    let errorSize;
    if (deltaMode) {
      const low = Math.max(-range, value - (deviation || 0));
      const high = Math.min(range, value + (deviation || 0));
      fillClass = value < 0 ? "negative" : value > 0 ? "positive" : "neutral";
      start = value < 0 ? 50 : 50 - value / range * 50;
      size = Math.abs(value) / range * 50;
      errorStart = 50 - high / range * 50;
      errorSize = Math.max(0, (high - low) / range * 50);
    } else {
      const low = Math.max(0, value - (deviation || 0));
      const high = Math.min(100, value + (deviation || 0));
      fillClass = brandInfo(row).css;
      start = 100 - Math.max(0, Math.min(100, value));
      size = Math.max(0, Math.min(100, value));
      errorStart = 100 - high;
      errorSize = Math.max(0, high - low);
    }
    const displayName = escapeHtml(modelDisplayName(row));
    const variant = escapeHtml(chartVariantLabel(row));
    const tooltipVariant = escapeHtml(variantLabel(row));
    const tooltipLabel = escapeHtml(modelDisplayName(row) + " · " + variantLabel(row));
    const fullValue = escapeHtml(text);
    const ifbenchOutputDetails = activeMetric === "ifbench" && typeof row.ifbench_max_new_tokens === "number"
      ? '<span>' + escapeHtml(messages[activeLanguage]["results.ifbenchOutputDetails"]
        .replace("{tokens}", String(row.ifbench_max_new_tokens))
        .replace("{count}", String(row.ifbench_truncated_responses ?? 0))) + '</span>'
      : "";
    const chartValue = escapeHtml(deltaMode ? deltaText(row, activeMetric, false).replace(" pp", "") : scoreText(row, activeMetric, false));
    const valueY = Math.max(5, Math.min(95, deltaMode ? (value < 0 ? 50 + size : start) : start));
    const barStyle = ' style="--bar-start:' + start + '%;--bar-size:' + size + '%;--value-y:' + valueY + '%;--error-start:' + errorStart + '%;--error-size:' + errorSize + '%"';
    const errorBar = showStdDev ? '<span class="uncertainty-range"' + barStyle + ' aria-hidden="true"></span>' : "";
    return '<div class="bar-column ' + (index === 0 ? "is-top " : "") + (deltaMode && value < 0 ? "is-loss" : "") + '"><div class="bar-plot ' + (deltaMode ? "delta-plot" : "score-plot") + '" role="img" tabindex="0" aria-label="' + tooltipLabel + ': ' + fullValue + '" title="' + tooltipLabel + '"><div class="bar-fill ' + fillClass + '"' + barStyle + '></div>' + errorBar + '<span class="bar-value"' + barStyle + '>' + chartValue + '</span><span class="bar-tooltip" aria-hidden="true"><strong>' + displayName + '</strong><span>' + tooltipVariant + '</span><span>' + fullValue + (deltaMode ? "" : " /100") + '</span>' + ifbenchOutputDetails + '</span></div><div class="bar-brand">' + modelLogo(row) + '</div><div class="bar-column-label" title="' + tooltipLabel + '"><strong>' + displayName + '</strong><small>' + variant + '</small></div></div>';
  }).join("");
}

function renderTable() {
  const benchmark = benchmarkCatalog[activeMetric];
  document.getElementById("table-metric-heading").textContent = benchmark.title;
  if (isPendingBenchmark()) {
    document.getElementById("score-table").innerHTML = '<tr><td class="empty-table" colspan="2">' + escapeHtml(messages[activeLanguage]["results.pendingStatus"]) + '</td></tr>';
    return;
  }
  const metric = metrics[activeMetric];
  const deltaMode = activeDeltaMode();
  const key = deltaMode ? metric.delta : metric.mean;
  const rows = summaryRows.filter(function (row) {
    return selectedModelIds.has(modelConfigId(row)) && typeof row[key] === "number";
  });
  rows.sort(function (a, b) {
    return (b[key] ?? -Infinity) - (a[key] ?? -Infinity);
  });
  if (!rows.length) {
    const message = selectedModelIds.size
      ? messages[activeLanguage]["results.noMatchingResults"]
      : messages[activeLanguage]["results.noVisibleModels"];
    document.getElementById("score-table").innerHTML = '<tr><td class="empty-table" colspan="2">' + escapeHtml(message) + '</td></tr>';
    return;
  }
  const ranks = [];
  let previousScore = null;
  let previousRank = 0;
  rows.forEach(function (row, index) {
    const roundedScore = Math.round(row[key] * 100) / 100;
    const rank = roundedScore === previousScore ? previousRank : index + 1;
    ranks.push(rank);
    previousScore = roundedScore;
    previousRank = rank;
  });
  document.getElementById("score-table").innerHTML = rows.map(function (row, index) {
    const label = escapeHtml(modelTag(row));
    const displayName = escapeHtml(modelDisplayName(row));
    const variant = escapeHtml(variantLabel(row));
    const rank = ranks[index];
    const value = deltaMode
      ? deltaText(row, activeMetric, stdDevVisibility[activeMetric])
      : scoreText(row, activeMetric, stdDevVisibility[activeMetric]);
    return '<tr class="' + (index === 0 ? "is-top" : "") + '"><td><div class="table-model">' + modelLogo(row) + '<span><strong class="model-name">' + displayName + '</strong><small>' + variant + ' · ' + label + '</small></span><span class="rank-badge">#' + rank + '</span></div></td><td>' + value + '</td></tr>';
  }).join("");
}

function renderHero() {
  const q4Deltas = summaryRows.flatMap(function (row) {
    if (row.variant !== "gguf_q4_k_m") return [];
    return Object.keys(metrics).map(function (key) { return row[metrics[key].delta]; }).filter(function (value) { return typeof value === "number"; });
  });
  if (q4Deltas.length) {
    const mean = q4Deltas.reduce(function (total, value) { return total + value; }, 0) / q4Deltas.length;
    const value = mean > 0 ? "+" + pretty(mean) : mean < 0 ? "−" + pretty(Math.abs(mean)) : pretty(0);
    document.getElementById("hero-score-value").textContent = value + " pp";
    document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "vs BF16 du même modèle" : "vs same-model BF16";
  }
  const models = new Set(summaryRows.filter(function (row) {
    return typeof row.rolebench_generalization_mean_100 === "number";
  }).map(function (row) { return row.model_key; }));
  document.getElementById("stat-models").textContent = String(models.size);
  document.getElementById("stat-variants").textContent = String(scoredRows("rolebench_generalization").length);
}

function renderEnvironment(environment) {
  const hardware = environment.hardware || {};
  const gguf = environment.gguf_evaluation || {};
  const ggufHardware = gguf.hardware || {};
  const q4 = environment.local_q4_benchmarks || {};
  const q4Hardware = q4.hardware || {};
  const values = [
    ["MLX", hardware.chip, hardware.macos ? "macOS " + hardware.macos : ""],
    ["GGUF", ggufHardware.gpu, ggufHardware.os],
    ["Q4 local", q4Hardware.gpu, q4Hardware.os],
  ].map(function (parts) { return parts.filter(Boolean).join(" · "); }).filter(Boolean);
  document.getElementById("environment-summary").textContent = values.join(" / ") || "MLX · GGUF";
}

function renderAll() {
  translate();
  renderHero();
  renderTable();
  renderChart();
}

document.querySelectorAll("[data-language]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeLanguage = button.dataset.language;
    localStorage.setItem("quantization-bench-language", activeLanguage);
    renderAll();
  });
});
document.querySelectorAll("[data-category]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeCategory = button.dataset.category;
    if (!categoryMetrics[activeCategory].includes(activeMetric)) activeMetric = categoryMetrics[activeCategory][0];
    renderAll();
  });
});
document.querySelectorAll("[data-metric]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeMetric = button.dataset.metric;
    renderAll();
  });
});
document.querySelectorAll("[data-view]").forEach(function (button) {
  button.addEventListener("click", function () {
    activeView = button.dataset.view;
    renderAll();
  });
});
document.getElementById("stddev-toggle").addEventListener("click", function () {
  stdDevVisibility[activeMetric] = !stdDevVisibility[activeMetric];
  renderAll();
});
document.getElementById("model-filter-toggle").addEventListener("click", function () {
  setModelFilterOpen(this.getAttribute("aria-expanded") !== "true");
});
document.getElementById("model-filter-search").addEventListener("input", applyModelFilterSearch);
document.getElementById("model-filter-options").addEventListener("change", function (event) {
  const group = event.target.closest(".model-filter-family");
  if (!group) return;
  if (event.target.matches("[data-family-toggle]")) {
    group.querySelectorAll("[data-model-id]").forEach(function (input) {
      input.checked = event.target.checked;
      if (event.target.checked) selectedModelIds.add(input.value);
      else selectedModelIds.delete(input.value);
    });
  } else if (event.target.matches("[data-model-id]")) {
    if (event.target.checked) selectedModelIds.add(event.target.value);
    else selectedModelIds.delete(event.target.value);
  } else {
    return;
  }
  syncFamilyToggles();
  updateModelFilterUrl();
  updateModelFilterCount();
  renderAll();
});
document.getElementById("model-select-all").addEventListener("click", function () {
  selectedModelIds = new Set(modelConfigs().map(modelConfigId));
  renderModelFilterOptions();
  updateModelFilterUrl();
  renderAll();
});
document.getElementById("model-select-none").addEventListener("click", function () {
  selectedModelIds = new Set();
  renderModelFilterOptions();
  updateModelFilterUrl();
  renderAll();
});
document.addEventListener("click", function (event) {
  if (!document.getElementById("model-filter").contains(event.target)) setModelFilterOpen(false);
});
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape" && document.getElementById("model-filter-toggle").getAttribute("aria-expanded") === "true") {
    setModelFilterOpen(false);
    document.getElementById("model-filter-toggle").focus();
  }
});

Promise.all([
  fetch("site-data/summary.json?v=local-benchmarks").then(function (response) { if (!response.ok) throw new Error("summary"); return response.json(); }),
  fetch("site-data/environment.json?v=local-benchmarks").then(function (response) { if (!response.ok) throw new Error("environment"); return response.json(); })
]).then(function (data) {
  summaryRows = data[0];
  initializeModelSelection();
  renderEnvironment(data[1]);
  renderAll();
}).catch(function () {
  document.getElementById("hero-score-value").textContent = "—";
  document.getElementById("hero-score-model").textContent = activeLanguage === "fr" ? "Données indisponibles." : "Data unavailable.";
});

renderAll();
