/**
 * Client-Side Demo Data & Offline Intelligence Engine for MTIS
 * Powers all 5 stages (Search, Gap, Titles, DeepDive, Plan) seamlessly
 * on Netlify or when the backend is offline.
 */

export const DEMO_USERS = [
  {
    id: "usr-student",
    tenant_id: "tenant-demo-002",
    name: "Demo Student",
    email: "student@demo.test",
    role: "student",
    plan: "free",
    quota_remaining: 3,
    quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
    created_at: new Date().toISOString(),
  },
  {
    id: "usr-ahmad",
    tenant_id: "tenant-utm-001",
    name: "Ahmad bin Razak",
    email: "ahmad@utm.my",
    role: "student",
    plan: "free",
    quota_remaining: 3,
    quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
    created_at: new Date().toISOString(),
  },
  {
    id: "usr-admin",
    tenant_id: "tenant-demo-002",
    name: "System Administrator",
    email: "admin@demo.test",
    role: "admin",
    plan: "enterprise",
    quota_remaining: 999,
    quota_reset_at: new Date(Date.now() + 86400000).toISOString(),
    created_at: new Date().toISOString(),
  },
];

export const DEMO_TENANTS: { [id: string]: { id: string; name: string } } = {
  "tenant-demo-002": { id: "tenant-demo-002", name: "Demo University Campus" },
  "tenant-utm-001": { id: "tenant-utm-001", name: "Universiti Teknologi Malaysia (UTM)" },
};

export const TVET_PAPERS = [
  {
    title: "Workplace Competency and Technical Skills Acquisition in Malaysian TVET Institutes: An Industry-Academia Linkage Model",
    authors: ["Mohd Zulkifli Ahmad", "Nor Azlan Ibrahim"],
    year: 2023,
    doi: "10.1016/j.procs.2023.01.205",
    url: "https://scholar.google.com/scholar?q=Workplace+Competency+and+Technical+Skills+Acquisition+in+Malaysian+TVET+Institutes",
    abstract: "This empirical study investigates the alignment between technical curriculum delivery in Malaysian polytechnics and Industry 4.0 competency requirements of advanced manufacturing employers in Johor and Selangor. Using structural equation modeling on data collected from 180 industrial training coordinators and 320 diploma apprentices, critical skill gaps in automation and industrial IoT troubleshooting were identified.",
    source: "openalex",
    citation_count: 27,
  },
  {
    title: "Digital Transformation Challenges in Malaysian Vocational Colleges (Kolej Vokasional): Instructor Readiness and Curriculum Friction",
    authors: ["Siti Aminah Kassim", "Faridah Othman"],
    year: 2024,
    doi: "10.1080/13636820.2023.2201945",
    url: "https://scholar.google.com/scholar?q=Digital+Transformation+Challenges+in+Malaysian+Vocational+Colleges+Kolej+Vokasional",
    abstract: "Malaysian TVET institutions face rapid shifts towards digitized workshop instruction. Drawing upon the Technology Acceptance Model (TAM), this study evaluates technological readiness and institutional barriers among 210 vocational instructors across Selangor and Perak.",
    source: "openalex",
    citation_count: 19,
  },
  {
    title: "Public-Private Partnerships in Technical and Vocational Education Training (TVET): Enhancing Graduate Employability in Southern Malaysia",
    authors: ["Tan Boon Kiat", "Kamarul Zaman"],
    year: 2023,
    doi: "10.1016/j.chb.2023.108442",
    url: "https://scholar.google.com/scholar?q=Public-Private+Partnerships+in+Technical+and+Vocational+Education+Training+TVET+Malaysia+UTM",
    abstract: "Analyzing tripartite governance between the Ministry of Higher Education, state skill development centers, and multinational engineering firms. Mixed-methods findings demonstrate a 34% increase in permanent technical job placements under structured work-based learning schemes.",
    source: "utm",
    citation_count: 31,
  },
  {
    title: "Green Skills Integration in Malaysian TVET Curricula: Perceptions of Engineering Technology Students and Industry Stakeholders",
    authors: ["Harpreet Kaur", "Muhammad Arif Ismail"],
    year: 2022,
    doi: "10.1108/JFM-04-2022-0044",
    url: "https://scholar.google.com/scholar?q=Green+Skills+Integration+in+Malaysian+TVET+Curricula+Perceptions+of+Engineering+Technology",
    abstract: "Assessing environmental sustainability and renewable energy modular competencies within Malaysian National Occupational Skills Standards (NOSS). Survey across four technical campuses highlights a significant deficit in practical green technology apprenticeships.",
    source: "utm",
    citation_count: 14,
  },
];

export const DEMO_SEARCH_PAPERS = [
  {
    title: "Determinants of E-Wallet Adoption among Malaysian Small and Medium Enterprises: A UTAUT2 Perspective",
    authors: ["Ahmad Razak", "Siti Nurhaliza"],
    year: 2023,
    doi: "10.1016/j.ijinfomgt.2023.102611",
    url: "https://scholar.google.com/scholar?q=Determinants+of+E-Wallet+Adoption+among+Malaysian+Small+and+Medium+Enterprises+UTAUT2",
    abstract: "This study examines the behavioral intentions of Malaysian SMEs toward continuous adoption of digital e-wallets. Using an extended UTAUT2 model incorporating transaction security and government subsidies under the Malaysia Digital Economy Blueprint.",
    source: "openalex",
    citation_count: 34,
  },
  {
    title: "Cybersecurity Vulnerabilities and Consumer Trust in Malaysian Cashless Payment Ecosystems",
    authors: ["Wei Lun Tan", "Mohd Hashim Ibrahim"],
    year: 2022,
    doi: "10.1016/j.chb.2022.107405",
    url: "https://scholar.google.com/scholar?q=Cybersecurity+Vulnerabilities+and+Consumer+Trust+in+Malaysian+Cashless+Payment",
    abstract: "Digital payment solutions have surged across urban Malaysian commercial centers. However, fraud vectors, unauthorized micro-transactions, and QR code tampering remain key obstacles for small micro-merchants.",
    source: "openalex",
    citation_count: 21,
  },
  {
    title: "Digital Transformation Challenges of Malaysian MSMEs: An Empirical Study of Touch 'n Go and GrabPay Integration",
    authors: ["Faridah Othman", "Kamarul Zaman", "Cheng Hock Lee"],
    year: 2023,
    doi: "10.1016/j.chb.2023.107890",
    url: "https://scholar.google.com/scholar?q=Digital+Transformation+Challenges+of+Malaysian+MSMEs+Touch+n+Go+GrabPay",
    abstract: "The post-pandemic digitization push accelerated cashless adoption among Malaysian micro, small, and medium enterprises. This paper analyzes technological and financial barriers faced by 450 merchants in Kuala Lumpur and Penang.",
    source: "openalex",
    citation_count: 48,
  },
  {
    title: "DuitNow QR Adoption Factors in Rural Malaysian Traditional Retailers: A TOE Framework Analysis",
    authors: ["Muhammad Arif Ismail", "Noraini Mat"],
    year: 2024,
    doi: "10.1108/JFM-08-2023-0091",
    url: "https://scholar.google.com/scholar?q=DuitNow+QR+Adoption+Factors+in+Rural+Malaysian+Traditional+Retailers+TOE",
    abstract: "Drawing on the Technology-Organization-Environment (TOE) framework, this research evaluates national interoperable QR code integration among rural grocery merchants across Pahang and Kelantan.",
    source: "openalex",
    citation_count: 12,
  },
];

export function getPapersForQuery(query: string, scope: string = "MY") {
  const q = (query || "").trim().toLowerCase();
  if (q.includes("tvet") || q.includes("vocational") || q.includes("curriculum") || q.includes("polytechnic")) {
    return TVET_PAPERS;
  }
  if (!q || q.includes("cashless") || q.includes("e-wallet") || q.includes("payment") || q.includes("fintech") || q.includes("sme")) {
    return DEMO_SEARCH_PAPERS;
  }

  const capTopic = query.trim().split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  return [
    {
      title: `Empirical Assessment of ${capTopic} Adoption in Malaysian Higher Education Institutions`,
      authors: ["Mohd Syazwan", "Nurul Hidayah"],
      year: 2023,
      doi: "10.1016/j.compedu.2023.104712",
      url: `https://scholar.google.com/scholar?q=${encodeURIComponent(`Empirical Assessment of ${capTopic} Adoption in Malaysian Higher Education Institutions`)}`,
      abstract: `This study examines institutional readiness, behavioral intentions, and policy friction surrounding ${query} across Malaysian campuses, using an extended technology acceptance framework.`,
      source: "openalex",
      citation_count: 24,
    },
    {
      title: `Implementation Challenges and Regulatory Compliance of ${capTopic} Across Malaysian Public Universities`,
      authors: ["Zalina Ahmad", "Kamarul Zaman"],
      year: 2024,
      doi: "10.1016/j.edurev.2023.100561",
      url: `https://scholar.google.com/scholar?q=${encodeURIComponent(`${capTopic} UTM Universiti Teknologi Malaysia`)}`,
      abstract: `Investigating governance models, resource allocation constraints, and stakeholder perspectives in deploying ${query} solutions within regional academic centers.`,
      source: "utm",
      citation_count: 18,
    },
    {
      title: `A Mixed-Methods Investigation into ${capTopic} for Regional Industry Competitiveness in Peninsular Malaysia`,
      authors: ["Ahmad Razak", "Faridah Othman"],
      year: 2023,
      doi: "10.1016/j.chb.2023.108442",
      url: `https://scholar.google.com/scholar?q=${encodeURIComponent(`${capTopic} Malaysia Higher Education TVET`)}`,
      abstract: `Survey data from 220 industry practitioners reveals how digital literacy, infrastructure readiness, and government subsidies mediate the sustainability of ${query}.`,
      source: "openalex",
      citation_count: 36,
    },
  ];
}

export function getGapsForTopic(topic: string) {
  const t = (topic || "").toLowerCase();
  if (t.includes("tvet") || t.includes("vocational") || t.includes("polytechnic")) {
    return [
      {
        gap_id: "GAP-1",
        description: "While generic TVET graduate employability in Malaysia has been broadly surveyed (P1, P3), empirical research has failed to evaluate instructor competency deficits and equipment readiness for Industry 4.0 automation in regional vocational colleges (P2, P4).",
        supporting_paper_ids: ["P1", "P2", "P4"],
      },
      {
        gap_id: "GAP-2",
        description: "Although national TVET transformation blueprints mandate green skills and sustainability modules (P4), practical work-based learning frameworks integrating renewable energy competencies remain unmodeled in standard technology acceptance literature (P3, P4).",
        supporting_paper_ids: ["P3", "P4"],
      },
      {
        gap_id: "GAP-3",
        description: "Current studies examine tripartite governance between universities and multinational corporations (P3), yet the specific operational friction of SME micro-apprenticeships within East Malaysian TVET centers is unaddressed.",
        supporting_paper_ids: ["P1", "P2"],
      },
    ];
  }

  return [
    {
      gap_id: "GAP-1",
      description: `While general adoption of ${topic || "the topic"} has been explored in metropolitan centers (P1), empirical frameworks fail to account for micro-enterprise trust deficits and operational latency in semi-rural commercial corridors (P2, P4).`,
      supporting_paper_ids: ["P1", "P2", "P4"],
    },
    {
      gap_id: "GAP-2",
      description: `Although national digitization policies promote ${topic || "this field"} (P1, P3), the dual barrier of transaction friction and digital financial illiteracy among traditional enterprises remains unaddressed in standard literature (P3, P5).`,
      supporting_paper_ids: ["P3", "P5"],
    },
    {
      gap_id: "GAP-3",
      description: `Existing literature focuses on short-term implementation transitions (P6), leaving a critical research gap regarding long-term regulatory compliance under Bank Negara Malaysia and institutional guidelines (P9).`,
      supporting_paper_ids: ["P6", "P7", "P9"],
    },
  ];
}

export function getTitlesForTopic(topic: string, gapId: string = "GAP-1") {
  const t = (topic || "").toLowerCase();
  if (t.includes("tvet") || t.includes("vocational") || t.includes("polytechnic")) {
    return [
      {
        title: "Workplace Competency and Technical Skills Readiness for Industry 4.0 in Malaysian TVET Institutions",
        language: "EN",
        gap_id: gapId,
        rationale: "Directly models the intersection of institutional instructor readiness and empirical student competency deficits.",
      },
      {
        title: "Kerangka Penilaian Kompetensi dan Kesediaan Industri 4.0 dalam Kalangan Pelajar Kolej Vokasional Malaysia",
        language: "BM",
        gap_id: gapId,
        rationale: "Sesuai untuk tesis pascasiswazah dalam Bahasa Melayu yang memberi tumpuan kepada kolej vokasional dan politeknik tempatan.",
      },
      {
        title: "A Structural Equation Model of Public-Private Apprenticeship Linkages and Graduate Employability in TVET Institutes",
        language: "EN",
        gap_id: gapId,
        rationale: "Provides quantitative structural modeling for tripartite industrial training partnerships in Johor and Selangor.",
      },
    ];
  }

  const cleanTitle = topic ? topic.replace(/^(empirical analysis of|investigation into)\s+/i, "") : "Digital Innovation";
  return [
    {
      title: `Empirical Analysis of Institutional Readiness and Adoption Barriers in Malaysian ${cleanTitle}`,
      language: "EN",
      gap_id: gapId,
      rationale: "Directly models the theoretical constructs of technology acceptance with empirical data from Malaysian institutions.",
    },
    {
      title: `Analisis Empirikal Cabaran dan Faktor Penerimaan ${cleanTitle} dalam Konteks Institusi Malaysia`,
      language: "BM",
      gap_id: gapId,
      rationale: "Sesuai untuk tesis penyelidikan dalam Bahasa Melayu yang memenuhi piawaian akademik peringkat tinggi.",
    },
    {
      title: `A Moderated Structural Equation Model of Operational Trust and Policy Incentives in ${cleanTitle}`,
      language: "EN",
      gap_id: gapId,
      rationale: "Addresses specific institutional and regulatory friction points identified in recent literature.",
    },
  ];
}

export function getPlanForTopic(title: string, gapId: string = "GAP-1") {
  const isTvet = (title || "").toLowerCase().includes("tvet") || (title || "").toLowerCase().includes("vokasional") || (title || "").toLowerCase().includes("polytechnic");
  
  const objectives = isTvet
    ? [
        {
          objective_id: "RO-1",
          text: "To identify and evaluate the specific curriculum and technological readiness friction points among Kolej Vokasional and Polytechnic instructors.",
        },
        {
          objective_id: "RO-2",
          text: "To construct and empirically validate a structural equation model (PLS-SEM) measuring the impact of digitized workshop instruction on apprentice employability.",
        },
        {
          objective_id: "RO-3",
          text: "To formulate actionable policy and strategic recommendations for the National TVET Council and institutional curriculum directors.",
        },
      ]
    : [
        {
          objective_id: "RO-1",
          text: `To identify and critically evaluate the key adoption barriers and empirical factors impacting ${title}.`,
        },
        {
          objective_id: "RO-2",
          text: "To construct and empirically test an extended structural equation model (PLS-SEM) incorporating institutional readiness.",
        },
        {
          objective_id: "RO-3",
          text: "To formulate actionable policy and strategic recommendations for Malaysian institutional stakeholders and regulatory bodies.",
        },
      ];

  const milestones = [
    {
      milestone_id: "M1",
      title: "Proposal Defense & Theoretical Framework Approval",
      description: "Synthesize literature review, finalize survey instrument and research methodology, and secure departmental committee defense approval.",
      target_month: "Month 3",
    },
    {
      milestone_id: "M2",
      title: "Pilot Testing & Scale Reliability Verification",
      description: "Administer pilot testing with 30 target respondents; establish composite reliability and Cronbach's alpha > 0.70 in SmartPLS.",
      target_month: "Month 5",
    },
    {
      milestone_id: "M3",
      title: "Field Sampling & Computational Modeling",
      description: "Collect empirical cross-sectional data (N=250) from target campuses; perform structural path modeling and hypothesis testing.",
      target_month: "Month 8",
    },
    {
      milestone_id: "M4",
      title: "Thesis Finalization & Oral Defense (Viva Voce)",
      description: "Compile dissertation findings, submit dissertation draft to external examiners, and defend findings before faculty viva board.",
      target_month: "Month 12",
    },
  ];

  const timeline = [
    {
      phase_name: "Phase 1: Conceptual Scoping & Institutional REC Ethics Clearance",
      months: "Months 1–3",
      tasks: [
        "Synthesize comprehensive literature review on Malaysian institutional frameworks",
        "Formulate conceptual model and operationalize indicator constructs",
        "Secure Institutional Human Research Ethics Committee (REC) clearance"
      ]
    },
    {
      phase_name: "Phase 2: Instrument Validation & Pilot Testing",
      months: "Months 4–6",
      tasks: [
        "Develop bilingual (EN/BM) survey questionnaire instrument",
        "Administer pilot test to 30 respondents for reliability verification",
        "Conduct Exploratory Factor Analysis (EFA) and refine scale items"
      ]
    },
    {
      phase_name: "Phase 3: Large-Scale Field Sampling & Computational Modeling",
      months: "Months 7–9",
      tasks: [
        "Execute stratified random sampling across participating campuses",
        "Perform Confirmatory Composite Analysis and PLS-SEM path modeling",
        "Conduct mediation, moderation, and multi-group analysis in SmartPLS 4"
      ]
    },
    {
      phase_name: "Phase 4: Dissertation Finalization & Viva Voce Defense",
      months: "Months 10–12",
      tasks: [
        "Compile empirical findings, discussion, and theoretical contributions",
        "Formulate actionable policy roadmaps for institutional stakeholders",
        "Submit dissertation for examination and conduct oral viva voce defense"
      ]
    }
  ];

  const necessary_resources = [
    {
      category: "Software & Analytical Tools",
      item: "SmartPLS 4 & IBM SPSS Statistics 28",
      justification: "Mandatory for composite reliability, discriminant validity, and structural path coefficient analysis.",
    },
    {
      category: "Institutional Sampling Frame",
      item: isTvet ? "Malaysian Kolej Vokasional & Polytechnic Institutional Directory" : "Malaysian Institutional Participant Registry",
      justification: "Required for stratified random sampling to ensure generalizable and defensible findings.",
    },
    {
      category: "Ethics & Compliance Clearance",
      item: "University Human Research Ethics Committee (REC) Approval",
      justification: "Institutional requirement prior to distributing questionnaires or conducting interviews.",
    },
    {
      category: "Field Research & Sampling Grant",
      item: "Institutional Travel & Sampling Operational Grant",
      justification: "Covers enumerator travel, printed instrument distribution, and respondent honorariums across campuses.",
    }
  ];

  return {
    plan_id: `plan-${Date.now()}`,
    title: title || "Empirical Research Plan on Malaysian Institutional Systems",
    gap_id: gapId,
    version: 1,
    methodology_summary: "A rigorous mixed-methods / PLS-SEM empirical research design adhering to Malaysian thesis standards, structured across 4 deliverable phases.",
    objectives,
    key_milestones: milestones,
    timeline,
    necessary_resources,
  };
}

/**
 * Intelligent Universal Academic Refinement Engine
 * Dynamically parses arbitrary natural language feedback (locations, topics, cohorts,
 * methodologies, sample sizes, durations) and customizes:
 * 1. Working Thesis Title
 * 2. 3 Disciplined SMART Research Objectives (RO-1, RO-2, RO-3)
 * 3. 4 Key Deliverable Milestones (M1 to M4)
 * 4. 4 Execution Timeline Phases (Phases 1 to 4)
 * 5. Resource Allocations & Feasibility Justifications (§ 04)
 */
export function refineResearchPlan(currentPlan: any, prompt: string) {
  const p = (prompt || "").trim();
  const lower = p.toLowerCase();
  const newVersion = (currentPlan?.version || 1) + 1;

  const isTvet =
    lower.includes("tvet") ||
    lower.includes("vokasional") ||
    lower.includes("polytechnic") ||
    (currentPlan?.title || "").toLowerCase().includes("tvet") ||
    (currentPlan?.title || "").toLowerCase().includes("technical");

  // 1. EXTRACT CORE SUBJECT FROM NATURAL CONVERSATION
  // Remove polite preambles and question phrases
  let cleanedSubject = p
    .replace(
      /^(?:please\s+|can\s+you\s+|could\s+you\s+|i\s+(?:want|need|wish|would\s+like)\s+to\s+|my\s+supervisor\s+(?:wants|asked|suggested|told)\s+(?:me\s+)?to\s+|we\s+(?:need|should|want)\s+to\s+|try\s+to\s+|how\s+about\s+|what\s+if\s+we\s+|change\s+(?:to\s+)?|switch\s+(?:to\s+)?|update\s+(?:to\s+)?|add\s+|include\s+|look\s+into\s+|study\s+|investigate\s+|examine\s+|explore\s+|focus(?:ing)?\s+on\s+|concentrate\s+on\s+|emphasize\s+|target(?:ing)?\s+|tailor(?:ed)?\s+to\s+|scoped?\s+to\s+)/i,
      ""
    )
    .replace(/[?.!]+$/, "")
    .trim();

  cleanedSubject = cleanedSubject.replace(/^(?:also\s+|make\s+sure\s+|now\s+|kindly\s+|furthermore\s+)/i, "").trim();

  // 2. GEOGRAPHIC EXTRACTION
  let detectedLocation = "";
  let locInstitutions = "";
  let locStakeholders = "";

  if (
    lower.includes("johor bahru") ||
    lower.includes("jb") ||
    lower.includes("tanjung puteri") ||
    lower.includes("pasir gudang") ||
    lower.includes("iskandar")
  ) {
    detectedLocation = "Johor Bahru";
    locInstitutions = isTvet
      ? "Kolej Vokasional and Polytechnic institutions specifically within Johor Bahru (e.g., KV Tanjung Puteri, KV Perdagangan Johor Bahru, and Politeknik Ibrahim Sultan)"
      : "higher educational institutions located within Johor Bahru and the southern industrial corridor";
    locStakeholders =
      "Johor Bahru vocational directors, Johor State Education Department (JPN Johor), and Southern Industrial Corridor (Iskandar Malaysia/Pasir Gudang) stakeholders";
  } else if (lower.includes("selangor") || lower.includes("shah alam") || lower.includes("klang") || lower.includes("bangi")) {
    detectedLocation = "Selangor";
    locInstitutions = isTvet
      ? "Kolej Vokasional and Polytechnic institutions across Selangor (e.g., KV Shah Alam, KV Klang, and Politeknik Sultan Salahuddin Abdul Aziz Shah)"
      : "higher educational institutions across Selangor";
    locStakeholders =
      "Selangor State Education Department (JPN Selangor) and Klang Valley industrial development councils";
  } else if (lower.includes("johor")) {
    detectedLocation = "Johor State";
    locInstitutions = isTvet
      ? "Kolej Vokasional and Polytechnic institutions across Johor State (e.g., KV Tanjung Puteri, KV Kluang, KV Batu Pahat, and Politeknik Ibrahim Sultan)"
      : "higher educational institutions across Johor State";
    locStakeholders = "Johor State Education Department (JPN Johor) and regional institutional leadership";
  } else if (lower.includes("kuala lumpur") || lower.includes("kl") || lower.includes("putrajaya") || lower.includes("klang valley")) {
    detectedLocation = "Kuala Lumpur & Klang Valley";
    locInstitutions = isTvet
      ? "polytechnic colleges and vocational training institutes across Kuala Lumpur and the Klang Valley"
      : "higher education institutions across the Federal Territory of Kuala Lumpur";
    locStakeholders = "Kuala Lumpur Education Department (JPWPKL) and central federal TVET curriculum committees";
  } else if (lower.includes("penang") || lower.includes("pulau pinang") || lower.includes("bayan lepas") || lower.includes("seberang perai")) {
    detectedLocation = "Penang";
    locInstitutions = isTvet
      ? "Kolej Vokasional and Polytechnic campuses across Penang (including Seberang Perai and Bayan Lepas clusters)"
      : "higher education institutions in Penang";
    locStakeholders = "Penang State Education Department and Penang Skills Development Centre (PSDC) industrial partners";
  } else if (lower.includes("perak") || lower.includes("ipoh") || lower.includes("ungku omar")) {
    detectedLocation = "Perak";
    locInstitutions = isTvet
      ? "technical institutions across Perak (including Politeknik Ungku Omar and KV Ipoh)"
      : "higher education institutions in Perak";
    locStakeholders = "Perak State Education Department and regional industrial skill clusters";
  } else if (lower.includes("melaka") || lower.includes("malacca")) {
    detectedLocation = "Melaka";
    locInstitutions = isTvet
      ? "Kolej Vokasional and technical institutes across Melaka (KV Melaka Tengah, KV Datuk Seri Mohd Zin)"
      : "higher education institutions in Melaka";
    locStakeholders = "Melaka State Education Department and state industrial development boards";
  } else if (lower.includes("kedah") || lower.includes("alor setar") || lower.includes("kulim")) {
    detectedLocation = "Kedah";
    locInstitutions = isTvet
      ? "vocational and polytechnic campuses across Kedah (Politeknik Tuanku Sultanah Bahiyah, Kulim Hi-Tech corridor)"
      : "higher education institutions in Kedah";
    locStakeholders = "Kedah State Education Department and Kulim Hi-Tech Park industrial authorities";
  } else if (lower.includes("pahang") || lower.includes("kuantan")) {
    detectedLocation = "Pahang";
    locInstitutions = isTvet
      ? "vocational institutions across Pahang (Politeknik Sultan Haji Ahmad Shah, KV Kuantan)"
      : "higher education institutions in Pahang";
    locStakeholders = "Pahang State Education Department and East Coast Economic Region (ECER) partners";
  } else if (lower.includes("terengganu") || lower.includes("kelantan")) {
    const stateName = lower.includes("terengganu") ? "Terengganu" : "Kelantan";
    detectedLocation = stateName;
    locInstitutions = isTvet
      ? `technical and vocational colleges across ${stateName}`
      : `higher education institutions in ${stateName}`;
    locStakeholders = `${stateName} State Education Department and East Coast human capital development boards`;
  } else if (lower.includes("sabah") || lower.includes("sarawak") || lower.includes("borneo")) {
    const isSabah = lower.includes("sabah");
    detectedLocation = isSabah ? "Sabah" : "Sarawak";
    locInstitutions = isTvet
      ? `technical and vocational institutions across ${detectedLocation} (including regional technical hubs)`
      : `higher education institutions across ${detectedLocation}`;
    locStakeholders = `${detectedLocation} State Education Department and regional technical human resource advisory panels`;
  }

  // 3. TARGET COHORT / DEMOGRAPHIC DETECTION
  let cohortName = "";
  if (lower.includes("b40") || lower.includes("low-income") || lower.includes("low income") || lower.includes("underprivileged")) {
    cohortName = "B40 and economically disadvantaged student cohorts";
  } else if (lower.includes("female") || lower.includes("women") || lower.includes("gender")) {
    cohortName = "female technical trainees and women in engineering/vocational tracks";
  } else if (lower.includes("lecturer") || lower.includes("teacher") || lower.includes("instructor") || lower.includes("faculty")) {
    cohortName = "technical vocational educators, instructors, and curriculum heads";
  } else if (lower.includes("industry") || lower.includes("employer") || lower.includes("partner") || lower.includes("supervisor")) {
    cohortName = "industrial supervisors, internship mentors, and technical employers";
  } else if (lower.includes("sme") || lower.includes("micro")) {
    cohortName = "Malaysian SME micro-enterprise operators and local merchants";
  } else {
    cohortName = isTvet ? "Kolej Vokasional and Polytechnic trainees and educators" : "higher education student cohorts and academic personnel";
  }

  // 4. SAMPLE SIZE DETECTION (e.g. 400 respondents, N=350, 30 experts)
  const sampleMatch = p.match(/(?:sample\s+(?:size\s+)?(?:of\s+)?|n\s*=\s*|with\s+)(\d{2,4})\s*(?:respondents|participants|teachers|lecturers|students|experts|users|firms|enterprises|cases)?/i);
  const customSampleSize = sampleMatch ? parseInt(sampleMatch[1], 10) : null;

  // 5. METHODOLOGY & ANALYTICAL TOOLS DETECTION
  let methodType = "quantitative";
  let methodologyText = "";
  let toolsText = "SmartPLS 4 & IBM SPSS Statistics 28";
  let pilotMethodDesc = "";
  let fieldMethodDesc = "";

  const isQualitative =
    lower.includes("qualitative") ||
    lower.includes("interview") ||
    lower.includes("focus group") ||
    lower.includes("thematic") ||
    lower.includes("grounded theory") ||
    lower.includes("phenomenolog");

  const isDelphi = lower.includes("delphi") || lower.includes("expert consensus");
  const isMachineLearning =
    lower.includes("machine learning") ||
    lower.includes("ai model") ||
    lower.includes("predictive algorithm") ||
    lower.includes("deep learning") ||
    lower.includes("neural network");

  const isExperimental =
    lower.includes("experiment") ||
    lower.includes("quasi-experiment") ||
    lower.includes("pre-test") ||
    lower.includes("intervention study");

  if (isQualitative) {
    methodType = "qualitative";
    toolsText = "NVivo 14, Atlas.ti 23 & IBM SPSS 28";
    methodologyText =
      "To construct and empirically validate a qualitative/mixed-methods framework integrating in-depth semi-structured expert interviews with construct saturation";
    const nInterviews = customSampleSize || 25;
    pilotMethodDesc = "Administer pilot interview protocol with 6–8 domain educators to verify semi-structured interview schedule fidelity.";
    fieldMethodDesc = `Conduct in-depth qualitative fieldwork collecting ${nInterviews} expert interview transcripts; establish thematic saturation and inter-coder reliability in NVivo 14.`;
  } else if (isDelphi) {
    methodType = "delphi";
    toolsText = "Qualtrics, SmartPLS 4 & IBM SPSS Statistics 28";
    methodologyText =
      "To formulate and empirically validate a multi-round modified Delphi consensus framework measuring convergence among academic and industrial panels";
    const nExperts = customSampleSize || 30;
    pilotMethodDesc = "Conduct Round 1 exploratory qualitative scoping with 12 panel experts; establish consensus indicator thresholds.";
    fieldMethodDesc = `Administer Rounds 2 & 3 Delphi questionnaires across panel experts (N=${nExperts}); verify consensus stability (Kendall's W > 0.70).`;
  } else if (isMachineLearning) {
    methodType = "machine_learning";
    toolsText = "Python 3.12 (Scikit-Learn, PyTorch), SmartPLS 4 & Jupyter Studio";
    methodologyText =
      "To construct, train, and empirically benchmark computational predictive machine learning models alongside structural equation modeling (PLS-SEM)";
    const nRecords = customSampleSize || 350;
    pilotMethodDesc = "Pre-process dataset, execute exploratory feature engineering, and run cross-validated hyperparameter tuning.";
    fieldMethodDesc = `Train and evaluate predictive models on empirical cohort dataset (N=${nRecords}); benchmark classification accuracy, ROC-AUC, and PLS-SEM path coefficients.`;
  } else if (isExperimental) {
    methodType = "experimental";
    toolsText = "G*Power 3.1, IBM SPSS Statistics 28 & SmartPLS 4";
    methodologyText =
      "To design and empirically execute a quasi-experimental pre-test/post-test evaluation measuring pedagogical interventions and performance gains";
    const nCohort = customSampleSize || 160;
    pilotMethodDesc = "Execute pilot instructional trial with 20 participants to calibrate intervention modules and assessment rubrics.";
    fieldMethodDesc = `Administer controlled quasi-experimental intervention across treatment and control cohorts (N=${nCohort}); evaluate ANCOVA and path effect sizes.`;
  } else {
    methodType = "quantitative";
    toolsText = "SmartPLS 4 & IBM SPSS Statistics 28";
    methodologyText =
      "To construct and empirically test an extended structural equation model (PLS-SEM) measuring the predictive relationships between institutional readiness, digital competency, and curriculum modernizations";
    const nSurvey = customSampleSize || 250;
    pilotMethodDesc = "Administer pilot survey with 30 target respondents; establish composite reliability and Cronbach's alpha > 0.70 in SmartPLS 4.";
    fieldMethodDesc = `Collect empirical cross-sectional data (N=${nSurvey}) from target institutions; perform path coefficient estimation, mediation, and hypothesis testing in SmartPLS 4.`;
  }

  // 6. TIMELINE & DURATION ADAPTATION
  const isShortened = lower.includes("shorten") || lower.includes("reduce") || lower.includes("6 month") || lower.includes("fast track") || lower.includes("accelerat");
  const is9Month = lower.includes("9 month");
  const isExtended = lower.includes("18 month") || lower.includes("24 month") || lower.includes("2 year") || lower.includes("extend") || lower.includes("part-time");

  const mTarget1 = isShortened ? "Month 2" : is9Month ? "Month 2" : isExtended ? "Month 4" : "Month 3";
  const mTarget2 = isShortened ? "Month 4" : is9Month ? "Month 4" : isExtended ? "Month 7" : "Month 5";
  const mTarget3 = isShortened ? "Month 5" : is9Month ? "Month 7" : isExtended ? "Month 13" : "Month 8";
  const mTarget4 = isShortened ? "Month 6" : is9Month ? "Month 9" : isExtended ? "Month 18" : "Month 12";

  const pMonths1 = isShortened ? "Months 1–2" : is9Month ? "Months 1–2" : isExtended ? "Months 1–4" : "Months 1–3";
  const pMonths2 = isShortened ? "Months 3–4" : is9Month ? "Months 3–4" : isExtended ? "Months 5–7" : "Months 4–6";
  const pMonths3 = isShortened ? "Month 5" : is9Month ? "Months 5–7" : isExtended ? "Months 8–13" : "Months 7–9";
  const pMonths4 = isShortened ? "Month 6" : is9Month ? "Months 8–9" : isExtended ? "Months 14–18" : "Months 10–12";

  // 7. ASSEMBLE TARGET SCOPE & DOMAIN LABELS
  const targetScope = locInstitutions || (
    isTvet
      ? `Malaysian Kolej Vokasional and technical training institutions (${cohortName})`
      : `Malaysian higher education institutions (${cohortName})`
  );

  const targetScopeShort = detectedLocation
    ? `${detectedLocation} technical and educational campuses`
    : (isTvet ? "Malaysian TVET and technical institutions" : "participating higher education campuses");

  const stakeholderScope = locStakeholders || (
    isTvet
      ? "Malaysian vocational directors, Technical & Vocational Education Division (BPLTV), and industry advisory councils"
      : "Malaysian higher educational directors, MOHE, and curriculum stakeholders"
  );

  // 8. TOPIC / SUBJECT TITLE AND BADGE
  // Formulate a clean, professional title addition
  let topicFocus = cleanedSubject || detectedLocation || "Curriculum Modernization & Technical Competency";
  if (topicFocus.length > 55) {
    topicFocus = topicFocus.substring(0, 52) + "...";
  }
  const formattedFocus = topicFocus.charAt(0).toUpperCase() + topicFocus.slice(1);

  let scopeBadge = detectedLocation || formattedFocus;
  if (isShortened && !detectedLocation) scopeBadge = "Accelerated (6-Month)";
  if (isQualitative && !detectedLocation) scopeBadge = "Qualitative Study";
  if (isDelphi && !detectedLocation) scopeBadge = "Delphi Consensus";
  if (isMachineLearning && !detectedLocation) scopeBadge = "Machine Learning Modeling";

  const rawBaseTitle = currentPlan?.title || "TVET Curriculum & Skill Modernization in Malaysian Technical Institutions";
  const baseTitle = rawBaseTitle.replace(/\s*:\s*(An Empirical Study|A Case Study|Focus on|Accelerated|A Qualitative|Investigating).*$/i, "");
  
  let updatedTitle = baseTitle;
  if (detectedLocation && !baseTitle.toLowerCase().includes(detectedLocation.toLowerCase())) {
    updatedTitle = `${baseTitle}: An Empirical Study in ${detectedLocation}`;
  } else if (cleanedSubject && !baseTitle.toLowerCase().includes(cleanedSubject.toLowerCase())) {
    updatedTitle = `${baseTitle}: Focus on ${formattedFocus}`;
  } else if (isQualitative) {
    updatedTitle = `${baseTitle}: A Qualitative Empirical Investigation`;
  } else if (isShortened) {
    updatedTitle = `${baseTitle}: Accelerated 6-Month Execution`;
  }

  // 9. DYNAMIC 3 SMART OBJECTIVES (RO-1, RO-2, RO-3)
  const objectives = [
    {
      objective_id: "RO-1",
      text: `To identify, evaluate, and prioritize the key empirical factors and operational barriers impacting ${topicFocus} within ${targetScope}.`,
    },
    {
      objective_id: "RO-2",
      text: `${methodologyText} focusing on ${topicFocus} within ${targetScopeShort}.`,
    },
    {
      objective_id: "RO-3",
      text: `To formulate actionable institutional policy frameworks and strategic implementation roadmaps for ${stakeholderScope} to foster sustainable ${topicFocus} advancements.`,
    },
  ];

  // 10. KEY DELIVERABLE MILESTONES (M1 to M4)
  const milestones = [
    {
      milestone_id: "M1",
      title: "Proposal Defense & Theoretical Framework Approval",
      description: `Synthesize systematic literature review on ${topicFocus}, operationalize theoretical construct items for ${targetScopeShort}, and secure departmental committee defense approval.`,
      target_month: mTarget1,
    },
    {
      milestone_id: "M2",
      title: "Instrument Validation & Pilot Verification",
      description: `${pilotMethodDesc} Tailored specifically to ${targetScopeShort}.`,
      target_month: mTarget2,
    },
    {
      milestone_id: "M3",
      title: "Field Sampling & Computational Modeling",
      description: `${fieldMethodDesc} Targeting ${targetScopeShort}.`,
      target_month: mTarget3,
    },
    {
      milestone_id: "M4",
      title: "Thesis Submission & Oral Viva Voce Defense",
      description: `Compile dissertation findings, submit draft addressing policy implications for ${stakeholderScope} to external examiners, and defend thesis before faculty viva board.`,
      target_month: mTarget4,
    },
  ];

  // 11. TIMELINE PHASES (Phases 1 to 4)
  const timeline = [
    {
      phase_name: `Phase 1: Conceptual Scoping & REC Ethics Approval (${pMonths1})`,
      months: pMonths1,
      tasks: [
        `Conduct systematic literature review focusing on ${topicFocus} in Malaysian institutions`,
        `Operationalize indicator scales and theoretical construct items tailored to ${targetScopeShort}`,
        "Obtain Human Research Ethics Committee (REC) and EPRD KPM compliance approvals",
      ],
    },
    {
      phase_name: `Phase 2: Instrument Validation & Pilot Pre-testing (${pMonths2})`,
      months: pMonths2,
      tasks: [
        `Distribute pilot instrument to target cohort respondents across ${targetScopeShort}`,
        `Execute measurement model verification, convergent validity, and reliability in ${toolsText}`,
        "Refine survey items, interview prompts, and protocols based on pilot participant feedback",
      ],
    },
    {
      phase_name: `Phase 3: Field Data Collection & Analytical Modeling (${pMonths3})`,
      months: pMonths3,
      tasks: [
        `Administer primary data collection across participating campuses in ${targetScopeShort}`,
        `Perform Confirmatory Composite Analysis and empirical structural modeling in ${toolsText}`,
        "Conduct mediation, moderation, robustness checks, or cross-validation benchmarking",
      ],
    },
    {
      phase_name: `Phase 4: Thesis Dissertation Compilation & Viva Defense (${pMonths4})`,
      months: pMonths4,
      tasks: [
        "Write up empirical findings, theoretical contributions, and managerial implications",
        `Formulate localized institutional policy roadmaps for ${stakeholderScope}`,
        "Formal thesis submission and oral examination (Viva Voce)",
      ],
    },
  ];

  // 12. RESOURCE REQUIREMENTS & FEASIBILITY (§ 04)
  const necessary_resources = [
    {
      category: "Software & Analytical Tools",
      item: toolsText,
      justification: `Mandatory for computational modeling, empirical hypothesis testing, and rigorous analytical evaluation of ${topicFocus}.`,
    },
    {
      category: "Institutional Sampling Frame",
      item: `Institutional Directory & Sampling Registry for ${targetScopeShort}`,
      justification: `Sampling frame required to conduct stratified random sampling across participating cohorts in ${targetScopeShort}.`,
    },
    {
      category: "Ethics & Compliance Clearance",
      item: "Institutional Human Research Ethics Committee (REC) Approval & EPRD Clearance",
      justification: `Mandatory prior to administering questionnaires or conducting interviews with institutional personnel in ${targetScopeShort}.`,
    },
    {
      category: "Field Research Grant",
      item: `Fieldwork & Travel Operational Grant (${detectedLocation || "Campus Network"})`,
      justification: `Covers fieldwork expenses, local campus travel across ${targetScopeShort}, and participant remuneration tokens.`,
    },
  ];

  return {
    ...currentPlan,
    title: updatedTitle,
    scope_focus: scopeBadge,
    version: newVersion,
    methodology_summary: `Refined Research Architecture (v${newVersion}) tailored to: "${p}". Maintains 3 disciplined SMART objectives, synchronized milestones, full timeline, and institutional resource allocations specifically aligned with ${scopeBadge}.`,
    objectives,
    key_milestones: milestones,
    timeline,
    necessary_resources,
  };
}

export const INITIAL_DEMO_PROJECTS = [
  {
    id: "proj-demo-101",
    tenant_id: "tenant-demo-002",
    user_id: "usr-student",
    title: "Empirical Analysis of Cybersecurity Trust Deficits in QR-Based Mobile Payment Adoption Among Semi-Rural Malaysian Micro-Enterprises",
    stage: "plan",
    state_json: {
      topic: "Malaysian SME Cashless Payment Adoption",
      scope: "MY",
      papers: DEMO_SEARCH_PAPERS,
      gaps: getGapsForTopic("e-wallet"),
      chosen_gap: getGapsForTopic("e-wallet")[0],
      titles: getTitlesForTopic("e-wallet"),
      chosen_title: getTitlesForTopic("e-wallet")[0].title,
      deepdive_papers: DEMO_SEARCH_PAPERS.slice(0, 4),
      plan: getPlanForTopic("Empirical Analysis of Cybersecurity Trust Deficits in QR-Based Mobile Payment Adoption Among Semi-Rural Malaysian Micro-Enterprises"),
    },
    current_plan_json: getPlanForTopic("Empirical Analysis of Cybersecurity Trust Deficits in QR-Based Mobile Payment Adoption Among Semi-Rural Malaysian Micro-Enterprises"),
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date().toISOString(),
  },
];
