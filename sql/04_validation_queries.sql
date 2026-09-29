-- ============================================================
-- EPMS - MySQL Data Validation
-- File: 04_validation_queries.sql
-- Purpose: Validate loaded portfolio-management data
-- ============================================================

USE engineering_portfolio_management;


-- ============================================================
-- 1. ROW COUNT VALIDATION
-- ============================================================

SELECT 'programs' AS TableName, COUNT(*) AS RowCount FROM programs
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'teams', COUNT(*) FROM teams
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'stakeholders', COUNT(*) FROM stakeholders
UNION ALL
SELECT 'employee_team_assignments', COUNT(*) FROM employee_team_assignments
UNION ALL
SELECT 'project_team_assignments', COUNT(*) FROM project_team_assignments
UNION ALL
SELECT 'project_stakeholder_assignments', COUNT(*) FROM project_stakeholder_assignments
UNION ALL
SELECT 'sprints', COUNT(*) FROM sprints
UNION ALL
SELECT 'work_items', COUNT(*) FROM work_items
UNION ALL
SELECT 'releases', COUNT(*) FROM releases
UNION ALL
SELECT 'dependencies', COUNT(*) FROM dependencies
UNION ALL
SELECT 'risks', COUNT(*) FROM risks
UNION ALL
SELECT 'meetings', COUNT(*) FROM meetings
UNION ALL
SELECT 'action_items', COUNT(*) FROM action_items
UNION ALL
SELECT 'decisions', COUNT(*) FROM decisions
UNION ALL
SELECT 'okrs', COUNT(*) FROM okrs
UNION ALL
SELECT 'roadmap_items', COUNT(*) FROM roadmap_items;

-- ============================================================
-- 2. REFERENTIAL INTEGRITY VALIDATION
-- Expected result for every check: 0
-- ============================================================

SELECT 'Projects without valid Program' AS ValidationCheck,
       COUNT(*) AS InvalidRows
FROM projects p
LEFT JOIN programs pr
    ON p.ProgramID = pr.ProgramID
WHERE pr.ProgramID IS NULL

UNION ALL

SELECT 'Products without valid Project',
       COUNT(*)
FROM products p
LEFT JOIN projects pr
    ON p.ProjectID = pr.ProjectID
WHERE pr.ProjectID IS NULL

UNION ALL

SELECT 'Sprints without valid Project',
       COUNT(*)
FROM sprints s
LEFT JOIN projects p
    ON s.ProjectID = p.ProjectID
WHERE p.ProjectID IS NULL

UNION ALL

SELECT 'Sprints without valid Team',
       COUNT(*)
FROM sprints s
LEFT JOIN teams t
    ON s.TeamID = t.TeamID
WHERE t.TeamID IS NULL

UNION ALL

SELECT 'Work Items without valid Project',
       COUNT(*)
FROM work_items w
LEFT JOIN projects p
    ON w.ProjectID = p.ProjectID
WHERE p.ProjectID IS NULL

UNION ALL

SELECT 'Work Items without valid Team',
       COUNT(*)
FROM work_items w
LEFT JOIN teams t
    ON w.TeamID = t.TeamID
WHERE w.TeamID IS NOT NULL
  AND t.TeamID IS NULL

UNION ALL

SELECT 'Work Items without valid Sprint',
       COUNT(*)
FROM work_items w
LEFT JOIN sprints s
    ON w.SprintID = s.SprintID
WHERE w.SprintID IS NOT NULL
  AND s.SprintID IS NULL

UNION ALL

SELECT 'Work Items without valid Parent',
       COUNT(*)
FROM work_items w
LEFT JOIN work_items parent
    ON w.ParentWorkItemID = parent.WorkItemID
WHERE w.ParentWorkItemID IS NOT NULL
  AND parent.WorkItemID IS NULL

UNION ALL

SELECT 'Releases without valid Project',
       COUNT(*)
FROM releases r
LEFT JOIN projects p
    ON r.ProjectID = p.ProjectID
WHERE p.ProjectID IS NULL

UNION ALL

SELECT 'Releases without valid Product',
       COUNT(*)
FROM releases r
LEFT JOIN products p
    ON r.ProductID = p.ProductID
WHERE r.ProductID IS NOT NULL
  AND p.ProductID IS NULL

UNION ALL

SELECT 'Risks without valid Project',
       COUNT(*)
FROM risks r
LEFT JOIN projects p
    ON r.ProjectID = p.ProjectID
WHERE p.ProjectID IS NULL

UNION ALL

SELECT 'Action Items without valid Meeting',
       COUNT(*)
FROM action_items a
LEFT JOIN meetings m
    ON a.MeetingID = m.MeetingID
WHERE a.MeetingID IS NOT NULL
  AND m.MeetingID IS NULL

UNION ALL

SELECT 'Decisions without valid Meeting',
       COUNT(*)
FROM decisions d
LEFT JOIN meetings m
    ON d.MeetingID = m.MeetingID
WHERE d.MeetingID IS NOT NULL
  AND m.MeetingID IS NULL

UNION ALL

SELECT 'Roadmap Items without valid Release',
       COUNT(*)
FROM roadmap_items r
LEFT JOIN releases rel
    ON r.ReleaseID = rel.ReleaseID
WHERE r.ReleaseID IS NOT NULL
  AND rel.ReleaseID IS NULL;

 -- ============================================================
-- 4. DATE LOGIC VALIDATION
-- Expected result for every check: 0
-- ============================================================

SELECT
    'Sprint End Before Start' AS ValidationCheck,
    COUNT(*) AS InvalidRows
FROM sprints
WHERE EndDate < StartDate

UNION ALL

SELECT
    'Work Item Closed Before Created',
    COUNT(*)
FROM work_items
WHERE ClosedDate IS NOT NULL
  AND ClosedDate < CreatedDate

UNION ALL

SELECT
    'Work Item Resolved Before Created',
    COUNT(*)
FROM work_items
WHERE ResolvedDate IS NOT NULL
  AND ResolvedDate < CreatedDate

UNION ALL

SELECT
    'Release Actual Before Planned',
    COUNT(*)
FROM releases
WHERE ActualReleaseDate IS NOT NULL
  AND ActualReleaseDate < PlannedReleaseDate

UNION ALL

SELECT
    'Risk Closed Before Identified',
    COUNT(*)
FROM risks
WHERE ClosedDate IS NOT NULL
  AND ClosedDate < IdentifiedDate

UNION ALL

SELECT
    'Action Completed Before Created',
    COUNT(*)
FROM action_items
WHERE CompletedDate IS NOT NULL
  AND CompletedDate < CreatedDate

UNION ALL

SELECT
    'OKR Period End Before Start',
    COUNT(*)
FROM okrs
WHERE PeriodEndDate < PeriodStartDate

UNION ALL

SELECT
    'Roadmap Planned End Before Start',
    COUNT(*)
FROM roadmap_items
WHERE PlannedEndDate < PlannedStartDate

UNION ALL

SELECT
    'Roadmap Forecast End Before Start',
    COUNT(*)
FROM roadmap_items
WHERE ForecastEndDate < PlannedStartDate;