from aws_cdk import (
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codebuild as codebuild,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    Stack, App, Environment
)
from constructs import Construct

class MyPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        artifact_bucket = s3.Bucket(self, "PipelineArtifactBucket")
        ecr_repo = ecr.Repository.from_repository_name(self, "MyEcrRepo", "nginx-hello-commit")
        source_artifact = codepipeline.Artifact()
        build_artifact = codepipeline.Artifact()

        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "echo Installing dependencies..."
                        ]
                    },
                    "build": {
                        "commands": [
                            "echo Building the Docker image...",
                            f"echo '[{{\"name\":\"nginx\",\"imageUri\":\"{ecr_repo.repository_uri}:latest\"}}]' > imagedefinitions.json"
                        ]
                    }
                },
                "artifacts": {
                    "files": "imagedefinitions.json"
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True  
            )
        )
        vpc = ec2.Vpc.from_vpc_attributes(
            self, "ImportedVpc",
            vpc_id="vpc-03f66344967a9f88c",  
            availability_zones=["us-east-1a"],  
            public_subnet_ids=["subnet-083509d35e9abecfd"], 
            private_subnet_ids=["subnet-023f2a7c498154fea"] 
        )
        cluster = ecs.Cluster.from_cluster_attributes(
            self, "ImportedCluster",
            cluster_name="ecs-cluster", 
            vpc=vpc
        )
        task_definition = ecs.TaskDefinition.from_task_definition_arn(
            self, "ImportedTaskDef",
            task_definition_arn="arn
        )
        ecs_service = ecs.FargateService.from_fargate_service_attributes(
            self, "ImportedService",
            service_name="nginx-service",  
            cluster=cluster
        )
        pipeline = codepipeline.Pipeline(self, "Pipeline",
            artifact_bucket=artifact_bucket,
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        cpactions.EcrSourceAction(
                            action_name="ECR",
                            repository=ecr_repo,
                            image_tag="latest",
                            output=source_artifact
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        cpactions.CodeBuildAction(
                            action_name="Build",
                            project=build_project,
                            input=source_artifact,
                            outputs=[build_artifact]
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[
                        cpactions.EcsDeployAction(
                            action_name="DeployAction",
                            service=ecs_service,
                            input=build_artifact
                        )
                    ]
                )
            ]
        )

app = App()
MyPipelineStack(app, "MyPipelineStack", env=Environment(region="us-east-1"))  
app.synth()

