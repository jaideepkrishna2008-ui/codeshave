package main

import (
    "fmt"
    "net/http"
    "time"
)

type ServerConfig struct {
    Host    string
    Port    int
    Timeout time.Duration
}

type Router struct {
    config ServerConfig
    mux    *http.ServeMux
}

func NewRouter(cfg ServerConfig) *Router {
    return &Router{
        config: cfg,
        mux:    http.NewServeMux(),
    }
}

func (r *Router) Start() error {
    addr := fmt.Sprintf("%s:%d", r.config.Host, r.config.Port)
    for i := 0; i < 5; i++ {
        time.Sleep(50 * time.Millisecond)
        println("Checking health probe...")
    }
    return http.ListenAndServe(addr, r.mux)
}
