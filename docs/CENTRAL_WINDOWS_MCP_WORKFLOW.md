# Central Windows-MCP / Host Access Workflow

This document is the project-specific operating contract for the central Windows-MCP gateway.

## Project route

- Gateway project ID: 3dprinthub
- Access mode: host-based
- Local repository: D:\projects\3DprintHub
- Dedicated Windows loopback route: 127.0.0.1:22024
- Tunnel port: 22024
- This route belongs only to 3DPrintHub; never use another project's tunnel as fallback.

## Local development workflow

Windows local development -> local test -> project router -> correct Host -> backup -> transfer/deploy -> verify -> documentation.
Use the central router only with the exact project ID:
D:\projects\.chatgpt-gateway\project-host.ps1 -Project 3dprinthub -Health
D:\projects\.chatgpt-gateway\project-host.ps1 -Project 3dprinthub -Command "read-only command"
The router must use only the project's mapped 127.0.0.1 route and fail closed if the route is missing or ambiguous.

## Host update/deploy workflow

After Local tests pass, use the project's approved GitHub/release workflow. Access the Host only through the dedicated project router route 127.0.0.1:22024. Before any transfer or deploy, verify the exact accepted revision, create the required Host backup, and retain the rollback path. Deploy nothing from an unaccepted dirty worktree or through another project route.

## Backup and rollback rule

Back up the exact Host/application targets before any stateful transfer, migration, or deployment. Record backup identity and rollback command before mutation. If a gate fails, stop and use only the verified rollback for this project. Never restore or operate through another project's route.

## Verification gates

Verify, in order: repository path and branch; Local tests; exact project-router mapping; dedicated loopback listener; Host identity and clean/accepted revision; backup; transfer/deploy result; runtime/health checks; post-change Git and application checks. A failing or unavailable dedicated tunnel blocks Host work.

## Secret handling policy

Never store or print passwords, tokens, private keys, authorization headers, or secret values in this document, the registry, Git, logs, or chat. The router may read an existing protected local credential profile internally; only non-secret route metadata is documented.

## Documentation closure rule

After each meaningful stage, update this workflow document and the project current-state document with the exact change, tests/evidence, failures, backup/rollback state, current branch or revision, Host/Production state, remaining work, and next safe step. Do not claim deployment or Production verification without evidence.

## Fallback prohibition

This project must never use another project's tunnel, SSH alias, credential, Host, or deployment command as a fallback. If the dedicated route is unavailable, stop and report the blocked gate.
