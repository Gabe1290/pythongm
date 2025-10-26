#!/usr/bin/env python3
"""
Code Generator - Converts visual nodes to executable action data
"""

from typing import List, Dict, Any, Optional
from .visual_node import VisualNode, PortType
from .connection import NodeConnection


class VisualCodeGenerator:
    """Generates executable action data from visual node graph"""
    
    def __init__(self):
        self.nodes: List[VisualNode] = []
        self.connections: List[NodeConnection] = []
    
    def set_graph(self, nodes: List[VisualNode], connections: List[NodeConnection]):
        """Set the node graph to generate code from"""
        self.nodes = nodes
        self.connections = connections
    
    def generate(self) -> Dict[str, Any]:
        """Generate event/action data structure from nodes"""
        # Find all event nodes (entry points)
        event_nodes = [node for node in self.nodes if hasattr(node, 'event_type')]
        
        # Generate action sequence for each event
        events_data = {}
        
        for event_node in event_nodes:
            event_type = event_node.event_type
            actions = self._generate_actions_from_node(event_node)
            
            if actions:
                events_data[event_type] = {
                    'actions': actions
                }
        
        return events_data
    
    def _generate_actions_from_node(self, node: VisualNode, visited: set = None) -> List[Dict[str, Any]]:
        """Generate action list starting from a node"""
        if visited is None:
            visited = set()
        
        # Prevent infinite loops
        if node.node_id in visited:
            return []
        
        visited.add(node.node_id)
        actions = []
        
        # If this is an action node, add it
        if hasattr(node, 'action_type'):
            action_data = self._node_to_action(node)
            if action_data:
                actions.append(action_data)
        
        # If this is a condition node, handle branching
        elif hasattr(node, 'condition_type'):
            condition_actions = self._handle_condition_node(node, visited)
            actions.extend(condition_actions)
        
        # Follow execution flow to next nodes
        next_nodes = self._get_next_execution_nodes(node)
        for next_node in next_nodes:
            next_actions = self._generate_actions_from_node(next_node, visited)
            actions.extend(next_actions)
        
        return actions
    
    def _node_to_action(self, node: VisualNode) -> Optional[Dict[str, Any]]:
        """Convert an action node to action data"""
        if not hasattr(node, 'action_type'):
            return None
        
        action_type = node.action_type
        
        # Get parameter values (from connections or node parameters)
        parameters = {}
        
        for input_port in node.input_ports:
            if input_port.port_type == PortType.DATA_IN:
                # Check if port has connection
                value = self._get_port_value(input_port)
                if value is not None:
                    parameters[input_port.name] = value
                elif input_port.name in node.parameters:
                    parameters[input_port.name] = node.parameters[input_port.name]
        
        # Map visual node action types to existing action system
        action_mapping = {
            'move': 'move_towards_direction',
            'set_sprite': 'set_sprite',
            'destroy_instance': 'destroy_instance',
            'create_instance': 'create_instance',
            'play_sound': 'play_sound',
        }
        
        mapped_action = action_mapping.get(action_type, action_type)
        
        return {
            'action': mapped_action,
            'parameters': parameters
        }
    
    def _handle_condition_node(self, node: VisualNode, visited: set) -> List[Dict[str, Any]]:
        """Handle conditional branching"""
        actions = []
        
        if not hasattr(node, 'condition_type'):
            return actions
        
        # Get parameters
        parameters = {}
        for input_port in node.input_ports:
            if input_port.port_type == PortType.DATA_IN:
                value = self._get_port_value(input_port)
                if value is not None:
                    parameters[input_port.name] = value
                elif input_port.name in node.parameters:
                    parameters[input_port.name] = node.parameters[input_port.name]
        
        # Find true and false branches
        true_port = None
        false_port = None
        
        for output_port in node.output_ports:
            if output_port.name == "True":
                true_port = output_port
            elif output_port.name == "False":
                false_port = output_port
        
        # Get actions for each branch
        true_actions = []
        false_actions = []
        
        if true_port:
            true_nodes = self._get_connected_nodes(true_port)
            for true_node in true_nodes:
                true_actions.extend(self._generate_actions_from_node(true_node, visited.copy()))
        
        if false_port:
            false_nodes = self._get_connected_nodes(false_port)
            for false_node in false_nodes:
                false_actions.extend(self._generate_actions_from_node(false_node, visited.copy()))
        
        # Create conditional action
        condition_type = node.condition_type
        
        # Map to existing condition system
        if condition_type == 'if_collision':
            condition_action = {
                'action': 'if_condition',
                'parameters': {
                    'condition_type': 'collision_with',
                    'object_name': parameters.get('object', ''),
                    'true_actions': true_actions,
                    'false_actions': false_actions
                }
            }
        elif condition_type == 'if_variable':
            condition_action = {
                'action': 'if_condition',
                'parameters': {
                    'condition_type': 'variable',
                    'variable': parameters.get('variable', ''),
                    'operator': parameters.get('operator', '=='),
                    'value': parameters.get('value', 0),
                    'true_actions': true_actions,
                    'false_actions': false_actions
                }
            }
        elif condition_type == 'if_key_pressed':
            condition_action = {
                'action': 'if_condition',
                'parameters': {
                    'condition_type': 'key_pressed',
                    'key': parameters.get('key', ''),
                    'true_actions': true_actions,
                    'false_actions': false_actions
                }
            }
        else:
            condition_action = None
        
        if condition_action:
            actions.append(condition_action)
        
        return actions
    
    def _get_port_value(self, port) -> Any:
        """Get value from connected port"""
        if not port.connections:
            return None
        
        # Get first connection
        connection = port.connections[0]
        source_port = connection.source_port if connection.target_port == port else connection.target_port
        
        # Find source node
        source_node = self._find_node_for_port(source_port)
        if not source_node:
            return None
        
        # If source is a value node, return its value
        if hasattr(source_node, 'value_type'):
            return source_node.parameters.get('value')
        
        # If source is a variable getter, return variable name
        if hasattr(source_node, 'is_getter') and source_node.is_getter:
            return f"${source_node.variable_name}"
        
        return None
    
    def _get_next_execution_nodes(self, node: VisualNode) -> List[VisualNode]:
        """Get nodes connected via execution flow"""
        next_nodes = []
        
        # Find execution output ports
        for output_port in node.output_ports:
            if output_port.port_type == PortType.EXECUTION_OUT and output_port.name == "":
                # Get connected nodes
                connected_nodes = self._get_connected_nodes(output_port)
                next_nodes.extend(connected_nodes)
        
        return next_nodes
    
    def _get_connected_nodes(self, port) -> List[VisualNode]:
        """Get nodes connected to a port"""
        nodes = []
        
        for connection in port.connections:
            target_port = connection.target_port if connection.source_port == port else connection.source_port
            if target_port:
                node = self._find_node_for_port(target_port)
                if node:
                    nodes.append(node)
        
        return nodes
    
    def _find_node_for_port(self, port) -> Optional[VisualNode]:
        """Find node that contains a port"""
        for node in self.nodes:
            if port in node.input_ports + node.output_ports:
                return node
        return None