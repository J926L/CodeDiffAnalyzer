// Package rpc provides gRPC client utilities to communicate with the Python engine.
package rpc

import (
	"context"
	"fmt"
	"log"
	"time"

	pb "github.com/codediffanalyzer/go-server/proto/analyzerpb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/keepalive"
)

// PythonEngineClient 封装与 Python 分析引擎的通信
type PythonEngineClient struct {
	conn   *grpc.ClientConn
	client pb.ASTAnalyzerClient
}

// NewPythonEngineClient 创建 gRPC 客户端连接
func NewPythonEngineClient(target string) (*PythonEngineClient, error) {
	kacp := keepalive.ClientParameters{
		Time:                10 * time.Second, // 10秒不活动后发送 ping
		Timeout:             time.Second,      // 1秒等待 ping ack
		PermitWithoutStream: true,             // 即使没有活跃流也发送
	}

	opts := []grpc.DialOption{
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithKeepaliveParams(kacp),
	}

	conn, err := grpc.NewClient(target, opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to dial python engine: %w", err)
	}

	return &PythonEngineClient{
		conn:   conn,
		client: pb.NewASTAnalyzerClient(conn),
	}, nil
}

// Close 关闭底层的 gRPC 连接
func (c *PythonEngineClient) Close() error {
	return c.conn.Close()
}

// AnalyzeAST 调用远程方法分析 AST 树流
func (c *PythonEngineClient) AnalyzeAST(ctx context.Context, trees []*pb.ASTTree) (*pb.AnalyzeResult, error) {
	stream, err := c.client.AnalyzeAST(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to open stream: %w", err)
	}

	for _, tree := range trees {
		if err := stream.Send(tree); err != nil {
			return nil, fmt.Errorf("failed to send tree to stream: %w", err)
		}
	}

	result, err := stream.CloseAndRecv()
	if err != nil {
		return nil, fmt.Errorf("failed to close and recv: %w", err)
	}

	return result, nil
}

// StreamProgress 请求进度更新并传入 handler
func (c *PythonEngineClient) StreamProgress(ctx context.Context, req *pb.AnalyzeRequest, handler func(*pb.ProgressEvent)) error {
	stream, err := c.client.StreamProgress(ctx, req)
	if err != nil {
		return fmt.Errorf("failed to start progress stream: %w", err)
	}

	for {
		event, err := stream.Recv()
		if err != nil {
			// io.EOF is mapped to grpc status code if normal, but stream.Recv returns io.EOF typically or err
			log.Printf("progress stream closed/error: %v", err)
			break
		}
		handler(event)
	}

	return nil
}
