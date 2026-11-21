/**
 * CropCare AI - Production Frontend Controller
 * Connects UI interactions to Flask REST APIs, manages vision models,
 * crop recommendation, expert system inference, and bilingual states.
 */

document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        crops: [],
        symptoms: [],
        selectedCrop: "tomato",
        selectedSymptoms: new Set(),
        selectedPartFilter: "all",
        uploadedFile: null,
        activeTab: "dashboard",
        apiKey: localStorage.getItem("cropcare_gemini_key") || ""
    };

    // DOM Elements Cache
    const elements = {
        cropSelect: document.getElementById("cropSelect"),
        symptomContainer: document.getElementById("symptomContainer"),
        symptomFilterBtns: document.querySelectorAll(".symptom-part-filter"),
        symptomSearchInput: document.getElementById("symptomSearchInput"),
        selectedCountBadge: document.getElementById("selectedCountBadge"),
        btnRunDiag: document.getElementById("btnRunDiagnosis"),
        btnResetDiag: document.getElementById("btnResetDiagnosis"),
        dropzone: document.getElementById("leafDropzone"),
        fileInput: document.getElementById("leafFileInput"),
        imagePreviewContainer: document.getElementById("imagePreviewContainer"),
        imagePreviewImg: document.getElementById("imagePreviewImg"),
        btnRemoveImage: document.getElementById("btnRemoveImage"),
        diagResultCard: document.getElementById("diagnosisResultCard"),
        diagEmptyCard: document.getElementById("diagnosisEmptyCard"),
        
        // Crop Recommender
        recNInput: document.getElementById("recNInput"),
        recPInput: document.getElementById("recPInput"),
        recKInput: document.getElementById("recKInput"),
        recPhInput: document.getElementById("recPhInput"),
        recTempInput: document.getElementById("recTempInput"),
        recHumInput: document.getElementById("recHumInput"),
        recRainInput: document.getElementById("recRainInput"),
        btnPredictCrop: document.getElementById("btnPredictCrop"),
        cropRecResultCard: document.getElementById("cropRecResultCard"),

        // Soil Advisory
        soilCropSelect: document.getElementById("soilCropSelect"),
        soilNInput: document.getElementById("soilNInput"),
        soilPInput: document.getElementById("soilPInput"),
        soilKInput: document.getElementById("soilKInput"),
        soilPhInput: document.getElementById("soilPhInput"),
        soilPhDisplay: document.getElementById("soilPhDisplay"),
        soilTypeSelect: document.getElementById("soilTypeSelect"),
        btnCalcSoil: document.getElementById("btnCalculateSoil"),
        soilResultCard: document.getElementById("soilResultCard"),
        phIndicatorPin: document.getElementById("phIndicatorPin"),
        
        // Irrigation
        irriCropSelect: document.getElementById("irriCropSelect"),
        irriStageSelect: document.getElementById("irriStageSelect"),
        irriSoilSelect: document.getElementById("irriSoilSelect"),
        irriSeasonSelect: document.getElementById("irriSeasonSelect"),
        btnGetIrri: document.getElementById("btnGetIrrigation"),
        irriResultCard: document.getElementById("irriResultCard"),
        
        // Chat
        chatInput: document.getElementById("chatInput"),
        btnSendChat: document.getElementById("btnSendChat"),
        chatMessagesList: document.getElementById("chatMessagesList"),
        chatChips: document.querySelectorAll(".chat-chip"),
        
        // History
        diagHistoryTableBody: document.getElementById("diagHistoryTableBody"),
        cropRecHistoryTableBody: document.getElementById("cropRecHistoryTableBody"),
        soilHistoryTableBody: document.getElementById("soilHistoryTableBody"),
        btnSeedSampleData: document.getElementById("btnSeedSampleData"),
        btnRefreshHistory: document.getElementById("btnRefreshHistory"),
        
        // Stats
        statDiagCount: document.getElementById("statDiagCount"),
        statRecCount: document.getElementById("statRecCount"),
        statConfAvg: document.getElementById("statConfAvg"),
        statSoilCount: document.getElementById("statSoilCount"),
        
        // AI Settings Modal
        btnOpenApiModal: document.getElementById("btnOpenApiModal"),
        btnCloseApiModal: document.getElementById("btnCloseApiModal"),
        apiSettingsModal: document.getElementById("apiSettingsModal"),
        geminiApiKeyInput: document.getElementById("geminiApiKeyInput"),
        btnSaveApiKey: document.getElementById("btnSaveApiKey"),
        btnClearApiKey: document.getElementById("btnClearApiKey")
    };

    // Initialize Application
    initApp();

    async function initApp() {
        setLanguage(getActiveLanguage());

        // Setup UI handlers
        setupTabNavigation();
        setupDropzone();
        setupChatbot();
        setupSoilPresets();
        setupCropRecPresets();
        setupApiModal();

        // Fetch Metadata
        await fetchCrops();
        await fetchSymptoms();
        await fetchStats();
        await fetchHistory();

        // Attach Event Listeners
        attachEventListeners();
    }

    // Helper: Standard Fetch headers with optional Gemini API Key
    function getApiHeaders(customHeaders = {}) {
        const headers = { ...customHeaders };
        if (state.apiKey) {
            headers["X-Gemini-API-Key"] = state.apiKey;
        }
        return headers;
    }

    // =========================================================================
    // NAVIGATION & TAB SWITCHING
    // =========================================================================
    function setupTabNavigation() {
        const navTabs = document.querySelectorAll(".nav-tab");
        const tabSections = document.querySelectorAll(".tab-section");

        navTabs.forEach(tab => {
            tab.addEventListener("click", (e) => {
                e.preventDefault();
                const targetTab = tab.getAttribute("data-tab");
                state.activeTab = targetTab;

                navTabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                tabSections.forEach(section => {
                    if (section.id === `tab-${targetTab}`) {
                        section.classList.remove("hidden");
                    } else {
                        section.classList.add("hidden");
                    }
                });

                if (targetTab === "history") fetchHistory();
                if (targetTab === "dashboard") fetchStats();
            });
        });

        // Quick action buttons from hero/cards
        document.querySelectorAll("[data-navigate-tab]").forEach(btn => {
            btn.addEventListener("click", () => {
                const target = btn.getAttribute("data-navigate-tab");
                const targetNav = document.querySelector(`.nav-tab[data-tab='${target}']`);
                if (targetNav) targetNav.click();
            });
        });

        // Language toggle button
        const langToggleBtn = document.getElementById("langToggleBtn");
        if (langToggleBtn) {
            langToggleBtn.addEventListener("click", () => {
                const nextLang = getActiveLanguage() === "en" ? "hi" : "en";
                setLanguage(nextLang);
            });
        }

        // Language change event
        window.addEventListener("languageChanged", () => {
            renderCropDropdowns();
            renderSymptoms();
            fetchHistory();
        });
    }

    // =========================================================================
    // AI SETTINGS MODAL
    // =========================================================================
    function setupApiModal() {
        if (!elements.btnOpenApiModal || !elements.apiSettingsModal) return;

        elements.geminiApiKeyInput.value = state.apiKey;

        elements.btnOpenApiModal.addEventListener("click", () => {
            elements.geminiApiKeyInput.value = state.apiKey;
            elements.apiSettingsModal.classList.remove("hidden");
        });

        elements.btnCloseApiModal.addEventListener("click", () => {
            elements.apiSettingsModal.classList.add("hidden");
        });

        elements.btnSaveApiKey.addEventListener("click", () => {
            const val = elements.geminiApiKeyInput.value.trim();
            state.apiKey = val;
            localStorage.setItem("cropcare_gemini_key", val);
            elements.apiSettingsModal.classList.add("hidden");
            showToast(val ? "Gemini 2.5 Flash Vision enabled!" : "Using Local Offline Models.", "success");
        });

        elements.btnClearApiKey.addEventListener("click", () => {
            state.apiKey = "";
            localStorage.removeItem("cropcare_gemini_key");
            elements.geminiApiKeyInput.value = "";
            elements.apiSettingsModal.classList.add("hidden");
            showToast("Switched to Local Offline Models.", "info");
        });
    }

    // =========================================================================
    // METADATA FETCHING
    // =========================================================================
    async function fetchCrops() {
        try {
            const res = await fetch("/api/crops");
            const data = await res.json();
            if (data.success) {
                state.crops = data.crops;
                renderCropDropdowns();
            }
        } catch (err) {
            console.error("Failed to fetch crops:", err);
        }
    }

    function renderCropDropdowns() {
        const lang = getActiveLanguage();
        const selects = [elements.cropSelect, elements.soilCropSelect, elements.irriCropSelect];

        selects.forEach(select => {
            if (!select) return;
            const currentVal = select.value || "tomato";
            select.innerHTML = "";
            state.crops.forEach(c => {
                const opt = document.createElement("option");
                opt.value = c.id;
                opt.textContent = `${c.icon} ${lang === "hi" ? c.name_hi : c.name_en}`;
                select.appendChild(opt);
            });
            select.value = currentVal;
        });
    }

    async function fetchSymptoms() {
        try {
            const res = await fetch("/api/symptoms");
            const data = await res.json();
            if (data.success) {
                state.symptoms = data.symptoms;
                renderSymptoms();
            }
        } catch (err) {
            console.error("Failed to fetch symptoms:", err);
        }
    }

    function renderSymptoms() {
        if (!elements.symptomContainer) return;
        elements.symptomContainer.innerHTML = "";
        const lang = getActiveLanguage();
        const filter = state.selectedPartFilter;
        const search = (elements.symptomSearchInput?.value || "").toLowerCase().trim();

        const filtered = state.symptoms.filter(s => {
            const matchPart = filter === "all" || s.part === filter;
            const label = (lang === "hi" ? s.hi : s.en).toLowerCase();
            const matchSearch = !search || label.includes(search);
            return matchPart && matchSearch;
        });

        if (filtered.length === 0) {
            elements.symptomContainer.innerHTML = `
                <div class="col-span-full py-6 text-center text-slate-400 text-sm">
                    ${lang === "hi" ? "कोई लक्षण नहीं मिला।" : "No matching symptoms found."}
                </div>
            `;
            return;
        }

        filtered.forEach(s => {
            const isSelected = state.selectedSymptoms.has(s.id);
            const chip = document.createElement("div");
            chip.className = `symptom-chip p-2.5 rounded-xl border text-xs sm:text-sm font-medium flex items-center justify-between transition-all ${
                isSelected ? "selected" : "bg-white border-slate-200 text-slate-700"
            }`;
            chip.innerHTML = `
                <span>${lang === "hi" ? s.hi : s.en}</span>
                <span class="ml-2 text-xs opacity-75">${isSelected ? "✓" : "+"}</span>
            `;

            chip.addEventListener("click", () => {
                if (state.selectedSymptoms.has(s.id)) {
                    state.selectedSymptoms.delete(s.id);
                } else {
                    state.selectedSymptoms.add(s.id);
                }
                updateSelectedSymptomsBadge();
                renderSymptoms();
            });

            elements.symptomContainer.appendChild(chip);
        });
    }

    function updateSelectedSymptomsBadge() {
        const count = state.selectedSymptoms.size;
        if (elements.selectedCountBadge) {
            elements.selectedCountBadge.textContent = count;
        }
    }

    // =========================================================================
    // DROPZONE & IMAGE UPLOAD
    // =========================================================================
    function setupDropzone() {
        const dropzone = elements.dropzone;
        const fileInput = elements.fileInput;
        if (!dropzone || !fileInput) return;

        dropzone.addEventListener("click", () => fileInput.click());

        ["dragenter", "dragover"].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.remove("dragover");
            });
        });

        dropzone.addEventListener("drop", (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        fileInput.addEventListener("change", () => {
            if (fileInput.files && fileInput.files.length > 0) {
                handleFileSelect(fileInput.files[0]);
            }
        });

        if (elements.btnRemoveImage) {
            elements.btnRemoveImage.addEventListener("click", (e) => {
                e.stopPropagation();
                clearImagePreview();
            });
        }
    }

    function handleFileSelect(file) {
        if (!file.type.startsWith("image/")) {
            showToast("Please upload a valid image file (PNG, JPG, WEBP).", "error");
            return;
        }
        state.uploadedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            elements.imagePreviewImg.src = e.target.result;
            elements.imagePreviewContainer.classList.remove("hidden");
            elements.dropzone.classList.add("hidden");
        };
        reader.readAsDataURL(file);
    }

    function clearImagePreview() {
        state.uploadedFile = null;
        if (elements.fileInput) elements.fileInput.value = "";
        if (elements.imagePreviewImg) elements.imagePreviewImg.src = "";
        elements.imagePreviewContainer.classList.add("hidden");
        elements.dropzone.classList.remove("hidden");
    }

    // =========================================================================
    // EVENT LISTENERS & DISEASE DIAGNOSIS
    // =========================================================================
    function attachEventListeners() {
        // Symptom part filter tabs
        elements.symptomFilterBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                elements.symptomFilterBtns.forEach(b => {
                    b.classList.remove("bg-emerald-600", "text-white");
                    b.classList.add("bg-slate-100", "text-slate-600");
                });
                btn.classList.remove("bg-slate-100", "text-slate-600");
                btn.classList.add("bg-emerald-600", "text-white");

                state.selectedPartFilter = btn.getAttribute("data-part");
                renderSymptoms();
            });
        });

        // Symptom search input
        if (elements.symptomSearchInput) {
            elements.symptomSearchInput.addEventListener("input", () => {
                renderSymptoms();
            });
        }

        // Reset Diagnosis Form
        if (elements.btnResetDiag) {
            elements.btnResetDiag.addEventListener("click", () => {
                state.selectedSymptoms.clear();
                updateSelectedSymptomsBadge();
                renderSymptoms();
                clearImagePreview();
                elements.diagResultCard.classList.add("hidden");
                elements.diagEmptyCard.classList.remove("hidden");
                showToast("Diagnosis form reset.", "info");
            });
        }

        // Run Diagnosis
        if (elements.btnRunDiag) {
            elements.btnRunDiag.addEventListener("click", runDiagnosis);
        }

        // Predict Crop
        if (elements.btnPredictCrop) {
            elements.btnPredictCrop.addEventListener("click", runCropRecommendation);
        }

        // Soil pH Slider update
        if (elements.soilPhInput && elements.soilPhDisplay) {
            elements.soilPhInput.addEventListener("input", (e) => {
                const val = parseFloat(e.target.value);
                elements.soilPhDisplay.textContent = val.toFixed(1);
                updatePhGauge(val);
            });
        }

        // Calculate Soil Fertilizer Plan
        if (elements.btnCalcSoil) {
            elements.btnCalcSoil.addEventListener("click", calculateSoilPlan);
        }

        // Irrigation Guidance
        if (elements.btnGetIrri) {
            elements.btnGetIrri.addEventListener("click", getIrrigationGuidance);
        }

        // Seed Sample Data
        if (elements.btnSeedSampleData) {
            elements.btnSeedSampleData.addEventListener("click", seedSampleData);
        }

        // Refresh History
        if (elements.btnRefreshHistory) {
            elements.btnRefreshHistory.addEventListener("click", () => {
                fetchHistory();
                fetchStats();
                showToast("Records refreshed.", "info");
            });
        }

        // Print Diagnosis
        const btnPrint = document.getElementById("btnPrintDiagnosis");
        if (btnPrint) {
            btnPrint.addEventListener("click", () => window.print());
        }
    }

    async function runDiagnosis() {
        const crop = elements.cropSelect?.value || "";
        const weather = document.getElementById("weatherSelect")?.value || "";
        const growthStage = document.getElementById("growthStageSelect")?.value || "vegetative";
        const lang = getActiveLanguage();

        if (state.selectedSymptoms.size === 0 && !state.uploadedFile && !crop) {
            showToast(
                lang === "hi"
                    ? "कृपया फसल चुनें, लक्षण चुनें या पत्ती की फोटो अपलोड करें।"
                    : "Please select a crop, symptoms, or upload a leaf photo.",
                "warning"
            );
            return;
        }

        elements.btnRunDiag.disabled = true;
        elements.btnRunDiag.innerHTML = `<span class="inline-block animate-spin mr-2">🔄</span> ${lang === "hi" ? "एआई विज़न विश्लेषण जारी..." : "Vision AI Analyzing..."}`;

        try {
            let res;
            if (state.uploadedFile) {
                const formData = new FormData();
                formData.append("crop", crop);
                formData.append("weather", weather);
                formData.append("growth_stage", growthStage);
                formData.append("lang", lang);
                formData.append("leaf_image", state.uploadedFile);
                if (state.apiKey) formData.append("api_key", state.apiKey);
                state.selectedSymptoms.forEach(s => formData.append("symptoms[]", s));

                res = await fetch("/api/diagnose", {
                    method: "POST",
                    headers: getApiHeaders(),
                    body: formData
                });
            } else {
                const payload = {
                    crop: crop || "tomato",
                    symptoms: Array.from(state.selectedSymptoms),
                    weather: weather,
                    growth_stage: growthStage,
                    lang: lang,
                    api_key: state.apiKey || undefined
                };
                res = await fetch("/api/diagnose", {
                    method: "POST",
                    headers: getApiHeaders({ "Content-Type": "application/json" }),
                    body: JSON.stringify(payload)
                });
            }

            const data = await res.json();
            if (data.success) {
                renderDiagnosisResult(data);
                fetchStats();
                showToast(
                    lang === "hi" ? "निदान सफलतापूर्वक पूरा हुआ!" : "Diagnosis generated successfully!",
                    "success"
                );
            } else {
                showToast(data.error || "Diagnosis failed.", "error");
            }
        } catch (err) {
            console.error(err);
            showToast("Server error during diagnosis: " + err.message, "error");
        } finally {
            elements.btnRunDiag.disabled = false;
            elements.btnRunDiag.innerHTML = `<span class="mr-2">⚡</span> <span data-i18n="btn_run_diag">${t("btn_run_diag")}</span>`;
        }
    }

    function renderDiagnosisResult(resData) {
        const diag = resData.diagnosis_result;
        const primary = diag.primary_diagnosis;
        const lang = getActiveLanguage();

        elements.diagEmptyCard.classList.add("hidden");
        elements.diagResultCard.classList.remove("hidden");

        if (!primary) {
            document.getElementById("resDiseaseTitle").textContent = lang === "hi" ? "अनिर्णायक निदान" : "Inconclusive Diagnosis";
            document.getElementById("resConfidencePercent").textContent = "N/A";
            document.getElementById("resConfidenceBar").style.width = "10%";
            document.getElementById("resConfidenceBar").className = "h-full bg-slate-400";
            document.getElementById("resPathogenBadge").textContent = "Unknown";
            document.getElementById("resSeverityBadge").textContent = "Low";
            document.getElementById("resWhySelected").textContent = diag.explanation?.why_selected || "Insufficient patterns.";
            document.getElementById("treatmentContainer").classList.add("hidden");
            return;
        }

        // Primary Match Details
        document.getElementById("resDiseaseTitle").textContent = lang === "hi" ? (primary.name_hi || primary.name) : (primary.name_en || primary.name);
        document.getElementById("resSubTitle").textContent = lang === "hi" ? (primary.name_en || "") : (primary.name_hi || "");
        document.getElementById("resConfidencePercent").textContent = `${primary.confidence}%${primary.is_uncertain ? " (Uncertain)" : ""}`;
        
        const confBar = document.getElementById("resConfidenceBar");
        confBar.style.width = `${primary.confidence}%`;
        if (primary.is_uncertain) {
            confBar.className = "h-full bg-amber-500 rounded-full transition-all duration-700";
            document.getElementById("resDiseaseTitle").className = "text-xl sm:text-2xl font-extrabold text-amber-950";
        } else if (primary.confidence >= 80) {
            confBar.className = "h-full bg-emerald-500 rounded-full transition-all duration-700";
            document.getElementById("resDiseaseTitle").className = "text-2xl sm:text-3xl font-extrabold text-slate-900";
        } else if (primary.confidence >= 60) {
            confBar.className = "h-full bg-amber-500 rounded-full transition-all duration-700";
            document.getElementById("resDiseaseTitle").className = "text-2xl sm:text-3xl font-extrabold text-slate-900";
        } else {
            confBar.className = "h-full bg-orange-500 rounded-full transition-all duration-700";
            document.getElementById("resDiseaseTitle").className = "text-2xl sm:text-3xl font-extrabold text-slate-900";
        }

        document.getElementById("resPathogenBadge").textContent = primary.pathogen || "Fungal";
        
        const sevBadge = document.getElementById("resSeverityBadge");
        if (primary.is_uncertain) {
            sevBadge.textContent = lang === "hi" ? (primary.severity_hi || "सत्यापन आवश्यक") : primary.severity;
            sevBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300";
        } else {
            sevBadge.textContent = primary.severity || "Moderate";
            sevBadge.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200";
        }
        
        const engineBadge = document.getElementById("resEngineBadge");
        if (engineBadge) {
            engineBadge.textContent = resData.vision_analysis?.engine ? "Vision + Rules Fusion" : (primary.rule_id || "Production AI");
        }

        // Image Analysis Visual Card if image was uploaded
        const imgCard = document.getElementById("resImageAnalysisCard");
        if (resData.vision_analysis && resData.vision_analysis.visual_metrics) {
            imgCard.classList.remove("hidden");
            const vm = resData.vision_analysis.visual_metrics;
            document.getElementById("imgHealthyPct").textContent = `${vm.healthy_ratio}%`;
            document.getElementById("imgChlorosisPct").textContent = `${vm.chlorosis_ratio}%`;
            document.getElementById("imgNecrosisPct").textContent = `${vm.necrosis_ratio}%`;
            document.getElementById("imgAssessmentText").textContent = resData.vision_analysis.explanation?.why_selected || "";
            if (resData.image_url) {
                document.getElementById("resUploadedLeafThumb").src = resData.image_url;
            }
        } else {
            imgCard.classList.add("hidden");
        }

        // Multi-Modal Evidence Breakdown Card
        const multiModalCard = document.getElementById("multiModalEvidenceCard");
        const fusionMeta = resData.fusion_analysis;
        const indepVis = resData.independent_vision_result;
        const indepRule = resData.independent_rule_result;

        if (multiModalCard && (indepVis || indepRule)) {
            multiModalCard.classList.remove("hidden");

            // Status Badge
            const statusBadge = document.getElementById("fusionStatusBadge");
            if (statusBadge && fusionMeta) {
                statusBadge.textContent = fusionMeta.status_label || fusionMeta.status;
                if (fusionMeta.is_conflict) {
                    statusBadge.className = "self-start sm:self-auto px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300";
                } else {
                    statusBadge.className = "self-start sm:self-auto px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300";
                }
            }

            // Vision Column
            if (indepVis) {
                document.getElementById("visionConfBadge").textContent = `${indepVis.confidence}%`;
                document.getElementById("visionDiseaseTitle").textContent = lang === "hi" ? (indepVis.disease_name_hi || indepVis.disease_name) : (indepVis.disease_name_en || indepVis.disease_name);
                const vm = indepVis.visual_metrics || {};
                const spotClusters = vm.num_spot_clusters !== undefined ? vm.num_spot_clusters : "--";
                const haloPct = vm.halo_ratio !== undefined ? `${Math.round(vm.halo_ratio * 100)}%` : "--";
                document.getElementById("visionMorphologySummary").textContent = 
                    lang === "hi"
                        ? `${spotClusters} घाव समूह, ${haloPct} पीला घेरा (हेलो), ${vm.necrosis_ratio || 0}% परिगलन।`
                        : `${spotClusters} necrotic spot clusters, ${haloPct} halo overlap, ${vm.necrosis_ratio || 0}% necrosis.`;
                document.getElementById("visionEngineName").textContent = indepVis.engine ? indepVis.engine.split("(")[0].trim() : "Local CV";
                document.getElementById("visionSpotCount").textContent = `${spotClusters} spots`;
            } else {
                document.getElementById("visionConfBadge").textContent = "N/A";
                document.getElementById("visionDiseaseTitle").textContent = lang === "hi" ? "कोई फोटो नहीं" : "No Photo Uploaded";
                document.getElementById("visionMorphologySummary").textContent = lang === "hi" ? "केवल लक्षण नियम चलाए गए।" : "Evaluated symptom rules only.";
                document.getElementById("visionSpotCount").textContent = "0 spots";
            }

            // Rule Column
            if (indepRule && indepRule.primary_diagnosis) {
                const rp = indepRule.primary_diagnosis;
                document.getElementById("ruleConfBadge").textContent = `${rp.confidence}%`;
                document.getElementById("ruleDiseaseTitle").textContent = lang === "hi" ? (rp.name_hi || rp.name) : (rp.name_en || rp.name);
                const matched = indepRule.explanation?.key_symptoms_matched || [];
                document.getElementById("ruleMatchedSummary").textContent = matched.join(", ") || (lang === "hi" ? "लक्षण मेल खाए" : "Matched symptoms");
                document.getElementById("ruleFiredId").textContent = rp.rule_id || "RULE";

                const hasPatho = (matched.some(m => m.toLowerCase().includes("concentric") || m.toLowerCase().includes("सकेंद्रित") || m.toLowerCase().includes("pustule") || m.toLowerCase().includes("powdery")));
                document.getElementById("rulePathoCheck").textContent = hasPatho 
                    ? (lang === "hi" ? "हाँ (विशिष्ट लक्षण)" : "Yes (Pathognomonic)") 
                    : (lang === "hi" ? "मूल्यांकित" : "Evaluated");
            } else {
                document.getElementById("ruleConfBadge").textContent = "N/A";
                document.getElementById("ruleDiseaseTitle").textContent = lang === "hi" ? "कोई लक्षण नहीं" : "No Symptoms Picked";
                document.getElementById("ruleMatchedSummary").textContent = lang === "hi" ? "केवल विज़न एआई चलाया गया।" : "Evaluated leaf photo only.";
                document.getElementById("ruleFiredId").textContent = "None";
                document.getElementById("rulePathoCheck").textContent = "--";
            }

            // Reconciliation Box
            const reasonText = fusionMeta?.reconciliation_reason || diag.explanation?.why_selected || "";
            document.getElementById("fusionReasoningText").textContent = reasonText;
        } else if (multiModalCard) {
            multiModalCard.classList.add("hidden");
        }

        // Dual Candidate Comparison Card (During Uncertain/Conflict State)
        const dualCard = document.getElementById("dualCandidateCard");
        if (primary.is_uncertain && primary.candidates && primary.candidates.length >= 2) {
            if (dualCard) {
                dualCard.classList.remove("hidden");
                const c1 = primary.candidates[0];
                const c2 = primary.candidates[1];

                document.getElementById("cand1Title").textContent = lang === "hi" ? (c1.name_hi || c1.name) : (c1.name_en || c1.name);
                document.getElementById("cand1ConfBadge").textContent = `${c1.confidence}%`;
                document.getElementById("cand1Evidence").textContent = lang === "hi" ? c1.evidence_hi : c1.evidence_en;
                document.getElementById("cand1Modality").textContent = lang === "hi" ? (c1.modality_hi || c1.modality) : c1.modality;

                document.getElementById("cand2Title").textContent = lang === "hi" ? (c2.name_hi || c2.name) : (c2.name_en || c2.name);
                document.getElementById("cand2ConfBadge").textContent = `${c2.confidence}%`;
                document.getElementById("cand2Evidence").textContent = lang === "hi" ? c2.evidence_hi : c2.evidence_en;
                document.getElementById("cand2Modality").textContent = lang === "hi" ? (c2.modality_hi || c2.modality) : c2.modality;

                const testBox = document.getElementById("fieldTestText");
                if (testBox) {
                    testBox.textContent = primary.discriminating_field_test || fusionMeta?.discriminating_field_test || "";
                }
            }
        } else if (dualCard) {
            dualCard.classList.add("hidden");
        }

        // Explanation Facility
        document.getElementById("resWhySelected").textContent = diag.explanation?.why_selected || "";
        
        const stepsUl = document.getElementById("resReasoningSteps");
        stepsUl.innerHTML = (diag.explanation?.reasoning_steps || [])
            .map(step => `<li class="text-sm text-slate-700 mb-1 flex items-start"><span class="text-emerald-600 mr-2 font-bold">✔</span><span>${step}</span></li>`)
            .join("");

        // Source-Separated Symptoms Rendering
        const userSymsList = document.getElementById("resUserSymptomsList");
        const imgSymsList = document.getElementById("resImageSymptomsList");
        const userBox = document.getElementById("userSymptomsBox");
        const imgBox = document.getElementById("imageSymptomsBox");

        const sb = resData.symptoms_breakdown || diag.symptoms_breakdown || {};
        const userSyms = sb.user_selected || [];
        const imgSyms = sb.image_detected || [];

        if (userSymsList && userBox) {
            if (userSyms.length > 0) {
                userBox.classList.remove("hidden");
                userSymsList.innerHTML = userSyms.map(s => `
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-900 border border-blue-200">
                        <span class="mr-1">🧑‍🌾</span> ${lang === "hi" ? (s.name_hi || s.name) : (s.name_en || s.name)}
                    </span>
                `).join("");
            } else {
                userBox.classList.add("hidden");
            }
        }

        if (imgSymsList && imgBox) {
            if (imgSyms.length > 0) {
                imgBox.classList.remove("hidden");
                imgSymsList.innerHTML = imgSyms.map(s => `
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-50 text-emerald-900 border border-emerald-200" title="${s.detail || ''}">
                        <span class="mr-1">📷</span> ${lang === "hi" ? (s.name_hi || s.name) : (s.name_en || s.name)}
                        ${s.detail ? `<span class="ml-1.5 text-[10px] text-emerald-800 bg-white/80 px-1.5 py-0.5 rounded font-normal border border-emerald-100">${s.detail}</span>` : ""}
                    </span>
                `).join("");
            } else {
                imgBox.classList.add("hidden");
            }
        }

        // Differential Diagnoses
        const diffContainer = document.getElementById("resDifferentialList");
        const diffWrapper = document.getElementById("differentialContainer");
        if (diag.differential_diagnoses && diag.differential_diagnoses.length > 0) {
            if (diffWrapper) diffWrapper.classList.remove("hidden");
            diffContainer.innerHTML = diag.differential_diagnoses.map(alt => `
                <div class="p-2.5 bg-slate-50 border border-slate-200 rounded-xl mb-2 flex items-center justify-between text-xs sm:text-sm">
                    <div>
                        <span class="font-semibold text-slate-800">${lang === "hi" ? alt.name_hi : alt.name_en}</span>
                        <span class="text-slate-500 ml-1">(${alt.pathogen})</span>
                    </div>
                    <div class="text-amber-700 font-bold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                        ${alt.confidence}% ${lang === "hi" ? "संभावना" : "score"}
                    </div>
                </div>
            `).join("");
        } else {
            if (diffWrapper) diffWrapper.classList.add("hidden");
        }

        // Treatment details
        document.getElementById("treatmentContainer").classList.remove("hidden");
        const t = primary.treatment || {};
        document.getElementById("resOrganicTreatment").textContent = lang === "hi" ? (t.organic_hi || t.organic_en) : t.organic_en;
        document.getElementById("resChemicalTreatment").textContent = lang === "hi" ? (t.chemical_hi || t.chemical_en) : t.chemical_en;
        document.getElementById("resDosageSchedule").textContent = t.dosage || "2 - 2.5 g/L";
        document.getElementById("resPreventiveMeasures").textContent = lang === "hi" ? (t.prevention_hi || t.prevention_en) : t.prevention_en;

        elements.diagResultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // =========================================================================
    // CROP RECOMMENDATION MODULE
    // =========================================================================
    function setupCropRecPresets() {
        const presets = {
            paddy: { n: 80, p: 48, k: 40, ph: 6.4, temp: 24.0, hum: 82.0, rain: 230.0 },
            wheat: { n: 115, p: 55, k: 40, ph: 6.8, temp: 18.0, hum: 60.0, rain: 75.0 },
            maize: { n: 78, p: 48, k: 20, ph: 6.2, temp: 23.0, hum: 65.0, rain: 85.0 },
            pulses: { n: 38, p: 68, k: 78, ph: 7.2, temp: 19.0, hum: 18.0, rain: 80.0 }
        };

        document.querySelectorAll("[data-rec-preset]").forEach(btn => {
            btn.addEventListener("click", () => {
                const key = btn.getAttribute("data-rec-preset");
                const p = presets[key];
                if (!p) return;

                elements.recNInput.value = p.n;
                elements.recPInput.value = p.p;
                elements.recKInput.value = p.k;
                elements.recPhInput.value = p.ph;
                elements.recTempInput.value = p.temp;
                elements.recHumInput.value = p.hum;
                elements.recRainInput.value = p.rain;
                showToast(`Loaded ${key} preset parameters.`, "info");
            });
        });
    }

    async function runCropRecommendation() {
        const n = parseFloat(elements.recNInput.value) || 0;
        const p = parseFloat(elements.recPInput.value) || 0;
        const k = parseFloat(elements.recKInput.value) || 0;
        const ph = parseFloat(elements.recPhInput.value) || 6.5;
        const temp = parseFloat(elements.recTempInput.value) || 24.0;
        const hum = parseFloat(elements.recHumInput.value) || 65.0;
        const rain = parseFloat(elements.recRainInput.value) || 100.0;
        const lang = getActiveLanguage();

        elements.btnPredictCrop.disabled = true;

        try {
            const res = await fetch("/api/recommend-crop", {
                method: "POST",
                headers: getApiHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify({
                    n, p, k, ph,
                    temperature: temp,
                    humidity: hum,
                    rainfall: rain,
                    lang
                })
            });
            const data = await res.json();
            if (data.success) {
                renderCropRecResult(data.recommendation);
                fetchStats();
                showToast(lang === "hi" ? "फसल अनुशंसा तैयार है!" : "Crop recommended successfully!", "success");
            } else {
                showToast(data.error || "Recommendation error.", "error");
            }
        } catch (err) {
            showToast("Failed to recommend crop: " + err.message, "error");
        } finally {
            elements.btnPredictCrop.disabled = false;
        }
    }

    function renderCropRecResult(rec) {
        elements.cropRecResultCard.classList.remove("hidden");
        const top = rec.recommended_crop;

        document.getElementById("resTopCropIcon").textContent = top.icon || "🌾";
        document.getElementById("resTopCropName").textContent = top.name;
        document.getElementById("resTopCropDuration").textContent = `${top.season} • ${top.duration}`;
        document.getElementById("resTopCropConfidence").textContent = `${top.confidence}%`;
        document.getElementById("resTopCropTip").textContent = top.cultivation_tip;
        document.getElementById("resCropExplanation").textContent = rec.explanation;

        // Alternatives
        const altContainer = document.getElementById("resCropAlternativesList");
        altContainer.innerHTML = (rec.alternatives || []).map(alt => `
            <div class="bg-white border border-slate-200 p-4 rounded-xl flex items-center justify-between shadow-sm">
                <div class="flex items-center space-x-3">
                    <span class="text-2xl">${alt.icon}</span>
                    <span class="font-bold text-slate-800 text-sm">${alt.name}</span>
                </div>
                <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                    ${alt.confidence}%
                </span>
            </div>
        `).join("");

        elements.cropRecResultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // =========================================================================
    // SOIL ADVISORY MODULE
    // =========================================================================
    function setupSoilPresets() {
        const presets = {
            low_n: { n: 45, p: 40, k: 35, ph: 6.8, type: "loamy" },
            acidic: { n: 85, p: 45, k: 50, ph: 5.2, type: "clayey" },
            alkaline: { n: 90, p: 55, k: 60, ph: 8.4, type: "sandy" },
            balanced: { n: 110, p: 55, k: 45, ph: 6.7, type: "loamy" }
        };

        document.querySelectorAll("[data-soil-preset]").forEach(btn => {
            btn.addEventListener("click", () => {
                const key = btn.getAttribute("data-soil-preset");
                const p = presets[key];
                if (!p) return;

                elements.soilNInput.value = p.n;
                elements.soilPInput.value = p.p;
                elements.soilKInput.value = p.k;
                elements.soilPhInput.value = p.ph;
                elements.soilPhDisplay.textContent = p.ph.toFixed(1);
                elements.soilTypeSelect.value = p.type;
                updatePhGauge(p.ph);
                showToast(`Loaded ${key.replace('_', ' ')} preset.`, "info");
            });
        });
    }

    function updatePhGauge(ph) {
        if (!elements.phIndicatorPin) return;
        const minPh = 4.0;
        const maxPh = 9.5;
        const clamped = Math.max(minPh, Math.min(maxPh, ph));
        const pct = ((clamped - minPh) / (maxPh - minPh)) * 100;
        elements.phIndicatorPin.style.left = `${pct}%`;
    }

    async function calculateSoilPlan() {
        const crop = elements.soilCropSelect.value;
        const n = parseFloat(elements.soilNInput.value) || 0;
        const p = parseFloat(elements.soilPInput.value) || 0;
        const k = parseFloat(elements.soilKInput.value) || 0;
        const ph = parseFloat(elements.soilPhInput.value) || 7.0;
        const soilType = elements.soilTypeSelect.value;
        const lang = getActiveLanguage();

        elements.btnCalcSoil.disabled = true;

        try {
            const res = await fetch("/api/soil-advisory", {
                method: "POST",
                headers: getApiHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify({ crop, n, p, k, ph, soil_type: soilType, lang })
            });
            const data = await res.json();
            if (data.success) {
                renderSoilResult(data.advisory);
                fetchStats();
                showToast(lang === "hi" ? "उर्वरक योजना तैयार है!" : "Soil advisory calculated!", "success");
            } else {
                showToast(data.error, "error");
            }
        } catch (err) {
            showToast("Soil calculation error: " + err.message, "error");
        } finally {
            elements.btnCalcSoil.disabled = false;
        }
    }

    function renderSoilResult(adv) {
        elements.soilResultCard.classList.remove("hidden");
        document.getElementById("resSoilSummary").textContent = adv.soil_summary;
        document.getElementById("resPhAdvice").textContent = adv.ph_advice;

        const n = adv.nutrient_status.nitrogen;
        const p = adv.nutrient_status.phosphorus;
        const k = adv.nutrient_status.potassium;
        
        document.getElementById("resNLevel").textContent = `${n.value} kg/ha (${n.level})`;
        document.getElementById("resPLevel").textContent = `${p.value} kg/ha (${p.level})`;
        document.getElementById("resKLevel").textContent = `${k.value} kg/ha (${k.level})`;

        const plan = adv.fertilizer_plan_per_acre;
        document.getElementById("resUreaKg").textContent = `${plan.urea_kg} kg`;
        document.getElementById("resUreaBags").textContent = `(~${(plan.urea_kg / 45).toFixed(1)} bags of 45kg)`;
        
        document.getElementById("resDapKg").textContent = `${plan.dap_kg} kg`;
        document.getElementById("resDapBags").textContent = `(~${(plan.dap_kg / 50).toFixed(1)} bags of 50kg)`;
        
        document.getElementById("resMopKg").textContent = `${plan.mop_potash_kg} kg`;
        document.getElementById("resMopBags").textContent = `(~${(plan.mop_potash_kg / 50).toFixed(1)} bags of 50kg)`;

        const orgList = document.getElementById("resOrganicRemediesList");
        orgList.innerHTML = (adv.organic_remedies || [])
            .map(item => `<li class="text-sm text-slate-700 mb-1.5 flex items-start"><span class="text-emerald-600 mr-2 font-bold">🌱</span><span>${item}</span></li>`)
            .join("");

        elements.soilResultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // =========================================================================
    // IRRIGATION GUIDANCE MODULE
    // =========================================================================
    async function getIrrigationGuidance() {
        const crop = elements.irriCropSelect.value;
        const stage = elements.irriStageSelect.value;
        const soilType = elements.irriSoilSelect.value;
        const season = elements.irriSeasonSelect.value;
        const lang = getActiveLanguage();

        elements.btnGetIrri.disabled = true;

        try {
            const res = await fetch("/api/irrigation-advisory", {
                method: "POST",
                headers: getApiHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify({ crop, stage, soil_type: soilType, season, lang })
            });
            const data = await res.json();
            if (data.success) {
                renderIrrigationResult(data.guidance);
                showToast(lang === "hi" ? "सिंचाई सारणी तैयार है!" : "Irrigation guidance generated!", "success");
            }
        } catch (err) {
            showToast("Irrigation error: " + err.message, "error");
        } finally {
            elements.btnGetIrri.disabled = false;
        }
    }

    function renderIrrigationResult(gui) {
        const lang = getActiveLanguage();
        elements.irriResultCard.classList.remove("hidden");

        document.getElementById("resIrriInterval").textContent = `Every ${gui.recommended_interval_days} Days`;
        document.getElementById("resIrriMethod").textContent = gui.recommended_method;

        const stagesContainer = document.getElementById("resCriticalStagesList");
        stagesContainer.innerHTML = (gui.critical_stages || []).map(st => `
            <div class="p-3 bg-white border border-slate-200 rounded-xl mb-2 flex items-center justify-between">
                <div>
                    <span class="font-semibold text-slate-800">${lang === "hi" ? st.stage_hi : st.stage_en}</span>
                </div>
                <span class="px-2.5 py-1 text-xs font-bold rounded-lg ${st.importance === 'Most Critical' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-amber-100 text-amber-700 border border-amber-200'}">
                    ${st.importance}
                </span>
            </div>
        `).join("");

        const tipsContainer = document.getElementById("resWaterTipsList");
        tipsContainer.innerHTML = (gui.actionable_tips || [])
            .map(tip => `<li class="text-sm text-slate-700 mb-1 flex items-start"><span class="text-blue-500 mr-2">💧</span><span>${tip}</span></li>`)
            .join("");

        elements.irriResultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // =========================================================================
    // KISAN MITRA AGRI-BOT
    // =========================================================================
    function setupChatbot() {
        if (!elements.btnSendChat || !elements.chatInput) return;

        elements.btnSendChat.addEventListener("click", sendChatMessage);
        elements.chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") sendChatMessage();
        });

        elements.chatChips.forEach(chip => {
            chip.addEventListener("click", () => {
                const prompt = chip.getAttribute("data-prompt");
                if (prompt) {
                    elements.chatInput.value = prompt;
                    sendChatMessage();
                }
            });
        });
    }

    async function sendChatMessage() {
        const text = elements.chatInput.value.trim();
        if (!text) return;
        const lang = getActiveLanguage();

        appendChatBubble("user", text);
        elements.chatInput.value = "";

        const typingId = "typing-" + Date.now();
        const typingEl = document.createElement("div");
        typingEl.id = typingId;
        typingEl.className = "flex items-start mb-3";
        typingEl.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center text-sm mr-2.5">🤖</div>
            <div class="chat-bubble-bot p-3 rounded-2xl text-sm italic text-slate-500">
                ${lang === "hi" ? "किसान मित्र उत्तर तैयार कर रहा है..." : "Kisan Mitra is answering..."}
            </div>
        `;
        elements.chatMessagesList.appendChild(typingEl);
        elements.chatMessagesList.scrollTop = elements.chatMessagesList.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: getApiHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify({ message: text, lang: lang, api_key: state.apiKey || undefined })
            });
            const data = await res.json();
            
            const el = document.getElementById(typingId);
            if (el) el.remove();

            if (data.success) {
                appendChatBubble("bot", data.reply);
            }
        } catch (err) {
            const el = document.getElementById(typingId);
            if (el) el.remove();
            appendChatBubble("bot", "Error connecting to assistant: " + err.message);
        }
    }

    function appendChatBubble(sender, message) {
        const div = document.createElement("div");
        div.className = `flex items-start mb-3 ${sender === "user" ? "justify-end" : "justify-start"}`;

        if (sender === "user") {
            div.innerHTML = `
                <div class="chat-bubble-user p-3.5 rounded-2xl text-sm max-w-[85%] sm:max-w-[75%] shadow-sm">
                    ${escapeHtml(message)}
                </div>
            `;
        } else {
            const formatted = message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br/>');

            div.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center text-sm mr-2.5 flex-shrink-0 shadow-sm">🤖</div>
                <div class="chat-bubble-bot p-3.5 rounded-2xl text-sm max-w-[85%] sm:max-w-[75%] shadow-sm leading-relaxed">
                    ${formatted}
                </div>
            `;
        }

        elements.chatMessagesList.appendChild(div);
        elements.chatMessagesList.scrollTop = elements.chatMessagesList.scrollHeight;
    }

    // =========================================================================
    // HISTORY & RECORDS
    // =========================================================================
    async function fetchHistory() {
        try {
            const res = await fetch("/api/history");
            const data = await res.json();
            if (data.success) {
                renderHistoryTables(data);
            }
        } catch (err) {
            console.error("Failed to fetch history:", err);
        }
    }

    function renderHistoryTables(data) {
        const lang = getActiveLanguage();
        
        // 1. Diagnoses table
        if (elements.diagHistoryTableBody) {
            elements.diagHistoryTableBody.innerHTML = "";
            if (!data.diagnoses || data.diagnoses.length === 0) {
                elements.diagHistoryTableBody.innerHTML = `
                    <tr><td colspan="5" class="py-6 text-center text-slate-400 text-sm">
                        ${lang === "hi" ? "कोई निदान रिकॉर्ड नहीं मिला।" : "No diagnosis records found."}
                    </td></tr>
                `;
            } else {
                data.diagnoses.forEach(d => {
                    const tr = document.createElement("tr");
                    tr.className = "border-b border-slate-100 hover:bg-slate-50 transition";
                    tr.innerHTML = `
                        <td class="py-3 px-4 text-xs text-slate-500 whitespace-nowrap">${d.timestamp}</td>
                        <td class="py-3 px-4 font-semibold text-slate-800 capitalize">${d.crop_label || d.crop}</td>
                        <td class="py-3 px-4 text-emerald-800 font-medium">${d.disease_name}</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-0.5 rounded text-xs font-bold ${d.confidence >= 80 ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                                ${d.confidence}%
                            </span>
                        </td>
                        <td class="py-3 px-4 text-right">
                            <button class="delete-diag-btn text-rose-500 hover:text-rose-700 text-xs font-semibold px-2 py-1 rounded" data-id="${d.id}">
                                ${lang === "hi" ? "हटाएं" : "Delete"}
                            </button>
                        </td>
                    `;
                    elements.diagHistoryTableBody.appendChild(tr);
                });

                document.querySelectorAll(".delete-diag-btn").forEach(btn => {
                    btn.addEventListener("click", async () => {
                        const id = btn.getAttribute("data-id");
                        await deleteHistoryItem("diagnoses", id);
                    });
                });
            }
        }

        // 2. Crop Recommendations table
        if (elements.cropRecHistoryTableBody) {
            elements.cropRecHistoryTableBody.innerHTML = "";
            if (!data.crop_recommendations || data.crop_recommendations.length === 0) {
                elements.cropRecHistoryTableBody.innerHTML = `
                    <tr><td colspan="6" class="py-6 text-center text-slate-400 text-sm">
                        ${lang === "hi" ? "कोई फसल चयन रिकॉर्ड नहीं मिला।" : "No crop recommendation records found."}
                    </td></tr>
                `;
            } else {
                data.crop_recommendations.forEach(r => {
                    const tr = document.createElement("tr");
                    tr.className = "border-b border-slate-100 hover:bg-slate-50 transition";
                    tr.innerHTML = `
                        <td class="py-3 px-4 text-xs text-slate-500 whitespace-nowrap">${r.timestamp}</td>
                        <td class="py-3 px-4 font-bold text-emerald-900">${r.recommended_crop}</td>
                        <td class="py-3 px-4 text-xs text-slate-600">N:${r.n_val} P:${r.p_val} K:${r.k_val}</td>
                        <td class="py-3 px-4 text-xs text-slate-600">${r.temperature}°C, ${r.rainfall}mm, pH ${r.ph_val}</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800">
                                ${r.confidence}%
                            </span>
                        </td>
                        <td class="py-3 px-4 text-right">
                            <button class="delete-rec-btn text-rose-500 hover:text-rose-700 text-xs font-semibold px-2 py-1 rounded" data-id="${r.id}">
                                ${lang === "hi" ? "हटाएं" : "Delete"}
                            </button>
                        </td>
                    `;
                    elements.cropRecHistoryTableBody.appendChild(tr);
                });

                document.querySelectorAll(".delete-rec-btn").forEach(btn => {
                    btn.addEventListener("click", async () => {
                        const id = btn.getAttribute("data-id");
                        await deleteHistoryItem("crop_recommendations", id);
                    });
                });
            }
        }

        // 3. Soil table
        if (elements.soilHistoryTableBody) {
            elements.soilHistoryTableBody.innerHTML = "";
            if (!data.soil_records || data.soil_records.length === 0) {
                elements.soilHistoryTableBody.innerHTML = `
                    <tr><td colspan="5" class="py-6 text-center text-slate-400 text-sm">
                        ${lang === "hi" ? "कोई मृदा रिकॉर्ड नहीं है।" : "No soil records saved yet."}
                    </td></tr>
                `;
            } else {
                data.soil_records.forEach(s => {
                    const tr = document.createElement("tr");
                    tr.className = "border-b border-slate-100 hover:bg-slate-50 transition";
                    tr.innerHTML = `
                        <td class="py-3 px-4 text-xs text-slate-500 whitespace-nowrap">${s.timestamp}</td>
                        <td class="py-3 px-4 font-semibold text-slate-800 capitalize">${s.crop}</td>
                        <td class="py-3 px-4 text-xs text-slate-600">N: ${s.n_val} | P: ${s.p_val} | K: ${s.k_val}</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">
                                pH ${s.ph_val}
                            </span>
                        </td>
                        <td class="py-3 px-4 text-right">
                            <button class="delete-soil-btn text-rose-500 hover:text-rose-700 text-xs font-semibold px-2 py-1 rounded" data-id="${s.id}">
                                ${lang === "hi" ? "हटाएं" : "Delete"}
                            </button>
                        </td>
                    `;
                    elements.soilHistoryTableBody.appendChild(tr);
                });

                document.querySelectorAll(".delete-soil-btn").forEach(btn => {
                    btn.addEventListener("click", async () => {
                        const id = btn.getAttribute("data-id");
                        await deleteHistoryItem("soil_records", id);
                    });
                });
            }
        }
    }

    async function deleteHistoryItem(table, id) {
        try {
            const res = await fetch(`/api/history/${table}/${id}`, { method: "DELETE" });
            const data = await res.json();
            if (data.success) {
                showToast("Record removed.", "info");
                fetchHistory();
                fetchStats();
            }
        } catch (err) {
            showToast("Delete failed: " + err.message, "error");
        }
    }

    async function seedSampleData() {
        try {
            const res = await fetch("/api/seed-sample-data", { method: "POST" });
            const data = await res.json();
            if (data.success) {
                showToast(data.message, "success");
                fetchHistory();
                fetchStats();
            }
        } catch (err) {
            showToast("Failed to seed sample data: " + err.message, "error");
        }
    }

    // =========================================================================
    // STATS & UTILITIES
    // =========================================================================
    async function fetchStats() {
        try {
            const res = await fetch("/api/stats");
            const data = await res.json();
            if (data.success && data.stats) {
                if (elements.statDiagCount) elements.statDiagCount.textContent = data.stats.total_diagnoses;
                if (elements.statRecCount) elements.statRecCount.textContent = data.stats.total_crop_recommendations || 0;
                if (elements.statConfAvg) elements.statConfAvg.textContent = `${data.stats.average_confidence}%`;
                if (elements.statSoilCount) elements.statSoilCount.textContent = data.stats.total_soil_advisories;
            }
        } catch (err) {
            console.error("Stats error:", err);
        }
    }

    function showToast(message, type = "info") {
        const toast = document.getElementById("toastNotification");
        const msgEl = document.getElementById("toastMessage");
        const iconEl = document.getElementById("toastIcon");
        if (!toast || !msgEl) return;

        msgEl.textContent = message;
        if (type === "success") {
            iconEl.textContent = "✅";
            toast.className = "fixed bottom-5 right-5 z-50 bg-emerald-800 text-white px-4 py-3 rounded-xl shadow-lg flex items-center space-x-2";
        } else if (type === "error") {
            iconEl.textContent = "❌";
            toast.className = "fixed bottom-5 right-5 z-50 bg-rose-700 text-white px-4 py-3 rounded-xl shadow-lg flex items-center space-x-2";
        } else if (type === "warning") {
            iconEl.textContent = "⚠️";
            toast.className = "fixed bottom-5 right-5 z-50 bg-amber-600 text-white px-4 py-3 rounded-xl shadow-lg flex items-center space-x-2";
        } else {
            iconEl.textContent = "ℹ️";
            toast.className = "fixed bottom-5 right-5 z-50 bg-slate-800 text-white px-4 py-3 rounded-xl shadow-lg flex items-center space-x-2";
        }

        toast.classList.remove("hidden", "opacity-0");
        toast.classList.add("opacity-100");

        setTimeout(() => {
            toast.classList.add("opacity-0");
            setTimeout(() => toast.classList.add("hidden"), 300);
        }, 3500);
    }

    function escapeHtml(string) {
        const div = document.createElement("div");
        div.innerText = string;
        return div.innerHTML;
    }
});
