-- ============================================================
-- EPMS - Analytics Views
-- File: 05_create_analytics_views.sql
-- Purpose: Reusable analytical layer for Power BI and SQL
-- ============================================================

USE engineering_portfolio_management;


-- ============================================================
-- 1. PROJECT PORTFOLIO HEALTH
-- Grain: One row per project
-- ============================================================

CREATE OR REPLACE VIEW vw_project_portfolio_health AS

SELECT
    p.ProjectID,
    p.ProjectName,
    p.ProgramID,
    pr.ProgramName,

    COALESCE(s.SprintCount, 0) AS SprintCount,
    COALESCE(rel.ReleaseCount, 0) AS ReleaseCount,
    COALESCE(w.WorkItemCount, 0) AS WorkItemCount,
    COALESCE(rk.RiskCount, 0) AS RiskCount,

    COALESCE(rk.OpenRiskCount, 0) AS OpenRiskCount,
    COALESCE(rk.HighCriticalOpenRiskCount, 0)
        AS HighCriticalOpenRiskCount,

    COALESCE(w.BugCount, 0) AS BugCount,
    COALESCE(w.OpenBugCount, 0) AS OpenBugCount,

    s.AvgSprintCompletionPercent,
    rel.AvgReleaseReadinessPercent,
    rel.AvgReleaseDelayDays

FROM projects p

INNER JOIN programs pr
    ON p.ProgramID = pr.ProgramID


-- ------------------------------------------------------------
-- Sprint metrics
-- ------------------------------------------------------------

LEFT JOIN (
    SELECT
        ProjectID,
        COUNT(*) AS SprintCount,
        ROUND(
            AVG(CompletionPercent),
            2
        ) AS AvgSprintCompletionPercent

    FROM sprints

    GROUP BY ProjectID
) s
    ON p.ProjectID = s.ProjectID


-- ------------------------------------------------------------
-- Release metrics
-- ------------------------------------------------------------

LEFT JOIN (
    SELECT
        ProjectID,
        COUNT(*) AS ReleaseCount,

        ROUND(
            AVG(ReadinessPercent),
            2
        ) AS AvgReleaseReadinessPercent,

        ROUND(
            AVG(DelayDays),
            2
        ) AS AvgReleaseDelayDays

    FROM releases

    GROUP BY ProjectID
) rel
    ON p.ProjectID = rel.ProjectID


-- ------------------------------------------------------------
-- Work item / bug metrics
-- ------------------------------------------------------------

LEFT JOIN (
    SELECT
        ProjectID,

        COUNT(*) AS WorkItemCount,

        SUM(
            CASE
                WHEN WorkItemType = 'Bug'
                THEN 1
                ELSE 0
            END
        ) AS BugCount,

        SUM(
            CASE
                WHEN WorkItemType = 'Bug'
                     AND State NOT IN (
                         'Closed',
                         'Resolved'
                     )
                THEN 1
                ELSE 0
            END
        ) AS OpenBugCount

    FROM work_items

    GROUP BY ProjectID
) w
    ON p.ProjectID = w.ProjectID


-- ------------------------------------------------------------
-- Risk metrics
-- ------------------------------------------------------------

LEFT JOIN (
    SELECT
        ProjectID,

        COUNT(*) AS RiskCount,

        SUM(
            CASE
                WHEN RiskStatus <> 'Closed'
                THEN 1
                ELSE 0
            END
        ) AS OpenRiskCount,

        SUM(
            CASE
                WHEN RiskStatus <> 'Closed'
                     AND RiskRating IN (
                         'High',
                         'Critical'
                     )
                THEN 1
                ELSE 0
            END
        ) AS HighCriticalOpenRiskCount

    FROM risks

    GROUP BY ProjectID
) rk
    ON p.ProjectID = rk.ProjectID;

    -- ============================================================
-- 2. SPRINT DELIVERY PERFORMANCE
-- Grain: One row per sprint
-- ============================================================

CREATE OR REPLACE VIEW vw_sprint_delivery_performance AS

SELECT
    s.SprintID,
    s.SprintName,
    s.SprintNumber,

    s.ProjectID,
    p.ProjectName,

    p.ProgramID,
    pr.ProgramName,

    s.TeamID,
    t.TeamName,

    s.StartDate,
    s.EndDate,
    s.SprintStatus,

    s.PlannedCapacityHours,
    s.ActualCapacityHours,
    s.CapacityUtilizationPercent,

    s.CommittedStoryPoints,
    s.CompletedStoryPoints,
    s.Velocity,
    s.SpilloverStoryPoints,
    s.CompletionPercent,

    CASE
        WHEN s.CommittedStoryPoints > 0
        THEN ROUND(
            (
                s.SpilloverStoryPoints
                / s.CommittedStoryPoints
            ) * 100,
            2
        )
        ELSE 0
    END AS SpilloverPercent,

    CASE
        WHEN s.CompletionPercent >= 90
        THEN 'Healthy'

        WHEN s.CompletionPercent >= 75
        THEN 'Watch'

        ELSE 'At Risk'
    END AS SprintHealth

FROM sprints s

INNER JOIN projects p
    ON s.ProjectID = p.ProjectID

INNER JOIN programs pr
    ON p.ProgramID = pr.ProgramID

INNER JOIN teams t
    ON s.TeamID = t.TeamID;

    -- ============================================================
-- 3. RELEASE HEALTH
-- Grain: One row per release
-- ============================================================

CREATE OR REPLACE VIEW vw_release_health AS

SELECT
    r.ReleaseID,
    r.ReleaseName,
    r.ReleaseType,

    r.ProjectID,
    p.ProjectName,

    p.ProgramID,
    pr.ProgramName,

    r.ProductID,
    prod.ProductName,

    r.PlannedReleaseDate,
    r.ForecastReleaseDate,
    r.ActualReleaseDate,

    r.ReleaseStatus,
    r.DelayDays,
    r.ReadinessPercent,

    r.PlannedStoryPoints,
    r.CompletedStoryPoints,

    r.OpenBugCount,
    r.CriticalBugCount,
    r.GoLiveDecision,

    CASE
        WHEN r.PlannedStoryPoints > 0
        THEN ROUND(
            (
                r.CompletedStoryPoints
                / r.PlannedStoryPoints
            ) * 100,
            2
        )
        ELSE 0
    END AS StoryPointCompletionPercent,

    CASE
        WHEN r.CriticalBugCount > 0
             OR r.DelayDays > 14
             OR r.ReadinessPercent < 70
        THEN 'At Risk'

        WHEN r.DelayDays > 0
             OR r.ReadinessPercent < 90
        THEN 'Watch'

        ELSE 'Healthy'
    END AS ReleaseHealth

FROM releases r

INNER JOIN projects p
    ON r.ProjectID = p.ProjectID

INNER JOIN programs pr
    ON p.ProgramID = pr.ProgramID

LEFT JOIN products prod
    ON r.ProductID = prod.ProductID;

    -- ============================================================
-- 4. RISK EXPOSURE
-- Grain: One row per risk
-- ============================================================

CREATE OR REPLACE VIEW vw_risk_exposure AS

SELECT
    r.RiskID,

    r.ProjectID,
    p.ProjectName,

    p.ProgramID,
    pr.ProgramName,

    r.RiskCategory,
    r.RiskTitle,

    r.Probability,
    r.Impact,
    r.RiskScore,
    r.RiskRating,
    r.RiskStatus,

    r.Owner,
    r.IdentifiedDate,
    r.TargetMitigationDate,
    r.ClosedDate,

    r.TriggerSource,
    r.ResidualRiskScore,

    CASE
        WHEN r.RiskStatus <> 'Closed'
             AND r.TargetMitigationDate < CURDATE()
        THEN 1
        ELSE 0
    END AS IsMitigationOverdue,

    CASE
        WHEN r.RiskStatus <> 'Closed'
             AND r.RiskRating IN ('High', 'Critical')
        THEN 1
        ELSE 0
    END AS IsHighCriticalOpenRisk

FROM risks r

INNER JOIN projects p
    ON r.ProjectID = p.ProjectID

INNER JOIN programs pr
    ON p.ProgramID = pr.ProgramID;
    -- ============================================================
-- 5. DEPENDENCY EXPOSURE
-- Grain: One row per dependency
-- ============================================================

CREATE OR REPLACE VIEW vw_dependency_exposure AS

SELECT
    d.DependencyID,

    d.DependentProjectID,
    dp.ProjectName AS DependentProjectName,

    d.ProviderProjectID,
    pp.ProjectName AS ProviderProjectName,

    dp.ProgramID AS DependentProgramID,
    dpr.ProgramName AS DependentProgramName,

    d.DependentTeamID,
    dt.TeamName AS DependentTeamName,

    d.ProviderTeamID,
    pt.TeamName AS ProviderTeamName,

    d.DependencyType,
    d.Description,
    d.Criticality,
    d.DependencyStatus,

    d.CreatedDate,
    d.PlannedResolutionDate,
    d.ForecastResolutionDate,
    d.ActualResolutionDate,

    d.DelayDays,
    d.ReleaseImpact,

    CASE
        WHEN d.DependencyStatus <> 'Resolved'
             AND d.PlannedResolutionDate < CURDATE()
        THEN 1
        ELSE 0
    END AS IsOverdue,

    CASE
        WHEN d.DependencyStatus <> 'Resolved'
             AND d.Criticality IN ('High', 'Critical')
        THEN 1
        ELSE 0
    END AS IsHighCriticalOpenDependency

FROM dependencies d

INNER JOIN projects dp
    ON d.DependentProjectID = dp.ProjectID

INNER JOIN programs dpr
    ON dp.ProgramID = dpr.ProgramID

INNER JOIN projects pp
    ON d.ProviderProjectID = pp.ProjectID

INNER JOIN teams dt
    ON d.DependentTeamID = dt.TeamID

INNER JOIN teams pt
    ON d.ProviderTeamID = pt.TeamID;

    -- ============================================================
-- 6. ACTION ITEM GOVERNANCE
-- Grain: One row per action item
-- ============================================================

CREATE OR REPLACE VIEW vw_action_item_governance AS

SELECT
    a.ActionItemID,
    a.MeetingID,

    a.ProgramID,
    pr.ProgramName,

    a.ProjectID,
    p.ProjectName,

    m.MeetingType,
    m.MeetingDate,

    a.ActionDescription,
    a.Owner,
    a.Priority,
    a.ActionStatus,

    a.CreatedDate,
    a.DueDate,
    a.CompletedDate,

    a.IsOverdue,
    a.SourceType,

    CASE
        WHEN a.ActionStatus <> 'Completed'
             AND a.DueDate < CURDATE()
        THEN DATEDIFF(
            CURDATE(),
            a.DueDate
        )
        ELSE 0
    END AS DaysOverdue,

    CASE
        WHEN a.ActionStatus = 'Completed'
        THEN DATEDIFF(
            a.CompletedDate,
            a.CreatedDate
        )
        ELSE NULL
    END AS CompletionCycleDays

FROM action_items a

LEFT JOIN meetings m
    ON a.MeetingID = m.MeetingID

INNER JOIN programs pr
    ON a.ProgramID = pr.ProgramID

INNER JOIN projects p
    ON a.ProjectID = p.ProjectID;

    -- ============================================================
-- 7. OKR PERFORMANCE
-- Grain: One row per OKR
-- ============================================================

CREATE OR REPLACE VIEW vw_okr_performance AS

SELECT
    o.OKRID,

    o.ProgramID,
    pr.ProgramName,

    o.ProjectID,
    p.ProjectName,

    o.OKRCategory,
    o.Objective,
    o.KeyResult,
    o.MetricUnit,

    o.TargetValue,
    o.ActualValue,
    o.ProgressPercent,

    o.OKRStatus,
    o.ConfidenceLevel,
    o.Owner,

    o.PeriodStartDate,
    o.PeriodEndDate,

    CASE
        WHEN o.ProgressPercent >= 90
        THEN 'On Track'

        WHEN o.ProgressPercent >= 70
        THEN 'Watch'

        ELSE 'At Risk'
    END AS PerformanceHealth,

    CASE
        WHEN o.ActualValue >= o.TargetValue
        THEN 1
        ELSE 0
    END AS IsTargetAchieved

FROM okrs o

INNER JOIN programs pr
    ON o.ProgramID = pr.ProgramID

INNER JOIN projects p
    ON o.ProjectID = p.ProjectID;
    -- ============================================================
-- 8. ROADMAP DELIVERY
-- Grain: One row per roadmap item
-- ============================================================

CREATE OR REPLACE VIEW vw_roadmap_delivery AS

SELECT
    rm.RoadmapItemID,

    rm.ProgramID,
    pr.ProgramName,

    rm.ProjectID,
    p.ProjectName,

    rm.ProductID,
    prod.ProductName,

    rm.ReleaseID,
    rel.ReleaseName,

    rm.RoadmapType,
    rm.RoadmapTitle,
    rm.StrategicTheme,
    rm.Priority,
    rm.RoadmapOwner,

    rm.PlannedStartDate,
    rm.PlannedEndDate,
    rm.ForecastEndDate,

    rm.ScheduleVarianceDays,
    rm.ProgressPercent,
    rm.RoadmapStatus,

    CASE
        WHEN rm.ScheduleVarianceDays > 14
             OR rm.ProgressPercent < 50
        THEN 'At Risk'

        WHEN rm.ScheduleVarianceDays > 0
             OR rm.ProgressPercent < 75
        THEN 'Watch'

        ELSE 'Healthy'
    END AS RoadmapHealth,

    CASE
        WHEN rm.ForecastEndDate > rm.PlannedEndDate
        THEN 1
        ELSE 0
    END AS IsForecastDelayed

FROM roadmap_items rm

INNER JOIN programs pr
    ON rm.ProgramID = pr.ProgramID

INNER JOIN projects p
    ON rm.ProjectID = p.ProjectID

LEFT JOIN products prod
    ON rm.ProductID = prod.ProductID

LEFT JOIN releases rel
    ON rm.ReleaseID = rel.ReleaseID;

    -- ============================================================
-- 9. WORK ITEM DELIVERY
-- Grain: One row per work item
-- ============================================================

CREATE OR REPLACE VIEW vw_work_item_delivery AS

SELECT
    wi.WorkItemID,
    wi.ParentWorkItemID,
    wi.WorkItemType,

    wi.ProjectID,
    p.ProjectName,

    p.ProgramID,
    pr.ProgramName,

    wi.TeamID,
    t.TeamName,

    wi.SprintID,
    s.SprintName,
    s.SprintNumber,

    wi.Title,
    wi.State,
    wi.Priority,
    wi.StoryPoints,
    wi.Severity,

    wi.CreatedDate,
    wi.ActivatedDate,
    wi.ResolvedDate,
    wi.ClosedDate,

    wi.OriginalEstimateHours,
    wi.CompletedWorkHours,
    wi.RemainingWorkHours,
    wi.DefectSource,

    CASE
        WHEN wi.WorkItemType = 'Bug'
        THEN 1
        ELSE 0
    END AS IsBug,

    CASE
        WHEN wi.WorkItemType = 'Bug'
             AND wi.State NOT IN ('Closed', 'Resolved')
        THEN 1
        ELSE 0
    END AS IsOpenBug,

    CASE
        WHEN wi.WorkItemType = 'Bug'
             AND wi.Severity IN ('Critical', 'High')
             AND wi.State NOT IN ('Closed', 'Resolved')
        THEN 1
        ELSE 0
    END AS IsHighSeverityOpenBug,

    CASE
        WHEN wi.ClosedDate IS NOT NULL
        THEN DATEDIFF(
            wi.ClosedDate,
            wi.CreatedDate
        )
        ELSE NULL
    END AS CycleDays

FROM work_items wi

INNER JOIN projects p
    ON wi.ProjectID = p.ProjectID

INNER JOIN programs pr
    ON p.ProgramID = pr.ProgramID

LEFT JOIN teams t
    ON wi.TeamID = t.TeamID

LEFT JOIN sprints s
    ON wi.SprintID = s.SprintID;