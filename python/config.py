"""
Central configuration for the
Engineering Portfolio Management & Delivery Intelligence Platform.

All synthetic-data generation scripts use this file for shared
paths, dataset sizes, dates, business rules, and reproducibility.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RAW_BACKUP_DIR = DATA_DIR / "raw_backup"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORT_DATA_DIR = DATA_DIR / "exports"

SQL_DIR = PROJECT_ROOT / "sql"
POWERBI_DIR = PROJECT_ROOT / "powerbi"
EXCEL_DIR = PROJECT_ROOT / "excel"
DOCS_DIR = PROJECT_ROOT / "docs"
IMAGES_DIR = PROJECT_ROOT / "images"


# ============================================================
# REPRODUCIBILITY
# ============================================================

RANDOM_SEED = 42


# ============================================================
# FICTIONAL ORGANIZATION
# ============================================================

COMPANY_NAME = "Northstar Digital Systems"

COMPANY_INDUSTRY = (
    "Enterprise Cloud and Software Technology"
)

COMPANY_DESCRIPTION = (
    "A fictional global technology organization used to simulate "
    "enterprise engineering portfolio management."
)


# ============================================================
# REPORTING PERIOD
# ============================================================

DATA_START_DATE = "2024-01-01"
DATA_END_DATE = "2026-08-31"


# ============================================================
# EXISTING MASTER DATA VOLUMES
# ============================================================

NUM_PROGRAMS = 10
NUM_PROJECTS = 50
NUM_PRODUCTS = 25
NUM_TEAMS = 20
NUM_EMPLOYEES = 250
NUM_STAKEHOLDERS = 150


# ============================================================
# DELIVERY DATA TARGETS
# ============================================================

TARGET_SPRINTS = 500

TARGET_EPICS = 250
TARGET_FEATURES = 1_000
TARGET_USER_STORIES = 8_000
TARGET_TASKS = 25_000
TARGET_BUGS = 8_000

TARGET_RELEASES = 150
TARGET_DEPENDENCIES = 500


# ============================================================
# GOVERNANCE DATA TARGETS
# ============================================================

TARGET_RISKS = 1_200
TARGET_MEETINGS = 3_000
TARGET_ACTION_ITEMS = 10_000
TARGET_DECISIONS = 2_000
TARGET_OKRS = 500
TARGET_ROADMAP_ITEMS = 500


# ============================================================
# AGILE SETTINGS
# ============================================================

SPRINT_LENGTH_DAYS = 14

STANDARD_WEEKLY_HOURS = 40

MIN_STORY_POINTS = 1
MAX_STORY_POINTS = 13


# ============================================================
# TEAM SETTINGS
# ============================================================

MIN_TEAM_SIZE = 10
MAX_TEAM_SIZE = 15

MIN_VELOCITY_TARGET = 30
MAX_VELOCITY_TARGET = 70


# ============================================================
# WORK ITEM TYPES
# ============================================================

WORK_ITEM_TYPES = [
    "Epic",
    "Feature",
    "User Story",
    "Task",
    "Bug",
]


WORK_ITEM_STATES = [
    "New",
    "Active",
    "Resolved",
    "Closed",
    "Removed",
]


# ============================================================
# PRIORITIES
# ============================================================

PRIORITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]


# ============================================================
# BUG SEVERITIES
# ============================================================

BUG_SEVERITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]


# ============================================================
# HEALTH STATUS
# ============================================================

HEALTH_STATUSES = [
    "Green",
    "Amber",
    "Red",
]


# ============================================================
# RELEASE STATUS
# ============================================================

RELEASE_STATUSES = [
    "Planned",
    "In Development",
    "Testing",
    "Ready for Release",
    "Released",
    "Delayed",
]


# ============================================================
# RISK SETTINGS
# ============================================================

RISK_CATEGORIES = [
    "Schedule",
    "Budget",
    "Resource",
    "Technical",
    "Security",
    "Dependency",
    "Quality",
    "Scope",
    "Vendor",
]


RISK_STATUSES = [
    "Open",
    "Mitigating",
    "Monitoring",
    "Closed",
]


# ============================================================
# ACTION ITEM STATUS
# ============================================================

ACTION_STATUSES = [
    "Open",
    "In Progress",
    "Blocked",
    "Completed",
]


# ============================================================
# MEETING TYPES
# ============================================================

MEETING_TYPES = [
    "Sprint Planning",
    "Daily Scrum",
    "Sprint Review",
    "Sprint Retrospective",
    "Program Review",
    "Monthly Business Review",
    "Risk Review",
    "Release Readiness Review",
    "Architecture Review",
    "Stakeholder Review",
]


# ============================================================
# ANALYTICS THRESHOLDS
# ============================================================

GREEN_RISK_SCORE_MAX = 6
AMBER_RISK_SCORE_MAX = 12

LOW_CAPACITY_THRESHOLD = 75

HIGH_BUG_RATE_THRESHOLD = 0.15

SPRINT_SPILLOVER_WARNING_THRESHOLD = 0.20

BUDGET_WARNING_THRESHOLD = 0.90


# ============================================================
# CREATE REQUIRED DIRECTORIES IF MISSING
# ============================================================

DIRECTORIES = [
    DATA_DIR,
    RAW_DATA_DIR,
    RAW_BACKUP_DIR,
    PROCESSED_DATA_DIR,
    EXPORT_DATA_DIR,
    SQL_DIR,
    POWERBI_DIR,
    EXCEL_DIR,
    DOCS_DIR,
    IMAGES_DIR,
]


for directory in DIRECTORIES:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# CONFIGURATION TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "ENGINEERING PORTFOLIO MANAGEMENT "
        "& DELIVERY INTELLIGENCE PLATFORM"
    )
    print("=" * 70)

    print(
        f"\nCompany       : {COMPANY_NAME}"
    )

    print(
        f"Data Period   : "
        f"{DATA_START_DATE} to {DATA_END_DATE}"
    )

    print(
        f"Programs      : {NUM_PROGRAMS}"
    )

    print(
        f"Projects      : {NUM_PROJECTS}"
    )

    print(
        f"Teams         : {NUM_TEAMS}"
    )

    print(
        f"Employees     : {NUM_EMPLOYEES}"
    )

    print(
        f"Stakeholders  : {NUM_STAKEHOLDERS}"
    )

    print(
        f"Target Sprints: {TARGET_SPRINTS}"
    )

    print(
        f"Work Items    : "
        f"{TARGET_EPICS + TARGET_FEATURES + TARGET_USER_STORIES + TARGET_TASKS + TARGET_BUGS:,}"
    )

    print(
        f"\nProject Root:"
        f"\n{PROJECT_ROOT}"
    )

    print(
        f"\nRaw Data:"
        f"\n{RAW_DATA_DIR}"
    )

    print(
        f"\nBackup:"
        f"\n{RAW_BACKUP_DIR}"
    )

    print(
        "\nConfiguration loaded successfully!"
    )