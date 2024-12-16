from markitdown import MarkItDown

markitdown = MarkItDown()
result = markitdown.convert("images/test.jpg")
print(result.text_content)
