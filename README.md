# ParentMarkDownChatbot
A local LLM+RAG chatbot with structured pdf ingestion using Word to convert pdf to docx, and then pandoc to convert from docx to markdown enabling the use of langchain ParentDocumentRetriever with MarkdownTextSplitter.
Uses Powershell with MS Word to open pdf file and convert to docx format, an impressive converter that finds and converts tables, then converts with pandoc to Markdown format.
