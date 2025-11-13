# Unified Bitcoin Mainnet System Architecture
## R-COREX Bitcoin Core Integration

**Version:** 1.0.0
**Date:** 2025-11-13
**Status:** Production Ready

---

## 1. SYSTEM OVERVIEW

This system provides a unified Bitcoin mainnet infrastructure with comprehensive API access, real-time analytics, network visualization, and secure wallet management. All cryptographic operations use the Bitcoin standard double SHA256 algorithm.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Client Applications                          │
│         (Web, Mobile, Desktop, Third-party APIs)                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   API Gateway Layer                              │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐     │
│  │ /status  │ /tx/<h>  │ /blocks  │ /mempool │ /network │     │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘     │
│              FastAPI + Auth + Rate Limiting                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Business Logic Layer                              │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  Service Modules (Inherited from main.py concept)    │      │
│  │                                                        │      │
│  │  1. bitcoin_node_service     → Node operations       │      │
│  │  2. transaction_service       → TX processing        │      │
│  │  3. blockchain_service        → Block management     │      │
│  │  4. mempool_service           → Mempool monitoring   │      │
│  │  5. wallet_service            → Key & wallet mgmt    │      │
│  │  6. analytics_service         → Intelligence engine  │      │
│  │  7. network_graph_service     → Topology analysis    │      │
│  │  8. security_service          → Crypto & validation  │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                   Data Access Layer                              │
│  ┌──────────┬───────────┬──────────┬──────────┐                │
│  │PostgreSQL│ Redis     │TimescaleDB│  Neo4j  │                │
│  │(indexed) │ (cache)   │(analytics)│ (graph) │                │
│  └──────────┴───────────┴──────────┴──────────┘                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                 Bitcoin Core Layer                               │
│  ┌────────────────────────────────────────────────────┐         │
│  │          Bitcoin Core Node (mainnet)               │         │
│  │                                                      │         │
│  │  • Full blockchain validation                       │         │
│  │  • SHA256 double hashing                           │         │
│  │  • P2P network communication                        │         │
│  │  • UTXO set management                             │         │
│  │  • Mempool management                              │         │
│  │  • JSON-RPC interface                              │         │
│  └────────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. MODULE MAPPING (From Conceptual to Bitcoin Reality)

### Original Module → Bitcoin Implementation

1. **quantum_pulse.QuantumPulseEngine** → **bitcoin_network.P2PManager**
   - P2P network communication
   - Peer discovery and management
   - Network message handling

2. **quantum_audio_engine.QuantumAudioEngine** → **notification_service.AlertManager**
   - Transaction notifications
   - Block confirmation alerts
   - System event notifications

3. **infinite_crystalstack.CrystalStack** → **blockchain_storage.BlockchainDB**
   - Blockchain data storage
   - Block indexing
   - Transaction history

4. **obfuscation_lock.PresenceVault** → **wallet_manager.SecureWallet**
   - Private key management
   - HD wallet (BIP32/39/44)
   - Multi-signature support

5. **logic_forecast.ForecastEngine** → **analytics_engine.TransactionAnalyzer**
   - Fee estimation
   - Transaction pattern analysis
   - Network health metrics

6. **self_building_routines.AutoBuilder** → **automation_service.PaymentAutomation**
   - Scheduled payments
   - Smart contract execution
   - Batch processing

7. **trigger_portal.ThoughtTrigger** → **mobile_api.MobileGateway**
   - Mobile app API
   - Push notifications
   - QR code generation

8. **indexing_grid.DimensionalIndex** → **graph_database.NetworkGraph**
   - Transaction graph
   - Address clustering
   - Network topology visualization

---

## 3. API ENDPOINT SPECIFICATIONS

### 3.1 GET /status
**Purpose:** Node health and synchronization status

**Response:**
```json
{
  "node": {
    "version": "26.0.0",
    "network": "mainnet",
    "uptime": 86400,
    "connections": 45
  },
  "blockchain": {
    "blocks": 820145,
    "headers": 820145,
    "sync_progress": 1.0,
    "verification_progress": 1.0,
    "size_on_disk": 567382901234
  },
  "mempool": {
    "size": 12453,
    "bytes": 34567890,
    "usage": 124567890
  },
  "system": {
    "presence_verified": true,
    "modules_initialized": true,
    "api_online": true,
    "timestamp": "2025-11-13T12:34:56Z"
  }
}
```

### 3.2 GET /transaction/<tx_hash>
**Purpose:** Retrieve transaction details by hash

**Parameters:**
- `tx_hash` (required): Transaction hash (64 hex characters)

**Response:**
```json
{
  "txid": "abc123...",
  "hash": "abc123...",
  "version": 2,
  "size": 225,
  "vsize": 144,
  "weight": 573,
  "locktime": 0,
  "vin": [...],
  "vout": [...],
  "hex": "01000000...",
  "blockhash": "00000000...",
  "confirmations": 6,
  "time": 1699891234,
  "blocktime": 1699891234,
  "analysis": {
    "fee": 0.00001440,
    "fee_rate": 10.0,
    "type": "P2WPKH"
  }
}
```

### 3.3 GET /blocks
**Purpose:** Retrieve block data and history

**Query Parameters:**
- `height` (optional): Specific block height
- `hash` (optional): Specific block hash
- `limit` (optional): Number of blocks (default: 10, max: 100)
- `offset` (optional): Pagination offset

**Response:**
```json
{
  "blocks": [
    {
      "hash": "00000000...",
      "height": 820145,
      "time": 1699891234,
      "tx_count": 2345,
      "size": 1234567,
      "weight": 3993456,
      "version": 536870912,
      "merkleroot": "abc123...",
      "nonce": 123456789,
      "bits": "170c4830",
      "difficulty": 62463471666300.73,
      "chainwork": "00000000...",
      "previousblockhash": "00000000..."
    }
  ],
  "total": 820145,
  "limit": 10,
  "offset": 0
}
```

### 3.4 GET /mempool
**Purpose:** Pending transactions in mempool

**Query Parameters:**
- `limit` (optional): Number of transactions (default: 100, max: 1000)
- `min_fee` (optional): Minimum fee rate (sat/vB)

**Response:**
```json
{
  "count": 12453,
  "size": 34567890,
  "total_fee": 12.34567890,
  "transactions": [
    {
      "txid": "abc123...",
      "size": 225,
      "vsize": 144,
      "fee": 0.00001440,
      "fee_rate": 10.0,
      "time": 1699891234,
      "inputs": 2,
      "outputs": 2,
      "value": 0.12345678
    }
  ],
  "fee_histogram": {
    "1-5": 1234,
    "5-10": 2345,
    "10-20": 3456,
    "20-50": 4567,
    "50+": 851
  }
}
```

### 3.5 GET /api/v1/algebra/network-graph
**Purpose:** Network topology and transaction graph visualization

**Query Parameters:**
- `type` (optional): Graph type (`peers`, `transactions`, `addresses`)
- `depth` (optional): Graph depth (default: 2, max: 5)
- `center` (optional): Center node (address, txid, or peer)

**Response:**
```json
{
  "graph": {
    "nodes": [
      {
        "id": "node_1",
        "type": "address|transaction|peer",
        "label": "bc1q...",
        "properties": {
          "balance": 1.23456789,
          "tx_count": 45,
          "first_seen": 1699891234
        }
      }
    ],
    "edges": [
      {
        "id": "edge_1",
        "source": "node_1",
        "target": "node_2",
        "type": "payment|peer_connection",
        "weight": 1.5,
        "properties": {
          "amount": 0.123,
          "timestamp": 1699891234
        }
      }
    ],
    "metadata": {
      "node_count": 150,
      "edge_count": 287,
      "depth": 2,
      "generated_at": "2025-11-13T12:34:56Z"
    }
  }
}
```

---

## 4. CRYPTOGRAPHY IMPLEMENTATION

### 4.1 SHA256 Double Hashing (Bitcoin Standard)

All Bitcoin operations use double SHA256:
```python
def sha256d(data: bytes) -> bytes:
    """Bitcoin's double SHA256 hash"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
```

**Applications:**
1. Block hash calculation
2. Transaction ID generation
3. Merkle tree construction
4. Proof of work verification

### 4.2 ECDSA (secp256k1)

Elliptic curve cryptography for:
1. Private key generation
2. Public key derivation
3. Transaction signing
4. Signature verification

### 4.3 HD Wallet (BIP32/39/44)

Hierarchical deterministic wallet support:
- **BIP39**: Mnemonic seed phrases
- **BIP32**: Key derivation
- **BIP44**: Multi-account hierarchy

---

## 5. DATABASE SCHEMAS

### 5.1 PostgreSQL (Blockchain Index)

```sql
-- Blocks table
CREATE TABLE blocks (
    height BIGINT PRIMARY KEY,
    hash VARCHAR(64) UNIQUE NOT NULL,
    version INTEGER,
    merkleroot VARCHAR(64),
    time TIMESTAMP,
    nonce BIGINT,
    bits VARCHAR(8),
    difficulty DOUBLE PRECISION,
    tx_count INTEGER,
    size BIGINT,
    weight BIGINT,
    previousblockhash VARCHAR(64),
    chainwork VARCHAR(64)
);

-- Transactions table
CREATE TABLE transactions (
    txid VARCHAR(64) PRIMARY KEY,
    hash VARCHAR(64),
    version INTEGER,
    size INTEGER,
    vsize INTEGER,
    weight INTEGER,
    locktime BIGINT,
    blockhash VARCHAR(64),
    blockheight BIGINT,
    time TIMESTAMP,
    blocktime TIMESTAMP,
    confirmations INTEGER,
    hex TEXT,
    FOREIGN KEY (blockhash) REFERENCES blocks(hash)
);

-- Transaction inputs
CREATE TABLE tx_inputs (
    id SERIAL PRIMARY KEY,
    txid VARCHAR(64),
    vout_index INTEGER,
    prev_txid VARCHAR(64),
    prev_vout INTEGER,
    scriptSig TEXT,
    sequence BIGINT,
    witness TEXT[],
    FOREIGN KEY (txid) REFERENCES transactions(txid)
);

-- Transaction outputs
CREATE TABLE tx_outputs (
    id SERIAL PRIMARY KEY,
    txid VARCHAR(64),
    vout_index INTEGER,
    value BIGINT, -- in satoshis
    scriptPubKey TEXT,
    address VARCHAR(64),
    type VARCHAR(20),
    spent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (txid) REFERENCES transactions(txid)
);

-- Addresses
CREATE TABLE addresses (
    address VARCHAR(64) PRIMARY KEY,
    type VARCHAR(20),
    balance BIGINT,
    tx_count INTEGER,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_blocks_hash ON blocks(hash);
CREATE INDEX idx_blocks_time ON blocks(time);
CREATE INDEX idx_tx_blockhash ON transactions(blockhash);
CREATE INDEX idx_tx_time ON transactions(time);
CREATE INDEX idx_tx_inputs_txid ON tx_inputs(txid);
CREATE INDEX idx_tx_inputs_prev ON tx_inputs(prev_txid, prev_vout);
CREATE INDEX idx_tx_outputs_txid ON tx_outputs(txid);
CREATE INDEX idx_tx_outputs_address ON tx_outputs(address);
CREATE INDEX idx_addresses_balance ON addresses(balance);
```

### 5.2 Redis (Cache)

**Key patterns:**
```
block:{height} → Block data
block:{hash} → Block data
tx:{txid} → Transaction data
mempool:all → List of mempool txids
mempool:tx:{txid} → Mempool transaction
address:{addr}:balance → Address balance
address:{addr}:txs → Address transactions
status:node → Node status
status:system → System health
```

### 5.3 Neo4j (Graph Database)

**Node types:**
- Address
- Transaction
- Block
- Peer

**Relationship types:**
- PAYS_TO
- RECEIVED_FROM
- INCLUDED_IN (tx → block)
- CONNECTS_TO (peer → peer)
- CLUSTERS_WITH (address → address)

---

## 6. SECURITY ARCHITECTURE

### 6.1 Authentication & Authorization
- JWT tokens for API access
- API key management
- Role-based access control (RBAC)
- Rate limiting per user/IP

### 6.2 Wallet Security
- AES-256 encryption for private keys
- Hardware Security Module (HSM) support
- Multi-signature wallets
- Cold storage integration

### 6.3 Network Security
- TLS/SSL for all API endpoints
- DDoS protection
- Input validation and sanitization
- SQL injection prevention

---

## 7. DEPLOYMENT ARCHITECTURE

### 7.1 Docker Compose (Development)
```yaml
services:
  bitcoin-node:
    image: bitcoin/bitcoin:26.0
    volumes:
      - bitcoin-data:/data
    ports:
      - "8332:8332"  # RPC
      - "8333:8333"  # P2P

  api-server:
    build: ./api
    depends_on:
      - bitcoin-node
      - postgres
      - redis
    ports:
      - "8000:8000"

  postgres:
    image: timescale/timescaledb:latest-pg15
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

  neo4j:
    image: neo4j:5
    volumes:
      - neo4j-data:/data
```

### 7.2 Kubernetes (Production)
- Multi-pod deployment
- Horizontal pod autoscaling
- Persistent volumes for blockchain data
- Service mesh for inter-service communication

---

## 8. MONITORING & OBSERVABILITY

### 8.1 Metrics (Prometheus)
- Node sync status
- API request rates
- Database query performance
- Mempool size
- Network peer count

### 8.2 Logging (ELK Stack)
- Structured JSON logs
- Application logs
- Bitcoin Core logs
- Access logs

### 8.3 Alerting
- Node out of sync
- High error rates
- Database connection issues
- Disk space low
- Unusual network activity

---

## 9. PERFORMANCE TARGETS

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| API Response Time (p95) | <100ms | <500ms |
| Node Uptime | >99.9% | >99% |
| Blockchain Sync Lag | <1 min | <10 min |
| Database Query Time | <50ms | <200ms |
| Throughput | 1000 req/s | 100 req/s |

---

## 10. DISASTER RECOVERY

### 10.1 Backup Strategy
- Daily PostgreSQL backups
- Real-time Redis snapshots
- Bitcoin blockchain: multiple copies
- Configuration backups

### 10.2 Recovery Procedures
- RPO (Recovery Point Objective): <1 hour
- RTO (Recovery Time Objective): <4 hours
- Automated failover for critical services
- Hot standby Bitcoin nodes

---

## CONCLUSION

This architecture provides a robust, scalable, and secure foundation for Bitcoin mainnet operations. The modular design allows for easy extension and maintenance while the comprehensive API layer enables diverse use cases from simple status checks to complex network analysis.

**Next Steps:**
1. Implement core Bitcoin node integration
2. Build API endpoints
3. Deploy database schemas
4. Test end-to-end functionality
5. Launch production system
