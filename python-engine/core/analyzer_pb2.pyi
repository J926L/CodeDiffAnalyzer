# pyright: reportMissingTypeArgument=false, reportUnknownParameterType=false
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NodeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NODE_TYPE_UNSPECIFIED: _ClassVar[NodeType]
    NODE_TYPE_FUNCTION: _ClassVar[NodeType]
    NODE_TYPE_CLASS: _ClassVar[NodeType]
    NODE_TYPE_VARIABLE: _ClassVar[NodeType]
    NODE_TYPE_STATEMENT: _ClassVar[NodeType]
    NODE_TYPE_EXPRESSION: _ClassVar[NodeType]
    NODE_TYPE_BLOCK: _ClassVar[NodeType]
    NODE_TYPE_PARAMETER: _ClassVar[NodeType]
    NODE_TYPE_IMPORT: _ClassVar[NodeType]
    NODE_TYPE_COMMENT: _ClassVar[NodeType]

class ChangeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHANGE_TYPE_UNSPECIFIED: _ClassVar[ChangeType]
    CHANGE_TYPE_RENAME: _ClassVar[ChangeType]
    CHANGE_TYPE_EXTRACT_FUNCTION: _ClassVar[ChangeType]
    CHANGE_TYPE_CONTROL_FLOW: _ClassVar[ChangeType]
    CHANGE_TYPE_ADD: _ClassVar[ChangeType]
    CHANGE_TYPE_DELETE: _ClassVar[ChangeType]
    CHANGE_TYPE_MOVE: _ClassVar[ChangeType]
NODE_TYPE_UNSPECIFIED: NodeType
NODE_TYPE_FUNCTION: NodeType
NODE_TYPE_CLASS: NodeType
NODE_TYPE_VARIABLE: NodeType
NODE_TYPE_STATEMENT: NodeType
NODE_TYPE_EXPRESSION: NodeType
NODE_TYPE_BLOCK: NodeType
NODE_TYPE_PARAMETER: NodeType
NODE_TYPE_IMPORT: NodeType
NODE_TYPE_COMMENT: NodeType
CHANGE_TYPE_UNSPECIFIED: ChangeType
CHANGE_TYPE_RENAME: ChangeType
CHANGE_TYPE_EXTRACT_FUNCTION: ChangeType
CHANGE_TYPE_CONTROL_FLOW: ChangeType
CHANGE_TYPE_ADD: ChangeType
CHANGE_TYPE_DELETE: ChangeType
CHANGE_TYPE_MOVE: ChangeType

class ASTNode(_message.Message):
    __slots__ = ("id", "type", "label", "start_line", "end_line", "children")
    ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    START_LINE_FIELD_NUMBER: _ClassVar[int]
    END_LINE_FIELD_NUMBER: _ClassVar[int]
    CHILDREN_FIELD_NUMBER: _ClassVar[int]
    id: int
    type: NodeType
    label: str
    start_line: int
    end_line: int
    children: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., type: _Optional[_Union[NodeType, str]] = ..., label: _Optional[str] = ..., start_line: _Optional[int] = ..., end_line: _Optional[int] = ..., children: _Optional[_Iterable[int]] = ...) -> None: ...

class ASTTree(_message.Message):
    __slots__ = ("file_path", "commit_id", "nodes", "root_id")
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    COMMIT_ID_FIELD_NUMBER: _ClassVar[int]
    NODES_FIELD_NUMBER: _ClassVar[int]
    ROOT_ID_FIELD_NUMBER: _ClassVar[int]
    file_path: str
    commit_id: str
    nodes: _containers.RepeatedCompositeFieldContainer[ASTNode]
    root_id: int
    def __init__(self, file_path: _Optional[str] = ..., commit_id: _Optional[str] = ..., nodes: _Optional[_Iterable[_Union[ASTNode, _Mapping]]] = ..., root_id: _Optional[int] = ...) -> None: ...

class AnalyzeRequest(_message.Message):
    __slots__ = ("repo_path", "file_path", "old_commit", "new_commit")
    REPO_PATH_FIELD_NUMBER: _ClassVar[int]
    FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    OLD_COMMIT_FIELD_NUMBER: _ClassVar[int]
    NEW_COMMIT_FIELD_NUMBER: _ClassVar[int]
    repo_path: str
    file_path: str
    old_commit: str
    new_commit: str
    def __init__(self, repo_path: _Optional[str] = ..., file_path: _Optional[str] = ..., old_commit: _Optional[str] = ..., new_commit: _Optional[str] = ...) -> None: ...

class SemanticDiff(_message.Message):
    __slots__ = ("change_type", "description", "old_node", "new_node", "confidence")
    CHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OLD_NODE_FIELD_NUMBER: _ClassVar[int]
    NEW_NODE_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    change_type: ChangeType
    description: str
    old_node: ASTNode
    new_node: ASTNode
    confidence: float
    def __init__(self, change_type: _Optional[_Union[ChangeType, str]] = ..., description: _Optional[str] = ..., old_node: _Optional[_Union[ASTNode, _Mapping]] = ..., new_node: _Optional[_Union[ASTNode, _Mapping]] = ..., confidence: _Optional[float] = ...) -> None: ...

class Community(_message.Message):
    __slots__ = ("id", "members", "cohesion")
    ID_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    COHESION_FIELD_NUMBER: _ClassVar[int]
    id: int
    members: _containers.RepeatedScalarFieldContainer[str]
    cohesion: float
    def __init__(self, id: _Optional[int] = ..., members: _Optional[_Iterable[str]] = ..., cohesion: _Optional[float] = ...) -> None: ...

class AnalyzeResult(_message.Message):
    __slots__ = ("diffs", "communities", "edit_distance")
    DIFFS_FIELD_NUMBER: _ClassVar[int]
    COMMUNITIES_FIELD_NUMBER: _ClassVar[int]
    EDIT_DISTANCE_FIELD_NUMBER: _ClassVar[int]
    diffs: _containers.RepeatedCompositeFieldContainer[SemanticDiff]
    communities: _containers.RepeatedCompositeFieldContainer[Community]
    edit_distance: float
    def __init__(self, diffs: _Optional[_Iterable[_Union[SemanticDiff, _Mapping]]] = ..., communities: _Optional[_Iterable[_Union[Community, _Mapping]]] = ..., edit_distance: _Optional[float] = ...) -> None: ...

class ProgressEvent(_message.Message):
    __slots__ = ("stage", "percent", "message")
    STAGE_FIELD_NUMBER: _ClassVar[int]
    PERCENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    stage: str
    percent: int
    message: str
    def __init__(self, stage: _Optional[str] = ..., percent: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

