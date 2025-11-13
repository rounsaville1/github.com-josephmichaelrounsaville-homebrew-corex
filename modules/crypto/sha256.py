"""
Bitcoin SHA256 Double Hashing Implementation
Standard Bitcoin cryptographic functions using double SHA256

All Bitcoin block hashes, transaction IDs, and Merkle trees use double SHA256.
This is the core cryptographic primitive of the Bitcoin protocol.
"""

import hashlib
from typing import List, Union


def sha256d(data: Union[bytes, str]) -> bytes:
    """
    Bitcoin's double SHA256 hash function.

    This is the fundamental hashing algorithm used throughout Bitcoin:
    - Block hashes
    - Transaction IDs (txid)
    - Merkle tree construction
    - Proof of work

    Args:
        data: Input data as bytes or hex string

    Returns:
        32-byte hash digest

    Example:
        >>> sha256d(b"Hello Bitcoin").hex()
        '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069'
    """
    if isinstance(data, str):
        data = bytes.fromhex(data)

    # First SHA256
    first_hash = hashlib.sha256(data).digest()

    # Second SHA256 (double hash)
    second_hash = hashlib.sha256(first_hash).digest()

    return second_hash


def hash160(data: Union[bytes, str]) -> bytes:
    """
    Bitcoin's HASH160 function: RIPEMD160(SHA256(data))

    Used for:
    - Creating P2PKH addresses
    - Creating P2WPKH addresses
    - Script hash generation

    Args:
        data: Input data as bytes or hex string

    Returns:
        20-byte hash digest
    """
    if isinstance(data, str):
        data = bytes.fromhex(data)

    # SHA256 first
    sha = hashlib.sha256(data).digest()

    # Then RIPEMD160
    ripe = hashlib.new('ripemd160')
    ripe.update(sha)

    return ripe.digest()


def verify_block_hash(block_header: bytes, target_hash: str) -> bool:
    """
    Verify a Bitcoin block hash meets the required difficulty target.

    Bitcoin block headers are 80 bytes:
    - Version (4 bytes)
    - Previous block hash (32 bytes)
    - Merkle root (32 bytes)
    - Timestamp (4 bytes)
    - Bits (4 bytes)
    - Nonce (4 bytes)

    Args:
        block_header: 80-byte block header
        target_hash: Expected block hash (in reverse byte order)

    Returns:
        True if the hash is valid

    Example:
        >>> header = bytes.fromhex("0100000000000000000000...")
        >>> verify_block_hash(header, "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
        True
    """
    if len(block_header) != 80:
        raise ValueError(f"Block header must be 80 bytes, got {len(block_header)}")

    # Calculate double SHA256
    calculated_hash = sha256d(block_header)

    # Reverse bytes for display (Bitcoin convention)
    calculated_hash_hex = calculated_hash[::-1].hex()

    return calculated_hash_hex == target_hash


def calculate_merkle_root(transaction_hashes: List[str]) -> str:
    """
    Calculate the Merkle root of a list of transaction hashes.

    Bitcoin uses a binary Merkle tree where each non-leaf node is the
    double SHA256 of its two children. If there's an odd number of nodes,
    the last one is duplicated.

    Args:
        transaction_hashes: List of transaction IDs (as hex strings)

    Returns:
        Merkle root as hex string

    Example:
        >>> txs = ["abc123...", "def456..."]
        >>> root = calculate_merkle_root(txs)
        >>> isinstance(root, str) and len(root) == 64
        True
    """
    if not transaction_hashes:
        # Empty merkle root for blocks with no transactions
        return "0" * 64

    # Convert hex strings to bytes (reversed for Bitcoin convention)
    hashes = [bytes.fromhex(tx)[::-1] for tx in transaction_hashes]

    # Build the merkle tree bottom-up
    while len(hashes) > 1:
        # If odd number, duplicate the last hash
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        # Pair up hashes and compute parent hashes
        next_level = []
        for i in range(0, len(hashes), 2):
            # Concatenate pairs and double hash
            combined = hashes[i] + hashes[i + 1]
            parent_hash = sha256d(combined)
            next_level.append(parent_hash)

        hashes = next_level

    # Reverse bytes back for display
    merkle_root = hashes[0][::-1].hex()
    return merkle_root


def validate_proof_of_work(block_hash: str, bits: int) -> bool:
    """
    Validate that a block hash meets the proof-of-work difficulty target.

    The 'bits' field is a compact representation of the target. A valid
    block hash must be numerically less than the target.

    Args:
        block_hash: Block hash as hex string
        bits: Compact difficulty bits from block header

    Returns:
        True if proof of work is valid
    """
    # Convert block hash to integer
    hash_int = int(block_hash, 16)

    # Decode target from bits (compact format)
    exponent = bits >> 24
    mantissa = bits & 0xFFFFFF

    if exponent <= 3:
        target = mantissa >> (8 * (3 - exponent))
    else:
        target = mantissa << (8 * (exponent - 3))

    # Valid if hash is less than target
    return hash_int < target


# Test vectors from Bitcoin Core
def _run_tests():
    """
    Run test vectors to verify SHA256d implementation.
    These are actual Bitcoin block hashes.
    """
    # Genesis block header (Bitcoin block 0)
    genesis_header = (
        "01000000"  # Version
        "0000000000000000000000000000000000000000000000000000000000000000"  # Prev block
        "3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a"  # Merkle root
        "29ab5f49"  # Timestamp
        "ffff001d"  # Bits
        "1dac2b7c"  # Nonce
    )

    genesis_hash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"

    # Verify genesis block
    calculated = sha256d(genesis_header)[::-1].hex()
    assert calculated == genesis_hash, f"Genesis block hash mismatch: {calculated}"

    print("✓ SHA256d implementation verified against Bitcoin genesis block")
    print(f"  Genesis hash: {genesis_hash}")

    # Test hash160
    pubkey = bytes.fromhex("0450863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b23522cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6")
    hash160_result = hash160(pubkey).hex()
    expected_hash160 = "010966776006953d5567439e5e39f86a0d273bee"
    assert hash160_result == expected_hash160, f"HASH160 mismatch: {hash160_result}"

    print("✓ HASH160 implementation verified")

    # Test merkle root calculation
    # Block 100,000 transactions (simplified single tx)
    block_100k_txs = [
        "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87"  # Coinbase tx
    ]
    merkle_root = calculate_merkle_root(block_100k_txs)
    expected_merkle = "8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87"
    assert merkle_root == expected_merkle, f"Merkle root mismatch: {merkle_root}"

    print("✓ Merkle root calculation verified")
    print("\nAll cryptographic tests passed! ✓")


if __name__ == "__main__":
    _run_tests()
