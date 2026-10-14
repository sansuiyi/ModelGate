package com.modelgate.service;

import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class HeuristicClassifier {

    private static final List<String> COMPLEX_KEYWORDS = List.of(
            "analyze", "evaluate", "compare", "assess", "investigate",
            "multi", "comprehensive", "detailed analysis", "liability",
            "legal", "compliance", "financial", "strategy", "recommend",
            "across multiple", "in-depth", "thoroughly", "architect",
            "design", "implement", "build", "create", "develop", "write",
            "refactor", "debug", "optimize", "security", "audit",
            "research", "essay", "report", "review", "critique",
            "feature rich", "production", "full", "complete", "entire"
    );

    private static final List<String> MEDIUM_KEYWORDS = List.of(
            "explain", "describe", "summarize", "translate", "convert",
            "difference between", "how does", "why does", "list",
            "steps to", "example of", "pros and cons", "rewrite"
    );

    private static final List<String> SIMPLE_KEYWORDS = List.of(
            "what is", "where is", "when does", "status",
            "hello", "hi ", "hey", "thanks", "help", "faq", "return policy",
            "hours", "price", "cost of", "yes", "no", "ok", "sure"
    );

    private static final List<String> CODE_SIGNALS = List.of(
            "```", "code", "function", "class", "program", "script",
            "api", "database", "algorithm", "game", "app", "application"
    );

    public String classify(String prompt) {
        String[] tokens = prompt.split("\\s+");
        int tokenCount = tokens.length;
        String promptLower = prompt.toLowerCase();

        int complexScore = 0;
        for (String kw : COMPLEX_KEYWORDS) {
            if (promptLower.contains(kw)) complexScore++;
        }

        int mediumScore = 0;
        for (String kw : MEDIUM_KEYWORDS) {
            if (promptLower.contains(kw)) mediumScore++;
        }

        int simpleScore = 0;
        for (String kw : SIMPLE_KEYWORDS) {
            if (promptLower.contains(kw)) simpleScore++;
        }

        int codeScore = 0;
        for (String kw : CODE_SIGNALS) {
            if (promptLower.contains(kw)) codeScore++;
        }

        if (tokenCount <= 5 && complexScore == 0 && codeScore == 0 && mediumScore == 0) {
            return "simple";
        }
        if (simpleScore > 0 && complexScore == 0 && codeScore == 0 && mediumScore == 0 && tokenCount < 20) {
            return "simple";
        }

        if (codeScore >= 1) {
            return "complex";
        }

        if (complexScore >= 2) {
            return "complex";
        }
        if (complexScore >= 1 && tokenCount > 25) {
            return "complex";
        }
        if (tokenCount > 80) {
            return "complex";
        }

        if (mediumScore >= 1 || tokenCount > 30) {
            return "medium";
        }
        if (complexScore >= 1) {
            return "medium";
        }

        return "simple";
    }
}
