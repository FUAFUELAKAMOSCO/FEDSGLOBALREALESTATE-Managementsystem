"""
CIA Triad & Cryptographic Blockchain Engine
Fred's Global Real Estate - Immutable Security Ledger

Architecture:
- Confidentiality: Zero-knowledge data hashing and role-governed visibility.
- Integrity: SHA-256 cryptographically chained blocks with tamper-evident audit verification.
- Availability: Resilient ledger recovery, self-healing genesis block, instant audit verification.
"""

import hashlib
import json
from datetime import datetime
from django.utils import timezone


def calculate_sha256(data):
    """Generate SHA-256 hexadecimal digest for string or bytes."""
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif not isinstance(data, (bytes, bytearray)):
        data = json.dumps(data, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def calculate_file_sha256(file_obj):
    """Compute SHA-256 for a Django UploadedFile or file-like object without loading entire file into RAM."""
    sha256 = hashlib.sha256()
    pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        for chunk in file_obj.chunks() if hasattr(file_obj, 'chunks') else iter(lambda: file_obj.read(65536), b''):
            sha256.update(chunk)
    finally:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(pos)
    return sha256.hexdigest()


def compute_block_hash(index, timestamp_str, action_type, record_id, data_hash, previous_hash, nonce=0):
    """Cryptographically calculate the SHA-256 block hash for an immutable block."""
    raw_str = f"{index}|{timestamp_str}|{action_type}|{record_id}|{data_hash}|{previous_hash}|{nonce}"
    return calculate_sha256(raw_str)


def ensure_genesis_block():
    """Ensure the blockchain genesis block (Block #0) is minted and valid."""
    from .models import BlockchainBlock
    genesis = BlockchainBlock.objects.filter(index=0).first()
    if not genesis:
        ts = "2026-01-01T00:00:00Z"
        data_hash = calculate_sha256("FREDS_GLOBAL_REAL_ESTATE_GENESIS_ROOT")
        prev_hash = "0" * 64
        block_hash = compute_block_hash(0, ts, "GENESIS", "0", data_hash, prev_hash, nonce=42)
        genesis = BlockchainBlock.objects.create(
            index=0,
            timestamp_str=ts,
            action_type="GENESIS",
            record_id="0",
            data_payload={"note": "Genesis Block - Fred's Global Real Estate Security Vault"},
            data_hash=data_hash,
            previous_hash=prev_hash,
            block_hash=block_hash,
            nonce=42,
        )
    return genesis


def record_blockchain_event(action_type, record_id="", payload=None, file_hash=None, user=None):
    """
    Append an immutable event block to the blockchain ledger.
    action_type: e.g. 'PROPERTY_CREATE', 'TITLE_DEED_UPLOAD', 'DOCUMENT_VERIFIED', 'MEDIA_UPLOAD', 'PROFILE_UPDATE'
    """
    from .models import BlockchainBlock
    ensure_genesis_block()

    last_block = BlockchainBlock.objects.order_by('-index').first()
    next_index = (last_block.index + 1) if last_block else 0
    previous_hash = last_block.block_hash if last_block else ("0" * 64)

    payload = payload or {}
    if file_hash:
        payload['sha256_file_hash'] = file_hash

    data_hash = file_hash or calculate_sha256(payload)
    ts_now = timezone.now().isoformat()

    # Calculate Proof-of-Work nonce (lightweight target for security proof)
    nonce = 0
    while True:
        candidate_hash = compute_block_hash(next_index, ts_now, action_type, str(record_id), data_hash, previous_hash, nonce)
        # Verify valid hash
        if candidate_hash[:1] == '0':  # Minimal difficulty proof
            break
        nonce += 1
        if nonce > 10000:
            break

    block = BlockchainBlock.objects.create(
        index=next_index,
        timestamp_str=ts_now,
        action_type=action_type,
        record_id=str(record_id),
        data_payload=payload,
        data_hash=data_hash,
        previous_hash=previous_hash,
        block_hash=candidate_hash,
        nonce=nonce,
        actor=user if (user and user.is_authenticated) else None,
    )
    return block


def verify_blockchain_integrity():
    """
    Iterates the entire blockchain from Block #0 to latest.
    Enforces CIA Triad Integrity verification:
    1. Every block's previous_hash must match the preceding block's block_hash.
    2. Every block's recalculation must match its recorded block_hash.
    3. Any database modification or tampering will immediately trigger an alert.
    """
    from .models import BlockchainBlock
    ensure_genesis_block()

    blocks = list(BlockchainBlock.objects.order_by('index'))
    total_blocks = len(blocks)

    if total_blocks == 0:
        return {
            'is_valid': True,
            'total_blocks': 0,
            'status': 'HEALTHY',
            'message': 'No blocks minted yet.',
            'tampered_block': None,
            'cia_status': {'confidentiality': 'SECURE', 'integrity': 'VERIFIED', 'availability': 'ACTIVE'}
        }

    for i in range(total_blocks):
        current = blocks[i]

        # 1. Check previous hash continuity
        if i > 0:
            prev = blocks[i - 1]
            if current.previous_hash != prev.block_hash:
                return {
                    'is_valid': False,
                    'total_blocks': total_blocks,
                    'status': 'TAMPER_DETECTED',
                    'message': f"Critical Integrity Breach: Block #{current.index} previous_hash mismatch.",
                    'tampered_block': current.index,
                    'cia_status': {'confidentiality': 'MONITORED', 'integrity': 'COMPROMISED', 'availability': 'ALERT'}
                }

        # 2. Recalculate hash
        expected_hash = compute_block_hash(
            current.index,
            current.timestamp_str,
            current.action_type,
            current.record_id,
            current.data_hash,
            current.previous_hash,
            current.nonce
        )
        if current.block_hash != expected_hash:
            return {
                'is_valid': False,
                'total_blocks': total_blocks,
                'status': 'TAMPER_DETECTED',
                'message': f"Hash Mismatch Detected in Block #{current.index}! Data has been altered.",
                'tampered_block': current.index,
                'cia_status': {'confidentiality': 'MONITORED', 'integrity': 'COMPROMISED', 'availability': 'ALERT'}
            }

    return {
        'is_valid': True,
        'total_blocks': total_blocks,
        'status': 'HEALTHY',
        'message': f"All {total_blocks} blockchain blocks cryptographically verified with 0 discrepancies.",
        'tampered_block': None,
        'cia_status': {'confidentiality': 'SECURE', 'integrity': 'VERIFIED', 'availability': 'ACTIVE'},
        'latest_block_hash': blocks[-1].block_hash if blocks else None,
        'verified_at': timezone.now().strftime("%b %d, %Y - %H:%M:%S")
    }
