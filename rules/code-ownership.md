# Code Ownership

Pre-bind and post-bind are the backend teams, so asking which one code belongs to is asking who
owns it. Three signals answer it, all worth using:

1. **What the code acts on.** A quote is pre-bind, a policy is post-bind, the bind is the boundary,
   all defined with code evidence in `swyfft-domain.md` § "Swyfft/Insurance Terminology". IMS is
   the policy management system and is post-bind.
2. **Who owns the path.** `.github/CODEOWNERS`.
3. **Who has worked on the file.** `git log` and `git blame`.

Signals 2 and 3 name individuals. Map each to their group and manager.

## Managers (not in the repo)

| Person | Role |
|---|---|
| Kenneth Smith (`ken-swyfft`) | CTO. Covers every area, so his name locates nothing |
| Ehren Weerheim (`ehrenw`) | Pre-bind manager. Eli's manager |
| Wayne Allen (`wayneswyfft`) | Post-bind manager |

`frontend` (`chrisharrington`, `dariuscarrick`) sits outside the pre-bind/post-bind split. It has
no manager of its own.

**A manager's name means the manager's team.** "Wayne's team owns this" names the `postbind`
group, satisfied by any member.

## Rosters (in the repo, read them)

| Question | Source |
|---|---|
| Who's in `prebind-backend`, `postbind`, `frontend`, `claims`, `automation`? | `.github/auto_request_review.yml` § `groups:` |
| Who reviews a path? | `.github/CODEOWNERS` |
| Who's requested on Eli's PRs? | `auto_request_review.yml` § `per_author:` → `eli-swyfft` |

CODEOWNERS' `*` line covers every path with no specific entry, so an absent folder is routed by
`*`.

- **What happened:** a ticket said another manager's team owned the path. The file's authors were
  checked, the group roster was not, and the note was called wrong. CODEOWNERS named a member of
  that manager's team.
