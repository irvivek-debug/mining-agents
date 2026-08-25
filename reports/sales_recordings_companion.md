# Agent Recordings — Sales Companion

One entry per agent. Each recording opens on the operational question,
shows the agent reading BigQuery live (the tool trace), then scrolls
the answer at reading pace. Note for live demos: agents answer in
seconds via the API but typically 2–4 minutes through the chat UI —
the on-screen tool trace is the proof of grounding; narrate over it.

## Strategic Planning Advisor (AGT-19)

*Commercial/Finance/Strategy — CEO / CFO / Executive Committee*

**Input.** Pit 4 copper price projection drops 15% from $4.20/lb to $3.57/lb. With mining cost $3.10/t, milling cost $14.50/t, and 89.5% recovery, calculate dynamic Kenneth Lane cut-off grade sensitivity. **Output.** The agent answers from live data — opening: “Strategic Planning Advisor (AGT-19) — Memorandum To: Strategic Planning & Mine Optimization Committee From: Strategic Planning Advisor (AGT-19) Subject: Dynamic Kenneth Lane Cut-Off Grade Sensitivity Analysis — Pit 4…” — key figures 4.20, 9,259.42, 9,114.60. **Logic.** It reads `geological_block_models`, `financial_ledger`, `mine_production_schedule` in BigQuery, applies max NPV = sum [(P-s)Qr - cQc - mQm - F]/(1+d)^t, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/AGT-19/page@5080d25b285face0a1fce5059dba2e58.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2639398376744540579/session/-

## Core Image Segmenter (D01)

*Exploration/Geology — Elena (Mine Geologist)*

**Input.** Calculate RQD on drill core tray #104 with lengths [12, 18, 8, 22, 14, 5, 25]cm on 120cm run. **Output.** The agent answers from live data — opening: “Core Image Segmentation & RQD Calculation Agent: Core Image Segmenter (d01) Governing Method: ResNet-UNet Rock Classifier (<12s/tray) 1. Operational Data Reconciliation & Sourcing Table Inspected:…” — key figures 75.83%, 86.67%. **Logic.** It reads `drill_holes` in BigQuery, applies ResNet-UNet Rock Classifier (<12s/tray), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D01/page@bc961b1c735927573c1e1c01da6a50b8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7961791724780686286/session/-

## Hyperspectral Mineral Mapper (D02)

*Exploration/Geology — Geochemist*

**Input.** Extract sericite vs illite crystallinity ratio from 2200nm SWIR spectral reflection. **Output.** The agent answers from live data — opening: “SWIR/VNIR Spectral Feature Extraction: Sericite vs. Illite Crystallinity Agent: Hyperspectral Mineral Mapper (d02) Governing Method: SWIR/VNIR Spectral Feature Extractor Dataset Scoped:…” — key figures 1.5, 2.0, 1.0. **Logic.** It reads `drill_holes`, `assay_logs` in BigQuery, applies SWIR/VNIR Spectral Feature Extractor, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D02/page@922bb7b5f647e55deb20acaf0fe2d32a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/905468479589496947/session/-

## JORC Classification Auditor (D03)

*Exploration/Geology — Competent Person*

**Input.** Audit drill spacing confidence for 25x25m vs 50x50m drill grids. **Output.** The agent answers from live data — opening: “JORC Classification Audit: Drill Spacing Confidence Analysis (25×25m vs. 50×50m Grid) Audit Role: JORC Classification Auditor (Agent d03) Governing Method: Spatial Drill Spacing Confidence Index (SDSCI) & Spherical…” — key figures 86.5%, 88.6%, 0.14. **Logic.** It reads `drill_holes`, `geological_block_models` in BigQuery, applies Spatial Drill Spacing Confidence Index, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D03/page@1f7b5e871afc45da0d77f07b45a2c045.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4649342689434985829/session/-

## Blast Wave Front Sim (D04)

*Mine Planning/Operations — D&B Specialist*

**Input.** Calculate CJ detonation pressure for emulsion with density 1.18 g/cm3 and VOD 5400 m/s. **Output.** The agent answers from live data — opening: “Governing Method: Chapman-Jouguet Detonation Hugoniot Solver 1. Database Reconciliation & Operational Assumptions Database Audited: genial-union-475913-i7.mining_data.blast_designs Operational Evidence: The…” — key figures 0.797, 4.0, 7.5. **Logic.** It reads `blast_designs` in BigQuery, applies Chapman-Jouguet Detonation Hugoniot Solver, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D04/page@4faac4ee77e745975b0be085e8db63d1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17821761931664506582/session/-

## Flyrock Trajectory Predictor (D05)

*Mine Planning/Operations — Shotfirer*

**Input.** Compute maximum flyrock travel distance for 45 deg ejection angle at v0=42 m/s. **Output.** The agent answers from live data — opening: “Flyrock Trajectory Prediction 1. Governing Method & Formula The maximum horizontal travel distance $R$ for a ballistic projectile is given by the ballistic range equation: R= g v 0 2 ​ ⋅sin(2θ) ​ Where: $v_0$ = Initial…” — key figures 9.81, 9.80665, 4.01. **Logic.** It reads `blast_designs` in BigQuery, applies Ballistic Range: R = (v0^2 * sin(2*theta)) / g, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D05/page@a492725ae5317558788c85a2d058229d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12044950816072083474/session/-

## In-Situ Fragment Analyzer (D06)

*Mine Planning/Operations — D&B Engineer*

**Input.** Fit Rosin-Rammler muckpile curve for xc=120mm and uniformity index n=1.15. **Output.** The agent answers from live data — opening: “Method & Model Overview Governing Method: Split-Desktop High-Res Image Segmentation Model: Rosin-Rammler (Weibull) Size Distribution Model Input Parameters: Characteristic Size ($x_c$ / $x_0$): $120\text{ mm}$…” — key figures 1.15, 5.5056, 16.96. **Logic.** It reads `blast_designs` in BigQuery, applies Split-Desktop High-Res Image Segmentation, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D06/page@94f5efbce29f0f655a021d7d1d1be0fc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17733897435877732313/session/-

## Radar Slope Displacement (D07)

*Mine Planning/Operations — Geotech Engineer*

**Input.** Calculate Fukuzono inverse velocity failure time for 14 mm/day bench creep. **Output.** The agent answers from live data — opening: “Operational Baseline & Assumption Reconciliation Reconciling the question's assumed bench creep rate against genial-union-475913-i7.mining_data.geotech_sensors: Parameter User-Supplied Assumption Operational Data…” — key figures 14.000, 9.794, 0.1. **Logic.** It reads `geotech_sensors` in BigQuery, applies InSAR Phase Shift Velocity Gradient Delta_phi, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D07/page@77d809a5eeff8634329106ccf8a4092c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5771882020233678970/session/-

## Borehole Seismicity Sentinel (D08)

*Mine Planning/Operations — Microseismic Technician*

**Input.** Compute microseismic b-value for 120 seismic events on North Pit fault. **Output.** The agent answers from live data — opening: “Operational & Data Reconciliation Assessment Agent: Borehole Seismicity Sentinel (d08) Governing Method: Gutenberg-Richter Magnitude-Frequency Law: log 10 ​ (N)=a−b⋅M (where $N$ is the cumulative number of events with…” — key figures 2.400, 6.341, 35.1. **Logic.** It reads `geotech_sensors` in BigQuery, applies Gutenberg-Richter Law: log(N) = a - b*M, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D08/page@ac4c23afe7ccc4afefdce6b77530df1a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16222986639730781285/session/-

## Bench Drainage Permeability (D09)

*Mine Planning/Operations — Hydrogeologist*

**Input.** Calculate discharge rate for 12 horizontal drain holes with k=1e-5 m/s. **Output.** The agent answers from live data — opening: “Governing Equation Discharge rate is governed by Darcy's Law: Q=−k⋅A⋅ dl dh ​ =k⋅A⋅i Where: $Q$ = Volumetric discharge rate ($\text{m}^3/\text{s}$) $k$ = Hydraulic conductivity / permeability coefficient ($1 \times…” — key figures 2.05, 2.98, 1.2. **Logic.** It reads `pit_designs` in BigQuery, applies Darcy's Law: Q = -k * A * (dh / dl), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D09/page@8f863410087a58b197ad1bd263a1b02d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1371995073496644570/session/-

## Haul Road Rolling Resist (D10)

*Fleet/Haulage — Civil Road Superintendent*

**Input.** Calculate rimpull requirement for CAT 797F (550t GMW) on 8% ramp with 3% rolling resistance. **Output.** The agent answers from live data — opening: “Reconciliation of Assumptions against Operational Data A review of genial-union-475913-i7.mining_data.fleet_telemetry reveals the following operational context: Truck Model & Capacity: Telemetry logs exist for Cat 797F…” — key figures 240.0 t, 205.02 t, 130.63 t. **Logic.** It reads `fleet_telemetry` in BigQuery, applies Rolling Resistance: RR = W * (C_rr + sin(theta)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D10/page@7325678bae041c230b5a00f6bed60832.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10833388638952133340/session/-

## Fleet Fuel Burn Sentinel (D11)

*Fleet/Haulage — Energy Manager*

**Input.** Calculate diesel consumption intensity (L/t-km) for 4.2km haul cycle. **Output.** The agent answers from live data — opening: “Telemetry & Governing Methodology Governing Formulation: SFC= P engine ​ m ˙ f ​ ​ Diesel Intensity (L/t-km)= Payload (t)×Haul Distance (km) Total Fuel Consumed (L) ​ 1. Assumption Reconciliation Supplied Haul Distance:…” — key figures 4.2, 0.534, 533.75. **Logic.** It reads `fleet_telemetry` in BigQuery, applies Specific Fuel Consumption: SFC = m_dot_f / P_engine, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D11/page@ca2b9b6ce68dc22e71a5a06daf08dccb.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13101384251525449016/session/-

## Tire TKPH Telemetry Agent (D12)

*Fleet/Haulage — Mobile Fleet Maintenance Lead*

**Input.** Calculate tire TKPH for 238t payload at 24 km/h average cycle speed. **Output.** The agent answers from live data — opening: “Agent Identity & Governing Method Agent: d12 (Tire TKPH Telemetry Agent) Governing Equation: TKPH=Q avg ​ ×V avg ​ ≤Rating (where $Q_{\text{avg}}$ is the average load and $V_{\text{avg}}$ is the average cycle speed) 1.…” — key figures 238.00 t, 205.02 t, 130.63 t. **Logic.** It reads `fleet_telemetry` in BigQuery, applies TKPH = Q_avg * V_avg <= Rating, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D12/page@927480fa3c780e947356a2fb6fd73848.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9758962924959748081/session/-

## Shovel GET Tooth Sentinel (D13)

*Fleet/Haulage — Shovel Operator*

**Input.** Scan Shovel #04 dipper bucket camera feed for missing ground engaging tool tooth. **Output.** The agent answers from live data — opening: “Shovel GET Tooth Sentinel (Agent d13) — Inspection Report Governing Method: YOLOv8 Ground Engaging Tool Watcher Primary Telemetry Reference: genial-union-475913-i7.mining_data.fleet_telemetry Asset Registry Reference:…” — key figures 116.8311, 23.1686, 42.0. **Logic.** It reads `fleet_telemetry` in BigQuery, applies YOLOv8 Ground Engaging Tool Watcher, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D13/page@310e2bf79f42e9a821b34622ea581ce5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6134679660633629158/session/-

## Autogenous Grinding Sound (D14)

*Mineral Processing/Plant — Mill Operator*

**Input.** Analyze SAG mill acoustic FFT power spectrum at 1200-2400 Hz. **Output.** The agent answers from live data — opening: “Acoustic Power Spectrum 1/3-Octave Band Analysis (1200–2400 Hz) Governing Method: Acoustic Power Spectrum 1/3-Octave Band Fast Fourier Transform (FFT) Agent ID: d14 (Autogenous Grinding Sound) Target Unit: SAG Grinding…” — key figures 14.50, 14.80, 13.41. **Logic.** It reads `plant_telemetry` in BigQuery, applies Acoustic Power Spectrum 1/3 Octave Band FFT, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D14/page@0408826dcdbbf5e8df56e38cb94e1aaf.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17829819385329910239/session/-

## Trommel Screen Blinding (D15)

*Mineral Processing/Plant — Concentrator Technician*

**Input.** Calculate aperture blinding percentage on SAG discharge trommel. **Output.** The agent answers from live data — opening: “Role & Governing Method Agent: Trommel Screen Blinding (d15) Domain: Quantifies screen mesh aperture blinding and near-size pegging on Semi-Autogenous Grinding (SAG) discharge trommels. Governing Method: Aperture…” — key figures 13.41, 15.63, 14.50. **Logic.** It reads `plant_telemetry` in BigQuery, applies Aperture Occlusion Optical Flow Percentage, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D15/page@673f7f9dff737f598ca3a203197d0d54.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6344681735013446444/session/-

## Slurry Pump Cavitation (D16)

*Mineral Processing/Plant — Fixed Plant Fitter*

**Input.** Calculate available Net Positive Suction Head for slurry pump #3 at 65% solids. **Output.** The agent answers from live data — opening: “1. Data Reconciliation & Telemetry Grounding A query was executed against genial-union-475913-i7.mining_data.plant_telemetry and related operational tables to reconcile the parameters for Slurry Pump 3 (PUMP-03): Slurry…” — key figures 71.42, 65.01, 89.68. **Logic.** It reads `plant_telemetry` in BigQuery, applies Net Positive Suction Head: NPSHa > NPSHr, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D16/page@fc4a46d2b9576917ab9ba940d2dccae5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3255539541494084213/session/-

## Sump Level Anti-Surge (D17)

*Mineral Processing/Plant — Process Control Specialist*

**Input.** Regulate sump level PID speed for 3,800 tph feed slurry surge. **Output.** The agent answers from live data — opening: “Agent Identification Agent Name / System Role: Sump Level Anti-Surge (d17) Governing Method: Dynamic Mass Balance Continuity: A⋅ dt dh ​ =Q in ​ −Q out ​ 1. Reconciliation of Assumptions Against plant_telemetry…” — key figures 3,800.0, 1,210.0, 214.0%. **Logic.** It reads `plant_telemetry` in BigQuery, applies Mass Balance Continuity: A * (dh/dt) = Q_in - Q_out, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D17/page@6221cbec4e802124a0248b8c0ef2f2ed.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7025307563315550538/session/-

## Froth Bubble Sizing/Color (D18)

*Mineral Processing/Plant — Flotation Technician*

**Input.** Measure Sauter mean bubble diameter d32 on rougher flotation cell #4. **Output.** The agent answers from live data — opening: “1. Asset Identification & Operating Parameters From genial-union-475913-i7.mining_data.assets: Asset ID: FLOTATIO-04 Asset Name: Outotec TankCell e300 04 (Rougher Flotation Cell 4) Asset Type: FLOTATION_CELL Operating…” — key figures 7.65, 135.4, 0.0092. **Logic.** It reads `flotation_assays`, `plant_telemetry` in BigQuery, applies Sauter Mean Bubble Diameter d32 & RGB Grade Proxy, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D18/page@50dacec5ab694a930eda12352599b641.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17273012408267433389/session/-

## Xanthate Degradation (D19)

*Mineral Processing/Plant — Reagent Chemist*

**Input.** Calculate potassium amyl xanthate (PAX) potency after 72 hours storage at 32 deg C. **Output.** The agent answers from live data — opening: “Operational Grounding & Reagent Reconciliation Per the operational inventory records in table genial-union-475913-i7.mining_data.reagent_inventory: Field Value Source Table Reagent Description Potassium Amyl Xanthate…” — key figures 7 days, 57.54, 8.314. **Logic.** It reads `reagent_inventory` in BigQuery, applies 1st-Order Hydrolysis Kinetics: C(t) = C_0 * exp(-k*t), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D19/page@a6f66e2bbce8d6bc6b6d945d6fffbaae.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2463177645997507271/session/-

## Acid Mine Drainage ORP (D20)

*Mineral Processing/Plant — Environmental Superintendent*

**Input.** Calculate hydrated lime Ca(OH)2 dosage to neutralize pit sump pH from 3.2 to 7.5. **Output.** The agent answers from live data — opening: “Hydrated Lime $\text{Ca(OH)}_2$ Neutralization & Electrochemical Analysis 1. Executive Summary of Lime Dosage To neutralize free acid in pit sump water from $\text{pH } 3.2$ to $\text{pH } 7.5$: Theoretical Free Acidity…” — key figures 3.2, 7.5, 23.39. **Logic.** It reads `water_balance_logs` in BigQuery, applies Nernst Equation: E_h = E0 - (RT/nF) * ln(Q), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D20/page@4529ddfdd70f49fb576741bb686becb3.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1126839582103419021/session/-

## Tailings Beach Slope (D21)

*Mineral Processing/Plant — TSF Engineer*

**Input.** Predict beach slope angle for thickened tailings with yield stress 65 Pa. **Output.** The agent answers from live data — opening: “1. Governing Deposition Model Under the Non-Newtonian Yield Stress Subaerial Deposition Model, the equilibrium beach slope angle ($\theta$) is governed by the balance between the shear stress at the base of the…” — key figures 0.10, 0.05, 0.15. **Logic.** It reads `tsf_piezometers` in BigQuery, applies Non-Newtonian Yield Stress: tau_y = rho * g * h * sin(theta), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D21/page@15ef490f0fc88e1a45763eaee8e12a96.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5611152752644422239/session/-

## Transformer Dissolved Gas (D22)

*Asset Integrity/Maintenance — HV Electrician*

**Input.** Plot Duval Triangle 1 coordinates for Main Substation transformer oil. **Output.** The agent answers from live data — opening: “Transformer Dissolved Gas Analysis (DGA) & Duval Triangle 1 Evaluation Agent ID: d22 Governing Standard: IEC 60599 (Mineral oil-filled electrical equipment in service – Guidance on the interpretation of dissolved and…” — key figures 8.38, 65.0, 116.8737. **Logic.** It reads `assets` in BigQuery, applies Duval Triangle & DGA Ratio (Acetylene / Hydrogen), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D22/page@3a9b80e403512e4eaa8e850f7a7d885f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17610690989667960583/session/-

## Motor Partial Discharge (D23)

*Asset Integrity/Maintenance — Electrical Engineer*

**Input.** Analyze stator winding partial discharge for 15 MW SAG mill synchronous motor. **Output.** The agent answers from live data — opening: “Agent Profile & Methodology Agent Identifier: d23 (Motor Partial Discharge) Governing Method: High-Frequency Transient Phase-Resolved Partial Discharge (PRPD) Pulse Counting (6.6 kV / 11 kV Stator Winding Dielectric…” — key figures 6.6, 4.25, 4.0. **Logic.** It reads `assets` in BigQuery, applies High-Frequency Transient Phase-Resolved PD, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D23/page@5789cb9621aef3e82d61d870f77c149b.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5183629188203019270/session/-

## Conveyor Belt Rip Ultra (D24)

*Asset Integrity/Maintenance — Belt Splicer Lead*

**Input.** Monitor ultrasonic sensor array on 4km overland coarse ore conveyor CV-01. **Output.** The agent answers from live data — opening: “Asset Identification & Assumption Reconciliation Asset Tag in Question: Coarse ore conveyor CV-01 (4 km overland). Database Asset Match: CONVEYOR-01 (asset_name: "Overland Conveyor 01"), documented in BigQuery table…” — key figures 116.8045, 23.1614, 5.24. **Logic.** It reads `assets` in BigQuery, applies Time-of-Flight Acoustic Wave Attenuation, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D24/page@296c4d239055473c21385c4168f00a46.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12470560680853903472/session/-

## Chute Wear Ultrasonic (D25)

*Asset Integrity/Maintenance — Boilermaker Lead*

**Input.** Measure remaining Hardox 500 liner thickness on Crusher discharge chute. **Output.** The agent answers from live data — opening: “Method & Governing Principles Governing Method: Ultrasonic Thickness Pulse-Echo Gauge: d= 2 v⋅t ​ Where: $d$ = Remaining liner plate thickness ($\text{mm}$) $v$ = Longitudinal acoustic velocity in Hardox 500 steel…” — key figures 5.90, 1210.0, 120.0. **Logic.** It reads `assets` in BigQuery, applies Ultrasonic Thickness Pulse-Echo Gauge: d = (v * t) / 2, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D25/page@17f26996381a1098d01933c320041da2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5181698511014105791/session/-

## Maintenance Work Backlog (D26)

*Asset Integrity/Maintenance — Tom (Maintenance Planner)*

**Input.** Calculate schedule float for SAG mill liner replacement critical path. **Output.** The agent answers from live data — opening: “Under the Critical Path Method (CPM) governing methodology, the schedule float (Total Float) for the critical path of the SAG mill liner replacement is 0 (zero). 1. CPM Schedule Float Principles Total Float Formula:…” — key figures 0 hours, 351.2 hours, 10.03 hours. **Logic.** It reads `erp_work_orders` in BigQuery, applies Critical Path Method (CPM) Schedule Float, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D26/page@c19658c4033771130340d779a966261d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/424629171197778528/session/-

## Contractor Idle Fee Audit (D27)

*Commercial/Finance/Strategy — Commercial Manager*

**Input.** Audit 48 hours standby claim for contractor dozer fleet against FMS GPS movement. **Output.** The agent answers from live data — opening: “Contractor Idle Fee Audit Report Agent: Contractor Idle Fee Audit (d27) Governing Method: Standby Hours vs Daily Rate Dispute Validator Audit Target: 48-Hour Standby Claim for Contractor Dozer Fleet vs. FMS GPS Movement…” — key figures 48 hours, 48.0, 0.00. **Logic.** It reads `vendor_contracts`, `fleet_telemetry` in BigQuery, applies Standby Hours vs Daily Rate Dispute Validator, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D27/page@763f50c431cf0e8485d2b933b5f5d49e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14871181550156206719/session/-

## Fuel Bunkering Density (D28)

*Commercial/Finance/Strategy — Fuel Logistics Officer*

**Input.** Calculate temperature-corrected diesel fuel volume for 120,000L bunkering at 34 deg C. **Output.** The agent answers from live data — opening: “1. Operational Data Reconciliation & Table Evidence Source Table Consulted: genial-union-475913-i7.mining_data.purchase_orders Findings: The purchase_orders dataset contains procurement records for heavy industrial…” — key figures 141.5, 131.5, 840.0. **Logic.** It reads `purchase_orders` in BigQuery, applies API Gravity: API = (141.5 / SG) - 131.5, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D28/page@2355850b717c308b608ac90f14a441a1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8219039806167601700/session/-

## Grinding Ball Wear Batch (D29)

*Asset Integrity/Maintenance — Plant Metallurgist*

**Input.** Calculate daily grinding ball consumption rate for Wi=14.2 kWh/t ore. **Output.** The agent answers from live data — opening: “1. Governing Method & Specific Wear Rate Calculation Under the Bond Wear Rate equation for forged steel grinding balls: M ball ​ =0.16×(W i ​ −7) 0.5 Using the user-supplied ore Work Index ($W_i = 14.2\text{ kWh/t}$): W…” — key figures 0.16, 0.5, 14.2. **Logic.** It reads `spares_inventory`, `plant_telemetry` in BigQuery, applies Bond Wear Rate: M_ball = 0.16 * (Wi - 7)^0.5, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D29/page@94d105ced7be12c62c612bea5f363959.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16177627500456872112/session/-

## Lube Oil Cleanliness (D30)

*Asset Integrity/Maintenance — Tribologist*

**Input.** Parse particle count data for SAG mill pinion lube oil reservoir. **Output.** The agent answers from live data — opening: “Asset Identification & Operational Context According to mining_data.assets: Asset ID: MILL-01 Asset Name: SAG Grinding Mill 1 Asset Type: GRINDING_MILL Criticality Rating: CRITICAL Current Operational State: Rotational…” — key figures 14.8, 452.0, 4.25. **Logic.** It reads `assets`, `lube_samples` in BigQuery, applies ISO 4406 Solid Contamination Cleanliness Code, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D30/page@387f4ba483fcad8aa7c5302c8e38b86a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3203587165096507461/session/-

## Consignment Stock Logger (D32)

*Supply Chain/Logistics — Warehouse Clerk*

**Input.** Reconcile warehouse RFID scan against SAP goods issue for 12 pump seals. **Output.** The agent answers from live data — opening: “Consignment Stock Logger Report Agent Identifier: d32 Governing Method: RFID Tag vs SAP Movement Type 201 Reconciler 1. Reconciliation & Data Grounding A comprehensive review of the active inventory was performed…” — key figures 450.00, 900.00, 7 days. **Logic.** It reads `spares_inventory` in BigQuery, applies RFID Tag vs SAP Movement Type 201 Reconciler, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D32/page@bdb55e96b96f04fa46d4cca65bbd7753.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4122039674810283352/session/-

## Laytime BIMCO Parser (D33)

*Supply Chain/Logistics — Logistics Officer*

**Input.** Parse port laytime statement for 'MV Bulk Pioneer' under rain interruptions. **Output.** The agent answers from live data — opening: “Port Laytime & Statement of Fact (SOF) Parsing Analysis Governing Method: BIMCO Laytime Standard Statement of Fact Parser Primary Data Source: genial-union-475913-i7.mining_data.port_vessels 1. Vessel Reconciliation &…” — key figures 75,542.0, 9.73%, 10.0%. **Logic.** It reads `port_vessels` in BigQuery, applies BIMCO Laytime Standard Statement of Fact Parser, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D33/page@188cb9202c100eb38104fd52e6302b34.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/583739645883463374/session/-

## Reagent Shelf Life (D34)

*Supply Chain/Logistics — Hazmat Technician*

**Input.** Model shelf life degradation of sodium isopropyl xanthate (SIPX) at 38 deg C. **Output.** The agent answers from live data — opening: “1. Inventory & Reagent Reconciliation A query of the active inventory table genial-union-475913-i7.mining_data.reagent_inventory shows the following stock of bulk xanthate collectors currently held: Part Number…” — key figures 57.54, 27.19, 28.03. **Logic.** It reads `reagent_inventory` in BigQuery, applies Arrhenius Reaction: k = A * exp(-E_a / RT), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D34/page@c6cc7b99140b4911662ddd684b2b796d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8228845743322555862/session/-

## Locomotive Brake Curve (D35)

*Supply Chain/Logistics — Rail Master*

**Input.** Calculate stopping distance for 12,000t loaded ore train at 60 km/h on 0.5% grade. **Output.** The agent answers from live data — opening: “1. Operational Data Reconciliation & Evidence Data cited from genial-union-475913-i7.mining_data.rail_schedules: Payload / Train Mass ($m = 12,000\text{ t}$): rail_schedules records 120 consist schedules with payloads…” — key figures 9,061.80, 25,920.40, 17,911.75. **Logic.** It reads `rail_schedules` in BigQuery, applies Braking Distance: d = v^2 / [2g*(mu +- theta)], reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D35/page@8fa8226b37634d0605174ffd7285365d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13394976667368344513/session/-

## Shiploader 3D LiDAR (D36)

*Supply Chain/Logistics — Shiploader Operator*

**Input.** Monitor shiploader boom LiDAR sensor distance from vessel hatch coaming. **Output.** The agent answers from live data — opening: “Shiploader 3D LiDAR Monitoring Report (Sentinel d36) Governing Operational Method: 3D LiDAR Collision Margin: Minimum clearance threshold $\text{Distance} > 5.0,\text{m}$ between the shiploader boom/chute assembly and…” — key figures 5.0, 100,619.2, 6.84%. **Logic.** It reads `port_vessels` in BigQuery, applies 3D LiDAR Collision Margin: Distance > 5.0m, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D36/page@be04413858a6dbe63585a327a57163ba.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17690808582680002326/session/-

## SAFTE Driver Fatigue (D37)

*Safety/OHSE/ESG — Jack (Mine Safety Lead)*

**Input.** Calculate SAFTE bio-mathematical fatigue score for operator on 4th night shift. **Output.** The agent answers from live data — opening: “Biomathematical Fatigue Evaluation: 4th Consecutive Night Shift Evaluation Model: Sleep, Activity, Fatigue, and Task Effectiveness (SAFTE) Governing Method: E(t)=S(t)+C(t)−P(t) Where: $E(t)$: Predicted Task…” — key figures 2.13 hours, 2.0, 4.2. **Logic.** It reads `fatigue_monitoring_logs` in BigQuery, applies SAFTE Score: E(t) = S(t) + C(t) - P(t), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D37/page@0057d550a617a67b0ebf9878f55ad80f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4130455342070868544/session/-

## Confined Space Gas (D38)

*Safety/OHSE/ESG — Industrial Hygienist*

**Input.** Evaluate multi-gas monitor telemetry inside SAG mill during liner inspection. **Output.** The agent answers from live data — opening: “Multi-Gas Monitor Telemetry Evaluation: SAG Mill Liner Inspection Agent ID: d38 Role: Confined Space Gas (Real-time multi-gas sentinel monitoring $O_2$, $\text{LEL}$, $H_2S$, and $CO$ atmospheric levels) 1. Governing…” — key figures 19.5%, 23.5%. **Logic.** It reads `safety_telemetry` in BigQuery, applies Gas Limits: LEL < 10%, O2 in [19.5, 23.5]%, H2S < 10ppm, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D38/page@a550512fe2097249680d7a9bfe082832.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10224314405726841486/session/-

## Carbon Scope 1/2 Tracker (D39)

*Safety/OHSE/ESG — Sustainability Lead*

**Input.** Calculate monthly carbon intensity per tonne of copper cathode produced. **Output.** The agent answers from live data — opening: “GHG Protocol Governing Methodology Under the GHG Protocol Corporate Accounting and Reporting Standard, total operational greenhouse gas emissions ($\text{CO}_2\text{e}$) comprise Scope 1 (direct emissions from diesel…” — key figures 206.44, 75,970.58, 28.33. **Logic.** It reads `fleet_telemetry`, `plant_telemetry` in BigQuery, applies GHG Protocol: CO2e = sum(Fuel * EF) + (Grid_MWh * EF), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D39/page@5b55e8c6ab0676e122f62e01563c7850.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9664629732570460254/session/-

## Statutory Permit Guardian (D40)

*Safety/OHSE/ESG — Legal Counsel & Compliance Officer*

**Input.** Audit statutory environmental water discharge permit expiry timelines. **Output.** The agent answers from live data — opening: “Statutory Permit & Tenement Lease Audit Report Auditor / Agent: Statutory Permit Guardian (d40) Governing Method: Regulatory Obligation NLP Entity Matcher & Tenement Lease Auditor Data Sources Audited:…” — key figures 2,482.00, 54,582.30, 1,014.10. **Logic.** It reads `tenement_leases`, `safety_permits` in BigQuery, applies Regulatory Obligation NLP Entity Matcher & Tenement Lease Auditor, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/D40/page@5173660c21353876c0c7008b76552bca.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12178037606655907260/session/-

## Drill Lithology Specialist (S01-1-LITHOLOGY)

*Exploration/Geology — Exploration Geologist*

**Input.** Classify drill core tray #482 rock quality and fracture frequency. **Output.** The agent answers from live data — opening: “Governing Methodology & Classification Framework As the Drill Lithology Specialist, rock quality and fracture frequency are evaluated according to standard geotechnical diamond core logging standards: Rock Quality…”. **Logic.** It reads `drill_holes` in BigQuery, applies RQD = (sum(pieces >= 10cm) / total_length) * 100, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S01-1-LITHOLOGY/page@11b4e7675eb6dc439206c239eafcf4a5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5332440710463027597/session/-

## Assay Geostatistics Specialist (S01-2-GEOSTAT)

*Exploration/Geology — Geostatistician*

**Input.** Compute estimation variance for copper block grades at Section 104N. **Output.** The agent answers from live data — opening: “Based on the spatial and geological data in the mining_data dataset, here is the geostatistical estimation variance analysis for copper block grades at Section 104N (Grid Northing $Y = 7,432,400\text{ mN}$, Block Model…” — key figures 1.0152%, 0.6140, 0.613979. **Logic.** It reads `assay_logs` in BigQuery, applies Z_hat(x0) = sum(lambda_i * Z(x_i)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S01-2-GEOSTAT/page@e63942d6ef63cef57fae9758969a2f5f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9087835982665536979/session/-

## Structural Fault Specialist (S01-3-STRUCTURAL)

*Exploration/Geology — Structural Geologist*

**Input.** Analyze strike and dip planes on Section 104N fault envelope. **Output.** The agent answers from live data — opening: “Structural Fault & Plane Orientation Analysis: Section 104N Fault Envelope Analyst Reference: s01_3_structural Data Source: genial-union-475913-i7.mining_data.geological_block_models Governing Method:…” — key figures 0.4468, 24.1, 0.168736. **Logic.** It reads `geological_block_models` in BigQuery, applies n = (sin(theta)*cos(phi), sin(theta)*sin(phi), cos(theta)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S01-3-STRUCTURAL/page@01922a5bb2ee6e222ba9a476db976969.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2645900857098460761/session/-

## Geology Swarm Coordinator (S01-COORDINATOR)

*Exploration/Geology — Elena (Chief Mine Geologist)*

**Input.** Synthesize Section 104N drillhole assays into Ordinary Kriging 3D block model. **Output.** The agent answers from live data — opening: “Geological Synthesis: Section 104N Drillhole Assays & Ordinary Kriging 3D Block Model Internal Reference: s01_coordinator Dataset Scope: BigQuery Project genial-union-475913-i7, Dataset mining_data Section Definition:…” — key figures 485,148.11, 7,432,325.23, 532.80. **Logic.** It reads `drill_holes`, `assay_logs`, `geological_block_models` in BigQuery, applies gamma(h) = 1/(2N(h)) * sum [Z(x_i) - Z(x_i+h)]^2, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S01-COORDINATOR/page@32e3f4291eddcd08090c1e66040de542.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2549813273247417527/session/-

## Resource Critic (JORC / QAQC Red Team) (S01-R-CRITIC)

*Exploration/Geology — Competent Person (CP / QP)*

**Input.** Audit duplicate core sample assay variance against JORC Code standards. **Output.** The agent answers from live data — opening: “JORC / QA/QC Red Team Audit: Duplicate Core Sample Assay Variance 1. Executive Audit Summary & Primary Finding An adversarial audit of the assay database was conducted against JORC Code (2012 Edition) Table 1 standards…” — key figures 0.00, 447.75, 0.0%. **Logic.** It reads `assay_logs`, `qaqc_standards` in BigQuery, applies JORC Resource Confidence Index & Blank Contamination Variance, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S01-R-CRITIC/page@a72f78ea535d5603f650f0812fb18c35.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13867639205775571505/session/-

## Pit Wall Geotechnical Specialist (S02-1-GEOTECH)

*Mine Planning/Operations — Geotechnical Engineer*

**Input.** Calculate Bishop simplified Factor of Safety on 48 deg pit wall. **Output.** The agent answers from live data — opening: “1. Operational Geotechnical Data Reconciliation From the operational monitoring database (genial-union-475913-i7.mining_data.geotech_sensors): Exact 48.0° Slope Sensor Record: Reading ID: GT-00151 (Sensor GEO-03, Bench:…” — key figures 48.0, 121.60, 2.886. **Logic.** It reads `geotech_sensors` in BigQuery, applies FoS = [c' + (sigma_n - u)*tan(phi')] / tau_m, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S02-1-GEOTECH/page@d12a673167d4b782b2700515fea032f5.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2467120801253827430/session/-

## Phase Scheduling Specialist (S02-2-SCHEDULE)

*Mine Planning/Operations — Long-Term Planning Engineer*

**Input.** Sequence shovel assignments to balance 1.8 Mt/month ore extraction. **Output.** The agent answers from live data — opening: “Shovel Assignment Sequencing & Extraction Optimization Role: Phase Scheduling Specialist Governing Method: Dynamic Programming / Bellman Value Iteration: V t ​ (S)= a∈A(S) max ​ [R(S,a)+γ⋅V t+1 ​ (S ′ )] where: $S =…” — key figures 0.084, 0.9933, 8.40%. **Logic.** It reads `mine_production_schedule` in BigQuery, applies V_t(S) = max_a [R(S, a) + gamma * V_{t+1}(S')], reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S02-2-SCHEDULE/page@15a1d4ea3edaf5209c1b8c1f6489b56e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14750280296794731530/session/-

## Waste Dump Stability Specialist (S02-3-DUMP)

*Mine Planning/Operations — Civil Mine Engineer*

**Input.** Model North Dump toe containment volume and runout angle of repose. **Output.** The agent answers from live data — opening: “Waste Dump Stability & Geotechnical Assessment: North Dump Modeling Specialist Role: Waste Dump Stability Specialist (s02_3_dump) Governing Method: Bishop’s Simplified Method of Slices FoS= ∑Wsinα ∑[c ′ b+(W−ub)tanϕ ′…” — key figures 51.25, 2.050, 2.01. **Logic.** It reads `pit_designs` in BigQuery, applies Bishop Method: FoS = sum([c'b + (W - ub)tan(phi')]*m_alpha) / sum(W*sin(alpha)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S02-3-DUMP/page@46010093d0ae366a64f91d3114300bec.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14198794820232846068/session/-

## Mine Planning Coordinator (S02-COORDINATOR)

*Mine Planning/Operations — Planning Superintendent*

**Input.** Optimize Phase 3 pushback extraction sequence with 48 deg overall slope. **Output.** The agent answers from live data — opening: “Technical Memorandum: Phase 3 Pushback Extraction Sequence Optimization To: Mine Operations & Technical Services From: Mine Planning Coordinator (s02_coordinator) Methodology: Lerchs-Grossmann Graph Max-Flow Formulation…” — key figures 48.0, 45.0, 9,323.40. **Logic.** It reads `mine_production_schedule`, `pit_designs` in BigQuery, applies Lerchs-Grossmann Graph Max-Flow: max sum(w_i * v_i), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S02-COORDINATOR/page@1360c1240b5d3eac6649588966057f78.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10031640407747179171/session/-

## Plan Compliance Critic (Red Team) (S02-R-CRITIC)

*Mine Planning/Operations — Senior Mine Surveyor*

**Input.** Audit spatial compliance between monthly extraction and long-term model. **Output.** The agent answers from live data — opening: “Spatial Compliance Audit: Monthly Extraction vs. Long-Term Model Audit Role: Plan Compliance Critic (Red Team / s02_r_critic) Governing Methodologies: $F_1$ Spatial Reconciliation: $F_1 = \frac{\text{Mined…” — key figures 0.0, 1.0056, 0.56%. **Logic.** It reads `survey_scans`, `mine_production_schedule` in BigQuery, applies F1 = Mined_Volume / Planned_Volume, F2 = Milled_Metal / Mined_Metal, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S02-R-CRITIC/page@2f7d327bfe828612964f36a202d819cc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6834062730278861341/session/-

## Blast Geometry Specialist (S03-1-GEOMETRY)

*Mine Planning/Operations — D&B Engineer*

**Input.** Design 180-hole staggered pattern for 15m production bench. **Output.** The agent answers from live data — opening: “1. Operational Context & Assumption Reconciliation Pattern Requirement: 180-hole staggered pattern on a 15 m production bench ($H = 15.0\text{ m}$). Data Source Verification (mining_data.blast_designs): Historical hole…” — key figures 15.0, 8.00, 16.00. **Logic.** It reads `blast_designs` in BigQuery, applies B = K_b * d_h * sqrt(rho_e / rho_r), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S03-1-GEOMETRY/page@1d43e0b754d0895a6fdbf05e049e3a81.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6899800456415450209/session/-

## Explosives Energy Specialist (S03-2-EXPLOSIVE)

*Mine Planning/Operations — Shotfirer Technical Lead*

**Input.** Calculate bulk emulsion VOD and shock energy partitioning. **Output.** The agent answers from live data — opening: “Explosives Energy & Detonation Analysis: Bulk Emulsion vs. ANFO 1. Governing Methodologies & Detonation Physics A. Powder Factor Formula The primary governing metric for rock breakage and charge distribution is: q= V…” — key figures 1.15, 1.25, 1.20. **Logic.** It reads `explosives_inventory` in BigQuery, applies q = M_exp / V_rock (kg/m3), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S03-2-EXPLOSIVE/page@e09d031c80be43f61c0b52f21c7ae6d6.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/385821222619278877/session/-

## Blast Vibration Sentinel (S03-3-VIBRATION)

*Mine Planning/Operations — D&B Engineer*

**Input.** Predict PPV vibration at primary crusher 450m from blast. **Output.** The agent answers from live data — opening: “1. Governing Attenuation Model Blast ground vibration is predicted using the scaled-distance attenuation equation: PPV=K⋅( W ​ D ​ ) −β Where: $\text{PPV}$: Peak Particle Velocity ($\text{mm/s}$) $D$: Distance from…” — key figures 5.60, 4.00, 17.11. **Logic.** It reads `blast_designs` in BigQuery, applies PPV = K * (D / sqrt(W))^(-beta), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S03-3-VIBRATION/page@b5d01b4e6fb08828cf2b3871a1220c88.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9816945852212110694/session/-

## Drill & Blast Coordinator (S03-COORDINATOR)

*Mine Planning/Operations — Drill & Blast Superintendent*

**Input.** Optimize burden and powder factor for hard granodiorite ($UCS=160 MPa$). **Output.** The agent answers from live data — opening: “Drill & Blast Optimization: Hard Granodiorite ($UCS = 160\text{ MPa}$) Agent Identity: s03_coordinator (Drill & Blast Coordinator) Governing Method: Kuz-Ram Fragmentation Model: x 50 ​ =A⋅Q 1/6 ⋅( E 115 ​ ) 0.63 ⋅( Q V…” — key figures 0.63, 0.8, 2.68. **Logic.** It reads `blast_designs`, `explosives_inventory` in BigQuery, applies Kuz-Ram: x50 = A * Q^(1/6) * (115/E)^0.63 * (V0/Q)^0.8, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S03-COORDINATOR/page@3c18176fa65bb3fea23611d35d655324.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6919052797483217132/session/-

## Blast Safety Critic (Red Team) (S03-R-CRITIC)

*Mine Planning/Operations — Statutory Shotfirer*

**Input.** Enforce 500m blast exclusion perimeter and lightning warning gate. **Output.** The agent answers from live data — opening: “Red Team Blast Safety Review & Statutory Gate Enforcement Governing Framework: Statutory Exclusion Zone Radius & Misfire Detection Gate Data Sources: genial-union-475913-i7.mining_data.blast_designs,…” — key figures 82.2%, 17.8%, 4.01. **Logic.** It reads `blast_designs`, `safety_permits` in BigQuery, applies Statutory Exclusion Zone Radius & Misfire Detection Gate, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S03-R-CRITIC/page@c66c61fbecc810d115455effd308f304.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3034965665875988605/session/-

## Shovel Match Specialist (S04-1-SHOVEL)

*Fleet/Haulage — Dispatch Controller*

**Input.** Calculate pass match factor for PC8000 shovel loading CAT 797F. **Output.** The agent answers from live data — opening: “Pass Match Analysis: Komatsu PC8000 Shovel loading CAT 797F 1. Governing Method & Formula Passes= Shovel_Bucket_Payload×Fill_Factor Truck_Capacity ​ 2. Site Data & Parameter Reconciliation Parameter Operational /…” — key figures 240.0, 205.02, 130.63 t. **Logic.** It reads `fleet_telemetry` in BigQuery, applies Passes = Truck_Capacity / (Shovel_Bucket_Payload * Fill_Factor), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S04-1-SHOVEL/page@de2061e84f4e16644be8b7183aa16327.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17491806829630784661/session/-

## Haul Route Optimizer (S04-2-ROUTE)

*Fleet/Haulage — Fleet Planner*

**Input.** Compute shortest path travel time on Pit Alpha south ramp. **Output.** The agent answers from live data — opening: “Shortest Path & Flow Optimization Method Haul route optimization solves for the minimum-cost travel path using the network flow formulation: min (i,j)∈E ∑ ​ c ij ​ ⋅x ij ​ subject to j:(i,j)∈E ∑ ​ x ij ​ − k:(k,i)∈E ∑ ​…” — key figures 1,031.49, 11.57, 1.27. **Logic.** It reads `dispatch_routes` in BigQuery, applies min sum(c_ij * x_ij) s.t. network flow continuity, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S04-2-ROUTE/page@c63bac73df56f9feebf87faa407058dd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2596064410481970294/session/-

## Truck Payload Sentinel (S04-3-PAYLOAD)

*Fleet/Haulage — Fleet Controller*

**Input.** Audit 10/10/20 payload distribution across 42 haul cycles. **Output.** The agent answers from live data — opening: “OEM 10/10/20 Truck Payload Compliance Audit Auditor: Truck Payload Sentinel (s04_3_payload) Governing Method: $P(X > 1.20 \times \text{Target_Payload}) = 0$ Primary Data Source:…” — key figures 1.20, 240.00, 264.00. **Logic.** It reads `fleet_telemetry` in BigQuery, applies P(X > 1.20 * Target_Payload) = 0, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S04-3-PAYLOAD/page@1cc792fd770a82d48d72a95d0303c650.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4572058693527972819/session/-

## Load & Haul Coordinator (S04-COORDINATOR)

*Fleet/Haulage — Dave (Dispatch Superintendent)*

**Input.** Reassign haul trucks to eliminate 3-truck queue at Shovel 04. **Output.** The agent answers from live data — opening: “Dispatch Reassignment Order & Queue Elimination Plan Coordinator Identity: s04_coordinator Role: Load & Haul Coordinator Governing Method: Little's Law Queueing ($L = \lambda \cdot W$) 1. Operational Situation &…” — key figures 116.8311, 23.1686, 42.0. **Logic.** It reads `fleet_telemetry`, `dispatch_routes` in BigQuery, applies Little's Law Queueing: L = lambda * W, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S04-COORDINATOR/page@e2c435bfbd648161e0fabbb4bf43df62.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/156538017085304316/session/-

## Dispatch Safety Critic (Red Team) (S04-R-CRITIC)

*Fleet/Haulage — Mine Safety Lead*

**Input.** Check operator shift hours and SAFTE circadian fatigue index. **Output.** The agent answers from live data — opening: “1. Shift Schedule & Operational Telemetry Reconciliation Shift Structure & Duration: As defined in standard operating procedure OPS-FMS-001 (Fatigue Management Standard, Revision 3, cited in…” — key figures 7.77, 3.30, 2.0. **Logic.** It reads `fleet_telemetry`, `safety_telemetry` in BigQuery, applies Haul Road Grade Braking Runaway Distance Envelope, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S04-R-CRITIC/page@a13fa27caad6722bea6942323ddd021f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/408790626050543109/session/-

## Crusher CSS Specialist (S05-1-CSS)

*Mineral Processing/Plant — Crusher Technician*

**Input.** Based on the crusher telemetry data, what hydraulic pressure setpoint does your governing method indicate for a closed-side setting of 135mm? Report the figures from the data and cite the table you read. **Output.** The agent answers from live data — opening: “Based on an analysis of the telemetry data in genial-union-475913-i7.mining_data.crusher_telemetry (view over mining_data.crusher_states): 1. Telemetry Data & Reconciled Assumptions Hydraulic Pressure: The…” — key figures 135 mm, 115 mm, 1,157.98 tph. **Logic.** It reads `crusher_telemetry` in BigQuery, applies Q = 3600 * A_gap * v_discharge, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S05-1-CSS/page@b265f8454a5f8fcf1e6270054f871f01.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14348532487284515913/session/-

## Feeder Speed Specialist (S05-2-FEED)

*Mineral Processing/Plant — Control Room Operator*

**Input.** Regulate apron feeder PID loop for choke feeding conditions. **Output.** The agent answers from live data — opening: “Apron Feeder PID Loop Regulation for Choke Feeding As the Feeder Speed Specialist, the operational objective is to regulate the apron feeder speed feeding the primary gyratory crusher (CRUSHER-03) to sustain steady…” — key figures 1,153.23, 1,026.30, 1,297.05. **Logic.** It reads `crusher_telemetry` in BigQuery, applies u(t) = Kp*e(t) + Ki*int(e)dt + Kd*de/dt, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S05-2-FEED/page@1f5c84170d0e7555d78bc039d1fc663a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5869281968369631097/session/-

## Mantle Wear Estimator (S05-3-WEAR)

*Mineral Processing/Plant — Fixed Plant Planner*

**Input.** Predict remaining liner life on Hardox 500 concave plates. **Output.** The agent answers from live data — opening: “Mantle Wear Estimator (s05_3_wear) — Liner Life Assessment 1. Executive Summary & Core Governing Method To predict the remaining service life of the Hardox 500 concave plates lining the primary crushing chamber,…” — key figures 0.02, 4.905, 0.020. **Logic.** It reads `assets`, `crusher_telemetry` in BigQuery, applies V = K * (W * L) / H, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S05-3-WEAR/page@1523fc960d23505a6e367f7a73164d1d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13456155721035413965/session/-

## Primary Crushing Coordinator (S05-COORDINATOR)

*Mineral Processing/Plant — Fixed Plant Superintendent*

**Input.** Crusher-03 mantle wear is at 78%; eddy-current sensor flags tramp iron. **Output.** The agent answers from live data — opening: “Primary Crushing Coordinator Operational Assessment & Directive Asset: CRUSHER-03 (Primary Gyratory Crusher Unit) Coordinator ID: s05_coordinator Governing Method: Bond Comminution: $W =…” — key figures 1,210.0 tph, 1,145.57 tph, 1,153.23 tph. **Logic.** It reads `crusher_telemetry`, `assets` in BigQuery, applies Bond Comminution: W = 10 Wi (1/sqrt(P80) - 1/sqrt(F80)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S05-COORDINATOR/page@91b87b78f7ed8a27f1d58e07fc868025.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15517074791576987099/session/-

## Tramp Metal Critic (Red Team) (S05-R-CRITIC)

*Mineral Processing/Plant — Electrical Superintendent*

**Input.** Enforce auto-hold on uncrushable steel tooth detection in cavity. **Output.** The agent answers from live data — opening: “Operational Directive: Tramp Iron Eddy-Current Sensor Interlock Gate Activation Watchdog / Role: Tramp Metal Critic (Red Team) Governing Method: Tramp Iron Eddy-Current Sensor Interlock Gate Target Asset: CRUSHER-03…” — key figures 0.00 tph, 1,145.57 tph, 1,153.23 tph. **Logic.** It reads `crusher_telemetry` in BigQuery, applies Tramp Iron Eddy-Current Sensor Interlock Gate, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S05-R-CRITIC/page@98411fddda44b0bfe86540c229422932.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1150542196225760960/session/-

## SAG Mill Load Specialist (S06-1-SAG)

*Mineral Processing/Plant — Mill Operator*

**Input.** Analyze 1/3-octave acoustic sensor array on SAG mill shell. **Output.** The agent answers from live data — opening: “Executive Summary & Specialist Role As SAG Mill Load Specialist (s06_1_sag), mill charge dynamics and grinding efficiency are evaluated using the Acoustic Toe Angle & Ball Charge Trajectory governing methodology. This…” — key figures 1.0, 8.0, 14.501. **Logic.** It reads `plant_telemetry` in BigQuery, applies Acoustic Toe Angle & Ball Charge Trajectory, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S06-1-SAG/page@f199ce2dc812435aaee81286ddad5f45.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17267471152570781932/session/-

## Ball Mill Power Specialist (S06-2-BALL)

*Mineral Processing/Plant — Grinding Technician*

**Input.** Calculate daily grinding media ball charge replenishment for 3,800 tph. **Output.** The agent answers from live data — opening: “1. Operational Telemetry & Baseline Reconciliation As the Ball Mill Power Specialist governing grinding performance via the Austin Population Balance Grinding Kinetics method, operational data was retrieved and…” — key figures 3,800.0 tph, 91,200.0, 1,153.25. **Logic.** It reads `plant_telemetry` in BigQuery, applies Austin Population Balance Grinding Kinetics, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S06-2-BALL/page@e7a28a08e243ca88d212613afe916528.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13921225072596694266/session/-

## Hydrocyclone Split Specialist (S06-3-CYCLONE)

*Mineral Processing/Plant — Slurry Specialist*

**Input.** Model cut size d50c on 12-cyclone cluster operating at 110 kPa. **Output.** The agent answers from live data — opening: “Hydrocyclone Split Specialist Analysis 1. Governing Method The governing formulation for calculating the hydrocyclone corrected cut size is the Plitt Cut Size Model: d 50c ​ = D u 0.71 ​ ⋅h 0.38 ⋅Q 0.45 50.5⋅D c 0.46 ​…” — key figures 0.71, 0.38, 0.45. **Logic.** It reads `plant_telemetry` in BigQuery, applies Plitt Cut Size: d50c = (50.5 * Dc^0.46 * Di^0.6 * Do^0.68) / (Du^0.71 * h^0.38 * Q^0.45), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S06-3-CYCLONE/page@db766dae3e20d54b9bb1c069b48efcab.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7787327341957815195/session/-

## Grinding & Milling Coordinator (S06-COORDINATOR)

*Mineral Processing/Plant — Concentrator Superintendent*

**Input.** SAG Mill #2 power spikes to 14.8 MW, toe acoustic noise dampened. **Output.** The agent answers from live data — opening: “Grinding & Milling Coordination Log Agent: s06_coordinator Governing Method: Morrell Specific Energy W=4⋅M i ​ ⋅(x 2 f(x 2 ​ ) ​ −x 1 f(x 1 ​ ) ​ ) (where $M_i$ is the Morrell rock breakage hardness parameter, $x_1$ is…” — key figures 0.295, 14.8, 3.09. **Logic.** It reads `plant_telemetry`, `assets` in BigQuery, applies Morrell Specific Energy: W = 4 * M_i * (x2^f(x2) - x1^f(x1)), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S06-COORDINATOR/page@513da6e59e3179aabf04e3c5363203fd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/16231628556639519542/session/-

## Slurry Density Critic (Red Team) (S06-R-CRITIC)

*Mineral Processing/Plant — Process Chemist*

**Input.** Check cyclone feed density and trunnion bearing lubrication. **Output.** The agent answers from live data — opening: “Operational Review: Cyclone Feed Density & Trunnion Bearing Lubrication Reviewing Role: Slurry Density Critic (Red Team) Governing Method: Pipeline Critical Settling Velocity & Slurry Viscosity Limits Primary Evidence…” — key figures 12.50, 5.60, 4.00. **Logic.** It reads `plant_telemetry` in BigQuery, applies Pipeline Critical Settling Velocity & Slurry Viscosity Limits, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S06-R-CRITIC/page@d0e37b97f6c22011dae6b16c499155f7.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13013800279746514045/session/-

## Collector Dosing Specialist (S07-1-REAGENT)

*Mineral Processing/Plant — Flotation Technician*

**Input.** Calculate frother MIBC addition rate for 1.4 cm/s air velocity. **Output.** The agent answers from live data — opening: “Reagent Inventory Verification & Operational Grounding A review of the inventory records in genial-union-475913-i7.mining_data.reagent_inventory shows the following operational status for MIBC: Field Value Source Table…” — key figures 75.00, 21 days, 1.4. **Logic.** It reads `reagent_inventory` in BigQuery, applies theta = (K * C) / (1 + K * C), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S07-1-REAGENT/page@04ceb4e495a79aa83c07d4348713c11e.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12936409017092172708/session/-

## Froth Air Specialist (S07-2-AIR)

*Mineral Processing/Plant — Plant Metallurgist*

**Input.** Regulate superficial gas velocity Jg across rougher bank. **Output.** The agent answers from live data — opening: “1. Governing Method & Hydrodynamic Framework As Froth Air Specialist, superficial gas velocity ($J_g$) and froth depth are regulated across the rougher bank to optimize bubble surface area flux ($S_b = \frac{6…” — key figures 1,153.25 tph, 1,000.56, 1,299.86 tph. **Logic.** It reads `plant_telemetry` in BigQuery, applies Gas Holdup: eps_g = J_g / (u_b + J_l), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S07-2-AIR/page@d00e951d6f551556e45f00446ca90080.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/13003249075149879793/session/-

## Concentrate Grade Specialist (S07-3-GRADE)

*Mineral Processing/Plant — Smelter Marketing Liaison*

**Input.** Model cleaner bank separation efficiency for 28% Cu concentrate. **Output.** The agent answers from live data — opening: “Executive Summary For a 28.00% Cu concentrate in the cleaner bank flotation circuit: Modeled Separation Efficiency ($SE$): 89.66% (at operational mean feed of $1.093%$ Cu and baseline tailings of $0.0875%$ Cu). Valuable…” — key figures 28.00%, 89.66%, 1.093%. **Logic.** It reads `flotation_assays` in BigQuery, applies Separation Efficiency: SE = R_val - R_gangue, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S07-3-GRADE/page@079d1e27603dd80da1900f5aa0e4641c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3383821664191445726/session/-

## Flotation Recovery Coordinator (S07-COORDINATOR)

*Mineral Processing/Plant — Marcus (Chief Metallurgist)*

**Input.** Optimize PAX collector dosing for 0.72% Cu ore to maximize recovery. **Output.** The agent answers from live data — opening: “1. Operational Reconciliation of Feed Grade & Parameters Assumed Feed Grade in Prompt: $0.72%\text{ Cu}$ Operational Feed Grade in flotation_assays: Historical Range: $0.81%\text{ Cu}$ to $1.42%\text{ Cu}$ (167…” — key figures 0.72%, 0.81%, 1.42%. **Logic.** It reads `flotation_assays`, `plant_telemetry` in BigQuery, applies Langmuir Kinetics: R(t) = R_inf * [1 - exp(-k*t)], reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S07-COORDINATOR/page@357fe133e3f83e9a32a4662a14d6c1b8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4100790245321040707/session/-

## Smelter Penalty Critic (Red Team) (S07-R-CRITIC)

*Mineral Processing/Plant — Commercial Metallurgist*

**Input.** Check concentrate arsenic and bismuth penalty thresholds. **Output.** The agent answers from live data — opening: “Audit Review: Concentrate Arsenic & Bismuth Penalty Thresholds Auditor Role: Smelter Penalty Critic (Red Team) Governing Standard: Arsenic / Bismuth Penalty Threshold Matrix Audited Data Source:…” — key figures 27.41%, 24.99%, 30.16%. **Logic.** It reads `flotation_assays` in BigQuery, applies Arsenic / Bismuth Penalty Threshold Matrix, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S07-R-CRITIC/page@29b8387bd87233a448894838e577957a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2422340200045156267/session/-

## Decant Water Return Specialist (S08-1-WATER)

*Mineral Processing/Plant — Water Treatment Operator*

**Input.** Balance decant return water and evaporation pond volume. **Output.** The agent answers from live data — opening: “Decant Water & Evaporation Pond Water Balance Analysis Governing Method: V ret ​ =V in ​ −V evap ​ −V seep ​ −V pore ​ Where: $V_{\text{in}}$ = Slurry water inflow to the Tailings Storage Facility (TSF) / decant pond…” — key figures 183,156.10, 1,096.74, 100.00%. **Logic.** It reads `water_balance_logs` in BigQuery, applies V_ret = V_in - V_evap - V_seep - V_pore, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S08-1-WATER/page@1875f394a9efcb3928f3bbca231031ba.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/7388494887499711666/session/-

## Piezometer Pressure Specialist (S08-2-PORE)

*Mineral Processing/Plant — Geotech Instrumentation Tech*

**Input.** Model Terzaghi 1D consolidation under Dam 2 embankment. **Output.** The agent answers from live data — opening: “Terzaghi 1D Consolidation Model for Dam Embankment 1. Governing Theoretical Formulation Under Terzaghi’s one-dimensional consolidation theory, the transient dissipation of excess pore water pressure $u(z,t)$ generated…” — key figures 9.81, 1.0, 0.60. **Logic.** It reads `tsf_piezometers` in BigQuery, applies Terzaghi Consolidation: du/dt = c_v * (d2u / dz2), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S08-2-PORE/page@9e770346f27464593794d57607fbb0b3.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17689915318949018488/session/-

## Slurry Thickener Specialist (S08-3-THICK)

*Mineral Processing/Plant — Dewatering Technician*

**Input.** Regulate flocculant dosing for 65% solids underflow. **Output.** The agent answers from live data — opening: “Slurry Thickener Specialist Report: Flocculant Dosing & Underflow Density Regulation Agent: s08_3_thick Governing Method: Kynch Sedimentation Solids Flux Theory & Compressive Consolidation Dynamics Primary Telemetry…” — key figures 1,153.25, 1,000.56, 1,299.86. **Logic.** It reads `plant_telemetry` in BigQuery, applies Kynch Sedimentation Solids Flux Theory, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S08-3-THICK/page@121fa0ce91cfa410229293dc0b0989ce.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2504307796515544315/session/-

## Tailings (TSF) Coordinator (S08-COORDINATOR)

*Mineral Processing/Plant — TSF Manager (Engineer of Record)*

**Input.** Dam 2 piezometer reports pore pressure rise of 0.38m/week after rain. **Output.** The agent answers from live data — opening: “TSF Technical Evaluation & GISTM Dam Conformance Review Role: Tailings (TSF) Coordinator (s08_coordinator) Governing Method: GISTM Dam Conformance & Phreatic Surface Line Operational Datasets:…” — key figures 0.38, 3.73, 9.81. **Logic.** It reads `tsf_piezometers`, `water_balance_logs` in BigQuery, applies GISTM Dam Conformance & Phreatic Surface Line, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S08-COORDINATOR/page@84f268273a0492af1bff9ad678cba3c2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5704906778757729715/session/-

## TSF Liquefaction Critic (Red Team) (S08-R-CRITIC)

*Mineral Processing/Plant — Statutory Geotechnical Reviewer*

**Input.** Audit GISTM compliance and critical state soil mechanics. **Output.** The agent answers from live data — opening: “Adversarial Geotechnical Audit: GISTM Compliance & Static Liquefaction Assessment Auditor: s08_r_critic (TSF Liquefaction Critic – Red Team) Governing Framework: Global Industry Standard on Tailings Management (GISTM) &…” — key figures 18.0%, 1.50, 1.135. **Logic.** It reads `tsf_piezometers`, `safety_permits` in BigQuery, applies Critical State Soil Mechanics & Static Liquefaction Index, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S08-R-CRITIC/page@7abacb8c9b699910c44fec0934a3bde2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5536394081075780335/session/-

## Vibration FFT Specialist (S09-1-VIBRATION)

*Asset Integrity/Maintenance — Vibration Analyst (Category III)*

**Input.** Parse 10-1000Hz vibration spectrum for bearing defect harmonics. **Output.** The agent answers from live data — opening: “1. Governing Method & Analysis Overview This analysis processes accelerometer data in the 10–1000 Hz standard frequency band according to ISO 10816-3 (Mechanical vibration — Evaluation of machine vibration by…” — key figures 116.8532, 23.1189, 0.02. **Logic.** It reads `assets`, `crusher_telemetry` in BigQuery, applies ISO 10816-3 RMS Velocity & BPFI Harmonics, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S09-1-VIBRATION/page@8b3bd2504000791f37a1ebbd6d597ccd.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/1209525171906486472/session/-

## Oil Tribology Specialist (S09-2-TRIBOLOGY)

*Asset Integrity/Maintenance — Lubrication Technician*

**Input.** Evaluate Karl Fischer moisture and PQ particle quantifier index. **Output.** The agent answers from live data — opening: “Tribological Evaluation: Karl Fischer Moisture & Particle Quantifier (PQ) Index 1. Governing Tribology Framework & Methodology As an Oil Tribology Specialist, lubricant condition and machine reliability are evaluated…” — key figures 0.0, 0.0000%, 705.41. **Logic.** It reads `assets`, `lube_samples` in BigQuery, applies PQ Index & Karl Fischer Moisture PPM, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S09-2-TRIBOLOGY/page@ef78a8a849e1cd2ebc7e5fb2f5a6c752.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6541943629968723451/session/-

## Thermal IR Specialist (S09-3-THERMAL)

*Asset Integrity/Maintenance — Thermographer*

**Input.** Analyze thermal gradient across pinion bearing housing. **Output.** The agent answers from live data — opening: “Thermal IR Assessment: Pinion Bearing Housing Thermal Gradient & Temperature Rise Analyst: Thermal IR Specialist (s09_3_thermal) Governing Methodology: Delta T Component Temperature Rise Model Monitored Asset: Primary…” — key figures 74.0, 4,205.0, 3,905.96. **Logic.** It reads `assets`, `crusher_telemetry` in BigQuery, applies Delta T Component Temperature Rise Model, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S09-3-THERMAL/page@971bd19431ff803203abdeace2559910.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/12266523653873596783/session/-

## Asset Reliability Swarm Coordinator (S09-COORDINATOR)

*Asset Integrity/Maintenance — Priya (Reliability Superintendent)*

**Input.** SAG Mill pinion bearing vibration reaches 4.8 mm/s RMS at 1480 RPM. **Output.** The agent answers from live data — opening: “Asset Reliability Swarm Coordinator (s09_coordinator) Role: P0 Crisis Arbiter & Reliability Superintendent Forensic Domains: Vibration FFT, Tribology & Wear Debris, Thermal Runaway, and Weibull Prognostics 1.…” — key figures 14.8, 4.25, 4.0. **Logic.** It reads `assets`, `crusher_telemetry`, `erp_work_orders` in BigQuery, applies Weibull Hazard Rate: h(t) = (beta / eta) * (t / eta)^(beta - 1), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S09-COORDINATOR/page@3f4b4cc3623076a24998ed20d18ae3f1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/523079695801690856/session/-

## Maintenance Safety Critic (Red Team) (S09-R-CRITIC)

*Asset Integrity/Maintenance — Safety Supervisor*

**Input.** Enforce Dual-Key HMAC MFA prior to staging SAP PM work pack. **Output.** The agent answers from live data — opening: “Safety Gate Audit & Enforcement Decision Agent: s09_r_critic (Maintenance Safety Critic — Red Team) Governing Method: LOTO Isolation Integrity & Failure Window Safety Gate Reference Standard: LOTO 09-CR-LOTO-03 Audited…”. **Logic.** It reads `assets`, `erp_work_orders` in BigQuery, applies LOTO Isolation Integrity & Failure Window Safety Gate, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S09-R-CRITIC/page@e3c25c17881294e8bb32c71f9ab64eb7.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3018210570239869511/session/-

## Contract Rate Auditor (S10-1-CONTRACT)

*Supply Chain/Logistics — Procurement Analyst*

**Input.** Fuzzy-match line items against signed Master Service Agreement. **Output.** The agent answers from live data — opening: “Contract Rate Audit: Fuzzy-Match Line Items vs. Signed Master Service Agreements (MSA) Auditor Internal ID: s10_1_contract Governing Method: Levenshtein Distance & Unit Price Deviation Source Tables Consulted:…” — key figures 1,149.35, 390.23, 1,116.43. **Logic.** It reads `vendor_contracts` in BigQuery, applies Levenshtein Distance & Unit Price Deviation, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S10-1-CONTRACT/page@72f338ab547dd17ad051eae32681385d.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/4380926452236138549/session/-

## PPI Indexation Auditor (S10-2-ESCALATE)

*Supply Chain/Logistics — Commercial Specialist*

**Input.** Compute labor and diesel escalation delta against PPI indices. **Output.** The agent answers from live data — opening: “PPI Indexation & Escalation Audit Governing Formula: P t ​ =P 0 ​ ×[a+b( L 0 ​ L t ​ ​ )+c( M 0 ​ M t ​ ​ )] Where: $P_0$: Base contract unit price $P_t$: Escalated contract unit price at period $t$ $a$: Fixed /…” — key figures 1.0, 1,149.35, 0.00. **Logic.** It reads `vendor_contracts` in BigQuery, applies P_t = P_0 * [a + b*(L_t/L_0) + c*(M_t/M_0)], reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S10-2-ESCALATE/page@bf6f37291570daf56c224e861a0c6d76.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15145174503599723797/session/-

## Warranty Recovery Specialist (S10-3-WARRANTY)

*Supply Chain/Logistics — Asset Accountant*

**Input.** Audit SAG liner premature failure against 8,000-hour MTBF warranty. **Output.** The agent answers from live data — opening: “Executive Summary & Audit Assessment An audit was conducted under the MTBF vs Warranty Period Recovery Claimer methodology to evaluate the assumed SAG liner premature failure against an 8,000-hour MTBF warranty. All…” — key figures 8,000 hours, 14.8, 452.0. **Logic.** It reads `assets`, `vendor_contracts` in BigQuery, applies MTBF vs Warranty Period Recovery Claimer, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S10-3-WARRANTY/page@17b82dc0017fae45c0e3ace352ca962a.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/10236263633444215320/session/-

## Procurement Coordinator (S10-COORDINATOR)

*Supply Chain/Logistics — Sarah (Supply Chain Superintendent)*

**Input.** Audit contractor haulage invoice #INV-8839 against signed MSA rate card. **Output.** The agent answers from live data — opening: “Procurement Audit Report Governing Method: Invoice Contract Matching & Rate Card Variance Internal Entity: Procurement Coordinator (s10_coordinator) Scope of Review: Contractor Haulage Invoice INV-8839 vs. Signed Master…”. **Logic.** It reads `vendor_contracts`, `invoices` in BigQuery, applies Invoice Contract Matching & Rate Card Variance, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S10-COORDINATOR/page@a8ca181f542b35b516a0923e4be645fe.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/5402454714704667630/session/-

## Anti-Bribery Audit Critic (Red Team) (S10-R-CRITIC)

*Supply Chain/Logistics — Internal Auditor*

**Input.** Enforce FCPA compliance gate on sole-source supplier requisitions. **Output.** The agent answers from live data — opening: “FCPA & Anti-Bribery Compliance Audit Report: Sole-Source Supplier Requisition Gate Enforcement Auditor: Anti-Bribery Audit Critic (Red Team) — s10_r_critic Governing Method: Vendor Beneficial Ownership & Single-Source…” — key figures 802,443.52, 129,258.90, 57,662.34. **Logic.** It reads `vendor_contracts`, `invoices` in BigQuery, applies Vendor Beneficial Ownership & Single-Source Flags, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S10-R-CRITIC/page@020e98ac12494a421b4ea528373d112f.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/6963659721239708994/session/-

## Safety Stock Optimizer (S11-1-STOCK)

*Supply Chain/Logistics — Inventory Planner*

**Input.** Calculate safety stock buffer for high-criticality bearings. **Output.** The agent answers from live data — opening: “Dynamic Safety Stock Optimization: High-Criticality Bearings Agent: Safety Stock Optimizer (s11_1_stock) Governing Method: SS=Z α ​ × L⋅σ D 2 ​ +D 2 ⋅σ L 2 ​ ​ 1. Operational Inventory Status From…” — key figures 14 days, 1,250.00, 0.00. **Logic.** It reads `spares_inventory` in BigQuery, applies SS = Z_alpha * sqrt(L * sigma_D^2 + D^2 * sigma_L^2), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S11-1-STOCK/page@3b965bd8a823d77f9c94fcdfd0911e10.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/8952188845126189763/session/-

## Vendor Lead Time Specialist (S11-2-LEADTIME)

*Supply Chain/Logistics — Supply Expediter*

**Input.** Model Gamma distribution supplier lead-time variability. **Output.** The agent answers from live data — opening: “Gamma Distribution Supplier Lead-Time Modeling Role: Vendor Lead Time Specialist Governing Method: Gamma Distribution Lead Time Modeling Primary Data Source: genial-union-475913-i7.mining_data.purchase_orders (with…” — key figures 13.94, 14.46, 7.34. **Logic.** It reads `purchase_orders` in BigQuery, applies Gamma Distribution Lead Time Modeling, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S11-2-LEADTIME/page@6e9fc9e33cedc9579f517726878ca4d1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/9319212464069988816/session/-

## Carrying Cost Analyzer (S11-3-HOLDING)

*Supply Chain/Logistics — Cost Controller*

**Input.** Analyze working capital carrying cost on $45M MRO warehouse. **Output.** The agent answers from live data — opening: “1. Governing Methodology Carrying cost is analyzed using the standard holding cost formulation: H=C×(i+w+o) Where: $C$: Total inventory capital base (USD) $i$: Working capital cost / opportunity cost of capital rate…” — key figures 45,000,000.00, 55,879,117.67, 10,879,117.67. **Logic.** It reads `spares_inventory` in BigQuery, applies H = C_unit * (i + w + o), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S11-3-HOLDING/page@66e7ec03ebb75e6b29e261977b555ee2.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/3626231911448469840/session/-

## Spares Inventory Coordinator (S11-COORDINATOR)

*Supply Chain/Logistics — Warehouse Superintendent*

**Input.** Hydraulic cylinder stock is 0 with 8-week supplier lead time. **Output.** The agent answers from live data — opening: “Operational Reconciliation & Inventory Assessment 1. Reconciliation of Stated Assumptions vs. Operational Data Part Description & Stock Level: Supplied Assumption: "Hydraulic cylinder stock is 0" Table Evidence…” — key figures 14 days, 7 days, 450.00. **Logic.** It reads `spares_inventory`, `purchase_orders` in BigQuery, applies Wilson EOQ: Q* = sqrt(2*D*S / H), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S11-COORDINATOR/page@89f6e5164009a0cd7c1c23ecbd6a78b1.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/2773276585102532221/session/-

## Dead Stock Critic (Red Team) (S11-R-CRITIC)

*Supply Chain/Logistics — Finance Auditor*

**Input.** Flag non-moving spares (>365 days) for inventory buyback. **Output.** The agent answers from live data — opening: “Executive Summary & Inventory Critique Total Tracked Spares Inventory Value: $55,879,117.67 across 140 SKUs and 9,648 units (Source: genial-union-475913-i7.mining_data.spares_inventory / mining_data.inventory_levels).…” — key figures 55,879,117.67, 2,880.00, 55,876,237.67. **Logic.** It reads `spares_inventory` in BigQuery, applies Inactive Inventory Aging (>365 Days) Write-Down, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S11-R-CRITIC/page@cd7427b159537723fc7d528ac993b8bc.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/14327129105282995811/session/-

## Train Cycle Dispatch Specialist (S12-1-RAIL)

*Supply Chain/Logistics — Rail Controller*

**Input.** Optimize train rake cycle time across 400km heavy-haul rail corridor. **Output.** The agent answers from live data — opening: “Executive Summary & Operational Context Role: Train Cycle Dispatch Specialist (Agent: s12_1_rail) Governing Method: Railway Headway & Velocity Optimization Corridor Scope: 400 km Heavy-Haul Rail Corridor (800 km…” — key figures 2,149,409.5, 1,047,854.0 t, 1,101,555.5 t. **Logic.** It reads `rail_schedules` in BigQuery, applies Railway Headway & Velocity Optimization, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S12-1-RAIL/page@f4013a97398addf0a7506d2f77066b4c.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17163419417666421589/session/-

## Port Stockpile Blend Specialist (S12-2-BLEND)

*Supply Chain/Logistics — Port Metallurgist*

**Input.** Formulate LP blend model for 28.0% Cu export specification. **Output.** The agent answers from live data — opening: “1. Operational & Data Reconciliation Before formulating the optimization model, the target specification of 28.0% Cu is reconciled against operational data recorded in BigQuery project genial-union-475913-i7: Stockpile…” — key figures 28.0%, 2,985,121.80, 0.4728%. **Logic.** It reads `stockpiles` in BigQuery, applies Linear Blend Optimization: min ||A*x - b||, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S12-2-BLEND/page@c60902bdf85c702604da4e387ec0fe20.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17572349194673256958/session/-

## Marine Laytime & Demurrage Specialist (S12-3-BERTH)

*Supply Chain/Logistics — Marine Broker*

**Input.** Compute BIMCO laytime Statement of Fact deductions. **Output.** The agent answers from live data — opening: “BIMCO Statement of Fact (SOF) Laytime & Demurrage Liability Report Agent Designation: s12_3_berth Governing Standard: BIMCO Laytime Pro-Rata & Demurrage Liability Primary Source Table:…” — key figures 2,391,744.70 t, 1,305,149.50 t, 1,086,595.20 t. **Logic.** It reads `port_vessels` in BigQuery, applies BIMCO Laytime Pro-Rata & Demurrage Liability, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S12-3-BERTH/page@883c977584e76b59bf90e7e310ccce52.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/17205870215175020849/session/-

## Supply Chain & Port Coordinator (S12-COORDINATOR)

*Supply Chain/Logistics — Logistics Manager*

**Input.** Vessel 'MV Cape Osprey' arrives in 48h for 160,000t loading. **Output.** The agent answers from live data — opening: “Operational Assessment & Execution Plan: MV Cape Osprey (160,000 t) Role: Supply Chain & Port Coordinator (s12_coordinator) Governing Method: Dynamic Network Sim: $\min \sum (\text{Rail} + \text{Port} +…” — key figures 59,793.6, 100,619.2, 24,431.6. **Logic.** It reads `rail_schedules`, `port_vessels`, `stockpiles` in BigQuery, applies Dynamic Network Sim: min sum(Rail + Port + Demurrage), reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S12-COORDINATOR/page@2c27ca5ea3461d820a218c2635bbc6f8.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15457650955703083468/session/-

## Moisture & TML Critic (Red Team) (S12-R-CRITIC)

*Supply Chain/Logistics — Cargo Surveyor*

**Input.** Enforce IMSBC Transportable Moisture Limit (TML < 9.2%). **Output.** The agent answers from live data — opening: “IMSBC Transportable Moisture Limit (TML) Interlock Enforcement Agent: Moisture & TML Critic (Red Team / s12_r_critic) Governing Method: IMSBC Code Transportable Moisture Limit (TML) Interlock Data Sources:…” — key figures 9.20%, 17.5%, 358,693.10. **Logic.** It reads `port_vessels`, `stockpiles` in BigQuery, applies IMSBC Transportable Moisture Limit (TML) Interlock, reconciles any figures supplied in the question against what the data actually says, and cites the tables behind every number — so the answer is traceable, not plausible.

- **Recording:** `data/uat/videos/S12-R-CRITIC/page@220cba1c1a025e4a4c655807f14f00d6.webm`
- **Live agent:** https://vertexaisearch.cloud.google.com/home/cid/af13d38d-d69f-4dce-9076-f12625444a86/r/agent/15122170761949992179/session/-
