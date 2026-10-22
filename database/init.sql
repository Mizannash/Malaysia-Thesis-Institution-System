-- MTIS Database Initialization & Multi-Tenant Migrations
-- Phase 1 Foundation: Tenants, Users, Projects with RLS

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tenants Table
CREATE TABLE IF NOT EXISTS tenants (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'supervisor', 'admin')),
    plan VARCHAR(32) NOT NULL DEFAULT 'free',
    trial_start TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    quota_remaining INT NOT NULL DEFAULT 3,
    quota_reset_at TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 day'),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(64) PRIMARY KEY,
    tenant_id VARCHAR(64) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(512) NOT NULL,
    stage VARCHAR(64) NOT NULL DEFAULT 'search',
    state_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance & tenant filtering
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Enforce RLS even for table owners when set
ALTER TABLE users FORCE ROW LEVEL SECURITY;
ALTER TABLE projects FORCE ROW LEVEL SECURITY;

-- Helper function to retrieve active tenant from session variable or Supabase JWT
CREATE OR REPLACE FUNCTION get_current_tenant() RETURNS text AS $$
BEGIN
    -- 1. Try application session variable
    IF NULLIF(current_setting('app.current_tenant_id', true), '') IS NOT NULL THEN
        RETURN current_setting('app.current_tenant_id', true);
    END IF;
    -- 2. Try Supabase JWT claim if present
    BEGIN
        IF NULLIF(current_setting('request.jwt.claims', true), '') IS NOT NULL THEN
            RETURN (current_setting('request.jwt.claims', true)::jsonb -> 'app_metadata' ->> 'tenant_id');
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RETURN NULL;
    END;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- RLS Policies for Projects
DROP POLICY IF EXISTS tenant_isolation_projects ON projects;
CREATE POLICY tenant_isolation_projects ON projects
    FOR ALL
    USING (tenant_id = get_current_tenant())
    WITH CHECK (tenant_id = get_current_tenant());

-- RLS Policies for Users
DROP POLICY IF EXISTS tenant_isolation_users ON users;
CREATE POLICY tenant_isolation_users ON users
    FOR ALL
    USING (tenant_id = get_current_tenant())
    WITH CHECK (tenant_id = get_current_tenant());

-- Bypass policy for app_admin role or unconstrained internal tasks when explicitly configured
CREATE ROLE IF NOT EXISTS mtis_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mtis_app;

-- Seed Data: TWO Tenants (UTM default + Demo University)
INSERT INTO tenants (id, name, created_at)
VALUES 
    ('tenant-utm-001', 'Universiti Teknologi Malaysia (UTM)', CURRENT_TIMESTAMP),
    ('tenant-demo-002', 'Demo University', CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Temporarily bypass RLS to seed initial users and projects
SET LOCAL app.current_tenant_id = 'tenant-utm-001';

INSERT INTO users (id, tenant_id, name, email, role, plan, quota_remaining)
VALUES 
    ('usr-utm-student', 'tenant-utm-001', 'Ahmad Student', 'ahmad@utm.my', 'student', 'free', 3),
    ('usr-utm-supervisor', 'tenant-utm-001', 'Dr. Siti Supervisor', 'siti@utm.my', 'supervisor', 'pro', 99)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO projects (id, tenant_id, user_id, title, stage, state_json)
VALUES 
    ('prj-utm-101', 'tenant-utm-001', 'usr-utm-student', 'AI Research Gap Analysis in SME E-Wallet Adoption', 'search', '{"topic": "E-wallet adoption in Malaysian SMEs", "scope": "MY"}'::jsonb),
    ('prj-utm-102', 'tenant-utm-001', 'usr-utm-student', 'IoT Precision Farming in Johor Palm Oil Plantations', 'gap', '{"topic": "IoT precision agriculture", "scope": "MY"}'::jsonb)
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title;

-- Seed Demo University
SET LOCAL app.current_tenant_id = 'tenant-demo-002';

INSERT INTO users (id, tenant_id, name, email, role, plan, quota_remaining)
VALUES 
    ('usr-demo-student', 'tenant-demo-002', 'Alex Demo Student', 'alex@demouniv.edu.my', 'student', 'free', 3),
    ('usr-demo-supervisor', 'tenant-demo-002', 'Prof. Tan Supervisor', 'tan@demouniv.edu.my', 'supervisor', 'pro', 99)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO projects (id, tenant_id, user_id, title, stage, state_json)
VALUES 
    ('prj-demo-201', 'tenant-demo-002', 'usr-demo-student', 'Blockchain Smart Contracts in Malaysian Logistic Supply Chains', 'title', '{"topic": "Logistics supply chain blockchain", "scope": "INT"}'::jsonb)
ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title;

-- Reset tenant session
RESET app.current_tenant_id;
