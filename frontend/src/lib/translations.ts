/**
 * Bilingual Translations Dictionary (Bahasa Malaysia & English)
 * Adheres to standard academic terminology used in Malaysian universities (UTM, UM, UKM, USM).
 */

export type Language = "en" | "bm";

export const translations = {
  en: {
    // Navbar & Common
    app_name: "ScholarPulse MTIS",
    app_badge: "Academic Coach v2.4",
    nav_pricing: "Pricing (RM15/mo)",
    nav_signin: "Sign In",
    nav_launch: "Launch App",
    nav_dashboard: "Go to Dashboard",
    nav_back_dashboard: "Back to Dashboard",
    nav_signout: "Sign Out",
    nav_admin: "Admin Center",
    nav_workspace: "Thesis Workspace",
    nav_subscriptions: "Subscriptions",
    nav_demo_badge: "Zero-Key Demo Active",
    lang_toggle_label: "Language",

    // Home Page
    hero_badge: "Higher Education Research Intelligence",
    hero_title: "Find Novel Research Gaps for Your Malaysian Thesis",
    hero_subtitle:
      "Empowers Malaysian diploma, degree, and postgraduate researchers to identify defensible literature gaps, formulate defended titles in English & BM, and draft multi-objective research plans backed by institutional citations.",
    hero_cta_demo: "Get Started with Zero Keys",
    hero_cta_pricing: "View Student Pricing (RM15/mo)",
    feat_1_title: "Institutional Repositories",
    feat_1_desc: "Direct integration with Malaysian university archives and global OpenAlex corpus.",
    feat_2_title: "Novel Gap Detection",
    feat_2_desc: "Discover unaddressed empirical and theoretical gaps to defend your thesis originality.",
    feat_3_title: "Multi-Tenant Isolation",
    feat_3_desc: "Institutional data protection ensuring individual researchers and campuses stay private.",

    // Login Page
    login_title: "Sign in to MTIS",
    login_subtitle: "Institutional Thesis Structuring & Research Gap Discovery",
    login_google_btn: "Continue with Google (Coming Soon)",
    login_google_hint: "Google Sign-In will be available after deployment. Use demo personas below.",
    login_or_divider: "OR TEST PERSONAS (DEMO MODE)",
    login_student_section: "RESEARCHER / STUDENT ACCESS",
    login_admin_section: "SYSTEM OWNER / ADMIN ACCESS",
    login_demo_uni: "Demo University Researcher",
    login_utm_ahmad: "UTM Researcher (Ahmad)",
    login_admin_owner: "System Admin (Owner)",
    login_coach_note:
      "MTIS isolates research workspaces by institutional tenant. Selecting any demo persona simulates verified campus access.",

    // Dashboard
    dash_stage1_title: "1. Topic Search",
    dash_stage1_sub: "OpenAlex & UTM Index",
    dash_stage2_title: "2. Gap Analysis",
    dash_stage2_sub: "Novel Gap Discovery",
    dash_stage3_title: "3. Title Suggestions",
    dash_stage3_sub: "Defended EN/BM Titles",
    dash_stage4_title: "4. Deep-Dive Search",
    dash_stage4_sub: "Targeted Sub-field Papers",
    dash_stage5_title: "5. Research Plan",
    dash_stage5_sub: "Objectives & Methodology",

    dash_stage1_header: "Stage 1: Topic Literature Search & Article Discovery",
    dash_stage1_desc:
      "Query Malaysian university e-prints (UTM E-Theses) & global peer-reviewed repositories (OpenAlex).",
    dash_scope_my: "Malaysian (UTM & MY)",
    dash_scope_int: "Global (OpenAlex)",
    dash_search_placeholder: "e.g. tvet, e-wallet, IoT smart agriculture, blockchain...",
    dash_btn_search: "Search Articles",
    dash_searching: "Searching Repositories...",
    dash_btn_gap: "Run Stage 2: Gap Analysis",
    dash_btn_title: "Run Stage 3: Title Suggestions",
    dash_btn_deepdive: "Run Stage 4: Deep-Dive",
    dash_btn_plan: "Run Stage 5: Research Plan",
    dash_open_canvas: "Open Plan Canvas",

    dash_quota_badge: "Daily AI Quota",
    dash_refill_btn: "Refill Quota",
    dash_settings_btn: "API Key Settings",
    dash_tenant_title: "Tenant Isolation",
    dash_coach_title: "Academic Coach Assistant",
    dash_coach_topics: "QUICK EXPLORATION TOPICS:",
    dash_coach_prompt_ph: "Ask Coach or search topic...",

    // Plan Studio (/plan)
    plan_title: "Objectives, Methodology & Computational Execution",
    plan_badge: "Contract Hardened",
    plan_sec1_title: "Primary Research Objectives",
    plan_sec2_title: "Key Deliverable Milestones",
    plan_sec3_title: "High-Level Timeline & Phases",
    plan_sec4_title: "Resource Requirements & Feasibility",
    plan_refine_title: "Refine with Coach",
    plan_refine_desc:
      'Provide feedback to iterate on objectives, methodology, or resources (e.g. "Focus more on Malaysian SMEs" or "Shorten timeline to 18 months").',
    plan_prompt_label: "FEEDBACK PROMPT",
    plan_prompt_ph: "e.g. Focus on Kolej Vokasional campuses in Selangor and Johor...",
    plan_btn_refine: "Submit Refinement",
    plan_refining: "Applying Refinement...",
    plan_vc_title: "Version Control Note",
    plan_vc_desc:
      "Refinements re-synthesize the 3 core SMART objectives, synchronize delivery milestones, and update institutional resources.",

    // Pricing Page
    price_title: "Fair, Student-Friendly Pricing",
    price_subtitle:
      "Tailored specifically for Malaysian diploma, degree, and postgraduate researchers. Replace expensive manual tools with an institutional AI thesis guide.",
    price_free_title: "Student Explorer",
    price_free_desc: "Everything needed to start scoping a topic and finding genuine literature gaps.",
    price_free_quota: "3 Gap Analyses per day (resets daily)",
    price_pro_title: "Postgraduate Pro",
    price_pro_desc: "Unrestricted multi-stage analysis, bilingual title defense, and automated LaTeX plan export.",
    price_pro_quota: "99 AI Research Queries / month",
    price_free_cta: "Start Free Trial",
    price_pro_cta: "Upgrade to Pro",
    price_recommended: "RECOMMENDED",
    price_economics_title: "Business Model & Unit Economics (D1 Evidence)",
    price_month: "/ month",
    price_student_month: "/ student / month",
  },
  bm: {
    // Navbar & Common
    app_name: "ScholarPulse MTIS",
    app_badge: "Jurulatih Akademik v2.4",
    nav_pricing: "Harga Pelan (RM15/bln)",
    nav_signin: "Log Masuk",
    nav_launch: "Buka Aplikasi",
    nav_dashboard: "Pergi ke Papan Pemuka",
    nav_back_dashboard: "Kembali ke Papan Pemuka",
    nav_signout: "Log Keluar",
    nav_admin: "Pusat Pentadbir",
    nav_workspace: "Ruang Kerja Tesis",
    nav_subscriptions: "Langganan",
    nav_demo_badge: "Demo Tanpa Kunci Aktif",
    lang_toggle_label: "Bahasa",

    // Home Page
    hero_badge: "Kecerdasan Penyelidikan Pengajian Tinggi",
    hero_title: "Kenal Pasti Jurang Penyelidikan Novel untuk Tesis Malaysia Anda",
    hero_subtitle:
      "Memperkasa penyelidik diploma, ijazah, dan pascasiswazah Malaysia mengenal pasti jurang literatur yang kukuh, merangka tajuk tesis dwibahasa (BM & EN), serta merancang pelan metodologi berasaskan rujukan institusi.",
    hero_cta_demo: "Mula Sekarang Tanpa Kunci API",
    hero_cta_pricing: "Lihat Harga Pelajar (RM15/bln)",
    feat_1_title: "Repositori Institusi",
    feat_1_desc: "Integrasi terus bersama arkib universiti tempatan (UTM E-Theses) dan korpus global OpenAlex.",
    feat_2_title: "Penemuan Jurang Novel",
    feat_2_desc: "Cari jurang empirikal dan teoretikal yang belum diterokai bagi mempertahankan keaslian tesis anda.",
    feat_3_title: "Pengasingan Pelbagai Penyewa",
    feat_3_desc: "Perlindungan data institusi memastikan setiap penyelidik dan kampus kekal terpelihara serta peribadi.",

    // Login Page
    login_title: "Log Masuk ke MTIS",
    login_subtitle: "Penstrukturan Tesis Institusi & Penemuan Jurang Penyelidikan",
    login_google_btn: "Teruskan dengan Google (Akan Datang)",
    login_google_hint: "Log masuk Google akan diaktifkan selepas pelancaran. Sila guna persona demo di bawah.",
    login_or_divider: "ATAU GUNA PERSONA UJIAN (MOD DEMO)",
    login_student_section: "AKSES PENYELIDIK / PELAJAR",
    login_admin_section: "AKSES PENTADBIR SISTEM / PEMILIK",
    login_demo_uni: "Penyelidik Universiti Demo",
    login_utm_ahmad: "Penyelidik UTM (Ahmad)",
    login_admin_owner: "Pentadbir Sistem (Pemilik)",
    login_coach_note:
      "MTIS mengasingkan ruang kerja mengikut penyewa institusi. Memilih persona demo mensimulasikan akses kampus yang disahkan.",

    // Dashboard
    dash_stage1_title: "1. Carian Topik",
    dash_stage1_sub: "Indeks OpenAlex & UTM",
    dash_stage2_title: "2. Analisis Jurang",
    dash_stage2_sub: "Penemuan Jurang Novel",
    dash_stage3_title: "3. Cadangan Tajuk",
    dash_stage3_sub: "Tajuk Berasas EN / BM",
    dash_stage4_title: "4. Carian Terperinci",
    dash_stage4_sub: "Artikel Sub-Bidang Khusus",
    dash_stage5_title: "5. Pelan Penyelidikan",
    dash_stage5_sub: "Objektif & Metodologi",

    dash_stage1_header: "Peringkat 1: Carian Literatur Topik & Penemuan Artikel",
    dash_stage1_desc:
      "Cari e-tesis universiti Malaysia (UTM E-Theses) dan repositori berwasit global (OpenAlex).",
    dash_scope_my: "Malaysia (UTM & Tempatan)",
    dash_scope_int: "Global (OpenAlex Antarabangsa)",
    dash_search_placeholder: "cth. tvet, e-wallet, pertanian pintar IoT, rantaian blok halal...",
    dash_btn_search: "Cari Artikel",
    dash_searching: "Sedang Mencari Repositori...",
    dash_btn_gap: "Jalankan Peringkat 2: Analisis Jurang",
    dash_btn_title: "Jalankan Peringkat 3: Cadangan Tajuk",
    dash_btn_deepdive: "Jalankan Peringkat 4: Carian Terperinci",
    dash_btn_plan: "Jalankan Peringkat 5: Pelan Penyelidikan",
    dash_open_canvas: "Buka Kanvas Pelan",

    dash_quota_badge: "Kuota AI Harian",
    dash_refill_btn: "Isi Semula Kuota",
    dash_settings_btn: "Tetapan Kunci API",
    dash_tenant_title: "Pengasingan Institusi",
    dash_coach_title: "Pembantu Jurulatih Akademik",
    dash_coach_topics: "CADANGAN TOPIK PANTAS:",
    dash_coach_prompt_ph: "Tanya jurulatih atau cari topik...",

    // Plan Studio (/plan)
    plan_title: "Objektif, Metodologi & Pelaksanaan Berkomputer",
    plan_badge: "Memenuhi Kontrak AI",
    plan_sec1_title: "Objektif Utama Penyelidikan",
    plan_sec2_title: "Pencapaian Utama (Milestones)",
    plan_sec3_title: "Garis Masa & Fasa Penyelidikan",
    plan_sec4_title: "Keperluan Sumber & Kebolehlaksanaan",
    plan_refine_title: "Penambahbaikan Bersama Jurulatih",
    plan_refine_desc:
      'Berikan maklum balas untuk meminda objektif, kaedah, atau sumber (cth: "Fokus kepada PKS Malaysia" atau "Pendekkan garis masa kepada 18 bulan").',
    plan_prompt_label: "PROMPT MAKLUM BALAS",
    plan_prompt_ph: "cth: Fokus kepada kampus Kolej Vokasional di Selangor dan Johor...",
    plan_btn_refine: "Hantar Penambahbaikan",
    plan_refining: "Sedang Mengemaskini...",
    plan_vc_title: "Nota Kawalan Versi",
    plan_vc_desc:
      "Penambahbaikan akan mensintesis semula 3 objektif SMART yang jitu, menyelaraskan milestone, dan mengemas kini sumber institusi.",

    // Pricing Page
    price_title: "Harga Berpatutan & Mesra Pelajar",
    price_subtitle:
      "Direka khas untuk penyelidik diploma, ijazah, dan pascasiswazah di Malaysia. Gantikan perisian manual yang mahal dengan panduan tesis AI berinstitusi.",
    price_free_title: "Peneroka Pelajar",
    price_free_desc: "Semua keperluan asas untuk meninjau topik dan mengenal pasti jurang literatur tulen.",
    price_free_quota: "3 Analisis Jurang setiap hari (set semula harian)",
    price_pro_title: "Pascasiswazah Pro",
    price_pro_desc: "Analisis tanpa had, pembelaan tajuk dwibahasa (BM/EN), dan eksport pelan ke format LaTeX/PDF.",
    price_pro_quota: "99 Pertanyaan Penyelidikan AI / bulan",
    price_free_cta: "Mula Percuma",
    price_pro_cta: "Naik Taraf ke Pro",
    price_recommended: "DISYORKAN",
    price_economics_title: "Model Perniagaan & Ekonomi Unit (Bukti D1)",
    price_month: "/ bulan",
    price_student_month: "/ pelajar / bulan",
  },
};

export type TranslationKey = keyof typeof translations.en;
