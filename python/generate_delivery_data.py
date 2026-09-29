"""
Generate delivery data for the Engineering Portfolio Management
& Delivery Intelligence Platform.

Delivery datasets:
1. Sprints
2. Work Items
3. Releases
4. Dependencies

This first section generates and validates Sprints.
"""
import random

import numpy as np
import pandas as pd

from python import config


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(config.RANDOM_SEED + 100)
np.random.seed(config.RANDOM_SEED + 100)


# ============================================================
# FILE PATHS
# ============================================================

PROJECTS_FILE = (
    config.RAW_DATA_DIR
    / "projects.csv"
)

TEAMS_FILE = (
    config.RAW_DATA_DIR
    / "teams.csv"
)

PROJECT_TEAM_FILE = (
    config.RAW_DATA_DIR
    / "project_team_assignments.csv"
)


# ============================================================
# VALIDATE REQUIRED SOURCE FILES
# ============================================================

required_files = [
    PROJECTS_FILE,
    TEAMS_FILE,
    PROJECT_TEAM_FILE,
]


for file_path in required_files:

    if not file_path.exists():

        raise FileNotFoundError(
            f"Required source file missing: "
            f"{file_path}"
        )


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


teams_df = pd.read_csv(
    TEAMS_FILE
)


project_team_df = pd.read_csv(
    PROJECT_TEAM_FILE,
    parse_dates=[
        "AssignmentStartDate",
        "AssignmentEndDate",
    ],
)


# ============================================================
# BASIC SOURCE VALIDATION
# ============================================================

assert len(projects_df) == config.NUM_PROJECTS, (
    "Unexpected project count."
)


assert len(teams_df) == config.NUM_TEAMS, (
    "Unexpected team count."
)


assert projects_df[
    "ProjectID"
].is_unique, (
    "Duplicate ProjectID detected."
)


assert teams_df[
    "TeamID"
].is_unique, (
    "Duplicate TeamID detected."
)


# ============================================================
# BUILD VALID PROJECT-TEAM WINDOWS
# ============================================================

assignment_windows = (
    project_team_df
    .merge(
        projects_df[
            [
                "ProjectID",
                "StartDate",
                "PlannedEndDate",
            ]
        ],
        on="ProjectID",
        how="left",
    )
    .merge(
        teams_df[
            [
                "TeamID",
                "PlannedTeamSize",
                "VelocityTarget",
            ]
        ],
        on="TeamID",
        how="left",
    )
)


assignment_windows[
    "EffectiveStartDate"
] = assignment_windows[
    [
        "AssignmentStartDate",
        "StartDate",
    ]
].max(axis=1)


assignment_windows[
    "EffectiveEndDate"
] = assignment_windows[
    [
        "AssignmentEndDate",
        "PlannedEndDate",
    ]
].min(axis=1)


assignment_windows = assignment_windows[
    (
        assignment_windows[
            "EffectiveEndDate"
        ]
        -
        assignment_windows[
            "EffectiveStartDate"
        ]
    ).dt.days
    >= config.SPRINT_LENGTH_DAYS
].copy()


if assignment_windows.empty:

    raise ValueError(
        "No valid project-team assignment "
        "windows were found."
    )


# ============================================================
# CREATE ALL POSSIBLE SPRINT WINDOWS
# ============================================================

possible_sprints = []


for _, assignment in assignment_windows.iterrows():

    project_id = int(
        assignment["ProjectID"]
    )

    team_id = int(
        assignment["TeamID"]
    )

    sprint_start = pd.Timestamp(
        assignment[
            "EffectiveStartDate"
        ]
    )

    assignment_end = pd.Timestamp(
        assignment[
            "EffectiveEndDate"
        ]
    )

    sprint_number = 1


    while True:

        sprint_end = (
            sprint_start
            + pd.Timedelta(
                days=(
                    config.SPRINT_LENGTH_DAYS
                    - 1
                )
            )
        )


        if sprint_end > assignment_end:
            break


        possible_sprints.append(
            {
                "ProjectID":
                    project_id,

                "TeamID":
                    team_id,

                "SprintNumber":
                    sprint_number,

                "StartDate":
                    sprint_start,

                "EndDate":
                    sprint_end,

                "PlannedTeamSize":
                    int(
                        assignment[
                            "PlannedTeamSize"
                        ]
                    ),

                "VelocityTarget":
                    int(
                        assignment[
                            "VelocityTarget"
                        ]
                    ),
            }
        )


        sprint_number += 1

        sprint_start = (
            sprint_start
            + pd.Timedelta(
                days=config.SPRINT_LENGTH_DAYS
            )
        )


possible_sprints_df = pd.DataFrame(
    possible_sprints
)


print(
    f"Possible sprint windows found: "
    f"{len(possible_sprints_df)}"
)


if len(
    possible_sprints_df
) < config.TARGET_SPRINTS:

    raise ValueError(
        f"Only {len(possible_sprints_df)} "
        f"valid sprint windows exist, but "
        f"{config.TARGET_SPRINTS} are required."
    )


# ============================================================
# GUARANTEE EVERY PROJECT HAS SPRINT COVERAGE
# ============================================================

selected_indices = set()


for project_id, group in (
    possible_sprints_df
    .groupby("ProjectID")
):

    chosen_index = random.choice(
        group.index.tolist()
    )

    selected_indices.add(
        chosen_index
    )


covered_projects = set(
    possible_sprints_df
    .loc[
        list(selected_indices),
        "ProjectID"
    ]
)


expected_projects = set(
    projects_df[
        "ProjectID"
    ]
)


if covered_projects != expected_projects:

    missing = (
        expected_projects
        - covered_projects
    )

    raise ValueError(
        f"Projects without sprint coverage: "
        f"{missing}"
    )


# ============================================================
# FILL REMAINING SPRINT TARGET
# ============================================================

remaining_needed = (
    config.TARGET_SPRINTS
    - len(selected_indices)
)


available_indices = [
    index
    for index
    in possible_sprints_df.index
    if index not in selected_indices
]


additional_indices = random.sample(
    available_indices,
    remaining_needed,
)


selected_indices.update(
    additional_indices
)


selected_sprints_df = (
    possible_sprints_df
    .loc[
        sorted(selected_indices)
    ]
    .copy()
)


# ============================================================
# SPRINT GOALS
# ============================================================

SPRINT_GOALS = [
    "Deliver planned feature increment",
    "Improve platform reliability",
    "Complete API integration milestone",
    "Reduce technical debt",
    "Improve security posture",
    "Complete modernization milestone",
    "Improve developer experience",
    "Deliver customer-facing capability",
    "Improve operational readiness",
    "Complete data platform enhancement",
]


# ============================================================
# GENERATE SPRINT PERFORMANCE
# ============================================================

sprints = []


for sprint_id, (_, sprint) in enumerate(
    selected_sprints_df.iterrows(),
    start=1,
):

    team_size = int(
        sprint["PlannedTeamSize"]
    )

    velocity_target = int(
        sprint["VelocityTarget"]
    )


    planned_capacity_hours = (
        team_size
        * config.STANDARD_WEEKLY_HOURS
        * 2
    )


    # Capacity availability is intentionally
    # correlated with delivery performance.
    capacity_factor = random.choices(
        population=[
            0.65,
            0.75,
            0.85,
            0.95,
            1.00,
        ],
        weights=[
            5,
            10,
            20,
            30,
            35,
        ],
        k=1,
    )[0]


    actual_capacity_hours = round(
        planned_capacity_hours
        * capacity_factor
    )


    committed_story_points = max(
        10,
        round(
            np.random.normal(
                loc=velocity_target,
                scale=max(
                    4,
                    velocity_target * 0.12,
                ),
            )
        ),
    )


    base_completion_ratio = (
        0.72
        +
        (
            capacity_factor
            - 0.65
        )
        * 0.65
    )


    completion_ratio = float(
        np.clip(
            base_completion_ratio
            + np.random.normal(
                0,
                0.06,
            ),
            0.55,
            1.00,
        )
    )


    completed_story_points = round(
        committed_story_points
        * completion_ratio
    )


    completed_story_points = min(
        completed_story_points,
        committed_story_points,
    )


    spillover_story_points = (
        committed_story_points
        - completed_story_points
    )


    completion_percent = round(
        (
            completed_story_points
            /
            committed_story_points
        )
        * 100,
        1,
    )


    capacity_percent = round(
        (
            actual_capacity_hours
            /
            planned_capacity_hours
        )
        * 100,
        1,
    )


    sprint_record = {

        "SprintID":
            sprint_id,

        "ProjectID":
            int(
                sprint["ProjectID"]
            ),

        "TeamID":
            int(
                sprint["TeamID"]
            ),

        "SprintName":
            (
                f"P{int(sprint['ProjectID']):03d}"
                f"-T{int(sprint['TeamID']):02d}"
                f"-Sprint-"
                f"{int(sprint['SprintNumber']):02d}"
            ),

        "SprintNumber":
            int(
                sprint["SprintNumber"]
            ),

        "StartDate":
            pd.Timestamp(
                sprint["StartDate"]
            ).date(),

        "EndDate":
            pd.Timestamp(
                sprint["EndDate"]
            ).date(),

        "SprintGoal":
            random.choice(
                SPRINT_GOALS
            ),

        "PlannedCapacityHours":
            planned_capacity_hours,

        "ActualCapacityHours":
            actual_capacity_hours,

        "CapacityUtilizationPercent":
            capacity_percent,

        "CommittedStoryPoints":
            committed_story_points,

        "CompletedStoryPoints":
            completed_story_points,

        "Velocity":
            completed_story_points,

        "SpilloverStoryPoints":
            spillover_story_points,

        "CompletionPercent":
            completion_percent,

        "SprintStatus":
            "Completed",
    }


    sprints.append(
        sprint_record
    )


# ============================================================
# CREATE SPRINT DATAFRAME
# ============================================================

sprints_df = pd.DataFrame(
    sprints
)


# ============================================================
# SPRINT VALIDATION
# ============================================================

assert len(
    sprints_df
) == config.TARGET_SPRINTS, (
    "Incorrect sprint count."
)


assert sprints_df[
    "SprintID"
].is_unique, (
    "Duplicate SprintID detected."
)


assert sprints_df[
    "ProjectID"
].nunique() == config.NUM_PROJECTS, (
    "Not every project has sprint coverage."
)


assert (
    sprints_df[
        "CompletedStoryPoints"
    ]
    <=
    sprints_df[
        "CommittedStoryPoints"
    ]
).all(), (
    "Completed story points exceed commitment."
)


assert (
    sprints_df[
        "SpilloverStoryPoints"
    ]
    ==
    (
        sprints_df[
            "CommittedStoryPoints"
        ]
        -
        sprints_df[
            "CompletedStoryPoints"
        ]
    )
).all(), (
    "Sprint spillover calculation is incorrect."
)


valid_project_team_pairs = set(
    zip(
        project_team_df["ProjectID"],
        project_team_df["TeamID"],
    )
)


generated_project_team_pairs = set(
    zip(
        sprints_df["ProjectID"],
        sprints_df["TeamID"],
    )
)


assert generated_project_team_pairs.issubset(
    valid_project_team_pairs
), (
    "Invalid Project-Team combination "
    "found in sprint data."
)


# ============================================================
# EXPORT SPRINTS
# ============================================================

SPRINT_OUTPUT_FILE = (
    config.RAW_DATA_DIR
    / "sprints.csv"
)


sprints_df.to_csv(
    SPRINT_OUTPUT_FILE,
    index=False,
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DELIVERY DATA GENERATION - SPRINTS")
print("=" * 70)


print(
    f"\nSprints generated    : "
    f"{len(sprints_df)}"
)


print(
    f"Projects represented : "
    f"{sprints_df['ProjectID'].nunique()}"
)


print(
    f"Teams represented    : "
    f"{sprints_df['TeamID'].nunique()}"
)


print(
    f"Average velocity     : "
    f"{sprints_df['Velocity'].mean():.2f}"
)


print(
    f"Average completion   : "
    f"{sprints_df['CompletionPercent'].mean():.2f}%"
)


print(
    f"Average capacity     : "
    f"{sprints_df['CapacityUtilizationPercent'].mean():.2f}%"
)


print(
    f"Total spillover      : "
    f"{sprints_df['SpilloverStoryPoints'].sum()}"
)


print(
    f"\nOutput:"
    f"\n{SPRINT_OUTPUT_FILE}"
)


print(
    "\nSprint validation passed."
)


print(
    "sprints.csv generated successfully!"
)
# ============================================================
# WORK ITEM GENERATION
# PART 1: EPICS -> FEATURES -> USER STORIES
# ============================================================

print("\n" + "=" * 70)
print("DELIVERY DATA GENERATION - WORK ITEMS")
print("=" * 70)


# ============================================================
# WORK ITEM SETTINGS
# ============================================================

WORK_ITEM_STATES = [
    "New",
    "Active",
    "Resolved",
    "Closed",
]


PRIORITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]


STORY_POINT_OPTIONS = [
    1,
    2,
    3,
    5,
    8,
    13,
]


EPIC_THEMES = [
    "Platform Modernization",
    "Security Improvement",
    "Developer Experience",
    "Cloud Migration",
    "API Transformation",
    "Operational Excellence",
    "Data Platform Enhancement",
    "Application Modernization",
    "Reliability Improvement",
    "Engineering Productivity",
]


FEATURE_THEMES = [
    "Authentication Enhancement",
    "API Integration",
    "Monitoring Capability",
    "Deployment Automation",
    "Security Controls",
    "Data Processing",
    "Developer Tooling",
    "Platform Reliability",
    "Service Integration",
    "Performance Improvement",
]


STORY_THEMES = [
    "Implement service capability",
    "Configure platform component",
    "Improve user workflow",
    "Add validation logic",
    "Implement API endpoint",
    "Improve monitoring",
    "Automate deployment step",
    "Add security control",
    "Improve error handling",
    "Implement data processing",
]


# ============================================================
# HELPER FUNCTION: WORK ITEM STATE
# ============================================================

def choose_work_item_state(sprint_end_date):
    """
    Choose a state based partly on sprint timing.

    Older sprint work is more likely to be resolved or closed,
    while newer work has a higher probability of remaining active.
    """

    sprint_end_date = pd.Timestamp(
        sprint_end_date
    )

    data_end = pd.Timestamp(
        config.DATA_END_DATE
    )

    days_from_end = (
        data_end
        - sprint_end_date
    ).days


    if days_from_end > 180:

        return random.choices(
            population=[
                "Closed",
                "Resolved",
                "Active",
            ],
            weights=[
                75,
                20,
                5,
            ],
            k=1,
        )[0]


    if days_from_end > 60:

        return random.choices(
            population=[
                "Closed",
                "Resolved",
                "Active",
                "New",
            ],
            weights=[
                55,
                25,
                15,
                5,
            ],
            k=1,
        )[0]


    return random.choices(
        population=[
            "Closed",
            "Resolved",
            "Active",
            "New",
        ],
        weights=[
            30,
            25,
            35,
            10,
        ],
        k=1,
    )[0]


# ============================================================
# HELPER FUNCTION: DATES
# ============================================================

def create_work_item_dates(
    state,
    sprint_start,
    sprint_end,
):
    """
    Create logically ordered work-item lifecycle dates.
    """

    sprint_start = pd.Timestamp(
        sprint_start
    )

    sprint_end = pd.Timestamp(
        sprint_end
    )


    created_date = (
        sprint_start
        - pd.Timedelta(
            days=random.randint(
                1,
                30,
            )
        )
    )


    activated_date = pd.NaT
    resolved_date = pd.NaT
    closed_date = pd.NaT


    if state in [
        "Active",
        "Resolved",
        "Closed",
    ]:

        activated_date = min(
            sprint_end,
            created_date
            + pd.Timedelta(
                days=random.randint(
                    1,
                    15,
                )
            ),
        )


    if state in [
        "Resolved",
        "Closed",
    ]:

        resolution_start = max(
            activated_date,
            sprint_start,
        )

        available_days = max(
            0,
            (
                sprint_end
                - resolution_start
            ).days
        )

        resolved_date = (
            resolution_start
            + pd.Timedelta(
                days=random.randint(
                    0,
                    available_days,
                )
            )
        )


    if state == "Closed":

        closed_date = min(
            sprint_end,
            resolved_date
            + pd.Timedelta(
                days=random.randint(
                    0,
                    3,
                )
            ),
        )


    return (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    )


# ============================================================
# PREPARE PROJECT / SPRINT LOOKUPS
# ============================================================

sprints_by_project = {
    project_id: group.copy()
    for project_id, group
    in sprints_df.groupby(
        "ProjectID"
    )
}


project_ids = sorted(
    sprints_by_project.keys()
)


# ============================================================
# WORK ITEM CONTAINER
# ============================================================

work_items = []

next_work_item_id = 1


# ============================================================
# GENERATE 250 EPICS
# ============================================================

epic_ids = []


for epic_number in range(
    1,
    config.TARGET_EPICS + 1,
):

    project_id = project_ids[
        (
            epic_number - 1
        )
        % len(project_ids)
    ]


    project_sprints = (
        sprints_by_project[
            project_id
        ]
    )


    sprint = project_sprints.sample(
        n=1,
        random_state=(
            config.RANDOM_SEED
            + epic_number
        ),
    ).iloc[0]


    state = choose_work_item_state(
        sprint["EndDate"]
    )


    (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    ) = create_work_item_dates(
        state,
        sprint["StartDate"],
        sprint["EndDate"],
    )


    work_item_id = (
        next_work_item_id
    )


    epic_ids.append(
        work_item_id
    )


    work_items.append(
        {
            "WorkItemID":
                work_item_id,

            "ParentWorkItemID":
                pd.NA,

            "WorkItemType":
                "Epic",

            "ProjectID":
                int(project_id),

            "TeamID":
                int(
                    sprint["TeamID"]
                ),

            "SprintID":
                pd.NA,

            "Title":
                (
                    f"{random.choice(EPIC_THEMES)} "
                    f"Epic {epic_number:03d}"
                ),

            "State":
                state,

            "Priority":
                random.choices(
                    PRIORITIES,
                    weights=[
                        10,
                        35,
                        45,
                        10,
                    ],
                    k=1,
                )[0],

            "StoryPoints":
                pd.NA,

            "Severity":
                pd.NA,

            "CreatedDate":
                created_date.date(),

            "ActivatedDate":
                (
                    activated_date.date()
                    if pd.notna(
                        activated_date
                    )
                    else pd.NaT
                ),

            "ResolvedDate":
                (
                    resolved_date.date()
                    if pd.notna(
                        resolved_date
                    )
                    else pd.NaT
                ),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),
        }
    )


    next_work_item_id += 1


# ============================================================
# CREATE EPIC LOOKUP
# ============================================================

epics_df = pd.DataFrame(
    work_items
)


epics_by_project = {
    project_id:
        group["WorkItemID"].tolist()

    for project_id, group
    in epics_df.groupby(
        "ProjectID"
    )
}


# ============================================================
# GENERATE 1,000 FEATURES
# ============================================================

feature_records = []


for feature_number in range(
    1,
    config.TARGET_FEATURES + 1,
):

    project_id = project_ids[
        (
            feature_number - 1
        )
        % len(project_ids)
    ]


    parent_epic_id = random.choice(
        epics_by_project[
            project_id
        ]
    )


    project_sprints = (
        sprints_by_project[
            project_id
        ]
    )


    sprint = project_sprints.sample(
        n=1,
        random_state=(
            config.RANDOM_SEED
            + 10_000
            + feature_number
        ),
    ).iloc[0]


    state = choose_work_item_state(
        sprint["EndDate"]
    )


    (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    ) = create_work_item_dates(
        state,
        sprint["StartDate"],
        sprint["EndDate"],
    )


    work_item_id = (
        next_work_item_id
    )


    feature_records.append(
        {
            "WorkItemID":
                work_item_id,

            "ParentWorkItemID":
                parent_epic_id,

            "WorkItemType":
                "Feature",

            "ProjectID":
                int(project_id),

            "TeamID":
                int(
                    sprint["TeamID"]
                ),

            "SprintID":
                pd.NA,

            "Title":
                (
                    f"{random.choice(FEATURE_THEMES)} "
                    f"Feature {feature_number:04d}"
                ),

            "State":
                state,

            "Priority":
                random.choices(
                    PRIORITIES,
                    weights=[
                        8,
                        32,
                        48,
                        12,
                    ],
                    k=1,
                )[0],

            "StoryPoints":
                pd.NA,

            "Severity":
                pd.NA,

            "CreatedDate":
                created_date.date(),

            "ActivatedDate":
                (
                    activated_date.date()
                    if pd.notna(
                        activated_date
                    )
                    else pd.NaT
                ),

            "ResolvedDate":
                (
                    resolved_date.date()
                    if pd.notna(
                        resolved_date
                    )
                    else pd.NaT
                ),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),
        }
    )


    next_work_item_id += 1


work_items.extend(
    feature_records
)


# ============================================================
# CREATE FEATURE LOOKUP
# ============================================================

features_df = pd.DataFrame(
    feature_records
)


features_by_project = {
    project_id:
        group["WorkItemID"].tolist()

    for project_id, group
    in features_df.groupby(
        "ProjectID"
    )
}


# ============================================================
# GENERATE 8,000 USER STORIES
# ============================================================

story_records = []


for story_number in range(
    1,
    config.TARGET_USER_STORIES + 1,
):

    project_id = project_ids[
        (
            story_number - 1
        )
        % len(project_ids)
    ]


    parent_feature_id = random.choice(
        features_by_project[
            project_id
        ]
    )


    project_sprints = (
        sprints_by_project[
            project_id
        ]
    )


    sprint = project_sprints.sample(
        n=1,
        random_state=(
            config.RANDOM_SEED
            + 20_000
            + story_number
        ),
    ).iloc[0]


    state = choose_work_item_state(
        sprint["EndDate"]
    )


    (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    ) = create_work_item_dates(
        state,
        sprint["StartDate"],
        sprint["EndDate"],
    )


    work_item_id = (
        next_work_item_id
    )


    story_records.append(
        {
            "WorkItemID":
                work_item_id,

            "ParentWorkItemID":
                parent_feature_id,

            "WorkItemType":
                "User Story",

            "ProjectID":
                int(project_id),

            "TeamID":
                int(
                    sprint["TeamID"]
                ),

            "SprintID":
                int(
                    sprint["SprintID"]
                ),

            "Title":
                (
                    f"{random.choice(STORY_THEMES)} "
                    f"{story_number:05d}"
                ),

            "State":
                state,

            "Priority":
                random.choices(
                    PRIORITIES,
                    weights=[
                        5,
                        30,
                        50,
                        15,
                    ],
                    k=1,
                )[0],

            "StoryPoints":
                random.choices(
                    STORY_POINT_OPTIONS,
                    weights=[
                        8,
                        12,
                        28,
                        30,
                        17,
                        5,
                    ],
                    k=1,
                )[0],

            "Severity":
                pd.NA,

            "CreatedDate":
                created_date.date(),

            "ActivatedDate":
                (
                    activated_date.date()
                    if pd.notna(
                        activated_date
                    )
                    else pd.NaT
                ),

            "ResolvedDate":
                (
                    resolved_date.date()
                    if pd.notna(
                        resolved_date
                    )
                    else pd.NaT
                ),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),
        }
    )


    next_work_item_id += 1


work_items.extend(
    story_records
)


# ============================================================
# CREATE PART-1 DATAFRAME
# ============================================================

work_items_part1_df = pd.DataFrame(
    work_items
)


# Use nullable integer types for hierarchy fields.
work_items_part1_df[
    "WorkItemID"
] = work_items_part1_df[
    "WorkItemID"
].astype("Int64")


work_items_part1_df[
    "ParentWorkItemID"
] = work_items_part1_df[
    "ParentWorkItemID"
].astype("Int64")


work_items_part1_df[
    "SprintID"
] = work_items_part1_df[
    "SprintID"
].astype("Int64")


work_items_part1_df[
    "StoryPoints"
] = work_items_part1_df[
    "StoryPoints"
].astype("Int64")


# ============================================================
# PART-1 VALIDATION
# ============================================================

expected_part1_count = (
    config.TARGET_EPICS
    + config.TARGET_FEATURES
    + config.TARGET_USER_STORIES
)


assert len(
    work_items_part1_df
) == expected_part1_count, (
    "Incorrect Part-1 work item count."
)


assert work_items_part1_df[
    "WorkItemID"
].is_unique, (
    "Duplicate WorkItemID detected."
)


type_counts = (
    work_items_part1_df[
        "WorkItemType"
    ]
    .value_counts()
)


assert (
    type_counts.get(
        "Epic",
        0,
    )
    == config.TARGET_EPICS
)


assert (
    type_counts.get(
        "Feature",
        0,
    )
    == config.TARGET_FEATURES
)


assert (
    type_counts.get(
        "User Story",
        0,
    )
    == config.TARGET_USER_STORIES
)


# Epics must have no parent.
assert (
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "Epic",
        "ParentWorkItemID",
    ]
    .isna()
    .all()
), (
    "Epic contains a ParentWorkItemID."
)


# All Features must point to valid Epics.
valid_epic_ids = set(
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "Epic",
        "WorkItemID",
    ]
)


feature_parent_ids = set(
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "Feature",
        "ParentWorkItemID",
    ]
)


assert feature_parent_ids.issubset(
    valid_epic_ids
), (
    "Feature contains an invalid Epic parent."
)


# All Stories must point to valid Features.
valid_feature_ids = set(
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "Feature",
        "WorkItemID",
    ]
)


story_parent_ids = set(
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "User Story",
        "ParentWorkItemID",
    ]
)


assert story_parent_ids.issubset(
    valid_feature_ids
), (
    "User Story contains an invalid Feature parent."
)


# Stories must have valid Sprint IDs.
valid_sprint_ids = set(
    sprints_df[
        "SprintID"
    ]
)


story_sprint_ids = set(
    work_items_part1_df.loc[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "User Story",
        "SprintID",
    ]
)


assert story_sprint_ids.issubset(
    valid_sprint_ids
), (
    "User Story contains an invalid SprintID."
)


# Validate story Project-Team-Sprint relationships.
story_validation_df = (
    work_items_part1_df[
        work_items_part1_df[
            "WorkItemType"
        ]
        == "User Story"
    ]
    .merge(
        sprints_df[
            [
                "SprintID",
                "ProjectID",
                "TeamID",
            ]
        ],
        on="SprintID",
        how="left",
        suffixes=(
            "_WorkItem",
            "_Sprint",
        ),
    )
)


assert (
    story_validation_df[
        "ProjectID_WorkItem"
    ]
    ==
    story_validation_df[
        "ProjectID_Sprint"
    ]
).all(), (
    "User Story ProjectID does not match Sprint."
)


assert (
    story_validation_df[
        "TeamID_WorkItem"
    ]
    ==
    story_validation_df[
        "TeamID_Sprint"
    ]
).all(), (
    "User Story TeamID does not match Sprint."
)


# ============================================================
# TEMPORARY PART-1 EXPORT
# ============================================================

WORK_ITEMS_PART1_FILE = (
    config.RAW_DATA_DIR
    / "work_items_part1.csv"
)


work_items_part1_df.to_csv(
    WORK_ITEMS_PART1_FILE,
    index=False,
)


# ============================================================
# PART-1 SUMMARY
# ============================================================

print(
    f"\nEpics generated        : "
    f"{type_counts.get('Epic', 0):,}"
)


print(
    f"Features generated     : "
    f"{type_counts.get('Feature', 0):,}"
)


print(
    f"User Stories generated : "
    f"{type_counts.get('User Story', 0):,}"
)


print(
    f"Part-1 total           : "
    f"{len(work_items_part1_df):,}"
)


print(
    f"\nTemporary output:"
    f"\n{WORK_ITEMS_PART1_FILE}"
)


print(
    "\nWork Item Part-1 validation passed."
)
# ============================================================
# WORK ITEM GENERATION
# PART 2: TASKS + BUGS
# ============================================================

print("\n" + "=" * 70)
print("WORK ITEMS PART 2 - TASKS AND BUGS")
print("=" * 70)


# ============================================================
# TASK / BUG SETTINGS
# ============================================================

TASK_THEMES = [
    "Implement backend logic",
    "Create API integration",
    "Configure deployment pipeline",
    "Implement validation",
    "Create automated tests",
    "Update service configuration",
    "Implement database changes",
    "Improve monitoring",
    "Refactor application component",
    "Complete technical documentation",
]


BUG_THEMES = [
    "Authentication failure",
    "API response error",
    "Data validation defect",
    "Performance degradation",
    "Deployment failure",
    "UI workflow defect",
    "Integration failure",
    "Authorization issue",
    "Data synchronization defect",
    "Service reliability issue",
]


BUG_SEVERITIES = [
    "Critical",
    "High",
    "Medium",
    "Low",
]


# ============================================================
# PREPARE USER STORY LOOKUP
# ============================================================

stories_df = pd.DataFrame(
    story_records
).copy()


stories_df[
    "WorkItemID"
] = stories_df[
    "WorkItemID"
].astype("Int64")


stories_df[
    "SprintID"
] = stories_df[
    "SprintID"
].astype("Int64")


story_ids = stories_df[
    "WorkItemID"
].tolist()


story_lookup = (
    stories_df
    .set_index(
        "WorkItemID"
    )
)


# ============================================================
# SPRINT PERFORMANCE LOOKUP
# ============================================================

sprint_performance_lookup = (
    sprints_df
    .set_index(
        "SprintID"
    )[
        [
            "CompletionPercent",
            "CapacityUtilizationPercent",
            "SpilloverStoryPoints",
        ]
    ]
)


# ============================================================
# GENERATE 25,000 TASKS
# ============================================================

task_records = []


for task_number in range(
    1,
    config.TARGET_TASKS + 1,
):

    parent_story_id = int(
        story_ids[
            (
                task_number - 1
            )
            % len(story_ids)
        ]
    )


    parent_story = story_lookup.loc[
        parent_story_id
    ]


    sprint_id = int(
        parent_story[
            "SprintID"
        ]
    )


    sprint = sprints_df.loc[
        sprints_df[
            "SprintID"
        ]
        == sprint_id
    ].iloc[0]


    state = choose_work_item_state(
        sprint["EndDate"]
    )


    (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    ) = create_work_item_dates(
        state,
        sprint["StartDate"],
        sprint["EndDate"],
    )


    original_estimate_hours = random.choice(
        [
            2,
            4,
            6,
            8,
            12,
            16,
            20,
            24,
        ]
    )


    if state == "Closed":

        completed_work_hours = round(
            original_estimate_hours
            * random.uniform(
                0.85,
                1.20,
            ),
            1,
        )

        remaining_work_hours = 0.0


    elif state == "Resolved":

        completed_work_hours = round(
            original_estimate_hours
            * random.uniform(
                0.75,
                1.10,
            ),
            1,
        )

        remaining_work_hours = round(
            max(
                0,
                original_estimate_hours
                - completed_work_hours,
            ),
            1,
        )


    elif state == "Active":

        completed_work_hours = round(
            original_estimate_hours
            * random.uniform(
                0.20,
                0.75,
            ),
            1,
        )

        remaining_work_hours = round(
            max(
                0,
                original_estimate_hours
                - completed_work_hours,
            ),
            1,
        )


    else:

        completed_work_hours = 0.0

        remaining_work_hours = float(
            original_estimate_hours
        )


    task_records.append(
        {
            "WorkItemID":
                next_work_item_id,

            "ParentWorkItemID":
                parent_story_id,

            "WorkItemType":
                "Task",

            "ProjectID":
                int(
                    parent_story[
                        "ProjectID"
                    ]
                ),

            "TeamID":
                int(
                    parent_story[
                        "TeamID"
                    ]
                ),

            "SprintID":
                sprint_id,

            "Title":
                (
                    f"{random.choice(TASK_THEMES)} "
                    f"{task_number:05d}"
                ),

            "State":
                state,

            "Priority":
                random.choices(
                    PRIORITIES,
                    weights=[
                        3,
                        25,
                        55,
                        17,
                    ],
                    k=1,
                )[0],

            "StoryPoints":
                pd.NA,

            "Severity":
                pd.NA,

            "CreatedDate":
                created_date.date(),

            "ActivatedDate":
                (
                    activated_date.date()
                    if pd.notna(
                        activated_date
                    )
                    else pd.NaT
                ),

            "ResolvedDate":
                (
                    resolved_date.date()
                    if pd.notna(
                        resolved_date
                    )
                    else pd.NaT
                ),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),

            "OriginalEstimateHours":
                original_estimate_hours,

            "CompletedWorkHours":
                completed_work_hours,

            "RemainingWorkHours":
                remaining_work_hours,

            "DefectSource":
                pd.NA,
        }
    )


    next_work_item_id += 1


# ============================================================
# BUG WEIGHTING
# ============================================================
#
# Bugs are not distributed completely randomly.
#
# Sprints with:
# - lower completion
# - lower capacity
# - higher spillover
#
# receive a higher probability of defect generation.
#
# This creates meaningful relationships for later Power BI
# root-cause analysis.
# ============================================================

story_bug_weights = []


for story_id in story_ids:

    story = story_lookup.loc[
        story_id
    ]

    sprint_id = int(
        story[
            "SprintID"
        ]
    )

    sprint_metrics = (
        sprint_performance_lookup
        .loc[
            sprint_id
        ]
    )


    completion_percent = float(
        sprint_metrics[
            "CompletionPercent"
        ]
    )


    capacity_percent = float(
        sprint_metrics[
            "CapacityUtilizationPercent"
        ]
    )


    spillover_points = float(
        sprint_metrics[
            "SpilloverStoryPoints"
        ]
    )


    weight = 1.0


    if completion_percent < 80:
        weight += 2.0

    elif completion_percent < 90:
        weight += 1.0


    if capacity_percent < 75:
        weight += 1.5

    elif capacity_percent < 85:
        weight += 0.75


    if spillover_points >= 10:
        weight += 1.5

    elif spillover_points >= 5:
        weight += 0.75


    story_bug_weights.append(
        weight
    )


# ============================================================
# GENERATE 8,000 BUGS
# ============================================================

bug_records = []


for bug_number in range(
    1,
    config.TARGET_BUGS + 1,
):

    parent_story_id = int(
        random.choices(
            population=story_ids,
            weights=story_bug_weights,
            k=1,
        )[0]
    )


    parent_story = story_lookup.loc[
        parent_story_id
    ]


    sprint_id = int(
        parent_story[
            "SprintID"
        ]
    )


    sprint = sprints_df.loc[
        sprints_df[
            "SprintID"
        ]
        == sprint_id
    ].iloc[0]


    severity = random.choices(
        population=BUG_SEVERITIES,
        weights=[
            5,
            20,
            50,
            25,
        ],
        k=1,
    )[0]


    # Critical and High defects are more likely
    # to receive higher priority.
    if severity == "Critical":

        priority = random.choices(
            population=[
                "Critical",
                "High",
            ],
            weights=[
                80,
                20,
            ],
            k=1,
        )[0]


    elif severity == "High":

        priority = random.choices(
            population=[
                "Critical",
                "High",
                "Medium",
            ],
            weights=[
                10,
                70,
                20,
            ],
            k=1,
        )[0]


    elif severity == "Medium":

        priority = random.choices(
            population=[
                "High",
                "Medium",
                "Low",
            ],
            weights=[
                20,
                65,
                15,
            ],
            k=1,
        )[0]


    else:

        priority = random.choices(
            population=[
                "Medium",
                "Low",
            ],
            weights=[
                40,
                60,
            ],
            k=1,
        )[0]


    state = choose_work_item_state(
        sprint["EndDate"]
    )


    (
        created_date,
        activated_date,
        resolved_date,
        closed_date,
    ) = create_work_item_dates(
        state,
        sprint["StartDate"],
        sprint["EndDate"],
    )


    defect_source = random.choices(
        population=[
            "Development",
            "Integration Testing",
            "System Testing",
            "Regression Testing",
            "Production",
        ],
        weights=[
            20,
            20,
            25,
            20,
            15,
        ],
        k=1,
    )[0]


    bug_records.append(
        {
            "WorkItemID":
                next_work_item_id,

            "ParentWorkItemID":
                parent_story_id,

            "WorkItemType":
                "Bug",

            "ProjectID":
                int(
                    parent_story[
                        "ProjectID"
                    ]
                ),

            "TeamID":
                int(
                    parent_story[
                        "TeamID"
                    ]
                ),

            "SprintID":
                sprint_id,

            "Title":
                (
                    f"{random.choice(BUG_THEMES)} "
                    f"{bug_number:05d}"
                ),

            "State":
                state,

            "Priority":
                priority,

            "StoryPoints":
                pd.NA,

            "Severity":
                severity,

            "CreatedDate":
                created_date.date(),

            "ActivatedDate":
                (
                    activated_date.date()
                    if pd.notna(
                        activated_date
                    )
                    else pd.NaT
                ),

            "ResolvedDate":
                (
                    resolved_date.date()
                    if pd.notna(
                        resolved_date
                    )
                    else pd.NaT
                ),

            "ClosedDate":
                (
                    closed_date.date()
                    if pd.notna(
                        closed_date
                    )
                    else pd.NaT
                ),

            "OriginalEstimateHours":
                pd.NA,

            "CompletedWorkHours":
                pd.NA,

            "RemainingWorkHours":
                pd.NA,

            "DefectSource":
                defect_source,
        }
    )


    next_work_item_id += 1


# ============================================================
# NORMALIZE PART-1 COLUMNS
# ============================================================
#
# Part 1 did not need Task-specific columns.
# Add them before combining all work items.
# ============================================================

for column_name in [
    "OriginalEstimateHours",
    "CompletedWorkHours",
    "RemainingWorkHours",
    "DefectSource",
]:

    if column_name not in work_items_part1_df.columns:

        work_items_part1_df[
            column_name
        ] = pd.NA


# ============================================================
# CREATE TASK / BUG DATAFRAMES
# ============================================================

tasks_df = pd.DataFrame(
    task_records
)


bugs_df = pd.DataFrame(
    bug_records
)


# ============================================================
# COMBINE ALL 42,250 WORK ITEMS
# ============================================================

work_items_df = pd.concat(
    [
        work_items_part1_df,
        tasks_df,
        bugs_df,
    ],
    ignore_index=True,
)


# ============================================================
# NORMALIZE DATA TYPES
# ============================================================

for column_name in [
    "WorkItemID",
    "ParentWorkItemID",
    "SprintID",
    "StoryPoints",
]:

    work_items_df[
        column_name
    ] = work_items_df[
        column_name
    ].astype(
        "Int64"
    )


# ============================================================
# FINAL WORK ITEM VALIDATION
# ============================================================

expected_total = (
    config.TARGET_EPICS
    + config.TARGET_FEATURES
    + config.TARGET_USER_STORIES
    + config.TARGET_TASKS
    + config.TARGET_BUGS
)


assert len(
    work_items_df
) == expected_total, (
    "Incorrect total work item count."
)


assert work_items_df[
    "WorkItemID"
].is_unique, (
    "Duplicate WorkItemID detected."
)


final_type_counts = (
    work_items_df[
        "WorkItemType"
    ]
    .value_counts()
)


assert (
    final_type_counts.get(
        "Epic",
        0,
    )
    == config.TARGET_EPICS
)


assert (
    final_type_counts.get(
        "Feature",
        0,
    )
    == config.TARGET_FEATURES
)


assert (
    final_type_counts.get(
        "User Story",
        0,
    )
    == config.TARGET_USER_STORIES
)


assert (
    final_type_counts.get(
        "Task",
        0,
    )
    == config.TARGET_TASKS
)


assert (
    final_type_counts.get(
        "Bug",
        0,
    )
    == config.TARGET_BUGS
)


# ============================================================
# VALIDATE TASK / BUG PARENTS
# ============================================================

valid_story_ids = set(
    work_items_df.loc[
        work_items_df[
            "WorkItemType"
        ]
        == "User Story",
        "WorkItemID",
    ]
)


task_parent_ids = set(
    work_items_df.loc[
        work_items_df[
            "WorkItemType"
        ]
        == "Task",
        "ParentWorkItemID",
    ]
)


bug_parent_ids = set(
    work_items_df.loc[
        work_items_df[
            "WorkItemType"
        ]
        == "Bug",
        "ParentWorkItemID",
    ]
)


assert task_parent_ids.issubset(
    valid_story_ids
), (
    "Task contains an invalid User Story parent."
)


assert bug_parent_ids.issubset(
    valid_story_ids
), (
    "Bug contains an invalid User Story parent."
)


# ============================================================
# VALIDATE PROJECT / TEAM / SPRINT INHERITANCE
# ============================================================

child_validation_df = (
    work_items_df[
        work_items_df[
            "WorkItemType"
        ].isin(
            [
                "Task",
                "Bug",
            ]
        )
    ]
    .merge(
        stories_df[
            [
                "WorkItemID",
                "ProjectID",
                "TeamID",
                "SprintID",
            ]
        ],
        left_on="ParentWorkItemID",
        right_on="WorkItemID",
        how="left",
        suffixes=(
            "_Child",
            "_Parent",
        ),
    )
)


assert (
    child_validation_df[
        "ProjectID_Child"
    ]
    ==
    child_validation_df[
        "ProjectID_Parent"
    ]
).all(), (
    "Task/Bug ProjectID does not match parent Story."
)


assert (
    child_validation_df[
        "TeamID_Child"
    ]
    ==
    child_validation_df[
        "TeamID_Parent"
    ]
).all(), (
    "Task/Bug TeamID does not match parent Story."
)


assert (
    child_validation_df[
        "SprintID_Child"
    ]
    ==
    child_validation_df[
        "SprintID_Parent"
    ]
).all(), (
    "Task/Bug SprintID does not match parent Story."
)


# ============================================================
# VALIDATE SEVERITY
# ============================================================

non_bug_severity = work_items_df.loc[
    work_items_df[
        "WorkItemType"
    ]
    != "Bug",
    "Severity",
]


assert non_bug_severity.isna().all(), (
    "Non-Bug work item contains Severity."
)


assert work_items_df.loc[
    work_items_df[
        "WorkItemType"
    ]
    == "Bug",
    "Severity",
].notna().all(), (
    "Bug contains missing Severity."
)


# ============================================================
# VALIDATE TASK HOURS
# ============================================================

task_validation_df = work_items_df[
    work_items_df[
        "WorkItemType"
    ]
    == "Task"
]


assert task_validation_df[
    "OriginalEstimateHours"
].notna().all(), (
    "Task contains missing estimate hours."
)


assert (
    task_validation_df[
        "OriginalEstimateHours"
    ]
    > 0
).all(), (
    "Task contains invalid estimate hours."
)


assert (
    task_validation_df[
        "RemainingWorkHours"
    ]
    >= 0
).all(), (
    "Task contains negative remaining work."
)


# ============================================================
# FINAL EXPORT
# ============================================================

WORK_ITEMS_FILE = (
    config.RAW_DATA_DIR
    / "work_items.csv"
)


work_items_df.to_csv(
    WORK_ITEMS_FILE,
    index=False,
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL WORK ITEM SUMMARY")
print("=" * 70)


print(
    f"\nEpics        : "
    f"{final_type_counts.get('Epic', 0):,}"
)


print(
    f"Features     : "
    f"{final_type_counts.get('Feature', 0):,}"
)


print(
    f"User Stories : "
    f"{final_type_counts.get('User Story', 0):,}"
)


print(
    f"Tasks        : "
    f"{final_type_counts.get('Task', 0):,}"
)


print(
    f"Bugs         : "
    f"{final_type_counts.get('Bug', 0):,}"
)


print(
    f"\nTOTAL        : "
    f"{len(work_items_df):,}"
)


print(
    "\nBug Severity Distribution:"
)


print(
    bugs_df[
        "Severity"
    ].value_counts()
)


print(
    f"\nFinal output:"
    f"\n{WORK_ITEMS_FILE}"
)


print(
    "\nFull work-item hierarchy validation passed."
)


print(
    "work_items.csv generated successfully!"
)
# ============================================================
# RELEASE MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("DELIVERY DATA GENERATION - RELEASES")
print("=" * 70)


# ============================================================
# LOAD PRODUCT DATA
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

assert products_df[
    "ProductID"
].is_unique, (
    "Duplicate ProductID detected."
)


# ============================================================
# PRODUCT LOOKUP BY PROJECT
# ============================================================

product_by_project = (
    products_df
    .set_index("ProjectID")[
        "ProductID"
    ]
    .to_dict()
)


# ============================================================
# PROJECT DELIVERY PERFORMANCE
# ============================================================

project_delivery_metrics = (
    sprints_df
    .groupby("ProjectID")
    .agg(
        AverageCompletionPercent=(
            "CompletionPercent",
            "mean",
        ),
        AverageCapacityPercent=(
            "CapacityUtilizationPercent",
            "mean",
        ),
        TotalCommittedStoryPoints=(
            "CommittedStoryPoints",
            "sum",
        ),
        TotalCompletedStoryPoints=(
            "CompletedStoryPoints",
            "sum",
        ),
        TotalSpilloverStoryPoints=(
            "SpilloverStoryPoints",
            "sum",
        ),
    )
    .reset_index()
)


project_delivery_lookup = (
    project_delivery_metrics
    .set_index("ProjectID")
)


# ============================================================
# BUG METRICS BY PROJECT
# ============================================================

bugs_only_df = work_items_df[
    work_items_df[
        "WorkItemType"
    ]
    == "Bug"
].copy()


project_bug_metrics = (
    bugs_only_df
    .groupby("ProjectID")
    .agg(
        TotalBugCount=(
            "WorkItemID",
            "count",
        ),
        OpenBugCount=(
            "State",
            lambda values: (
                ~values.isin(
                    [
                        "Resolved",
                        "Closed",
                    ]
                )
            ).sum(),
        ),
        CriticalBugCount=(
            "Severity",
            lambda values: (
                values
                == "Critical"
            ).sum(),
        ),
    )
)


# ============================================================
# RELEASE SETTINGS
# ============================================================

RELEASE_TYPES = [
    "Major",
    "Minor",
    "Patch",
    "Platform",
]


# ============================================================
# GENERATE 150 RELEASES
# ============================================================

releases = []


for release_id in range(
    1,
    config.TARGET_RELEASES + 1,
):

    # 150 releases / 50 projects =
    # exactly 3 releases per project.
    project_id = (
        (
            release_id - 1
        )
        % config.NUM_PROJECTS
    ) + 1


    project = projects_df.loc[
        projects_df[
            "ProjectID"
        ]
        == project_id
    ].iloc[0]


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


    release_number = (
        (
            release_id - 1
        )
        // config.NUM_PROJECTS
    ) + 1


    # --------------------------------------------------------
    # RELEASE PLANNED DATE
    # --------------------------------------------------------

    project_duration_days = max(
        1,
        (
            project_end
            - project_start
        ).days,
    )


    release_fraction = (
        release_number
        / 4
    )


    planned_release_date = (
        project_start
        + pd.Timedelta(
            days=round(
                project_duration_days
                * release_fraction
            )
        )
    )


    # Keep dates within the synthetic
    # enterprise data period.
    planned_release_date = min(
        planned_release_date,
        pd.Timestamp(
            config.DATA_END_DATE
        ),
    )


    # --------------------------------------------------------
    # DELIVERY PERFORMANCE
    # --------------------------------------------------------

    delivery = (
        project_delivery_lookup
        .loc[
            project_id
        ]
    )


    avg_completion = float(
        delivery[
            "AverageCompletionPercent"
        ]
    )

    avg_capacity = float(
        delivery[
            "AverageCapacityPercent"
        ]
    )

    spillover = int(
        delivery[
            "TotalSpilloverStoryPoints"
        ]
    )


    # --------------------------------------------------------
    # RELEASE DELAY RISK SCORE
    # --------------------------------------------------------

    delay_risk_score = 0


    if avg_completion < 80:
        delay_risk_score += 3

    elif avg_completion < 90:
        delay_risk_score += 2

    elif avg_completion < 95:
        delay_risk_score += 1


    if avg_capacity < 75:
        delay_risk_score += 3

    elif avg_capacity < 85:
        delay_risk_score += 2

    elif avg_capacity < 95:
        delay_risk_score += 1


    if spillover >= 75:
        delay_risk_score += 3

    elif spillover >= 40:
        delay_risk_score += 2

    elif spillover >= 20:
        delay_risk_score += 1


    # --------------------------------------------------------
    # DETERMINE DELAY
    # --------------------------------------------------------

    if delay_risk_score >= 7:

        delay_days = random.randint(
            15,
            45,
        )


    elif delay_risk_score >= 5:

        delay_days = random.randint(
            7,
            25,
        )


    elif delay_risk_score >= 3:

        delay_days = random.randint(
            0,
            14,
        )


    else:

        delay_days = random.randint(
            0,
            5,
        )


    forecast_release_date = (
        planned_release_date
        + pd.Timedelta(
            days=delay_days
        )
    )


    # --------------------------------------------------------
    # DETERMINE RELEASE STATUS
    # --------------------------------------------------------

    data_end_date = pd.Timestamp(
        config.DATA_END_DATE
    )


    if forecast_release_date <= data_end_date:

        if delay_days >= 10:

            release_status = "Delayed"

        else:

            release_status = "Released"


        actual_release_date = (
            forecast_release_date
        )


    else:

        actual_release_date = pd.NaT


        days_until_release = (
            forecast_release_date
            - data_end_date
        ).days


        if days_until_release <= 14:

            release_status = (
                "Ready for Release"
            )


        elif days_until_release <= 45:

            release_status = "Testing"


        else:

            release_status = (
                "In Development"
            )


    # --------------------------------------------------------
    # READINESS
    # --------------------------------------------------------

    readiness_percent = round(
        np.clip(
            (
                avg_completion
                * 0.65
            )
            +
            (
                avg_capacity
                * 0.25
            )
            +
            random.uniform(
                -5,
                5,
            ),
            40,
            100,
        ),
        1,
    )


    if release_status == "Released":

        readiness_percent = 100.0


    # --------------------------------------------------------
    # RELEASE STORY POINTS
    # --------------------------------------------------------

    planned_story_points = max(
        20,
        round(
            int(
                delivery[
                    "TotalCommittedStoryPoints"
                ]
            )
            / 3
        ),
    )


    completion_ratio = float(
        np.clip(
            avg_completion
            / 100,
            0,
            1,
        )
    )


    completed_story_points = round(
        planned_story_points
        * completion_ratio
    )


    completed_story_points = min(
        completed_story_points,
        planned_story_points,
    )


    # --------------------------------------------------------
    # BUG METRICS
    # --------------------------------------------------------

    if project_id in (
        project_bug_metrics.index
    ):

        project_bug_data = (
            project_bug_metrics
            .loc[
                project_id
            ]
        )


        project_open_bugs = int(
            project_bug_data[
                "OpenBugCount"
            ]
        )


        project_critical_bugs = int(
            project_bug_data[
                "CriticalBugCount"
            ]
        )


    else:

        project_open_bugs = 0
        project_critical_bugs = 0


    # Allocate approximate project bug
    # burden across three releases.
    open_bug_count = max(
        0,
        round(
            project_open_bugs
            / 3
            * random.uniform(
                0.70,
                1.30,
            )
        ),
    )


    critical_bug_count = min(
        open_bug_count,
        max(
            0,
            round(
                project_critical_bugs
                / 3
                * random.uniform(
                    0.70,
                    1.30,
                )
            ),
        ),
    )


    # --------------------------------------------------------
    # GO-LIVE DECISION
    # --------------------------------------------------------

    if (
        critical_bug_count >= 3
        or readiness_percent < 70
    ):

        go_live_decision = "No-Go"


    elif (
        critical_bug_count >= 1
        or readiness_percent < 90
    ):

        go_live_decision = (
            "Conditional Go"
        )


    else:

        go_live_decision = "Go"


    # --------------------------------------------------------
    # PRODUCT RELATIONSHIP
    # --------------------------------------------------------

    product_id = (
        product_by_project.get(
            project_id,
            pd.NA,
        )
    )


    # --------------------------------------------------------
    # RELEASE RECORD
    # --------------------------------------------------------

    releases.append(
        {
            "ReleaseID":
                release_id,

            "ProjectID":
                project_id,

            "ProductID":
                product_id,

            "ReleaseName":
                (
                    f"P{project_id:03d}"
                    f"-Release-"
                    f"{release_number}"
                ),

            "ReleaseType":
                random.choices(
                    RELEASE_TYPES,
                    weights=[
                        20,
                        45,
                        25,
                        10,
                    ],
                    k=1,
                )[0],

            "PlannedReleaseDate":
                planned_release_date.date(),

            "ForecastReleaseDate":
                forecast_release_date.date(),

            "ActualReleaseDate":
                (
                    actual_release_date.date()
                    if pd.notna(
                        actual_release_date
                    )
                    else pd.NaT
                ),

            "ReleaseStatus":
                release_status,

            "DelayDays":
                delay_days,

            "ReadinessPercent":
                readiness_percent,

            "PlannedStoryPoints":
                planned_story_points,

            "CompletedStoryPoints":
                completed_story_points,

            "OpenBugCount":
                open_bug_count,

            "CriticalBugCount":
                critical_bug_count,

            "GoLiveDecision":
                go_live_decision,
        }
    )


# ============================================================
# CREATE RELEASE DATAFRAME
# ============================================================

releases_df = pd.DataFrame(
    releases
)


releases_df[
    "ProductID"
] = releases_df[
    "ProductID"
].astype(
    "Int64"
)


# ============================================================
# RELEASE VALIDATION
# ============================================================

assert len(
    releases_df
) == config.TARGET_RELEASES, (
    "Incorrect release count."
)


assert releases_df[
    "ReleaseID"
].is_unique, (
    "Duplicate ReleaseID detected."
)


assert releases_df[
    "ProjectID"
].isin(
    projects_df[
        "ProjectID"
    ]
).all(), (
    "Invalid ProjectID found in releases."
)


valid_product_ids = set(
    products_df[
        "ProductID"
    ]
)


release_product_ids = set(
    releases_df[
        "ProductID"
    ]
    .dropna()
)


assert release_product_ids.issubset(
    valid_product_ids
), (
    "Invalid ProductID found in releases."
)


# Validate Product -> Project mapping.
product_project_lookup = (
    products_df
    .set_index(
        "ProductID"
    )[
        "ProjectID"
    ]
    .to_dict()
)


for _, release in (
    releases_df[
        releases_df[
            "ProductID"
        ].notna()
    ]
    .iterrows()
):

    assert (
        product_project_lookup[
            int(
                release[
                    "ProductID"
                ]
            )
        ]
        ==
        int(
            release[
                "ProjectID"
            ]
        )
    ), (
        "Release ProductID does not "
        "match its ProjectID."
    )


release_dates_df = (
    releases_df.copy()
)


release_dates_df[
    "PlannedReleaseDate"
] = pd.to_datetime(
    release_dates_df[
        "PlannedReleaseDate"
    ]
)


release_dates_df[
    "ForecastReleaseDate"
] = pd.to_datetime(
    release_dates_df[
        "ForecastReleaseDate"
    ]
)


release_dates_df[
    "ActualReleaseDate"
] = pd.to_datetime(
    release_dates_df[
        "ActualReleaseDate"
    ]
)


assert (
    release_dates_df[
        "ForecastReleaseDate"
    ]
    >=
    release_dates_df[
        "PlannedReleaseDate"
    ]
).all(), (
    "Forecast release date occurs "
    "before planned release date."
)


actual_release_rows = (
    release_dates_df[
        release_dates_df[
            "ActualReleaseDate"
        ].notna()
    ]
)


assert (
    actual_release_rows[
        "ActualReleaseDate"
    ]
    >=
    actual_release_rows[
        "PlannedReleaseDate"
    ]
).all(), (
    "Actual release date occurs "
    "before planned release date."
)


assert (
    releases_df[
        "CompletedStoryPoints"
    ]
    <=
    releases_df[
        "PlannedStoryPoints"
    ]
).all(), (
    "Release completed story points "
    "exceed planned story points."
)


assert (
    releases_df[
        "CriticalBugCount"
    ]
    <=
    releases_df[
        "OpenBugCount"
    ]
).all(), (
    "Critical bug count exceeds "
    "open bug count."
)


assert releases_df[
    "ReadinessPercent"
].between(
    0,
    100,
).all(), (
    "Invalid release readiness percentage."
)


# Every project should have exactly
# three releases.
release_project_counts = (
    releases_df[
        "ProjectID"
    ]
    .value_counts()
)


assert (
    release_project_counts
    == 3
).all(), (
    "Every project should have "
    "exactly three releases."
)


# ============================================================
# EXPORT RELEASES
# ============================================================

RELEASES_FILE = (
    config.RAW_DATA_DIR
    / "releases.csv"
)


releases_df.to_csv(
    RELEASES_FILE,
    index=False,
)


# ============================================================
# RELEASE SUMMARY
# ============================================================

print(
    f"\nReleases generated    : "
    f"{len(releases_df):,}"
)


print(
    f"Projects represented  : "
    f"{releases_df['ProjectID'].nunique()}"
)


print(
    f"Product-linked        : "
    f"{releases_df['ProductID'].notna().sum():,}"
)


print(
    f"Average readiness     : "
    f"{releases_df['ReadinessPercent'].mean():.2f}%"
)


print(
    f"Average delay         : "
    f"{releases_df['DelayDays'].mean():.2f} days"
)


print(
    "\nRelease Status Distribution:"
)


print(
    releases_df[
        "ReleaseStatus"
    ].value_counts()
)


print(
    "\nGo-Live Decision Distribution:"
)


print(
    releases_df[
        "GoLiveDecision"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{RELEASES_FILE}"
)


print(
    "\nRelease validation passed."
)


print(
    "releases.csv generated successfully!"
)
# ============================================================
# DEPENDENCY MANAGEMENT DATA
# ============================================================

print("\n" + "=" * 70)
print("DELIVERY DATA GENERATION - DEPENDENCIES")
print("=" * 70)


# ============================================================
# DEPENDENCY SETTINGS
# ============================================================

DEPENDENCY_TYPES = [
    "Technical",
    "API",
    "Data",
    "Infrastructure",
    "Security",
    "Release",
    "Resource",
    "Vendor",
]


DEPENDENCY_STATUSES = [
    "Open",
    "In Progress",
    "Resolved",
    "Blocked",
]


DEPENDENCY_DESCRIPTIONS = [
    "API contract required before integration",
    "Shared platform capability required",
    "Infrastructure provisioning dependency",
    "Security approval required",
    "Data migration prerequisite",
    "Release sequencing dependency",
    "Architecture decision required",
    "Shared engineering resource required",
    "Service integration dependency",
    "Environment readiness dependency",
]


# ============================================================
# PROJECT -> TEAM LOOKUP
# ============================================================

primary_project_teams_df = (
    project_team_df[
        project_team_df[
            "PrimaryTeamFlag"
        ]
        == True
    ]
    .copy()
)


# Handle CSVs where Boolean values may
# have been read as strings.
if primary_project_teams_df.empty:

    primary_project_teams_df = (
        project_team_df[
            project_team_df[
                "PrimaryTeamFlag"
            ]
            .astype(str)
            .str.lower()
            == "true"
        ]
        .copy()
    )


project_primary_team = (
    primary_project_teams_df
    .drop_duplicates(
        subset=[
            "ProjectID",
        ]
    )
    .set_index(
        "ProjectID"
    )[
        "TeamID"
    ]
    .to_dict()
)


# Fallback for any project without an
# explicitly marked primary team.
for project_id in projects_df[
    "ProjectID"
]:

    if project_id not in project_primary_team:

        matching_assignment = (
            project_team_df[
                project_team_df[
                    "ProjectID"
                ]
                == project_id
            ]
        )

        if matching_assignment.empty:

            raise ValueError(
                f"No team assignment found "
                f"for ProjectID {project_id}."
            )

        project_primary_team[
            project_id
        ] = int(
            matching_assignment.iloc[0][
                "TeamID"
            ]
        )


# ============================================================
# RELEASE IMPACT LOOKUP
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
# GENERATE 500 DEPENDENCIES
# ============================================================

dependencies = []


project_id_list = (
    projects_df[
        "ProjectID"
    ]
    .astype(int)
    .tolist()
)


for dependency_id in range(
    1,
    config.TARGET_DEPENDENCIES + 1,
):

    # --------------------------------------------------------
    # DEPENDENT PROJECT
    # --------------------------------------------------------

    dependent_project_id = random.choice(
        project_id_list
    )


    # --------------------------------------------------------
    # BLOCKING / PROVIDING PROJECT
    # --------------------------------------------------------

    possible_provider_projects = [
        project_id
        for project_id
        in project_id_list
        if project_id
        != dependent_project_id
    ]


    provider_project_id = random.choice(
        possible_provider_projects
    )


    dependent_team_id = int(
        project_primary_team[
            dependent_project_id
        ]
    )


    provider_team_id = int(
        project_primary_team[
            provider_project_id
        ]
    )


    # --------------------------------------------------------
    # DEPENDENCY DATES
    # --------------------------------------------------------

    dependent_project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == dependent_project_id
        ]
        .iloc[0]
    )


    provider_project = (
        projects_df[
            projects_df[
                "ProjectID"
            ]
            == provider_project_id
        ]
        .iloc[0]
    )


    dependent_start = pd.Timestamp(
        dependent_project[
            "StartDate"
        ]
    )


    dependent_end = pd.Timestamp(
        dependent_project[
            "PlannedEndDate"
        ]
    )


    provider_start = pd.Timestamp(
        provider_project[
            "StartDate"
        ]
    )


    provider_end = pd.Timestamp(
        provider_project[
            "PlannedEndDate"
        ]
    )


    overlap_start = max(
        dependent_start,
        provider_start,
    )


    overlap_end = min(
        dependent_end,
        provider_end,
    )


    # If projects do not overlap, use the
    # dependent project's valid date range.
    if overlap_start > overlap_end:

        overlap_start = (
            dependent_start
        )

        overlap_end = (
            dependent_end
        )


    available_days = max(
        1,
        (
            overlap_end
            - overlap_start
        ).days,
    )


    created_offset = random.randint(
        0,
        max(
            0,
            available_days // 2,
        ),
    )


    created_date = (
        overlap_start
        + pd.Timedelta(
            days=created_offset
        )
    )


    remaining_days = max(
        1,
        (
            overlap_end
            - created_date
        ).days,
    )


    planned_resolution_offset = (
        random.randint(
            1,
            remaining_days,
        )
    )


    planned_resolution_date = (
        created_date
        + pd.Timedelta(
            days=planned_resolution_offset
        )
    )


    # --------------------------------------------------------
    # DEPENDENCY RISK
    # --------------------------------------------------------

    dependent_release = (
        project_release_metrics
        .loc[
            dependent_project_id
        ]
    )


    provider_release = (
        project_release_metrics
        .loc[
            provider_project_id
        ]
    )


    combined_delay = (
        float(
            dependent_release[
                "AverageReleaseDelay"
            ]
        )
        +
        float(
            provider_release[
                "AverageReleaseDelay"
            ]
        )
    ) / 2


    combined_readiness = (
        float(
            dependent_release[
                "AverageReadiness"
            ]
        )
        +
        float(
            provider_release[
                "AverageReadiness"
            ]
        )
    ) / 2


    risk_score = 0


    if combined_delay >= 15:
        risk_score += 3

    elif combined_delay >= 7:
        risk_score += 2

    elif combined_delay > 0:
        risk_score += 1


    if combined_readiness < 70:
        risk_score += 3

    elif combined_readiness < 85:
        risk_score += 2

    elif combined_readiness < 95:
        risk_score += 1


    # --------------------------------------------------------
    # CRITICALITY
    # --------------------------------------------------------

    if risk_score >= 5:

        criticality = random.choices(
            [
                "Critical",
                "High",
            ],
            weights=[
                45,
                55,
            ],
            k=1,
        )[0]


    elif risk_score >= 3:

        criticality = random.choices(
            [
                "High",
                "Medium",
            ],
            weights=[
                45,
                55,
            ],
            k=1,
        )[0]


    else:

        criticality = random.choices(
            [
                "Medium",
                "Low",
            ],
            weights=[
                55,
                45,
            ],
            k=1,
        )[0]


    # --------------------------------------------------------
    # DELAY
    # --------------------------------------------------------

    if criticality == "Critical":

        delay_days = random.randint(
            10,
            40,
        )


    elif criticality == "High":

        delay_days = random.randint(
            5,
            25,
        )


    elif criticality == "Medium":

        delay_days = random.randint(
            0,
            12,
        )


    else:

        delay_days = random.randint(
            0,
            5,
        )


    forecast_resolution_date = (
        planned_resolution_date
        + pd.Timedelta(
            days=delay_days
        )
    )


    # --------------------------------------------------------
    # STATUS / ACTUAL RESOLUTION
    # --------------------------------------------------------

    data_end_date = pd.Timestamp(
        config.DATA_END_DATE
    )


    if (
        forecast_resolution_date
        <= data_end_date
    ):

        if (
            criticality
            in [
                "Critical",
                "High",
            ]
            and delay_days >= 15
            and random.random() < 0.25
        ):

            dependency_status = (
                "Blocked"
            )

            actual_resolution_date = (
                pd.NaT
            )


        else:

            dependency_status = (
                "Resolved"
            )

            actual_resolution_date = (
                forecast_resolution_date
            )


    else:

        actual_resolution_date = (
            pd.NaT
        )


        if (
            criticality
            in [
                "Critical",
                "High",
            ]
            and random.random() < 0.35
        ):

            dependency_status = (
                "Blocked"
            )


        elif created_date <= data_end_date:

            dependency_status = (
                "In Progress"
            )


        else:

            dependency_status = "Open"


    # --------------------------------------------------------
    # RELEASE IMPACT
    # --------------------------------------------------------

    if (
        criticality == "Critical"
        or delay_days >= 20
    ):

        release_impact = "High"


    elif (
        criticality == "High"
        or delay_days >= 10
    ):

        release_impact = "Medium"


    else:

        release_impact = "Low"


    # --------------------------------------------------------
    # RECORD
    # --------------------------------------------------------

    dependencies.append(
        {
            "DependencyID":
                dependency_id,

            "DependentProjectID":
                dependent_project_id,

            "ProviderProjectID":
                provider_project_id,

            "DependentTeamID":
                dependent_team_id,

            "ProviderTeamID":
                provider_team_id,

            "DependencyType":
                random.choice(
                    DEPENDENCY_TYPES
                ),

            "Description":
                random.choice(
                    DEPENDENCY_DESCRIPTIONS
                ),

            "Criticality":
                criticality,

            "DependencyStatus":
                dependency_status,

            "CreatedDate":
                created_date.date(),

            "PlannedResolutionDate":
                planned_resolution_date.date(),

            "ForecastResolutionDate":
                forecast_resolution_date.date(),

            "ActualResolutionDate":
                (
                    actual_resolution_date.date()
                    if pd.notna(
                        actual_resolution_date
                    )
                    else pd.NaT
                ),

            "DelayDays":
                delay_days,

            "ReleaseImpact":
                release_impact,
        }
    )


# ============================================================
# CREATE DEPENDENCY DATAFRAME
# ============================================================

dependencies_df = pd.DataFrame(
    dependencies
)


# ============================================================
# DEPENDENCY VALIDATION
# ============================================================

assert len(
    dependencies_df
) == config.TARGET_DEPENDENCIES, (
    "Incorrect dependency count."
)


assert dependencies_df[
    "DependencyID"
].is_unique, (
    "Duplicate DependencyID detected."
)


valid_project_ids = set(
    projects_df[
        "ProjectID"
    ]
)


assert set(
    dependencies_df[
        "DependentProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid dependent ProjectID."
)


assert set(
    dependencies_df[
        "ProviderProjectID"
    ]
).issubset(
    valid_project_ids
), (
    "Invalid provider ProjectID."
)


assert (
    dependencies_df[
        "DependentProjectID"
    ]
    !=
    dependencies_df[
        "ProviderProjectID"
    ]
).all(), (
    "A project cannot depend on itself."
)


valid_team_ids = set(
    teams_df[
        "TeamID"
    ]
)


assert set(
    dependencies_df[
        "DependentTeamID"
    ]
).issubset(
    valid_team_ids
), (
    "Invalid dependent TeamID."
)


assert set(
    dependencies_df[
        "ProviderTeamID"
    ]
).issubset(
    valid_team_ids
), (
    "Invalid provider TeamID."
)


dependency_dates_df = (
    dependencies_df.copy()
)


for date_column in [
    "CreatedDate",
    "PlannedResolutionDate",
    "ForecastResolutionDate",
    "ActualResolutionDate",
]:

    dependency_dates_df[
        date_column
    ] = pd.to_datetime(
        dependency_dates_df[
            date_column
        ]
    )


assert (
    dependency_dates_df[
        "PlannedResolutionDate"
    ]
    >=
    dependency_dates_df[
        "CreatedDate"
    ]
).all(), (
    "Planned resolution occurs "
    "before dependency creation."
)


assert (
    dependency_dates_df[
        "ForecastResolutionDate"
    ]
    >=
    dependency_dates_df[
        "PlannedResolutionDate"
    ]
).all(), (
    "Forecast resolution occurs "
    "before planned resolution."
)


resolved_dependencies = (
    dependency_dates_df[
        dependency_dates_df[
            "ActualResolutionDate"
        ].notna()
    ]
)


assert (
    resolved_dependencies[
        "ActualResolutionDate"
    ]
    >=
    resolved_dependencies[
        "CreatedDate"
    ]
).all(), (
    "Actual resolution occurs "
    "before dependency creation."
)


assert (
    dependencies_df[
        "DelayDays"
    ]
    >= 0
).all(), (
    "Negative dependency delay detected."
)


# ============================================================
# EXPORT DEPENDENCIES
# ============================================================

DEPENDENCIES_FILE = (
    config.RAW_DATA_DIR
    / "dependencies.csv"
)


dependencies_df.to_csv(
    DEPENDENCIES_FILE,
    index=False,
)


# ============================================================
# DEPENDENCY SUMMARY
# ============================================================

print(
    f"\nDependencies generated : "
    f"{len(dependencies_df):,}"
)


print(
    f"Projects as dependents : "
    f"{dependencies_df['DependentProjectID'].nunique()}"
)


print(
    f"Projects as providers  : "
    f"{dependencies_df['ProviderProjectID'].nunique()}"
)


print(
    f"Average delay          : "
    f"{dependencies_df['DelayDays'].mean():.2f} days"
)


print(
    "\nDependency Status Distribution:"
)


print(
    dependencies_df[
        "DependencyStatus"
    ].value_counts()
)


print(
    "\nCriticality Distribution:"
)


print(
    dependencies_df[
        "Criticality"
    ].value_counts()
)


print(
    "\nRelease Impact Distribution:"
)


print(
    dependencies_df[
        "ReleaseImpact"
    ].value_counts()
)


print(
    f"\nOutput:"
    f"\n{DEPENDENCIES_FILE}"
)


print(
    "\nDependency validation passed."
)


print(
    "dependencies.csv generated successfully!"
)