"""
Bitcoin Node Manager
High-level interface for Bitcoin Core node operations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .rpc import BitcoinRPC


class BitcoinNode:
    """
    High-level Bitcoin node manager.

    Provides convenient methods for common Bitcoin operations,
    wrapping the lower-level RPC client.
    """

    def __init__(self, rpc: BitcoinRPC):
        """
        Initialize Bitcoin node manager.

        Args:
            rpc: Bitcoin RPC client instance
        """
        self.rpc = rpc
        self._status_cache = None
        self._cache_timestamp = None

    def get_status(self, use_cache: bool = True, cache_ttl: int = 5) -> Dict[str, Any]:
        """
        Get comprehensive node status.

        Args:
            use_cache: Whether to use cached status
            cache_ttl: Cache TTL in seconds

        Returns:
            Status dictionary with node, blockchain, mempool, and system info
        """
        # Check cache
        if use_cache and self._status_cache and self._cache_timestamp:
            age = (datetime.now() - self._cache_timestamp).total_seconds()
            if age < cache_ttl:
                return self._status_cache

        # Gather all status information
        try:
            blockchain_info = self.rpc.getblockchaininfo()
            network_info = self.rpc.getnetworkinfo()
            mempool_info = self.rpc.getmempoolinfo()
            peer_info = self.rpc.getpeerinfo()
            uptime = self.rpc.uptime()

            status = {
                "node": {
                    "version": network_info.get("version"),
                    "subversion": network_info.get("subversion"),
                    "network": blockchain_info.get("chain"),
                    "uptime": uptime,
                    "connections": len(peer_info),
                    "protocol_version": network_info.get("protocolversion"),
                },
                "blockchain": {
                    "blocks": blockchain_info.get("blocks"),
                    "headers": blockchain_info.get("headers"),
                    "bestblockhash": blockchain_info.get("bestblockhash"),
                    "difficulty": blockchain_info.get("difficulty"),
                    "mediantime": blockchain_info.get("mediantime"),
                    "sync_progress": blockchain_info.get("verificationprogress", 0),
                    "verification_progress": blockchain_info.get("verificationprogress", 0),
                    "size_on_disk": blockchain_info.get("size_on_disk"),
                    "pruned": blockchain_info.get("pruned", False),
                    "initial_block_download": blockchain_info.get("initialblockdownload", False),
                },
                "mempool": {
                    "size": mempool_info.get("size", 0),
                    "bytes": mempool_info.get("bytes", 0),
                    "usage": mempool_info.get("usage", 0),
                    "max_mempool": mempool_info.get("maxmempool", 0),
                    "mempool_min_fee": mempool_info.get("mempoolminfee", 0),
                },
                "system": {
                    "presence_verified": True,  # System is running
                    "modules_initialized": True,  # RPC connection works
                    "api_online": True,
                    "timestamp": datetime.now().isoformat(),
                },
            }

            # Cache the result
            self._status_cache = status
            self._cache_timestamp = datetime.now()

            return status

        except Exception as e:
            # Return error status
            return {
                "node": {"status": "error", "error": str(e)},
                "blockchain": {},
                "mempool": {},
                "system": {
                    "presence_verified": False,
                    "modules_initialized": False,
                    "api_online": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            }

    def get_transaction(self, txid: str) -> Dict[str, Any]:
        """
        Get detailed transaction information with analysis.

        Args:
            txid: Transaction ID

        Returns:
            Transaction data with additional analysis
        """
        try:
            # Get raw transaction
            tx = self.rpc.getrawtransaction(txid, verbose=True)

            # Calculate additional metrics
            total_input = 0
            total_output = sum(vout.get("value", 0) for vout in tx.get("vout", []))

            # For coinbase transactions, input is 0
            if not any(vin.get("coinbase") for vin in tx.get("vin", [])):
                # This would require looking up input transactions
                # Simplified for now
                pass

            # Calculate fee (if not coinbase)
            is_coinbase = any(vin.get("coinbase") for vin in tx.get("vin", []))
            fee = 0 if is_coinbase else tx.get("fee", 0)

            # Determine transaction type
            tx_type = "Unknown"
            if is_coinbase:
                tx_type = "Coinbase"
            elif tx.get("vout"):
                first_out = tx["vout"][0]
                script_type = first_out.get("scriptPubKey", {}).get("type", "")
                if "witness" in script_type:
                    tx_type = "P2WPKH" if "pubkeyhash" in script_type else "P2WSH"
                elif script_type == "pubkeyhash":
                    tx_type = "P2PKH"
                elif script_type == "scripthash":
                    tx_type = "P2SH"
                else:
                    tx_type = script_type

            # Add analysis
            tx["analysis"] = {
                "fee": fee,
                "fee_rate": (fee / (tx.get("vsize", 1))) if tx.get("vsize") else 0,
                "type": tx_type,
                "is_coinbase": is_coinbase,
                "total_output": total_output,
            }

            return tx

        except Exception as e:
            raise Exception(f"Failed to get transaction {txid}: {e}")

    def get_blocks(
        self,
        height: Optional[int] = None,
        block_hash: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Get block data with pagination.

        Args:
            height: Specific block height
            block_hash: Specific block hash
            limit: Number of blocks to return
            offset: Pagination offset

        Returns:
            Blocks data with pagination info
        """
        try:
            blocks = []

            if block_hash:
                # Get specific block by hash
                block = self.rpc.getblock(block_hash, verbosity=1)
                blocks.append(self._format_block(block))

            elif height is not None:
                # Get specific block by height
                bhash = self.rpc.getblockhash(height)
                block = self.rpc.getblock(bhash, verbosity=1)
                blocks.append(self._format_block(block))

            else:
                # Get recent blocks with pagination
                current_height = self.rpc.getblockcount()
                start_height = max(0, current_height - offset)
                end_height = max(0, start_height - limit)

                for h in range(start_height, end_height, -1):
                    bhash = self.rpc.getblockhash(h)
                    block = self.rpc.getblock(bhash, verbosity=1)
                    blocks.append(self._format_block(block))

            return {
                "blocks": blocks,
                "total": self.rpc.getblockcount(),
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            raise Exception(f"Failed to get blocks: {e}")

    def get_mempool(
        self, limit: int = 100, min_fee: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get mempool transactions.

        Args:
            limit: Maximum number of transactions to return
            min_fee: Minimum fee rate in sat/vB

        Returns:
            Mempool data with transactions
        """
        try:
            # Get mempool info
            mempool_info = self.rpc.getmempoolinfo()

            # Get all mempool transactions
            mempool_txids = self.rpc.getrawmempool(verbose=False)

            # Get detailed info for transactions (up to limit)
            transactions = []
            fee_histogram = {
                "1-5": 0,
                "5-10": 0,
                "10-20": 0,
                "20-50": 0,
                "50+": 0,
            }

            for txid in mempool_txids[:limit]:
                try:
                    entry = self.rpc.getmempoolentry(txid)

                    # Calculate fee rate in sat/vB
                    fee_btc = entry.get("fees", {}).get("base", 0)
                    fee_sat = int(fee_btc * 100_000_000)
                    vsize = entry.get("vsize", 1)
                    fee_rate = fee_sat / vsize

                    # Skip if below minimum fee
                    if min_fee and fee_rate < min_fee:
                        continue

                    # Update histogram
                    if fee_rate < 5:
                        fee_histogram["1-5"] += 1
                    elif fee_rate < 10:
                        fee_histogram["5-10"] += 1
                    elif fee_rate < 20:
                        fee_histogram["10-20"] += 1
                    elif fee_rate < 50:
                        fee_histogram["20-50"] += 1
                    else:
                        fee_histogram["50+"] += 1

                    transactions.append({
                        "txid": txid,
                        "size": entry.get("size", 0),
                        "vsize": vsize,
                        "fee": fee_btc,
                        "fee_rate": round(fee_rate, 2),
                        "time": entry.get("time", 0),
                        "height": entry.get("height", 0),
                    })

                except Exception:
                    # Skip transactions we can't get info for
                    continue

            # Calculate total fees
            total_fee = sum(tx["fee"] for tx in transactions)

            return {
                "count": mempool_info.get("size", 0),
                "size": mempool_info.get("bytes", 0),
                "total_fee": total_fee,
                "transactions": transactions,
                "fee_histogram": fee_histogram,
            }

        except Exception as e:
            raise Exception(f"Failed to get mempool: {e}")

    def _format_block(self, block: Dict[str, Any]) -> Dict[str, Any]:
        """Format block data for API response."""
        return {
            "hash": block.get("hash"),
            "height": block.get("height"),
            "time": block.get("time"),
            "tx_count": len(block.get("tx", [])),
            "size": block.get("size"),
            "weight": block.get("weight"),
            "version": block.get("version"),
            "merkleroot": block.get("merkleroot"),
            "nonce": block.get("nonce"),
            "bits": block.get("bits"),
            "difficulty": block.get("difficulty"),
            "chainwork": block.get("chainwork"),
            "previousblockhash": block.get("previousblockhash"),
            "nextblockhash": block.get("nextblockhash"),
        }
