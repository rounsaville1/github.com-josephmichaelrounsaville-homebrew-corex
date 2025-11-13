-- R-COREX Bitcoin Mainnet System
-- PostgreSQL Database Schema
-- Author: Joseph Michael Rounsaville

-- Enable TimescaleDB extension (if available)
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Enable pg_trgm for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- BLOCKCHAIN TABLES
-- ============================================================================

-- Blocks table - Stores all Bitcoin blocks
CREATE TABLE IF NOT EXISTS blocks (
    height BIGINT PRIMARY KEY,
    hash VARCHAR(64) UNIQUE NOT NULL,
    version INTEGER NOT NULL,
    merkleroot VARCHAR(64) NOT NULL,
    time TIMESTAMP NOT NULL,
    mediantime TIMESTAMP,
    nonce BIGINT NOT NULL,
    bits VARCHAR(8) NOT NULL,
    difficulty DOUBLE PRECISION NOT NULL,
    chainwork VARCHAR(64),
    tx_count INTEGER NOT NULL DEFAULT 0,
    size BIGINT NOT NULL,
    weight BIGINT NOT NULL,
    previousblockhash VARCHAR(64),
    nextblockhash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT blocks_height_check CHECK (height >= 0)
);

-- Create indexes for blocks
CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(hash);
CREATE INDEX IF NOT EXISTS idx_blocks_time ON blocks(time DESC);
CREATE INDEX IF NOT EXISTS idx_blocks_previoushash ON blocks(previousblockhash);
CREATE INDEX IF NOT EXISTS idx_blocks_difficulty ON blocks(difficulty DESC);

-- Convert to TimescaleDB hypertable (if available)
SELECT create_hypertable('blocks', 'time', if_not_exists => TRUE);

-- ============================================================================
-- TRANSACTION TABLES
-- ============================================================================

-- Transactions table - Stores all Bitcoin transactions
CREATE TABLE IF NOT EXISTS transactions (
    txid VARCHAR(64) PRIMARY KEY,
    hash VARCHAR(64) NOT NULL,
    version INTEGER NOT NULL,
    size INTEGER NOT NULL,
    vsize INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    locktime BIGINT NOT NULL,
    blockhash VARCHAR(64),
    blockheight BIGINT,
    time TIMESTAMP,
    blocktime TIMESTAMP,
    confirmations INTEGER DEFAULT 0,
    hex TEXT,
    is_coinbase BOOLEAN DEFAULT FALSE,
    fee BIGINT DEFAULT 0, -- in satoshis
    fee_rate DOUBLE PRECISION DEFAULT 0, -- sat/vB
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (blockhash) REFERENCES blocks(hash) ON DELETE CASCADE
);

-- Create indexes for transactions
CREATE INDEX IF NOT EXISTS idx_tx_blockhash ON transactions(blockhash);
CREATE INDEX IF NOT EXISTS idx_tx_blockheight ON transactions(blockheight DESC);
CREATE INDEX IF NOT EXISTS idx_tx_time ON transactions(time DESC);
CREATE INDEX IF NOT EXISTS idx_tx_confirmations ON transactions(confirmations);
CREATE INDEX IF NOT EXISTS idx_tx_is_coinbase ON transactions(is_coinbase);
CREATE INDEX IF NOT EXISTS idx_tx_fee_rate ON transactions(fee_rate DESC);

-- ============================================================================
-- TRANSACTION INPUT/OUTPUT TABLES
-- ============================================================================

-- Transaction inputs (vin)
CREATE TABLE IF NOT EXISTS tx_inputs (
    id BIGSERIAL PRIMARY KEY,
    txid VARCHAR(64) NOT NULL,
    vout_index INTEGER NOT NULL,
    prev_txid VARCHAR(64),
    prev_vout INTEGER,
    scriptSig TEXT,
    scriptsig_asm TEXT,
    sequence BIGINT NOT NULL,
    witness TEXT[], -- Array of witness data
    is_coinbase BOOLEAN DEFAULT FALSE,
    coinbase TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE,
    UNIQUE (txid, vout_index)
);

-- Create indexes for inputs
CREATE INDEX IF NOT EXISTS idx_tx_inputs_txid ON tx_inputs(txid);
CREATE INDEX IF NOT EXISTS idx_tx_inputs_prev ON tx_inputs(prev_txid, prev_vout);
CREATE INDEX IF NOT EXISTS idx_tx_inputs_coinbase ON tx_inputs(is_coinbase);

-- Transaction outputs (vout)
CREATE TABLE IF NOT EXISTS tx_outputs (
    id BIGSERIAL PRIMARY KEY,
    txid VARCHAR(64) NOT NULL,
    vout_index INTEGER NOT NULL,
    value BIGINT NOT NULL, -- in satoshis
    scriptPubKey TEXT NOT NULL,
    scriptpubkey_asm TEXT,
    scriptpubkey_type VARCHAR(20),
    address VARCHAR(100),
    spent BOOLEAN DEFAULT FALSE,
    spent_txid VARCHAR(64), -- Transaction that spent this output
    spent_vin INTEGER, -- Input index in spending transaction
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (txid) REFERENCES transactions(txid) ON DELETE CASCADE,
    UNIQUE (txid, vout_index)
);

-- Create indexes for outputs
CREATE INDEX IF NOT EXISTS idx_tx_outputs_txid ON tx_outputs(txid);
CREATE INDEX IF NOT EXISTS idx_tx_outputs_address ON tx_outputs(address);
CREATE INDEX IF NOT EXISTS idx_tx_outputs_spent ON tx_outputs(spent);
CREATE INDEX IF NOT EXISTS idx_tx_outputs_value ON tx_outputs(value DESC);
CREATE INDEX IF NOT EXISTS idx_tx_outputs_type ON tx_outputs(scriptpubkey_type);

-- ============================================================================
-- ADDRESS TABLES
-- ============================================================================

-- Addresses table - Aggregate address data
CREATE TABLE IF NOT EXISTS addresses (
    address VARCHAR(100) PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- P2PKH, P2SH, P2WPKH, P2WSH, etc.
    balance BIGINT DEFAULT 0, -- Current balance in satoshis
    received BIGINT DEFAULT 0, -- Total received in satoshis
    sent BIGINT DEFAULT 0, -- Total sent in satoshis
    tx_count INTEGER DEFAULT 0,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for addresses
CREATE INDEX IF NOT EXISTS idx_addresses_balance ON addresses(balance DESC);
CREATE INDEX IF NOT EXISTS idx_addresses_type ON addresses(type);
CREATE INDEX IF NOT EXISTS idx_addresses_tx_count ON addresses(tx_count DESC);
CREATE INDEX IF NOT EXISTS idx_addresses_last_seen ON addresses(last_seen DESC);

-- ============================================================================
-- MEMPOOL TABLES
-- ============================================================================

-- Mempool transactions
CREATE TABLE IF NOT EXISTS mempool_transactions (
    txid VARCHAR(64) PRIMARY KEY,
    size INTEGER NOT NULL,
    vsize INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    fee BIGINT NOT NULL, -- in satoshis
    fee_rate DOUBLE PRECISION NOT NULL, -- sat/vB
    time TIMESTAMP NOT NULL,
    height INTEGER NOT NULL,
    descendantcount INTEGER,
    descendantsize INTEGER,
    descendantfees BIGINT,
    ancestorcount INTEGER,
    ancestorsize INTEGER,
    ancestorfees BIGINT,
    depends TEXT[], -- Array of txids this depends on
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for mempool
CREATE INDEX IF NOT EXISTS idx_mempool_fee_rate ON mempool_transactions(fee_rate DESC);
CREATE INDEX IF NOT EXISTS idx_mempool_time ON mempool_transactions(time DESC);
CREATE INDEX IF NOT EXISTS idx_mempool_size ON mempool_transactions(vsize DESC);

-- ============================================================================
-- NETWORK TABLES
-- ============================================================================

-- Peer connections
CREATE TABLE IF NOT EXISTS peers (
    id SERIAL PRIMARY KEY,
    addr VARCHAR(100) NOT NULL,
    addrlocal VARCHAR(100),
    network VARCHAR(20),
    version INTEGER,
    subver VARCHAR(100),
    inbound BOOLEAN,
    addnode BOOLEAN,
    connection_type VARCHAR(20),
    synced_headers INTEGER,
    synced_blocks INTEGER,
    inflight INTEGER,
    bytessent BIGINT,
    bytesrecv BIGINT,
    conntime TIMESTAMP,
    pingtime DOUBLE PRECISION,
    minping DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for peers
CREATE INDEX IF NOT EXISTS idx_peers_addr ON peers(addr);
CREATE INDEX IF NOT EXISTS idx_peers_connection_type ON peers(connection_type);
CREATE INDEX IF NOT EXISTS idx_peers_last_seen ON peers(last_seen DESC);

-- ============================================================================
-- ANALYTICS TABLES
-- ============================================================================

-- Fee statistics (time-series)
CREATE TABLE IF NOT EXISTS fee_stats (
    time TIMESTAMP NOT NULL,
    target_blocks INTEGER NOT NULL, -- Confirmation target
    fee_rate DOUBLE PRECISION NOT NULL, -- sat/vB
    method VARCHAR(20), -- conservative, economical, smart
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (time, target_blocks)
);

-- Create hypertable for fee stats
SELECT create_hypertable('fee_stats', 'time', if_not_exists => TRUE);

-- Create index
CREATE INDEX IF NOT EXISTS idx_fee_stats_target ON fee_stats(target_blocks, time DESC);

-- Block statistics (time-series)
CREATE TABLE IF NOT EXISTS block_stats (
    height BIGINT PRIMARY KEY,
    time TIMESTAMP NOT NULL,
    total_fee BIGINT NOT NULL,
    avg_fee DOUBLE PRECISION,
    median_fee DOUBLE PRECISION,
    total_out BIGINT NOT NULL,
    avg_txsize INTEGER,
    median_txsize INTEGER,
    ins INTEGER NOT NULL,
    outs INTEGER NOT NULL,
    utxo_increase INTEGER,
    utxo_size_inc INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create hypertable for block stats
SELECT create_hypertable('block_stats', 'time', if_not_exists => TRUE);

-- ============================================================================
-- SYSTEM TABLES
-- ============================================================================

-- Indexing progress tracking
CREATE TABLE IF NOT EXISTS indexing_status (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL, -- blocks, transactions, addresses
    last_indexed_height BIGINT,
    last_indexed_hash VARCHAR(64),
    last_indexed_time TIMESTAMP,
    total_indexed BIGINT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, error
    error_message TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE IF NOT EXISTS api_usage (
    id BIGSERIAL PRIMARY KEY,
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    api_key VARCHAR(64),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create hypertable for API usage
SELECT create_hypertable('api_usage', 'timestamp', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_ip ON api_usage(ip_address, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_key ON api_usage(api_key, timestamp DESC);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Recent blocks view
CREATE OR REPLACE VIEW recent_blocks AS
SELECT
    height,
    hash,
    time,
    tx_count,
    size,
    difficulty,
    confirmations
FROM (
    SELECT
        height,
        hash,
        time,
        tx_count,
        size,
        difficulty,
        (SELECT MAX(height) FROM blocks) - height + 1 AS confirmations
    FROM blocks
    ORDER BY height DESC
    LIMIT 100
) AS recent;

-- Unspent transaction outputs (UTXO) view
CREATE OR REPLACE VIEW utxo_set AS
SELECT
    o.txid,
    o.vout_index,
    o.value,
    o.address,
    o.scriptpubkey_type,
    t.blockheight,
    t.confirmations
FROM tx_outputs o
JOIN transactions t ON o.txid = t.txid
WHERE o.spent = FALSE
    AND t.confirmations > 0;

-- Address balances view
CREATE OR REPLACE VIEW address_balances AS
SELECT
    address,
    SUM(value) AS balance,
    COUNT(*) AS utxo_count
FROM utxo_set
GROUP BY address
HAVING SUM(value) > 0
ORDER BY balance DESC;

-- Mempool fee histogram
CREATE OR REPLACE VIEW mempool_fee_histogram AS
SELECT
    CASE
        WHEN fee_rate < 1 THEN '0-1'
        WHEN fee_rate < 5 THEN '1-5'
        WHEN fee_rate < 10 THEN '5-10'
        WHEN fee_rate < 20 THEN '10-20'
        WHEN fee_rate < 50 THEN '20-50'
        WHEN fee_rate < 100 THEN '50-100'
        ELSE '100+'
    END AS fee_range,
    COUNT(*) AS count,
    SUM(vsize) AS total_vsize,
    AVG(fee_rate) AS avg_fee_rate
FROM mempool_transactions
GROUP BY fee_range
ORDER BY
    CASE fee_range
        WHEN '0-1' THEN 1
        WHEN '1-5' THEN 2
        WHEN '5-10' THEN 3
        WHEN '10-20' THEN 4
        WHEN '20-50' THEN 5
        WHEN '50-100' THEN 6
        ELSE 7
    END;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update address statistics
CREATE OR REPLACE FUNCTION update_address_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update address statistics when outputs are created or updated
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        INSERT INTO addresses (address, type, balance, tx_count, first_seen, last_seen)
        VALUES (
            NEW.address,
            NEW.scriptpubkey_type,
            NEW.value,
            1,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (address) DO UPDATE SET
            balance = addresses.balance + EXCLUDED.balance,
            tx_count = addresses.tx_count + 1,
            last_seen = CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update address stats
CREATE TRIGGER trigger_update_address_stats
AFTER INSERT OR UPDATE ON tx_outputs
FOR EACH ROW
WHEN (NEW.address IS NOT NULL)
EXECUTE FUNCTION update_address_stats();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert genesis block placeholder
INSERT INTO blocks (
    height, hash, version, merkleroot, time, nonce, bits, difficulty,
    tx_count, size, weight, previousblockhash
) VALUES (
    0,
    '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f',
    1,
    '4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b',
    '2009-01-03 18:15:05',
    2083236893,
    '1d00ffff',
    1.0,
    1,
    285,
    1140,
    '0000000000000000000000000000000000000000000000000000000000000000'
)
ON CONFLICT (height) DO NOTHING;

-- Initialize indexing status
INSERT INTO indexing_status (type, last_indexed_height, status) VALUES
    ('blocks', 0, 'active'),
    ('transactions', 0, 'active'),
    ('addresses', 0, 'active')
ON CONFLICT DO NOTHING;

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant permissions to bitcoin user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bitcoin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bitcoin;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO bitcoin;

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Set up automatic vacuum
ALTER TABLE transactions SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tx_inputs SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE tx_outputs SET (autovacuum_vacuum_scale_factor = 0.01);
ALTER TABLE addresses SET (autovacuum_vacuum_scale_factor = 0.05);

-- Analyze tables
ANALYZE blocks;
ANALYZE transactions;
ANALYZE tx_inputs;
ANALYZE tx_outputs;
ANALYZE addresses;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE blocks IS 'Bitcoin blockchain blocks';
COMMENT ON TABLE transactions IS 'Bitcoin transactions';
COMMENT ON TABLE tx_inputs IS 'Transaction inputs (vin)';
COMMENT ON TABLE tx_outputs IS 'Transaction outputs (vout/UTXO)';
COMMENT ON TABLE addresses IS 'Bitcoin addresses with aggregated statistics';
COMMENT ON TABLE mempool_transactions IS 'Pending transactions in mempool';
COMMENT ON TABLE peers IS 'Bitcoin network peer connections';
COMMENT ON TABLE fee_stats IS 'Fee estimation statistics over time';
COMMENT ON TABLE block_stats IS 'Block statistics for analytics';

-- Schema complete
COMMIT;
