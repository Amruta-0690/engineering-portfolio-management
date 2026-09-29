-- ============================================================
-- EPMS - Performance Indexes
-- File: 03_create_indexes.sql
-- Purpose: Add analytical indexes not already provided
--          by MySQL foreign-key indexes
-- ============================================================

USE engineering_portfolio_management;


-- ============================================================
-- 1. WORK ITEM ANALYTICS
-- ============================================================

CREATE INDEX idx_work_items_type
    ON work_items (WorkItemType);

CREATE INDEX idx_work_items_state
    ON work_items (State);

CREATE INDEX idx_work_items_project_type_state
    ON work_items (ProjectID, WorkItemType, State);


-- ============================================================
-- 2. DEPENDENCY ANALYTICS
-- ============================================================

CREATE INDEX idx_dependencies_status
    ON dependencies (DependencyStatus);


-- ============================================================
-- 3. RISK ANALYTICS
-- ============================================================

CREATE INDEX idx_risks_status_rating
    ON risks (RiskStatus, RiskRating);


-- ============================================================
-- 4. RELEASE ANALYTICS
-- ============================================================

CREATE INDEX idx_releases_status_date
    ON releases (ReleaseStatus, PlannedReleaseDate);


-- ============================================================
-- 5. SPRINT ANALYTICS
-- ============================================================

CREATE INDEX idx_sprints_status_dates
    ON sprints (SprintStatus, StartDate, EndDate);


-- ============================================================
-- 6. ACTION ITEM ANALYTICS
-- ============================================================

CREATE INDEX idx_action_items_status_due
    ON action_items (ActionStatus, DueDate);


-- ============================================================
-- 7. OKR ANALYTICS
-- ============================================================

CREATE INDEX idx_okrs_status
    ON okrs (OKRStatus);


-- ============================================================
-- 8. ROADMAP ANALYTICS
-- ============================================================

CREATE INDEX idx_roadmap_status
    ON roadmap_items (RoadmapStatus);