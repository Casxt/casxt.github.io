#!/usr/bin/env python3
"""VSA educational forward pass; Python 3 standard library only.

Single batch/head, one video region, no prefix/coarse branch/GPU kernel.
Original implementation for the accompanying article, 2026-10-23.
This checks mathematical/indexing relationships, not GPU performance.
"""
import math
import random


def partition(grid, tile):
    """Return original indices per 3-D block; x is the fastest axis."""
    nt, ny, nx = grid
    bt, by, bx = tile
    blocks = []
    for t0 in range(0, nt, bt):
        for y0 in range(0, ny, by):
            for x0 in range(0, nx, bx):
                blocks.append([
                    t * ny * nx + y * nx + x
                    for t in range(t0, min(t0 + bt, nt))
                    for y in range(y0, min(y0 + by, ny))
                    for x in range(x0, min(x0 + bx, nx))
                ])
    return blocks


def pack(x, blocks, capacity):
    d = len(x[0])
    return [[x[a][:] for a in block] +
            [[0.0] * d for _ in range(capacity - len(block))]
            for block in blocks]


def pool(x, sizes):
    return [[sum(row[c] for row in block[:n]) / n
             for c in range(len(block[0]))]
            for block, n in zip(x, sizes)]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def route(qmean, kmean, keep):
    scale = 1 / math.sqrt(len(qmean[0]))
    # Tie-break by block id for deterministic teaching output.
    # Sort selected ids afterward, matching mask->index traversal order.
    return [sorted(sorted(range(len(kmean)),
                          key=lambda j: (-dot(q, kmean[j]) * scale, j))[:keep])
            for q in qmean]


def online_update(m, denom, numer, logits, values):
    new_m = max(m, max(logits))
    alpha = math.exp(m - new_m)
    weights = [math.exp(s - new_m) for s in logits]
    new_denom = alpha * denom + sum(weights)
    new_numer = [alpha * u + sum(p * v[c] for p, v in zip(weights, values))
                 for c, u in enumerate(numer)]
    return new_m, new_denom, new_numer


def sparse_forward(qp, kp, vp, sizes, selected, blocks):
    d = len(qp[0][0])
    scale = 1 / math.sqrt(d)
    # Write directly back to original positions (the inverse pack operation).
    out = [None] * sum(sizes)
    for i, original_ids in enumerate(blocks):
        for offset, original_id in enumerate(original_ids):
            q = qp[i][offset]
            m, denom, numer = -math.inf, 0.0, [0.0] * d
            for j in selected[i]:
                # Padding is excluded using the actual valid count.
                logits = [dot(q, k) * scale for k in kp[j][:sizes[j]]]
                m, denom, numer = online_update(
                    m, denom, numer, logits, vp[j][:sizes[j]])
            out[original_id] = [u / denom for u in numer]
    return out


def original_order_attention(q, k, v, allowed):
    """Reference: explicit visible-key set per original query, one softmax."""
    scale = 1 / math.sqrt(len(q[0]))
    out = []
    for query, key_ids in zip(q, allowed):
        logits = [dot(query, k[j]) * scale for j in key_ids]
        m = max(logits)
        weights = [math.exp(s - m) for s in logits]
        denom = sum(weights)
        out.append([sum(p * v[j][c] for p, j in zip(weights, key_ids)) / denom
                    for c in range(len(v[0]))])
    return out


def max_error(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def run_case(grid, tile):
    d = 4
    n, capacity = math.prod(grid), math.prod(tile)
    rng = random.Random(7)
    q, k, v = [[[rng.uniform(-1, 1) for _ in range(d)] for _ in range(n)]
               for _ in range(3)]
    blocks = partition(grid, tile)
    sizes = [len(block) for block in blocks]
    qp, kp, vp = [pack(x, blocks, capacity) for x in (q, k, v)]
    qm, km = pool(qp, sizes), pool(kp, sizes)
    selected = route(qm, km, keep=2)
    allowed = [None] * n
    for i, original_ids in enumerate(blocks):
        key_ids = sorted(a for j in selected[i] for a in blocks[j])
        for a in original_ids:
            allowed[a] = key_ids
    sparse = sparse_forward(qp, kp, vp, sizes, selected, blocks)
    masked = original_order_attention(q, k, v, allowed)
    masked_error = max_error(sparse, masked)
    full_selection = route(qm, km, keep=len(blocks))
    full = sparse_forward(qp, kp, vp, sizes, full_selection, blocks)
    dense = original_order_attention(q, k, v, [list(range(n)) for _ in range(n)])
    dense_error = max_error(full, dense)
    assert sorted(a for block in blocks for a in block) == list(range(n))
    assert masked_error < 1e-12, masked_error
    assert dense_error < 1e-12, dense_error
    print(f'grid={grid}; tile={tile}; N={n}; D={d}')
    print(f'logical blocks={len(blocks)}; capacity={capacity}; valid sizes={sizes}')
    print(f'Q0 original indices: {blocks[0]}')
    print(f'Q0 selected KV blocks: {selected[0]}')
    print(f'sparse vs original-order masked attention: max error={masked_error:.3e}')
    print(f'all-blocks vs dense attention: max error={dense_error:.3e}')
    print('PASS: layout, padding, sparse selection and online softmax agree.')


if __name__ == '__main__':
    run_case((4, 4, 4), (4, 2, 2))
    print()
    run_case((5, 3, 4), (4, 2, 2))
