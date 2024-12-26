import os
import json
from aws_cdk import aws_bedrock as bedrock


def load_kb_data(kb_path):
    print("Loading knowledge base data from %s" % kb_path)
    kb_data = None
    if os.path.exists(kb_path):
        with open(kb_path, "r") as file:
            kb_data = json.load(file)
            return create_kb_property(kb_data)

    return kb_data


def create_kb_property(knowledge_bases):
    kb_group_properties = []
    for knowledge_base in knowledge_bases:
        kb_group_property = bedrock.CfnAgent.AgentKnowledgeBaseProperty(
            description=knowledge_base["description_kb"],
            knowledge_base_id=knowledge_base["knowledge_base_id"],
        )
    kb_group_properties.append(kb_group_property)
    return kb_group_properties


def load_ag_data(ag_path, function_arn):
    print("Loading agent action group data from %s" % ag_path)
    ag_data = None
    if os.path.exists(ag_path):
        with open(ag_path, "r") as file:
            ag_data = json.load(file)
            for action_group in ag_data:
                action_group["lambda_"] = function_arn
            return create_ag_property(ag_data)

    return ag_data


def create_ag_property(ag_data):
    agent_action_group_properties = []
    """     
    agent_action_group_property = bedrock.CfnAgent.AgentActionGroupProperty(
        action_group_name="askinuput", parent_action_group_signature="AMAZON.UserInput"
    ) """

    #agent_action_group_properties.append(agent_action_group_property)

    for action_group in ag_data:
        agent_action_group_properties.append(
            create_agent_action_group_property(action_group)
        )

    return agent_action_group_properties


def create_ag_parameters(action_group):
    parameters = {}
    for parameter in action_group["functions"]["parameters"]:
        parameters[parameter["name"]] = bedrock.CfnAgent.ParameterDetailProperty(
            type=parameter["type"],
            description=parameter["description"],
            required=bool(parameter["required"]),
        )
    return parameters


def create_agent_action_group_property(action_group):
    parameters = create_ag_parameters(action_group)
    return bedrock.CfnAgent.AgentActionGroupProperty(
        action_group_name=action_group["action_group_name"],
        action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
            lambda_=action_group["lambda_"]
        ),
        action_group_state="ENABLED",
        description=action_group["description"],
        function_schema=bedrock.CfnAgent.FunctionSchemaProperty(
            functions=[
                bedrock.CfnAgent.FunctionProperty(
                    name=action_group["functions"]["name"],
                    description=action_group["functions"]["description"],
                    parameters=parameters,
                )
            ]
        ),
        skip_resource_in_use_check_on_delete=False,
    )
