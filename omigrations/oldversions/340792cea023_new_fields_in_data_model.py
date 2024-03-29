"""new fields in data model

Revision ID: 340792cea023
Revises: 2b017edaa91f
Create Date: 2019-09-11 23:04:41.715941

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '340792cea023'
down_revision = '2b017edaa91f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('dob', sa.DATE(), nullable=True))
    op.add_column('user', sa.Column('gender', sa.String(length=1), nullable=True))
    op.add_column('user', sa.Column('usernum', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_user_usernum'), 'user', ['usernum'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_usernum'), table_name='user')
    op.drop_column('user', 'usernum')
    op.drop_column('user', 'gender')
    op.drop_column('user', 'dob')
    # ### end Alembic commands ###
