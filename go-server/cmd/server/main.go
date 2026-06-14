// Package main provides the entry point for the CodeDiffAnalyzer backend server.
package main

import (
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/codediffanalyzer/go-server/internal/rpc"
	"github.com/codediffanalyzer/go-server/internal/web"
)

func main() {
	// 1. 初始化 gRPC 客户端连接到 Python 引擎
	rpcTarget := os.Getenv("PYTHON_ENGINE_ADDR")
	if rpcTarget == "" {
		rpcTarget = "localhost:50051"
	}
	
	rpcClient, err := rpc.NewPythonEngineClient(rpcTarget)
	if err != nil {
		log.Fatalf("Failed to connect to Python engine: %v", err)
	}
	defer rpcClient.Close()
	log.Printf("Connected to Python engine at %s", rpcTarget)

	// 2. 初始化 Web Handler
	webServer := web.NewWebServer(rpcClient)

	// 3. 配置路由
	mux := http.NewServeMux()
	
	// 静态文件服务
	fileServer := http.FileServer(http.Dir("./static"))
	mux.Handle("/static/", http.StripPrefix("/static/", fileServer))
	
	// 页面和 API
	mux.HandleFunc("/", webServer.HandleIndex)
	mux.HandleFunc("/api/analyze", webServer.HandleAnalyze)
	mux.HandleFunc("/api/stream-progress", webServer.HandleStreamProgress)

	// 4. 启动 HTTP 服务
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	server := &http.Server{
		Addr:    ":" + port,
		Handler: mux,
	}

	go func() {
		log.Printf("CodeDiffAnalyzer Web Server is listening on http://localhost:%s", port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("HTTP server failed: %v", err)
		}
	}()

	// 5. 优雅关机
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")
	server.Close()
}
