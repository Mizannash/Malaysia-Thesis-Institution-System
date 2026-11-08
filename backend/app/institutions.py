"""
Malaysian institutions: which tenant a student joins, decided from their confirmed email domain.

Each institution is a tenant row with an `email_domain`. Subdomains match too
(e.g. siswa.um.edu.my -> Universiti Malaya). An unknown `<name>.edu.my` domain creates
its institution automatically; a student can only sign in after confirming an email at
that domain, so nobody can join an institution whose mailbox they do not control.
"""
import logging
import re
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Tenant

logger = logging.getLogger(__name__)

# (email_domain, tenant_id, name, short_name, kind). Admins can rename rows later.
MALAYSIAN_INSTITUTIONS = [
    # Public universities
    ("um.edu.my", "inst-um", "Universiti Malaya", "UM", "public"),
    ("ukm.edu.my", "inst-ukm", "Universiti Kebangsaan Malaysia", "UKM", "public"),
    ("usm.my", "inst-usm", "Universiti Sains Malaysia", "USM", "public"),
    ("upm.edu.my", "inst-upm", "Universiti Putra Malaysia", "UPM", "public"),
    ("utm.my", "tenant-utm-001", "Universiti Teknologi Malaysia (UTM)", "UTM", "public"),
    ("uitm.edu.my", "inst-uitm", "Universiti Teknologi MARA", "UiTM", "public"),
    ("uum.edu.my", "inst-uum", "Universiti Utara Malaysia", "UUM", "public"),
    ("iium.edu.my", "inst-iium", "International Islamic University Malaysia", "IIUM", "public"),
    ("uthm.edu.my", "inst-uthm", "Universiti Tun Hussein Onn Malaysia", "UTHM", "public"),
    ("umpsa.edu.my", "inst-umpsa", "Universiti Malaysia Pahang Al-Sultan Abdullah", "UMPSA", "public"),
    ("ump.edu.my", "inst-umpsa", "Universiti Malaysia Pahang Al-Sultan Abdullah", "UMPSA", "public"),
    ("unimas.my", "inst-unimas", "Universiti Malaysia Sarawak", "UNIMAS", "public"),
    ("ums.edu.my", "inst-ums", "Universiti Malaysia Sabah", "UMS", "public"),
    ("upsi.edu.my", "inst-upsi", "Universiti Pendidikan Sultan Idris", "UPSI", "public"),
    ("usim.edu.my", "inst-usim", "Universiti Sains Islam Malaysia", "USIM", "public"),
    ("unimap.edu.my", "inst-unimap", "Universiti Malaysia Perlis", "UniMAP", "public"),
    ("umt.edu.my", "inst-umt", "Universiti Malaysia Terengganu", "UMT", "public"),
    ("unisza.edu.my", "inst-unisza", "Universiti Sultan Zainal Abidin", "UniSZA", "public"),
    ("umk.edu.my", "inst-umk", "Universiti Malaysia Kelantan", "UMK", "public"),
    ("utem.edu.my", "inst-utem", "Universiti Teknikal Malaysia Melaka", "UTeM", "public"),
    ("upnm.edu.my", "inst-upnm", "Universiti Pertahanan Nasional Malaysia", "UPNM", "public"),
    # Private universities
    ("mmu.edu.my", "inst-mmu", "Multimedia University", "MMU", "private"),
    ("uniten.edu.my", "inst-uniten", "Universiti Tenaga Nasional", "UNITEN", "private"),
    ("utp.edu.my", "inst-utp", "Universiti Teknologi PETRONAS", "UTP", "private"),
    ("taylors.edu.my", "inst-taylors", "Taylor's University", "Taylor's", "private"),
    ("sunway.edu.my", "inst-sunway", "Sunway University", "Sunway", "private"),
    ("ucsiuniversity.edu.my", "inst-ucsi", "UCSI University", "UCSI", "private"),
    ("unikl.edu.my", "inst-unikl", "Universiti Kuala Lumpur", "UniKL", "private"),
    ("apu.edu.my", "inst-apu", "Asia Pacific University of Technology & Innovation", "APU", "private"),
    ("utar.edu.my", "inst-utar", "Universiti Tunku Abdul Rahman", "UTAR", "private"),
    ("msu.edu.my", "inst-msu", "Management and Science University", "MSU", "private"),
    ("segi.edu.my", "inst-segi", "SEGi University", "SEGi", "private"),
    ("help.edu.my", "inst-help", "HELP University", "HELP", "private"),
    ("inti.edu.my", "inst-inti", "INTI International University", "INTI", "private"),
    ("mahsa.edu.my", "inst-mahsa", "MAHSA University", "MAHSA", "private"),
    ("nottingham.edu.my", "inst-nottingham", "University of Nottingham Malaysia", "UNM", "private"),
    ("xmu.edu.my", "inst-xmum", "Xiamen University Malaysia", "XMUM", "private"),
    ("curtin.edu.my", "inst-curtin", "Curtin University Malaysia", "Curtin", "private"),
]

AUTO_SUFFIX = ".edu.my"
_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def seed_institutions(db: Session) -> None:
    """Insert missing institutions and attach email domains to existing rows. Safe to run on every start."""
    for domain, tenant_id, name, short_name, kind in MALAYSIAN_INSTITUTIONS:
        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if tenant is None:
            tenant = Tenant(id=tenant_id, name=name, short_name=short_name, kind=kind)
            db.add(tenant)
            db.flush()
        if not tenant.short_name:
            tenant.short_name = short_name
        if not tenant.kind:
            tenant.kind = kind
        # A tenant has one stored domain; alias domains (e.g. ump.edu.my) are matched through the list below
        if not tenant.email_domain and not db.query(Tenant).filter(Tenant.email_domain == domain).first():
            tenant.email_domain = domain
    db.commit()


def _email_host(email: str) -> str:
    return (email or "").strip().lower().rpartition("@")[2]


def _candidate_domains(host: str) -> list[str]:
    """host and each parent domain, longest first: a.b.c.my -> [a.b.c.my, b.c.my, c.my]."""
    parts = host.split(".")
    return [".".join(parts[i:]) for i in range(len(parts) - 1)]


def _known_alias(host: str) -> Optional[str]:
    """Tenant id from the built-in list, including alias domains not stored on the row."""
    for candidate in _candidate_domains(host):
        for domain, tenant_id, *_ in MALAYSIAN_INSTITUTIONS:
            if candidate == domain:
                return tenant_id
    return None


def resolve_institution(db: Session, email: str) -> Optional[str]:
    """The tenant id for this email's institution, creating unknown .edu.my institutions; None for private emails."""
    host = _email_host(email)
    if "." not in host:
        return None

    candidates = _candidate_domains(host)
    stored = db.query(Tenant).filter(Tenant.email_domain.in_(candidates)).all()
    if stored:
        # Longest (most specific) domain wins
        return max(stored, key=lambda t: len(t.email_domain)).id

    alias = _known_alias(host)
    if alias and db.query(Tenant).filter(Tenant.id == alias).first():
        return alias

    if not host.endswith(AUTO_SUFFIX):
        return None
    label = host[: -len(AUTO_SUFFIX)].rpartition(".")[2]
    if not _LABEL_RE.match(label):
        return None
    domain = f"{label}{AUTO_SUFFIX}"
    tenant_id = f"inst-{label}"[:64]
    try:
        db.add(Tenant(id=tenant_id, name=f"{label.upper()} ({domain})", short_name=label.upper()[:64],
                      email_domain=domain, kind="auto"))
        db.commit()
        logger.info("Auto-created institution tenant for domain %s", domain)
    except IntegrityError:
        # Created at the same moment by another sign-up (or the id is taken): use the existing row
        db.rollback()
        existing = db.query(Tenant).filter(Tenant.email_domain == domain).first()
        if existing:
            return existing.id
        return tenant_id if db.query(Tenant).filter(Tenant.id == tenant_id).first() else None
    return tenant_id
