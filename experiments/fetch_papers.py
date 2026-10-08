"""Download the reference papers into papers/ (they are gitignored).

    python experiments/fetch_papers.py
"""

from __future__ import annotations

import os
import urllib.request

PAPERS = {
    "01-single-index-bandits/2605.09454-Dey-Bhore-Ghosh-Optimal-Regret-Single-Index-Bandits.pdf": "2605.09454",
    "01-single-index-bandits/arxiv-2506.12751.pdf": "2506.12751",   # Kang et al., Single Index Bandits (ICLR 2026)
    "01-single-index-bandits/arxiv-2603.18938.pdf": "2603.18938",   # Arya et al., Kernel Single-Index Bandits
    "02-single-agent-foundations/arxiv-1704.00445.pdf": "1704.00445",   # Chowdhury & Gopalan, On Kernelized MAB
    "04-decentralized-bandits-graph/arxiv-2008.06220.pdf": "2008.06220",   # Dubey & Pentland, Coop-KernelUCB
    "04-decentralized-bandits-graph/arxiv-2012.00314.pdf": "2012.00314",   # Amani & Thrampoulidis, (Safe-)DLUCB
    "02-single-agent-foundations/arxiv-1704.06880.pdf": "1704.06880",   # Ghosh et al., Misspecified Linear Bandits
}


def main():
    os.makedirs("papers", exist_ok=True)
    for fname, arxiv_id in PAPERS.items():
        path = os.path.join("papers", fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            print(f"  have   {fname}")
            continue
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        print(f"  fetch  {fname}  <- {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "cs6007-project"})
        with urllib.request.urlopen(req) as r, open(path, "wb") as f:
            f.write(r.read())
    print("done")


if __name__ == "__main__":
    main()
