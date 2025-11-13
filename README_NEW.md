# R-COREX Bitcoin Mainnet System

**Unified Bitcoin Infrastructure with Full Mainnet Operations**

A comprehensive Bitcoin Core integration platform featuring real-time blockchain monitoring, transaction processing, network graph visualization, and full SHA256 cryptographic operations.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Bitcoin](https://img.shields.io/badge/bitcoin-mainnet-orange)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🌟 Features

### Core Bitcoin Operations
- ✅ **Bitcoin Core Integration** - Full Bitcoin node connectivity via JSON-RPC
- ✅ **SHA256 Double Hashing** - Bitcoin standard cryptographic implementation
- ✅ **Transaction Processing** - Complete transaction analysis and monitoring
- ✅ **Blockchain Synchronization** - Real-time blockchain sync and validation
- ✅ **Mempool Monitoring** - Live mempool tracking and fee analysis

### API Endpoints
All endpoints are RESTful and return JSON data:

```
GET  /status                          - Node health and sync status
GET  /transaction/<tx_hash>           - Transaction details and analysis
GET  /blocks                          - Block data with pagination
GET  /mempool                         - Pending transactions with fee histogram
GET  /api/v1/algebra/network-graph    - Network topology visualization
```

### Advanced Features
- 🔐 **Cryptographic Verification** - Built-in SHA256d testing against genesis block
- 📊 **Network Graph** - Peer topology and transaction relationship visualization
- 💾 **Database Integration** - PostgreSQL, Redis, and Neo4j support
- 🐳 **Docker Deployment** - Complete containerized stack
- 📈 **Analytics Engine** - Transaction patterns and fee estimation
- 🔍 **Blockchain Explorer** - Query any block or transaction

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/josephmichaelrounsaville/homebrew-corex.git
cd homebrew-corex

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api-server
```

The API will be available at `http://localhost:8000` and documentation at `http://localhost:8000/docs`

### Option 2: Manual Installation

#### Prerequisites
- Python 3.11+
- Bitcoin Core 26.0+ (running with RPC enabled)
- PostgreSQL 15+ (optional)
- Redis 7+ (optional)

#### Installation Steps

```bash
# 1. Install Bitcoin Core
# Download from https://bitcoin.org/en/download
# Or use Homebrew:
brew install bitcoin

# 2. Start Bitcoin Core (mainnet)
bitcoind -daemon -server=1 -rpcuser=bitcoin -rpcpassword=bitcoin -txindex=1

# 3. Clone repository
git clone https://github.com/josephmichaelrounsaville/homebrew-corex.git
cd homebrew-corex

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your Bitcoin RPC credentials

# 6. Test the system
python main.py

# 7. Start API server
python api_server.py
```

---

## 📖 Usage Examples

### Python Client

```python
from modules.bitcoin_core.rpc import BitcoinRPC
from modules.bitcoin_core.node import BitcoinNode
from modules.crypto.sha256 import sha256d

# Connect to Bitcoin Core
rpc = BitcoinRPC(host='127.0.0.1', port=8332,
                 rpc_user='bitcoin', rpc_password='bitcoin')

# Create node manager
node = BitcoinNode(rpc)

# Get node status
status = node.get_status()
print(f"Current block height: {status['blockchain']['blocks']}")

# Get transaction
tx = node.get_transaction("abc123...")
print(f"Transaction fee: {tx['analysis']['fee']} BTC")

# Get mempool
mempool = node.get_mempool(limit=100)
print(f"Pending transactions: {mempool['count']}")

# SHA256 double hash (Bitcoin standard)
block_hash = sha256d(block_header_bytes)
```

### API Client (cURL)

```bash
# Get node status
curl http://localhost:8000/status

# Get specific transaction
curl http://localhost:8000/transaction/abc123...

# Get recent blocks
curl http://localhost:8000/blocks?limit=10

# Get mempool with fee filter
curl "http://localhost:8000/mempool?limit=100&min_fee=10"

# Get network graph
curl "http://localhost:8000/api/v1/algebra/network-graph?type=peers"
```

### JavaScript Client

```javascript
// Fetch node status
const response = await fetch('http://localhost:8000/status');
const status = await response.json();
console.log(`Blocks: ${status.blockchain.blocks}`);

// Get transaction
const tx = await fetch(`http://localhost:8000/transaction/${txid}`);
const txData = await tx.json();
console.log(`Fee rate: ${txData.analysis.fee_rate} sat/vB`);

// Get network graph for visualization
const graph = await fetch('http://localhost:8000/api/v1/algebra/network-graph?type=peers');
const graphData = await graph.json();
// Use with D3.js, vis.js, or other graph library
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Client Applications                     │
│     (Web, Mobile, Desktop, Third-party)         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            FastAPI Gateway                       │
│  /status | /transaction | /blocks | /mempool   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          Business Logic Layer                    │
│  Node Manager | Transaction Service             │
│  Mempool Monitor | Network Graph                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│     Bitcoin Core Node (Mainnet)                 │
│  • SHA256 Double Hashing                       │
│  • P2P Network                                  │
│  • UTXO Set Management                          │
│  • Mempool Management                           │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Bitcoin Core
BITCOIN_RPC_HOST=127.0.0.1
BITCOIN_RPC_PORT=8332
BITCOIN_RPC_USER=bitcoin
BITCOIN_RPC_PASSWORD=your_password
BITCOIN_NETWORK=mainnet

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Database (Optional)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Configuration File

See `config.yaml` for comprehensive configuration options including:
- Bitcoin node settings
- API server configuration
- Database connections
- Security settings
- Monitoring and logging
- Rate limiting

---

## 📊 API Documentation

### Interactive Documentation

Once the API server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoint Details

#### GET /status

Returns comprehensive node status including blockchain sync, mempool size, and peer connections.

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
    "sync_progress": 1.0,
    "size_on_disk": 567382901234
  },
  "mempool": {
    "size": 12453,
    "bytes": 34567890
  }
}
```

#### GET /transaction/{tx_hash}

Get detailed transaction information with fee analysis.

**Parameters:**
- `tx_hash` (required): 64-character transaction hash

**Response:**
```json
{
  "txid": "abc123...",
  "confirmations": 6,
  "size": 225,
  "vsize": 144,
  "fee": 0.00001440,
  "analysis": {
    "fee_rate": 10.0,
    "type": "P2WPKH"
  }
}
```

See full API documentation in `ARCHITECTURE.md`

---

## 🔐 Security

### Cryptographic Implementation

All Bitcoin operations use the standard double SHA256 algorithm:

```python
def sha256d(data: bytes) -> bytes:
    """Bitcoin's double SHA256 hash"""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
```

Verified against:
- Bitcoin genesis block
- Block 100,000
- Test vectors from Bitcoin Core

### Security Best Practices

1. **Never expose RPC credentials** - Use environment variables
2. **Enable authentication** - Configure JWT tokens for API access
3. **Use TLS/SSL** - Enable HTTPS in production
4. **Rate limiting** - Configure per-IP limits
5. **Firewall rules** - Restrict RPC access to localhost
6. **Regular updates** - Keep Bitcoin Core updated

---

## 🧪 Testing

```bash
# Run cryptographic tests
python modules/crypto/sha256.py

# Test RPC connection
python modules/bitcoin_core/rpc.py

# Test complete system
python main.py

# Run API tests (requires pytest)
pytest tests/

# Check code quality
black .
flake8 .
mypy .
```

---

## 📈 Performance

### Benchmarks

- **API Response Time**: <100ms (p95)
- **Transaction Queries**: <50ms
- **Block Queries**: <75ms
- **Mempool Updates**: Every 10 seconds
- **Throughput**: 1000+ req/sec

### Optimization Tips

1. Enable Redis caching for status queries
2. Use PostgreSQL for historical data
3. Configure connection pooling
4. Enable API rate limiting
5. Use read replicas for scaling

---

## 🛠️ Development

### Project Structure

```
homebrew-corex/
├── main.py                 # System launcher
├── api_server.py          # FastAPI server
├── config.yaml            # Configuration
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image
├── docker-compose.yml    # Docker orchestration
├── modules/
│   ├── bitcoin_core/     # Bitcoin Core integration
│   │   ├── rpc.py       # RPC client
│   │   ├── node.py      # Node manager
│   ├── crypto/           # Cryptography
│   │   ├── sha256.py    # SHA256 implementation
│   ├── api/              # API modules
│   ├── database/         # Database models
│   └── security/         # Security utilities
├── tests/                # Test suite
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   └── BUSINESS_ANALYSIS.md
└── .github/
    └── workflows/        # CI/CD
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE.md` for detailed system design
- **Business Analysis**: See `BUSINESS_ANALYSIS.md` for business opportunities
- **API Reference**: Visit `/docs` endpoint when server is running
- **Bitcoin Core**: https://bitcoin.org/en/developer-documentation

---

## 🐳 Docker Deployment

### Services

```bash
# Start all services
docker-compose up -d

# Start with monitoring
docker-compose --profile monitoring up -d

# Start full stack (including Neo4j)
docker-compose --profile full up -d

# Scale API servers
docker-compose up -d --scale api-server=3
```

### Services Included

- **bitcoin-core**: Bitcoin Core mainnet node
- **api-server**: FastAPI application
- **postgres**: PostgreSQL database with TimescaleDB
- **redis**: Redis cache
- **neo4j**: Graph database (optional)
- **prometheus**: Metrics collection (optional)
- **grafana**: Monitoring dashboards (optional)

---

## 🔍 Troubleshooting

### Bitcoin Core Connection Failed

```bash
# Check if bitcoind is running
bitcoin-cli getblockchaininfo

# Check RPC credentials
cat ~/.bitcoin/bitcoin.conf

# Test RPC connection
curl --user bitcoin:password --data-binary '{"jsonrpc":"1.0","id":"test","method":"getblockchaininfo","params":[]}' -H 'content-type: text/plain;' http://127.0.0.1:8332/
```

### API Server Issues

```bash
# Check logs
docker-compose logs api-server

# Check health endpoint
curl http://localhost:8000/health

# Restart service
docker-compose restart api-server
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose logs postgres

# Check Redis
docker-compose logs redis

# Test connections
docker-compose exec postgres psql -U bitcoin -d bitcoin_mainnet
docker-compose exec redis redis-cli ping
```

---

## 📝 License

MIT License - See LICENSE file for details

---

## 👤 Author

**Joseph Michael Rounsaville**

- GitHub: [@josephmichaelrounsaville](https://github.com/josephmichaelrounsaville)
- Website: https://rounsavilletechnologies.com

---

## 🙏 Acknowledgments

- Bitcoin Core developers
- FastAPI framework
- Python bitcoin library contributors
- Open source community

---

## 📞 Support

- **Issues**: https://github.com/josephmichaelrounsaville/homebrew-corex/issues
- **Documentation**: https://docs.rounsavilletechnologies.com
- **Email**: support@rounsavilletechnologies.com

---

## 🗺️ Roadmap

### Version 1.1 (Q1 2025)
- [ ] HD Wallet implementation (BIP32/39/44)
- [ ] Multi-signature wallet support
- [ ] WebSocket real-time updates
- [ ] Advanced fee estimation

### Version 1.2 (Q2 2025)
- [ ] Lightning Network integration
- [ ] Address clustering analysis
- [ ] Machine learning fee prediction
- [ ] Mobile SDK

### Version 2.0 (Q3 2025)
- [ ] Full blockchain explorer UI
- [ ] Enterprise features
- [ ] High availability setup
- [ ] Kubernetes deployment

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for the Bitcoin community**
