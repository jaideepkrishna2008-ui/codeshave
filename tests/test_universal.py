"""
Unit tests for multi-language code compression and universal skeletonization.
"""

from codeshave.languages import compress_code, detect_language, skeletonize_curly, skeletonize_ruby


def test_detect_language():
    assert detect_language("app.ts") == "typescript"
    assert detect_language("server.go") == "go"
    assert detect_language("lib.rs") == "rust"
    assert detect_language("Main.java") == "java"
    assert detect_language("calc.cpp") == "cpp"
    assert detect_language("script.py") == "python"
    assert detect_language("app.rb") == "ruby"
    assert detect_language("deploy.sh") == "bash"


def test_typescript_skeleton():
    ts_code = """
import { useState } from 'react';

export interface User {
    id: string;
    name: string;
}

export class UserService {
    private url: string;
    constructor(url: string) {
        this.url = url;
    }
    async fetchUser(id: string): Promise<User> {
        const res = await fetch(`/api/${id}`);
        return await res.json();
    }
}

export const helper = (x: number): number => {
    return x * 2;
};
"""
    result = compress_code(ts_code, filename_or_ext="test.ts")
    assert "import { useState } from 'react';" in result
    assert "export interface User {" in result
    assert "id: string;" in result
    assert "constructor(url: string) { /* ... */ }" in result
    assert "async fetchUser(id: string): Promise<User> { /* ... */ }" in result
    assert "export const helper = (x: number): number => { /* ... */ };" in result
    assert "const res = await fetch" not in result


def test_go_skeleton():
    go_code = """
package main

import "fmt"

type Config struct {
    Host string
    Port int
}

func (c *Config) Address() string {
    return fmt.Sprintf("%s:%d", c.Host, c.Port)
}

func Start() error {
    println("starting")
    return nil
}
"""
    result = compress_code(go_code, filename_or_ext="main.go")
    assert "package main" in result
    assert "type Config struct {" in result
    assert "Host string" in result
    assert "func (c *Config) Address() string { /* ... */ }" in result
    assert "func Start() error { /* ... */ }" in result
    assert 'println("starting")' not in result


def test_rust_skeleton():
    rust_code = """
pub struct Point {
    pub x: f64,
    pub y: f64,
}

impl Point {
    pub fn new(x: f64, y: f64) -> Self {
        Point { x, y }
    }
    pub fn distance(&self) -> f64 {
        (self.x * self.x + self.y * self.y).sqrt()
    }
}
"""
    result = compress_code(rust_code, filename_or_ext="point.rs")
    assert "pub struct Point {" in result
    assert "pub x: f64," in result
    assert "impl Point {" in result
    assert "pub fn new(x: f64, y: f64) -> Self { /* ... */ }" in result
    assert "pub fn distance(&self) -> f64 { /* ... */ }" in result
    assert "Point { x, y }" not in result


def test_java_skeleton():
    java_code = """
package com.demo;

public class MathUtils {
    public static int add(int a, int b) {
        int sum = a + b;
        return sum;
    }
}
"""
    result = compress_code(java_code, filename_or_ext="MathUtils.java")
    assert "package com.demo;" in result
    assert "public class MathUtils {" in result
    assert "public static int add(int a, int b) { /* ... */ }" in result
    assert "int sum = a + b;" not in result


def test_cpp_skeleton():
    cpp_code = """
#include <iostream>

class Engine {
public:
    Engine() {
        setup();
    }
    void run() {
        execute();
    }
};
"""
    result = compress_code(cpp_code, filename_or_ext="engine.cpp")
    assert "#include <iostream>" in result
    assert "class Engine {" in result
    assert "Engine() { /* ... */ }" in result
    assert "void run() { /* ... */ }" in result
    assert "execute();" not in result


def test_ruby_skeleton():
    ruby_code = """
class Greeter
  def initialize(name)
    @name = name
  end

  def greet
    puts "Hello #{@name}"
  end
end
"""
    result = compress_code(ruby_code, filename_or_ext="greeter.rb")
    assert "class Greeter" in result
    assert "def initialize(name)" in result
    assert "def greet" in result
    assert "@name = name" not in result
