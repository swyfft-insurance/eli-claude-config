#!/usr/bin/env python3
"""PR feedback helper: fetch, reply to, and resolve PR review comments.

Subcommands:
    fetch <PR#>                       Fetch all review threads for a PR
    reply <PR#> <comment-id> <body>   Reply to a review comment
    resolve <thread-id>               Resolve a review thread

Uses `gh` CLI for GitHub API calls. Must be on PATH.
"""

import json
import subprocess
import sys


OWNER = "swyfft-insurance"
REPO = "swyfft_web"


def gh(*args, input_data=None):
    """Run a gh CLI command and return parsed JSON output."""
    cmd = ["gh"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        input=input_data,
        timeout=30,
    )
    if result.returncode != 0:
        print(json.dumps({
            "error": True,
            "command": " ".join(cmd),
            "stderr": result.stderr.strip(),
        }))
        sys.exit(1)
    if result.stdout.strip():
        return json.loads(result.stdout)
    return {}


def fetch(pr_number):
    """Fetch all review threads and top-level review comments for a PR."""
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          url
          title
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              path
              line
              startLine
              diffSide
              comments(first: 50) {
                nodes {
                  id
                  databaseId
                  author { login }
                  body
                  createdAt
                  path
                  position
                }
              }
            }
          }
          reviews(first: 50) {
            nodes {
              id
              databaseId
              author { login }
              body
              state
              createdAt
            }
          }
        }
      }
    }
    """
    data = gh(
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"owner={OWNER}",
        "-f", f"repo={REPO}",
        "-F", f"pr={pr_number}",
    )

    pr_data = data["data"]["repository"]["pullRequest"]
    threads = []

    for thread in pr_data["reviewThreads"]["nodes"]:
        if thread["isResolved"]:
            continue

        comments = []
        for comment in thread["comments"]["nodes"]:
            comments.append({
                "id": comment["id"],
                "databaseId": comment["databaseId"],
                "author": comment["author"]["login"] if comment["author"] else "unknown",
                "body": comment["body"],
                "createdAt": comment["createdAt"],
            })

        threads.append({
            "threadId": thread["id"],
            "path": thread["path"],
            "line": thread["line"],
            "startLine": thread["startLine"],
            "isOutdated": thread["isOutdated"],
            "comments": comments,
        })

    # Top-level review comments (review body text, not attached to specific lines)
    reviews = []
    for review in pr_data["reviews"]["nodes"]:
        body = (review.get("body") or "").strip()
        if not body:
            continue
        reviews.append({
            "id": review["id"],
            "databaseId": review["databaseId"],
            "author": review["author"]["login"] if review["author"] else "unknown",
            "body": body,
            "state": review["state"],
            "createdAt": review["createdAt"],
        })

    result = {
        "pr": pr_number,
        "url": pr_data["url"],
        "title": pr_data["title"],
        "unresolvedThreads": threads,
        "totalUnresolved": len(threads),
        "reviews": reviews,
        "totalReviews": len(reviews),
    }

    print(json.dumps(result, indent=2))


def reply(pr_number, comment_id, body):
    """Reply to a review comment."""
    result = gh(
        "api",
        f"repos/{OWNER}/{REPO}/pulls/{pr_number}/comments/{comment_id}/replies",
        "-f", f"body={body}",
    )
    print(json.dumps({
        "success": True,
        "commentId": comment_id,
        "replyId": result.get("id"),
    }))


def resolve(thread_id):
    """Resolve a review thread."""
    mutation = f'mutation {{ resolveReviewThread(input:{{threadId:"{thread_id}"}}) {{ thread {{ isResolved }} }} }}'
    result = gh("api", "graphql", "-f", f"query={mutation}")
    is_resolved = result.get("data", {}).get("resolveReviewThread", {}).get("thread", {}).get("isResolved", False)
    print(json.dumps({
        "success": is_resolved,
        "threadId": thread_id,
    }))


def review_reply(pr_number, body):
    """Post an issue comment on the PR conversation tab (for replying to top-level reviews)."""
    result = gh(
        "api",
        f"repos/{OWNER}/{REPO}/issues/{pr_number}/comments",
        "-f", f"body={body}",
    )
    print(json.dumps({
        "success": True,
        "prNumber": pr_number,
        "commentId": result.get("id"),
    }))


def main():
    if len(sys.argv) < 2:
        print("Usage: pr-feedback.py <fetch|reply|resolve|review-reply> [args...]", file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "fetch":
        if len(sys.argv) != 3:
            print("Usage: pr-feedback.py fetch <PR#>", file=sys.stderr)
            sys.exit(1)
        fetch(int(sys.argv[2]))

    elif cmd == "reply":
        if len(sys.argv) != 5:
            print("Usage: pr-feedback.py reply <PR#> <comment-id> <body>", file=sys.stderr)
            sys.exit(1)
        reply(int(sys.argv[2]), sys.argv[3], sys.argv[4])

    elif cmd == "resolve":
        if len(sys.argv) != 3:
            print("Usage: pr-feedback.py resolve <thread-id>", file=sys.stderr)
            sys.exit(1)
        resolve(sys.argv[2])

    elif cmd == "review-reply":
        if len(sys.argv) != 4:
            print("Usage: pr-feedback.py review-reply <PR#> <body>", file=sys.stderr)
            sys.exit(1)
        review_reply(int(sys.argv[2]), sys.argv[3])

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
