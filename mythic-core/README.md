# Mythic Core — upstream reference

This directory is reserved for the non-vendored Mythic Core integration.

## Official upstream

- Mythic Core: https://github.com/its-a-feature/Mythic
- MythicContainer: https://github.com/MythicMeta/MythicContainer
- Mythic Scripting: https://github.com/MythicMeta/Mythic_Scripting

The upstream Mythic repository contains the Core server, UI, Docker definitions, and CLI source. The upstream project explicitly keeps Payload Types/Agents and C2 Profiles in separate repositories.

## Repository policy

This project does not vendor operational payload/agent or C2-profile source. Those components can provide remote-control/C2 capabilities and are intentionally kept outside this repository.

For a local authorized lab, use the official upstream repository directly and keep its Docker project isolated from the other services on the host.
