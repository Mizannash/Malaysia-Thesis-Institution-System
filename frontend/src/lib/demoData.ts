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
    doi: "10.11113/mjitcs.v15n3.99104",
    url: "https://doi.org/10.11113/mjitcs.v15n3.99104",
    abstract: "This empirical study investigates the alignment between technical curriculum delivery in Malaysian polytechnics and Industry 4.0 competency requirements of advanced manufacturing employers in Johor and Selangor. Using structural equation modeling on data collected from 180 industrial training coordinators and 320 diploma apprentices, critical skill gaps in automation and industrial IoT troubleshooting were identified.",
    source: "openalex",
    citation_count: 27,
  },
  {
    title: "Digital Transformation Challenges in Malaysian Vocational Colleges (Kolej Vokasional): Instructor Readiness and Curriculum Friction",
    authors: ["Siti Aminah Kassim", "Faridah Othman"],
    year: 2024,
    doi: "10.11113/jt.v86.93201",
    url: "https://doi.org/10.11113/jt.v86.93201",
    abstract: "Malaysian TVET institutions face rapid shifts towards digitized workshop instruction. Drawing upon the Technology Acceptance Model (TAM), this study evaluates technological readiness and institutional barriers among 210 vocational instructors across Selangor and Perak.",
    source: "openalex",
    citation_count: 19,
  },
  {
    title: "Public-Private Partnerships in Technical and Vocational Education Training (TVET): Enhancing Graduate Employability in Southern Malaysia",
    authors: ["Tan Boon Kiat", "Kamarul Zaman"],
    year: 2023,
    doi: "10.1016/j.chb.2023.108442",
    url: "https://doi.org/10.1016/j.chb.2023.108442",
    abstract: "Analyzing tripartite governance between the Ministry of Higher Education, state skill development centers, and multinational engineering firms. Mixed-methods findings demonstrate a 34% increase in permanent technical job placements under structured work-based learning schemes.",
    source: "utm",
    citation_count: 31,
  },
  {
    title: "Green Skills Integration in Malaysian TVET Curricula: Perceptions of Engineering Technology Students and Industry Stakeholders",
    authors: ["Harpreet Kaur", "Muhammad Arif Ismail"],
    year: 2022,
    doi: "10.1108/JFM-04-2022-0044",
    url: "https://doi.org/10.1108/JFM-04-2022-0044",
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
    doi: "10.11113/mjitcs.v15n2.98124",
    url: "https://doi.org/10.11113/mjitcs.v15n2.98124",
    abstract: "This study examines the behavioral intentions of Malaysian SMEs toward continuous adoption of digital e-wallets. Using an extended UTAUT2 model incorporating transaction security and government subsidies under the Malaysia Digital Economy Blueprint.",
    source: "openalex",
    citation_count: 34,
  },
  {
    title: "Cybersecurity Vulnerabilities and Consumer Trust in Malaysian Cashless Payment Ecosystems",
    authors: ["Wei Lun Tan", "Mohd Hashim Ibrahim"],
    year: 2022,
    doi: "10.11113/jt.v84.92305",
    url: "https://doi.org/10.11113/jt.v84.92305",
    abstract: "Digital payment solutions have surged across urban Malaysian commercial centers. However, fraud vectors, unauthorized micro-transactions, and QR code tampering remain key obstacles for small micro-merchants.",
    source: "openalex",
    citation_count: 21,
  },
  {
    title: "Digital Transformation Challenges of Malaysian MSMEs: An Empirical Study of Touch 'n Go and GrabPay Integration",
    authors: ["Faridah Othman", "Kamarul Zaman", "Cheng Hock Lee"],
    year: 2023,
    doi: "10.1016/j.chb.2023.107890",
    url: "https://doi.org/10.1016/j.chb.2023.107890",
    abstract: "The post-pandemic digitization push accelerated cashless adoption among Malaysian micro, small, and medium enterprises. This paper analyzes technological and financial barriers faced by 450 merchants in Kuala Lumpur and Penang.",
    source: "openalex",
    citation_count: 48,
  },
  {
    title: "DuitNow QR Adoption Factors in Rural Malaysian Traditional Retailers: A TOE Framework Analysis",
    authors: ["Muhammad Arif Ismail", "Noraini Mat"],
    year: 2024,
    doi: "10.1108/JFM-08-2023-0091",
    url: "https://doi.org/10.1108/JFM-08-2023-0091",
    abstract: "Drawing on the Technology-Organization-Environment (TOE) framework, this research evaluates national interoperable QR code integration among rural grocery merchants across Pahang and Kelantan.",
    source: "openalex",
    citation_count: 12,
  },
  {
    title: "Mobile Payment System Architecture and Compliance with Bank Negara Malaysia Regulatory Framework",
    authors: ["Norhayati Sulaiman"],
    year: 2021,
    doi: "10.11113/englet.v30.89100",
    url: "https://doi.org/10.11113/englet.v30.89100",
    abstract: "Architectural analysis of payment gateway latency, compliance requirements under the Financial Services Act 2013, and customer authentication protocols.",
    source: "utm",
    citation_count: 16,
  },
  {
    title: "Fintech Adoption In Retail Food and Beverage Micro-Enterprises Across Johor Southern Corridor",
    authors: ["Harpreet Kaur", "Zalina Yusof"],
    year: 2023,
    doi: "10.11113/utmpj.v19n1.101452",
    url: "https://doi.org/10.11113/utmpj.v19n1.101452",
    abstract: "Investigating operational transitions from physical cash handling to DuitNow QR and Touch 'n Go eWallet platforms during post-pandemic recovery among hawkers in Iskandar Malaysia.",
    source: "utm",
    citation_count: 15,
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

  // Dynamic academic fallback for arbitrary user topics
  const capTopic = query.trim().split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  return [
    {
      title: `Empirical Assessment of ${capTopic} Adoption in Malaysian Higher Education Institutions`,
      authors: ["Mohd Syazwan", "Nurul Hidayah"],
      year: 2023,
      doi: `10.11113/mjitcs.v15n2.${Math.floor(10000 + Math.random() * 90000)}`,
      url: "https://doi.org/10.11113/mjitcs.v15n2.example",
      abstract: `This study examines institutional readiness, behavioral intentions, and policy friction surrounding ${query} across Malaysian campuses, using an extended technology acceptance framework.`,
      source: "openalex",
      citation_count: 24,
    },
    {
      title: `Implementation Challenges and Regulatory Compliance of ${capTopic} Across Malaysian Public Universities`,
      authors: ["Zalina Ahmad", "Kamarul Zaman"],
      year: 2024,
      doi: `10.11113/jt.v86.${Math.floor(10000 + Math.random() * 90000)}`,
      url: "https://doi.org/10.11113/jt.v86.example",
      abstract: `Investigating governance models, resource allocation constraints, and stakeholder perspectives in deploying ${query} solutions within regional academic centers.`,
      source: "utm",
      citation_count: 18,
    },
    {
      title: `A Mixed-Methods Investigation into ${capTopic} for Regional Industry Competitiveness in Peninsular Malaysia`,
      authors: ["Ahmad Razak", "Faridah Othman"],
      year: 2023,
      doi: `10.1016/j.chb.2023.${Math.floor(10000 + Math.random() * 90000)}`,
      url: "https://doi.org/10.1016/j.chb.2023.example",
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
  return {
    plan_id: `plan-${Date.now()}`,
    title: title || "Empirical Research Plan on Malaysian Institutional Systems",
    gap_id: gapId,
    version: 1,
    objectives: [
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
    ],
    key_milestones: [
      {
        milestone_id: "M1",
        title: "Proposal Defense & Theoretical Framework Approval",
        description: "Synthesize literature review, finalize survey instrument/methodology, and defend before faculty committee.",
        target_month: "Month 3",
      },
      {
        milestone_id: "M2",
        title: "Pilot Testing & Instrument Reliability Verification",
        description: "Administer pilot questionnaire to 30 sample respondents; test Cronbach's alpha and indicator loadings in SmartPLS.",
        target_month: "Month 5",
      },
      {
        milestone_id: "M3",
        title: "Field Data Collection & Structural Equation Modeling",
        description: "Collect cross-sectional data from 250 verified participants; perform full hypothesis testing and path analysis.",
        target_month: "Month 8",
      },
      {
        milestone_id: "M4",
        title: "Thesis Finalization & Oral Defense (Viva Voce)",
        description: "Complete all thesis chapters, submit dissertation to external examiners, and defend findings in viva voce.",
        target_month: "Month 12",
      },
    ],
    necessary_resources: [
      {
        category: "Software & Analytical Tools",
        item: "SmartPLS 4 & IBM SPSS Statistics 28",
        justification: "Mandatory for composite reliability, discriminant validity, and structural path coefficient analysis.",
      },
      {
        category: "Institutional Sampling Frame",
        item: "Malaysian Institutional Participant Registry",
        justification: "Required for stratified random sampling to ensure generalizable and defensible findings.",
      },
      {
        category: "Ethics & Compliance Clearance",
        item: "University Human Research Ethics Committee (REC) Approval",
        justification: "Institutional requirement prior to distributing questionnaires or conducting interviews.",
      },
    ],
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
