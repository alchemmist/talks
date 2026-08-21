import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen


REVIEW_IDS = (
    14736022,
    14742879,
    14065265,
    14073292,
    14084497,
    14073197,
    14076671,
    14073884,
    14073682,
    14065583,
    14073455,
    14063344,
    14074424,
    14066079,
    14074407,
    14073406,
    14041516,
    13935022,
    13934483,
    13934344,
    13934178,
    13934294,
    13934270,
    13934264,
    13934205,
    13934036,
    13935224,
    13934363,
    13935230,
    13934741,
    13934604,
    13935103,
    13934628,
    13934645,
    13934625,
    13704587,
    13934304,
    13934258,
    13934249,
    13934319,
    13934238,
    13934329,
    13934225,
    13934211,
    13934066,
    13933903,
    13933889,
)


def fetch_stats(review_id: int, token: str) -> tuple[int, int, int, str]:
    error = None
    for attempt in range(3):
        try:
            request = Request(
                f"<https://a.yandex-team.ru/review/{review_id}/details>",
                headers={
                    "Authorization": f"OAuth {token}",
                    "User-Agent": "format-quorum-talk-diffstats",
                },
            )
            with urlopen(request, timeout=30) as response:
                page = response.read().decode("utf-8")

            match = re.search(
                r"window\.__DATA__ = (\{.*?\});</script>", page, re.DOTALL
            )
            if not match:
                raise RuntimeError("window.__DATA__ not found")

            pull_request = json.loads(match.group(1))["store"]["pr"]
            stats = pull_request["active_diff_set"]["patch_stats"]
            summary = pull_request.get("summary", "")
            return review_id, stats["additions"], stats["deletions"], summary
        except Exception as current_error:
            error = current_error
            time.sleep(attempt + 1)

    raise RuntimeError(str(error))


def main() -> int:
    token = os.environ.get("ARC_TOKEN")
    if not token:
        print("ARC_TOKEN is not set", file=sys.stderr)
        return 1

    review_ids = tuple(dict.fromkeys(map(int, sys.argv[1:]))) or REVIEW_IDS
    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_stats, review_id, token): review_id
            for review_id in review_ids
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as error:
                errors.append((futures[future], str(error)))

    results.sort()
    for review_id, additions, deletions, summary in results:
        print(f"{review_id}\t+{additions}\t-{deletions}\t{summary}")

    print()
    print(f"PRs: {len(results)}")
    print(f"Additions: {sum(result[1] for result in results)}")
    print(f"Deletions: {sum(result[2] for result in results)}")

    for review_id, error in sorted(errors):
        print(f"{review_id}: {error}", file=sys.stderr)

    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
