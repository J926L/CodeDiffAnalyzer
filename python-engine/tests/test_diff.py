from core.diff_algo import analyze_semantic_diff
from core import analyzer_pb2
from tests.mock_data import generate_mock_old_ast, generate_mock_new_ast_rename, generate_mock_new_ast_add

def test_analyze_semantic_diff_rename():
    old_tree = generate_mock_old_ast()
    new_tree = generate_mock_new_ast_rename()
    
    dist, diffs = analyze_semantic_diff(old_tree, new_tree)
    
    # 期望有1次更新操作（重命名）
    assert dist == 1.0
    assert len(diffs) == 1
    assert diffs[0].change_type == analyzer_pb2.CHANGE_TYPE_RENAME
    assert diffs[0].old_node.label == "process"
    assert diffs[0].new_node.label == "processData"

def test_analyze_semantic_diff_add():
    old_tree = generate_mock_old_ast()
    new_tree = generate_mock_new_ast_add()
    
    dist, diffs = analyze_semantic_diff(old_tree, new_tree)
    
    # 期望有1次插入操作
    assert dist == 1.0
    assert len(diffs) == 1
    assert diffs[0].change_type == analyzer_pb2.CHANGE_TYPE_ADD
    assert diffs[0].new_node.label == "b"
