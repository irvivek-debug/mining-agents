# Agent Recordings — Sales Companion

One entry per agent. Each recording opens on the operational question,
shows the agent reading BigQuery live (the tool trace), then scrolls
the answer at reading pace. Note for live demos: agents answer in
seconds via the API but typically 2–4 minutes through the chat UI —
the on-screen tool trace is the proof of grounding; narrate over it.

## Strategic Planning Advisor (AGT-19)

*Commercial/Finance/Strategy — CEO / CFO / Executive Committee*

**The ask.** Pit 4 copper price projection drops 15% from $4.20/lb to $3.57/lb. With mining cost $3.10/t, milling cost $14.50/t, and 89.5% recovery, calculate dynamic Kenneth Lane cut-off grade sensitivity. **What the agent does.** It looks up the geological block model, the financial ledger and the mine production schedule — the operation's live data, not a briefing pack — and answers in its own words: “Strategic Planning Advisor (AGT-19) —” It reports real figures — 4.20, 9,259.42, 9,114.60 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/AGT-19/page@5080d25b285face0a1fce5059dba2e58.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2639398376744540579/session/-

## Core Image Segmenter (D01)

*Exploration/Geology — Elena (Mine Geologist)*

**The ask.** Calculate RQD on drill core tray #104 with lengths [12, 18, 8, 22, 14, 5, 25]cm on 120cm run. **What the agent does.** It looks up drill hole records — the operation's live data, not a briefing pack — and answers in its own words: “Core Image Segmentation & RQD” It reports real figures — 75.83%, 86.67% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D01/page@bc961b1c735927573c1e1c01da6a50b8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7961791724780686286/session/-

## Hyperspectral Mineral Mapper (D02)

*Exploration/Geology — Geochemist*

**The ask.** Extract sericite vs illite crystallinity ratio from 2200nm SWIR spectral reflection. **What the agent does.** It looks up drill hole records and assay results — the operation's live data, not a briefing pack — and answers in its own words: “SWIR/VNIR Spectral Feature Extraction: Sericite vs. Illite” It reports real figures — 1.5, 2.0, 1.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D02/page@922bb7b5f647e55deb20acaf0fe2d32a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/905468479589496947/session/-

## JORC Classification Auditor (D03)

*Exploration/Geology — Competent Person*

**The ask.** Audit drill spacing confidence for 25x25m vs 50x50m drill grids. **What the agent does.** It looks up drill hole records and the geological block model — the operation's live data, not a briefing pack — and answers in its own words: “JORC Classification Audit: Drill Spacing Confidence Analysis (25×25m vs. 50×50m” It reports real figures — 86.5%, 88.6%, 0.14 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Spatial Drill Spacing Confidence Index method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D03/page@1f7b5e871afc45da0d77f07b45a2c045.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4649342689434985829/session/-

## Blast Wave Front Sim (D04)

*Mine Planning/Operations — D&B Specialist*

**The ask.** Calculate CJ detonation pressure for emulsion with density 1.18 g/cm3 and VOD 5400 m/s. **What the agent does.** It looks up blast designs — the operation's live data, not a briefing pack — and answers in its own words: “1. Database Reconciliation & Operational” It reports real figures — 0.797, 4.0, 7.5 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Chapman-Jouguet Detonation Hugoniot Solver method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D04/page@4faac4ee77e745975b0be085e8db63d1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17821761931664506582/session/-

## Flyrock Trajectory Predictor (D05)

*Mine Planning/Operations — Shotfirer*

**The ask.** Compute maximum flyrock travel distance for 45 deg ejection angle at v0=42 m/s. **What the agent does.** It looks up blast designs — the operation's live data, not a briefing pack — and answers in its own words: “Flyrock Trajectory” It reports real figures — 9.81, 9.80665, 4.01 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D05/page@a492725ae5317558788c85a2d058229d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12044950816072083474/session/-

## In-Situ Fragment Analyzer (D06)

*Mine Planning/Operations — D&B Engineer*

**The ask.** Fit Rosin-Rammler muckpile curve for xc=120mm and uniformity index n=1.15. **What the agent does.** It looks up blast designs — the operation's live data, not a briefing pack — and answers in its own words: “Model: Rosin-Rammler (Weibull) Size Distribution” It reports real figures — 1.15, 5.5056, 16.96 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Split-Desktop High-Res Image Segmentation method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D06/page@94f5efbce29f0f655a021d7d1d1be0fc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17733897435877732313/session/-

## Radar Slope Displacement (D07)

*Mine Planning/Operations — Geotech Engineer*

**The ask.** Calculate Fukuzono inverse velocity failure time for 14 mm/day bench creep. **What the agent does.** It looks up geotechnical sensor readings — the operation's live data, not a briefing pack — and answers in its own words: “Operational Baseline & Assumption” It reports real figures — 14.000, 9.794, 0.1 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D07/page@77d809a5eeff8634329106ccf8a4092c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5771882020233678970/session/-

## Borehole Seismicity Sentinel (D08)

*Mine Planning/Operations — Microseismic Technician*

**The ask.** Compute microseismic b-value for 120 seismic events on North Pit fault. **What the agent does.** It looks up geotechnical sensor readings — the operation's live data, not a briefing pack — and answers in its own words: “Operational & Data Reconciliation” It reports real figures — 2.400, 6.341, 35.1 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D08/page@ac4c23afe7ccc4afefdce6b77530df1a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16222986639730781285/session/-

## Bench Drainage Permeability (D09)

*Mine Planning/Operations — Hydrogeologist*

**The ask.** Calculate discharge rate for 12 horizontal drain holes with k=1e-5 m/s. **What the agent does.** It looks up pit designs — the operation's live data, not a briefing pack — and answers in its own words: “Discharge rate is governed by Darcy's” It reports real figures — 2.05, 2.98, 1.2 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D09/page@8f863410087a58b197ad1bd263a1b02d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1371995073496644570/session/-

## Haul Road Rolling Resist (D10)

*Fleet/Haulage — Civil Road Superintendent*

**The ask.** Calculate rimpull requirement for CAT 797F (550t GMW) on 8% ramp with 3% rolling resistance. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Reconciliation of Assumptions against Operational” It reports real figures — 240.0 t, 205.02 t, 130.63 t — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D10/page@7325678bae041c230b5a00f6bed60832.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10833388638952133340/session/-

## Fleet Fuel Burn Sentinel (D11)

*Fleet/Haulage — Energy Manager*

**The ask.** Calculate diesel consumption intensity (L/t-km) for 4.2km haul cycle. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Telemetry & Governing” It reports real figures — 4.2, 0.534, 533.75 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D11/page@ca2b9b6ce68dc22e71a5a06daf08dccb.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13101384251525449016/session/-

## Tire TKPH Telemetry Agent (D12)

*Fleet/Haulage — Mobile Fleet Maintenance Lead*

**The ask.** Calculate tire TKPH for 238t payload at 24 km/h average cycle speed. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Agent Identity & Governing” It reports real figures — 238.00 t, 205.02 t, 130.63 t — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D12/page@927480fa3c780e947356a2fb6fd73848.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9758962924959748081/session/-

## Shovel GET Tooth Sentinel (D13)

*Fleet/Haulage — Shovel Operator*

**The ask.** Scan Shovel #04 dipper bucket camera feed for missing ground engaging tool tooth. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Shovel GET Tooth Sentinel (Agent d13) — Inspection” It reports real figures — 116.8311, 23.1686, 42.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its YOLOv8 Ground Engaging Tool Watcher method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D13/page@310e2bf79f42e9a821b34622ea581ce5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6134679660633629158/session/-

## Autogenous Grinding Sound (D14)

*Mineral Processing/Plant — Mill Operator*

**The ask.** Analyze SAG mill acoustic FFT power spectrum at 1200-2400 Hz. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Acoustic Power Spectrum 1/3-Octave Band Analysis (1200–2400” It reports real figures — 14.50, 14.80, 13.41 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D14/page@0408826dcdbbf5e8df56e38cb94e1aaf.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17829819385329910239/session/-

## Trommel Screen Blinding (D15)

*Mineral Processing/Plant — Concentrator Technician*

**The ask.** Calculate aperture blinding percentage on SAG discharge trommel. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Domain: Quantifies screen mesh aperture blinding and near-size pegging on Semi-Autogenous Grinding (SAG) discharge” It reports real figures — 13.41, 15.63, 14.50 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Aperture Occlusion Optical Flow Percentage method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D15/page@673f7f9dff737f598ca3a203197d0d54.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6344681735013446444/session/-

## Slurry Pump Cavitation (D16)

*Mineral Processing/Plant — Fixed Plant Fitter*

**The ask.** Calculate available Net Positive Suction Head for slurry pump #3 at 65% solids. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Data Reconciliation & Telemetry” It reports real figures — 71.42, 65.01, 89.68 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D16/page@fc4a46d2b9576917ab9ba940d2dccae5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3255539541494084213/session/-

## Sump Level Anti-Surge (D17)

*Mineral Processing/Plant — Process Control Specialist*

**The ask.** Regulate sump level PID speed for 3,800 tph feed slurry surge. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Agent Name / System Role: Sump Level Anti-Surge” It reports real figures — 3,800.0, 1,210.0, 214.0% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D17/page@6221cbec4e802124a0248b8c0ef2f2ed.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7025307563315550538/session/-

## Froth Bubble Sizing/Color (D18)

*Mineral Processing/Plant — Flotation Technician*

**The ask.** Measure Sauter mean bubble diameter d32 on rougher flotation cell #4. **What the agent does.** It looks up flotation assay results and plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Asset Identification & Operating” It reports real figures — 7.65, 135.4, 0.0092 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Sauter Mean Bubble Diameter d32 & RGB Grade Proxy method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D18/page@50dacec5ab694a930eda12352599b641.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17273012408267433389/session/-

## Xanthate Degradation (D19)

*Mineral Processing/Plant — Reagent Chemist*

**The ask.** Calculate potassium amyl xanthate (PAX) potency after 72 hours storage at 32 deg C. **What the agent does.** It looks up reagent stock levels — the operation's live data, not a briefing pack — and answers in its own words: “Operational Grounding & Reagent” It reports real figures — 7 days, 57.54, 8.314 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D19/page@a6f66e2bbce8d6bc6b6d945d6fffbaae.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2463177645997507271/session/-

## Acid Mine Drainage ORP (D20)

*Mineral Processing/Plant — Environmental Superintendent*

**The ask.** Calculate hydrated lime Ca(OH)2 dosage to neutralize pit sump pH from 3.2 to 7.5. **What the agent does.** It looks up water balance logs — the operation's live data, not a briefing pack — and answers in its own words: “Hydrated Lime $\text{Ca(OH)}_2$ Neutralization & Electrochemical” It reports real figures — 3.2, 7.5, 23.39 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D20/page@4529ddfdd70f49fb576741bb686becb3.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1126839582103419021/session/-

## Tailings Beach Slope (D21)

*Mineral Processing/Plant — TSF Engineer*

**The ask.** Predict beach slope angle for thickened tailings with yield stress 65 Pa. **What the agent does.** It looks up tailings dam sensor readings — the operation's live data, not a briefing pack — and answers in its own words: “1. Governing Deposition” It reports real figures — 0.10, 0.05, 0.15 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D21/page@15ef490f0fc88e1a45763eaee8e12a96.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5611152752644422239/session/-

## Transformer Dissolved Gas (D22)

*Asset Integrity/Maintenance — HV Electrician*

**The ask.** Plot Duval Triangle 1 coordinates for Main Substation transformer oil. **What the agent does.** It looks up the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Transformer Dissolved Gas Analysis (DGA) & Duval Triangle 1” It reports real figures — 8.38, 65.0, 116.8737 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D22/page@3a9b80e403512e4eaa8e850f7a7d885f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17610690989667960583/session/-

## Motor Partial Discharge (D23)

*Asset Integrity/Maintenance — Electrical Engineer*

**The ask.** Analyze stator winding partial discharge for 15 MW SAG mill synchronous motor. **What the agent does.** It looks up the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Agent Profile &” It reports real figures — 6.6, 4.25, 4.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its High-Frequency Transient Phase-Resolved PD method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D23/page@5789cb9621aef3e82d61d870f77c149b.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5183629188203019270/session/-

## Conveyor Belt Rip Ultra (D24)

*Asset Integrity/Maintenance — Belt Splicer Lead*

**The ask.** Monitor ultrasonic sensor array on 4km overland coarse ore conveyor CV-01. **What the agent does.** It looks up the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Asset Identification & Assumption” It reports real figures — 116.8045, 23.1614, 5.24 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Time-of-Flight Acoustic Wave Attenuation method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D24/page@296c4d239055473c21385c4168f00a46.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12470560680853903472/session/-

## Chute Wear Ultrasonic (D25)

*Asset Integrity/Maintenance — Boilermaker Lead*

**The ask.** Measure remaining Hardox 500 liner thickness on Crusher discharge chute. **What the agent does.** It looks up the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Method & Governing” It reports real figures — 5.90, 1210.0, 120.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D25/page@17f26996381a1098d01933c320041da2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5181698511014105791/session/-

## Maintenance Work Backlog (D26)

*Asset Integrity/Maintenance — Tom (Maintenance Planner)*

**The ask.** Calculate schedule float for SAG mill liner replacement critical path. **What the agent does.** It looks up open work orders — the operation's live data, not a briefing pack — and answers in its own words: “Under the Critical Path Method (CPM) governing methodology, the schedule float (Total Float) for the critical path of the SAG mill liner replacement is 0” It reports real figures — 0 hours, 351.2 hours, 10.03 hours — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D26/page@c19658c4033771130340d779a966261d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/424629171197778528/session/-

## Contractor Idle Fee Audit (D27)

*Commercial/Finance/Strategy — Commercial Manager*

**The ask.** Audit 48 hours standby claim for contractor dozer fleet against FMS GPS movement. **What the agent does.** It looks up supplier contracts and live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Contractor Idle Fee Audit” It reports real figures — 48 hours, 48.0, 0.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Standby Hours vs Daily Rate Dispute Validator method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D27/page@763f50c431cf0e8485d2b933b5f5d49e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14871181550156206719/session/-

## Fuel Bunkering Density (D28)

*Commercial/Finance/Strategy — Fuel Logistics Officer*

**The ask.** Calculate temperature-corrected diesel fuel volume for 120,000L bunkering at 34 deg C. **What the agent does.** It looks up purchase-order history — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Data Reconciliation & Table” It reports real figures — 141.5, 131.5, 840.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D28/page@2355850b717c308b608ac90f14a441a1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8219039806167601700/session/-

## Grinding Ball Wear Batch (D29)

*Asset Integrity/Maintenance — Plant Metallurgist*

**The ask.** Calculate daily grinding ball consumption rate for Wi=14.2 kWh/t ore. **What the agent does.** It looks up spare parts stock and plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Governing Method & Specific Wear Rate” It reports real figures — 0.16, 0.5, 14.2 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D29/page@94d105ced7be12c62c612bea5f363959.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16177627500456872112/session/-

## Lube Oil Cleanliness (D30)

*Asset Integrity/Maintenance — Tribologist*

**The ask.** Parse particle count data for SAG mill pinion lube oil reservoir. **What the agent does.** It looks up the asset register and oil sample analyses — the operation's live data, not a briefing pack — and answers in its own words: “Asset Identification & Operational” It reports real figures — 14.8, 452.0, 4.25 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its ISO 4406 Solid Contamination Cleanliness Code method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D30/page@387f4ba483fcad8aa7c5302c8e38b86a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3203587165096507461/session/-

## Consignment Stock Logger (D32)

*Supply Chain/Logistics — Warehouse Clerk*

**The ask.** Reconcile warehouse RFID scan against SAP goods issue for 12 pump seals. **What the agent does.** It looks up spare parts stock — the operation's live data, not a briefing pack — and answers in its own words: “Consignment Stock Logger” It reports real figures — 450.00, 900.00, 7 days — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its RFID Tag vs SAP Movement Type 201 Reconciler method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D32/page@bdb55e96b96f04fa46d4cca65bbd7753.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4122039674810283352/session/-

## Laytime BIMCO Parser (D33)

*Supply Chain/Logistics — Logistics Officer*

**The ask.** Parse port laytime statement for 'MV Bulk Pioneer' under rain interruptions. **What the agent does.** It looks up vessel movements at the port — the operation's live data, not a briefing pack — and answers in its own words: “Port Laytime & Statement of Fact (SOF) Parsing” It reports real figures — 75,542.0, 9.73%, 10.0% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its BIMCO Laytime Standard Statement of Fact Parser method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D33/page@188cb9202c100eb38104fd52e6302b34.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/583739645883463374/session/-

## Reagent Shelf Life (D34)

*Supply Chain/Logistics — Hazmat Technician*

**The ask.** Model shelf life degradation of sodium isopropyl xanthate (SIPX) at 38 deg C. **What the agent does.** It looks up reagent stock levels — the operation's live data, not a briefing pack — and answers in its own words: “1. Inventory & Reagent” It reports real figures — 57.54, 27.19, 28.03 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D34/page@c6cc7b99140b4911662ddd684b2b796d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8228845743322555862/session/-

## Locomotive Brake Curve (D35)

*Supply Chain/Logistics — Rail Master*

**The ask.** Calculate stopping distance for 12,000t loaded ore train at 60 km/h on 0.5% grade. **What the agent does.** It looks up rail schedules — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Data Reconciliation &” It reports real figures — 9,061.80, 25,920.40, 17,911.75 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D35/page@8fa8226b37634d0605174ffd7285365d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13394976667368344513/session/-

## Shiploader 3D LiDAR (D36)

*Supply Chain/Logistics — Shiploader Operator*

**The ask.** Monitor shiploader boom LiDAR sensor distance from vessel hatch coaming. **What the agent does.** It looks up vessel movements at the port — the operation's live data, not a briefing pack — and answers in its own words: “Shiploader 3D LiDAR Monitoring Report (Sentinel” It reports real figures — 5.0, 100,619.2, 6.84% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D36/page@be04413858a6dbe63585a327a57163ba.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17690808582680002326/session/-

## SAFTE Driver Fatigue (D37)

*Safety/OHSE/ESG — Jack (Mine Safety Lead)*

**The ask.** Calculate SAFTE bio-mathematical fatigue score for operator on 4th night shift. **What the agent does.** It looks up fatigue monitoring logs records — the operation's live data, not a briefing pack — and answers in its own words: “Biomathematical Fatigue Evaluation: 4th Consecutive Night” It reports real figures — 2.13 hours, 2.0, 4.2 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D37/page@0057d550a617a67b0ebf9878f55ad80f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4130455342070868544/session/-

## Confined Space Gas (D38)

*Safety/OHSE/ESG — Industrial Hygienist*

**The ask.** Evaluate multi-gas monitor telemetry inside SAG mill during liner inspection. **What the agent does.** It looks up safety telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Multi-Gas Monitor Telemetry Evaluation: SAG Mill Liner” It reports real figures — 19.5%, 23.5% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D38/page@a550512fe2097249680d7a9bfe082832.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10224314405726841486/session/-

## Carbon Scope 1/2 Tracker (D39)

*Safety/OHSE/ESG — Sustainability Lead*

**The ask.** Calculate monthly carbon intensity per tonne of copper cathode produced. **What the agent does.** It looks up live fleet telemetry and plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “GHG Protocol Governing” It reports real figures — 206.44, 75,970.58, 28.33 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D39/page@5b55e8c6ab0676e122f62e01563c7850.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9664629732570460254/session/-

## Statutory Permit Guardian (D40)

*Safety/OHSE/ESG — Legal Counsel & Compliance Officer*

**The ask.** Audit statutory environmental water discharge permit expiry timelines. **What the agent does.** It looks up tenement leases records and safety permits records — the operation's live data, not a briefing pack — and answers in its own words: “Statutory Permit & Tenement Lease Audit” It reports real figures — 2,482.00, 54,582.30, 1,014.10 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/D40/page@5173660c21353876c0c7008b76552bca.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12178037606655907260/session/-

## Drill Lithology Specialist (S01-1-LITHOLOGY)

*Exploration/Geology — Exploration Geologist*

**The ask.** Classify drill core tray #482 rock quality and fracture frequency. **What the agent does.** It looks up drill hole records — the operation's live data, not a briefing pack — and answers in its own words: “Governing Methodology & Classification” **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S01-1-LITHOLOGY/page@11b4e7675eb6dc439206c239eafcf4a5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5332440710463027597/session/-

## Assay Geostatistics Specialist (S01-2-GEOSTAT)

*Exploration/Geology — Geostatistician*

**The ask.** Compute estimation variance for copper block grades at Section 104N. **What the agent does.** It looks up assay results — the operation's live data, not a briefing pack — and answers in its own words: “Based on the spatial and geological data in the mining_data dataset, here is the geostatistical estimation variance analysis for copper block grades at Section 104N (Grid Northing $Y =…” It reports real figures — 1.0152%, 0.6140, 0.613979 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S01-2-GEOSTAT/page@e63942d6ef63cef57fae9758969a2f5f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9087835982665536979/session/-

## Structural Fault Specialist (S01-3-STRUCTURAL)

*Exploration/Geology — Structural Geologist*

**The ask.** Analyze strike and dip planes on Section 104N fault envelope. **What the agent does.** It looks up the geological block model — the operation's live data, not a briefing pack — and answers in its own words: “Structural Fault & Plane Orientation Analysis: Section 104N Fault” It reports real figures — 0.4468, 24.1, 0.168736 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S01-3-STRUCTURAL/page@01922a5bb2ee6e222ba9a476db976969.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2645900857098460761/session/-

## Geology Swarm Coordinator (S01-COORDINATOR)

*Exploration/Geology — Elena (Chief Mine Geologist)*

**The ask.** Synthesize Section 104N drillhole assays into Ordinary Kriging 3D block model. **What the agent does.** It looks up drill hole records, assay results and the geological block model — the operation's live data, not a briefing pack — and answers in its own words: “Geological Synthesis: Section 104N Drillhole Assays & Ordinary Kriging 3D Block” It reports real figures — 485,148.11, 7,432,325.23, 532.80 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S01-COORDINATOR/page@32e3f4291eddcd08090c1e66040de542.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2549813273247417527/session/-

## Resource Critic (JORC / QAQC Red Team) (S01-R-CRITIC)

*Exploration/Geology — Competent Person (CP / QP)*

**The ask.** Audit duplicate core sample assay variance against JORC Code standards. **What the agent does.** It looks up assay results and QA/QC standards — the operation's live data, not a briefing pack — and answers in its own words: “JORC / QA/QC Red Team Audit: Duplicate Core Sample Assay” It reports real figures — 0.00, 447.75, 0.0% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S01-R-CRITIC/page@a72f78ea535d5603f650f0812fb18c35.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13867639205775571505/session/-

## Pit Wall Geotechnical Specialist (S02-1-GEOTECH)

*Mine Planning/Operations — Geotechnical Engineer*

**The ask.** Calculate Bishop simplified Factor of Safety on 48 deg pit wall. **What the agent does.** It looks up geotechnical sensor readings — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Geotechnical Data” It reports real figures — 48.0, 121.60, 2.886 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S02-1-GEOTECH/page@d12a673167d4b782b2700515fea032f5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2467120801253827430/session/-

## Phase Scheduling Specialist (S02-2-SCHEDULE)

*Mine Planning/Operations — Long-Term Planning Engineer*

**The ask.** Sequence shovel assignments to balance 1.8 Mt/month ore extraction. **What the agent does.** It looks up the mine production schedule — the operation's live data, not a briefing pack — and answers in its own words: “Shovel Assignment Sequencing & Extraction” It reports real figures — 0.084, 0.9933, 8.40% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S02-2-SCHEDULE/page@15a1d4ea3edaf5209c1b8c1f6489b56e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14750280296794731530/session/-

## Waste Dump Stability Specialist (S02-3-DUMP)

*Mine Planning/Operations — Civil Mine Engineer*

**The ask.** Model North Dump toe containment volume and runout angle of repose. **What the agent does.** It looks up pit designs — the operation's live data, not a briefing pack — and answers in its own words: “Waste Dump Stability & Geotechnical Assessment: North Dump” It reports real figures — 51.25, 2.050, 2.01 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S02-3-DUMP/page@46010093d0ae366a64f91d3114300bec.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14198794820232846068/session/-

## Mine Planning Coordinator (S02-COORDINATOR)

*Mine Planning/Operations — Planning Superintendent*

**The ask.** Optimize Phase 3 pushback extraction sequence with 48 deg overall slope. **What the agent does.** It looks up the mine production schedule and pit designs — the operation's live data, not a briefing pack — and answers in its own words: “Technical Memorandum: Phase 3 Pushback Extraction Sequence” It reports real figures — 48.0, 45.0, 9,323.40 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S02-COORDINATOR/page@1360c1240b5d3eac6649588966057f78.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10031640407747179171/session/-

## Plan Compliance Critic (Red Team) (S02-R-CRITIC)

*Mine Planning/Operations — Senior Mine Surveyor*

**The ask.** Audit spatial compliance between monthly extraction and long-term model. **What the agent does.** It looks up survey scans and the mine production schedule — the operation's live data, not a briefing pack — and answers in its own words: “Spatial Compliance Audit: Monthly Extraction vs. Long-Term” It reports real figures — 0.0, 1.0056, 0.56% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S02-R-CRITIC/page@2f7d327bfe828612964f36a202d819cc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6834062730278861341/session/-

## Blast Geometry Specialist (S03-1-GEOMETRY)

*Mine Planning/Operations — D&B Engineer*

**The ask.** Design 180-hole staggered pattern for 15m production bench. **What the agent does.** It looks up blast designs — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Context & Assumption” It reports real figures — 15.0, 8.00, 16.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S03-1-GEOMETRY/page@1d43e0b754d0895a6fdbf05e049e3a81.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6899800456415450209/session/-

## Explosives Energy Specialist (S03-2-EXPLOSIVE)

*Mine Planning/Operations — Shotfirer Technical Lead*

**The ask.** Calculate bulk emulsion VOD and shock energy partitioning. **What the agent does.** It looks up explosives inventory — the operation's live data, not a briefing pack — and answers in its own words: “Explosives Energy & Detonation Analysis: Bulk Emulsion vs.” It reports real figures — 1.15, 1.25, 1.20 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S03-2-EXPLOSIVE/page@e09d031c80be43f61c0b52f21c7ae6d6.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/385821222619278877/session/-

## Blast Vibration Sentinel (S03-3-VIBRATION)

*Mine Planning/Operations — D&B Engineer*

**The ask.** Predict PPV vibration at primary crusher 450m from blast. **What the agent does.** It looks up blast designs — the operation's live data, not a briefing pack — and answers in its own words: “1. Governing Attenuation” It reports real figures — 5.60, 4.00, 17.11 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S03-3-VIBRATION/page@b5d01b4e6fb08828cf2b3871a1220c88.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9816945852212110694/session/-

## Drill & Blast Coordinator (S03-COORDINATOR)

*Mine Planning/Operations — Drill & Blast Superintendent*

**The ask.** Optimize burden and powder factor for hard granodiorite ($UCS=160 MPa$). **What the agent does.** It looks up blast designs and explosives inventory — the operation's live data, not a briefing pack — and answers in its own words: “Drill & Blast Optimization: Hard Granodiorite ($UCS = 160\text{” It reports real figures — 0.63, 0.8, 2.68 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S03-COORDINATOR/page@3c18176fa65bb3fea23611d35d655324.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6919052797483217132/session/-

## Blast Safety Critic (Red Team) (S03-R-CRITIC)

*Mine Planning/Operations — Statutory Shotfirer*

**The ask.** Enforce 500m blast exclusion perimeter and lightning warning gate. **What the agent does.** It looks up blast designs and safety permits records — the operation's live data, not a briefing pack — and answers in its own words: “Red Team Blast Safety Review & Statutory Gate” It reports real figures — 82.2%, 17.8%, 4.01 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Statutory Exclusion Zone Radius & Misfire Detection Gate method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S03-R-CRITIC/page@c66c61fbecc810d115455effd308f304.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3034965665875988605/session/-

## Shovel Match Specialist (S04-1-SHOVEL)

*Fleet/Haulage — Dispatch Controller*

**The ask.** Calculate pass match factor for PC8000 shovel loading CAT 797F. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Pass Match Analysis: Komatsu PC8000 Shovel loading CAT” It reports real figures — 240.0, 205.02, 130.63 t — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S04-1-SHOVEL/page@de2061e84f4e16644be8b7183aa16327.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17491806829630784661/session/-

## Haul Route Optimizer (S04-2-ROUTE)

*Fleet/Haulage — Fleet Planner*

**The ask.** Compute shortest path travel time on Pit Alpha south ramp. **What the agent does.** It looks up dispatch routes — the operation's live data, not a briefing pack — and answers in its own words: “Shortest Path & Flow Optimization” It reports real figures — 1,031.49, 11.57, 1.27 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S04-2-ROUTE/page@c63bac73df56f9feebf87faa407058dd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2596064410481970294/session/-

## Truck Payload Sentinel (S04-3-PAYLOAD)

*Fleet/Haulage — Fleet Controller*

**The ask.** Audit 10/10/20 payload distribution across 42 haul cycles. **What the agent does.** It looks up live fleet telemetry — the operation's live data, not a briefing pack — and answers in its own words: “OEM 10/10/20 Truck Payload Compliance” It reports real figures — 1.20, 240.00, 264.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S04-3-PAYLOAD/page@1cc792fd770a82d48d72a95d0303c650.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4572058693527972819/session/-

## Load & Haul Coordinator (S04-COORDINATOR)

*Fleet/Haulage — Dave (Dispatch Superintendent)*

**The ask.** Reassign haul trucks to eliminate 3-truck queue at Shovel 04. **What the agent does.** It looks up live fleet telemetry and dispatch routes — the operation's live data, not a briefing pack — and answers in its own words: “Dispatch Reassignment Order & Queue Elimination” It reports real figures — 116.8311, 23.1686, 42.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S04-COORDINATOR/page@e2c435bfbd648161e0fabbb4bf43df62.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/156538017085304316/session/-

## Dispatch Safety Critic (Red Team) (S04-R-CRITIC)

*Fleet/Haulage — Mine Safety Lead*

**The ask.** Check operator shift hours and SAFTE circadian fatigue index. **What the agent does.** It looks up live fleet telemetry and safety telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Shift Schedule & Operational Telemetry” It reports real figures — 7.77, 3.30, 2.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Haul Road Grade Braking Runaway Distance Envelope method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S04-R-CRITIC/page@a13fa27caad6722bea6942323ddd021f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/408790626050543109/session/-

## Crusher CSS Specialist (S05-1-CSS)

*Mineral Processing/Plant — Crusher Technician*

**The ask.** Based on the crusher telemetry data, what hydraulic pressure setpoint does your governing method indicate for a closed-side setting of 135mm? Report the figures from the data and cite the table you read. **What the agent does.** It looks up crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Based on an analysis of the telemetry data in genial-union-475913-i7.mining_data.crusher_telemetry (view over” It reports real figures — 135 mm, 115 mm, 1,157.98 tph — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S05-1-CSS/page@b265f8454a5f8fcf1e6270054f871f01.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14348532487284515913/session/-

## Feeder Speed Specialist (S05-2-FEED)

*Mineral Processing/Plant — Control Room Operator*

**The ask.** Regulate apron feeder PID loop for choke feeding conditions. **What the agent does.** It looks up crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Apron Feeder PID Loop Regulation for Choke” It reports real figures — 1,153.23, 1,026.30, 1,297.05 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S05-2-FEED/page@1f5c84170d0e7555d78bc039d1fc663a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5869281968369631097/session/-

## Mantle Wear Estimator (S05-3-WEAR)

*Mineral Processing/Plant — Fixed Plant Planner*

**The ask.** Predict remaining liner life on Hardox 500 concave plates. **What the agent does.** It looks up the asset register and crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Mantle Wear Estimator (s05_3_wear) — Liner Life” It reports real figures — 0.02, 4.905, 0.020 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S05-3-WEAR/page@1523fc960d23505a6e367f7a73164d1d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13456155721035413965/session/-

## Primary Crushing Coordinator (S05-COORDINATOR)

*Mineral Processing/Plant — Fixed Plant Superintendent*

**The ask.** Crusher-03 mantle wear is at 78%; eddy-current sensor flags tramp iron. **What the agent does.** It looks up crusher telemetry and the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Primary Crushing Coordinator Operational Assessment &” It reports real figures — 1,210.0 tph, 1,145.57 tph, 1,153.23 tph — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S05-COORDINATOR/page@91b87b78f7ed8a27f1d58e07fc868025.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15517074791576987099/session/-

## Tramp Metal Critic (Red Team) (S05-R-CRITIC)

*Mineral Processing/Plant — Electrical Superintendent*

**The ask.** Enforce auto-hold on uncrushable steel tooth detection in cavity. **What the agent does.** It looks up crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Operational Directive: Tramp Iron Eddy-Current Sensor Interlock Gate” It reports real figures — 0.00 tph, 1,145.57 tph, 1,153.23 tph — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Tramp Iron Eddy-Current Sensor Interlock Gate method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S05-R-CRITIC/page@98411fddda44b0bfe86540c229422932.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1150542196225760960/session/-

## SAG Mill Load Specialist (S06-1-SAG)

*Mineral Processing/Plant — Mill Operator*

**The ask.** Analyze 1/3-octave acoustic sensor array on SAG mill shell. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Executive Summary & Specialist” It reports real figures — 1.0, 8.0, 14.501 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Acoustic Toe Angle & Ball Charge Trajectory method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S06-1-SAG/page@f199ce2dc812435aaee81286ddad5f45.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17267471152570781932/session/-

## Ball Mill Power Specialist (S06-2-BALL)

*Mineral Processing/Plant — Grinding Technician*

**The ask.** Calculate daily grinding media ball charge replenishment for 3,800 tph. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Telemetry & Baseline” It reports real figures — 3,800.0 tph, 91,200.0, 1,153.25 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Austin Population Balance Grinding Kinetics method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S06-2-BALL/page@e7a28a08e243ca88d212613afe916528.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13921225072596694266/session/-

## Hydrocyclone Split Specialist (S06-3-CYCLONE)

*Mineral Processing/Plant — Slurry Specialist*

**The ask.** Model cut size d50c on 12-cyclone cluster operating at 110 kPa. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Hydrocyclone Split Specialist” It reports real figures — 0.71, 0.38, 0.45 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S06-3-CYCLONE/page@db766dae3e20d54b9bb1c069b48efcab.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7787327341957815195/session/-

## Grinding & Milling Coordinator (S06-COORDINATOR)

*Mineral Processing/Plant — Concentrator Superintendent*

**The ask.** SAG Mill #2 power spikes to 14.8 MW, toe acoustic noise dampened. **What the agent does.** It looks up plant telemetry and the asset register — the operation's live data, not a briefing pack — and answers in its own words: “Grinding & Milling Coordination Log Agent:” It reports real figures — 0.295, 14.8, 3.09 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S06-COORDINATOR/page@513da6e59e3179aabf04e3c5363203fd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16231628556639519542/session/-

## Slurry Density Critic (Red Team) (S06-R-CRITIC)

*Mineral Processing/Plant — Process Chemist*

**The ask.** Check cyclone feed density and trunnion bearing lubrication. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Operational Review: Cyclone Feed Density & Trunnion Bearing” It reports real figures — 12.50, 5.60, 4.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S06-R-CRITIC/page@d0e37b97f6c22011dae6b16c499155f7.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13013800279746514045/session/-

## Collector Dosing Specialist (S07-1-REAGENT)

*Mineral Processing/Plant — Flotation Technician*

**The ask.** Calculate frother MIBC addition rate for 1.4 cm/s air velocity. **What the agent does.** It looks up reagent stock levels — the operation's live data, not a briefing pack — and answers in its own words: “Reagent Inventory Verification & Operational” It reports real figures — 75.00, 21 days, 1.4 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S07-1-REAGENT/page@04ceb4e495a79aa83c07d4348713c11e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12936409017092172708/session/-

## Froth Air Specialist (S07-2-AIR)

*Mineral Processing/Plant — Plant Metallurgist*

**The ask.** Regulate superficial gas velocity Jg across rougher bank. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Governing Method & Hydrodynamic” It reports real figures — 1,153.25 tph, 1,000.56, 1,299.86 tph — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S07-2-AIR/page@d00e951d6f551556e45f00446ca90080.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13003249075149879793/session/-

## Concentrate Grade Specialist (S07-3-GRADE)

*Mineral Processing/Plant — Smelter Marketing Liaison*

**The ask.** Model cleaner bank separation efficiency for 28% Cu concentrate. **What the agent does.** It looks up flotation assay results — the operation's live data, not a briefing pack — and answers in its own words: “For a 28.00% Cu concentrate in the cleaner bank flotation” It reports real figures — 28.00%, 89.66%, 1.093% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S07-3-GRADE/page@079d1e27603dd80da1900f5aa0e4641c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3383821664191445726/session/-

## Flotation Recovery Coordinator (S07-COORDINATOR)

*Mineral Processing/Plant — Marcus (Chief Metallurgist)*

**The ask.** Optimize PAX collector dosing for 0.72% Cu ore to maximize recovery. **What the agent does.** It looks up flotation assay results and plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational Reconciliation of Feed Grade &” It reports real figures — 0.72%, 0.81%, 1.42% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S07-COORDINATOR/page@357fe133e3f83e9a32a4662a14d6c1b8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4100790245321040707/session/-

## Smelter Penalty Critic (Red Team) (S07-R-CRITIC)

*Mineral Processing/Plant — Commercial Metallurgist*

**The ask.** Check concentrate arsenic and bismuth penalty thresholds. **What the agent does.** It looks up flotation assay results — the operation's live data, not a briefing pack — and answers in its own words: “Audit Review: Concentrate Arsenic & Bismuth Penalty” It reports real figures — 27.41%, 24.99%, 30.16% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S07-R-CRITIC/page@29b8387bd87233a448894838e577957a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2422340200045156267/session/-

## Decant Water Return Specialist (S08-1-WATER)

*Mineral Processing/Plant — Water Treatment Operator*

**The ask.** Balance decant return water and evaporation pond volume. **What the agent does.** It looks up water balance logs — the operation's live data, not a briefing pack — and answers in its own words: “Decant Water & Evaporation Pond Water Balance” It reports real figures — 183,156.10, 1,096.74, 100.00% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S08-1-WATER/page@1875f394a9efcb3928f3bbca231031ba.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7388494887499711666/session/-

## Piezometer Pressure Specialist (S08-2-PORE)

*Mineral Processing/Plant — Geotech Instrumentation Tech*

**The ask.** Model Terzaghi 1D consolidation under Dam 2 embankment. **What the agent does.** It looks up tailings dam sensor readings — the operation's live data, not a briefing pack — and answers in its own words: “Terzaghi 1D Consolidation Model for Dam” It reports real figures — 9.81, 1.0, 0.60 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S08-2-PORE/page@9e770346f27464593794d57607fbb0b3.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17689915318949018488/session/-

## Slurry Thickener Specialist (S08-3-THICK)

*Mineral Processing/Plant — Dewatering Technician*

**The ask.** Regulate flocculant dosing for 65% solids underflow. **What the agent does.** It looks up plant telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Slurry Thickener Specialist Report: Flocculant Dosing & Underflow Density” It reports real figures — 1,153.25, 1,000.56, 1,299.86 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Kynch Sedimentation Solids Flux Theory method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S08-3-THICK/page@121fa0ce91cfa410229293dc0b0989ce.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2504307796515544315/session/-

## Tailings (TSF) Coordinator (S08-COORDINATOR)

*Mineral Processing/Plant — TSF Manager (Engineer of Record)*

**The ask.** Dam 2 piezometer reports pore pressure rise of 0.38m/week after rain. **What the agent does.** It looks up tailings dam sensor readings and water balance logs — the operation's live data, not a briefing pack — and answers in its own words: “TSF Technical Evaluation & GISTM Dam Conformance” It reports real figures — 0.38, 3.73, 9.81 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its GISTM Dam Conformance & Phreatic Surface Line method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S08-COORDINATOR/page@84f268273a0492af1bff9ad678cba3c2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5704906778757729715/session/-

## TSF Liquefaction Critic (Red Team) (S08-R-CRITIC)

*Mineral Processing/Plant — Statutory Geotechnical Reviewer*

**The ask.** Audit GISTM compliance and critical state soil mechanics. **What the agent does.** It looks up tailings dam sensor readings and safety permits records — the operation's live data, not a briefing pack — and answers in its own words: “Adversarial Geotechnical Audit: GISTM Compliance & Static Liquefaction” It reports real figures — 18.0%, 1.50, 1.135 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Critical State Soil Mechanics & Static Liquefaction Index method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S08-R-CRITIC/page@7abacb8c9b699910c44fec0934a3bde2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5536394081075780335/session/-

## Vibration FFT Specialist (S09-1-VIBRATION)

*Asset Integrity/Maintenance — Vibration Analyst (Category III)*

**The ask.** Parse 10-1000Hz vibration spectrum for bearing defect harmonics. **What the agent does.** It looks up the asset register and crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “1. Governing Method & Analysis” It reports real figures — 116.8532, 23.1189, 0.02 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its ISO 10816-3 RMS Velocity & BPFI Harmonics method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S09-1-VIBRATION/page@8b3bd2504000791f37a1ebbd6d597ccd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1209525171906486472/session/-

## Oil Tribology Specialist (S09-2-TRIBOLOGY)

*Asset Integrity/Maintenance — Lubrication Technician*

**The ask.** Evaluate Karl Fischer moisture and PQ particle quantifier index. **What the agent does.** It looks up the asset register and oil sample analyses — the operation's live data, not a briefing pack — and answers in its own words: “Tribological Evaluation: Karl Fischer Moisture & Particle Quantifier (PQ)” It reports real figures — 0.0, 0.0000%, 705.41 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its PQ Index & Karl Fischer Moisture PPM method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S09-2-TRIBOLOGY/page@ef78a8a849e1cd2ebc7e5fb2f5a6c752.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6541943629968723451/session/-

## Thermal IR Specialist (S09-3-THERMAL)

*Asset Integrity/Maintenance — Thermographer*

**The ask.** Analyze thermal gradient across pinion bearing housing. **What the agent does.** It looks up the asset register and crusher telemetry — the operation's live data, not a briefing pack — and answers in its own words: “Thermal IR Assessment: Pinion Bearing Housing Thermal Gradient & Temperature” It reports real figures — 74.0, 4,205.0, 3,905.96 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S09-3-THERMAL/page@971bd19431ff803203abdeace2559910.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12266523653873596783/session/-

## Asset Reliability Swarm Coordinator (S09-COORDINATOR)

*Asset Integrity/Maintenance — Priya (Reliability Superintendent)*

**The ask.** SAG Mill pinion bearing vibration reaches 4.8 mm/s RMS at 1480 RPM. **What the agent does.** It looks up the asset register, crusher telemetry and open work orders — the operation's live data, not a briefing pack — and answers in its own words: “Asset Reliability Swarm Coordinator” It reports real figures — 14.8, 4.25, 4.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S09-COORDINATOR/page@3f4b4cc3623076a24998ed20d18ae3f1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/523079695801690856/session/-

## Maintenance Safety Critic (Red Team) (S09-R-CRITIC)

*Asset Integrity/Maintenance — Safety Supervisor*

**The ask.** Enforce Dual-Key HMAC MFA prior to staging SAP PM work pack. **What the agent does.** It looks up the asset register and open work orders — the operation's live data, not a briefing pack — and answers in its own words: “Safety Gate Audit & Enforcement” **Why you can trust it.** Before answering it runs its LOTO Isolation Integrity & Failure Window Safety Gate method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S09-R-CRITIC/page@e3c25c17881294e8bb32c71f9ab64eb7.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3018210570239869511/session/-

## Contract Rate Auditor (S10-1-CONTRACT)

*Supply Chain/Logistics — Procurement Analyst*

**The ask.** Fuzzy-match line items against signed Master Service Agreement. **What the agent does.** It looks up supplier contracts — the operation's live data, not a briefing pack — and answers in its own words: “Contract Rate Audit: Fuzzy-Match Line Items vs. Signed Master Service Agreements” It reports real figures — 1,149.35, 390.23, 1,116.43 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Levenshtein Distance & Unit Price Deviation method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S10-1-CONTRACT/page@72f338ab547dd17ad051eae32681385d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4380926452236138549/session/-

## PPI Indexation Auditor (S10-2-ESCALATE)

*Supply Chain/Logistics — Commercial Specialist*

**The ask.** Compute labor and diesel escalation delta against PPI indices. **What the agent does.** It looks up supplier contracts — the operation's live data, not a briefing pack — and answers in its own words: “PPI Indexation & Escalation” It reports real figures — 1.0, 1,149.35, 0.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S10-2-ESCALATE/page@bf6f37291570daf56c224e861a0c6d76.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15145174503599723797/session/-

## Warranty Recovery Specialist (S10-3-WARRANTY)

*Supply Chain/Logistics — Asset Accountant*

**The ask.** Audit SAG liner premature failure against 8,000-hour MTBF warranty. **What the agent does.** It looks up the asset register and supplier contracts — the operation's live data, not a briefing pack — and answers in its own words: “Executive Summary & Audit” It reports real figures — 8,000 hours, 14.8, 452.0 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its MTBF vs Warranty Period Recovery Claimer method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S10-3-WARRANTY/page@17b82dc0017fae45c0e3ace352ca962a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10236263633444215320/session/-

## Procurement Coordinator (S10-COORDINATOR)

*Supply Chain/Logistics — Sarah (Supply Chain Superintendent)*

**The ask.** Audit contractor haulage invoice #INV-8839 against signed MSA rate card. **What the agent does.** It looks up supplier contracts and invoices — the operation's live data, not a briefing pack — and answers in its own words: “Internal Entity: Procurement Coordinator” **Why you can trust it.** Before answering it runs its Invoice Contract Matching & Rate Card Variance method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S10-COORDINATOR/page@a8ca181f542b35b516a0923e4be645fe.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5402454714704667630/session/-

## Anti-Bribery Audit Critic (Red Team) (S10-R-CRITIC)

*Supply Chain/Logistics — Internal Auditor*

**The ask.** Enforce FCPA compliance gate on sole-source supplier requisitions. **What the agent does.** It looks up supplier contracts and invoices — the operation's live data, not a briefing pack — and answers in its own words: “FCPA & Anti-Bribery Compliance Audit Report: Sole-Source Supplier Requisition Gate” It reports real figures — 802,443.52, 129,258.90, 57,662.34 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Vendor Beneficial Ownership & Single-Source Flags method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S10-R-CRITIC/page@020e98ac12494a421b4ea528373d112f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6963659721239708994/session/-

## Safety Stock Optimizer (S11-1-STOCK)

*Supply Chain/Logistics — Inventory Planner*

**The ask.** Calculate safety stock buffer for high-criticality bearings. **What the agent does.** It looks up spare parts stock — the operation's live data, not a briefing pack — and answers in its own words: “Dynamic Safety Stock Optimization: High-Criticality” It reports real figures — 14 days, 1,250.00, 0.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S11-1-STOCK/page@3b965bd8a823d77f9c94fcdfd0911e10.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8952188845126189763/session/-

## Vendor Lead Time Specialist (S11-2-LEADTIME)

*Supply Chain/Logistics — Supply Expediter*

**The ask.** Model Gamma distribution supplier lead-time variability. **What the agent does.** It looks up purchase-order history — the operation's live data, not a briefing pack — and answers in its own words: “Gamma Distribution Supplier Lead-Time” It reports real figures — 13.94, 14.46, 7.34 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Gamma Distribution Lead Time Modeling method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S11-2-LEADTIME/page@6e9fc9e33cedc9579f517726878ca4d1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9319212464069988816/session/-

## Carrying Cost Analyzer (S11-3-HOLDING)

*Supply Chain/Logistics — Cost Controller*

**The ask.** Analyze working capital carrying cost on $45M MRO warehouse. **What the agent does.** It looks up spare parts stock — the operation's live data, not a briefing pack — and answers in its own words: “Carrying cost is analyzed using the standard holding cost” It reports real figures — 45,000,000.00, 55,879,117.67, 10,879,117.67 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S11-3-HOLDING/page@66e7ec03ebb75e6b29e261977b555ee2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3626231911448469840/session/-

## Spares Inventory Coordinator (S11-COORDINATOR)

*Supply Chain/Logistics — Warehouse Superintendent*

**The ask.** Hydraulic cylinder stock is 0 with 8-week supplier lead time. **What the agent does.** It looks up spare parts stock and purchase-order history — the operation's live data, not a briefing pack — and answers in its own words: “Operational Reconciliation & Inventory” It reports real figures — 14 days, 7 days, 450.00 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S11-COORDINATOR/page@89f6e5164009a0cd7c1c23ecbd6a78b1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2773276585102532221/session/-

## Dead Stock Critic (Red Team) (S11-R-CRITIC)

*Supply Chain/Logistics — Finance Auditor*

**The ask.** Flag non-moving spares (>365 days) for inventory buyback. **What the agent does.** It looks up spare parts stock — the operation's live data, not a briefing pack — and answers in its own words: “Executive Summary & Inventory” It reports real figures — 55,879,117.67, 2,880.00, 55,876,237.67 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S11-R-CRITIC/page@cd7427b159537723fc7d528ac993b8bc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14327129105282995811/session/-

## Train Cycle Dispatch Specialist (S12-1-RAIL)

*Supply Chain/Logistics — Rail Controller*

**The ask.** Optimize train rake cycle time across 400km heavy-haul rail corridor. **What the agent does.** It looks up rail schedules — the operation's live data, not a briefing pack — and answers in its own words: “Executive Summary & Operational” It reports real figures — 2,149,409.5, 1,047,854.0 t, 1,101,555.5 t — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its Railway Headway & Velocity Optimization method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S12-1-RAIL/page@f4013a97398addf0a7506d2f77066b4c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17163419417666421589/session/-

## Port Stockpile Blend Specialist (S12-2-BLEND)

*Supply Chain/Logistics — Port Metallurgist*

**The ask.** Formulate LP blend model for 28.0% Cu export specification. **What the agent does.** It looks up stockpile records — the operation's live data, not a briefing pack — and answers in its own words: “1. Operational & Data” It reports real figures — 28.0%, 2,985,121.80, 0.4728% — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S12-2-BLEND/page@c60902bdf85c702604da4e387ec0fe20.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17572349194673256958/session/-

## Marine Laytime & Demurrage Specialist (S12-3-BERTH)

*Supply Chain/Logistics — Marine Broker*

**The ask.** Compute BIMCO laytime Statement of Fact deductions. **What the agent does.** It looks up vessel movements at the port — the operation's live data, not a briefing pack — and answers in its own words: “BIMCO Statement of Fact (SOF) Laytime & Demurrage Liability” It reports real figures — 2,391,744.70 t, 1,305,149.50 t, 1,086,595.20 t — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its BIMCO Laytime Pro-Rata & Demurrage Liability method, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S12-3-BERTH/page@883c977584e76b59bf90e7e310ccce52.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17205870215175020849/session/-

## Supply Chain & Port Coordinator (S12-COORDINATOR)

*Supply Chain/Logistics — Logistics Manager*

**The ask.** Vessel 'MV Cape Osprey' arrives in 48h for 160,000t loading. **What the agent does.** It looks up rail schedules, vessel movements at the port and stockpile records — the operation's live data, not a briefing pack — and answers in its own words: “Operational Assessment & Execution Plan: MV Cape Osprey (160,000” It reports real figures — 59,793.6, 100,619.2, 24,431.6 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S12-COORDINATOR/page@2c27ca5ea3461d820a218c2635bbc6f8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15457650955703083468/session/-

## Moisture & TML Critic (Red Team) (S12-R-CRITIC)

*Supply Chain/Logistics — Cargo Surveyor*

**The ask.** Enforce IMSBC Transportable Moisture Limit (TML < 9.2%). **What the agent does.** It looks up vessel movements at the port and stockpile records — the operation's live data, not a briefing pack — and answers in its own words: “IMSBC Transportable Moisture Limit (TML) Interlock” It reports real figures — 9.20%, 17.5%, 358,693.10 — pulled from the data during the recording. **Why you can trust it.** Before answering it runs its governing calculation, checks any numbers given in the question against what the records actually say, points out any difference, and names the records behind every figure. If it cannot back something with data, it says so instead of guessing.

- **Recording:** `data/uat/videos/S12-R-CRITIC/page@220cba1c1a025e4a4c655807f14f00d6.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15122170761949992179/session/-
