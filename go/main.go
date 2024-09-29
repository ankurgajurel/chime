package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"net"
)

type Request struct {
	Command string            `json:"command"`
	Args    map[string]string `json:"args"`
}

type Response struct {
	Message string `json:"message"`
}

type Server struct {
	connections []net.Conn
	users       map[string]*net.Conn
}

func (s *Server) addConn(conn net.Conn) {
	s.connections = append(s.connections, conn)
	log.Println("New client registered", conn.RemoteAddr().String())
}

func (s *Server) register(username string, conn *net.Conn) *Response {
	_, ok := s.users[username]
	if ok {
		return &Response{
			Message: "User already exists.",
		}
	}

	s.users[username] = conn
	log.Println("New user registered:", username)
	return &Response{
		Message: "User Registered",
	}
}

func (s *Server) sendMessageAll(res *Response) error {
	for _, conn := range s.connections {
		sendMessage(res, conn)
	}

	return nil
}

func sendMessage(res *Response, conn net.Conn) error {
	writer := bufio.NewWriter(conn)
	resText, err := json.Marshal(res)
	if err != nil {
		return err
	}
	_, err = writer.Write(append(resText, '\n'))
	if err != nil {
		return err
	}
	if err = writer.Flush(); err != nil {
		return err
	}

	return nil
}

func (s *Server) handleRequest(req *Request, conn *net.Conn) {
	switch req.Command {
	case "sendAll":
		res := &Response{Message: req.Args["message"]}
		s.sendMessageAll(res)
		log.Println("Sent a message to all clients.")

	case "register":
		res := s.register(req.Args["username"], conn)
		sendMessage(res, *conn)

	case "whisper":
		recvConn := s.users[req.Args["sendTo"]]
		sendMessage(&Response{Message: req.Args["message"]}, *recvConn)
		sendMessage(&Response{Message: fmt.Sprintf("Sent Message to %s", req.Args["sendTo"])}, *conn)

	default:
		log.Println("Invalid Request")
	}
}

func (s *Server) handleConnection(conn net.Conn) {
	reader := bufio.NewReader(conn)
	for {
		text, err := reader.ReadString('\n')
		if err != nil {
			log.Println("Connection Closed")
			break
		}

		var req Request
		json.Unmarshal([]byte(text), &req)
		s.handleRequest(&req, &conn)
	}
}

func main() {
	ln, err := net.Listen("tcp", ":3009")

	if err != nil {
		fmt.Println(err)
	}

	server := &Server{
		users: make(map[string]*net.Conn),
	}

	for {
		conn, err := ln.Accept()

		if err != nil {
			fmt.Println(err)
		}

		server.addConn(conn)

		go server.handleConnection(conn)
	}
}
