"""Protect attendance history when a student profile is deleted.

Revision ID: 9f4d8a2b6c1e
Revises: 2c3d1b5cc8e9
Create Date: 2026-10-24 10:30:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "9f4d8a2b6c1e"
down_revision: Union[str, Sequence[str], None] = "2c3d1b5cc8e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("attendance_records_student_id_fkey", "attendance_records", type_="foreignkey")
    op.create_foreign_key(
        "attendance_records_student_id_fkey",
        "attendance_records",
        "students",
        ["student_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("attendance_records_student_id_fkey", "attendance_records", type_="foreignkey")
    op.create_foreign_key(
        "attendance_records_student_id_fkey",
        "attendance_records",
        "students",
        ["student_id"],
        ["id"],
        ondelete="CASCADE",
    )
