# Recognition Specification

Status: DRAFT

## Recognition contract

The recognition layer converts parser observations into a parser-neutral canonical document without assigning normative meaning.

Required evidence dimensions:

- document identity and source SHA-256;
- page boundaries/count where available;
- structural node type;
- reading order;
- parent-child hierarchy;
- source page and bounding box where available;
- character spans where available;
- raw extracted text;
- parser identity/version;
- parser-specific confidence and attributes;
- reconciliation status.

## Quality classes

`PASS` — no blocking recognition defects.

`PASS_WITH_WARNINGS` — usable canonical representation with non-blocking evidence gaps.

`FAIL` — one or more blocking structural/provenance defects.

## Recognition is not normative acceptance

A successful recognition gate does not imply that a clause, table, formula, or value is normatively correct. Normative decomposition and verification are downstream consumers.
