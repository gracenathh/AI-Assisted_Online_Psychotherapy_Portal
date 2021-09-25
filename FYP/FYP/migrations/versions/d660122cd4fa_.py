"""empty message

Revision ID: d660122cd4fa
Revises: 8757c80982c8
Create Date: 2021-09-14 10:36:31.371949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd660122cd4fa'
down_revision = '8757c80982c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patient', sa.Column('therapist', sa.Integer(), nullable=False))
    op.drop_constraint(None, 'patient', type_='foreignkey')
    op.create_foreign_key(None, 'patient', 'user', ['therapist'], ['id'])
    op.drop_column('patient', 'therapy_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patient', sa.Column('therapy_id', sa.INTEGER(), nullable=False))
    op.drop_constraint(None, 'patient', type_='foreignkey')
    op.create_foreign_key(None, 'patient', 'user', ['therapy_id'], ['id'])
    op.drop_column('patient', 'therapist')
    # ### end Alembic commands ###