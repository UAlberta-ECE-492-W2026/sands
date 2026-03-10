# sands

SoC-Accelerated, Networked DNA Sequencing

## Setup

Orca, Buoy, and Port share a single repository-level dependency set. Create one
virtual environment at the repo root and install the base and developer
requirements:

```bash
$ ./x.sh setup-venv
$ source venv/bin/activate  # use `venv/Scripts/activate` on Windows
```

Each service README (see `orca/README.md`, `buoy/README.md`, and
`port/README.md`) still covers how to run that server once the shared
environment is active.

## Running and Testing

Use the main task runner, `x.sh`:

```bash
$ ./x.sh setup-venv  # Setup your local venv
$ ./x.sh tests       # Run all tests
$ ./x.sh check       # Typecheck all code
$ ./x.sh run-local   # Run locally (with docker-compose)
$ ./x.sh infra       # Run CDK commands (defaults to synth)
$ ./x.sh help        # Print this message
```

## AWS Deployment

The `infra/` directory now houses a Python CDK app that automates provisioning for `orca` plus the two `buoy` workers on ECS backed by EC2 instances. The stack:

- builds the existing Docker artifacts (`orca/Dockerfile` and `buoy/Dockerfile`) via `DockerImageAsset` so the same binaries and `fmindexer.rs/seq.fmi` copy flow into the cloud deployment.
- spins up a default-VPC cluster with one EC2 instance per container (the desired capacity matches the number of buoys plus `orca`), installs the AWS CLI via user data, and downloads `seq.fmi` to `/fmi/seq.fmi` so each instance can mount it into the containers.
- mirrors the inbound policy of the default security group (only intra-group traffic) for the ECS service security group so `orca` stays restricted to the default subnet rules; no load balancer or autoscaling is configured.
- exposes `orca` through AWS Cloud Map service discovery (`orca.sands.local`) so buoys can point their `ORCA_URL` at `http://orca.sands.local:8000`; all environment variables are static and injected directly from the stack context.
- bypasses Secrets Manager by using the existing shared-secret env var, and keeps the buoys statically defined (no dynamic scaling).

To deploy:

```bash
cd infra
python -m pip install -r requirements.txt
cdk synth
cdk deploy
```

To customize the stack, pass context values (for example, to add extra buoys or change the EC2 instance type):

```bash
cdk deploy --context buoy_ids=buoy-1,buoy-2,buoy-3 --context instance_type=t3.large
```

Destroy everything with `cdk destroy` when you no longer need the infrastructure. The stack keeps `seq.fmi` mounted by downloading the CDK-deployed asset to `/fmi/seq.fmi` on each EC2 host during boot.

Use `./x.sh infra` to run the CDK CLI (defaulting to `synth`). The script ensures the venv is active, installs the infra dependencies, and lets you pass extra CDK verbs (e.g., `./x.sh infra deploy`). The built-in `tests` task now includes `cdk synth` so the CDK template is validated as part of regression testing.

Note: the AWS CDK CLI must be installed and available in your PATH (e.g., via `npm install -g aws-cdk`).
