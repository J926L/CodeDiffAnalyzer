import typing
import zss # type: ignore
from core import analyzer_pb2

class ASTNodeWrapper:
    def __init__(self, pb_node: analyzer_pb2.ASTNode) -> None:
        self.pb_node: analyzer_pb2.ASTNode = pb_node
        self.children: list['ASTNodeWrapper'] = []
        # 将类型和标签结合，确保比较精确
        self.label: str = f"{pb_node.type}:{pb_node.label}"

    @staticmethod
    def get_children(node: 'ASTNodeWrapper') -> list['ASTNodeWrapper']:
        return node.children

    @staticmethod
    def get_label(node: 'ASTNodeWrapper') -> str:
        return node.label

    def addkid(self, node: 'ASTNodeWrapper', before: bool = False) -> 'ASTNodeWrapper':
        if before:
            self.children.insert(0, node)
        else:
            self.children.append(node)
        return self

def build_zss_tree(ast_tree: analyzer_pb2.ASTTree) -> ASTNodeWrapper | None:
    if not ast_tree.nodes:
        return None
        
    nodes_by_id: dict[int, analyzer_pb2.ASTNode] = {n.id: n for n in ast_tree.nodes}
    
    def traverse(node_id: int) -> ASTNodeWrapper | None:
        if node_id not in nodes_by_id:
            return None
        pb_node = nodes_by_id[node_id]
        zss_node = ASTNodeWrapper(pb_node)
        for child_id in pb_node.children:
            child_zss = traverse(child_id)
            if child_zss:
                zss_node.addkid(child_zss)
        return zss_node
    
    return traverse(ast_tree.root_id)

def analyze_semantic_diff(old_tree: analyzer_pb2.ASTTree, new_tree: analyzer_pb2.ASTTree) -> tuple[float, list[analyzer_pb2.SemanticDiff]]:
    old_zss = build_zss_tree(old_tree)
    new_zss = build_zss_tree(new_tree)
    
    if not old_zss or not new_zss:
        return 0.0, []
        
    # 计算树编辑距离
    def get_insert_cost(node: typing.Any) -> int: return 1
    def get_remove_cost(node: typing.Any) -> int: return 1
    def get_update_cost(a: ASTNodeWrapper, b: ASTNodeWrapper) -> int:
        return 0 if a.label == b.label else 1
        
    dist, ops = typing.cast(typing.Any, zss).distance( # type: ignore
        old_zss, new_zss, 
        ASTNodeWrapper.get_children, 
        insert_cost=get_insert_cost, 
        remove_cost=get_remove_cost, 
        update_cost=get_update_cost,
        return_operations=True
    )
    
    diffs: list[analyzer_pb2.SemanticDiff] = []
    # zss.distance with return_operations=True returns list of Operations
    for op in typing.cast(typing.Iterable[typing.Any], ops): # type: ignore
        op_type = op.type # type: ignore
        zss_op = typing.cast(typing.Any, zss).Operation # type: ignore
        if op_type == zss_op.insert:
            diffs.append(analyzer_pb2.SemanticDiff(
                change_type=analyzer_pb2.CHANGE_TYPE_ADD,
                description=f"新增节点: {op.arg2.pb_node.label}", # type: ignore
                new_node=op.arg2.pb_node, # type: ignore
                confidence=1.0
            ))
        elif op_type == zss_op.remove:
            diffs.append(analyzer_pb2.SemanticDiff(
                change_type=analyzer_pb2.CHANGE_TYPE_DELETE,
                description=f"删除节点: {op.arg1.pb_node.label}", # type: ignore
                old_node=op.arg1.pb_node, # type: ignore
                confidence=1.0
            ))
        elif op_type == zss_op.update:
            if op.arg1.label != op.arg2.label: # type: ignore
                # 启发式：如果节点类型相同但标签不同，推断为重命名
                if op.arg1.pb_node.type == op.arg2.pb_node.type: # type: ignore
                    diffs.append(analyzer_pb2.SemanticDiff(
                        change_type=analyzer_pb2.CHANGE_TYPE_RENAME,
                        description=f"重命名 {op.arg1.pb_node.label} 为 {op.arg2.pb_node.label}", # type: ignore
                        old_node=op.arg1.pb_node, # type: ignore
                        new_node=op.arg2.pb_node, # type: ignore
                        confidence=0.85
                    ))
                else:
                    diffs.append(analyzer_pb2.SemanticDiff(
                        change_type=analyzer_pb2.CHANGE_TYPE_UNSPECIFIED,
                        description=f"节点修改: {op.arg1.pb_node.label} -> {op.arg2.pb_node.label}", # type: ignore
                        old_node=op.arg1.pb_node, # type: ignore
                        new_node=op.arg2.pb_node, # type: ignore
                        confidence=0.6
                    ))
    
    return float(typing.cast(float, dist)), diffs
