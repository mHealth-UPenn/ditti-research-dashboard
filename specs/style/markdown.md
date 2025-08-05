# Markdown Style Guide

## Heading Increment

Heading levels should only increment by one level at a time.

```markdown
# Level 1
## Level 2
### Level 3
```

## Heading Style

Consistent heading style throughout the document.

```markdown
# Heading 1
## Heading 2
### Heading 3
```

## Unordered List Style

Consistent unordered list marker style.

```markdown
- Item 1
- Item 2
- Item 3
```

## List Indent

Consistent indentation for list items at the same level.

```markdown
- Item 1
  - Subitem 1
  - Subitem 2
- Item 2
```

## Unordered List Indent

Proper indentation for unordered lists.

## No Trailing Spaces

Remove trailing spaces at the end of lines.

## No Hard Tabs

Use spaces instead of hard tabs for indentation.

## No Reversed Links

Use proper link syntax.

```markdown
[Link text](url)
```

## No Multiple Blanks

No more than one consecutive blank line.

## Line Length

Limit line length to improve readability (recommended: 80-120 characters).

## Commands Show Output

When using dollar signs before commands, show the expected output.

```bash
$ ls -la
total 8
drwxr-xr-x  2 user  group   64 Jan  1 12:00 .
drwxr-xr-x  3 user  group   96 Jan  1 12:00 ..
```

## Blanks Around Headings

Headings should be surrounded by blank lines.

```markdown
Some text.

# Heading

More text.
```

## Heading Start Left

Headings must start at the beginning of the line.

```markdown
# Heading
```

## No Duplicate Heading

Multiple headings with the same content are not allowed.

## Single Title/Single H1

Only one top-level heading (H1) per document.

## No Trailing Punctuation

No trailing punctuation in headings.

## No Multiple Space Blockquote

Only one space after blockquote symbol.

```markdown
> This is a quote
```

## No Blanks Blockquote

No blank lines inside blockquotes.

## Ordered List Prefix

Consistent ordered list item prefix style.

```markdown
1. First item
2. Second item
3. Third item
```

## List Marker Space

Proper spacing after list markers.

```markdown
- Item 1
- Item 2
```

## Blanks Around Fences

Fenced code blocks should be surrounded by blank lines.

## Blanks Around Lists

Lists should be surrounded by blank lines.

## No Inline HTML

Avoid inline HTML in markdown documents.

## No Bare URLs

URLs should be properly formatted as links.

```markdown
[Visit our website](https://example.com)
```

## Horizontal Rule Style

Consistent horizontal rule style.

```markdown
---
```

## No Emphasis as Heading

Use proper headings instead of emphasis for section titles.

```markdown
# Section Title
```

## No Space in Emphasis

No spaces inside emphasis markers.

```markdown
*emphasized text*
```

## No Space in Code

No spaces inside code span elements.

```markdown
`code`
```

## No Space in Links

No spaces inside link text.

```markdown
[Link text](url)
```

## Fenced Code Language

Fenced code blocks should have a language specified.

```python
def hello():
    print("Hello, world!")
```

## First Line Heading

First line in file should be a top-level heading.

## No Empty Links

Links should have descriptive text.

```markdown
[Click here](url)
```

## Required Headings

Document should have required heading structure.

## Proper Names

Proper names should have correct capitalization.

## No Alt Text

Images should have alternate text (alt text).

```markdown
![Alt text](image.png)
```

## Code Block Style

Consistent code block style (fenced vs indented).

## Single Trailing Newline

Files should end with a single newline character.

## Code Fence Style

Consistent code fence style (backticks vs tildes).

```python
code here
```

## Emphasis Style

Emphasis style should be consistent (asterisks vs underscores).

```markdown
*emphasized text*
```

## Strong Style

Strong style should be consistent (asterisks vs underscores).

```markdown
**strong text**
```

## Link Fragments

Link fragments should be valid.

## Reference Links Images

Reference links and images should use defined labels.

```markdown
[Link text][label]

[label]: https://example.com
```

## Link Image Reference Definitions

Link and image reference definitions should be needed.

## Link Image Style

Consistent link and image style.

## Table Pipe Style

Consistent table pipe style.

```markdown
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
```

## Table Column Count

Consistent column count in tables.

## Blanks Around Tables

Tables should be surrounded by blank lines.

## Descriptive Link Text

Link text should be descriptive and meaningful.

```markdown
[Read our documentation](https://docs.example.com)
```

## Best Practices

1. **Consistency**: Use consistent formatting throughout your documents
2. **Readability**: Keep lines under 120 characters for better readability
3. **Accessibility**: Always include alt text for images
4. **Descriptive Links**: Use meaningful link text instead of generic phrases
5. **Proper Structure**: Use appropriate heading levels and maintain document hierarchy
6. **Code Blocks**: Always specify the language for fenced code blocks
7. **Clean Formatting**: Remove trailing spaces and use proper indentation
