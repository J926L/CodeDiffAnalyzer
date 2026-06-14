from core import analyzer_pb2
import typing

def create_mock_node(id: int, type: typing.Any, label: str, start_line: int = 1, end_line: int = 1, children: list[int] | None = None) -> analyzer_pb2.ASTNode:
    if children is None:
        children = []
    return analyzer_pb2.ASTNode(
        id=id,
        type=type,
        label=label,
        start_line=start_line,
        end_line=end_line,
        children=children
    )

def generate_mock_old_ast() -> analyzer_pb2.ASTTree:
    """
    func process() {
       a := 1
    }
    """
    nodes: list[analyzer_pb2.ASTNode] = [
        create_mock_node(1, analyzer_pb2.NODE_TYPE_FUNCTION, "process", children=[2]),
        create_mock_node(2, analyzer_pb2.NODE_TYPE_BLOCK, "block", children=[3]),
        create_mock_node(3, analyzer_pb2.NODE_TYPE_VARIABLE, "a")
    ]
    return analyzer_pb2.ASTTree(file_path="main.go", commit_id="v1", root_id=1, nodes=nodes)

def generate_mock_new_ast_rename() -> analyzer_pb2.ASTTree:
    """
    func processData() {
       a := 1
    }
    """
    nodes: list[analyzer_pb2.ASTNode] = [
        create_mock_node(1, analyzer_pb2.NODE_TYPE_FUNCTION, "processData", children=[2]),
        create_mock_node(2, analyzer_pb2.NODE_TYPE_BLOCK, "block", children=[3]),
        create_mock_node(3, analyzer_pb2.NODE_TYPE_VARIABLE, "a")
    ]
    return analyzer_pb2.ASTTree(file_path="main.go", commit_id="v2", root_id=1, nodes=nodes)

def generate_mock_new_ast_add() -> analyzer_pb2.ASTTree:
    """
    func process() {
       a := 1
       b := 2
    }
    """
    nodes: list[analyzer_pb2.ASTNode] = [
        create_mock_node(1, analyzer_pb2.NODE_TYPE_FUNCTION, "process", children=[2]),
        create_mock_node(2, analyzer_pb2.NODE_TYPE_BLOCK, "block", children=[3, 4]),
        create_mock_node(3, analyzer_pb2.NODE_TYPE_VARIABLE, "a"),
        create_mock_node(4, analyzer_pb2.NODE_TYPE_VARIABLE, "b")
    ]
    return analyzer_pb2.ASTTree(file_path="main.go", commit_id="v3", root_id=1, nodes=nodes)

