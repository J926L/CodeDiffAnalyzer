// Package parser handles source code parsing and AST generation using tree-sitter.
package parser

import (
	"context"
	"fmt"
	"sync/atomic"

	pb "github.com/codediffanalyzer/go-server/proto/analyzerpb"
	sitter "github.com/smacker/go-tree-sitter"
	"github.com/smacker/go-tree-sitter/golang"
)

// ParseFileToAST parses a go source code string into the protobuf ASTTree format
func ParseFileToAST(ctx context.Context, filePath, commitID string, sourceCode []byte) (*pb.ASTTree, error) {
	parser := sitter.NewParser()
	parser.SetLanguage(golang.GetLanguage())

	tree, err := parser.ParseCtx(ctx, nil, sourceCode)
	if err != nil {
		return nil, fmt.Errorf("failed to parse file %s: %w", filePath, err)
	}

	rootNode := tree.RootNode()

	astTree := &pb.ASTTree{
		FilePath: filePath,
		CommitId: commitID,
		Nodes:    make([]*pb.ASTNode, 0),
	}

	var nodeCounter int32 = 0

	// Pre-order traversal to populate the AST nodes
	var traverse func(node *sitter.Node) int32
	traverse = func(node *sitter.Node) int32 {
		id := atomic.AddInt32(&nodeCounter, 1)

		var pbType pb.NodeType
		nodeTypeStr := node.Type()
		// Simple heuristic mapping
		switch nodeTypeStr {
		case "function_declaration", "method_declaration":
			pbType = pb.NodeType_NODE_TYPE_FUNCTION
		case "type_declaration", "struct_type", "interface_type":
			pbType = pb.NodeType_NODE_TYPE_CLASS
		case "identifier":
			pbType = pb.NodeType_NODE_TYPE_VARIABLE
		case "block", "statement_list":
			pbType = pb.NodeType_NODE_TYPE_BLOCK
		case "parameter_list", "parameter_declaration":
			pbType = pb.NodeType_NODE_TYPE_PARAMETER
		case "comment":
			pbType = pb.NodeType_NODE_TYPE_COMMENT
		case "import_declaration", "import_spec":
			pbType = pb.NodeType_NODE_TYPE_IMPORT
		default:
			if node.IsNamed() {
				pbType = pb.NodeType_NODE_TYPE_STATEMENT
			} else {
				pbType = pb.NodeType_NODE_TYPE_EXPRESSION
			}
		}

		label := nodeTypeStr
		if node.Type() == "identifier" || node.Type() == "string_literal" {
			label = node.Content(sourceCode)
		}

		pbNode := &pb.ASTNode{
			Id:        id,
			Type:      pbType,
			Label:     label,
			StartLine: int32(node.StartPoint().Row + 1), // 1-indexed for protobuf
			EndLine:   int32(node.EndPoint().Row + 1),
			Children:  make([]int32, 0, node.ChildCount()),
		}

		// Keep track of index in the slice (which is id - 1)
		nodeIndex := id - 1
		astTree.Nodes = append(astTree.Nodes, nil) // placeholder

		for i := 0; i < int(node.ChildCount()); i++ {
			child := node.Child(i)
			childID := traverse(child)
			pbNode.Children = append(pbNode.Children, childID)
		}

		astTree.Nodes[nodeIndex] = pbNode
		return id
	}

	rootID := traverse(rootNode)
	astTree.RootId = rootID

	return astTree, nil
}
