-- Create scraping schema
CREATE SCHEMA IF NOT EXISTS scraping;

-- Create jobs table
CREATE TABLE IF NOT EXISTS scraping.jobs (
    id UUID PRIMARY KEY,
    parent_job_id UUID REFERENCES scraping.jobs(id),
    query TEXT,
    agent TEXT,
    role TEXT,
    report_type TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    status TEXT NOT NULL,
    research_costs DECIMAL(10,2) DEFAULT 0.0,
    visited_urls JSONB DEFAULT '[]'::jsonb,
    report TEXT,
    error_message TEXT,
    additional_info JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create pages table
CREATE TABLE IF NOT EXISTS scraping.pages (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES scraping.jobs(id),
    url TEXT NOT NULL,
    title TEXT,
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create logs table
CREATE TABLE IF NOT EXISTS scraping.logs (
    id UUID PRIMARY KEY,
    job_id UUID REFERENCES scraping.jobs(id),
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON scraping.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_started_at ON scraping.jobs(started_at);
CREATE INDEX IF NOT EXISTS idx_pages_job_id ON scraping.pages(job_id);
CREATE INDEX IF NOT EXISTS idx_pages_url ON scraping.pages(url);
CREATE INDEX IF NOT EXISTS idx_logs_job_id ON scraping.logs(job_id);
CREATE INDEX IF NOT EXISTS idx_logs_level ON scraping.logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON scraping.logs(created_at);
CREATE INDEX IF NOT EXISTS idx_jobs_parent_job_id ON scraping.jobs(parent_job_id);

-- Add RLS (Row Level Security) policies
ALTER TABLE scraping.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping.pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping.logs ENABLE ROW LEVEL SECURITY;

-- Create policies for jobs table
CREATE POLICY "Enable read access for all users" ON scraping.jobs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON scraping.jobs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for authenticated users only" ON scraping.jobs
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Create policies for pages table
CREATE POLICY "Enable read access for all users" ON scraping.pages
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON scraping.pages
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for authenticated users only" ON scraping.pages
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Create policies for logs table
CREATE POLICY "Enable read access for all users" ON scraping.logs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON scraping.logs
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable update for authenticated users only" ON scraping.logs
    FOR UPDATE USING (auth.role() = 'authenticated');
