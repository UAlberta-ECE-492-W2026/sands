# Port CLI

Simple Python CLI that talks to Orca, submits newline-delimited short reads,
and inspects job progress.

## Usage

```bash
python port/cli.py submit --reads reads.txt --fmi-path /fmi/seq.fmi  # Submit reads from a file
cat reads.txt | python port/cli.py submit --fmi-path /fmi/seq.fmi    # Submit reads via stdin
python port/cli.py status --job-id <JOB_ID>                          # Poll job status
```

All requests send `X-Orca-Timestamp` and `X-Orca-Signature` headers using the
shared secret `sands-shared-secret` (override with `--secret`).
