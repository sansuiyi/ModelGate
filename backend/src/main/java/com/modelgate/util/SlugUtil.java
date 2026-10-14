package com.modelgate.util;

import java.util.regex.Pattern;

public class SlugUtil {

    private static final Pattern NON_ALPHANUMERIC = Pattern.compile("[^a-z0-9]+");
    private static final Pattern TRAILING_HYPHEN = Pattern.compile("^-+|-+$");

    public static String slugify(String name) {
        if (name == null) {
            return "";
        }
        String slug = name.toLowerCase().trim();
        slug = NON_ALPHANUMERIC.matcher(slug).replaceAll("-");
        slug = TRAILING_HYPHEN.matcher(slug).replaceAll("");
        return slug;
    }
}
