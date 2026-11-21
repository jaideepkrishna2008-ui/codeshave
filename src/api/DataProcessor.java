package com.example.api;

import java.util.List;
import java.util.ArrayList;
import java.io.IOException;

public class DataProcessor {
    private final String endpoint;
    private boolean isReady;

    public DataProcessor(String endpoint) {
        this.endpoint = endpoint;
        this.isReady = false;
        System.out.println("Processor initialized for " + endpoint);
    }

    public List<String> processBatch(List<String> records) throws IOException {
        List<String> results = new ArrayList<>();
        for (String record : records) {
            String processed = record.trim().toUpperCase();
            results.add(processed);
        }
        return results;
    }
}
