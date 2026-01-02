"""Initial revision - before currencies

Revision ID: 88f1ebfdacd3
Revises:
Create Date: 2026-01-02 16:11:38.747574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '88f1ebfdacd3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'account',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'category',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'period',
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_table(
        'subcategory',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'business',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('default_category_id', sa.Integer(), nullable=False),
        sa.Column('default_subcategory_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['default_category_id'], ['category.id'], ),
        sa.ForeignKeyConstraint(['default_subcategory_id'], ['subcategory.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_table(
        'transaction',
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=True),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('account_for_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('subcategory_id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=True),
        sa.Column('period_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['account_for_id'], ['account.id'], ),
        sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.ForeignKeyConstraint(['period_id'], ['period.id'], ),
        sa.ForeignKeyConstraint(['subcategory_id'], ['subcategory.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('transaction')
    op.drop_table('business')
    op.drop_table('subcategory')
    op.drop_table('period')
    op.drop_table('category')
    op.drop_table('account')
