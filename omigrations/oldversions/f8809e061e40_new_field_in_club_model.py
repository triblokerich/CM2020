"""new field in club model

Revision ID: f8809e061e40
Revises: 5ff76ba76db1
Create Date: 2019-09-17 21:34:11.291076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8809e061e40'
down_revision = '5ff76ba76db1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('club', sa.Column('clubname', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('club', 'clubname')
    # ### end Alembic commands ###
