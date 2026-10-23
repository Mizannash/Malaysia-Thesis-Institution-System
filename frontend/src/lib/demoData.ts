/**
 * Client-Side Demo Data & Offline Engine for MTIS
 * Enables 100% full-featured demonstration on Netlify / preview hosting
 * when the Python/PostgreSQL backend is not running or unreachable.
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

export const DEMO_GAPS = [
  {
    gap_id: "GAP-1",
    description: "While general e-wallet adoption in Malaysian urban centers has been extensively modeled via UTAUT2 (P1), existing empirical frameworks fail to account for specific micro-merchant cybersecurity trust deficits and QR tampering vulnerabilities in semi-rural commercial corridors (P2, P4).",
    supporting_paper_ids: ["P1", "P2", "P4"],
  },
  {
    gap_id: "GAP-2",
    description: "Although national fintech digitization policies subsidize merchant acquisition (P1, P3), the dual barrier of Merchant Discount Rate (MDR) transaction fees and digital financial illiteracy among traditional family-run grocers in East Malaysia remains unaddressed in standard technology acceptance literature (P3, P5).",
    supporting_paper_ids: ["P3", "P5"],
  },
  {
    gap_id: "GAP-3",
    description: "Current literature investigates post-pandemic operational transitions for urban F&B micro-enterprises (P6) and Shariah compliance perception in digital wallets (P7), yet there is a critical gap evaluating how BNM regulatory compliance requirements (P9) constrain Islamic fintech feature innovation for rural micro-retailers.",
    supporting_paper_ids: ["P6", "P7", "P9"],
  },
];

export const DEMO_TITLES = [
  {
    title: "Empirical Analysis of Cybersecurity Trust Deficits in QR-Based Mobile Payment Adoption Among Semi-Rural Malaysian Micro-Enterprises",
    language: "EN",
    gap_id: "GAP-1",
    rationale: "Directly models the intersection of UTAUT2 performance expectancy and perceived cyber-fraud risks in non-metropolitan commercial zones.",
  },
  {
    title: "Analisis Empirikal Halangan Keselamatan Siber dan Kepercayaan Peniaga Mikro Terhadap Penggunaan E-Dompet di Johor",
    language: "BM",
    gap_id: "GAP-1",
    rationale: "Sesuai untuk tesis pascasiswazah dalam Bahasa Melayu yang memberi tumpuan kepada peniaga mikro di koridor perniagaan Johor.",
  },
  {
    title: "A Moderated Structural Equation Model of Merchant Discount Rates and Digital Financial Literacy on Cashless Persistence in Sabah",
    language: "EN",
    gap_id: "GAP-1",
    rationale: "Addresses the specific economic friction of transaction costs versus policy incentives in East Malaysian MSMEs.",
  },
];

export const DEMO_PLAN = {
  plan_id: "plan-utm-101",
  title: "Empirical Analysis of Cybersecurity Trust Deficits in QR-Based Mobile Payment Adoption Among Semi-Rural Malaysian Micro-Enterprises",
  gap_id: "GAP-1",
  version: 1,
  objectives: [
    {
      objective_id: "RO-1",
      text: "To identify and evaluate the specific cybersecurity trust barriers and fraud vulnerabilities impacting semi-rural micro-merchants in Johor.",
    },
    {
      objective_id: "RO-2",
      text: "To develop and empirically test an extended UTAUT2 structural model incorporating perceived transaction risk and merchant discount rate frictions.",
    },
    {
      objective_id: "RO-3",
      text: "To formulate actionable policy and technical recommendations for Bank Negara Malaysia (BNM) and fintech payment operators.",
    },
  ],
  key_milestones: [
    {
      milestone_id: "M1",
      title: "Proposal Defense & Theoretical Framework Approval",
      description: "Synthesize literature review, finalize survey instrument, and present to faculty defense committee.",
      target_month: "Month 3",
    },
    {
      milestone_id: "M2",
      title: "Pilot Study & Instrument Validation",
      description: "Administer pilot questionnaire to 30 micro-retailers in Iskandar Malaysia; test Cronbach's alpha and composite reliability.",
      target_month: "Month 5",
    },
    {
      milestone_id: "M3",
      title: "Field Data Collection & SEM Modeling",
      description: "Collect complete cross-sectional data from 250 SME merchants across Johor commercial corridors; conduct PLS-SEM analysis in SmartPLS.",
      target_month: "Month 8",
    },
    {
      milestone_id: "M4",
      title: "Thesis Submission & Viva Voce",
      description: "Finalize thesis chapters, submit dissertation draft for examiner review, and defend in oral examination.",
      target_month: "Month 12",
    },
  ],
  necessary_resources: [
    {
      category: "Software & Analytical Tools",
      item: "SmartPLS 4 & SPSS Statistics 28",
      justification: "Required for structural equation modeling, indicator loadings, and mediation testing.",
    },
    {
      category: "Data & Institutional Access",
      item: "Johor SME Association Merchant Registry",
      justification: "Sampling frame access for stratified random sampling of retail micro-enterprises.",
    },
    {
      category: "Regulatory & Ethics",
      item: "Institutional Human Research Ethics Clearance (UTM REC)",
      justification: "Mandatory prior to field survey distribution involving small business proprietors.",
    },
  ],
};

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
      gaps: DEMO_GAPS,
      chosen_gap: DEMO_GAPS[0],
      titles: DEMO_TITLES,
      chosen_title: DEMO_TITLES[0].title,
      deepdive_papers: DEMO_SEARCH_PAPERS.slice(0, 4),
      plan: DEMO_PLAN,
    },
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date().toISOString(),
  },
];
