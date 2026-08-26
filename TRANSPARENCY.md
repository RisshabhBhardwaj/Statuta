# Transparency log

Statuta provides a metadata-only, append-only Merkle-log primitive. Leaves may include a keyed commitment to an opaque caller-supplied reference, but must never include plate values, images, precise locations, names, free-text narratives, or raw hashes of low-entropy identifiers.

The implementation uses RFC 6962 domain separation (`0x00` leaves; `0x01` internal nodes), HMAC-SHA-256 commitments scoped to a rotating epoch, and a dependency-free inclusion-proof verifier.

Limitations: a log proves only that an evaluation was logged. It does not prove that its input was truthful, that its verdict was obeyed, or that off-system activity did not occur. Without an independent witness, an operator can still present different log views to different audiences. A blockchain does not cure these limitations.
