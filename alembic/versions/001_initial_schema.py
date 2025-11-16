"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-11-15

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('subscription_tier', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tenants_id', 'tenants', ['id'])
    op.create_index('ix_tenants_org_name', 'tenants', ['org_name'], unique=True)

    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # techniques table
    op.create_table(
        'techniques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('technique_id', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tactics', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('detection_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_techniques_id', 'techniques', ['id'])
    op.create_index('ix_techniques_technique_id', 'techniques', ['technique_id'], unique=True)

    # sub_techniques table
    op.create_table(
        'sub_techniques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('technique_id', sa.String(length=20), nullable=False),
        sa.Column('parent_technique_id', sa.String(length=20), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(['parent_technique_id'], ['techniques.technique_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sub_techniques_id', 'sub_techniques', ['id'])
    op.create_index('ix_sub_techniques_technique_id', 'sub_techniques', ['technique_id'], unique=True)

    # detection_strategies table
    op.create_table(
        'detection_strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.String(length=20), nullable=False),
        sa.Column('technique_id', sa.String(length=20), nullable=True),
        sa.Column('sub_technique_id', sa.String(length=20), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('behavior_to_detect', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['technique_id'], ['techniques.technique_id']),
        sa.ForeignKeyConstraint(['sub_technique_id'], ['sub_techniques.technique_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_detection_strategies_id', 'detection_strategies', ['id'])
    op.create_index('ix_detection_strategies_strategy_id', 'detection_strategies', ['strategy_id'], unique=True)

    # analytics table
    op.create_table(
        'analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analytic_id', sa.String(length=20), nullable=False),
        sa.Column('strategy_id', sa.String(length=20), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detection_logic', sa.Text(), nullable=True),
        sa.Column('platform', sa.String(length=100), nullable=True),
        sa.Column('data_components_required', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('tunable_parameters', postgresql.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['strategy_id'], ['detection_strategies.strategy_id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_id', 'analytics', ['id'])
    op.create_index('ix_analytics_analytic_id', 'analytics', ['analytic_id'], unique=True)

    # data_components table
    op.create_table(
        'data_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_source_name', sa.String(length=255), nullable=True),
        sa.Column('log_source_type', sa.String(length=100), nullable=True),
        sa.Column('collection_requirements', postgresql.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_data_components_id', 'data_components', ['id'])
    op.create_index('ix_data_components_component_id', 'data_components', ['component_id'], unique=True)

    # threat_groups table
    op.create_table(
        'threat_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('aliases', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_industries', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('techniques_used', postgresql.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_threat_groups_id', 'threat_groups', ['id'])
    op.create_index('ix_threat_groups_group_id', 'threat_groups', ['group_id'], unique=True)

    # assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('assessment_name', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('organization_size', sa.String(length=50), nullable=True),
        sa.Column('cloud_usage', postgresql.JSON(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('coverage_percentage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assessments_id', 'assessments', ['id'])

    # questionnaire_responses table
    op.create_table(
        'questionnaire_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.String(length=50), nullable=True),
        sa.Column('capability_type', sa.String(length=100), nullable=True),
        sa.Column('has_capability', sa.Boolean(), nullable=True),
        sa.Column('coverage_level', sa.Integer(), nullable=True),
        sa.Column('platforms_covered', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questionnaire_responses_id', 'questionnaire_responses', ['id'])

    # technique_coverage table
    op.create_table(
        'technique_coverage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=True),
        sa.Column('technique_id', sa.String(length=20), nullable=True),
        sa.Column('coverage_status', sa.Enum('COVERED', 'PARTIAL', 'NONE', 'NOT_APPLICABLE', name='coveragestatus'), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('strategies_implemented', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('analytics_implemented', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('data_components_available', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('data_components_missing', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('priority_rank', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_technique_coverage_id', 'technique_coverage', ['id'])

def downgrade() -> None:
    op.drop_table('technique_coverage')
    op.drop_table('questionnaire_responses')
    op.drop_table('assessments')
    op.drop_table('threat_groups')
    op.drop_table('data_components')
    op.drop_table('analytics')
    op.drop_table('detection_strategies')
    op.drop_table('sub_techniques')
    op.drop_table('techniques')
    op.drop_table('users')
    op.drop_table('tenants')
