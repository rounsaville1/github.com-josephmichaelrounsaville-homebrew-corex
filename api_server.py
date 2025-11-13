"""
R-COREX Bitcoin Mainnet API Server
FastAPI-based REST API for Bitcoin Core operations

Author: Joseph Michael Rounsaville
System: Unified Bitcoin Infrastructure

Available Endpoints:
  GET  /status
  GET  /transaction/<tx_hash>
  GET  /api/v1/algebra/network-graph
  GET  /blocks
  GET  /mempool
"""

import os
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from datetime import datetime
import uvicorn

# Import our Bitcoin modules
from modules.bitcoin_core.rpc import BitcoinRPC
from modules.bitcoin_core.node import BitcoinNode
from modules.crypto.sha256 import sha256d


# Initialize FastAPI app
app = FastAPI(
    title="R-COREX Bitcoin Mainnet API",
    description="Unified Bitcoin Infrastructure with full mainnet operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Bitcoin Core connection
# These should come from environment variables in production
RPC_HOST = os.getenv("BITCOIN_RPC_HOST", "127.0.0.1")
RPC_PORT = int(os.getenv("BITCOIN_RPC_PORT", "8332"))
RPC_USER = os.getenv("BITCOIN_RPC_USER", "bitcoin")
RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD", "bitcoin")

# Global RPC client and node manager
rpc_client = None
bitcoin_node = None


@app.on_event("startup")
async def startup_event():
    """Initialize Bitcoin Core connection on startup."""
    global rpc_client, bitcoin_node

    try:
        # Initialize RPC client
        rpc_client = BitcoinRPC(
            host=RPC_HOST,
            port=RPC_PORT,
            rpc_user=RPC_USER,
            rpc_password=RPC_PASSWORD,
        )

        # Initialize node manager
        bitcoin_node = BitcoinNode(rpc_client)

        # Test connection
        if rpc_client.is_connected():
            info = rpc_client.getblockchaininfo()
            print(f"✓ Connected to Bitcoin Core")
            print(f"  Chain: {info['chain']}")
            print(f"  Blocks: {info['blocks']}")
            print(f"  Sync: {info['verificationprogress']:.2%}")
        else:
            print("✗ Warning: Could not connect to Bitcoin Core")

    except Exception as e:
        print(f"✗ Error initializing Bitcoin Core connection: {e}")
        print("  API will start but some endpoints may fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("Shutting down API server...")


# Health check endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint - API health check."""
    return {
        "service": "R-COREX Bitcoin Mainnet API",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "GET /status",
            "GET /transaction/{tx_hash}",
            "GET /blocks",
            "GET /mempool",
            "GET /api/v1/algebra/network-graph",
        ],
    }


@app.get("/status", tags=["Node"])
async def get_status():
    """
    Get Bitcoin node status and health information.

    Returns comprehensive status including:
    - Node information (version, uptime, connections)
    - Blockchain sync status
    - Mempool statistics
    - System health
    """
    if not bitcoin_node:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin Core connection not initialized"
        )

    try:
        status = bitcoin_node.get_status()
        return JSONResponse(content=status)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get node status: {str(e)}"
        )


@app.get("/transaction/{tx_hash}", tags=["Transactions"])
async def get_transaction(
    tx_hash: str = Path(..., description="Transaction hash (64 hex characters)", min_length=64, max_length=64)
):
    """
    Get detailed transaction information by hash.

    Includes:
    - Transaction inputs and outputs
    - Block confirmation information
    - Fee analysis
    - Transaction type detection
    """
    if not bitcoin_node:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin Core connection not initialized"
        )

    try:
        # Validate transaction hash format
        if not all(c in "0123456789abcdefABCDEF" for c in tx_hash):
            raise HTTPException(
                status_code=400,
                detail="Invalid transaction hash format (must be 64 hex characters)"
            )

        tx = bitcoin_node.get_transaction(tx_hash)
        return JSONResponse(content=tx)

    except HTTPException:
        raise
    except Exception as e:
        # Check if transaction not found
        if "No such mempool or blockchain transaction" in str(e):
            raise HTTPException(
                status_code=404,
                detail=f"Transaction not found: {tx_hash}"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction: {str(e)}"
        )


@app.get("/blocks", tags=["Blockchain"])
async def get_blocks(
    height: Optional[int] = Query(None, description="Specific block height"),
    hash: Optional[str] = Query(None, description="Specific block hash"),
    limit: int = Query(10, description="Number of blocks to return", ge=1, le=100),
    offset: int = Query(0, description="Pagination offset", ge=0),
):
    """
    Get block data and history.

    Query Parameters:
    - height: Get specific block by height
    - hash: Get specific block by hash
    - limit: Number of blocks to return (default: 10, max: 100)
    - offset: Pagination offset (default: 0)

    Returns paginated block data with full block details.
    """
    if not bitcoin_node:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin Core connection not initialized"
        )

    try:
        blocks = bitcoin_node.get_blocks(
            height=height,
            block_hash=hash,
            limit=limit,
            offset=offset,
        )
        return JSONResponse(content=blocks)

    except Exception as e:
        if "Block not found" in str(e) or "Block height out of range" in str(e):
            raise HTTPException(
                status_code=404,
                detail="Block not found"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get blocks: {str(e)}"
        )


@app.get("/mempool", tags=["Mempool"])
async def get_mempool(
    limit: int = Query(100, description="Maximum number of transactions", ge=1, le=1000),
    min_fee: Optional[float] = Query(None, description="Minimum fee rate in sat/vB", ge=0),
):
    """
    Get pending transactions in mempool.

    Query Parameters:
    - limit: Maximum transactions to return (default: 100, max: 1000)
    - min_fee: Filter by minimum fee rate in sat/vB

    Returns:
    - Transaction list with fee analysis
    - Fee rate histogram
    - Mempool statistics
    """
    if not bitcoin_node:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin Core connection not initialized"
        )

    try:
        mempool = bitcoin_node.get_mempool(limit=limit, min_fee=min_fee)
        return JSONResponse(content=mempool)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get mempool: {str(e)}"
        )


@app.get("/api/v1/algebra/network-graph", tags=["Network"])
async def get_network_graph(
    graph_type: str = Query("peers", description="Graph type: peers, transactions, addresses"),
    depth: int = Query(2, description="Graph traversal depth", ge=1, le=5),
    center: Optional[str] = Query(None, description="Center node (address, txid, or peer)"),
):
    """
    Get network topology and transaction graph visualization.

    This endpoint provides graph data for visualizing:
    - Peer-to-peer network topology
    - Transaction relationships
    - Address clustering and relationships

    Query Parameters:
    - type: Graph type (peers, transactions, addresses)
    - depth: How many hops to traverse (1-5)
    - center: Starting point for graph traversal

    Returns graph data in nodes/edges format suitable for visualization.
    """
    if not rpc_client:
        raise HTTPException(
            status_code=503,
            detail="Bitcoin Core connection not initialized"
        )

    try:
        if graph_type == "peers":
            # Generate peer network graph
            peers = rpc_client.getpeerinfo()

            nodes = []
            edges = []

            for i, peer in enumerate(peers):
                nodes.append({
                    "id": f"peer_{i}",
                    "type": "peer",
                    "label": peer.get("addr", "Unknown"),
                    "properties": {
                        "version": peer.get("version"),
                        "subver": peer.get("subver"),
                        "inbound": peer.get("inbound", False),
                        "connection_time": peer.get("conntime"),
                        "bytes_sent": peer.get("bytessent", 0),
                        "bytes_recv": peer.get("bytesrecv", 0),
                    },
                })

                # Create edge from local node to peer
                edges.append({
                    "id": f"edge_{i}",
                    "source": "local_node",
                    "target": f"peer_{i}",
                    "type": "peer_connection",
                    "weight": 1.0,
                })

            # Add local node
            nodes.insert(0, {
                "id": "local_node",
                "type": "local",
                "label": "Local Node",
                "properties": {},
            })

            return JSONResponse(content={
                "graph": {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "node_count": len(nodes),
                        "edge_count": len(edges),
                        "depth": 1,
                        "type": "peers",
                        "generated_at": datetime.now().isoformat(),
                    },
                },
            })

        elif graph_type == "transactions":
            # For transaction graphs, we need a center transaction
            if not center:
                raise HTTPException(
                    status_code=400,
                    detail="Center transaction required for transaction graph"
                )

            # Get the center transaction
            tx = rpc_client.getrawtransaction(center, verbose=True)

            nodes = [{
                "id": center,
                "type": "transaction",
                "label": center[:8] + "...",
                "properties": {
                    "confirmations": tx.get("confirmations", 0),
                    "time": tx.get("time"),
                    "size": tx.get("size"),
                },
            }]

            edges = []

            # Add input transactions
            for vin in tx.get("vin", []):
                if "txid" in vin:
                    input_txid = vin["txid"]
                    nodes.append({
                        "id": input_txid,
                        "type": "transaction",
                        "label": input_txid[:8] + "...",
                        "properties": {},
                    })
                    edges.append({
                        "id": f"edge_in_{input_txid}",
                        "source": input_txid,
                        "target": center,
                        "type": "payment",
                        "weight": 1.0,
                    })

            return JSONResponse(content={
                "graph": {
                    "nodes": nodes,
                    "edges": edges,
                    "metadata": {
                        "node_count": len(nodes),
                        "edge_count": len(edges),
                        "depth": depth,
                        "type": "transactions",
                        "center": center,
                        "generated_at": datetime.now().isoformat(),
                    },
                },
            })

        elif graph_type == "addresses":
            # Address graph would require blockchain indexing
            # Simplified version for now
            return JSONResponse(content={
                "graph": {
                    "nodes": [],
                    "edges": [],
                    "metadata": {
                        "node_count": 0,
                        "edge_count": 0,
                        "depth": depth,
                        "type": "addresses",
                        "note": "Address graphs require full blockchain indexing",
                        "generated_at": datetime.now().isoformat(),
                    },
                },
            })

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid graph type: {graph_type}. Must be: peers, transactions, or addresses"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate network graph: {str(e)}"
        )


# Additional utility endpoints

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        if rpc_client and rpc_client.is_connected():
            return {
                "status": "healthy",
                "bitcoin_core": "connected",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "bitcoin_core": "disconnected",
                    "timestamp": datetime.now().isoformat(),
                },
            )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


@app.get("/version", tags=["System"])
async def get_version():
    """Get API and Bitcoin Core version information."""
    try:
        if rpc_client:
            network_info = rpc_client.getnetworkinfo()
            blockchain_info = rpc_client.getblockchaininfo()

            return {
                "api_version": "1.0.0",
                "bitcoin_core": {
                    "version": network_info.get("version"),
                    "subversion": network_info.get("subversion"),
                    "protocol_version": network_info.get("protocolversion"),
                    "chain": blockchain_info.get("chain"),
                },
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {
                "api_version": "1.0.0",
                "bitcoin_core": "not connected",
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get version info: {str(e)}"
        )


# Run the server
if __name__ == "__main__":
    print("=" * 60)
    print("R-COREX Bitcoin Mainnet API Server")
    print("=" * 60)
    print(f"Starting server...")
    print(f"Bitcoin RPC: {RPC_HOST}:{RPC_PORT}")
    print(f"API Documentation: http://0.0.0.0:8000/docs")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
