#!/usr/bin/env python3

import os

from aws_cdk import App, Environment

from infra.deployment_stack import SandsDeploymentStack


app = App()
SandsDeploymentStack(
    app,
    "SandsCloudDeployment",
    env=Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
