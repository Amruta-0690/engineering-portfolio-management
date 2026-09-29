"""
Load validated raw CSV data into the
Engineering Portfolio Management MySQL database.

Features:
- Runtime password entry
- Dependency-aware table loading
- CSV null handling
- Nullable integer normalization
- Batch inserts
- Transaction rollback on failure
- Row-count verification
"""

from getpass import getpass

import numpy as np
import pandas as pd
import mysql.connector

from python import config


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "engineering_portfolio_management"
DB_USER = "root"

BATCH_SIZE = 1000


# ============================================================
# TABLE LOAD ORDER
# ============================================================

TABLES = [
    "programs",
    "projects",
    "products",
    "teams",
    "employees",
    "stakeholders",
    "employee_team_assignments",
    "project_team_assignments",
    "project_stakeholder_assignments",
    "sprints",
    "work_items",
    "releases",
    "dependencies",
    "risks",
    "meetings",
    "action_items",
    "decisions",
    "okrs",
    "roadmap_items",
]


# ============================================================
# CSV FILE MAP
# ============================================================

FILES = {
    table: config.RAW_DATA_DIR / f"{table}.csv"
    for table in TABLES
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_value(value):
    """
    Convert pandas / NumPy values into
    MySQL-compatible Python values.
    """

    if pd.isna(value):
        return None

    if isinstance(value, np.integer):
        return int(value)

    if isinstance(value, np.floating):
        numeric_value = float(value)

        if numeric_value.is_integer():
            return int(numeric_value)

        return numeric_value

    if isinstance(value, np.bool_):
        return bool(value)

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value


def prepare_dataframe(table_name):
    """
    Read and normalize one CSV file.
    """

    file_path = FILES[table_name]

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing CSV file: {file_path}"
        )

    df = pd.read_csv(
        file_path
    )

    # Nullable numeric IDs can be read by pandas
    # as floats, for example ReleaseID = 1.0.
    # Convert these explicitly to nullable integers.
    nullable_id_columns = [
        "ParentWorkItemID",
        "ProjectID",
        "TeamID",
        "SprintID",
        "ProductID",
        "ReleaseID",
        "ManagerEmployeeID",
    ]

    for column in nullable_id_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            ).astype("Int64")

    return df


def build_insert_statement(
    table_name,
    columns,
):
    """
    Build a parameterized INSERT statement.
    """

    column_sql = ", ".join(
        f"`{column}`"
        for column in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    return (
        f"INSERT INTO `{table_name}` "
        f"({column_sql}) "
        f"VALUES ({placeholders})"
    )


def table_row_count(
    cursor,
    table_name,
):
    cursor.execute(
        f"SELECT COUNT(*) "
        f"FROM `{table_name}`"
    )

    return cursor.fetchone()[0]


# ============================================================
# START
# ============================================================

print("=" * 70)
print("MYSQL DATA LOADER")
print("=" * 70)


# ============================================================
# VERIFY SOURCE FILES
# ============================================================

missing_files = [
    str(path)
    for path in FILES.values()
    if not path.exists()
]


if missing_files:

    raise FileNotFoundError(
        "Required CSV files are missing:\n"
        + "\n".join(
            missing_files
        )
    )


print(
    f"\nSource CSV files found: "
    f"{len(FILES)}"
)


# ============================================================
# CONNECT
# ============================================================

db_password = getpass(
    "\nEnter MySQL root password: "
)


connection = None
cursor = None


try:

    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=db_password,
        database=DB_NAME,
    )


    cursor = connection.cursor()


    print(
        f"\nConnected to: {DB_NAME}"
    )


    # ========================================================
    # SAFETY CHECK - DATABASE MUST BE EMPTY
    # ========================================================

    non_empty_tables = []


    for table_name in TABLES:

        row_count = table_row_count(
            cursor,
            table_name,
        )

        if row_count != 0:

            non_empty_tables.append(
                (
                    table_name,
                    row_count,
                )
            )


    if non_empty_tables:

        details = "\n".join(
            f"{table}: {count:,} rows"
            for table, count
            in non_empty_tables
        )

        raise RuntimeError(
            "Load stopped because the database "
            "is not empty.\n\n"
            f"{details}\n\n"
            "No data was inserted."
        )


    print(
        "Database empty check passed."
    )


        # ========================================================
    # TRANSACTION
    # ========================================================
    # MySQL Connector has already opened a transaction
    # during the database safety checks above.
    # All subsequent inserts remain part of that transaction
    # until connection.commit() is called.

    expected_counts = {}

    # ========================================================
    # LOAD TABLES
    # ========================================================

    print(
        "\nLoading tables..."
    )


    for table_name in TABLES:

        df = prepare_dataframe(
            table_name
        )
        # Employees contain a self-referencing
        # ManagerEmployeeID foreign key.
        #
        # Load manager relationships in a second pass so
        # employee insertion does not depend on CSV row order.
        employee_manager_updates = None


        if table_name == "employees":

            employee_manager_updates = (
                df[
                    [
                        "EmployeeID",
                        "ManagerEmployeeID",
                    ]
                ]
                .dropna(
                    subset=[
                        "ManagerEmployeeID",
                    ]
                )
                .copy()
            )


            df[
                "ManagerEmployeeID"
            ] = pd.NA

        expected_counts[
            table_name
        ] = len(df)


        insert_sql = (
            build_insert_statement(
                table_name,
                df.columns,
            )
        )


        print(
            f"\nLoading "
            f"{table_name:<35} "
            f"{len(df):>7,} rows"
        )


        for start in range(
            0,
            len(df),
            BATCH_SIZE,
        ):

            batch = df.iloc[
                start:
                start + BATCH_SIZE
            ]


            records = [
                tuple(
                    clean_value(value)
                    for value in row
                )
                for row in batch.itertuples(
                    index=False,
                    name=None,
                )
            ]


            cursor.executemany(
                insert_sql,
                records,
            )

        # Restore employee-manager relationships only
        # after all employee rows exist.
        if (
            table_name == "employees"
            and employee_manager_updates is not None
        ):

            manager_update_sql = """
                UPDATE employees
                SET ManagerEmployeeID = %s
                WHERE EmployeeID = %s
            """


            manager_records = [
                (
                    int(row.ManagerEmployeeID),
                    int(row.EmployeeID),
                )
                for row in (
                    employee_manager_updates
                    .itertuples(
                        index=False
                    )
                )
            ]


            cursor.executemany(
                manager_update_sql,
                manager_records,
            )


            print(
                f"  [OK] Employee manager relationships: "
                f"{len(manager_records):,}"
            )


        print(
            f"  [OK] {table_name}"
        )
    # ========================================================
    # PRE-COMMIT ROW COUNT VALIDATION
    # ========================================================

    print(
        "\nVerifying loaded row counts..."
    )


    for table_name in TABLES:

        actual_count = table_row_count(
            cursor,
            table_name,
        )


        expected_count = (
            expected_counts[
                table_name
            ]
        )


        if actual_count != expected_count:

            raise RuntimeError(
                f"Row-count mismatch for "
                f"{table_name}. "
                f"Expected {expected_count:,}, "
                f"found {actual_count:,}."
            )


        print(
            f"  [PASS] "
            f"{table_name:<35} "
            f"{actual_count:>7,}"
        )


    # ========================================================
    # COMMIT
    # ========================================================

    connection.commit()


    print(
        "\nTransaction committed successfully."
    )


    # ========================================================
    # FINAL DATABASE SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "MYSQL LOAD COMPLETE"
    )

    print(
        "=" * 70
    )


    total_rows = 0


    for table_name in TABLES:

        row_count = table_row_count(
            cursor,
            table_name,
        )

        total_rows += row_count


        print(
            f"{table_name:<35} "
            f"{row_count:>8,}"
        )


    print(
        "-" * 45
    )

    print(
        f"{'TOTAL':<35} "
        f"{total_rows:>8,}"
    )


    print(
        "\nAll 19 CSV datasets loaded "
        "and verified successfully."
    )


except Exception as error:

    if (
        connection is not None
        and connection.is_connected()
    ):

        connection.rollback()


    print(
        "\n" + "=" * 70
    )

    print(
        "LOAD FAILED - TRANSACTION ROLLED BACK"
    )

    print(
        "=" * 70
    )

    print(
        f"\n{type(error).__name__}: "
        f"{error}"
    )


    raise


finally:

    if cursor is not None:
        cursor.close()


    if (
        connection is not None
        and connection.is_connected()
    ):

        connection.close()


    print(
        "\nMySQL connection closed."
    )