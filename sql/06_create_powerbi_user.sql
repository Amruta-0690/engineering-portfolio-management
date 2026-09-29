-- ============================================================
-- EPMS - Power BI Read-Only User
-- File: 06_create_powerbi_user.sql
-- Purpose: Create a least-privilege account for Power BI
-- ============================================================

-- IMPORTANT:
-- Do not store real passwords in GitHub.
-- Replace the placeholder locally before execution.

CREATE USER IF NOT EXISTS 'epms_powerbi'@'localhost'
IDENTIFIED BY 'REPLACE_WITH_LOCAL_PASSWORD';

GRANT SELECT
ON engineering_portfolio_management.*
TO 'epms_powerbi'@'localhost';

FLUSH PRIVILEGES;