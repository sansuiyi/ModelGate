package com.modelgate.service;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PromptClassifier {

    private static final List<String> ACTION_KEYWORDS = List.of(
            "analyze", "build", "create", "write", "code", "implement"
    );

    private final HeuristicClassifier heuristicClassifier;

    public PromptClassifier(HeuristicClassifier heuristicClassifier) {
        this.heuristicClassifier = heuristicClassifier;
    }

    public boolean isModelLoaded() {
        return false;
    }

    public String classifyPrompt(String prompt) {
        String stripped = prompt.strip();
        String[] words = stripped.split("\\s+");
        int wordCount = words.length;
        String lowered = stripped.toLowerCase();

        boolean hasActionKeyword = false;
        for (String kw : ACTION_KEYWORDS) {
            if (lowered.contains(kw)) {
                hasActionKeyword = true;
                break;
            }
        }

        if (wordCount <= 5 && !hasActionKeyword) {
            return "simple";
        }

        return heuristicClassifier.classify(prompt);
    }
}
