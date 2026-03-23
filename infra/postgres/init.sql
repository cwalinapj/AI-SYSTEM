-- Enable pgvector extension
create extension if not exists vector;
create extension if not exists "uuid-ossp";

-- Projects
create table if not exists projects (
  id uuid primary key default uuid_generate_v4(),
  name text not null unique,
  root_path text,
  created_at timestamptz default now()
);

-- Unified memory items (semantic, episodic, procedural)
create table if not exists memory_items (
  id uuid primary key default uuid_generate_v4(),
  project_id uuid references projects(id) on delete cascade,
  namespace text not null,
  memory_type text not null check (memory_type in ('semantic', 'episodic', 'procedural', 'artifact_only')),
  title text not null,
  summary text not null,
  content text,
  importance int default 3 check (importance between 1 and 5),
  tags jsonb default '[]'::jsonb,
  source_kind text check (source_kind in ('chat', 'terminal', 'git', 'test', 'script', 'sensor')),
  source_ref text,
  expert_domain text default 'general',
  created_at timestamptz default now(),
  last_used_at timestamptz,
  use_count int default 0,
  embedding vector(1024)
);

create index if not exists memory_items_project_namespace_idx
  on memory_items (project_id, namespace);

create index if not exists memory_items_type_domain_idx
  on memory_items (memory_type, expert_domain);

create index if not exists memory_items_embedding_idx
  on memory_items using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

-- Artifacts (scripts, logs, diffs, bundles, reports)
create table if not exists artifacts (
  id uuid primary key default uuid_generate_v4(),
  project_id uuid references projects(id) on delete cascade,
  namespace text not null,
  artifact_type text not null check (artifact_type in ('script', 'log', 'diff', 'bundle', 'report', 'snapshot')),
  title text not null,
  uri text not null,
  checksum text,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

create index if not exists artifacts_project_type_idx
  on artifacts (project_id, artifact_type);

-- Script versions with validation tracking
create table if not exists script_versions (
  id uuid primary key default uuid_generate_v4(),
  project_id uuid references projects(id) on delete cascade,
  script_name text not null,
  version int not null,
  language text not null check (language in ('bash', 'python', 'make')),
  artifact_id uuid references artifacts(id),
  generated_from jsonb,
  validation_status text not null check (validation_status in ('pending', 'passed', 'failed')),
  created_at timestamptz default now(),
  unique(project_id, script_name, version)
);

-- Port leases for port management agent
create table if not exists port_leases (
  id uuid primary key default uuid_generate_v4(),
  service_name text not null,
  host_name text not null,
  protocol text not null default 'tcp' check (protocol in ('tcp', 'udp')),
  requested_port int,
  assigned_port int not null check (assigned_port between 1 and 65535),
  port_range text,
  owner_agent text,
  status text not null check (status in ('reserved', 'active', 'stale', 'conflict', 'released')),
  metadata jsonb default '{}'::jsonb,
  heartbeat_at timestamptz,
  created_at timestamptz default now(),
  unique(host_name, protocol, assigned_port)
);

create index if not exists port_leases_status_idx
  on port_leases (status);

create index if not exists port_leases_host_idx
  on port_leases (host_name, status);

-- Seed default port ranges as reference data
insert into projects (id, name, root_path)
values (uuid_generate_v4(), '__system__', '/')
on conflict (name) do nothing;
