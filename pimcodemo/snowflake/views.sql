-- PIMCO Municipal Bond Demo - Views
-- Views on top of dynamic tables for cleaner querying and lineage demonstration
-- DataHub will show lineage: Bronze Tables → Dynamic Tables → Views

-- Silver Schema: Views on Dynamic Tables
-- View on cleaned transactions (points to DT_TXN_7821)
CREATE OR REPLACE VIEW SLV_009.TXN_7821 AS
SELECT * FROM SLV_009.DT_TXN_7821;

-- View on bond dimension (points to DT_DIM_BND_001)
CREATE OR REPLACE VIEW SLV_009.DIM_BND_001 AS
SELECT * FROM SLV_009.DT_DIM_BND_001;

-- View on issuer dimension (points to DT_DIM_ISS_002)
CREATE OR REPLACE VIEW SLV_009.DIM_ISS_002 AS
SELECT * FROM SLV_009.DT_DIM_ISS_002;

-- Note: DIM_REG_003 and DIM_SEG_4421 are static tables populated from seed_data.sql
-- They don't need views since they're not dynamic

-- Gold Schema: Views on Dynamic Tables
-- View on aggregated positions (points to DT_POS_9912)
CREATE OR REPLACE VIEW GLD_003.POS_9912 AS
SELECT * FROM GLD_003.DT_POS_9912;

-- View on segment aggregations (points to DT_SEG_4421)
CREATE OR REPLACE VIEW GLD_003.SEG_4421 AS
SELECT * FROM GLD_003.DT_SEG_4421;

-- View on region aggregations (points to DT_REG_7733)
CREATE OR REPLACE VIEW GLD_003.REG_7733 AS
SELECT * FROM GLD_003.DT_REG_7733;

-- View on issuer aggregations (points to DT_ISS_8844)
CREATE OR REPLACE VIEW GLD_003.ISS_8844 AS
SELECT * FROM GLD_003.DT_ISS_8844;

-- View on growth metrics (points to DT_GRO_5566)
CREATE OR REPLACE VIEW GLD_003.GRO_5566 AS
SELECT * FROM GLD_003.DT_GRO_5566;

