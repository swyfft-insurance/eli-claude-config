# Code Ownership

## Which team owns code

Pre-bind and post-bind are the backend teams. Three signals say which owns code:

1. What the code acts on. A quote is pre-bind, a policy is post-bind, and the bind is the boundary (`swyfft-domain.md` § "Swyfft/Insurance Terminology"). IMS is post-bind.
2. Who owns the path: `.github/CODEOWNERS`. Its `*` line routes every path with no specific entry.
3. Who has worked on the file: `git log` and `git blame`.

Map each person from signals 2 and 3 to their group and manager. A manager's name means the manager's team: "Wayne's team" is the `postbind` group, satisfied by any member.

## People and roles

| Person | Role |
|---|---|
| Kenneth Smith (`ken-swyfft`) | CTO. Covers every area, so his name locates nothing |
| Ehren Weerheim (`ehrenw`) | Pre-bind manager. Eli's manager |
| Wayne Allen (`wayneswyfft`) | Post-bind manager |

`frontend` (`chrisharrington`, `dariuscarrick`) is outside the pre-bind/post-bind split and has no manager.

## Where to look it up

| Question | Source |
|---|---|
| Who's in `prebind-backend`, `postbind`, `frontend`, `claims`, `automation`? | `.github/auto_request_review.yml` § `groups:` |
| Who reviews a path? | `.github/CODEOWNERS` |
| Who's requested on Eli's PRs? | `auto_request_review.yml` § `per_author:` → `eli-swyfft` |
