#!/usr/bin/env python3
"""
Node Types - Predefined node types for events and actions
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from PySide6.QtGui import QColor

from .visual_node import VisualNode, PortType


@dataclass
class NodeTypeDefinition:
    """Definition of a node type"""
    type_id: str
    display_name: str
    category: str
    color: str
    description: str
    input_ports: List[Dict[str, Any]]
    output_ports: List[Dict[str, Any]]
    parameters: Dict[str, Any]


class ActionNode(VisualNode):
    """Node representing an action"""
    
    def __init__(self, action_type: str, display_name: str):
        super().__init__(f"action_{action_type}", display_name, "Actions")
        self.action_type = action_type
        self.color = QColor("#E74C3C")  # Red for actions
        
        # All action nodes have execution flow
        self.add_input_port("", PortType.EXECUTION_IN)
        self.add_output_port("", PortType.EXECUTION_OUT)


class EventNode(VisualNode):
    """Node representing an event"""
    
    def __init__(self, event_type: str, display_name: str):
        super().__init__(f"event_{event_type}", display_name, "Events")
        self.event_type = event_type
        self.color = QColor("#2ECC71")  # Green for events
        
        # Events only have execution output
        self.add_output_port("", PortType.EXECUTION_OUT)


class ConditionNode(VisualNode):
    """Node representing a conditional"""
    
    def __init__(self, condition_type: str, display_name: str):
        super().__init__(f"condition_{condition_type}", display_name, "Conditions")
        self.condition_type = condition_type
        self.color = QColor("#F39C12")  # Orange for conditions
        
        # Conditions have execution in and multiple outputs
        self.add_input_port("", PortType.EXECUTION_IN)
        self.add_output_port("True", PortType.EXECUTION_OUT)
        self.add_output_port("False", PortType.EXECUTION_OUT)


class VariableNode(VisualNode):
    """Node for getting/setting variables"""
    
    def __init__(self, variable_name: str, is_getter: bool = True):
        node_type = "get" if is_getter else "set"
        super().__init__(f"var_{node_type}_{variable_name}", f"{node_type.title()} {variable_name}", "Variables")
        self.variable_name = variable_name
        self.is_getter = is_getter
        self.color = QColor("#9B59B6")  # Purple for variables
        
        if is_getter:
            # Getter: only data output
            self.add_output_port(variable_name, PortType.DATA_OUT, "any")
        else:
            # Setter: execution + data input + execution output
            self.add_input_port("", PortType.EXECUTION_IN)
            self.add_input_port(variable_name, PortType.DATA_IN, "any")
            self.add_output_port("", PortType.EXECUTION_OUT)


class ValueNode(VisualNode):
    """Node for constant values"""
    
    def __init__(self, value_type: str, default_value: Any = None):
        super().__init__(f"value_{value_type}", f"{value_type} Value", "Values")
        self.value_type = value_type
        self.color = QColor("#3498DB")  # Blue for values
        
        self.add_output_port("value", PortType.DATA_OUT, value_type)
        self.parameters['value'] = default_value or self._get_default_for_type(value_type)
    
    def _get_default_for_type(self, value_type: str):
        """Get default value for type"""
        defaults = {
            'number': 0,
            'string': '',
            'boolean': False
        }
        return defaults.get(value_type, None)


def get_node_types() -> Dict[str, NodeTypeDefinition]:
    """Get all available node types"""
    
    node_types = {}
    
    # Event nodes
    events = [
        ("create", "Create", "Triggered when instance is created"),
        ("step", "Step", "Triggered every frame"),
        ("destroy", "Destroy", "Triggered when instance is destroyed"),
        ("keyboard_left", "Keyboard: Left", "Triggered when left arrow pressed"),
        ("keyboard_right", "Keyboard: Right", "Triggered when right arrow pressed"),
        ("keyboard_up", "Keyboard: Up", "Triggered when up arrow pressed"),
        ("keyboard_down", "Keyboard: Down", "Triggered when down arrow pressed"),
        ("collision", "Collision", "Triggered on collision"),
    ]
    
    for event_id, name, desc in events:
        node_types[f"event_{event_id}"] = NodeTypeDefinition(
            type_id=f"event_{event_id}",
            display_name=name,
            category="Events",
            color="#2ECC71",
            description=desc,
            input_ports=[],
            output_ports=[{"name": "", "type": "execution"}],
            parameters={}
        )
    
    # Action nodes
    actions = [
        ("move", "Move", [
            {"name": "direction", "type": "string"},
            {"name": "speed", "type": "number"}
        ]),
        ("set_sprite", "Set Sprite", [
            {"name": "sprite", "type": "string"}
        ]),
        ("destroy_instance", "Destroy Instance", []),
        ("create_instance", "Create Instance", [
            {"name": "object", "type": "string"},
            {"name": "x", "type": "number"},
            {"name": "y", "type": "number"}
        ]),
        ("play_sound", "Play Sound", [
            {"name": "sound", "type": "string"}
        ]),
    ]
    
    for action_id, name, params in actions:
        param_dict = {p['name']: "" if p['type'] == 'string' else 0 for p in params}
        
        input_ports = [{"name": "", "type": "execution"}]
        input_ports.extend([{"name": p['name'], "type": p['type']} for p in params])
        
        node_types[f"action_{action_id}"] = NodeTypeDefinition(
            type_id=f"action_{action_id}",
            display_name=name,
            category="Actions",
            color="#E74C3C",
            description=f"Action: {name}",
            input_ports=input_ports,
            output_ports=[{"name": "", "type": "execution"}],
            parameters=param_dict
        )
    
    # Condition nodes
    conditions = [
        ("if_collision", "If Collision With", [
            {"name": "object", "type": "string"}
        ]),
        ("if_variable", "If Variable", [
            {"name": "variable", "type": "string"},
            {"name": "operator", "type": "string"},
            {"name": "value", "type": "any"}
        ]),
        ("if_key_pressed", "If Key Pressed", [
            {"name": "key", "type": "string"}
        ]),
    ]
    
    for cond_id, name, params in conditions:
        param_dict = {p['name']: "" if p['type'] == 'string' else 0 for p in params}
        
        input_ports = [{"name": "", "type": "execution"}]
        input_ports.extend([{"name": p['name'], "type": p['type']} for p in params])
        
        node_types[f"condition_{cond_id}"] = NodeTypeDefinition(
            type_id=f"condition_{cond_id}",
            display_name=name,
            category="Conditions",
            color="#F39C12",
            description=f"Condition: {name}",
            input_ports=input_ports,
            output_ports=[
                {"name": "True", "type": "execution"},
                {"name": "False", "type": "execution"}
            ],
            parameters=param_dict
        )
    
    return node_types


def create_node_from_type(type_id: str, node_types: Dict[str, NodeTypeDefinition] = None) -> VisualNode:
    """Create a node instance from a type definition"""
    
    if node_types is None:
        node_types = get_node_types()
    
    if type_id not in node_types:
        return None
    
    node_def = node_types[type_id]
    
    # Create appropriate node based on category
    if node_def.category == "Events":
        event_type = type_id.replace("event_", "")
        node = EventNode(event_type, node_def.display_name)
    
    elif node_def.category == "Actions":
        action_type = type_id.replace("action_", "")
        node = ActionNode(action_type, node_def.display_name)
        
        # Add data input ports for parameters
        for port_def in node_def.input_ports[1:]:  # Skip execution port
            node.add_input_port(port_def['name'], PortType.DATA_IN, port_def['type'])
        
        node.parameters = node_def.parameters.copy()
    
    elif node_def.category == "Conditions":
        condition_type = type_id.replace("condition_", "")
        node = ConditionNode(condition_type, node_def.display_name)
        
        # Add data input ports for parameters
        for port_def in node_def.input_ports[1:]:  # Skip execution port
            node.add_input_port(port_def['name'], PortType.DATA_IN, port_def['type'])
        
        node.parameters = node_def.parameters.copy()
    
    else:
        # Generic node
        node = VisualNode(type_id, node_def.display_name, node_def.category)
        node.color = QColor(node_def.color)
        node.parameters = node_def.parameters.copy()
    
    # Update node height based on ports
    node.height = max(
        node.NODE_HEIGHT,
        node.TITLE_HEIGHT + max(len(node.input_ports), len(node.output_ports)) * 25 + 10
    )
    node.update_port_positions()
    
    return node