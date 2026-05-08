"""Added currencies

Revision ID: 18af1d975a1a
Revises: 88f1ebfdacd3
Create Date: 2026-05-08 21:59:21.119951

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from finance_tracker.main import interact


# revision identifiers, used by Alembic.
revision: str = '18af1d975a1a'
down_revision: Union[str, None] = '88f1ebfdacd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    currency = op.create_table('currency',
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_table('currency_rate',
        sa.Column('period_id', sa.Integer(), nullable=False),
        sa.Column('currency_from_id', sa.Integer(), nullable=False),
        sa.Column('currency_to_id', sa.Integer(), nullable=False),
        sa.Column('rate', sa.Float(), nullable=False),
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['currency_from_id'], ['currency.id'], name='fk_currency_rate_currency_from'),
        sa.ForeignKeyConstraint(['currency_to_id'], ['currency.id'], name='fk_currency_rate_currency_to'),
        sa.ForeignKeyConstraint(['period_id'], ['period.id'], name='fk_currency_rate_period'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period_id', 'currency_from_id', 'currency_to_id', name='uq_period_currency_from_currency_to')
    )

    #   Add default currencies - hard-code them here same as defaults
    currencies = [
        {"code": "EUR", "name": "Euro"},
        {"code": "USD", "name": "United States Dollar"},
        {"code": "GBP", "name": "Pound Sterling"},
        {"code": "BGN", "name": "Bulgarian Lev"},
        {"code": "CHF", "name": "Swiss Frank"},
        {"code": "JPY", "name": "Japanese Yen"},
        {"code": "CNY", "name": "Chinese Yuan"},
        {"code": "PLN", "name": "Polish Zloty"},
        {"code": "CZK", "name": "Czech Koruna"},
        {"code": "RON", "name": "Romanian Leu"},
        {"code": "DKK", "name": "Danish Krone"},
        {"code": "TRY", "name": "Turkish Lira"},
        {"code": "RUB", "name": "Russian Ruble"},
    ]
    with op.batch_alter_table("account") as batch_op:
        batch_op.add_column(sa.Column('default_currency_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_account_currency', 'currency', ['default_currency_id'], ['id'])

    with op.batch_alter_table("transaction") as batch_op:
        batch_op.add_column(sa.Column('currency_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_transaction_currency', 'currency', ['currency_id'], ['id'])

    #   Interaction
    op.bulk_insert(currency, currencies)
    default_currency = interact("Choose currency for existing data", currencies)
    default_currency_id = currencies.index(default_currency)
    account = sa.Table("account", sa.MetaData(), autoload_with=op.get_bind())
    op.execute(
        sa.update(account)
        .values({"default_currency_id": default_currency_id})
    )
    transaction = sa.Table("transaction", sa.MetaData(), autoload_with=op.get_bind())
    op.execute(
        sa.update(transaction)
        .values({"currency_id": default_currency_id})
    )

    with op.batch_alter_table("account") as batch_op:
        batch_op.alter_column("default_currency_id", nullable=False)

    with op.batch_alter_table("transaction") as batch_op:
        batch_op.alter_column("currency_id", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_transaction_currency', 'transaction', type_='foreignkey')
    op.drop_column('transaction', 'currency_id')
    op.drop_constraint('fk_account_currency', 'account', type_='foreignkey')
    op.drop_column('account', 'default_currency_id')
    op.drop_table('currency_rate')
    op.drop_table('currency')
