"""add club field

Revision ID: 432f5eef9ba9
Revises: 2da1d950f91f
Create Date: 2019-09-18 17:51:39.761880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '432f5eef9ba9'
down_revision = '2da1d950f91f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('club', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'user', 'club', ['club'], ['clubnum'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='foreignkey')
    op.drop_column('user', 'club')
    # ### end Alembic commands ###
