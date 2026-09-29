-- ============================================================
-- Engineering Portfolio Management & Delivery Intelligence
-- MySQL 8.0 Relational Schema
-- ============================================================

USE engineering_portfolio_management;


-- ============================================================
-- 1. PROGRAMS
-- ============================================================

CREATE TABLE programs (
    ProgramID INT PRIMARY KEY,
    ProgramName VARCHAR(150) NOT NULL,
    BusinessUnit VARCHAR(100),
    ProgramManager VARCHAR(150),
    ExecutiveSponsor VARCHAR(150),
    StartDate DATE NOT NULL,
    PlannedEndDate DATE NOT NULL,
    Status VARCHAR(50),
    HealthStatus VARCHAR(20),
    Budget DECIMAL(15,2),
    StrategicObjective VARCHAR(500),
    CreatedDate DATE
) ENGINE=InnoDB;


-- ============================================================
-- 2. PROJECTS
-- ============================================================

CREATE TABLE projects (
    ProjectID INT PRIMARY KEY,
    ProgramID INT NOT NULL,
    ProjectName VARCHAR(150) NOT NULL,
    ProjectManager VARCHAR(150),
    ProjectType VARCHAR(75),
    Methodology VARCHAR(50),
    Priority VARCHAR(20),
    StartDate DATE NOT NULL,
    PlannedEndDate DATE NOT NULL,
    Status VARCHAR(50),
    HealthStatus VARCHAR(20),
    CurrentPhase VARCHAR(75),
    ProgressPercent DECIMAL(5,2),
    PlannedBudget DECIMAL(15,2),
    ForecastBudget DECIMAL(15,2),
    BudgetVariancePercent DECIMAL(8,2),
    ScheduleVarianceDays INT,
    CreatedDate DATE,

    CONSTRAINT fk_projects_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID)
) ENGINE=InnoDB;


-- ============================================================
-- 3. PRODUCTS
-- ============================================================

CREATE TABLE products (
    ProductID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    ProductName VARCHAR(150) NOT NULL,
    ProductOwner VARCHAR(150),
    BusinessDomain VARCHAR(100),
    CustomerSegment VARCHAR(100),
    LifecycleStage VARCHAR(50),
    CurrentVersion VARCHAR(50),
    ReleaseFrequency VARCHAR(50),
    ActiveFlag BOOLEAN,

    CONSTRAINT fk_products_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;


-- ============================================================
-- 4. TEAMS
-- ============================================================

CREATE TABLE teams (
    TeamID INT PRIMARY KEY,
    TeamName VARCHAR(150) NOT NULL,
    TeamLead VARCHAR(150),
    ScrumMaster VARCHAR(150),
    PrimaryLocation VARCHAR(100),
    Specialization VARCHAR(100),
    DeliveryModel VARCHAR(50),
    PlannedTeamSize INT,
    VelocityTarget DECIMAL(8,2),
    ActiveFlag BOOLEAN
) ENGINE=InnoDB;


-- ============================================================
-- 5. EMPLOYEES
-- ============================================================

CREATE TABLE employees (
    EmployeeID INT PRIMARY KEY,
    EmployeeName VARCHAR(150) NOT NULL,
    Role VARCHAR(100),
    PrimarySkill VARCHAR(100),
    SecondarySkill VARCHAR(100),
    ExperienceYears DECIMAL(5,2),
    Location VARCHAR(100),
    EmploymentType VARCHAR(50),
    HireDate DATE,
    ManagerEmployeeID INT NULL,
    HourlyCostRate DECIMAL(10,2),
    ActiveFlag BOOLEAN,

    CONSTRAINT fk_employees_manager
        FOREIGN KEY (ManagerEmployeeID)
        REFERENCES employees (EmployeeID)
) ENGINE=InnoDB;


-- ============================================================
-- 6. STAKEHOLDERS
-- ============================================================

CREATE TABLE stakeholders (
    StakeholderID INT PRIMARY KEY,
    StakeholderName VARCHAR(150) NOT NULL,
    StakeholderRole VARCHAR(100),
    OrganizationLevel VARCHAR(75),
    StakeholderType VARCHAR(75),
    BusinessUnit VARCHAR(100),
    Location VARCHAR(100),
    InfluenceLevel VARCHAR(30),
    InterestLevel VARCHAR(30),
    CommunicationPreference VARCHAR(75),
    ActiveFlag BOOLEAN
) ENGINE=InnoDB;

-- ============================================================
-- 7. EMPLOYEE TEAM ASSIGNMENTS
-- ============================================================

CREATE TABLE employee_team_assignments (
    AssignmentID INT PRIMARY KEY,
    EmployeeID INT NOT NULL,
    TeamID INT NOT NULL,
    AssignmentStartDate DATE NOT NULL,
    AssignmentEndDate DATE NULL,
    AllocationPercent DECIMAL(5,2),
    AssignmentRole VARCHAR(100),
    AssignmentStatus VARCHAR(50),
    PrimaryAssignmentFlag BOOLEAN,

    CONSTRAINT fk_employee_team_employee
        FOREIGN KEY (EmployeeID)
        REFERENCES employees (EmployeeID),

    CONSTRAINT fk_employee_team_team
        FOREIGN KEY (TeamID)
        REFERENCES teams (TeamID)
) ENGINE=InnoDB;


-- ============================================================
-- 8. PROJECT TEAM ASSIGNMENTS
-- ============================================================

CREATE TABLE project_team_assignments (
    ProjectTeamAssignmentID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    TeamID INT NOT NULL,
    AssignmentStartDate DATE NOT NULL,
    AssignmentEndDate DATE NULL,
    AllocationPercent DECIMAL(5,2),
    AssignmentStatus VARCHAR(50),
    PrimaryTeamFlag BOOLEAN,

    CONSTRAINT fk_project_team_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_project_team_team
        FOREIGN KEY (TeamID)
        REFERENCES teams (TeamID)
) ENGINE=InnoDB;


-- ============================================================
-- 9. PROJECT STAKEHOLDER ASSIGNMENTS
-- ============================================================

CREATE TABLE project_stakeholder_assignments (
    ProjectStakeholderAssignmentID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    StakeholderID INT NOT NULL,
    StakeholderResponsibility VARCHAR(100),
    EngagementLevel VARCHAR(50),
    DecisionAuthority VARCHAR(50),
    CommunicationFrequency VARCHAR(50),
    AssignmentStartDate DATE NOT NULL,
    AssignmentEndDate DATE NULL,
    ActiveFlag BOOLEAN,

    CONSTRAINT fk_project_stakeholder_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_project_stakeholder_stakeholder
        FOREIGN KEY (StakeholderID)
        REFERENCES stakeholders (StakeholderID)
) ENGINE=InnoDB;

-- ============================================================
-- 10. SPRINTS
-- ============================================================

CREATE TABLE sprints (
    SprintID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    TeamID INT NOT NULL,
    SprintName VARCHAR(150) NOT NULL,
    SprintNumber INT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    SprintGoal VARCHAR(500),
    PlannedCapacityHours DECIMAL(10,2),
    ActualCapacityHours DECIMAL(10,2),
    CapacityUtilizationPercent DECIMAL(6,2),
    CommittedStoryPoints INT,
    CompletedStoryPoints INT,
    Velocity INT,
    SpilloverStoryPoints INT,
    CompletionPercent DECIMAL(6,2),
    SprintStatus VARCHAR(50),

    CONSTRAINT fk_sprints_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_sprints_team
        FOREIGN KEY (TeamID)
        REFERENCES teams (TeamID)
) ENGINE=InnoDB;


-- ============================================================
-- 11. WORK ITEMS
-- ============================================================

CREATE TABLE work_items (
    WorkItemID INT PRIMARY KEY,
    ParentWorkItemID INT NULL,
    WorkItemType VARCHAR(50) NOT NULL,
    ProjectID INT NULL,
    TeamID INT NULL,
    SprintID INT NULL,
    Title VARCHAR(255) NOT NULL,
    State VARCHAR(50),
    Priority VARCHAR(20),
    StoryPoints DECIMAL(6,2) NULL,
    Severity VARCHAR(20) NULL,
    CreatedDate DATE NOT NULL,
    ActivatedDate DATE NULL,
    ResolvedDate DATE NULL,
    ClosedDate DATE NULL,
    OriginalEstimateHours DECIMAL(10,2) NULL,
    CompletedWorkHours DECIMAL(10,2) NULL,
    RemainingWorkHours DECIMAL(10,2) NULL,
    DefectSource VARCHAR(100) NULL,

    CONSTRAINT fk_work_items_parent
        FOREIGN KEY (ParentWorkItemID)
        REFERENCES work_items (WorkItemID),

    CONSTRAINT fk_work_items_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_work_items_team
        FOREIGN KEY (TeamID)
        REFERENCES teams (TeamID),

    CONSTRAINT fk_work_items_sprint
        FOREIGN KEY (SprintID)
        REFERENCES sprints (SprintID)
) ENGINE=InnoDB;

-- ============================================================
-- 12. RELEASES
-- ============================================================

CREATE TABLE releases (
    ReleaseID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    ProductID INT NULL,
    ReleaseName VARCHAR(150) NOT NULL,
    ReleaseType VARCHAR(50),
    PlannedReleaseDate DATE NOT NULL,
    ForecastReleaseDate DATE,
    ActualReleaseDate DATE NULL,
    ReleaseStatus VARCHAR(50),
    DelayDays INT,
    ReadinessPercent DECIMAL(6,2),
    PlannedStoryPoints INT,
    CompletedStoryPoints INT,
    OpenBugCount INT,
    CriticalBugCount INT,
    GoLiveDecision VARCHAR(50),

    CONSTRAINT fk_releases_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_releases_product
        FOREIGN KEY (ProductID)
        REFERENCES products (ProductID)
) ENGINE=InnoDB;


-- ============================================================
-- 13. DEPENDENCIES
-- ============================================================

CREATE TABLE dependencies (
    DependencyID INT PRIMARY KEY,
    DependentProjectID INT NOT NULL,
    ProviderProjectID INT NOT NULL,
    DependentTeamID INT NOT NULL,
    ProviderTeamID INT NOT NULL,
    DependencyType VARCHAR(75),
    Description VARCHAR(500),
    Criticality VARCHAR(20),
    DependencyStatus VARCHAR(50),
    CreatedDate DATE NOT NULL,
    PlannedResolutionDate DATE,
    ForecastResolutionDate DATE,
    ActualResolutionDate DATE NULL,
    DelayDays INT,
    ReleaseImpact VARCHAR(50),

    CONSTRAINT fk_dependencies_dependent_project
        FOREIGN KEY (DependentProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_dependencies_provider_project
        FOREIGN KEY (ProviderProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_dependencies_dependent_team
        FOREIGN KEY (DependentTeamID)
        REFERENCES teams (TeamID),

    CONSTRAINT fk_dependencies_provider_team
        FOREIGN KEY (ProviderTeamID)
        REFERENCES teams (TeamID)
) ENGINE=InnoDB;


-- ============================================================
-- 14. RISKS
-- ============================================================

CREATE TABLE risks (
    RiskID INT PRIMARY KEY,
    ProjectID INT NOT NULL,
    RiskCategory VARCHAR(75),
    RiskTitle VARCHAR(255) NOT NULL,
    Probability INT,
    Impact INT,
    RiskScore INT,
    RiskRating VARCHAR(20),
    RiskStatus VARCHAR(50),
    Owner VARCHAR(150),
    IdentifiedDate DATE NOT NULL,
    TargetMitigationDate DATE,
    ClosedDate DATE NULL,
    MitigationPlan VARCHAR(1000),
    TriggerSource VARCHAR(100),
    ResidualRiskScore INT,

    CONSTRAINT fk_risks_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;

-- ============================================================
-- 15. MEETINGS
-- ============================================================

CREATE TABLE meetings (
    MeetingID INT PRIMARY KEY,
    ProgramID INT NOT NULL,
    ProjectID INT NOT NULL,
    MeetingType VARCHAR(75),
    MeetingDate DATE NOT NULL,
    Organizer VARCHAR(150),
    DurationMinutes INT,
    AttendeeCount INT,
    StakeholderAttendees TEXT,
    Agenda VARCHAR(1000),
    MeetingOutcome VARCHAR(500),
    FollowUpRequired BOOLEAN,
    FollowUpDate DATE NULL,

    CONSTRAINT fk_meetings_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID),

    CONSTRAINT fk_meetings_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;


-- ============================================================
-- 16. ACTION ITEMS
-- ============================================================

CREATE TABLE action_items (
    ActionItemID INT PRIMARY KEY,
    MeetingID INT NOT NULL,
    ProgramID INT NOT NULL,
    ProjectID INT NOT NULL,
    ActionDescription VARCHAR(500) NOT NULL,
    Owner VARCHAR(150),
    Priority VARCHAR(20),
    ActionStatus VARCHAR(50),
    CreatedDate DATE NOT NULL,
    DueDate DATE,
    CompletedDate DATE NULL,
    IsOverdue BOOLEAN,
    SourceType VARCHAR(75),

    CONSTRAINT fk_action_items_meeting
        FOREIGN KEY (MeetingID)
        REFERENCES meetings (MeetingID),

    CONSTRAINT fk_action_items_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID),

    CONSTRAINT fk_action_items_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;


-- ============================================================
-- 17. DECISIONS
-- ============================================================

CREATE TABLE decisions (
    DecisionID INT PRIMARY KEY,
    MeetingID INT NOT NULL,
    ProgramID INT NOT NULL,
    ProjectID INT NOT NULL,
    DecisionType VARCHAR(75),
    DecisionSummary VARCHAR(500) NOT NULL,
    DecisionOwner VARCHAR(150),
    DecisionDate DATE NOT NULL,
    DecisionStatus VARCHAR(50),
    EffectiveDate DATE NULL,
    BusinessImpact VARCHAR(50),
    RequiresFollowUp BOOLEAN,

    CONSTRAINT fk_decisions_meeting
        FOREIGN KEY (MeetingID)
        REFERENCES meetings (MeetingID),

    CONSTRAINT fk_decisions_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID),

    CONSTRAINT fk_decisions_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;

-- ============================================================
-- 18. OKRS
-- ============================================================

CREATE TABLE okrs (
    OKRID INT PRIMARY KEY,
    ProgramID INT NOT NULL,
    ProjectID INT NOT NULL,
    OKRCategory VARCHAR(50),
    Objective VARCHAR(500) NOT NULL,
    KeyResult VARCHAR(500) NOT NULL,
    MetricUnit VARCHAR(50),
    TargetValue DECIMAL(10,2),
    ActualValue DECIMAL(10,2),
    ProgressPercent DECIMAL(6,2),
    OKRStatus VARCHAR(50),
    ConfidenceLevel VARCHAR(30),
    Owner VARCHAR(150),
    PeriodStartDate DATE NOT NULL,
    PeriodEndDate DATE NOT NULL,

    CONSTRAINT fk_okrs_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID),

    CONSTRAINT fk_okrs_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID)
) ENGINE=InnoDB;


-- ============================================================
-- 19. ROADMAP ITEMS
-- ============================================================

CREATE TABLE roadmap_items (
    RoadmapItemID INT PRIMARY KEY,
    ProgramID INT NOT NULL,
    ProjectID INT NOT NULL,
    ProductID INT NULL,
    ReleaseID INT NULL,
    RoadmapType VARCHAR(75),
    RoadmapTitle VARCHAR(255) NOT NULL,
    StrategicTheme VARCHAR(100),
    Priority VARCHAR(20),
    RoadmapOwner VARCHAR(150),
    PlannedStartDate DATE NOT NULL,
    PlannedEndDate DATE NOT NULL,
    ForecastEndDate DATE,
    ScheduleVarianceDays INT,
    ProgressPercent DECIMAL(6,2),
    RoadmapStatus VARCHAR(50),

    CONSTRAINT fk_roadmap_program
        FOREIGN KEY (ProgramID)
        REFERENCES programs (ProgramID),

    CONSTRAINT fk_roadmap_project
        FOREIGN KEY (ProjectID)
        REFERENCES projects (ProjectID),

    CONSTRAINT fk_roadmap_product
        FOREIGN KEY (ProductID)
        REFERENCES products (ProductID),

    CONSTRAINT fk_roadmap_release
        FOREIGN KEY (ReleaseID)
        REFERENCES releases (ReleaseID)
) ENGINE=InnoDB;