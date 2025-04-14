import DOMPurify from "isomorphic-dompurify";

type AttributesByTag = {
  [key: string]: string[];
};

type ClassAllowlist = {
  [key: string]: string[];
};

/**
 * Sanitizes HTML content from the Quill editor to prevent XSS attacks
 * while preserving the necessary formatting and structure.
 * @param html The HTML content to sanitize.
 * @returns Sanitized HTML string.
 */
export function sanitize_quill_html(html: string): string {
  const allowed_tags = [
    "a", "blockquote", "br", "div", "em", "h1", "h2", "h3", "h4", "h5", "h6",
    "iframe", "img", "li", "ol", "p", "pre", "span", "strong", "sub", "sup",
    "table", "tbody", "td", "tr", "ul", "select", "option", "u", "s"
  ];

  const all_attributes = [
    "class", "style", "data-language", "data-row", "data-list",
    "allowfullscreen", "frameborder", "src", "href", "target", "value", "alt"
  ];

  const attributes_by_tag: AttributesByTag = {
    "div": ["class", "style", "data-language"],
    "td": ["class", "style", "data-row"],
    "li": ["class", "style", "data-list"],
    "iframe": ["class", "style", "allowfullscreen", "frameborder", "src"],
    "a": ["class", "style", "href", "target"],
    "select": ["class", "style"],
    "option": ["class", "style", "value"],
    "img": ["class", "style", "src", "alt"],
    "p": ["class", "style"],
    "span": ["class", "style"],
    "h1": ["class", "style"],
    "h2": ["class", "style"],
    "h3": ["class", "style"],
    "h4": ["class", "style"],
    "h5": ["class", "style"],
    "h6": ["class", "style"],
    "blockquote": ["class", "style"],
    "pre": ["class", "style"],
    "ol": ["class", "style"],
    "ul": ["class", "style"],
    "table": ["class", "style"],
    "tbody": ["class", "style"],
    "tr": ["class", "style"],
    "strong": ["class", "style"],
    "em": ["class", "style"],
    "sub": ["class", "style"],
    "sup": ["class", "style"],
    "br": ["class", "style"],
    "u": ["class", "style"],
    "s": ["class", "style"]
  };

  const class_allowlist: ClassAllowlist = {
    "div": [
      "ql-code-block-container", "ql-code-block", "ql-token", "ql-ui",
      "ql-align-center", "ql-align-right", "ql-align-justify",
      "ql-indent-1", "ql-indent-2", "ql-indent-3", "ql-indent-4", "ql-indent-5",
      "ql-indent-6", "ql-indent-7", "ql-indent-8", "ql-indent-9",
      "ql-size-small", "ql-size-large", "ql-size-huge", "ql-video"
    ],
    "span": [
      "ql-token", "hljs-keyword", "hljs-number", "hljs-string", "hljs-comment",
      "hljs-function", "hljs-title", "hljs-params", "hljs-variable",
      "hljs-operator", "hljs-builtin", "ql-ui"  // "ql-ui" is explicitly allowed
    ],
    "p": [
      "ql-align-center", "ql-align-right", "ql-align-justify",
      "ql-indent-1", "ql-indent-2", "ql-indent-3", "ql-indent-4", "ql-indent-5",
      "ql-indent-6", "ql-indent-7", "ql-indent-8", "ql-indent-9"
    ],
    "li": [
      "ql-align-center", "ql-align-right", "ql-align-justify",
      "ql-indent-1", "ql-indent-2", "ql-indent-3", "ql-indent-4", "ql-indent-5",
      "ql-indent-6", "ql-indent-7", "ql-indent-8", "ql-indent-9"
    ],
    "iframe": ["ql-video"],
    "td": ["ql-align-center", "ql-align-right", "ql-align-justify"],
    "select": ["ql-ui"],
    "tr": ["ql-align-center", "ql-align-right", "ql-align-justify"]
  };

  const config = {
    ALLOWED_TAGS: allowed_tags,
    ALLOWED_ATTR: all_attributes,
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+-]+(?:[^a-z+-:]|$))/i,
    FORBID_CONTENTS: [] as string[]
  };

  // Add a hook to filter out unauthorized attributes and classes.
  DOMPurify.addHook("afterSanitizeAttributes", (node: Element) => {
    const tagName = node.nodeName.toLowerCase();

    // Remove any attribute not allowed for this tag.
    if (tagName in attributes_by_tag) {
      const allowedAttributes = new Set(attributes_by_tag[tagName]);
      const attrs = Array.from(node.attributes);
      for (const attr of attrs) {
        if (!allowedAttributes.has(attr.name)) {
          node.removeAttribute(attr.name);
        }
      }
    }

    // Filter class names: only allow those in the defined class allowlist.
    if (node.hasAttribute("class") && tagName in class_allowlist) {
      const allowedClasses = new Set(class_allowlist[tagName]);
      const classNames = node.getAttribute("class")?.split(/\s+/) || [];
      const filteredClasses = classNames.filter((cls: string) =>
        allowedClasses.has(cls)
      );

      if (filteredClasses.length > 0) {
        node.setAttribute("class", filteredClasses.join(" "));
      } else {
        node.removeAttribute("class");
      }
    }

    // For anchor tags, enforce a safe "rel" when target is "_blank".
    if (tagName === "a" && node.hasAttribute("href")) {
      if (node.getAttribute("target") === "_blank") {
        node.setAttribute("rel", "noopener noreferrer");
      }
    }
  });

  return DOMPurify.sanitize(html, config);
}
