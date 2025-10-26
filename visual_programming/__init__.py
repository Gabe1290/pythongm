"""
Visual Programming System
Node-based visual scripting for GameMaker IDE
"""

from .visual_node import VisualNode, NodePort, PortType
from .visual_canvas import VisualCanvas
from .connection import NodeConnection
from .node_types import NodeTypeDefinition, get_node_types, create_node_from_type
from .code_generator import VisualCodeGenerator
from .node_palette import NodePalette
from .node_properties import NodePropertiesPanel

__all__ = [
    'VisualNode',
    'NodePort',
    'PortType',
    'VisualCanvas',
    'NodeConnection',
    'NodeTypeDefinition',
    'get_node_types',
    'create_node_from_type',
    'VisualCodeGenerator',
    'NodePalette',
    'NodePropertiesPanel'
]