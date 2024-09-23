"""initial migration

Revision ID: dba6ad1c960b
Revises: 
Create Date: 2024-09-23 21:19:20.722815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dba6ad1c960b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('food', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))

    with op.batch_alter_table('food', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
