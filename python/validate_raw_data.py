"""
Portfolio-wide raw data validation for the
Engineering Portfolio Management & Delivery Intelligence Platform.

This script validates:
- Expected row counts
- Primary key uniqueness
- Foreign key integrity
- Cross-table relationship consistency
- Date logic
- Work item hierarchy integrity
- Project/team consistency
- Governance relationships
"""

import pandas as pd

from python import config


print("=" * 70)
print("RAW DATA VALIDATION")
print("=" * 70)


# ============================================================
# FILE REGISTRY
# ============================================================

FILES = {
    "programs": config.RAW_DATA_DIR / "programs.csv",
    "projects": config.RAW_DATA_DIR / "projects.csv",
    "products": config.RAW_DATA_DIR / "products.csv",
    "teams": config.RAW_DATA_DIR / "teams.csv",
    "employees": config.RAW_DATA_DIR / "employees.csv",
    "stakeholders": config.RAW_DATA_DIR / "stakeholders.csv",

    "employee_team_assignments":
        config.RAW_DATA_DIR / "employee_team_assignments.csv",

    "project_team_assignments":
        config.RAW_DATA_DIR / "project_team_assignments.csv",

    "project_stakeholder_assignments":
        config.RAW_DATA_DIR / "project_stakeholder_assignments.csv",

    "sprints": config.RAW_DATA_DIR / "sprints.csv",
    "work_items": config.RAW_DATA_DIR / "work_items.csv",
    "releases": config.RAW_DATA_DIR / "releases.csv",
    "dependencies": config.RAW_DATA_DIR / "dependencies.csv",

    "risks": config.RAW_DATA_DIR / "risks.csv",
    "meetings": config.RAW_DATA_DIR / "meetings.csv",
    "action_items": config.RAW_DATA_DIR / "action_items.csv",
    "decisions": config.RAW_DATA_DIR / "decisions.csv",
    "okrs": config.RAW_DATA_DIR / "okrs.csv",
    "roadmap_items": config.RAW_DATA_DIR / "roadmap_items.csv",
}


# ============================================================
# FILE EXISTENCE
# ============================================================

missing_files = [
    name
    for name, path in FILES.items()
    if not path.exists()
]


assert not missing_files, (
    f"Missing required files: {missing_files}"
)


print(
    f"\nFiles found: {len(FILES)}"
)


# ============================================================
# LOAD DATA
# ============================================================

dfs = {
    name: pd.read_csv(path)
    for name, path in FILES.items()
}


programs_df = dfs["programs"]
projects_df = dfs["projects"]
products_df = dfs["products"]
teams_df = dfs["teams"]
employees_df = dfs["employees"]
stakeholders_df = dfs["stakeholders"]

employee_team_df = (
    dfs["employee_team_assignments"]
)

project_team_df = (
    dfs["project_team_assignments"]
)

project_stakeholder_df = (
    dfs["project_stakeholder_assignments"]
)

sprints_df = dfs["sprints"]
work_items_df = dfs["work_items"]
releases_df = dfs["releases"]
dependencies_df = dfs["dependencies"]

risks_df = dfs["risks"]
meetings_df = dfs["meetings"]
action_items_df = dfs["action_items"]
decisions_df = dfs["decisions"]
okrs_df = dfs["okrs"]
roadmap_df = dfs["roadmap_items"]


# ============================================================
# HELPERS
# ============================================================

checks_passed = 0


def pass_check(message):
    global checks_passed

    checks_passed += 1

    print(
        f"[PASS] {message}"
    )


def assert_unique(
    df,
    column,
    table_name,
):
    assert df[column].is_unique, (
        f"{table_name}.{column} "
        f"contains duplicates."
    )

    pass_check(
        f"{table_name}.{column} is unique"
    )


def assert_fk(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name,
    allow_null=False,
):
    child_values = (
        child_df[
            child_column
        ]
    )


    if allow_null:

        child_values = (
            child_values.dropna()
        )


    child_values = set(
        child_values
    )


    parent_values = set(
        parent_df[
            parent_column
        ]
    )


    invalid_values = (
        child_values
        - parent_values
    )


    assert not invalid_values, (
        f"{relationship_name} has invalid values: "
        f"{list(invalid_values)[:10]}"
    )


    pass_check(
        relationship_name
    )


# ============================================================
# EXPECTED ROW COUNTS
# ============================================================

expected_counts = {
    "programs":
        config.NUM_PROGRAMS,

    "projects":
        config.NUM_PROJECTS,

    "products":
        config.NUM_PRODUCTS,

    "teams":
        config.NUM_TEAMS,

    "employees":
        config.NUM_EMPLOYEES,

    "stakeholders":
        config.NUM_STAKEHOLDERS,

    "sprints":
        config.TARGET_SPRINTS,

    "work_items":
        (
            config.TARGET_EPICS
            + config.TARGET_FEATURES
            + config.TARGET_USER_STORIES
            + config.TARGET_TASKS
            + config.TARGET_BUGS
        ),

    "releases":
        config.TARGET_RELEASES,

    "dependencies":
        config.TARGET_DEPENDENCIES,

    "risks":
        config.TARGET_RISKS,

    "meetings":
        config.TARGET_MEETINGS,

    "action_items":
        config.TARGET_ACTION_ITEMS,

    "decisions":
        config.TARGET_DECISIONS,

    "okrs":
        config.TARGET_OKRS,

    "roadmap_items":
        config.TARGET_ROADMAP_ITEMS,
}


for table_name, expected_count in (
    expected_counts.items()
):

    actual_count = len(
        dfs[
            table_name
        ]
    )


    assert actual_count == expected_count, (
        f"{table_name} row count mismatch. "
        f"Expected {expected_count}, "
        f"found {actual_count}."
    )


    pass_check(
        f"{table_name} row count = {actual_count:,}"
    )


# ============================================================
# PRIMARY KEY UNIQUENESS
# ============================================================

assert_unique(
    programs_df,
    "ProgramID",
    "programs",
)

assert_unique(
    projects_df,
    "ProjectID",
    "projects",
)

assert_unique(
    products_df,
    "ProductID",
    "products",
)

assert_unique(
    teams_df,
    "TeamID",
    "teams",
)

assert_unique(
    employees_df,
    "EmployeeID",
    "employees",
)

assert_unique(
    stakeholders_df,
    "StakeholderID",
    "stakeholders",
)

assert_unique(
    employee_team_df,
    "AssignmentID",
    "employee_team_assignments",
)

assert_unique(
    project_team_df,
    "ProjectTeamAssignmentID",
    "project_team_assignments",
)

assert_unique(
    project_stakeholder_df,
    "ProjectStakeholderAssignmentID",
    "project_stakeholder_assignments",
)

assert_unique(
    sprints_df,
    "SprintID",
    "sprints",
)

assert_unique(
    work_items_df,
    "WorkItemID",
    "work_items",
)

assert_unique(
    releases_df,
    "ReleaseID",
    "releases",
)

assert_unique(
    dependencies_df,
    "DependencyID",
    "dependencies",
)

assert_unique(
    risks_df,
    "RiskID",
    "risks",
)

assert_unique(
    meetings_df,
    "MeetingID",
    "meetings",
)

assert_unique(
    action_items_df,
    "ActionItemID",
    "action_items",
)

assert_unique(
    decisions_df,
    "DecisionID",
    "decisions",
)

assert_unique(
    okrs_df,
    "OKRID",
    "okrs",
)

assert_unique(
    roadmap_df,
    "RoadmapItemID",
    "roadmap_items",
)


# ============================================================
# FOREIGN KEY INTEGRITY
# ============================================================

assert_fk(
    projects_df,
    "ProgramID",
    programs_df,
    "ProgramID",
    "projects.ProgramID -> programs.ProgramID",
)

assert_fk(
    products_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "products.ProjectID -> projects.ProjectID",
)

assert_fk(
    employee_team_df,
    "EmployeeID",
    employees_df,
    "EmployeeID",
    "employee_team_assignments.EmployeeID -> employees.EmployeeID",
)

assert_fk(
    employee_team_df,
    "TeamID",
    teams_df,
    "TeamID",
    "employee_team_assignments.TeamID -> teams.TeamID",
)

assert_fk(
    project_team_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "project_team_assignments.ProjectID -> projects.ProjectID",
)

assert_fk(
    project_team_df,
    "TeamID",
    teams_df,
    "TeamID",
    "project_team_assignments.TeamID -> teams.TeamID",
)

assert_fk(
    project_stakeholder_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "project_stakeholder_assignments.ProjectID -> projects.ProjectID",
)

assert_fk(
    project_stakeholder_df,
    "StakeholderID",
    stakeholders_df,
    "StakeholderID",
    "project_stakeholder_assignments.StakeholderID -> stakeholders.StakeholderID",
)

assert_fk(
    sprints_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "sprints.ProjectID -> projects.ProjectID",
)

assert_fk(
    sprints_df,
    "TeamID",
    teams_df,
    "TeamID",
    "sprints.TeamID -> teams.TeamID",
)

assert_fk(
    work_items_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "work_items.ProjectID -> projects.ProjectID",
    allow_null=True,
)

assert_fk(
    work_items_df,
    "TeamID",
    teams_df,
    "TeamID",
    "work_items.TeamID -> teams.TeamID",
    allow_null=True,
)

assert_fk(
    work_items_df,
    "SprintID",
    sprints_df,
    "SprintID",
    "work_items.SprintID -> sprints.SprintID",
    allow_null=True,
)

assert_fk(
    releases_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "releases.ProjectID -> projects.ProjectID",
)

assert_fk(
    releases_df,
    "ProductID",
    products_df,
    "ProductID",
    "releases.ProductID -> products.ProductID",
    allow_null=True,
)

assert_fk(
    dependencies_df,
    "DependentProjectID",
    projects_df,
    "ProjectID",
    "dependencies.DependentProjectID -> projects.ProjectID",
)

assert_fk(
    dependencies_df,
    "ProviderProjectID",
    projects_df,
    "ProjectID",
    "dependencies.ProviderProjectID -> projects.ProjectID",
)

assert_fk(
    dependencies_df,
    "DependentTeamID",
    teams_df,
    "TeamID",
    "dependencies.DependentTeamID -> teams.TeamID",
)

assert_fk(
    dependencies_df,
    "ProviderTeamID",
    teams_df,
    "TeamID",
    "dependencies.ProviderTeamID -> teams.TeamID",
)

assert_fk(
    risks_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "risks.ProjectID -> projects.ProjectID",
)

assert_fk(
    meetings_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "meetings.ProjectID -> projects.ProjectID",
)

assert_fk(
    meetings_df,
    "ProgramID",
    programs_df,
    "ProgramID",
    "meetings.ProgramID -> programs.ProgramID",
)

assert_fk(
    action_items_df,
    "MeetingID",
    meetings_df,
    "MeetingID",
    "action_items.MeetingID -> meetings.MeetingID",
)

assert_fk(
    decisions_df,
    "MeetingID",
    meetings_df,
    "MeetingID",
    "decisions.MeetingID -> meetings.MeetingID",
)

assert_fk(
    okrs_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "okrs.ProjectID -> projects.ProjectID",
)

assert_fk(
    roadmap_df,
    "ProjectID",
    projects_df,
    "ProjectID",
    "roadmap_items.ProjectID -> projects.ProjectID",
)

assert_fk(
    roadmap_df,
    "ProductID",
    products_df,
    "ProductID",
    "roadmap_items.ProductID -> products.ProductID",
    allow_null=True,
)

assert_fk(
    roadmap_df,
    "ReleaseID",
    releases_df,
    "ReleaseID",
    "roadmap_items.ReleaseID -> releases.ReleaseID",
    allow_null=True,
)


# ============================================================
# PROJECT -> PROGRAM CONSISTENCY
# ============================================================

project_program_lookup = (
    projects_df
    .set_index(
        "ProjectID"
    )[
        "ProgramID"
    ]
    .to_dict()
)


for table_name, df in [
    (
        "meetings",
        meetings_df,
    ),
    (
        "action_items",
        action_items_df,
    ),
    (
        "decisions",
        decisions_df,
    ),
    (
        "okrs",
        okrs_df,
    ),
    (
        "roadmap_items",
        roadmap_df,
    ),
]:

    expected_programs = (
        df[
            "ProjectID"
        ]
        .map(
            project_program_lookup
        )
    )


    assert (
        expected_programs
        ==
        df[
            "ProgramID"
        ]
    ).all(), (
        f"{table_name} has ProjectID / "
        f"ProgramID mismatch."
    )


    pass_check(
        f"{table_name} ProjectID -> ProgramID consistency"
    )


# ============================================================
# PROJECT -> TEAM CONSISTENCY
# ============================================================

valid_project_team_pairs = set(
    zip(
        project_team_df[
            "ProjectID"
        ],
        project_team_df[
            "TeamID"
        ],
    )
)


sprint_pairs = set(
    zip(
        sprints_df[
            "ProjectID"
        ],
        sprints_df[
            "TeamID"
        ],
    )
)


invalid_sprint_pairs = (
    sprint_pairs
    - valid_project_team_pairs
)


assert not invalid_sprint_pairs, (
    "Sprints contain invalid ProjectID / "
    "TeamID combinations."
)


pass_check(
    "Sprint ProjectID / TeamID combinations are valid"
)


# ============================================================
# WORK ITEM TYPE COUNTS
# ============================================================

expected_work_item_counts = {
    "Epic":
        config.TARGET_EPICS,

    "Feature":
        config.TARGET_FEATURES,

    "User Story":
        config.TARGET_USER_STORIES,

    "Task":
        config.TARGET_TASKS,

    "Bug":
        config.TARGET_BUGS,
}


actual_work_item_counts = (
    work_items_df[
        "WorkItemType"
    ]
    .value_counts()
    .to_dict()
)


assert (
    actual_work_item_counts
    ==
    expected_work_item_counts
), (
    "Work item type counts do not "
    "match configuration."
)


pass_check(
    "Work item type counts match configuration"
)


# ============================================================
# WORK ITEM HIERARCHY
# ============================================================

work_item_type_lookup = (
    work_items_df
    .set_index(
        "WorkItemID"
    )[
        "WorkItemType"
    ]
    .to_dict()
)


features_df = (
    work_items_df[
        work_items_df[
            "WorkItemType"
        ]
        == "Feature"
    ]
)


stories_df = (
    work_items_df[
        work_items_df[
            "WorkItemType"
        ]
        == "User Story"
    ]
)


tasks_df = (
    work_items_df[
        work_items_df[
            "WorkItemType"
        ]
        == "Task"
    ]
)


bugs_df = (
    work_items_df[
        work_items_df[
            "WorkItemType"
        ]
        == "Bug"
    ]
)


assert (
    features_df[
        "ParentWorkItemID"
    ]
    .map(
        work_item_type_lookup
    )
    ==
    "Epic"
).all(), (
    "Feature parent must be Epic."
)


pass_check(
    "Feature -> Epic hierarchy"
)


assert (
    stories_df[
        "ParentWorkItemID"
    ]
    .map(
        work_item_type_lookup
    )
    ==
    "Feature"
).all(), (
    "User Story parent must be Feature."
)


pass_check(
    "User Story -> Feature hierarchy"
)


assert (
    tasks_df[
        "ParentWorkItemID"
    ]
    .map(
        work_item_type_lookup
    )
    ==
    "User Story"
).all(), (
    "Task parent must be User Story."
)


pass_check(
    "Task -> User Story hierarchy"
)


assert (
    bugs_df[
        "ParentWorkItemID"
    ]
    .map(
        work_item_type_lookup
    )
    ==
    "User Story"
).all(), (
    "Bug parent must be User Story."
)


pass_check(
    "Bug -> User Story hierarchy"
)


# ============================================================
# WORK ITEM PROJECT / TEAM / SPRINT INHERITANCE
# ============================================================

story_lookup = (
    stories_df
    .set_index(
        "WorkItemID"
    )[
        [
            "ProjectID",
            "TeamID",
            "SprintID",
        ]
    ]
)


for child_name, child_df in [
    (
        "Task",
        tasks_df,
    ),
    (
        "Bug",
        bugs_df,
    ),
]:

    joined = (
        child_df[
            [
                "ParentWorkItemID",
                "ProjectID",
                "TeamID",
                "SprintID",
            ]
        ]
        .merge(
            story_lookup,
            left_on="ParentWorkItemID",
            right_index=True,
            suffixes=(
                "_Child",
                "_Story",
            ),
        )
    )


    assert (
        joined[
            "ProjectID_Child"
        ]
        ==
        joined[
            "ProjectID_Story"
        ]
    ).all(), (
        f"{child_name} ProjectID does not "
        f"match parent User Story."
    )


    assert (
        joined[
            "TeamID_Child"
        ]
        ==
        joined[
            "TeamID_Story"
        ]
    ).all(), (
        f"{child_name} TeamID does not "
        f"match parent User Story."
    )


    assert (
        joined[
            "SprintID_Child"
        ]
        ==
        joined[
            "SprintID_Story"
        ]
    ).all(), (
        f"{child_name} SprintID does not "
        f"match parent User Story."
    )


    pass_check(
        f"{child_name} inherits Project/Team/Sprint from User Story"
    )


# ============================================================
# DEPENDENCY VALIDATION
# ============================================================

assert (
    dependencies_df[
        "DependentProjectID"
    ]
    !=
    dependencies_df[
        "ProviderProjectID"
    ]
).all(), (
    "Self-dependencies detected."
)


pass_check(
    "No project self-dependencies"
)


# ============================================================
# RELEASE -> PRODUCT CONSISTENCY
# ============================================================

product_project_lookup = (
    products_df
    .set_index(
        "ProductID"
    )[
        "ProjectID"
    ]
    .to_dict()
)


release_products = (
    releases_df[
        releases_df[
            "ProductID"
        ].notna()
    ]
)


expected_release_project = (
    release_products[
        "ProductID"
    ]
    .astype(int)
    .map(
        product_project_lookup
    )
)


assert (
    expected_release_project.values
    ==
    release_products[
        "ProjectID"
    ].values
).all(), (
    "Release ProductID does not belong "
    "to Release ProjectID."
)


pass_check(
    "Release ProductID -> ProjectID consistency"
)


# ============================================================
# MEETING -> ACTION / DECISION CONSISTENCY
# ============================================================

meeting_project_lookup = (
    meetings_df
    .set_index(
        "MeetingID"
    )[
        "ProjectID"
    ]
    .to_dict()
)


meeting_program_lookup = (
    meetings_df
    .set_index(
        "MeetingID"
    )[
        "ProgramID"
    ]
    .to_dict()
)


for table_name, df in [
    (
        "action_items",
        action_items_df,
    ),
    (
        "decisions",
        decisions_df,
    ),
]:

    assert (
        df[
            "MeetingID"
        ]
        .map(
            meeting_project_lookup
        )
        ==
        df[
            "ProjectID"
        ]
    ).all(), (
        f"{table_name} MeetingID / "
        f"ProjectID mismatch."
    )


    assert (
        df[
            "MeetingID"
        ]
        .map(
            meeting_program_lookup
        )
        ==
        df[
            "ProgramID"
        ]
    ).all(), (
        f"{table_name} MeetingID / "
        f"ProgramID mismatch."
    )


    pass_check(
        f"{table_name} inherits Project/Program from Meeting"
    )


# ============================================================
# ROADMAP -> RELEASE CONSISTENCY
# ============================================================

release_project_lookup = (
    releases_df
    .set_index(
        "ReleaseID"
    )[
        "ProjectID"
    ]
    .to_dict()
)


linked_roadmap = (
    roadmap_df[
        roadmap_df[
            "ReleaseID"
        ].notna()
    ]
)


expected_roadmap_project = (
    linked_roadmap[
        "ReleaseID"
    ]
    .astype(int)
    .map(
        release_project_lookup
    )
)


assert (
    expected_roadmap_project.values
    ==
    linked_roadmap[
        "ProjectID"
    ].values
).all(), (
    "Roadmap ReleaseID does not belong "
    "to Roadmap ProjectID."
)


pass_check(
    "Roadmap ReleaseID -> ProjectID consistency"
)


# ============================================================
# DATE LOGIC
# ============================================================

date_checks = [
    (
        projects_df,
        "StartDate",
        "PlannedEndDate",
        "projects",
    ),
    (
        sprints_df,
        "StartDate",
        "EndDate",
        "sprints",
    ),
    (
        employee_team_df,
        "AssignmentStartDate",
        "AssignmentEndDate",
        "employee_team_assignments",
    ),
    (
        project_team_df,
        "AssignmentStartDate",
        "AssignmentEndDate",
        "project_team_assignments",
    ),
    (
        project_stakeholder_df,
        "AssignmentStartDate",
        "AssignmentEndDate",
        "project_stakeholder_assignments",
    ),
    (
        risks_df,
        "IdentifiedDate",
        "TargetMitigationDate",
        "risks",
    ),
    (
        action_items_df,
        "CreatedDate",
        "DueDate",
        "action_items",
    ),
    (
        okrs_df,
        "PeriodStartDate",
        "PeriodEndDate",
        "okrs",
    ),
    (
        roadmap_df,
        "PlannedStartDate",
        "PlannedEndDate",
        "roadmap_items",
    ),
]


for (
    df,
    start_column,
    end_column,
    table_name,
) in date_checks:

    start_dates = pd.to_datetime(
        df[
            start_column
        ],
        errors="coerce",
    )


    end_dates = pd.to_datetime(
        df[
            end_column
        ],
        errors="coerce",
    )


    comparable = (
        start_dates.notna()
        &
        end_dates.notna()
    )


    assert (
        end_dates[
            comparable
        ]
        >=
        start_dates[
            comparable
        ]
    ).all(), (
        f"{table_name} contains invalid "
        f"{start_column}/{end_column} ordering."
    )


    pass_check(
        f"{table_name} date ordering"
    )


# ============================================================
# CLOSED / COMPLETED DATE LOGIC
# ============================================================

risk_closed_dates = pd.to_datetime(
    risks_df[
        "ClosedDate"
    ],
    errors="coerce",
)


assert (
    risk_closed_dates[
        risks_df[
            "RiskStatus"
        ]
        == "Closed"
    ]
    .notna()
    .all()
), (
    "Closed risks missing ClosedDate."
)


assert (
    risk_closed_dates[
        risks_df[
            "RiskStatus"
        ]
        != "Closed"
    ]
    .isna()
    .all()
), (
    "Non-closed risks contain ClosedDate."
)


pass_check(
    "Risk status / ClosedDate consistency"
)


action_completed_dates = pd.to_datetime(
    action_items_df[
        "CompletedDate"
    ],
    errors="coerce",
)


assert (
    action_completed_dates[
        action_items_df[
            "ActionStatus"
        ]
        == "Completed"
    ]
    .notna()
    .all()
), (
    "Completed actions missing CompletedDate."
)


assert (
    action_completed_dates[
        action_items_df[
            "ActionStatus"
        ]
        != "Completed"
    ]
    .isna()
    .all()
), (
    "Incomplete actions contain CompletedDate."
)


pass_check(
    "Action status / CompletedDate consistency"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)

print(
    f"ALL VALIDATION CHECKS PASSED: "
    f"{checks_passed}"
)

print("=" * 70)

print(
    "\nRaw data layer is ready "
    "for database loading."
)