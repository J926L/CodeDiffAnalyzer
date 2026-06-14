import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

import typing
import logging
from concurrent import futures
import grpc
from core import analyzer_pb2
from core import analyzer_pb2_grpc
from core.diff_algo import analyze_semantic_diff
from core.graph_algo import detect_communities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ASTAnalyzerServicer(analyzer_pb2_grpc.ASTAnalyzerServicer): # type: ignore
    def AnalyzeAST(self, request_iterator: typing.Iterable[analyzer_pb2.ASTTree], context: grpc.ServicerContext) -> analyzer_pb2.AnalyzeResult:
        """
        接收 Go 发来的 AST 树流，进行分析并返回结果。
        预期的流中应包含两棵树：旧版本和新版本。
        """
        trees: list[analyzer_pb2.ASTTree] = []
        try:
            for tree in request_iterator:
                trees.append(tree)
                logger.info(f"Received AST tree for file: {tree.file_path}, nodes count: {len(tree.nodes)}")
                
                # 为防止流数据过大，设定上限（此案例只处理一对树）
                if len(trees) >= 2:
                    break
                    
            if len(trees) < 2:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT) # type: ignore
                context.set_details('Expected exactly two AST trees (old and new)') # type: ignore
                return analyzer_pb2.AnalyzeResult()
                
            old_tree = trees[0]
            new_tree = trees[1]
            
            # 计算差异
            logger.info("Computing semantic diff...")
            edit_distance, diffs = analyze_semantic_diff(old_tree, new_tree)
            
            # 计算社区（基于新版本AST）
            logger.info("Detecting communities...")
            communities = detect_communities(new_tree)
            
            logger.info(f"Analysis complete. Distance: {edit_distance}, Diffs: {len(diffs)}, Communities: {len(communities)}")
            return analyzer_pb2.AnalyzeResult(
                diffs=diffs,
                communities=communities,
                edit_distance=edit_distance
            )

        except Exception as e:
            logger.error(f"Error during AnalyzeAST: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL) # type: ignore
            context.set_details(str(e)) # type: ignore
            return analyzer_pb2.AnalyzeResult()

    def StreamProgress(self, request: typing.Any, context: grpc.ServicerContext) -> typing.Any:
        # Progress 流目前由 Go 侧控制（结合 htmx SSE），
        # 接口预留在此以便未来 Python 也能够上报更细粒度的进度。
        context.set_code(grpc.StatusCode.UNIMPLEMENTED) # type: ignore
        context.set_details('Progress streaming from Python is not implemented yet.') # type: ignore
        raise NotImplementedError('Method not implemented!')

def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    typing.cast(typing.Any, analyzer_pb2_grpc).add_ASTAnalyzerServicer_to_server(ASTAnalyzerServicer(), server) # type: ignore
    server.add_insecure_port(f'0.0.0.0:{port}')
    server.start()
    logger.info(f"Python Engine gRPC server listening on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
