from __future__ import annotations

from pathlib import Path
from typing import Iterable

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr_assets as ecr_assets,
    aws_s3_assets as s3_assets,
)
from constructs import Construct


class SandsDeploymentStack(Stack):
    DEFAULT_BUOY_IDS = ["buoy-1", "buoy-2"]
    DEFAULT_INSTANCE_TYPE = "t3.medium"
    DEFAULT_SHARED_SECRET = "sands-shared-secret"
    DEFAULT_ORCA_PORT = 8000
    DEFAULT_FMI_PATH = "/fmi/seq.fmi"
    DEFAULT_FMINDEXER_BIN = "/usr/local/bin/fmindexer"

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        context = self.node.try_get_context
        repo_root = Path(__file__).resolve().parents[1]
        seq_asset = s3_assets.Asset(
            self,
            "SeqFmiAsset",
            path=str(repo_root / "fmindexer.rs" / "seq.fmi"),
        )

        shared_secret = context("shared_secret") or self.DEFAULT_SHARED_SECRET
        orca_port = (
            int(context("orca_port"))
            if context("orca_port")
            else self.DEFAULT_ORCA_PORT
        )
        instance_type = context("instance_type") or self.DEFAULT_INSTANCE_TYPE
        buoy_ids = self._sanitize_buoy_ids(context("buoy_ids"))

        vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)
        service_sg = ec2.SecurityGroup(
            self,
            "ServiceSecurityGroup",
            vpc=vpc,
            description="Match default security group inbound policy",
            allow_all_outbound=True,
        )
        service_sg.add_ingress_rule(
            service_sg,
            ec2.Port.all_traffic(),
            "default-vpc-style internal traffic",
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum install -y aws-cli",
            "mkdir -p /fmi",
            f"aws s3 cp s3://{seq_asset.s3_bucket_name}/{seq_asset.s3_object_key} {self.DEFAULT_FMI_PATH}",
            f"chmod 644 {self.DEFAULT_FMI_PATH}",
        )

        cluster = ecs.Cluster(self, "SandsCluster", vpc=vpc)
        namespace = cluster.add_default_cloud_map_namespace(name="sands.local")

        capacity = cluster.add_capacity(
            "InstanceCapacity",
            instance_type=ec2.InstanceType(instance_type),
            min_capacity=len(buoy_ids) + 1,
            desired_capacity=len(buoy_ids) + 1,
            max_capacity=len(buoy_ids) + 1,
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            user_data=user_data,
            associate_public_ip_address=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_groups=[service_sg],
        )
        seq_asset.grant_read(capacity.role)

        fmi_volume = ecs.Volume(name="fmi-volume", host=ecs.Host(source_path="/fmi"))

        orca_image_asset = ecr_assets.DockerImageAsset(
            self,
            "OrcaImage",
            directory=str(repo_root),
            file="orca/Dockerfile",
        )
        buoy_image_asset = ecr_assets.DockerImageAsset(
            self,
            "BuoyImage",
            directory=str(repo_root),
            file="buoy/Dockerfile",
        )
        orca_image = ecs.ContainerImage.from_docker_image_asset(orca_image_asset)
        buoy_image = ecs.ContainerImage.from_docker_image_asset(buoy_image_asset)

        orca_task = ecs.Ec2TaskDefinition(
            self,
            "OrcaTask",
            network_mode=ecs.NetworkMode.AWS_VPC,
        )
        orca_task.add_volume(fmi_volume)
        orca_container = orca_task.add_container(
            "OrcaContainer",
            image=orca_image,
            environment={
                "ORCA_SHARED_SECRET": shared_secret,
                "ORCA_DEFAULT_FMI_PATH": self.DEFAULT_FMI_PATH,
                "ORCA_TRACE_ENABLED": "true",
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix="orca"),
        )
        orca_container.add_port_mappings(
            ecs.PortMapping(container_port=orca_port, host_port=orca_port)
        )
        orca_container.add_mount_points(
            ecs.MountPoint(
                container_path="/fmi",
                source_volume="fmi-volume",
                read_only=True,
            )
        )

        orca_service = ecs.Ec2Service(
            self,
            "OrcaService",
            cluster=cluster,
            task_definition=orca_task,
            desired_count=1,
            cloud_map_options=ecs.CloudMapOptions(
                name="orca", cloud_map_namespace=namespace
            ),
            security_groups=[service_sg],
        )

        orca_url = f"http://orca.{namespace.namespace_name}:{orca_port}"

        for buoy_id in buoy_ids:
            self._add_buoy_service(
                cluster,
                service_sg,
                fmi_volume,
                buoy_image,
                shared_secret,
                orca_url,
                buoy_id,
            )

    def _add_buoy_service(
        self,
        cluster: ecs.Cluster,
        security_group: ec2.SecurityGroup,
        fmi_volume: ecs.Volume,
        buoy_image: ecs.ContainerImage,
        shared_secret: str,
        orca_url: str,
        buoy_id: str,
    ) -> None:
        task = ecs.Ec2TaskDefinition(
            self,
            f"BuoyTask{buoy_id}",
            network_mode=ecs.NetworkMode.AWS_VPC,
        )
        task.add_volume(fmi_volume)
        task.add_container(
            f"BuoyContainer{buoy_id}",
            image=buoy_image,
            environment={
                "ORCA_SHARED_SECRET": shared_secret,
                "FMINDEXER_BIN": self.DEFAULT_FMINDEXER_BIN,
                "ORCA_URL": orca_url,
                "BUOY_ID": buoy_id,
            },
            logging=ecs.LogDrivers.aws_logs(stream_prefix=f"buoy-{buoy_id}"),
        )

        ecs.Ec2Service(
            self,
            f"BuoyService{buoy_id}",
            cluster=cluster,
            task_definition=task,
            desired_count=1,
            security_groups=[security_group],
        )

    def _sanitize_buoy_ids(self, value: str | Iterable[str] | None) -> list[str]:
        if value is None:
            return self.DEFAULT_BUOY_IDS
        if isinstance(value, str):
            items = [item.strip() for item in value.split(",") if item.strip()]
            return items or self.DEFAULT_BUOY_IDS
        return [item for item in value if item]
