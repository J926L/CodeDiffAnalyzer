// Package web contains HTTP handlers, routing, and SSE logic for the web UI.
package web

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/codediffanalyzer/go-server/internal/parser"
	"github.com/codediffanalyzer/go-server/internal/rpc"
	pb "github.com/codediffanalyzer/go-server/proto/analyzerpb"
)

type WebServer struct {
	Templates  *template.Template
	RpcClient  *rpc.PythonEngineClient
	TaskStatus map[string]*TaskContext
	mu         sync.Mutex
}

type TaskContext struct {
	ID        string
	Progress  chan *pb.ProgressEvent
	Result    *pb.AnalyzeResult
	GraphData string
	Error     error
	Done      chan struct{}
}

func NewWebServer(rpcClient *rpc.PythonEngineClient) *WebServer {
	funcMap := template.FuncMap{
		"mul": func(a, b float64) float64 {
			return a * b
		},
	}

	// 预编译模板，在解析前注册自定义函数
	tmpl := template.New("").Funcs(funcMap)
	tmpl = template.Must(tmpl.ParseGlob("templates/*.html"))
	tmpl = template.Must(tmpl.ParseGlob("templates/layouts/*.html"))
	tmpl = template.Must(tmpl.ParseGlob("templates/partials/*.html"))

	return &WebServer{
		Templates:  tmpl,
		RpcClient:  rpcClient,
		TaskStatus: make(map[string]*TaskContext),
	}
}

// 渲染首页
func (s *WebServer) HandleIndex(w http.ResponseWriter, r *http.Request) {
	if err := s.Templates.ExecuteTemplate(w, "index.html", nil); err != nil {
		log.Printf("Template render error: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}
}

// 处理表单提交，触发分析任务
func (s *WebServer) HandleAnalyze(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	repoPath := r.FormValue("repo_path")
	filePath := r.FormValue("file_path")
	oldCommit := r.FormValue("old_commit")
	newCommit := r.FormValue("new_commit")

	taskID := fmt.Sprintf("task_%d", time.Now().UnixNano())

	taskCtx := &TaskContext{
		ID:       taskID,
		Progress: make(chan *pb.ProgressEvent, 10),
		Done:     make(chan struct{}),
	}

	s.mu.Lock()
	s.TaskStatus[taskID] = taskCtx
	s.mu.Unlock()

	// 异步启动核心分析流程
	go s.runAnalysisTask(taskCtx, repoPath, filePath, oldCommit, newCommit)

	// 立即返回带 SSE 监听的进度条片段
	if err := s.Templates.ExecuteTemplate(w, "progress", map[string]interface{}{
		"TaskID": taskID,
	}); err != nil {
		log.Printf("Template render error: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
	}
}

// 提供 SSE 流
func (s *WebServer) HandleStreamProgress(w http.ResponseWriter, r *http.Request) {
	taskID := r.URL.Query().Get("task_id")

	s.mu.Lock()
	taskCtx, exists := s.TaskStatus[taskID]
	s.mu.Unlock()

	if !exists {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported", http.StatusInternalServerError)
		return
	}

	// 持续推送进度
	for {
		select {
		case event := <-taskCtx.Progress:
			// 渲染进度条本体
			fmt.Fprintf(w, "event: progress-bar\n")
			fmt.Fprintf(w, "data: <div sse-swap=\"progress-bar\" hx-swap=\"outerHTML\" style=\"width: %d%%\" class=\"shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-brand transition-all duration-500\"></div>\n\n", event.Percent)

			// 渲染进度文本
			fmt.Fprintf(w, "event: progress-text\n")
			fmt.Fprintf(w, "data: <div sse-swap=\"progress-text\" hx-swap=\"innerHTML\" class=\"text-xs font-semibold inline-block text-brand\">%s</div>\n\n", event.Message)

			flusher.Flush()

		case <-taskCtx.Done:
			// 分析完毕，渲染最终结果并推送替换
			if taskCtx.Error != nil {
				fmt.Fprintf(w, "event: result\n")
				fmt.Fprintf(w, "data: <div sse-swap=\"result\" hx-swap=\"outerHTML\" class=\"text-red-500\">Error: %s</div>\n\n", taskCtx.Error.Error())
				flusher.Flush()
				return
			}

			// 组装传给模板的数据
			data := map[string]interface{}{
				"EditDistance":   taskCtx.Result.EditDistance,
				"DiffCount":      len(taskCtx.Result.Diffs),
				"CommunityCount": len(taskCtx.Result.Communities),
				"Diffs":          taskCtx.Result.Diffs,
				"GraphJSON":      template.JS(taskCtx.GraphData),
			}

			var buf bytes.Buffer
			if err := s.Templates.ExecuteTemplate(&buf, "result", data); err != nil {
				log.Printf("Template render error: %v", err)
			}

			fmt.Fprintf(w, "event: result\n")
			// 必须处理多行 HTML 到单行 data: 的格式
			htmlLines := bytes.Split(buf.Bytes(), []byte("\n"))
			for _, line := range htmlLines {
				fmt.Fprintf(w, "data: %s\n", line)
			}
			fmt.Fprintf(w, "\n")
			flusher.Flush()
			return

		case <-r.Context().Done():
			// 客户端断开
			return
		}
	}
}

// 真实的分析逻辑
func (s *WebServer) runAnalysisTask(task *TaskContext, repoPath, filePath, oldCommit, newCommit string) {
	defer close(task.Done)
	ctx := context.Background()

	// 模拟进度 - 读取源码
	task.Progress <- &pb.ProgressEvent{Stage: "READ", Percent: 10, Message: "正在提取源码..."}
	
	// 在真实环境中，这里应调用 Git 命令行获取不同版本的源码。这里做简单 Mock:
	var sourceOld, sourceNew []byte
	var err error
	
	if repoPath == "." {
		// 方便本地直接测试
		sourceOld, err = os.ReadFile(filepath.Join(repoPath, filePath))
		sourceNew = sourceOld
	}
	
	if err != nil {
		task.Error = err
		return
	}

	if len(sourceOld) == 0 {
		sourceOld = []byte("package main\nfunc oldFunc() {}")
		sourceNew = []byte("package main\nfunc newFunc() {}")
	}

	task.Progress <- &pb.ProgressEvent{Stage: "PARSE", Percent: 30, Message: "解析抽象语法树 (AST)..."}

	// 解析 旧 AST
	astOld, err := parser.ParseFileToAST(ctx, filePath, oldCommit, sourceOld)
	if err != nil {
		task.Error = err
		return
	}

	// 解析 新 AST
	astNew, err := parser.ParseFileToAST(ctx, filePath, newCommit, sourceNew)
	if err != nil {
		task.Error = err
		return
	}

	task.Progress <- &pb.ProgressEvent{Stage: "RPC", Percent: 60, Message: "正在进行远程 Python 语义比对..."}

	// 通过 RPC 发送给 Python
	trees := []*pb.ASTTree{astOld, astNew}
	result, err := s.RpcClient.AnalyzeAST(ctx, trees)
	if err != nil {
		task.Error = err
		return
	}

	task.Progress <- &pb.ProgressEvent{Stage: "RENDER", Percent: 90, Message: "渲染拓扑图..."}

	// 根据结果生成供 Canvas 渲染的伪数据（真实情况应由 Python 布局或在 Go 这里做力导向布局）
	task.Result = result
	
	graphObj := map[string]interface{}{
		"nodes": []map[string]interface{}{
			{"id": 1, "x": 100, "y": 100, "label": "oldFunc", "color": "#f87171"},
			{"id": 2, "x": 300, "y": 100, "label": "newFunc", "color": "#34d399"},
		},
		"edges": []map[string]interface{}{},
	}
	graphJsonBytes, _ := json.Marshal(graphObj)
	task.GraphData = string(graphJsonBytes)

	task.Progress <- &pb.ProgressEvent{Stage: "DONE", Percent: 100, Message: "分析完成"}
	time.Sleep(500 * time.Millisecond) // 给前端一点时间表现满格进度条
}
