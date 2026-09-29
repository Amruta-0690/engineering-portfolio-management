"""
Generate governance and program-management data for the
Engineering Portfolio Management & Delivery Intelligence Platform.

Governance datasets:
1. Risks
2. Meetings
3. Action Items
4. Decisions
5. OKRs
6. Roadmap Items
"""

import random

import numpy as np
import pandas as pd

from python import config


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(
    config.RANDOM_SEED + 300
)

np.random.seed(
    config.RANDOM_SEED + 300
)


# ============================================================
# SOURCE FILES
# ============================================================

PROJECTS_FILE = (
    config.RAW_DATA_DIR
    / "projects.csv"
)

SPRINTS_FILE = (
    config.RAW_DATA_DIR
    / "sprints.csv"
)

WORK_ITEMS_FILE = (
    config.RAW_DATA_DIR
    / "work_items.csv"
)

RELEASES_FILE = (
    config.RAW_DATA_DIR
    / "releases.csv"
)

DEPENDENCIES_FILE = (
    config.RAW_DATA_DIR
    / "dependencies.csv"
)


# ============================================================
# VALIDATE SOURCE FILES
# ============================================================

required_files = [
    PROJECTS_FILE,
    SPRINTS_FILE,
    WORK_ITEMS_FILE,
    RELEASES_FILE,
    DEPENDENCIES_FILE,
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required source file missing: "
            f"{file_path}"
        )


print("=" * 70)

print(
    "GOVERNANCE DATA GENERATOR"
)

print("=" * 70)

print(
    "\nAll required delivery source files found."
)

print(
    "Governance generator initialized successfully!"
)

# ============================================================
# RISK MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - RISKS")
print("=" * 70)


# ============================================================
# LOAD SOURCE DATA
# ============================================================

projects_df = pd.read_csv(
    PROJECTS_FILE,
    parse_dates=[
        "StartDate",
        "PlannedEndDate",
    ],
)

sprints_df = pd.read_csv(
    SPRINTS_FILE,
    parse_dates=[
        "StartDate",
        "EndDate",
    ],
)

work_items_df = pd.read_csv(
    WORK_ITEMS_FILE,
)

releases_df = pd.read_csv(
    RELEASES_FILE,
    parse_dates=[
        "PlannedReleaseDate",
        "ForecastReleaseDate",
        "ActualReleaseDate",
    ],
)

dependencies_df = pd.read_csv(
    DEPENDENCIES_FILE,
    parse_dates=[
        "CreatedDate",
        "PlannedResolutionDate",
        "ForecastResolutionDate",
        "ActualResolutionDate",
    ],
)


# ============================================================
# SOURCE VALIDATION
# ============================================================

assert projects_df[
    "ProjectID"
].is_unique, (
    "Duplicate ProjectID detected."
)

assert len(
    projects_df
) == config.NUM_PROJECTS, (
    "Unexpected project count."
)

assert len(
    sprints_df
) == config.TARGET_SPRINTS, (
    "Unexpected sprint count."
)

assert len(
    work_items_df
) == (
    config.TARGET_EPICS
    + config.TARGET_FEATURES
    + config.TARGET_USER_STORIES
    + config.TARGET_TASKS
    + config.TARGET_BUGS
), (
    "Unexpected work-item count."
)

assert len(
    releases_df
) == config.TARGET_RELEASES, (
    "Unexpected release count."
)

assert len(
    dependencies_df
) == config.TARGET_DEPENDENCIES, (
    "Unexpected dependency count."
)


# ============================================================
# PROJECT DELIVERY METRICS
# ============================================================

project_sprint_metrics = (
    sprints_df
    .groupby(
        "ProjectID"
    )
    .agg(
        AverageCompletionPercent=(
            "CompletionPercent",
            "mean",
        ),
        AverageCapacityPercent=(
            "CapacityUtilizationPercent",
            "mean",
        ),
        TotalSpilloverStoryPoints=(
            "SpilloverStoryPoints",
            "sum",
        ),
    )
)


# ============================================================
# PROJECT BUG METRICS
# ============================================================

bugs_df = work_items_df[
    work_items_df[
        "WorkItemType"
    ]
    == "Bug"
].copy()


bugs_df[
    "IsOpenBug"
] = ~bugs_df[
    "State"
].isin(
    [
        "Resolved",
        "Closed",
    ]
)


bugs_df[
    "IsCriticalBug"
] = (
    bugs_df[
        "Severity"
    ]
    == "Critical"
)


project_bug_metrics = (
    bugs_df
    .groupby(
        "ProjectID"
    )
    .agg(
        TotalBugs=(
            "WorkItemID",
            "count",
        ),
        OpenBugs=(
            "IsOpenBug",
            "sum",
        ),
        CriticalBugs=(
            "IsCriticalBug",
            "sum",
        ),
    )
)


# ============================================================
# PROJECT RELEASE METRICS
# ============================================================

project_release_metrics = (
    releases_df
    .groupby(
        "ProjectID"
    )
    .agg(
        AverageReleaseDelay=(
            "DelayDays",
            "mean",
        ),
        MaximumReleaseDelay=(
            "DelayDays",
            "max",
        ),
        AverageReadiness=(
            "ReadinessPercent",
            "mean",
        ),
    )
)


# ============================================================
# PROJECT DEPENDENCY METRICS
# ============================================================

dependent_metrics = (
    dependencies_df
    .groupby(
        "DependentProjectID"
    )
    .agg(
        DependencyCount=(
            "DependencyID",
            "count",
        ),
        BlockedDependencies=(
            "DependencyStatus",
            lambda values: (
                values
                == "Blocked"
            ).sum(),
        ),
        HighImpactDependencies=(
            "ReleaseImpact",
            lambda values: (
                values
                == "High"
            ).sum(),
        ),
    )
)


# ============================================================
# BUILD PROJECT RISK PROFILE
# ============================================================

project_risk_profiles = {}


for _, project in projects_df.iterrows():

    project_id = int(
        project[
            "ProjectID"
        ]
    )


    sprint_metrics = (
        project_sprint_metrics
        .loc[
            project_id
        ]
    )


    bug_metrics = (
        project_bug_metrics
        .loc[
            project_id
        ]
        if project_id
        in project_bug_metrics.index
        else None
    )


    release_metrics = (
        project_release_metrics
        .loc[
            project_id
        ]
    )


    dependency_metrics = (
        dependent_metrics
        .loc[
            project_id
        ]
        if project_id
        in dependent_metrics.index
        else None
    )


    average_completion = float(
        sprint_metrics[
            "AverageCompletionPercent"
        ]
    )


    average_capacity = float(
        sprint_metrics[
            "AverageCapacityPercent"
        ]
    )


    spillover = int(
        sprint_metrics[
            "TotalSpilloverStoryPoints"
        ]
    )


    open_bugs = (
        int(
            bug_metrics[
                "OpenBugs"
            ]
        )
        if bug_metrics is not None
        else 0
    )


    critical_bugs = (
        int(
            bug_metrics[
                "CriticalBugs"
            ]
        )
        if bug_metrics is not None
        else 0
    )


    average_release_delay = float(
        release_metrics[
            "AverageReleaseDelay"
        ]
    )


    average_readiness = float(
        release_metrics[
            "AverageReadiness"
        ]
    )


    blocked_dependencies = (
        int(
            dependency_metrics[
                "BlockedDependencies"
            ]
        )
        if dependency_metrics is not None
        else 0
    )


    high_impact_dependencies = (
        int(
            dependency_metrics[
                "HighImpactDependencies"
            ]
        )
        if dependency_metrics is not None
        else 0
    )


    project_risk_profiles[
        project_id
    ] = {
        "AverageCompletion":
            average_completion,

        "AverageCapacity":
            average_capacity,

        "Spillover":
            spillover,

        "OpenBugs":
            open_bugs,

        "CriticalBugs":
            critical_bugs,

        "AverageReleaseDelay":
            average_release_delay,

        "AverageReadiness":
            average_readiness,

        "BlockedDependencies":
            blocked_dependencies,

        "HighImpactDependencies":
            high_impact_dependencies,
    }


# ============================================================
# RISK DEFINITIONS
# ============================================================

RISK_DEFINITIONS = {
    "Schedule": [
        "Delivery milestone may miss committed date",
        "Sprint spillover may affect project schedule",
        "Release timeline may exceed planned date",
    ],

    "Budget": [
        "Forecast delivery cost may exceed budget",
        "Additional engineering effort may increase cost",
        "Schedule variance may create budget pressure",
    ],

    "Resource": [
        "Team capacity may be insufficient for planned scope",
        "Resource constraints may reduce delivery velocity",
        "Specialized engineering capacity may be unavailable",
    ],

    "Technical": [
        "Technical complexity may delay implementation",
        "Architecture constraints may affect delivery",
        "Platform integration may require additional effort",
    ],

    "Security": [
        "Security remediation may delay release readiness",
        "Security control implementation may require rework",
        "Security validation may identify release blockers",
    ],

    "Dependency": [
        "Cross-project dependency may delay delivery",
        "Blocked dependency may affect release milestone",
        "External team dependency may delay implementation",
    ],

    "Quality": [
        "Defect volume may affect release readiness",
        "Critical defects may block production release",
        "Quality issues may increase engineering rework",
    ],

    "Scope": [
        "Scope growth may affect committed delivery",
        "Requirement changes may increase delivery effort",
        "Feature expansion may affect milestone completion",
    ],

    "Vendor": [
        "External provider dependency may affect schedule",
        "Vendor delivery timing may impact implementation",
        "Third-party service readiness may delay release",
    ],
}


MITIGATION_PLANS = {
    "Schedule":
        "Rebaseline milestones, prioritize critical scope, "
        "and review schedule variance weekly.",

    "Budget":
        "Review forecast spend, control scope growth, "
        "and escalate material budget variance.",

    "Resource":
        "Rebalance team capacity, prioritize critical work, "
        "and secure required specialist support.",

    "Technical":
        "Complete architecture review, reduce technical "
        "uncertainty, and track engineering blockers.",

    "Security":
        "Prioritize security remediation and complete "
        "required validation before release approval.",

    "Dependency":
        "Assign dependency owners, track resolution dates, "
        "and escalate blocked cross-team dependencies.",

    "Quality":
        "Prioritize critical defects, expand regression "
        "coverage, and review defect trends.",

    "Scope":
        "Apply change control, prioritize committed scope, "
        "and defer lower-value requirements when needed.",

    "Vendor":
        "Review vendor milestones, establish contingency "
        "plans, and escalate missed external commitments.",
}


# ============================================================
# PROJECT RISK WEIGHT
# ============================================================

project_ids = (
    projects_df[
        "ProjectID"
    ]
    .astype(int)
    .tolist()
)


project_weights = []


for project_id in project_ids:

    profile = (
        project_risk_profiles[
            project_id
        ]
    )


    weight = 1.0


    if (
        profile[
            "AverageCompletion"
        ]
        < 85
    ):
        weight += 1.5


    if (
        profile[
            "AverageCapacity"
        ]
        < 85
    ):
        weight += 1.0


    if (
        profile[
            "Spillover"
        ]
        >= 50
    ):
        weight += 1.0


    if (
        profile[
            "CriticalBugs"
        ]
        >= 5
    ):
        weight += 1.5


    if (
        profile[
            "AverageReleaseDelay"
        ]
        >= 10
    ):
        weight += 1.5


    if (
        profile[
            "BlockedDependencies"
        ]
        >= 2
    ):
        weight += 1.5


    project_weights.append(
        weight
    )


# ============================================================
# GENERATE 1,200 RISKS
# ============================================================

risks = []


for risk_id in range(
    1,
    config.TARGET_RISKS + 1,
):

    project_id = int(
        random.choices(
            population=project_ids,
            weights=project_weights,
            k=1,
        )[0]
    )


    project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == project_id
        ]
        .iloc[0]
    )


    profile = (
        project_risk_profiles[
            project_id
        ]
    )


    # --------------------------------------------------------
    # CATEGORY / TRIGGER
    # --------------------------------------------------------

    category_weights = {
        "Schedule": 10,
        "Budget": 7,
        "Resource": 9,
        "Technical": 10,
        "Security": 7,
        "Dependency": 10,
        "Quality": 10,
        "Scope": 8,
        "Vendor": 4,
    }


    if (
        profile[
            "AverageCompletion"
        ]
        < 85
        or profile[
            "Spillover"
        ]
        >= 50
    ):

        category_weights[
            "Schedule"
        ] += 15


    if (
        profile[
            "AverageCapacity"
        ]
        < 85
    ):

        category_weights[
            "Resource"
        ] += 15


    if (
        profile[
            "CriticalBugs"
        ]
        >= 5
    ):

        category_weights[
            "Quality"
        ] += 18


    if (
        profile[
            "BlockedDependencies"
        ]
        >= 2
        or profile[
            "HighImpactDependencies"
        ]
        >= 3
    ):

        category_weights[
            "Dependency"
        ] += 18


    if (
        profile[
            "AverageReleaseDelay"
        ]
        >= 10
    ):

        category_weights[
            "Schedule"
        ] += 10


    risk_category = random.choices(
        population=list(
            category_weights.keys()
        ),
        weights=list(
            category_weights.values()
        ),
        k=1,
    )[0]


    if risk_category == "Schedule":

        trigger_source = (
            "Sprint / Release Performance"
        )


    elif risk_category == "Resource":

        trigger_source = (
            "Capacity Analysis"
        )


    elif risk_category == "Quality":

        trigger_source = (
            "Defect Analysis"
        )


    elif risk_category == "Dependency":

        trigger_source = (
            "Dependency Review"
        )


    elif risk_category == "Budget":

        trigger_source = (
            "Budget Review"
        )


    elif risk_category == "Security":

        trigger_source = (
            "Security Review"
        )


    elif risk_category == "Scope":

        trigger_source = (
            "Scope Review"
        )


    elif risk_category == "Vendor":

        trigger_source = (
            "Vendor Review"
        )


    else:

        trigger_source = (
            "Technical Review"
        )


    # --------------------------------------------------------
    # PROBABILITY / IMPACT
    # --------------------------------------------------------

    exposure_boost = 0


    if (
        profile[
            "AverageCompletion"
        ]
        < 85
    ):
        exposure_boost += 1


    if (
        profile[
            "AverageCapacity"
        ]
        < 85
    ):
        exposure_boost += 1


    if (
        profile[
            "CriticalBugs"
        ]
        >= 5
    ):
        exposure_boost += 1


    if (
        profile[
            "AverageReleaseDelay"
        ]
        >= 10
    ):
        exposure_boost += 1


    if (
        profile[
            "BlockedDependencies"
        ]
        >= 2
    ):
        exposure_boost += 1


    probability = int(
        np.clip(
            random.choices(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                ],
                weights=[
                    8,
                    20,
                    35,
                    25,
                    12,
                ],
                k=1,
            )[0]
            +
            (
                1
                if exposure_boost >= 3
                and random.random() < 0.45
                else 0
            ),
            1,
            5,
        )
    )


    impact = int(
        np.clip(
            random.choices(
                [
                    1,
                    2,
                    3,
                    4,
                    5,
                ],
                weights=[
                    5,
                    15,
                    35,
                    30,
                    15,
                ],
                k=1,
            )[0]
            +
            (
                1
                if exposure_boost >= 4
                and random.random() < 0.50
                else 0
            ),
            1,
            5,
        )
    )


    risk_score = (
        probability
        * impact
    )


    if risk_score <= 6:

        risk_rating = "Low"


    elif risk_score <= 12:

        risk_rating = "Medium"


    elif risk_score <= 19:

        risk_rating = "High"


    else:

        risk_rating = "Critical"


    # --------------------------------------------------------
    # RISK DATES
    # --------------------------------------------------------

    project_start = pd.Timestamp(
        project[
            "StartDate"
        ]
    )


    project_end = pd.Timestamp(
        project[
            "PlannedEndDate"
        ]
    )


    data_end = pd.Timestamp(
        config.DATA_END_DATE
    )


    latest_identified_date = min(
        project_end,
        data_end,
    )


    available_identification_days = max(
        0,
        (
            latest_identified_date
            - project_start
        ).days,
    )


    identified_date = (
        project_start
        + pd.Timedelta(
            days=random.randint(
                0,
                available_identification_days,
            )
        )
    )


    mitigation_window = random.randint(
        14,
        90,
    )


    target_mitigation_date = (
        identified_date
        + pd.Timedelta(
            days=mitigation_window
        )
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    age_days = (
        data_end
        - identified_date
    ).days


    if (
        age_days > 120
        and random.random() < 0.65
    ):

        risk_status = "Closed"


    elif risk_score >= 13:

        risk_status = random.choices(
            [
                "Open",
                "Mitigating",
                "Monitoring",
            ],
            weights=[
                25,
                55,
                20,
            ],
            k=1,
        )[0]


    else:

        risk_status = random.choices(
            [
                "Open",
                "Mitigating",
                "Monitoring",
            ],
            weights=[
                20,
                35,
                45,
            ],
            k=1,
        )[0]


    if risk_status == "Closed":

        earliest_close_date = (
            identified_date
            + pd.Timedelta(
                days=7
            )
        )


        latest_close_date = min(
            data_end,
            target_mitigation_date
            + pd.Timedelta(
                days=30
            ),
        )


        if (
            earliest_close_date
            <= latest_close_date
        ):

            close_days = (
                latest_close_date
                - earliest_close_date
            ).days


            closed_date = (
                earliest_close_date
                + pd.Timedelta(
                    days=random.randint(
                        0,
                        close_days,
                    )
                )
            )


        else:

            closed_date = (
                latest_close_date
            )


    else:

        closed_date = pd.NaT


    # --------------------------------------------------------
    # RESIDUAL RISK
    # --------------------------------------------------------

    if risk_status == "Closed":

        reduction = random.randint(
            2,
            min(
                8,
                max(
                    2,
                    risk_score - 1,
                ),
            ),
        )


    elif risk_status == "Mitigating":

        reduction = random.randint(
            1,
            min(
                5,
                max(
                    1,
                    risk_score - 1,
                ),
            ),
        )


    elif risk_status == "Monitoring":

        reduction = random.randint(
            0,
            min(
                3,
                max(
                    0,
                    risk_score - 1,
                ),
            ),
        )


    else:

        reduction = random.randint(
            0,
            min(
                2,
                max(
                    0,
                    risk_score - 1,
                ),
            ),
        )


    residual_risk_score = max(
        1,
        risk_score - reduction,
    )


    # --------------------------------------------------------
    # OWNER
    # --------------------------------------------------------

    owner = str(
        project[
            "ProjectManager"
        ]
    )


    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    risks.append(
        {
            "RiskID":
                risk_id,

            "ProjectID":
                project_id,

            "RiskCategory":
                risk_category,

            "RiskTitle":
                random.choice(
                    RISK_DEFINITIONS[
                        risk_category
                    ]
                ),

            "Probability":
                probability,

            "Impact":
                impact,

            "RiskScore":
                risk_score,

            "RiskRating":
                risk_rating,

            "RiskStatus":
                risk_status,

            "Owner":
                owner,

            "IdentifiedDate":
                identified_date.date(),

            "TargetMitigationDate":
                target_mitigation_date.date(),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),

            "MitigationPlan":
                MITIGATION_PLANS[
                    risk_category
                ],

            "TriggerSource":
                trigger_source,

            "ResidualRiskScore":
                residual_risk_score,
        }
    )


# ============================================================
# CREATE RISK DATAFRAME
# ============================================================

risks_df = pd.DataFrame(
    risks
)


# ============================================================
# RISK VALIDATION
# ============================================================

assert len(
    risks_df
) == config.TARGET_RISKS, (
    "Incorrect risk count."
)


assert risks_df[
    "RiskID"
].is_unique, (
    "Duplicate RiskID detected."
)


valid_project_ids = set(
    projects_df[
        "ProjectID"
    ]
)


assert set(
    risks_df[
        "ProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid ProjectID found in risks."
)


assert risks_df[
    "Probability"
].between(
    1,
    5,
).all(), (
    "Invalid risk probability."
)


assert risks_df[
    "Impact"
].between(
    1,
    5,
).all(), (
    "Invalid risk impact."
)


assert (
    risks_df[
        "RiskScore"
    ]
    ==
    (
        risks_df[
            "Probability"
        ]
        *
        risks_df[
            "Impact"
        ]
    )
).all(), (
    "Risk score calculation is incorrect."
)


assert risks_df[
    "RiskScore"
].between(
    1,
    25,
).all(), (
    "Risk score outside valid range."
)


assert (
    risks_df[
        "ResidualRiskScore"
    ]
    <=
    risks_df[
        "RiskScore"
    ]
).all(), (
    "Residual risk exceeds original risk."
)


assert (
    risks_df[
        "ResidualRiskScore"
    ]
    >= 1
).all(), (
    "Invalid residual risk score."
)


risk_dates_df = (
    risks_df.copy()
)


for date_column in [
    "IdentifiedDate",
    "TargetMitigationDate",
    "ClosedDate",
]:

    risk_dates_df[
        date_column
    ] = pd.to_datetime(
        risk_dates_df[
            date_column
        ]
    )


assert (
    risk_dates_df[
        "TargetMitigationDate"
    ]
    >=
    risk_dates_df[
        "IdentifiedDate"
    ]
).all(), (
    "Risk mitigation date occurs "
    "before identification."
)


closed_risks = (
    risk_dates_df[
        risk_dates_df[
            "ClosedDate"
        ].notna()
    ]
)


assert (
    closed_risks[
        "ClosedDate"
    ]
    >=
    closed_risks[
        "IdentifiedDate"
    ]
).all(), (
    "Risk closed before identification."
)


assert (
    risks_df.loc[
        risks_df[
            "RiskStatus"
        ]
        == "Closed",
        "ClosedDate",
    ]
    .notna()
    .all()
), (
    "Closed risk is missing ClosedDate."
)


assert (
    risks_df.loc[
        risks_df[
            "RiskStatus"
        ]
        != "Closed",
        "ClosedDate",
    ]
    .isna()
    .all()
), (
    "Open risk contains ClosedDate."
)


# ============================================================
# EXPORT RISKS
# ============================================================

RISKS_FILE = (
    config.RAW_DATA_DIR
    / "risks.csv"
)


risks_df.to_csv(
    RISKS_FILE,
    index=False,
)


# ============================================================
# RISK SUMMARY
# ============================================================

print(
    f"\nRisks generated       : "
    f"{len(risks_df):,}"
)


print(
    f"Projects represented  : "
    f"{risks_df['ProjectID'].nunique()}"
)


print(
    f"Average risk score    : "
    f"{risks_df['RiskScore'].mean():.2f}"
)


print(
    f"Average residual risk : "
    f"{risks_df['ResidualRiskScore'].mean():.2f}"
)


print(
    "\nRisk Rating Distribution:"
)


print(
    risks_df[
        "RiskRating"
    ].value_counts()
)


print(
    "\nRisk Status Distribution:"
)


print(
    risks_df[
        "RiskStatus"
    ].value_counts()
)


print(
    "\nRisk Category Distribution:"
)


print(
    risks_df[
        "RiskCategory"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{RISKS_FILE}"
)


print(
    "\nRisk validation passed."
)


print(
    "risks.csv generated successfully!"
)

# ============================================================
# MEETING MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - MEETINGS")
print("=" * 70)


# ============================================================
# LOAD STAKEHOLDER DATA
# ============================================================

STAKEHOLDERS_FILE = (
    config.RAW_DATA_DIR
    / "stakeholders.csv"
)

PROJECT_STAKEHOLDERS_FILE = (
    config.RAW_DATA_DIR
    / "project_stakeholder_assignments.csv"
)


for file_path in [
    STAKEHOLDERS_FILE,
    PROJECT_STAKEHOLDERS_FILE,
]:

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required source file missing: "
            f"{file_path}"
        )


stakeholders_df = pd.read_csv(
    STAKEHOLDERS_FILE
)

project_stakeholders_df = pd.read_csv(
    PROJECT_STAKEHOLDERS_FILE,
    parse_dates=[
        "AssignmentStartDate",
        "AssignmentEndDate",
    ],
)


# ============================================================
# MEETING SETTINGS
# ============================================================

MEETING_DURATION = {
    "Sprint Planning": 60,
    "Daily Scrum": 30,
    "Sprint Review": 60,
    "Sprint Retrospective": 45,
    "Program Review": 60,
    "Monthly Business Review": 90,
    "Risk Review": 60,
    "Release Readiness Review": 60,
    "Architecture Review": 75,
    "Stakeholder Review": 60,
}


MEETING_AGENDAS = {
    "Sprint Planning":
        "Review sprint scope, capacity, priorities, "
        "and delivery commitments.",

    "Daily Scrum":
        "Review delivery progress, blockers, "
        "dependencies, and immediate priorities.",

    "Sprint Review":
        "Review completed work, demonstrations, "
        "feedback, and outstanding scope.",

    "Sprint Retrospective":
        "Review delivery outcomes, improvement areas, "
        "and team actions.",

    "Program Review":
        "Review program health, milestones, risks, "
        "dependencies, and executive decisions.",

    "Monthly Business Review":
        "Review portfolio performance, KPIs, delivery "
        "health, risks, budget, and strategic outcomes.",

    "Risk Review":
        "Review open risks, exposure, mitigation plans, "
        "owners, and escalation requirements.",

    "Release Readiness Review":
        "Review release readiness, defects, dependencies, "
        "testing status, and go-live decision.",

    "Architecture Review":
        "Review technical design, integration decisions, "
        "architecture risks, and implementation approach.",

    "Stakeholder Review":
        "Review project progress, decisions, concerns, "
        "milestones, and stakeholder expectations.",
}


# ============================================================
# PROJECT -> STAKEHOLDER LOOKUP
# ============================================================

stakeholder_name_lookup = (
    stakeholders_df
    .set_index(
        "StakeholderID"
    )[
        "StakeholderName"
    ]
    .to_dict()
)


project_stakeholder_lookup = {}


for project_id, group in (
    project_stakeholders_df
    .groupby(
        "ProjectID"
    )
):

    project_stakeholder_lookup[
        int(project_id)
    ] = (
        group[
            "StakeholderID"
        ]
        .astype(int)
        .tolist()
    )


# ============================================================
# PROJECT -> RISK METRICS
# ============================================================

project_risk_metrics = (
    risks_df
    .groupby(
        "ProjectID"
    )
    .agg(
        OpenRiskCount=(
            "RiskStatus",
            lambda values: (
                values
                != "Closed"
            ).sum(),
        ),
        HighCriticalRiskCount=(
            "RiskRating",
            lambda values: (
                values.isin(
                    [
                        "High",
                        "Critical",
                    ]
                )
            ).sum(),
        ),
    )
)


# ============================================================
# MEETING TYPE SELECTION
# ============================================================

def choose_meeting_type(
    project_id,
):
    """
    Select a meeting type with additional
    weight for risk and release governance
    when project conditions justify it.
    """

    weights = {
        "Sprint Planning": 14,
        "Daily Scrum": 10,
        "Sprint Review": 12,
        "Sprint Retrospective": 10,
        "Program Review": 10,
        "Monthly Business Review": 7,
        "Risk Review": 10,
        "Release Readiness Review": 10,
        "Architecture Review": 8,
        "Stakeholder Review": 9,
    }


    if project_id in (
        project_risk_metrics.index
    ):

        risk_metrics = (
            project_risk_metrics
            .loc[
                project_id
            ]
        )


        if (
            int(
                risk_metrics[
                    "HighCriticalRiskCount"
                ]
            )
            >= 5
        ):

            weights[
                "Risk Review"
            ] += 12


    release_metrics = (
        releases_df[
            releases_df[
                "ProjectID"
            ]
            == project_id
        ]
    )


    if not release_metrics.empty:

        if (
            release_metrics[
                "DelayDays"
            ].max()
            >= 10
        ):

            weights[
                "Release Readiness Review"
            ] += 10


    return random.choices(
        population=list(
            weights.keys()
        ),
        weights=list(
            weights.values()
        ),
        k=1,
    )[0]


# ============================================================
# GENERATE 3,000 MEETINGS
# ============================================================

meetings = []


project_ids = (
    projects_df[
        "ProjectID"
    ]
    .astype(int)
    .tolist()
)


for meeting_id in range(
    1,
    config.TARGET_MEETINGS + 1,
):

    project_id = int(
        random.choice(
            project_ids
        )
    )


    project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == project_id
        ]
        .iloc[0]
    )


    program_id = int(
        project[
            "ProgramID"
        ]
    )


    project_start = pd.Timestamp(
        project[
            "StartDate"
        ]
    )


    project_end = min(
        pd.Timestamp(
            project[
                "PlannedEndDate"
            ]
        ),
        pd.Timestamp(
            config.DATA_END_DATE
        ),
    )


    available_days = max(
        0,
        (
            project_end
            - project_start
        ).days,
    )


    meeting_date = (
        project_start
        + pd.Timedelta(
            days=random.randint(
                0,
                available_days,
            )
        )
    )


    meeting_type = (
        choose_meeting_type(
            project_id
        )
    )


    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if meeting_type in [
        "Program Review",
        "Monthly Business Review",
        "Stakeholder Review",
    ]:

        organizer = str(
            project[
                "ProjectManager"
            ]
        )


    elif meeting_type in [
        "Risk Review",
        "Release Readiness Review",
    ]:

        organizer = str(
            project[
                "ProjectManager"
            ]
        )


    else:

        organizer = str(
            project[
                "ProjectManager"
            ]
        )


    # --------------------------------------------------------
    # ATTENDEES
    # --------------------------------------------------------

    stakeholder_ids = (
        project_stakeholder_lookup
        .get(
            project_id,
            [],
        )
    )


    if stakeholder_ids:

        max_stakeholders = min(
            len(
                stakeholder_ids
            ),
            random.randint(
                2,
                6,
            ),
        )


        selected_stakeholder_ids = (
            random.sample(
                stakeholder_ids,
                k=max_stakeholders,
            )
        )


        stakeholder_attendees = [
            stakeholder_name_lookup[
                stakeholder_id
            ]
            for stakeholder_id
            in selected_stakeholder_ids
            if stakeholder_id
            in stakeholder_name_lookup
        ]


    else:

        stakeholder_attendees = []


    attendee_count = (
        len(
            stakeholder_attendees
        )
        +
        random.randint(
            3,
            10,
        )
    )


    # --------------------------------------------------------
    # MEETING OUTCOME
    # --------------------------------------------------------

    if meeting_type == "Risk Review":

        meeting_outcome = random.choice(
            [
                "Mitigation actions confirmed",
                "Risk exposure reviewed",
                "Escalation required",
                "Risk owners aligned",
            ]
        )


    elif meeting_type == (
        "Release Readiness Review"
    ):

        meeting_outcome = random.choice(
            [
                "Release approved",
                "Conditional approval",
                "Readiness actions required",
                "Release blockers identified",
            ]
        )


    elif meeting_type in [
        "Program Review",
        "Monthly Business Review",
    ]:

        meeting_outcome = random.choice(
            [
                "Portfolio actions confirmed",
                "Leadership decisions captured",
                "Delivery priorities aligned",
                "Escalations identified",
            ]
        )


    elif meeting_type == (
        "Architecture Review"
    ):

        meeting_outcome = random.choice(
            [
                "Architecture approved",
                "Design changes required",
                "Technical actions identified",
                "Additional review required",
            ]
        )


    else:

        meeting_outcome = random.choice(
            [
                "Delivery actions confirmed",
                "Team priorities aligned",
                "Blockers identified",
                "No major issues identified",
            ]
        )


    # --------------------------------------------------------
    # FOLLOW-UP
    # --------------------------------------------------------

    follow_up_required = (
        meeting_outcome
        not in [
            "Release approved",
            "Architecture approved",
            "No major issues identified",
        ]
    )


    if follow_up_required:

        follow_up_date = (
            meeting_date
            + pd.Timedelta(
                days=random.randint(
                    3,
                    14,
                )
            )
        )


    else:

        follow_up_date = pd.NaT


    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    meetings.append(
        {
            "MeetingID":
                meeting_id,

            "ProgramID":
                program_id,

            "ProjectID":
                project_id,

            "MeetingType":
                meeting_type,

            "MeetingDate":
                meeting_date.date(),

            "Organizer":
                organizer,

            "DurationMinutes":
                MEETING_DURATION[
                    meeting_type
                ],

            "AttendeeCount":
                attendee_count,

            "StakeholderAttendees":
                "; ".join(
                    stakeholder_attendees
                ),

            "Agenda":
                MEETING_AGENDAS[
                    meeting_type
                ],

            "MeetingOutcome":
                meeting_outcome,

            "FollowUpRequired":
                follow_up_required,

            "FollowUpDate":
                (
                    follow_up_date.date()
                    if pd.notna(
                        follow_up_date
                    )
                    else pd.NaT
                ),
        }
    )


# ============================================================
# CREATE MEETING DATAFRAME
# ============================================================

meetings_df = pd.DataFrame(
    meetings
)


# ============================================================
# MEETING VALIDATION
# ============================================================

assert len(
    meetings_df
) == config.TARGET_MEETINGS, (
    "Incorrect meeting count."
)


assert meetings_df[
    "MeetingID"
].is_unique, (
    "Duplicate MeetingID detected."
)


valid_project_ids = set(
    projects_df[
        "ProjectID"
    ]
)


valid_program_ids = set(
    projects_df[
        "ProgramID"
    ]
)


assert set(
    meetings_df[
        "ProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid ProjectID found in meetings."
)


assert set(
    meetings_df[
        "ProgramID"
    ]
).issubset(
    valid_program_ids
), (
    "Invalid ProgramID found in meetings."
)


# Project -> Program relationship must match.
project_program_lookup = (
    projects_df
    .set_index(
        "ProjectID"
    )[
        "ProgramID"
    ]
    .to_dict()
)


for _, meeting in (
    meetings_df.iterrows()
):

    assert (
        project_program_lookup[
            int(
                meeting[
                    "ProjectID"
                ]
            )
        ]
        ==
        int(
            meeting[
                "ProgramID"
            ]
        )
    ), (
        "Meeting ProgramID does not "
        "match ProjectID."
    )


assert (
    meetings_df[
        "DurationMinutes"
    ]
    > 0
).all(), (
    "Invalid meeting duration."
)


assert (
    meetings_df[
        "AttendeeCount"
    ]
    > 0
).all(), (
    "Invalid meeting attendee count."
)


meeting_dates_df = (
    meetings_df.copy()
)


meeting_dates_df[
    "MeetingDate"
] = pd.to_datetime(
    meeting_dates_df[
        "MeetingDate"
    ]
)


meeting_dates_df[
    "FollowUpDate"
] = pd.to_datetime(
    meeting_dates_df[
        "FollowUpDate"
    ]
)


follow_up_rows = (
    meeting_dates_df[
        meeting_dates_df[
            "FollowUpDate"
        ].notna()
    ]
)


assert (
    follow_up_rows[
        "FollowUpDate"
    ]
    >=
    follow_up_rows[
        "MeetingDate"
    ]
).all(), (
    "Follow-up date occurs "
    "before meeting date."
)


assert (
    meetings_df.loc[
        meetings_df[
            "FollowUpRequired"
        ]
        == True,
        "FollowUpDate",
    ]
    .notna()
    .all()
), (
    "Meeting requiring follow-up "
    "has no FollowUpDate."
)


assert (
    meetings_df.loc[
        meetings_df[
            "FollowUpRequired"
        ]
        == False,
        "FollowUpDate",
    ]
    .isna()
    .all()
), (
    "Meeting without follow-up "
    "contains FollowUpDate."
)


# ============================================================
# EXPORT MEETINGS
# ============================================================

MEETINGS_FILE = (
    config.RAW_DATA_DIR
    / "meetings.csv"
)


meetings_df.to_csv(
    MEETINGS_FILE,
    index=False,
)


# ============================================================
# MEETING SUMMARY
# ============================================================

print(
    f"\nMeetings generated    : "
    f"{len(meetings_df):,}"
)


print(
    f"Projects represented  : "
    f"{meetings_df['ProjectID'].nunique()}"
)


print(
    f"Programs represented  : "
    f"{meetings_df['ProgramID'].nunique()}"
)


print(
    f"Follow-ups required   : "
    f"{meetings_df['FollowUpRequired'].sum():,}"
)


print(
    "\nMeeting Type Distribution:"
)


print(
    meetings_df[
        "MeetingType"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{MEETINGS_FILE}"
)


print(
    "\nMeeting validation passed."
)


print(
    "meetings.csv generated successfully!"
)

# ============================================================
# ACTION ITEM MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - ACTION ITEMS")
print("=" * 70)


# ============================================================
# ACTION ITEM SETTINGS
# ============================================================

ACTION_DESCRIPTIONS = [
    "Resolve identified delivery blocker",
    "Complete technical follow-up",
    "Update project delivery plan",
    "Complete risk mitigation activity",
    "Validate release readiness item",
    "Resolve cross-team dependency",
    "Complete architecture follow-up",
    "Update stakeholder communication",
    "Complete defect remediation activity",
    "Review delivery milestone variance",
    "Confirm scope and priority",
    "Complete security remediation activity",
]


# ============================================================
# MEETING ACTION WEIGHTS
# ============================================================
#
# Meetings requiring follow-up should naturally
# produce more action items.
# ============================================================

meeting_ids = (
    meetings_df[
        "MeetingID"
    ]
    .astype(int)
    .tolist()
)


meeting_action_weights = []


for _, meeting in meetings_df.iterrows():

    weight = 1.0


    if bool(
        meeting[
            "FollowUpRequired"
        ]
    ):

        weight += 2.0


    if meeting[
        "MeetingType"
    ] in [
        "Risk Review",
        "Release Readiness Review",
        "Program Review",
        "Monthly Business Review",
        "Architecture Review",
    ]:

        weight += 1.0


    meeting_action_weights.append(
        weight
    )


# ============================================================
# MEETING LOOKUP
# ============================================================

meeting_lookup = (
    meetings_df
    .set_index(
        "MeetingID"
    )
)


# ============================================================
# PROJECT RISK LOOKUP
# ============================================================

project_high_risk_lookup = (
    risks_df[
        risks_df[
            "RiskRating"
        ].isin(
            [
                "High",
                "Critical",
            ]
        )
    ]
    .groupby(
        "ProjectID"
    )[
        "RiskID"
    ]
    .count()
    .to_dict()
)


# ============================================================
# GENERATE 10,000 ACTION ITEMS
# ============================================================

action_items = []


for action_id in range(
    1,
    config.TARGET_ACTION_ITEMS + 1,
):

    meeting_id = int(
        random.choices(
            population=meeting_ids,
            weights=meeting_action_weights,
            k=1,
        )[0]
    )


    meeting = meeting_lookup.loc[
        meeting_id
    ]


    project_id = int(
        meeting[
            "ProjectID"
        ]
    )


    program_id = int(
        meeting[
            "ProgramID"
        ]
    )


    meeting_date = pd.Timestamp(
        meeting[
            "MeetingDate"
        ]
    )


    meeting_type = str(
        meeting[
            "MeetingType"
        ]
    )


    # --------------------------------------------------------
    # PRIORITY
    # --------------------------------------------------------

    high_risk_count = int(
        project_high_risk_lookup.get(
            project_id,
            0,
        )
    )


    if (
        meeting_type
        in [
            "Risk Review",
            "Release Readiness Review",
        ]
        or high_risk_count >= 5
    ):

        priority = random.choices(
            population=[
                "Critical",
                "High",
                "Medium",
                "Low",
            ],
            weights=[
                12,
                43,
                35,
                10,
            ],
            k=1,
        )[0]


    else:

        priority = random.choices(
            population=[
                "Critical",
                "High",
                "Medium",
                "Low",
            ],
            weights=[
                4,
                25,
                51,
                20,
            ],
            k=1,
        )[0]


    # --------------------------------------------------------
    # OWNER
    # --------------------------------------------------------
    #
    # Use the Project Manager already present
    # in the project master rather than inventing
    # an unrelated owner.
    # --------------------------------------------------------

    project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == project_id
        ]
        .iloc[0]
    )


    owner = str(
        project[
            "ProjectManager"
        ]
    )


    # --------------------------------------------------------
    # CREATED / DUE DATE
    # --------------------------------------------------------

    created_date = meeting_date


    if priority == "Critical":

        due_days = random.randint(
            1,
            7,
        )


    elif priority == "High":

        due_days = random.randint(
            3,
            14,
        )


    elif priority == "Medium":

        due_days = random.randint(
            7,
            30,
        )


    else:

        due_days = random.randint(
            14,
            45,
        )


    due_date = (
        created_date
        + pd.Timedelta(
            days=due_days
        )
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    data_end = pd.Timestamp(
        config.DATA_END_DATE
    )


    age_days = (
        data_end
        - created_date
    ).days


    if age_days < 0:

        action_status = "Open"


    elif age_days > 90:

        action_status = random.choices(
            population=[
                "Completed",
                "In Progress",
                "Blocked",
                "Open",
            ],
            weights=[
                72,
                14,
                7,
                7,
            ],
            k=1,
        )[0]


    elif age_days > 30:

        action_status = random.choices(
            population=[
                "Completed",
                "In Progress",
                "Blocked",
                "Open",
            ],
            weights=[
                55,
                23,
                10,
                12,
            ],
            k=1,
        )[0]


    else:

        action_status = random.choices(
            population=[
                "Completed",
                "In Progress",
                "Blocked",
                "Open",
            ],
            weights=[
                28,
                35,
                15,
                22,
            ],
            k=1,
        )[0]


    # Higher-risk governance actions are somewhat
    # more likely to remain blocked.
    if (
        high_risk_count >= 8
        and action_status
        in [
            "Open",
            "In Progress",
        ]
        and random.random() < 0.12
    ):

        action_status = "Blocked"


    # --------------------------------------------------------
    # COMPLETION DATE
    # --------------------------------------------------------

    if action_status == "Completed":

        max_completion_date = min(
            data_end,
            due_date
            + pd.Timedelta(
                days=20
            ),
        )


        earliest_completion_date = (
            created_date
            + pd.Timedelta(
                days=1
            )
        )


        if (
            max_completion_date
            >= earliest_completion_date
        ):

            completion_window = (
                max_completion_date
                - earliest_completion_date
            ).days


            completed_date = (
                earliest_completion_date
                + pd.Timedelta(
                    days=random.randint(
                        0,
                        completion_window,
                    )
                )
            )


        else:

            completed_date = (
                max_completion_date
            )


    else:

        completed_date = pd.NaT


    # --------------------------------------------------------
    # OVERDUE
    # --------------------------------------------------------

    if action_status == "Completed":

        is_overdue = (
            completed_date
            > due_date
        )


    else:

        is_overdue = (
            due_date
            < data_end
        )


    # --------------------------------------------------------
    # SOURCE TYPE
    # --------------------------------------------------------

    if meeting_type == "Risk Review":

        source_type = "Risk"


    elif meeting_type == (
        "Release Readiness Review"
    ):

        source_type = "Release"


    elif meeting_type == (
        "Architecture Review"
    ):

        source_type = "Technical"


    elif meeting_type in [
        "Program Review",
        "Monthly Business Review",
    ]:

        source_type = "Program Governance"


    elif meeting_type == (
        "Stakeholder Review"
    ):

        source_type = "Stakeholder"


    else:

        source_type = "Delivery"


    # --------------------------------------------------------
    # ACTION RECORD
    # --------------------------------------------------------

    action_items.append(
        {
            "ActionItemID":
                action_id,

            "MeetingID":
                meeting_id,

            "ProgramID":
                program_id,

            "ProjectID":
                project_id,

            "ActionDescription":
                random.choice(
                    ACTION_DESCRIPTIONS
                ),

            "Owner":
                owner,

            "Priority":
                priority,

            "ActionStatus":
                action_status,

            "CreatedDate":
                created_date.date(),

            "DueDate":
                due_date.date(),

            "CompletedDate":
                (
                    completed_date.date()
                    if pd.notna(
                        completed_date
                    )
                    else pd.NaT
                ),

            "IsOverdue":
                bool(
                    is_overdue
                ),

            "SourceType":
                source_type,
        }
    )


# ============================================================
# CREATE ACTION ITEM DATAFRAME
# ============================================================

action_items_df = pd.DataFrame(
    action_items
)


# ============================================================
# ACTION ITEM VALIDATION
# ============================================================

assert len(
    action_items_df
) == config.TARGET_ACTION_ITEMS, (
    "Incorrect action-item count."
)


assert action_items_df[
    "ActionItemID"
].is_unique, (
    "Duplicate ActionItemID detected."
)


valid_meeting_ids = set(
    meetings_df[
        "MeetingID"
    ]
)


assert set(
    action_items_df[
        "MeetingID"
    ]
).issubset(
    valid_meeting_ids
), (
    "Invalid MeetingID found in action items."
)


# Meeting, Project and Program must agree.
action_relationship_check = (
    action_items_df[
        [
            "ActionItemID",
            "MeetingID",
            "ProjectID",
            "ProgramID",
        ]
    ]
    .merge(
        meetings_df[
            [
                "MeetingID",
                "ProjectID",
                "ProgramID",
            ]
        ],
        on="MeetingID",
        how="left",
        suffixes=(
            "_Action",
            "_Meeting",
        ),
    )
)


assert (
    action_relationship_check[
        "ProjectID_Action"
    ]
    ==
    action_relationship_check[
        "ProjectID_Meeting"
    ]
).all(), (
    "Action-item ProjectID does not "
    "match its MeetingID."
)


assert (
    action_relationship_check[
        "ProgramID_Action"
    ]
    ==
    action_relationship_check[
        "ProgramID_Meeting"
    ]
).all(), (
    "Action-item ProgramID does not "
    "match its MeetingID."
)


# ------------------------------------------------------------
# DATE VALIDATION
# ------------------------------------------------------------

action_dates_df = (
    action_items_df.copy()
)


for date_column in [
    "CreatedDate",
    "DueDate",
    "CompletedDate",
]:

    action_dates_df[
        date_column
    ] = pd.to_datetime(
        action_dates_df[
            date_column
        ]
    )


assert (
    action_dates_df[
        "DueDate"
    ]
    >=
    action_dates_df[
        "CreatedDate"
    ]
).all(), (
    "Action-item DueDate occurs "
    "before CreatedDate."
)


completed_actions = (
    action_dates_df[
        action_dates_df[
            "CompletedDate"
        ].notna()
    ]
)


assert (
    completed_actions[
        "CompletedDate"
    ]
    >=
    completed_actions[
        "CreatedDate"
    ]
).all(), (
    "Action item completed before creation."
)


assert (
    action_items_df.loc[
        action_items_df[
            "ActionStatus"
        ]
        == "Completed",
        "CompletedDate",
    ]
    .notna()
    .all()
), (
    "Completed action is missing "
    "CompletedDate."
)


assert (
    action_items_df.loc[
        action_items_df[
            "ActionStatus"
        ]
        != "Completed",
        "CompletedDate",
    ]
    .isna()
    .all()
), (
    "Incomplete action contains "
    "CompletedDate."
)


# Recalculate overdue status independently
# and verify the generated value.
calculated_overdue = []


for _, action in (
    action_dates_df.iterrows()
):

    if (
        action[
            "ActionStatus"
        ]
        == "Completed"
    ):

        overdue = (
            action[
                "CompletedDate"
            ]
            >
            action[
                "DueDate"
            ]
        )


    else:

        overdue = (
            action[
                "DueDate"
            ]
            <
            pd.Timestamp(
                config.DATA_END_DATE
            )
        )


    calculated_overdue.append(
        bool(overdue)
    )


assert (
    action_items_df[
        "IsOverdue"
    ].tolist()
    ==
    calculated_overdue
), (
    "Action-item overdue calculation "
    "is incorrect."
)


# ============================================================
# EXPORT ACTION ITEMS
# ============================================================

ACTION_ITEMS_FILE = (
    config.RAW_DATA_DIR
    / "action_items.csv"
)


action_items_df.to_csv(
    ACTION_ITEMS_FILE,
    index=False,
)


# ============================================================
# ACTION ITEM SUMMARY
# ============================================================

print(
    f"\nAction Items generated : "
    f"{len(action_items_df):,}"
)


print(
    f"Meetings represented   : "
    f"{action_items_df['MeetingID'].nunique():,}"
)


print(
    f"Projects represented   : "
    f"{action_items_df['ProjectID'].nunique()}"
)


print(
    f"Overdue actions        : "
    f"{action_items_df['IsOverdue'].sum():,}"
)


print(
    "\nAction Status Distribution:"
)


print(
    action_items_df[
        "ActionStatus"
    ].value_counts()
)


print(
    "\nPriority Distribution:"
)


print(
    action_items_df[
        "Priority"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{ACTION_ITEMS_FILE}"
)


print(
    "\nAction-item validation passed."
)


print(
    "action_items.csv generated successfully!"
)

# ============================================================
# DECISION LOG DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - DECISIONS")
print("=" * 70)


# ============================================================
# DECISION SETTINGS
# ============================================================

DECISION_TYPES = [
    "Release",
    "Architecture",
    "Scope",
    "Risk",
    "Priority",
    "Resource",
    "Budget",
    "Dependency",
    "Technical",
    "Stakeholder",
]


DECISION_SUMMARIES = {
    "Release": [
        "Approved release for planned deployment",
        "Deferred release pending readiness actions",
        "Approved conditional release with follow-up actions",
    ],

    "Architecture": [
        "Approved proposed architecture approach",
        "Requested architecture redesign before implementation",
        "Approved integration design with constraints",
    ],

    "Scope": [
        "Approved scope adjustment",
        "Deferred lower-priority scope",
        "Approved change request affecting delivery scope",
    ],

    "Risk": [
        "Accepted residual delivery risk",
        "Approved mitigation approach",
        "Escalated risk for leadership review",
    ],

    "Priority": [
        "Reprioritized delivery backlog",
        "Approved critical work as highest priority",
        "Deferred lower-value work",
    ],

    "Resource": [
        "Approved resource reallocation",
        "Approved additional engineering support",
        "Deferred staffing change",
    ],

    "Budget": [
        "Approved forecast budget adjustment",
        "Requested cost reduction actions",
        "Approved use of contingency budget",
    ],

    "Dependency": [
        "Approved dependency escalation",
        "Confirmed cross-team delivery commitment",
        "Approved contingency for blocked dependency",
    ],

    "Technical": [
        "Approved technical implementation approach",
        "Requested additional technical validation",
        "Approved remediation plan",
    ],

    "Stakeholder": [
        "Confirmed stakeholder alignment",
        "Escalated unresolved stakeholder concern",
        "Approved communication approach",
    ],
}


# ============================================================
# MEETING DECISION WEIGHTS
# ============================================================

decision_meeting_ids = (
    meetings_df[
        "MeetingID"
    ]
    .astype(int)
    .tolist()
)


decision_meeting_weights = []


for _, meeting in meetings_df.iterrows():

    weight = 1.0


    if meeting[
        "MeetingType"
    ] in [
        "Program Review",
        "Monthly Business Review",
        "Risk Review",
        "Release Readiness Review",
        "Architecture Review",
        "Stakeholder Review",
    ]:

        weight += 2.5


    if bool(
        meeting[
            "FollowUpRequired"
        ]
    ):

        weight += 0.5


    decision_meeting_weights.append(
        weight
    )


# ============================================================
# DECISION TYPE SELECTION
# ============================================================

def choose_decision_type(
    meeting_type,
):
    """
    Choose a decision type based on the
    type of governance meeting.
    """

    weights = {
        "Release": 10,
        "Architecture": 10,
        "Scope": 10,
        "Risk": 10,
        "Priority": 10,
        "Resource": 8,
        "Budget": 7,
        "Dependency": 9,
        "Technical": 10,
        "Stakeholder": 8,
    }


    if meeting_type == "Release Readiness Review":

        weights["Release"] += 25
        weights["Risk"] += 8
        weights["Technical"] += 6


    elif meeting_type == "Architecture Review":

        weights["Architecture"] += 25
        weights["Technical"] += 12


    elif meeting_type == "Risk Review":

        weights["Risk"] += 25
        weights["Dependency"] += 8


    elif meeting_type == "Program Review":

        weights["Priority"] += 12
        weights["Resource"] += 8
        weights["Scope"] += 8


    elif meeting_type == "Monthly Business Review":

        weights["Budget"] += 12
        weights["Priority"] += 10
        weights["Resource"] += 6


    elif meeting_type == "Stakeholder Review":

        weights["Stakeholder"] += 20
        weights["Scope"] += 10


    elif meeting_type in [
        "Sprint Planning",
        "Sprint Review",
        "Sprint Retrospective",
    ]:

        weights["Scope"] += 8
        weights["Priority"] += 8
        weights["Technical"] += 5


    return random.choices(
        population=list(
            weights.keys()
        ),
        weights=list(
            weights.values()
        ),
        k=1,
    )[0]


# ============================================================
# GENERATE 2,000 DECISIONS
# ============================================================

decisions = []


for decision_id in range(
    1,
    config.TARGET_DECISIONS + 1,
):

    meeting_id = int(
        random.choices(
            population=decision_meeting_ids,
            weights=decision_meeting_weights,
            k=1,
        )[0]
    )


    meeting = meeting_lookup.loc[
        meeting_id
    ]


    project_id = int(
        meeting[
            "ProjectID"
        ]
    )


    program_id = int(
        meeting[
            "ProgramID"
        ]
    )


    meeting_date = pd.Timestamp(
        meeting[
            "MeetingDate"
        ]
    )


    meeting_type = str(
        meeting[
            "MeetingType"
        ]
    )


    decision_type = (
        choose_decision_type(
            meeting_type
        )
    )


    decision_summary = random.choice(
        DECISION_SUMMARIES[
            decision_type
        ]
    )


    # --------------------------------------------------------
    # DECISION OWNER
    # --------------------------------------------------------

    project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == project_id
        ]
        .iloc[0]
    )


    decision_owner = str(
        project[
            "ProjectManager"
        ]
    )


    # --------------------------------------------------------
    # DECISION STATUS
    # --------------------------------------------------------

    data_end = pd.Timestamp(
        config.DATA_END_DATE
    )


    decision_age_days = (
        data_end
        - meeting_date
    ).days


    if decision_age_days > 60:

        decision_status = random.choices(
            population=[
                "Implemented",
                "In Progress",
                "Pending",
                "Superseded",
            ],
            weights=[
                68,
                18,
                8,
                6,
            ],
            k=1,
        )[0]


    else:

        decision_status = random.choices(
            population=[
                "Implemented",
                "In Progress",
                "Pending",
                "Superseded",
            ],
            weights=[
                36,
                34,
                24,
                6,
            ],
            k=1,
        )[0]


    # --------------------------------------------------------
    # EFFECTIVE DATE
    # --------------------------------------------------------

    if decision_status in [
        "Implemented",
        "In Progress",
    ]:

        effective_date = (
            meeting_date
            + pd.Timedelta(
                days=random.randint(
                    0,
                    21,
                )
            )
        )


        if effective_date > data_end:

            effective_date = data_end


    else:

        effective_date = pd.NaT


    # --------------------------------------------------------
    # REQUIRES FOLLOW-UP
    # --------------------------------------------------------

    requires_follow_up = (
        decision_status
        in [
            "In Progress",
            "Pending",
        ]
        or decision_type
        in [
            "Risk",
            "Dependency",
            "Release",
        ]
        and random.random() < 0.45
    )


    # --------------------------------------------------------
    # BUSINESS IMPACT
    # --------------------------------------------------------

    if decision_type in [
        "Release",
        "Risk",
        "Budget",
        "Resource",
    ]:

        business_impact = random.choices(
            population=[
                "High",
                "Medium",
                "Low",
            ],
            weights=[
                45,
                45,
                10,
            ],
            k=1,
        )[0]


    else:

        business_impact = random.choices(
            population=[
                "High",
                "Medium",
                "Low",
            ],
            weights=[
                25,
                55,
                20,
            ],
            k=1,
        )[0]


    # --------------------------------------------------------
    # DECISION RECORD
    # --------------------------------------------------------

    decisions.append(
        {
            "DecisionID":
                decision_id,

            "MeetingID":
                meeting_id,

            "ProgramID":
                program_id,

            "ProjectID":
                project_id,

            "DecisionType":
                decision_type,

            "DecisionSummary":
                decision_summary,

            "DecisionOwner":
                decision_owner,

            "DecisionDate":
                meeting_date.date(),

            "DecisionStatus":
                decision_status,

            "EffectiveDate":
                (
                    effective_date.date()
                    if pd.notna(
                        effective_date
                    )
                    else pd.NaT
                ),

            "BusinessImpact":
                business_impact,

            "RequiresFollowUp":
                bool(
                    requires_follow_up
                ),
        }
    )


# ============================================================
# CREATE DECISION DATAFRAME
# ============================================================

decisions_df = pd.DataFrame(
    decisions
)


# ============================================================
# DECISION VALIDATION
# ============================================================

assert len(
    decisions_df
) == config.TARGET_DECISIONS, (
    "Incorrect decision count."
)


assert decisions_df[
    "DecisionID"
].is_unique, (
    "Duplicate DecisionID detected."
)


assert set(
    decisions_df[
        "MeetingID"
    ]
).issubset(
    valid_meeting_ids
), (
    "Invalid MeetingID found in decisions."
)


decision_relationship_check = (
    decisions_df[
        [
            "DecisionID",
            "MeetingID",
            "ProjectID",
            "ProgramID",
        ]
    ]
    .merge(
        meetings_df[
            [
                "MeetingID",
                "ProjectID",
                "ProgramID",
            ]
        ],
        on="MeetingID",
        how="left",
        suffixes=(
            "_Decision",
            "_Meeting",
        ),
    )
)


assert (
    decision_relationship_check[
        "ProjectID_Decision"
    ]
    ==
    decision_relationship_check[
        "ProjectID_Meeting"
    ]
).all(), (
    "Decision ProjectID does not "
    "match MeetingID."
)


assert (
    decision_relationship_check[
        "ProgramID_Decision"
    ]
    ==
    decision_relationship_check[
        "ProgramID_Meeting"
    ]
).all(), (
    "Decision ProgramID does not "
    "match MeetingID."
)


# ------------------------------------------------------------
# DATE VALIDATION
# ------------------------------------------------------------

decision_dates_df = (
    decisions_df.copy()
)


for date_column in [
    "DecisionDate",
    "EffectiveDate",
]:

    decision_dates_df[
        date_column
    ] = pd.to_datetime(
        decision_dates_df[
            date_column
        ]
    )


implemented_decisions = (
    decision_dates_df[
        decision_dates_df[
            "EffectiveDate"
        ].notna()
    ]
)


assert (
    implemented_decisions[
        "EffectiveDate"
    ]
    >=
    implemented_decisions[
        "DecisionDate"
    ]
).all(), (
    "Decision EffectiveDate occurs "
    "before DecisionDate."
)


assert (
    decisions_df.loc[
        decisions_df[
            "DecisionStatus"
        ].isin(
            [
                "Implemented",
                "In Progress",
            ]
        ),
        "EffectiveDate",
    ]
    .notna()
    .all()
), (
    "Implemented/In Progress decision "
    "is missing EffectiveDate."
)


assert (
    decisions_df.loc[
        ~decisions_df[
            "DecisionStatus"
        ].isin(
            [
                "Implemented",
                "In Progress",
            ]
        ),
        "EffectiveDate",
    ]
    .isna()
    .all()
), (
    "Pending/Superseded decision "
    "contains EffectiveDate."
)


# ============================================================
# EXPORT DECISIONS
# ============================================================

DECISIONS_FILE = (
    config.RAW_DATA_DIR
    / "decisions.csv"
)


decisions_df.to_csv(
    DECISIONS_FILE,
    index=False,
)


# ============================================================
# DECISION SUMMARY
# ============================================================

print(
    f"\nDecisions generated    : "
    f"{len(decisions_df):,}"
)


print(
    f"Meetings represented   : "
    f"{decisions_df['MeetingID'].nunique():,}"
)


print(
    f"Projects represented   : "
    f"{decisions_df['ProjectID'].nunique()}"
)


print(
    "\nDecision Type Distribution:"
)


print(
    decisions_df[
        "DecisionType"
    ].value_counts()
)


print(
    "\nDecision Status Distribution:"
)


print(
    decisions_df[
        "DecisionStatus"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{DECISIONS_FILE}"
)


print(
    "\nDecision validation passed."
)


print(
    "decisions.csv generated successfully!"
)

# ============================================================
# OKR / KPI MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - OKRS")
print("=" * 70)


# ============================================================
# OKR SETTINGS
# ============================================================

OKR_DEFINITIONS = {
    "Delivery": [
        (
            "Improve predictable delivery",
            "Increase milestone delivery performance",
            "Percent",
            90,
        ),
        (
            "Reduce delivery variance",
            "Reduce schedule variance across commitments",
            "Percent",
            85,
        ),
    ],

    "Quality": [
        (
            "Improve engineering quality",
            "Increase defect-free delivery performance",
            "Percent",
            92,
        ),
        (
            "Improve release quality",
            "Increase release quality readiness",
            "Percent",
            90,
        ),
    ],

    "Release": [
        (
            "Improve release predictability",
            "Increase on-time release performance",
            "Percent",
            90,
        ),
        (
            "Improve release readiness",
            "Increase average release readiness",
            "Percent",
            92,
        ),
    ],

    "Risk": [
        (
            "Reduce delivery risk exposure",
            "Increase effective risk mitigation",
            "Percent",
            85,
        ),
        (
            "Improve governance effectiveness",
            "Increase closure of material risks",
            "Percent",
            90,
        ),
    ],

    "Capacity": [
        (
            "Improve engineering capacity",
            "Increase effective team capacity utilization",
            "Percent",
            90,
        ),
        (
            "Improve delivery throughput",
            "Increase sprint completion performance",
            "Percent",
            90,
        ),
    ],

    "Financial": [
        (
            "Improve budget predictability",
            "Maintain delivery within approved forecast",
            "Percent",
            95,
        ),
        (
            "Improve portfolio cost control",
            "Reduce unfavorable budget variance",
            "Percent",
            95,
        ),
    ],
}


OKR_CATEGORIES = list(
    OKR_DEFINITIONS.keys()
)


# ============================================================
# PROJECT OKR PERFORMANCE PROFILE
# ============================================================

project_okr_profiles = {}


for _, project in projects_df.iterrows():

    project_id = int(
        project[
            "ProjectID"
        ]
    )


    profile = (
        project_risk_profiles[
            project_id
        ]
    )


    # Delivery score
    delivery_score = float(
        np.clip(
            profile[
                "AverageCompletion"
            ],
            0,
            100,
        )
    )


    # Capacity score
    capacity_score = float(
        np.clip(
            profile[
                "AverageCapacity"
            ],
            0,
            100,
        )
    )


    # Release score combines readiness
    # and schedule performance.
    release_delay_penalty = min(
        max(
            profile[
                "AverageReleaseDelay"
            ],
            0,
        )
        * 1.5,
        35,
    )


    release_score = float(
        np.clip(
            profile[
                "AverageReadiness"
            ]
            - release_delay_penalty,
            0,
            100,
        )
    )


    # Quality score is reduced by open
    # and critical defects.
    quality_penalty = min(
        (
            profile[
                "OpenBugs"
            ]
            * 0.10
        )
        +
        (
            profile[
                "CriticalBugs"
            ]
            * 2.0
        ),
        45,
    )


    quality_score = float(
        np.clip(
            100
            - quality_penalty,
            0,
            100,
        )
    )


    # Risk score uses the generated
    # governance risk dataset.
    project_risks = (
        risks_df[
            risks_df[
                "ProjectID"
            ]
            == project_id
        ]
    )


    if not project_risks.empty:

        open_material_risks = int(
            (
                (
                    project_risks[
                        "RiskStatus"
                    ]
                    != "Closed"
                )
                &
                (
                    project_risks[
                        "RiskRating"
                    ].isin(
                        [
                            "High",
                            "Critical",
                        ]
                    )
                )
            ).sum()
        )


        average_residual_risk = float(
            project_risks[
                "ResidualRiskScore"
            ].mean()
        )


    else:

        open_material_risks = 0
        average_residual_risk = 0


    risk_score = float(
        np.clip(
            100
            -
            (
                open_material_risks
                * 3
            )
            -
            (
                average_residual_risk
                * 2
            ),
            0,
            100,
        )
    )


    # Financial score is based on
    # budget variance from project master.
    budget_variance = abs(
        float(
            project[
                "BudgetVariancePercent"
            ]
        )
    )


    financial_score = float(
        np.clip(
            100
            -
            (
                budget_variance
                * 2
            ),
            0,
            100,
        )
    )


    project_okr_profiles[
        project_id
    ] = {
        "Delivery":
            delivery_score,

        "Quality":
            quality_score,

        "Release":
            release_score,

        "Risk":
            risk_score,

        "Capacity":
            capacity_score,

        "Financial":
            financial_score,
    }


# ============================================================
# GENERATE 500 OKRS
# ============================================================

okrs = []


# 500 OKRs / 50 projects = 10 OKRs per project.
okrs_per_project = (
    config.TARGET_OKRS
    // config.NUM_PROJECTS
)


assert (
    okrs_per_project
    * config.NUM_PROJECTS
    ==
    config.TARGET_OKRS
), (
    "TARGET_OKRS must divide evenly "
    "across projects."
)


okr_id = 1


for _, project in projects_df.iterrows():

    project_id = int(
        project[
            "ProjectID"
        ]
    )


    program_id = int(
        project[
            "ProgramID"
        ]
    )


    project_start = pd.Timestamp(
        project[
            "StartDate"
        ]
    )


    project_end = min(
        pd.Timestamp(
            project[
                "PlannedEndDate"
            ]
        ),
        pd.Timestamp(
            config.DATA_END_DATE
        ),
    )


    project_manager = str(
        project[
            "ProjectManager"
        ]
    )


    performance_profile = (
        project_okr_profiles[
            project_id
        ]
    )


    # Guarantee broad category coverage
    # while still allowing variation.
    category_sequence = (
        OKR_CATEGORIES.copy()
    )


    while len(
        category_sequence
    ) < okrs_per_project:

        category_sequence.append(
            random.choice(
                OKR_CATEGORIES
            )
        )


    random.shuffle(
        category_sequence
    )


    for okr_number in range(
        okrs_per_project
    ):

        category = (
            category_sequence[
                okr_number
            ]
        )


        (
            objective,
            key_result,
            metric_unit,
            target_value,
        ) = random.choice(
            OKR_DEFINITIONS[
                category
            ]
        )


        # ----------------------------------------------------
        # OKR PERIOD
        # ----------------------------------------------------

        available_days = max(
            0,
            (
                project_end
                - project_start
            ).days,
        )


        if available_days > 120:

            offset_days = random.randint(
                0,
                max(
                    0,
                    available_days - 90,
                ),
            )


        else:

            offset_days = 0


        period_start = (
            project_start
            + pd.Timedelta(
                days=offset_days
            )
        )


        period_end = min(
            period_start
            + pd.Timedelta(
                days=random.randint(
                    60,
                    120,
                )
            ),
            project_end,
        )


        # ----------------------------------------------------
        # ACTUAL PERFORMANCE
        # ----------------------------------------------------

        base_performance = float(
            performance_profile[
                category
            ]
        )


        actual_value = float(
            np.clip(
                base_performance
                + np.random.normal(
                    loc=0,
                    scale=5,
                ),
                0,
                100,
            )
        )


        actual_value = round(
            actual_value,
            1,
        )


        target_value_numeric = float(
            target_value
        )


        progress_percent = float(
            np.clip(
                (
                    actual_value
                    /
                    target_value_numeric
                )
                * 100,
                0,
                120,
            )
        )


        progress_percent = round(
            progress_percent,
            1,
        )


        # ----------------------------------------------------
        # OKR STATUS
        # ----------------------------------------------------

        if progress_percent >= 100:

            okr_status = "Achieved"


        elif progress_percent >= 85:

            okr_status = "On Track"


        elif progress_percent >= 70:

            okr_status = "At Risk"


        else:

            okr_status = "Off Track"


        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        if okr_status == "Achieved":

            confidence_level = "High"


        elif okr_status == "On Track":

            confidence_level = random.choice(
                [
                    "High",
                    "Medium",
                ]
            )


        elif okr_status == "At Risk":

            confidence_level = random.choice(
                [
                    "Medium",
                    "Low",
                ]
            )


        else:

            confidence_level = "Low"


        # ----------------------------------------------------
        # RECORD
        # ----------------------------------------------------

        okrs.append(
            {
                "OKRID":
                    okr_id,

                "ProgramID":
                    program_id,

                "ProjectID":
                    project_id,

                "OKRCategory":
                    category,

                "Objective":
                    objective,

                "KeyResult":
                    key_result,

                "MetricUnit":
                    metric_unit,

                "TargetValue":
                    target_value_numeric,

                "ActualValue":
                    actual_value,

                "ProgressPercent":
                    progress_percent,

                "OKRStatus":
                    okr_status,

                "ConfidenceLevel":
                    confidence_level,

                "Owner":
                    project_manager,

                "PeriodStartDate":
                    period_start.date(),

                "PeriodEndDate":
                    period_end.date(),
            }
        )


        okr_id += 1


# ============================================================
# CREATE OKR DATAFRAME
# ============================================================

okrs_df = pd.DataFrame(
    okrs
)


# ============================================================
# OKR VALIDATION
# ============================================================

assert len(
    okrs_df
) == config.TARGET_OKRS, (
    "Incorrect OKR count."
)


assert okrs_df[
    "OKRID"
].is_unique, (
    "Duplicate OKRID detected."
)


assert set(
    okrs_df[
        "ProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid ProjectID found in OKRs."
)


assert set(
    okrs_df[
        "ProgramID"
    ]
).issubset(
    valid_program_ids
), (
    "Invalid ProgramID found in OKRs."
)


# Every project should have exactly
# 10 OKRs.
okr_project_counts = (
    okrs_df[
        "ProjectID"
    ]
    .value_counts()
)


assert (
    okr_project_counts
    ==
    okrs_per_project
).all(), (
    "Projects do not have the expected "
    "number of OKRs."
)


# Validate Project -> Program relationship.
okr_relationship_check = (
    okrs_df[
        [
            "OKRID",
            "ProjectID",
            "ProgramID",
        ]
    ]
    .copy()
)


okr_relationship_check[
    "ExpectedProgramID"
] = (
    okr_relationship_check[
        "ProjectID"
    ]
    .map(
        project_program_lookup
    )
)


assert (
    okr_relationship_check[
        "ProgramID"
    ]
    ==
    okr_relationship_check[
        "ExpectedProgramID"
    ]
).all(), (
    "OKR ProgramID does not match "
    "ProjectID."
)


assert okrs_df[
    "ActualValue"
].between(
    0,
    100,
).all(), (
    "Invalid OKR ActualValue."
)


assert okrs_df[
    "ProgressPercent"
].between(
    0,
    120,
).all(), (
    "Invalid OKR ProgressPercent."
)


# ------------------------------------------------------------
# STATUS VALIDATION
# ------------------------------------------------------------

def expected_okr_status(
    progress,
):

    if progress >= 100:
        return "Achieved"

    if progress >= 85:
        return "On Track"

    if progress >= 70:
        return "At Risk"

    return "Off Track"


expected_statuses = (
    okrs_df[
        "ProgressPercent"
    ]
    .apply(
        expected_okr_status
    )
)


assert (
    okrs_df[
        "OKRStatus"
    ]
    ==
    expected_statuses
).all(), (
    "OKR status does not match "
    "ProgressPercent."
)


# ------------------------------------------------------------
# DATE VALIDATION
# ------------------------------------------------------------

okr_dates_df = (
    okrs_df.copy()
)


okr_dates_df[
    "PeriodStartDate"
] = pd.to_datetime(
    okr_dates_df[
        "PeriodStartDate"
    ]
)


okr_dates_df[
    "PeriodEndDate"
] = pd.to_datetime(
    okr_dates_df[
        "PeriodEndDate"
    ]
)


assert (
    okr_dates_df[
        "PeriodEndDate"
    ]
    >=
    okr_dates_df[
        "PeriodStartDate"
    ]
).all(), (
    "OKR PeriodEndDate occurs "
    "before PeriodStartDate."
)


# ============================================================
# EXPORT OKRS
# ============================================================

OKRS_FILE = (
    config.RAW_DATA_DIR
    / "okrs.csv"
)


okrs_df.to_csv(
    OKRS_FILE,
    index=False,
)


# ============================================================
# OKR SUMMARY
# ============================================================

print(
    f"\nOKRs generated         : "
    f"{len(okrs_df):,}"
)


print(
    f"Projects represented   : "
    f"{okrs_df['ProjectID'].nunique()}"
)


print(
    f"Programs represented   : "
    f"{okrs_df['ProgramID'].nunique()}"
)


print(
    f"Average progress       : "
    f"{okrs_df['ProgressPercent'].mean():.2f}%"
)


print(
    "\nOKR Status Distribution:"
)


print(
    okrs_df[
        "OKRStatus"
    ].value_counts()
)


print(
    "\nOKR Category Distribution:"
)


print(
    okrs_df[
        "OKRCategory"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{OKRS_FILE}"
)


print(
    "\nOKR validation passed."
)


print(
    "okrs.csv generated successfully!"
)

# ============================================================
# PRODUCT ROADMAP DATA
# ============================================================

print("\n" + "=" * 70)
print("GOVERNANCE DATA GENERATION - ROADMAP ITEMS")
print("=" * 70)


# ============================================================
# ROADMAP SOURCE DATA
# ============================================================

PRODUCTS_FILE = (
    config.RAW_DATA_DIR
    / "products.csv"
)


if not PRODUCTS_FILE.exists():

    raise FileNotFoundError(
        f"Required source file missing: "
        f"{PRODUCTS_FILE}"
    )


products_df = pd.read_csv(
    PRODUCTS_FILE
)


# ============================================================
# PRODUCT / RELEASE LOOKUPS
# ============================================================

project_product_lookup = (
    products_df
    .set_index(
        "ProjectID"
    )[
        "ProductID"
    ]
    .to_dict()
)


project_release_lookup = {}


for project_id, group in (
    releases_df
    .groupby(
        "ProjectID"
    )
):

    project_release_lookup[
        int(project_id)
    ] = (
        group[
            "ReleaseID"
        ]
        .astype(int)
        .tolist()
    )


release_lookup = (
    releases_df
    .set_index(
        "ReleaseID"
    )
)


# ============================================================
# ROADMAP SETTINGS
# ============================================================

ROADMAP_TYPES = [
    "Feature",
    "Platform",
    "Security",
    "Reliability",
    "Developer Experience",
    "Technical Debt",
    "Integration",
    "Compliance",
]


STRATEGIC_THEMES = [
    "Customer Experience",
    "Engineering Excellence",
    "Platform Modernization",
    "Security and Compliance",
    "Operational Efficiency",
    "Developer Productivity",
    "Cloud Transformation",
    "Product Growth",
]


ROADMAP_TITLES = {
    "Feature": [
        "Deliver strategic product capability",
        "Expand customer-facing functionality",
        "Enable priority product experience",
    ],

    "Platform": [
        "Modernize core platform capability",
        "Improve shared platform services",
        "Expand platform scalability",
    ],

    "Security": [
        "Complete security modernization",
        "Strengthen platform security controls",
        "Deliver security remediation capability",
    ],

    "Reliability": [
        "Improve service reliability",
        "Increase platform resilience",
        "Reduce operational failure exposure",
    ],

    "Developer Experience": [
        "Improve developer onboarding experience",
        "Streamline engineering workflows",
        "Improve developer self-service capability",
    ],

    "Technical Debt": [
        "Reduce priority technical debt",
        "Modernize legacy implementation",
        "Complete engineering remediation",
    ],

    "Integration": [
        "Deliver strategic system integration",
        "Improve cross-platform interoperability",
        "Enable service integration capability",
    ],

    "Compliance": [
        "Deliver compliance requirements",
        "Complete regulatory control implementation",
        "Improve compliance readiness",
    ],
}


# ============================================================
# GENERATE 500 ROADMAP ITEMS
# ============================================================

roadmap_items = []


roadmap_items_per_project = (
    config.TARGET_ROADMAP_ITEMS
    // config.NUM_PROJECTS
)


assert (
    roadmap_items_per_project
    * config.NUM_PROJECTS
    ==
    config.TARGET_ROADMAP_ITEMS
), (
    "TARGET_ROADMAP_ITEMS must divide "
    "evenly across projects."
)


roadmap_item_id = 1


for _, project in projects_df.iterrows():

    project_id = int(
        project[
            "ProjectID"
        ]
    )


    program_id = int(
        project[
            "ProgramID"
        ]
    )


    project_start = pd.Timestamp(
        project[
            "StartDate"
        ]
    )


    project_end = min(
        pd.Timestamp(
            project[
                "PlannedEndDate"
            ]
        ),
        pd.Timestamp(
            config.DATA_END_DATE
        ),
    )


    product_id = (
        int(
            project_product_lookup[
                project_id
            ]
        )
        if project_id
        in project_product_lookup
        else None
    )


    release_ids = (
        project_release_lookup
        .get(
            project_id,
            [],
        )
    )


    delivery_profile = (
        project_risk_profiles[
            project_id
        ]
    )


    for _ in range(
        roadmap_items_per_project
    ):

        roadmap_type = random.choice(
            ROADMAP_TYPES
        )


        strategic_theme = random.choice(
            STRATEGIC_THEMES
        )


        # ----------------------------------------------------
        # RELEASE LINK
        # ----------------------------------------------------

        if (
            release_ids
            and random.random() < 0.80
        ):

            release_id = int(
                random.choice(
                    release_ids
                )
            )


            release = (
                release_lookup.loc[
                    release_id
                ]
            )


            planned_end_date = pd.Timestamp(
                release[
                    "PlannedReleaseDate"
                ]
            )


            forecast_end_date = pd.Timestamp(
                release[
                    "ForecastReleaseDate"
                ]
            )


        else:

            release_id = None


            available_days = max(
                0,
                (
                    project_end
                    - project_start
                ).days,
            )


            planned_offset = random.randint(
                0,
                available_days,
            )


            planned_end_date = (
                project_start
                + pd.Timedelta(
                    days=planned_offset
                )
            )


            forecast_variance = random.randint(
                -7,
                30,
            )


            forecast_end_date = (
                planned_end_date
                + pd.Timedelta(
                    days=forecast_variance
                )
            )


        # Keep dates inside the
        # project/data horizon.
        planned_end_date = min(
            planned_end_date,
            project_end,
        )


        forecast_end_date = min(
            forecast_end_date,
            project_end,
        )


        forecast_end_date = max(
            forecast_end_date,
            project_start,
        )


        # ----------------------------------------------------
        # START DATE
        # ----------------------------------------------------

        duration_days = random.randint(
            30,
            120,
        )


        planned_start_date = max(
            project_start,
            planned_end_date
            - pd.Timedelta(
                days=duration_days
            ),
        )


        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        if roadmap_type in [
            "Security",
            "Compliance",
            "Reliability",
        ]:

            priority = random.choices(
                population=[
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                ],
                weights=[
                    15,
                    45,
                    32,
                    8,
                ],
                k=1,
            )[0]


        else:

            priority = random.choices(
                population=[
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                ],
                weights=[
                    5,
                    30,
                    50,
                    15,
                ],
                k=1,
            )[0]


        # ----------------------------------------------------
        # DELIVERY PERFORMANCE
        # ----------------------------------------------------

        performance_score = (
            delivery_profile[
                "AverageCompletion"
            ]
        )


        release_delay = (
            delivery_profile[
                "AverageReleaseDelay"
            ]
        )


        critical_bugs = (
            delivery_profile[
                "CriticalBugs"
            ]
        )


        blocked_dependencies = (
            delivery_profile[
                "BlockedDependencies"
            ]
        )


        delivery_penalty = 0


        if performance_score < 85:
            delivery_penalty += 8


        if release_delay >= 10:
            delivery_penalty += 10


        if critical_bugs >= 5:
            delivery_penalty += 6


        if blocked_dependencies >= 2:
            delivery_penalty += 8


        progress_percent = float(
            np.clip(
                performance_score
                - delivery_penalty
                + np.random.normal(
                    0,
                    8,
                ),
                0,
                100,
            )
        )


        progress_percent = round(
            progress_percent,
            1,
        )


        # ----------------------------------------------------
        # ROADMAP STATUS
        # ----------------------------------------------------

        schedule_variance_days = (
            forecast_end_date
            - planned_end_date
        ).days


        if progress_percent >= 100:

            roadmap_status = "Completed"


        elif (
            schedule_variance_days > 14
            or progress_percent < 60
        ):

            roadmap_status = "At Risk"


        elif progress_percent >= 75:

            roadmap_status = "On Track"


        else:

            roadmap_status = "In Progress"


        # ----------------------------------------------------
        # OWNER
        # ----------------------------------------------------

        roadmap_owner = str(
            project[
                "ProjectManager"
            ]
        )


        # ----------------------------------------------------
        # RECORD
        # ----------------------------------------------------

        roadmap_items.append(
            {
                "RoadmapItemID":
                    roadmap_item_id,

                "ProgramID":
                    program_id,

                "ProjectID":
                    project_id,

                "ProductID":
                    product_id,

                "ReleaseID":
                    release_id,

                "RoadmapType":
                    roadmap_type,

                "RoadmapTitle":
                    random.choice(
                        ROADMAP_TITLES[
                            roadmap_type
                        ]
                    ),

                "StrategicTheme":
                    strategic_theme,

                "Priority":
                    priority,

                "RoadmapOwner":
                    roadmap_owner,

                "PlannedStartDate":
                    planned_start_date.date(),

                "PlannedEndDate":
                    planned_end_date.date(),

                "ForecastEndDate":
                    forecast_end_date.date(),

                "ScheduleVarianceDays":
                    schedule_variance_days,

                "ProgressPercent":
                    progress_percent,

                "RoadmapStatus":
                    roadmap_status,
            }
        )


        roadmap_item_id += 1


# ============================================================
# CREATE ROADMAP DATAFRAME
# ============================================================

roadmap_items_df = pd.DataFrame(
    roadmap_items
)


# ============================================================
# ROADMAP VALIDATION
# ============================================================

assert len(
    roadmap_items_df
) == config.TARGET_ROADMAP_ITEMS, (
    "Incorrect roadmap-item count."
)


assert roadmap_items_df[
    "RoadmapItemID"
].is_unique, (
    "Duplicate RoadmapItemID detected."
)


assert set(
    roadmap_items_df[
        "ProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid ProjectID found "
    "in roadmap items."
)


assert set(
    roadmap_items_df[
        "ProgramID"
    ]
).issubset(
    valid_program_ids
), (
    "Invalid ProgramID found "
    "in roadmap items."
)


roadmap_project_counts = (
    roadmap_items_df[
        "ProjectID"
    ]
    .value_counts()
)


assert (
    roadmap_project_counts
    ==
    roadmap_items_per_project
).all(), (
    "Projects do not have expected "
    "roadmap-item count."
)


# ------------------------------------------------------------
# PROJECT -> PROGRAM VALIDATION
# ------------------------------------------------------------

roadmap_relationship_check = (
    roadmap_items_df[
        [
            "RoadmapItemID",
            "ProjectID",
            "ProgramID",
        ]
    ]
    .copy()
)


roadmap_relationship_check[
    "ExpectedProgramID"
] = (
    roadmap_relationship_check[
        "ProjectID"
    ]
    .map(
        project_program_lookup
    )
)


assert (
    roadmap_relationship_check[
        "ProgramID"
    ]
    ==
    roadmap_relationship_check[
        "ExpectedProgramID"
    ]
).all(), (
    "Roadmap ProgramID does not "
    "match ProjectID."
)


# ------------------------------------------------------------
# PRODUCT VALIDATION
# ------------------------------------------------------------

roadmap_products = (
    roadmap_items_df[
        roadmap_items_df[
            "ProductID"
        ].notna()
    ]
)


valid_product_ids = set(
    products_df[
        "ProductID"
    ]
)


assert set(
    roadmap_products[
        "ProductID"
    ]
    .astype(int)
).issubset(
    valid_product_ids
), (
    "Invalid ProductID found "
    "in roadmap items."
)


# ------------------------------------------------------------
# RELEASE VALIDATION
# ------------------------------------------------------------

roadmap_releases = (
    roadmap_items_df[
        roadmap_items_df[
            "ReleaseID"
        ].notna()
    ]
)


valid_release_ids = set(
    releases_df[
        "ReleaseID"
    ]
)


assert set(
    roadmap_releases[
        "ReleaseID"
    ]
    .astype(int)
).issubset(
    valid_release_ids
), (
    "Invalid ReleaseID found "
    "in roadmap items."
)


# Release must belong to same project.
release_project_lookup = (
    releases_df
    .set_index(
        "ReleaseID"
    )[
        "ProjectID"
    ]
    .to_dict()
)


for _, item in (
    roadmap_releases.iterrows()
):

    assert (
        release_project_lookup[
            int(
                item[
                    "ReleaseID"
                ]
            )
        ]
        ==
        int(
            item[
                "ProjectID"
            ]
        )
    ), (
        "Roadmap ReleaseID does not "
        "belong to ProjectID."
    )


# ------------------------------------------------------------
# DATE VALIDATION
# ------------------------------------------------------------

roadmap_dates_df = (
    roadmap_items_df.copy()
)


for date_column in [
    "PlannedStartDate",
    "PlannedEndDate",
    "ForecastEndDate",
]:

    roadmap_dates_df[
        date_column
    ] = pd.to_datetime(
        roadmap_dates_df[
            date_column
        ]
    )


assert (
    roadmap_dates_df[
        "PlannedEndDate"
    ]
    >=
    roadmap_dates_df[
        "PlannedStartDate"
    ]
).all(), (
    "Roadmap PlannedEndDate occurs "
    "before PlannedStartDate."
)


calculated_schedule_variance = (
    roadmap_dates_df[
        "ForecastEndDate"
    ]
    -
    roadmap_dates_df[
        "PlannedEndDate"
    ]
).dt.days


assert (
    calculated_schedule_variance
    ==
    roadmap_items_df[
        "ScheduleVarianceDays"
    ]
).all(), (
    "Roadmap schedule variance "
    "calculation is incorrect."
)


assert roadmap_items_df[
    "ProgressPercent"
].between(
    0,
    100,
).all(), (
    "Invalid roadmap ProgressPercent."
)


# ============================================================
# EXPORT ROADMAP ITEMS
# ============================================================

ROADMAP_ITEMS_FILE = (
    config.RAW_DATA_DIR
    / "roadmap_items.csv"
)


roadmap_items_df.to_csv(
    ROADMAP_ITEMS_FILE,
    index=False,
)


# ============================================================
# ROADMAP SUMMARY
# ============================================================

print(
    f"\nRoadmap Items generated: "
    f"{len(roadmap_items_df):,}"
)


print(
    f"Projects represented   : "
    f"{roadmap_items_df['ProjectID'].nunique()}"
)


print(
    f"Programs represented   : "
    f"{roadmap_items_df['ProgramID'].nunique()}"
)


print(
    f"Linked to products     : "
    f"{roadmap_items_df['ProductID'].notna().sum():,}"
)


print(
    f"Linked to releases     : "
    f"{roadmap_items_df['ReleaseID'].notna().sum():,}"
)


print(
    "\nRoadmap Status Distribution:"
)


print(
    roadmap_items_df[
        "RoadmapStatus"
    ].value_counts()
)


print(
    "\nRoadmap Type Distribution:"
)


print(
    roadmap_items_df[
        "RoadmapType"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{ROADMAP_ITEMS_FILE}"
)


print(
    "\nRoadmap validation passed."
)


print(
    "roadmap_items.csv generated successfully!"
)


print("\n" + "=" * 70)

print(
    "GOVERNANCE DATA GENERATION COMPLETE"
)

print("=" * 70)