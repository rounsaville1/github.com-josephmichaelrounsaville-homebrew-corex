"""
Bitcoin Core JSON-RPC Client
Communicates with Bitcoin Core node for mainnet operations
"""

import json
import requests
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin


class BitcoinRPC:
    """
    Bitcoin Core JSON-RPC client for mainnet operations.

    Connects to a running Bitcoin Core node and provides methods
    for querying blockchain data, transactions, mempool, and network info.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8332,
        rpc_user: str = "bitcoin",
        rpc_password: str = "bitcoin",
        timeout: int = 30,
    ):
        """
        Initialize Bitcoin RPC client.

        Args:
            host: Bitcoin Core RPC host
            port: Bitcoin Core RPC port (8332 for mainnet)
            rpc_user: RPC username
            rpc_password: RPC password
            timeout: Request timeout in seconds
        """
        self.url = f"http://{host}:{port}"
        self.auth = (rpc_user, rpc_password)
        self.timeout = timeout
        self.headers = {"content-type": "application/json"}
        self._request_id = 0

    def _call(self, method: str, params: Optional[List] = None) -> Any:
        """
        Make a JSON-RPC call to Bitcoin Core.

        Args:
            method: RPC method name
            params: Method parameters

        Returns:
            RPC response result

        Raises:
            Exception: If RPC call fails
        """
        self._request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or [],
        }

        try:
            response = requests.post(
                self.url,
                data=json.dumps(payload),
                headers=self.headers,
                auth=self.auth,
                timeout=self.timeout,
            )
            response.raise_for_status()

            result = response.json()

            if "error" in result and result["error"] is not None:
                raise Exception(
                    f"RPC Error: {result['error']['message']} (code: {result['error']['code']})"
                )

            return result.get("result")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Bitcoin Core: {e}")

    # Blockchain methods

    def getblockchaininfo(self) -> Dict[str, Any]:
        """Get blockchain information including sync status."""
        return self._call("getblockchaininfo")

    def getblockcount(self) -> int:
        """Get the current block height."""
        return self._call("getblockcount")

    def getblockhash(self, height: int) -> str:
        """Get block hash at specific height."""
        return self._call("getblockhash", [height])

    def getblock(self, block_hash: str, verbosity: int = 2) -> Dict[str, Any]:
        """
        Get block data.

        Args:
            block_hash: Block hash
            verbosity: 0=hex, 1=json, 2=json with tx details

        Returns:
            Block data
        """
        return self._call("getblock", [block_hash, verbosity])

    def getblockheader(self, block_hash: str, verbose: bool = True) -> Dict[str, Any]:
        """Get block header information."""
        return self._call("getblockheader", [block_hash, verbose])

    def getbestblockhash(self) -> str:
        """Get the hash of the best (tip) block."""
        return self._call("getbestblockhash")

    # Transaction methods

    def getrawtransaction(
        self, txid: str, verbose: bool = True, blockhash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get raw transaction data.

        Args:
            txid: Transaction ID
            verbose: If True, return JSON object instead of hex
            blockhash: Block hash to look in (optional)

        Returns:
            Transaction data
        """
        params = [txid, verbose]
        if blockhash:
            params.append(blockhash)
        return self._call("getrawtransaction", params)

    def gettransaction(self, txid: str) -> Dict[str, Any]:
        """Get detailed transaction information (wallet tx only)."""
        return self._call("gettransaction", [txid])

    def sendrawtransaction(self, hex_string: str) -> str:
        """
        Broadcast a raw transaction to the network.

        Args:
            hex_string: Signed transaction in hex

        Returns:
            Transaction ID
        """
        return self._call("sendrawtransaction", [hex_string])

    def decoderawtransaction(self, hex_string: str) -> Dict[str, Any]:
        """Decode a raw transaction hex into JSON."""
        return self._call("decoderawtransaction", [hex_string])

    # Mempool methods

    def getmempoolinfo(self) -> Dict[str, Any]:
        """Get mempool information."""
        return self._call("getmempoolinfo")

    def getrawmempool(self, verbose: bool = False) -> Any:
        """
        Get all transactions in mempool.

        Args:
            verbose: If True, return detailed info for each tx

        Returns:
            List of txids or dict of tx details
        """
        return self._call("getrawmempool", [verbose])

    def getmempoolentry(self, txid: str) -> Dict[str, Any]:
        """Get mempool entry for specific transaction."""
        return self._call("getmempoolentry", [txid])

    def getmempoolancestors(self, txid: str, verbose: bool = False) -> Any:
        """Get all in-mempool ancestors of a transaction."""
        return self._call("getmempoolancestors", [txid, verbose])

    def getmempooldescendants(self, txid: str, verbose: bool = False) -> Any:
        """Get all in-mempool descendants of a transaction."""
        return self._call("getmempooldescendants", [txid, verbose])

    # Network methods

    def getnetworkinfo(self) -> Dict[str, Any]:
        """Get network information."""
        return self._call("getnetworkinfo")

    def getpeerinfo(self) -> List[Dict[str, Any]]:
        """Get information about connected peers."""
        return self._call("getpeerinfo")

    def getconnectioncount(self) -> int:
        """Get number of connections to other nodes."""
        return self._call("getconnectioncount")

    def getnettotals(self) -> Dict[str, Any]:
        """Get network traffic information."""
        return self._call("getnettotals")

    # Mining methods

    def getmininginfo(self) -> Dict[str, Any]:
        """Get mining-related information."""
        return self._call("getmininginfo")

    def getdifficulty(self) -> float:
        """Get current mining difficulty."""
        return self._call("getdifficulty")

    # Utility methods

    def estimatesmartfee(self, conf_target: int) -> Dict[str, Any]:
        """
        Estimate fee for transaction confirmation in conf_target blocks.

        Args:
            conf_target: Number of blocks for confirmation

        Returns:
            Fee estimate in BTC/kB
        """
        return self._call("estimatesmartfee", [conf_target])

    def validateaddress(self, address: str) -> Dict[str, Any]:
        """Validate a Bitcoin address."""
        return self._call("validateaddress", [address])

    def getaddressinfo(self, address: str) -> Dict[str, Any]:
        """Get detailed information about an address."""
        return self._call("getaddressinfo", [address])

    def uptime(self) -> int:
        """Get node uptime in seconds."""
        return self._call("uptime")

    def ping(self) -> None:
        """Ping the node to keep connection alive."""
        return self._call("ping")

    # Blockchain analysis

    def getchaintips(self) -> List[Dict[str, Any]]:
        """Get information about all known chain tips."""
        return self._call("getchaintips")

    def getchaintxstats(
        self, nblocks: Optional[int] = None, blockhash: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics about the blockchain."""
        params = []
        if nblocks is not None:
            params.append(nblocks)
            if blockhash is not None:
                params.append(blockhash)
        return self._call("getchaintxstats", params if params else None)

    def getblockstats(self, hash_or_height: Any, stats: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get statistics for a given block."""
        params = [hash_or_height]
        if stats:
            params.append(stats)
        return self._call("getblockstats", params)

    # Health check

    def is_connected(self) -> bool:
        """
        Check if connection to Bitcoin Core is working.

        Returns:
            True if connected and responsive
        """
        try:
            self.getblockchaininfo()
            return True
        except Exception:
            return False

    def is_synced(self) -> bool:
        """
        Check if blockchain is fully synced.

        Returns:
            True if sync is complete
        """
        try:
            info = self.getblockchaininfo()
            return info.get("initialblockdownload", True) == False
        except Exception:
            return False


# Example usage and testing
if __name__ == "__main__":
    # This requires a running Bitcoin Core node
    # For testing purposes only

    rpc = BitcoinRPC(
        host="127.0.0.1",
        port=8332,
        rpc_user="bitcoin",
        rpc_password="bitcoin"
    )

    try:
        if rpc.is_connected():
            print("✓ Connected to Bitcoin Core")

            # Get blockchain info
            info = rpc.getblockchaininfo()
            print(f"✓ Chain: {info['chain']}")
            print(f"✓ Blocks: {info['blocks']}")
            print(f"✓ Headers: {info['headers']}")
            print(f"✓ Verification: {info['verificationprogress']:.2%}")

            # Get network info
            net_info = rpc.getnetworkinfo()
            print(f"✓ Version: {net_info['version']}")
            print(f"✓ Connections: {rpc.getconnectioncount()}")

            # Get mempool info
            mempool = rpc.getmempoolinfo()
            print(f"✓ Mempool size: {mempool['size']} transactions")
            print(f"✓ Mempool bytes: {mempool['bytes']:,} bytes")

        else:
            print("✗ Could not connect to Bitcoin Core")
            print("  Make sure bitcoind is running with RPC enabled")

    except Exception as e:
        print(f"✗ Error: {e}")
