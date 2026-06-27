"""add_loan_number_column

Revision ID: f0cd718050b4
Revises: 305d85088306
Create Date: 2026-06-25 23:52:50.375843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0cd718050b4'
down_revision: Union[str, Sequence[str], None] = '305d85088306'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the sequence that will drive future auto-increments
    op.execute("CREATE SEQUENCE IF NOT EXISTS loan_number_seq START 1")

    # Add the column (nullable so existing rows don't fail)
    op.add_column('loans', sa.Column('loan_number', sa.Integer(), nullable=True))

    # Back-fill existing loans with sequential numbers ordered by creation date
    op.execute("""
        UPDATE loans
        SET loan_number = sub.rn
        FROM (
            SELECT id, ROW_NUMBER() OVER (ORDER BY created_at ASC) AS rn
            FROM loans
        ) sub
        WHERE loans.id = sub.id
    """)

    # Set the sequence to continue from after the highest existing number
    op.execute("SELECT setval('loan_number_seq', COALESCE((SELECT MAX(loan_number) FROM loans), 0) + 1, false)")

    # Set the column default to draw from the sequence
    op.execute("ALTER TABLE loans ALTER COLUMN loan_number SET DEFAULT nextval('loan_number_seq')")

    # Add unique constraint
    op.create_unique_constraint('uq_loans_loan_number', 'loans', ['loan_number'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_loans_loan_number', 'loans', type_='unique')
    op.execute("ALTER TABLE loans ALTER COLUMN loan_number DROP DEFAULT")
    op.drop_column('loans', 'loan_number')
    op.execute("DROP SEQUENCE IF EXISTS loan_number_seq")
