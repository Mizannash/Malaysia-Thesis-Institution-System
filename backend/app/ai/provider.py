"""
LLM Provider Adapter for MTIS.
Supports swappable model providers (DeepSeek, OpenAI, Gemini),
deterministic fixture-based execution for DEMO_MODE / no-key mode,
and mock handlers for stress & contract tests.
"""
import os
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ProviderResponse:
    content: str
    tokens: int
    cost_myr: float
    model: str
    status: str = "ok"  # "ok" | "no_key_mode"


# Global test hook for injecting mock responses in stress tests
_mock_handler: Optional[Callable[[str, List[Dict[str, str]]], str]] = None


def set_mock_provider_handler(handler: Optional[Callable[[str, List[Dict[str, str]]], str]]):
    """Set custom mock handler for testing malformed, repair, or edge-case responses."""
    global _mock_handler
    _mock_handler = handler


def reset_mock_provider_handler():
    """Reset the mock provider handler to None."""
    global _mock_handler
    _mock_handler = None


def _load_fixture_data(filename: str) -> Any:
    candidate_paths = [
        Path(__file__).resolve().parent.parent.parent.parent / "tests" / "fixtures" / filename,
        Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / filename,
        Path("tests/fixtures") / filename,
        Path("/app/tests/fixtures") / filename,
    ]
    for p in candidate_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read fixture {p}: {e}")
    return None


def call_llm_provider(
    stage: str,
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    user_email: Optional[str] = "anonymous",
) -> ProviderResponse:
    """
    Calls configured LLM provider or fallback fixture engine.
    - If mock handler is set, invokes handler.
    - If DEMO_MODE or no keys configured, returns cached fixture with cost_myr=0.00.
    - Otherwise, dispatches to live API.
    """
    # 1. Test Mock Handler Hook
    if _mock_handler is not None:
        content = _mock_handler(stage, messages)
        return ProviderResponse(
            content=content,
            tokens=120,
            cost_myr=0.00,
            model="mock-provider",
            status="ok"
        )

    # 2. Check for active API Keys
    deepseek_key = getattr(settings, "DEEPSEEK_API_KEY", None) or os.getenv("DEEPSEEK_API_KEY")
    openai_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")

    has_live_keys = bool((deepseek_key and deepseek_key.strip()) or (openai_key and openai_key.strip()))

    # 3. DEMO_MODE or NO-KEY Mode Fallback (D4 requirement)
    if getattr(settings, "DEMO_MODE", True) or not has_live_keys:
        logger.info(f"LLM Provider executing in NO-KEY / DEMO mode for stage '{stage}'")
        messages_text = " ".join(m.get("content", "") for m in messages if isinstance(m, dict))
        if stage == "gap":
            import re, copy
            found_paper_ids = re.findall(r'"paper_id":\s*"([^"]+)"', messages_text)
            if not found_paper_ids:
                found_paper_ids = list(dict.fromkeys(re.findall(r'\b(P\d+)\b', messages_text))) or ["P1", "P2", "P3", "P4"]

            paper_titles = re.findall(r'"title":\s*"([^"]+)"', messages_text)

            is_fintech = any("wallet" in t.lower() or "fintech" in t.lower() or "qr" in t.lower() for t in paper_titles)
            is_tvet = any("tvet" in t.lower() or "vocational" in t.lower() or "skill" in t.lower() for t in paper_titles) or "tvet" in messages_text.lower()

            if is_tvet:
                p1 = found_paper_ids[0] if len(found_paper_ids) > 0 else "P1"
                p2 = found_paper_ids[1] if len(found_paper_ids) > 1 else p1
                p3 = found_paper_ids[2] if len(found_paper_ids) > 2 else p1
                p4 = found_paper_ids[3] if len(found_paper_ids) > 3 else p2

                t1 = paper_titles[0] if len(paper_titles) > 0 else "TVET in Malaysia"
                t2 = paper_titles[1] if len(paper_titles) > 1 else "ICT Integrations in TVET"
                t3 = paper_titles[2] if len(paper_titles) > 2 else "TVET Instructor Competency Framework"

                fixture_data = {
                    "gaps": [
                        {
                            "gap_id": "GAP-1",
                            "description": f"While foundational research examines {t1} ({p1}), existing pedagogical frameworks fail to model technical simulation integration and Industry 4.0 competency alignment within Malaysian public vocational training polytechnics ({p2}).",
                            "supporting_paper_ids": [p1, p2],
                        },
                        {
                            "gap_id": "GAP-2",
                            "description": f"Although empirical studies investigate {t2} ({p2}), a critical research gap persists regarding vocational instructor technical reskilling barriers and workplace apprenticeship retention rates across suburban Malaysian industrial corridors ({p1}, {p3}).",
                            "supporting_paper_ids": [p2, p3],
                        },
                        {
                            "gap_id": "GAP-3",
                            "description": f"Current scholarship evaluates {t3} ({p3}), yet there is a significant deficiency in empirical structural equation models evaluating graduate employability persistence and workplace automation readiness among Malaysian vocational diploma cohorts ({p3}, {p4}).",
                            "supporting_paper_ids": [p3, p4],
                        },
                    ]
                }
            elif not is_fintech and paper_titles and len(paper_titles) >= 1:
                p1 = found_paper_ids[0] if len(found_paper_ids) > 0 else "P1"
                p2 = found_paper_ids[1] if len(found_paper_ids) > 1 else p1
                p3 = found_paper_ids[2] if len(found_paper_ids) > 2 else p1
                p4 = found_paper_ids[3] if len(found_paper_ids) > 3 else p2

                t1 = paper_titles[0]
                t2 = paper_titles[1] if len(paper_titles) > 1 else t1
                t3 = paper_titles[2] if len(paper_titles) > 2 else t1

                fixture_data = {
                    "gaps": [
                        {
                            "gap_id": "GAP-1",
                            "description": f"While prior literature addresses {t1} ({p1}), current empirical frameworks fail to account for implementation constraints and institutional adaptation within the Malaysian academic and socio-economic context ({p2}).",
                            "supporting_paper_ids": [p1, p2],
                        },
                        {
                            "gap_id": "GAP-2",
                            "description": f"Although studies investigate {t2} ({p2}), a critical empirical research gap persists regarding multi-stakeholder operational barriers and regional infrastructure readiness across Malaysian states ({p1}, {p3}).",
                            "supporting_paper_ids": [p2, p3],
                        },
                        {
                            "gap_id": "GAP-3",
                            "description": f"Current scholarship reviews {t3} ({p3}), yet there is an unaddressed gap in longitudinal validation and predictive structural equation modeling for Malaysian institutional deployments ({p3}, {p4}).",
                            "supporting_paper_ids": [p3, p4],
                        },
                    ]
                }
            else:
                fixture_data = _load_fixture_data("gap_fixture.json")
                if fixture_data:
                    fixture_data = copy.deepcopy(fixture_data)
                    for idx, gap in enumerate(fixture_data.get("gaps", [])):
                        cites = [found_paper_ids[idx % len(found_paper_ids)]]
                        if len(found_paper_ids) > 1:
                            next_id = found_paper_ids[(idx + 1) % len(found_paper_ids)]
                            if next_id not in cites:
                                cites.append(next_id)
                        gap["supporting_paper_ids"] = cites

            return ProviderResponse(
                content=json.dumps(fixture_data),
                tokens=450,
                cost_myr=0.00,
                model="demo-fixtures",
                status="no_key_mode"
            )
        elif stage == "title":
            import re
            gap_match = re.search(r'"gap_id":\s*"([^"]+)"', messages_text)
            target_gap = gap_match.group(1) if gap_match else "GAP-1"

            is_tvet = "tvet" in messages_text.lower() or "vocational" in messages_text.lower() or "polytechnic" in messages_text.lower()
            is_fintech = "wallet" in messages_text.lower() or "fintech" in messages_text.lower() or "merchant" in messages_text.lower()

            if is_tvet:
                fixture_data = {
                    "titles": [
                        {
                            "title": "Empirical Evaluation of Digital Simulation Integration and Technical Competency Acquisition in Malaysian TVET Polytechnics",
                            "title_bm": "Penilaian Empirikal Integrasi Simulasi Digital dan Pemerolehan Kompetensi Teknikal di Politeknik TVET Malaysia",
                            "gap_id": target_gap,
                            "language": "EN",
                            "novelty_score": 9.2,
                            "feasibility": "HIGH",
                            "methodology_type": "Quantitative / Structural Equation Modeling (PLS-SEM)",
                        },
                        {
                            "title": "Industry 4.0 Technical Curriculum Alignment and Apprenticeship Retention in Malaysian Vocational Institutes: A Multi-Stakeholder Analysis",
                            "title_bm": "Penyelarasan Kurikulum Teknikal Industri 4.0 dan Pengekalan Perantisan di Institut Vokasional Malaysia",
                            "gap_id": target_gap,
                            "language": "EN",
                            "novelty_score": 8.9,
                            "feasibility": "HIGH",
                            "methodology_type": "Mixed Methods (Cross-Sectional Survey & Expert Interviews)",
                        },
                        {
                            "title": "Assessing Vocational Instructor Digital Readiness and Work-Based Learning Outcomes across Malaysian Technical Colleges",
                            "title_bm": "Menilai Kesediaan Digital Pengajar Vokasional dan Hasil Pembelajaran Berasaskan Kerja di Kolej Vokasional Malaysia",
                            "gap_id": target_gap,
                            "language": "EN",
                            "novelty_score": 8.6,
                            "feasibility": "MEDIUM",
                            "methodology_type": "Empirical Survey & Factor Analysis",
                        },
                    ]
                }
            elif not is_fintech and ("iot" in messages_text.lower() or "agriculture" in messages_text.lower()):
                fixture_data = {
                    "titles": [
                        {
                            "title": "An Empirical Framework for IoT Sensor Network Adoption in Malaysian Smart Agricultural Smallholdings",
                            "title_bm": "Kerangka Empirikal Penggunaan Rangkaian Penderia IoT dalam Pertanian Pintar Pekebun Kecil Malaysia",
                            "gap_id": target_gap,
                            "language": "EN",
                            "novelty_score": 9.0,
                            "feasibility": "HIGH",
                            "methodology_type": "Quantitative / PLS-SEM",
                        },
                        {
                            "title": "Evaluating Resource-Constrained IoT Telemetry Deployment for Sustainable Crop Monitoring in Johor Agriculture",
                            "title_bm": "Menilai Penggunaan Telemetri IoT Berkekangan Sumber untuk Pemantauan Tanaman Mampan di Johor",
                            "gap_id": target_gap,
                            "language": "EN",
                            "novelty_score": 8.7,
                            "feasibility": "HIGH",
                            "methodology_type": "Field Experiment & Survey",
                        },
                    ]
                }
            else:
                fixture_data = _load_fixture_data("title_fixture.json")
                if fixture_data:
                    for item in fixture_data.get("titles", []):
                        item["gap_id"] = target_gap

            return ProviderResponse(
                content=json.dumps(fixture_data),
                tokens=280,
                cost_myr=0.00,
                model="demo-fixtures",
                status="no_key_mode"
            )
        elif stage == "deepdive":
            import re, copy
            title_match = re.search(r'"chosen_title":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if not title_match:
                title_match = re.search(r'"title":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if title_match:
                try:
                    chosen_title = json.loads(f'"{title_match.group(1)}"')
                except Exception:
                    chosen_title = title_match.group(1).replace(r'\"', '"')
            else:
                chosen_title = "Empirical Evaluation of Digital Simulation Integration and Technical Competency Acquisition in Malaysian TVET Polytechnics"

            gap_match = re.search(r'"gap_id":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if gap_match:
                try:
                    target_gap = json.loads(f'"{gap_match.group(1)}"')
                except Exception:
                    target_gap = gap_match.group(1)
            else:
                target_gap = "GAP-1"

            is_tvet = "tvet" in messages_text.lower() or "vocational" in messages_text.lower() or "polytechnic" in messages_text.lower()

            if is_tvet:
                fixture_data = {
                    "gap_id": target_gap,
                    "chosen_title": chosen_title,
                    "papers": [
                        {
                            "title": "Work-Based Learning and Digital Pedagogy in Malaysian TVET: Current Challenges and Future Outlook",
                            "authors": ["Mohd Yusof, H.", "Ahmad, N. A.", "Razali, M."],
                            "year": 2023,
                            "doi": "10.11113/jt.v84.92305",
                            "url": "http://eprints.utm.my/id/eprint/tvet01",
                            "abstract": "This empirical study investigates the operational integration of interactive simulations and technical workshop facilities across Malaysian public vocational institutions, highlighting critical gaps in curriculum responsiveness.",
                            "citation_count": 34,
                            "source": "utm"
                        },
                        {
                            "title": "Industry 4.0 Readiness and Apprenticeship Retention in Malaysian Technical Training Institutes",
                            "authors": ["Ibrahim, Z.", "Kassim, R."],
                            "year": 2024,
                            "doi": "10.1016/j.tvet.2024.102341",
                            "url": "https://doi.org/10.1016/j.tvet.2024.102341",
                            "abstract": "An evaluation of institutional-industrial collaboration models in Johor and Selangor, identifying key factors influencing vocational apprentice workplace readiness and skills retention.",
                            "citation_count": 28,
                            "source": "openalex"
                        },
                        {
                            "title": "Assessing Vocational Teacher Competency and Digital Tool Adoption in Malaysian Vocational Colleges",
                            "authors": ["Sulaiman, S.", "Alias, M."],
                            "year": 2022,
                            "doi": "10.11113/mjitcs.v15n2.98124",
                            "url": "http://eprints.utm.my/id/eprint/tvet03",
                            "abstract": "A quantitative assessment of technical instructors in MARA and MOE vocational colleges, measuring self-efficacy in virtual training environment execution.",
                            "citation_count": 41,
                            "source": "utm"
                        },
                        {
                            "title": "National Qualification Frameworks and Employer Perception of Malaysian TVET Graduates",
                            "authors": ["Tan, K. L.", "Othman, B."],
                            "year": 2023,
                            "doi": "10.1108/ET-08-2023-0199",
                            "url": "https://doi.org/10.1108/ET-08-2023-0199",
                            "abstract": "Examines the alignment between Malaysian Skills Certification (SKM) standards and industry employer requirements in high-growth manufacturing sectors.",
                            "citation_count": 19,
                            "source": "openalex"
                        },
                        {
                            "title": "Smart Polytechnic Framework: Enhancing Technical and Vocational Training via Cloud Simulation Platforms",
                            "authors": ["Che Ahmad, C. N.", "Yahya, S."],
                            "year": 2023,
                            "doi": "10.11113/englet.v30.89100",
                            "url": "http://eprints.utm.my/id/eprint/tvet05",
                            "abstract": "Evaluates the infrastructure requirements and instructional design strategies for implementing digital simulation labs in polytechnic engineering departments across Malaysia.",
                            "citation_count": 22,
                            "source": "utm"
                        },
                        {
                            "title": "Employability Outcomes of TVET Graduates in the Malaysian High-Tech Sector: A PLS-SEM Analysis",
                            "authors": ["Kamal, M. R.", "Zakaria, A."],
                            "year": 2024,
                            "doi": "10.1016/j.ijedudev.2024.103112",
                            "url": "https://doi.org/10.1016/j.ijedudev.2024.103112",
                            "abstract": "An empirical structural equation modeling analysis assessing the alignment between technical diploma curricula and Industry 4.0 job competency profiles in Malaysian economic corridors.",
                            "citation_count": 17,
                            "source": "openalex"
                        }
                    ]
                }
            else:
                loaded = _load_fixture_data("deepdive_fixture.json")
                if loaded:
                    fixture_data = copy.deepcopy(loaded)
                    fixture_data["gap_id"] = target_gap
                    fixture_data["chosen_title"] = chosen_title
                else:
                    fixture_data = {
                        "gap_id": target_gap,
                        "chosen_title": chosen_title,
                        "papers": [
                            {
                                "title": "Empirical Evaluation of Digital Adoption Barriers in Malaysian Higher Education",
                                "authors": ["Zulkafli, A.", "Hamid, R."],
                                "year": 2023,
                                "doi": "10.11113/jt.v84.92305",
                                "url": "https://doi.org/10.11113/jt.v84.92305",
                                "abstract": "Investigates institutional and technological barriers affecting digital learning adoption across Malaysian public universities.",
                                "citation_count": 21,
                                "source": "openalex"
                            },
                            {
                                "title": "Technological Frameworks for Sustainable Institutional Transformation in Malaysia",
                                "authors": ["Tan, W. L.", "Ibrahim, M. H."],
                                "year": 2024,
                                "doi": "10.1108/JFM-08-2023-0091",
                                "url": "https://doi.org/10.1108/JFM-08-2023-0091",
                                "abstract": "Examines operational transitions and compliance mechanisms under national higher education blueprints.",
                                "citation_count": 18,
                                "source": "openalex"
                            },
                            {
                                "title": "Structural Equation Modeling of Digital Tool Persistence in Malaysian Institutions",
                                "authors": ["Sulaiman, N.", "Othman, B."],
                                "year": 2023,
                                "doi": "10.11113/mjitcs.v15n2.98124",
                                "url": "https://doi.org/10.11113/mjitcs.v15n2.98124",
                                "abstract": "Empirical survey modeling behavioral intentions and persistence among postgraduate researchers.",
                                "citation_count": 29,
                                "source": "utm"
                            },
                            {
                                "title": "Collaborative Research Frameworks and Knowledge Sharing Across Malaysian HEIs",
                                "authors": ["Kaur, H.", "Yusof, Z."],
                                "year": 2022,
                                "doi": "10.11113/englet.v30.89100",
                                "url": "https://doi.org/10.11113/englet.v30.89100",
                                "abstract": "Evaluates cross-institutional knowledge transfer and collaborative repository networks.",
                                "citation_count": 15,
                                "source": "utm"
                            },
                            {
                                "title": "Predictive Modeling of Academic Competency Acquisition in Malaysian Technical Degrees",
                                "authors": ["Razak, A.", "Nurhaliza, S."],
                                "year": 2023,
                                "doi": "10.11113/utmpj.v19n1.101452",
                                "url": "https://doi.org/10.11113/utmpj.v19n1.101452",
                                "abstract": "Assesses curriculum alignment and technical competency acquisition in Malaysian engineering faculties.",
                                "citation_count": 16,
                                "source": "openalex"
                            },
                            {
                                "title": "Industry-Academia Partnerships and Graduate Readiness in Malaysian Research Universities",
                                "authors": ["Lim, B. K.", "Mokhtar, S."],
                                "year": 2024,
                                "doi": "10.1016/j.eswa.2024.123456",
                                "url": "https://doi.org/10.1016/j.eswa.2024.123456",
                                "abstract": "A multi-stakeholder assessment evaluating graduate readiness and industry research translation in Malaysia.",
                                "citation_count": 14,
                                "source": "openalex"
                            }
                        ]
                    }

            return ProviderResponse(
                content=json.dumps(fixture_data),
                tokens=520,
                cost_myr=0.00,
                model="demo-fixtures",
                status="no_key_mode"
            )
        elif stage in ("plan", "refine"):
            import re, copy
            title_match = re.search(r'"chosen_title":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if not title_match:
                title_match = re.search(r'"title":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if title_match:
                try:
                    chosen_title = json.loads(f'"{title_match.group(1)}"')
                except Exception:
                    chosen_title = title_match.group(1).replace(r'\"', '"')
            else:
                chosen_title = "Empirical Thesis Research Plan in Malaysian Context"

            gap_match = re.search(r'"gap_id":\s*"((?:[^"\\]|\\.)*)"', messages_text)
            if gap_match:
                try:
                    target_gap = json.loads(f'"{gap_match.group(1)}"')
                except Exception:
                    target_gap = gap_match.group(1)
            else:
                target_gap = "GAP-1"

            is_tvet = "tvet" in messages_text.lower() or "vocational" in messages_text.lower() or "polytechnic" in messages_text.lower()

            if is_tvet:
                fixture_data = {
                    "plan_id": "plan-tvet-01",
                    "title": chosen_title or "Empirical Evaluation of Digital Simulation Integration in Malaysian TVET Polytechnics",
                    "gap_id": target_gap,
                    "version": 1,
                    "objectives": [
                        {
                            "objective_id": "RO-1",
                            "text": "To evaluate the current state and operational barriers of digital simulation lab integration across Malaysian public TVET polytechnics."
                        },
                        {
                            "objective_id": "RO-2",
                            "text": "To determine the empirical relationship between Industry 4.0 technical curriculum alignment and apprentice practical competency acquisition."
                        },
                        {
                            "objective_id": "RO-3",
                            "text": "To formulate and validate a predictive structural model of vocational instructor digital efficacy and graduate workplace employability."
                        }
                    ],
                    "methodology_summary": "A mixed-methods empirical investigation combining a cross-sectional questionnaire survey administered across 350 TVET students and instructors in Malaysian polytechnics with qualitative expert interviews from manufacturing partners, analyzed via PLS-SEM (SmartPLS 4).",
                    "key_milestones": [
                        {
                            "milestone_id": "M1",
                            "title": "Literature Synthesis & Instrument Design",
                            "description": "Synthesize literature from OpenAlex and UTM repositories, draft survey instrument, and conduct pilot reliability testing.",
                            "target_month": "Month 3"
                        },
                        {
                            "milestone_id": "M2",
                            "title": "Field Sampling & Institutional Data Collection",
                            "description": "Administer cross-sectional survey to TVET cohorts across selected polytechnics in Johor, Selangor, and Penang.",
                            "target_month": "Month 6"
                        },
                        {
                            "milestone_id": "M3",
                            "title": "Structural Equation Modeling & Hypothesis Testing",
                            "description": "Execute measurement model verification, discriminant validity, and structural path coefficient estimation in SmartPLS 4.",
                            "target_month": "Month 9"
                        },
                        {
                            "milestone_id": "M4",
                            "title": "Dissertation Finalization & Viva Voce",
                            "description": "Complete final 5-chapter thesis manuscript, incorporate supervisory feedback, and defend findings in oral examination.",
                            "target_month": "Month 12"
                        }
                    ],
                    "timeline": [
                        {
                            "phase_name": "Phase 1: Conceptualization & Ethics",
                            "months": "Months 1 - 3",
                            "tasks": [
                                "Conduct systematic literature synthesis on TVET digital simulation integration",
                                "Formulate research hypotheses and measurement indicators",
                                "Secure institutional review board ethical clearance"
                            ]
                        },
                        {
                            "phase_name": "Phase 2: Empirical Fieldwork & SEM Analysis",
                            "months": "Months 4 - 8",
                            "tasks": [
                                "Distribute bilingual survey questionnaire across 10 polytechnic campuses",
                                "Perform data cleaning, normality screening, and common method bias testing",
                                "Execute PLS-SEM bootstrapping and path analysis"
                            ]
                        },
                        {
                            "phase_name": "Phase 3: Synthesis, Thesis Defense & Policy Translation",
                            "months": "Months 9 - 12",
                            "tasks": [
                                "Formulate practical recommendations for MOHE TVET Division",
                                "Draft 5-chapter thesis dissertation",
                                "Complete final viva voce defense"
                            ]
                        }
                    ],
                    "necessary_resources": [
                        {
                            "category": "Software & Analytical Tools",
                            "item": "SmartPLS 4 & IBM SPSS Statistics 29",
                            "justification": "Required for partial least squares structural equation modeling and exploratory factor analysis."
                        },
                        {
                            "category": "Institutional Access",
                            "item": "Ministry of Higher Education (MOHE) TVET Division Research Permit",
                            "justification": "Mandatory clearance for administering survey instruments across Malaysian polytechnics."
                        },
                        {
                            "category": "Field Travel",
                            "item": "Polytechnic Campus Site Visit Travel Grant",
                            "justification": "Required for in-person instructor interviews and workshop facility benchmarking across Selangor, Penang, and Johor."
                        }
                    ]
                }
            else:
                loaded = _load_fixture_data("plan_fixture.json")
                if loaded:
                    fixture_data = copy.deepcopy(loaded)
                    fixture_data["title"] = chosen_title
                    fixture_data["gap_id"] = target_gap
                else:
                    fixture_data = {
                        "plan_id": "plan-general-01",
                        "title": chosen_title,
                        "gap_id": target_gap,
                        "version": 1,
                        "objectives": [
                            {
                                "objective_id": "RO-1",
                                "text": "To investigate the institutional and empirical factors influencing academic adoption across Malaysian higher education."
                            },
                            {
                                "objective_id": "RO-2",
                                "text": "To formulate and empirically evaluate an extended structural equation model (PLS-SEM) of institutional readiness."
                            },
                            {
                                "objective_id": "RO-3",
                                "text": "To provide evidence-based policy recommendations for Malaysian higher education institutions and regulatory agencies."
                            }
                        ],
                        "key_milestones": [
                            {
                                "milestone_id": "M1",
                                "title": "Systematic Literature Review & Proposal Defense",
                                "description": "Synthesize existing literature, complete conceptual framework, and obtain proposal defense approval.",
                                "target_month": "Month 3"
                            },
                            {
                                "milestone_id": "M2",
                                "title": "Instrumentation & Pilot Validation",
                                "description": "Design survey instrument, conduct pilot study, and establish reliability and validity.",
                                "target_month": "Month 6"
                            },
                            {
                                "milestone_id": "M3",
                                "title": "Field Sampling & PLS-SEM Estimation",
                                "description": "Administer survey across target institutions and execute structural path analysis in SmartPLS 4.",
                                "target_month": "Month 9"
                            },
                            {
                                "milestone_id": "M4",
                                "title": "Thesis Dissertation Submission & Viva",
                                "description": "Draft complete 5-chapter thesis dissertation, address supervisor feedback, and defend in oral viva voce.",
                                "target_month": "Month 12"
                            }
                        ],
                        "necessary_resources": [
                            {
                                "category": "Software & Analytical Tools",
                                "item": "SmartPLS 4 & IBM SPSS Statistics",
                                "justification": "Required for partial least squares structural equation modeling."
                            },
                            {
                                "category": "Ethics & Clearances",
                                "item": "Institutional Human Research Ethics Clearance",
                                "justification": "Mandatory prior to field sampling and survey distribution."
                            },
                            {
                                "category": "Institutional Access",
                                "item": "Higher Education Institutional Registry Access",
                                "justification": "Sampling frame access for target participants."
                            }
                        ],
                        "timeline": [
                            {
                                "phase_name": "Phase 1: Conceptualization & Ethics",
                                "months": "Months 1 - 3",
                                "tasks": [
                                    "Complete systematic literature synthesis",
                                    "Formulate conceptual model and hypotheses",
                                    "Obtain institutional ethics board approval"
                                ]
                            },
                            {
                                "phase_name": "Phase 2: Empirical Fieldwork & SEM Analysis",
                                "months": "Months 4 - 8",
                                "tasks": [
                                    "Administer survey to target cohorts",
                                    "Screen data and evaluate measurement model",
                                    "Run bootstrapping for structural path significance"
                                ]
                            },
                            {
                                "phase_name": "Phase 3: Thesis Writing & Defense",
                                "months": "Months 9 - 12",
                                "tasks": [
                                    "Synthesize findings and practical implications",
                                    "Complete 5-chapter thesis submission",
                                    "Prepare and complete viva voce defense"
                                ]
                            }
                        ],
                        "methodology_summary": "Cross-sectional quantitative empirical design utilizing structural equation modeling (PLS-SEM) across Malaysian higher education institutions to evaluate structural relationships and institutional adoption factors.",
                        "version": 1
                    }

            if stage == "refine":
                feedback_match = re.search(r'(?:Feedback|revision instructions|user_prompt)[:\s]*([^\n"]+)', messages_text, re.IGNORECASE)
                feedback = feedback_match.group(1).strip() if feedback_match else "Focused refinement on Malaysian institutions"
                lower_fb = feedback.lower()
                fixture_data["version"] = fixture_data.get("version", 1) + 1

                # Determine targeted scope for Johor Bahru and other foci
                if "johor bahru" in lower_fb or "jb" in lower_fb:
                    target_scope = "Kolej Vokasional and Polytechnic institutions specifically within Johor Bahru (e.g., KV Tanjung Puteri, KV Perdagangan JB, and Politeknik Ibrahim Sultan)"
                    target_scope_short = "Johor Bahru technical and vocational campuses"
                    stakeholder_scope = "Johor Bahru vocational directors, Johor State Education Department (JPN Johor), and Southern Corridor (Iskandar Malaysia/Pasir Gudang) stakeholders"
                    scope_name = "Johor Bahru"
                elif "selangor" in lower_fb:
                    target_scope = "Kolej Vokasional and Polytechnic institutions across Selangor (e.g., KV Shah Alam, KV Klang, Politeknik Sultan Salahuddin Abdul Aziz Shah)"
                    target_scope_short = "Selangor technical campuses"
                    stakeholder_scope = "Selangor State Education Department and Klang Valley industrial development councils"
                    scope_name = "Selangor"
                elif "penang" in lower_fb:
                    target_scope = "Kolej Vokasional and Polytechnic campuses across Penang (Seberang Perai and Bayan Lepas clusters)"
                    target_scope_short = "Penang technical institutions"
                    stakeholder_scope = "Penang State Education Department and PSDC industrial partners"
                    scope_name = "Penang"
                else:
                    scope_name = feedback.capitalize()
                    target_scope = f"Malaysian technical and higher education institutions with specific focus on {feedback}"
                    target_scope_short = f"participating campuses focusing on {feedback}"
                    stakeholder_scope = f"Malaysian educational leadership, policy directors, and {feedback} stakeholders"

                fixture_data["scope_focus"] = scope_name
                if "title" in fixture_data and scope_name and scope_name.lower() not in fixture_data["title"].lower():
                    fixture_data["title"] = f"{fixture_data['title']}: An Empirical Study in {scope_name}"

                fixture_data["methodology_summary"] = (
                    f"Refined Research Architecture (v{fixture_data['version']}) tailored to: '{feedback}'. "
                    f"Maintains 3 disciplined SMART objectives, synchronized milestones, full timeline, and institutional resource allocations specifically aligned with {scope_name}."
                )

                if fixture_data.get("objectives") and len(fixture_data["objectives"]) >= 3:
                    fixture_data["objectives"][0]["text"] = (
                        f"To identify, evaluate, and prioritize the key empirical factors and operational barriers impacting {target_scope}."
                    )
                    fixture_data["objectives"][1]["text"] = (
                        f"To construct and empirically test an extended structural equation model (PLS-SEM) measuring the predictive relationships between institutional readiness, digital competency, and curriculum modernizations within {target_scope_short}."
                    )
                    fixture_data["objectives"][2]["text"] = (
                        f"To formulate actionable institutional policy frameworks and strategic implementation roadmaps for {stakeholder_scope}."
                    )

                if fixture_data.get("key_milestones"):
                    for m in fixture_data["key_milestones"]:
                        mid = m.get("milestone_id")
                        if mid == "M1":
                            m["description"] = f"Synthesize literature review, operationalize constructs tailored specifically to {target_scope_short}, and secure departmental committee defense approval."
                        elif mid == "M2":
                            m["description"] = f"Administer pilot testing with 30 target vocational educators and respondents from {target_scope_short}; establish composite reliability and Cronbach's alpha > 0.70."
                        elif mid == "M3":
                            m["description"] = f"Collect empirical cross-sectional data (N=250) from {target_scope_short}; perform path coefficient estimation and hypothesis testing in SmartPLS 4."
                        elif mid == "M4":
                            m["description"] = f"Compile dissertation findings, submit draft with localized policy implications for {scope_name} to external examiners, and successfully defend thesis before the faculty viva board."

            return ProviderResponse(
                content=json.dumps(fixture_data),
                tokens=650,
                cost_myr=0.00,
                model="demo-fixtures",
                status="no_key_mode"
            )



        # Fallback minimal JSON if fixture not found
        return ProviderResponse(
            content=json.dumps({"gaps": []} if stage == "gap" else {"titles": []}),
            tokens=50,
            cost_myr=0.00,
            model="demo-fixtures-empty",
            status="no_key_mode"
        )

    # 4. Live Provider Call (DeepSeek / OpenAI)
    from app.ai.llm_adapter import resolve_provider_config
    cfg = resolve_provider_config()
    target_model = model or cfg.model
    api_key = cfg.api_key
    base_url = "https://api.deepseek.com/v1" if cfg.provider == "deepseek" else "https://api.openai.com/v1"

    try:
        import httpx
        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            prompt_toks = usage.get("prompt_tokens", 0)
            comp_toks = usage.get("completion_tokens", 0)
            total_toks = usage.get("total_tokens", prompt_toks + comp_toks)

            # DeepSeek token rate: ~$0.14 per 1M input (~RM0.65), ~$0.28 per 1M output (~RM1.30)
            cost_usd = (prompt_toks * 0.00000014) + (comp_toks * 0.00000028)
            cost_myr = round(cost_usd * 4.65, 4)

            return ProviderResponse(
                content=choice,
                tokens=total_toks,
                cost_myr=cost_myr,
                model=target_model,
                status="ok"
            )
    except Exception as e:
        logger.error(f"Live provider call failed: {e}. Falling back to cached fixture.")
        return ProviderResponse(
            content=json.dumps({"error": str(e)}),
            tokens=0,
            cost_myr=0.00,
            model=target_model,
            status="error"
        )
