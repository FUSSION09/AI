// ==============================================================================
// Neo4j Community Edition: Triplestore Schema & Constraints
// Location: d:\AI\configs\neo4j_schema.cypher
// ==============================================================================

// 1. Uniqueness Constraints (Primary Keys)
CREATE CONSTRAINT constraint_document_id IF NOT EXISTS
FOR (d:Document) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT constraint_entity_name IF NOT EXISTS
FOR (e:Entity) REQUIRE e.name IS UNIQUE;

CREATE CONSTRAINT constraint_statute_code IF NOT EXISTS
FOR (s:Statute) REQUIRE s.code IS UNIQUE;

CREATE CONSTRAINT constraint_transaction_id IF NOT EXISTS
FOR (t:Transaction) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT constraint_risk_id IF NOT EXISTS
FOR (r:RiskIndicator) REQUIRE r.id IS UNIQUE;

// 2. Performance Indexes
CREATE INDEX index_entity_type IF NOT EXISTS
FOR (e:Entity) ON (e.type);

CREATE INDEX index_document_type IF NOT EXISTS
FOR (d:Document) ON (d.doc_type);

CREATE INDEX index_risk_severity IF NOT EXISTS
FOR (r:RiskIndicator) ON (r.severity);

// ==============================================================================
// 3. Triplestore Structural Mapping
//
// (:Document)        -[:CITES]->            (:Statute)
// (:Document)        -[:MENTIONS]->         (:Entity)
// (:Entity)          -[:CONTROLS]->         (:Entity)
// (:Entity)          -[:INITIATED]->        (:Transaction)
// (:Transaction)     -[:BENEFICIARY]->      (:Entity)
// (:Transaction)     -[:ASSOCIATED_WITH]->  (:RiskIndicator)
// (:RiskIndicator)   -[:BREACHES]->         (:Statute)
// ==============================================================================

