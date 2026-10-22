# Authentication and authorization

## Authentication: who you are
- Email magic link
- Google sign-in

Options:
- Verify the email address
- Password reset by email
- Slow down and lock out after failed sign-ins
- Use a proven library or auth service; never store a password yourself.
- Sessions are secure, HTTP-only cookies; sign-out ends the session on the server.

## Authorization: what you may do
- Deny by default: a route with no rule below is refused.
- Check the permission on the server, on every request; pages only hide what the server already refuses.
- Tenants: One database, tenant id on every row and key. Every row and key carries the tenant id, and every query filters by it. This is always on.

| Permission | Owner | Student / Researcher | Admin (add via "+ Add a role") |
|---|---|---|---|
| Auth | yes | yes | — |
| Auth | yes | yes | — |
| Topic Search | yes | yes | — |
| Gap Analysis | yes | yes | — |
| Title Suggestions | yes | yes | — |
| Deep-Dive Search | yes | yes | — |
| Objectives & Methodology | yes | yes | — |
| Usage Quota | yes | yes | — |
| Usage Quota | yes | yes | — |
| Project History | yes | yes | — |
| Export to Word/PDF | yes | yes | — |
| Subscription & Payment | yes | yes | — |
| Subscription & Payment | yes | yes | — |
| Citation Checker | yes | yes | — |
| Admin Dashboard | yes | — | — |
| Manage team and roles | yes | — | — |
| Billing and plan | yes | — | — |
| Business settings | yes | — | — |
| AI settings | yes | — | — |
| Usage and logs | yes | — | — |
| Export data | yes | — | — |

Options:
- Invite team members by email
- API keys for customers' own software
