// Neo4j initialization script for organizational graph data
// This script sets up the initial constraints and indexes for the organizational twin

// Create constraints for unique identifiers
CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT role_id_unique IF NOT EXISTS FOR (r:Role) REQUIRE r.id IS UNIQUE;
CREATE CONSTRAINT department_id_unique IF NOT EXISTS FOR (d:Department) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT team_id_unique IF NOT EXISTS FOR (t:Team) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;

// Create indexes for performance
CREATE INDEX person_email_index IF NOT EXISTS FOR (p:Person) ON (p.email);
CREATE INDEX person_name_index IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX department_name_index IF NOT EXISTS FOR (d:Department) ON (d.name);
CREATE INDEX role_title_index IF NOT EXISTS FOR (r:Role) ON (r.title);
CREATE INDEX project_name_index IF NOT EXISTS FOR (p:Project) ON (p.name);
CREATE INDEX team_name_index IF NOT EXISTS FOR (t:Team) ON (t.name);

// Create text indexes for search
CREATE TEXT INDEX person_search_index IF NOT EXISTS FOR (p:Person) ON (p.name, p.bio, p.title);
CREATE TEXT INDEX project_search_index IF NOT EXISTS FOR (p:Project) ON (p.name, p.description);

// Create sample organizational structure
// Note: This will be replaced by migration data, but provides initial structure

// Create CEO
MERGE (ceo:Person {id: 'ceo-001', email: 'ceo@antifragile.com'})
SET ceo.name = 'CEO Executive',
    ceo.title = 'Chief Executive Officer',
    ceo.bio = 'Leading the organization with vision and strategy',
    ceo.created_at = datetime(),
    ceo.updated_at = datetime();

// Create CEO role
MERGE (ceo_role:Role {id: 'role-ceo'})
SET ceo_role.title = 'Chief Executive Officer',
    ceo_role.level = 'C-Level',
    ceo_role.description = 'Overall leadership and strategic direction';

// Create executive department
MERGE (exec_dept:Department {id: 'dept-executive'})
SET exec_dept.name = 'Executive',
    exec_dept.description = 'Executive leadership team';

// Create relationships
MERGE (ceo)-[:HAS_ROLE]->(ceo_role);
MERGE (ceo)-[:BELONGS_TO]->(exec_dept);
MERGE (ceo_role)-[:IN_DEPARTMENT]->(exec_dept);

// Log initialization
MERGE (init_log:InitLog {timestamp: datetime()})
SET init_log.message = 'Neo4j organizational graph initialized',
    init_log.version = '1.0.0';
