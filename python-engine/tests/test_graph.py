from core.graph_algo import detect_communities
from core import analyzer_pb2
from tests.mock_data import create_mock_node

def test_detect_communities():
    # 构造一个强耦合的 AST 树作为 Mock
    # Root -> [FuncA, FuncB]
    # FuncA -> [Var1, Var2]
    nodes = [
        create_mock_node(1, analyzer_pb2.NODE_TYPE_BLOCK, "root", children=[2, 3]),
        create_mock_node(2, analyzer_pb2.NODE_TYPE_FUNCTION, "FuncA", children=[4, 5]),
        create_mock_node(3, analyzer_pb2.NODE_TYPE_FUNCTION, "FuncB", children=[]),
        create_mock_node(4, analyzer_pb2.NODE_TYPE_VARIABLE, "Var1"),
        create_mock_node(5, analyzer_pb2.NODE_TYPE_VARIABLE, "Var2"),
    ]
    tree = analyzer_pb2.ASTTree(root_id=1, nodes=nodes)
    
    communities = detect_communities(tree)
    
    # Louvain 应至少将高度连接的 FuncA 和其内部变量划入某个社区
    assert len(communities) > 0
    # 验证社区内部含有正确类型的成员
    found_funcA = any("FuncA" in c.members for c in communities)
    assert found_funcA
