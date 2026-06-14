import typing
import networkx as nx
from core import analyzer_pb2

def detect_communities(ast_tree: analyzer_pb2.ASTTree) -> list[analyzer_pb2.Community]:
    """
    基于 AST 结构，使用 NetworkX 的 Louvain 算法识别高内聚模块/社区。
    我们将拥有父子关系的 AST 节点（主要是函数、类级别的节点）视为无向边。
    """
    if not ast_tree.nodes:
        return []

    G = typing.cast(typing.Any, nx).Graph() # type: ignore
    nodes_by_id: dict[int, analyzer_pb2.ASTNode] = {n.id: n for n in ast_tree.nodes}
    
    # 构建结构图
    for node in ast_tree.nodes:
        G.add_node(node.id, label=node.label) # type: ignore
        for child_id in node.children:
            G.add_edge(node.id, child_id) # type: ignore

    if len(G.nodes) == 0: # type: ignore
        return []

    # 运行 Louvain 社区发现算法
    try:
        communities: typing.Iterable[typing.Iterable[int]] = typing.cast(typing.Any, nx).community.louvain_communities(G) # type: ignore
    except Exception as e:
        print(f"Louvain algorithm error: {e}")
        return []

    results: list[analyzer_pb2.Community] = []
    for i, comm in enumerate(communities):
        members: list[str] = []
        for node_id in comm:
            pb_node = nodes_by_id.get(node_id)
            # 仅提取核心标识符作为社区成员表示
            if pb_node and len(pb_node.label) > 1 and pb_node.type in (
                analyzer_pb2.NODE_TYPE_FUNCTION, 
                analyzer_pb2.NODE_TYPE_CLASS, 
                analyzer_pb2.NODE_TYPE_VARIABLE
            ):
                members.append(pb_node.label)
        
        # 去重
        members = list(set(members))
        if members:
            # 计算简单内聚度：社区节点数 / 图总节点数
            cohesion = len(list(comm)) / len(G.nodes) # type: ignore
            results.append(analyzer_pb2.Community(
                id=i+1,
                members=members,
                cohesion=float(cohesion)
            ))

    return results
