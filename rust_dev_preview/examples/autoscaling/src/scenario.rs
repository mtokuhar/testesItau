use std::fmt::Display;

use anyhow::anyhow;
use aws_sdk_autoscaling::types::{AutoScalingGroup, Instance, LaunchTemplateSpecification};
use aws_sdk_ec2::types::RequestLaunchTemplateData;
use tracing::info;

const LAUNCH_TEMPLATE_NAME: &str = "SDK_Code_Examples_EC2_Autoscaling_template_from_Rust_SDK";
const AUTOSCALING_GROUP_NAME: &str = "SDK_Code_Examples_EC2_Autoscaling_Group_from_Rust_SDK";

pub struct AutoScalingScenario {
    ec2: aws_sdk_ec2::Client,
    autoscaling: aws_sdk_autoscaling::Client,
    launch_template_arn: String,
    auto_scaling_group_name: String,
}

impl Display for AutoScalingScenario {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_fmt(format_args!(
            "\tLaunch Template ID: {}\n",
            self.launch_template_arn
        ))?;
        f.write_fmt(format_args!(
            "\tScaling Group Name: {}\n",
            self.auto_scaling_group_name
        ))?;

        Ok(())
    }
}

pub struct AutoScalingScenarioDescription {
    instances: Vec<Instance>,
}

impl Display for AutoScalingScenarioDescription {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("\t        Instances:\n")?;
        for instance in &self.instances {
            f.write_fmt(format_args!(
                "\t\t- {}\n",
                instance.instance_id().unwrap_or_default()
            ))?;
        }

        Ok(())
    }
}

impl AutoScalingScenario {
    pub async fn prepare_scenario(
        sdk_config: &aws_types::sdk_config::SdkConfig,
    ) -> Result<Self, anyhow::Error> {
        let ec2 = aws_sdk_ec2::Client::new(sdk_config);
        let autoscaling = aws_sdk_autoscaling::Client::new(sdk_config);

        // Before creating any resources, prepare the list of AZs
        let availablity_zones = ec2.describe_availability_zones().send().await;
        if let Err(err) = availablity_zones {
            return Err(anyhow!("Failed to find AZs: {err}"));
        }

        let availability_zones: Vec<String> = availablity_zones
            .unwrap()
            .availability_zones
            .unwrap_or_default()
            .iter()
            .take(3)
            .map(|z| z.zone_name.clone().unwrap())
            .collect();

        // 1. Create an EC2 launch template that you'll use to create an auto scaling group. Bonus: use SDK with EC2.CreateLaunchTemplate to create the launch template.
        //   * Recommended: InstanceType='t1.micro', ImageId='ami-0ca285d4c2cda3300'
        let create_launch_template = ec2
            .create_launch_template()
            .launch_template_name(LAUNCH_TEMPLATE_NAME)
            .launch_template_data(
                RequestLaunchTemplateData::builder()
                    .instance_type(aws_sdk_ec2::types::InstanceType::T1Micro)
                    .image_id("ami-0ca285d4c2cda3300")
                    .build(),
            )
            .send()
            .await?;

        let launch_template_arn = match create_launch_template.launch_template {
            Some(launch_template) => launch_template.launch_template_id.unwrap_or_default(),
            None => {
                return Err(anyhow::anyhow!("Failed to load launch template"));
            }
        };

        // 2. CreateAutoScalingGroup: pass it the launch template you created in step 0. Give it min/max of 1 instance.
        //   You can use EC2.describe_availability_zones() to get a list of AZs (you have to specify an AZ when you create the group).
        //   Wait for instance to launch. Use a waiter if you have one, otherwise DescribeAutoScalingInstances until LifecycleState='InService'

        let create_autoscaling_group = autoscaling
            .create_auto_scaling_group()
            .auto_scaling_group_name(AUTOSCALING_GROUP_NAME)
            .launch_template(
                LaunchTemplateSpecification::builder()
                    .launch_template_id(launch_template_arn.clone())
                    .version("$Latest")
                    .build(),
            )
            .max_size(1)
            .min_size(1)
            .set_availability_zones(Some(availability_zones))
            .send()
            .await;

        if let Err(err) = create_autoscaling_group {
            let delete_launch_template = ec2
                .delete_launch_template()
                .launch_template_id(launch_template_arn.clone())
                .send()
                .await;
            if delete_launch_template.is_ok() {
                return Err(anyhow!("Failed to create autoscaling group: {err:?}"));
            } else {
                return Err(anyhow!("Failed to create autoscaling group: {err:?}\nFailed to clean up launch template: {delete_launch_template:?}"));
            }
        }

        let auto_scaling_group_name = String::from(AUTOSCALING_GROUP_NAME);

        // 4. EnableMetricsCollection: enable all metrics or a subset.
        //   If a subset, this list makes the most sense: 'GroupMinSize', 'GroupMaxSize', 'GroupDesiredCapacity', 'GroupInServiceInstances', 'GroupTotalInstances'.

        Ok(AutoScalingScenario {
            ec2,
            autoscaling,
            auto_scaling_group_name,
            launch_template_arn,
        })
    }

    pub async fn clean_scenario(self) -> Result<(), anyhow::Error> {
        let delete_group = self
            .autoscaling
            .delete_auto_scaling_group()
            .auto_scaling_group_name(self.auto_scaling_group_name.clone())
            .send()
            .await;

        // 14. Delete LaunchTemplate.
        let delete_launch_template = self
            .ec2
            .delete_launch_template()
            .launch_template_id(self.launch_template_arn.clone())
            .send()
            .await;

        if delete_group.is_ok() && delete_launch_template.is_ok() {
            Ok(())
        } else {
            Err(anyhow!("There was an error cleaning the scenario\nScale Group: {delete_group:?}\nDelete Launch Template: {delete_launch_template:?}"))
        }
    }

    pub async fn describe_scenario(&self) -> Result<AutoScalingScenarioDescription, anyhow::Error> {
        // 3. DescribeAutoScalingInstances: show that one instance has launched.
        // 8. DescribeAutoScalingInstances: show that two instances are launched.

        let instances = self.list_instances().await?;

        // 6. DescribeAutoScalingGroups: show the current state of the group.
        // 10. DescribeScalingActivities: list the scaling activities that have occurred for the group so far.
        //   Bonus: use CloudWatch API to get and show some metrics collected for the group.
        //   CW.ListMetrics with Namespace='AWS/AutoScaling' and Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': }]
        //   CW.GetMetricStatistics with Statistics='Sum'. Start and End times must be in UTC!

        Ok(AutoScalingScenarioDescription { instances })
    }

    async fn get_group(&self) -> Result<AutoScalingGroup, anyhow::Error> {
        let describe_auto_scaling_groups = self
            .autoscaling
            .describe_auto_scaling_groups()
            .auto_scaling_group_names(self.auto_scaling_group_name.clone())
            .send()
            .await;

        if let Err(err) = describe_auto_scaling_groups {
            return Err(anyhow!(
                "Failed to get status of autoscaling group {}: {err}",
                self.auto_scaling_group_name.clone()
            ));
        }

        let auto_scaling_groups = describe_auto_scaling_groups
            .unwrap()
            .auto_scaling_groups
            .unwrap_or_default();
        let auto_scaling_group = auto_scaling_groups.first();

        if auto_scaling_group.is_none() {
            return Err(anyhow!(
                "Could not find autoscaling group {}",
                self.auto_scaling_group_name.clone()
            ));
        }

        Ok(auto_scaling_group.unwrap().clone())
    }

    pub async fn wait_for_stable(&self, size: usize) -> Result<(), anyhow::Error> {
        let mut group = self.get_group().await?;

        while !{
            let group = &group;
            group
                .instances
                .as_ref()
                .map(|i| i.len())
                .unwrap_or_default()
                == size
        } {
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
            group = self.get_group().await?;
        }

        Ok(())
    }

    pub async fn list_instances(&self) -> Result<Vec<Instance>, anyhow::Error> {
        Ok(self.get_group().await?.instances.unwrap_or_default())
    }

    pub async fn scale_min_size(&self, size: i32) -> Result<(), anyhow::Error> {
        let update_group = self
            .autoscaling
            .update_auto_scaling_group()
            .auto_scaling_group_name(self.auto_scaling_group_name.clone())
            .min_size(size)
            .send()
            .await;
        if let Err(err) = update_group {
            return Err(anyhow!(
                "Failed to update group to min size ({size}): {err:?}"
            ));
        }
        Ok(())
    }

    pub async fn scale_max_size(&self, size: i32) -> Result<(), anyhow::Error> {
        // 5. UpdateAutoScalingGroup: update max size to 3.
        let update_group = self
            .autoscaling
            .update_auto_scaling_group()
            .auto_scaling_group_name(self.auto_scaling_group_name.clone())
            .max_size(size)
            .send()
            .await;
        if let Err(err) = update_group {
            return Err(anyhow!(
                "Failed to update group to max size ({size}): {err:?}"
            ));
        }
        Ok(())
    }

    pub async fn scale_desired_capacity(&self, capacity: i32) -> Result<(), anyhow::Error> {
        // 7. SetDesiredCapacity: set desired capacity to 2.
        //   Wait for a second instance to launch.
        let update_group = self
            .autoscaling
            .update_auto_scaling_group()
            .auto_scaling_group_name(self.auto_scaling_group_name.clone())
            .desired_capacity(capacity)
            .send()
            .await;
        if let Err(err) = update_group {
            return Err(anyhow!(
                "Failed to update group to desired capacity ({capacity}): {err:?}"
            ));
        }
        Ok(())
    }

    pub async fn scale_group(&self) -> Result<(), anyhow::Error> {
        // 11. DisableMetricsCollection

        // 12. DeleteAutoScalingGroup (to delete the group you must stop all instances):
        //   UpdateAutoScalingGroup with MinSize=0
        let update_group = self
            .autoscaling
            .update_auto_scaling_group()
            .auto_scaling_group_name(self.auto_scaling_group_name.clone())
            .min_size(0)
            .desired_capacity(0)
            .send()
            .await;
        if let Err(err) = update_group {
            return Err(anyhow!("Failed to update group for scaling down: {err:?}"));
        }

        let stable = self.wait_for_stable(0).await;
        if let Err(err) = stable {
            return Err(anyhow!(
                "Error while waiting for group to be stable on scale down: {err:?}"
            ));
        }

        Ok(())
    }

    pub async fn terminate_some_instance(&self) -> Result<(), anyhow::Error> {
        // 9. TerminateInstanceInAutoScalingGroup: terminate one of the instances in the group.
        //   Wait for the old instance to stop and a new instance to launch to bring the capacity back to 2.
        let instances = self.list_instances().await;
        match instances {
            Ok(instances) => {
                let instance = instances.first();
                if let Some(instance) = instance {
                    let id = instance.instance_id().unwrap();
                    info!("Terminating {id}");
                    let termination = self.ec2.terminate_instances().instance_ids(id).send().await;
                    if let Err(err) = termination {
                        Err(anyhow!(
                            "There was a problem terminating an instance\n{err:?}"
                        ))
                    } else {
                        Ok(())
                    }
                } else {
                    Err(anyhow!("There was no instance to terminate"))
                }
            }
            Err(err) => Err(anyhow!(
                "Error getting Autoscaling Group Instances\n{err:?}"
            )),
        }
    }
}